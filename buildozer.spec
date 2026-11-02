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
requirements = python3,flask,werkzeug,jinja2,markupsafe,itsdangerous,click,blinker,sqlite3
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.png
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.bootstrap = webview
p4a.port = 5000

[buildozer]
log_level = 2
warn_on_root = 1
