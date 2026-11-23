[app]
title = JS Studio
package.name = jsstudio
package.domain = com.jsstudio
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt
source.exclude_dirs = tests, bin, venv, .git, .buildozer
version = 1.0.0
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.private_storage = True
android.enable_androidx = True
android.accept_sdk_license = True
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 0