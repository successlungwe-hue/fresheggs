"""Android entry point (Buildozer / python-for-android, WebView bootstrap).

The app starts the Flask server on the phone; Android shows it in a WebView.
"""
import os

# Keep the database in the app's private storage.
os.environ.setdefault(
    "FRESHEGGS_DATA_DIR",
    os.path.join(os.environ.get("ANDROID_PRIVATE", os.path.dirname(os.path.abspath(__file__))), "instance"),
)

from app import app  # noqa: E402

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")),
            debug=False, use_reloader=False, threaded=True)
