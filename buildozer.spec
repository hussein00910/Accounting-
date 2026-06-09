[app]
title = المحاسب الذكي
package.name = smartaccountant
package.domain = com.hussein.smartaccountant

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,pyjnius,android

# Include data files
source.include_patterns = data/*.json

orientation = portrait
fullscreen = 0

android.permissions = READ_SMS, RECEIVE_SMS, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET
android.api = 34
android.minapi = 26
android.ndk = 25b
android.sdk = 34
android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True
android.accept_sdk_license = True

# Build settings
p4a.branch = master
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
