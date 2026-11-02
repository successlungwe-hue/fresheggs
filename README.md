# FreshEggs Delivery (Flask)

Egg ordering app: customers order and track orders; the administrator manages products, stock, prices and order status.

**Admin login:** `/admin/login`, username `success`, password `lungwe04!`
The shop starts empty: log in and use **Add a product**.

## Files
| File | Purpose |
|---|---|
| `app.py` | Flask application |
| `desktop.py` | Starts the app on Windows (used for the .exe) |
| `main.py` | Starts the app inside the Android app |
| `buildozer.spec` | Android build settings |
| `build_exe.bat` | Builds `FreshEggs.exe` locally on Windows |
| `.github/workflows/build.yml` | Builds the .exe and .apk on GitHub |

## Run on a computer
```
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python desktop.py
```

## Get the .exe and .apk from GitHub
Push this folder to a GitHub repository. Open the **Actions** tab, run **Build FreshEggs (.exe and .apk)**, and download `FreshEggs-windows-exe` and `FreshEggs-android-apk` from **Artifacts** (about 10-25 minutes; the first APK build is the slowest).

The database is stored next to the .exe in `instance\`, and in the app's private storage on the phone.
Set `SECRET_KEY` and change the admin password before any public deployment.
