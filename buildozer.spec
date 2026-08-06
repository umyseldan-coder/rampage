[app]
title = Rampage
package.name = rampage
package.domain = com.rampage

version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec,pyc,pyo,pyd

application.fullscreen = 0

requirements = python3,kivy,requests,android

orientation = portrait
fullscreen = 0

android.minapi = 21
android.maxapi = 33
android.targetapi = 31
android.api = 31

android.permissions = INTERNET,CAMERA,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE,FLASHLIGHT

android.wakelock = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 0
build_dir = .buildozer
bin_dir = bin
