/* SPDX-License-Identifier: AGPL-3.0-or-later */
// Compile the production maps reader/parser with only its system calls replaced.
// No Android process or device fixture is involved.
#include "targets/home/tweaks/image.h"
#include "targets/home/tweaks/common.h"
#include "nativehook/native_image.h"
#include "nativehook/memory_io.h"
#include <elf.h>
#include <fcntl.h>
#include <link.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <array>
#include <cerrno>
#include <charconv>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <new>
#include <set>
#include <sstream>
#include <utility>

static bool fail_next_allocation = false;
[[gnu::noinline]] void* operator new(std::size_t size) {
    if (std::exchange(fail_next_allocation, false)) throw std::bad_alloc();
    if (void* memory = std::malloc(size ? size : 1)) return memory;
    throw std::bad_alloc();
}
[[gnu::noinline]] void operator delete(void* memory) noexcept { std::free(memory); }
[[gnu::noinline]] void operator delete(void* memory, std::size_t) noexcept { std::free(memory); }

namespace fixture {
std::string contents;
size_t position = 0;
unsigned reads = 0, closes = 0, interrupted = 0;
bool open_failure = false, read_failure = false, close_failure = false;
bool oversized_read = false, allocation_failure = false;
constexpr int descriptor = 17;

void reset(std::string text) {
    contents = std::move(text);
    position = 0;
    reads = closes = interrupted = 0;
    open_failure = read_failure = close_failure = oversized_read = allocation_failure = false;
    fail_next_allocation = false;
}
int open_file(const char* path, int flags) {
    if (std::string_view(path) != "/proc/self/maps" || flags != (O_RDONLY | O_CLOEXEC))
        std::abort();
    if (open_failure) { errno = EACCES; return -1; }
    return descriptor;
}
ssize_t read_chunk(int fd, void* destination, size_t capacity) {
    if (fd != descriptor || capacity != 4096) std::abort();
    ++reads;
    if (interrupted) { --interrupted; errno = EINTR; return -1; }
    if (read_failure && position) { errno = EIO; return -1; }
    if (oversized_read) return ssize_t(capacity + 1);
    const size_t amount = std::min(capacity, contents.size() - position);
    std::copy_n(contents.data() + position, amount, static_cast<char*>(destination));
    position += amount;
    if (allocation_failure && amount) {
        allocation_failure = false;
        fail_next_allocation = true; // The production string append now throws.
    }
    return ssize_t(amount);
}
int close_file(int fd) {
    if (fd != descriptor) std::abort();
    ++closes;
    if (close_failure) { errno = EINTR; return -1; }
    return 0;
}
} // namespace fixture

#define open fixture::open_file
#define read fixture::read_chunk
#define close fixture::close_file
#include "targets/home/tweaks/image.cpp"
#undef close
#undef read
#undef open

namespace {
unsigned checks = 0, failures = 0;
void check(bool condition, std::string_view label) {
    ++checks;
    if (!condition) { ++failures; std::cerr << "FAIL " << label << '\n'; }
}
std::string row(std::string_view range = "1000-2000", std::string_view permissions = "r-xp",
    std::string_view offset = "00000000", std::string_view device = "08:02",
    std::string_view inode = "123", std::string_view path = "/system/lib name.so") {
    return std::string(range) + " " + std::string(permissions) + " " + std::string(offset)
        + " " + std::string(device) + " " + std::string(inode) + "    " + std::string(path) + "\n";
}
bool parse(std::string text, std::vector<hometweaks::MapRow>& rows) {
    fixture::reset(std::move(text));
    return hometweaks::MapSnapshot(rows);
}
void reject(std::string text, std::string_view label) {
    std::vector<hometweaks::MapRow> rows;
    check(!parse(std::move(text), rows), label);
    check(fixture::closes == 1, "parser closes descriptor once");
}
void failed_read(std::string_view label) {
    std::string destination = "unchanged";
    check(!hometweaks::ReadMaps(destination), label);
    check(destination == "unchanged", "failure does not publish partial snapshot");
    check(fixture::closes == 1, "reader closes descriptor once");
}
} // namespace

