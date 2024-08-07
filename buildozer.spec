[app] 
title = cookin calendar
package.name = myapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java
version = 0.1
requirements = python3==3.11.0,hostpython3==3.11.0,kivy,pillow
orientation = portrait
fullscreen = 1
android.permissions = SEND_SMS, RECEIVE_SMS, READ_SMS
android.add_src = javafiles/org/test/smsreceiver
android.logcat_filters = *:S python:D
android.copy_libs = 1
android.archs = arm64-v8a
android.allow_backup = True
android.debug_artifact = apk
android.api = 33
android.build_tools = 33.0.0
[buildozer]
log_level = 2
warn_on_root = 1
