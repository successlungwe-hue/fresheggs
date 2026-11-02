[app]
title = FreshEggs
package.name = fresheggs
package.domain = org.fresheggs
source.dir = .
source.include_exts = py,html,css,png,ico
source.include_patterns = templates/*,static/*
source.exclude_dirs = .github,.venv,bin,build,dist,instance,__pycache__
source.exclude_patterns = desktop.py,build_exe.bat
version = 1.0
requirements = python3,flask==2.2.5,werkzeug==2.2.3,jinja2==3.1.2,markupsafe==2.1.3,itsdangerous==2.1.2,click==8.1.7,sqlite3
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.png
android.permissions = INTERNET
android.api = 33
android.ndk = 25b
android.ndk_api = 21
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.branch = v2024.01.21
p4a.bootstrap = webview
p4a.port = 5000

[buildozer]
log_level = 2
warn_on_root = 1