int main() {
    std::vector<hometweaks::MapRow> rows;
    check(parse(row() + row("2000-3000", "rw-s", "1000", "ff:1", "456", "/data/source.apk")
        + row("3000-4000", "rw-p", "0", "00:00", "0", "[heap]"), rows), "valid maps");
    check(rows.size() == 2, "skip anonymous mappings");
    if (rows.size() == 2) {
        check(rows[0].readable && rows[0].map.executable && !rows[0].map.writable
            && rows[0].map.path == "/system/lib name.so", "path spaces and permissions");
        check(rows[1].map.file_offset == 0x1000 && rows[1].map.device_major == 0xff
            && rows[1].map.device_minor == 1 && rows[1].map.inode == 456, "numeric metadata");
    }
    reject(row("10000000000000000-2000"), "begin overflow");
    reject(row("1000-10000000000000000"), "end overflow");
    reject(row("2000-1000"), "reversed range");
    reject(row("1000-1000"), "empty range");
    reject(row("+1000-2000"), "signed address");
    reject(row("1000-2000junk"), "address suffix");
    reject(row("1000:2000"), "missing range separator");
    reject(row("1000-2000", "r-xp", "10000000000000000"), "offset overflow");
    reject(row("1000-2000", "r-xp", "0", "100000000:01"), "major overflow");
    reject(row("1000-2000", "r-xp", "0", "01:100000000"), "minor overflow");
    reject(row("1000-2000", "r-xp", "0", "01:02:03"), "extra device separator");
    reject(row("1000-2000", "r-xp", "0", "01:02", "18446744073709551616"), "inode overflow");
    reject(row("1000-2000", "r-xp", "0", "01:02", "-1"), "signed inode");
    for (const char* permissions : {"r-x", "r-xpp", "q-xp", "rqxp", "r-qp", "r-xq"})
        reject(row("1000-2000", permissions), "malformed permissions");
    reject("1000-2000 r-xp 0 08:02\n", "missing inode");
    auto nul_row = row(); nul_row.insert(4, 1, '\0');
    reject(nul_row, "embedded nul");
    std::string too_many;
    for (size_t i = 0; i < 16385; ++i) too_many += row();
    reject(std::move(too_many), "inventory line cap");

    fixture::reset(row()); fixture::interrupted = 32;
    std::string snapshot;
    check(hometweaks::ReadMaps(snapshot) && snapshot == fixture::contents
        && fixture::closes == 1, "finite interruptions recover");
    fixture::reset(row()); fixture::interrupted = 33;
    failed_read("interruption budget exhausted");
    check(fixture::reads == 33, "retry budget terminates");
    fixture::reset(std::string(8192, 'x') + "\n"); fixture::read_failure = true;
    failed_read("error after partial snapshot");
    fixture::reset(row()); fixture::oversized_read = true;
    failed_read("oversized syscall return");
    fixture::reset(std::string(2 * 1024 * 1024 - 1, 'x') + "\n");
    check(hometweaks::ReadMaps(snapshot) && snapshot.size() == 2 * 1024 * 1024,
        "accept exact byte cap");
    fixture::reset(std::string(2 * 1024 * 1024, 'x') + "\n");
    failed_read("reject above byte cap");
    fixture::reset(row()); fixture::close_failure = true;
    failed_read("close failure without retry");
    fixture::reset(""); failed_read("empty snapshot");
    fixture::reset("1000-2000 r-xp 0 08:02 1 /file"); failed_read("incomplete final line");
    fixture::reset(std::string(4096, 'x') + "\n"); fixture::allocation_failure = true;
    failed_read("allocation failure closes descriptor");
    check(!fail_next_allocation, "allocation failure injected into production append");
    fixture::reset(row()); fixture::open_failure = true;
    check(!hometweaks::ReadMaps(snapshot) && fixture::closes == 0 && fixture::reads == 0,
        "open failure has no descriptor to close");
    std::cout << "NativeMapsParseTest: " << checks << " checks; failures=" << failures << '\n';
    return failures ? 1 : 0;
}
