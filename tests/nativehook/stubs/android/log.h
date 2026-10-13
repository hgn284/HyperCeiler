/* SPDX-License-Identifier: AGPL-3.0-or-later */
#pragma once
constexpr int ANDROID_LOG_INFO = 4;
constexpr int ANDROID_LOG_WARN = 5;
constexpr int ANDROID_LOG_ERROR = 6;
inline int __android_log_print(int, const char*, const char*, ...) { return 0; }
