package android.database;

public class ContentObserver {
    // The Android-compatible parameter is unused by this synchronous test stub.
    @SuppressWarnings("PMD.UnusedFormalParameter")
    public ContentObserver(Object handler) {
        // Callback dispatch is synchronous in the host fixture.
    }
    public void onChange(boolean selfChange, android.net.Uri uri) {
        // Subclasses override the callback under test.
    }
}
