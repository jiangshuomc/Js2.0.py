[app]
title = JS Studio
package.name = jsstudio
package.domain = com.jsstudio
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt
version = 1.0
requirements = python3,kivy==2.3.0,android
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.build_tools_version = 33.0.2
android.archs = arm64-v8a
p4a.branch = master
p4a.bootstrap = sdl2
android.enable_androidx = True
android.private_storage = True
android.logcat_filters = *:S python:D
