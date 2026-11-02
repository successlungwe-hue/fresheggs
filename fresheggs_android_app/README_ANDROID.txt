FRESHEGGS ANDROID APP (WebView)
===============================
This app opens the FreshEggs website inside an Android app. The FreshEggs server
(the Python program) must be running on a computer, or hosted online, and the
phone must be able to reach it.

BUILD THE APK (Android Studio, free)
1. Install Android Studio from developer.android.com/studio.
2. File > Open > choose this folder (FreshEggsApp). Wait for "Gradle sync" to finish
   (it downloads what it needs; internet required).
3. Build > Build Bundle(s) / APK(s) > Build APK(s).
4. Click "locate" in the pop-up. The file is app\build\outputs\apk\debug\app-debug.apk
5. Copy it to the phone and install it (allow "Install unknown apps" if asked).

RUN THE SERVER FOR THE PHONE
1. On the Windows computer, double-click run_for_phone.bat (in the fresheggs_python folder).
2. It prints an address such as http://192.168.1.20:5000 . Phone and computer must
   be on the same Wi-Fi. If Windows Firewall asks, allow Python on private networks.
3. Open the FreshEggs app on the phone and type that address when asked.
   (Android emulator: use http://10.0.2.2:5000)
The address can be changed later from the menu (top right) > Server address.
