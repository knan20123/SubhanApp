[app]

# (str) عنوان التطبيق
title = سُبْحَان

# (str) اسم الحزمة (Package Name)
package.name = subhan_app

# (str) النطاق العكسي للحزمة (يجب أن يكون فريداً)
package.domain = com.drasimelnegar

# (str) المجلد المصدر للمشروع
source.dir = .

# (list) امتدادات الملفات التي سيتم تضمينها
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,mp3,json,spec

# (list) الملفات أو المجلدات التي سيتم استبعادها
source.exclude_exts = pyc,pyo,db,pickle
source.exclude_dirs = tests,__pycache__,.git,.idea,.vscode

# (str) إصدار التطبيق
version = 3.0.0

# (list) المتطلبات والمكتبات المطلوبة
# تم تحديثها لتشمل جميع المكتبات المستخدمة في الكود
requirements = python3==3.11.8,hostpython3==3.11.8,kivy==2.3.0,plyer,arabic-reshaper,python-bidi==0.4.2,cython==3.0.11,colorama

# (str) اتجاه الشاشة (portrait, landscape, أو both)
orientation = portrait

# (bool) وضع ملء الشاشة (0 = إيقاف, 1 = تشغيل)
fullscreen = 0

# (str) ملف أيقونة التطبيق
icon.filename = icon.png

# (str) ملف شاشة البداية (Splash Screen)
presplash.filename = presplash.png

# (str) لون خلفية شاشة البداية
android.presplash_color = #F2E5D7

# (str) إعدادات إضافية لشاشة البداية
android.meta_data = presplash-fit=cover

# (list) صلاحيات Android المطلوبة
# أضفت صلاحيات التخزين لتخزين البيانات والإشعارات
android.permissions = INTERNET,VIBRATE,WAKE_LOCK,POST_NOTIFICATIONS,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,FOREGROUND_SERVICE

# (int) مستوى Android API (34 = Android 14)
android.api = 34

# (int) الحد الأدنى لمستوى Android API (21 = Android 5.0)
android.minapi = 21

# (str) إصدار Android NDK
android.ndk = 25b

# (list) معماريات المعالج المدعومة
android.arch = arm64-v8a, armeabi-v7a

# (bool) تمكين AndroidX (مطلوب للمكتبات الحديثة)
android.enable_androidx = True

# (bool) وضع التصحيح (True للإصدارات التجريبية، False للإصدار النهائي)
android.debug = False

# (bool) تمكين دعم الأدوات (Toolchain)
android.use_sdk_tools = True

# (str) الهدف الأدنى لنظام Android
android.min_sdk_version = 21

# (str) الهدف لنظام Android
android.target_sdk_version = 34

# (bool) تمكين دعم Gradle
android.gradle_dependencies = True

# (bool) تمكين دعم AndroidX Core
android.enable_androidx_core = True

# (list) أذونات الإشعارات الإضافية
android.permissions += = POST_NOTIFICATIONS

# (str) نوع الخدمة الخلفية (للإشعارات)
android.services = your.service.here

# ====== خيارات iOS (يمكن تجاهلها حالياً) ======
# (str) اسم الفريق في Apple
ios.app_team = 

# (str) اسم شهادة التوزيع
ios.codesign.certificate = 

# ====== خيارات التعبئة ======
# (bool) تقليل حجم التطبيق (إزالة الملفات غير الضرورية)
android.strip_libs = True

# (bool) ضغط الملفات القابلة للتنفيذ
android.compress_shared_libs = True

# (str) اسم الملف النهائي
android.filename = subhan.apk

# (bool) تمكين الـ APK القابل للتقسيم (تطبيقات كبيرة)
android.split_apks = False

# ====== خيارات الخطوط ======
# (list) مجلدات الخطوط التي سيتم تضمينها
android.add_src = fonts

# (list) ملفات الخطوط المحددة للتضمين
android.add_src_ext = ttf,otf

# ====== خيارات التوقيع ======
# (bool) تمكين توقيع APK
android.sign = True

# (str) كلمة مرور الـ Keystore (استخدم كلمة قوية)
android.keystore_password = Subhan2024@Secure

# (str) كلمة مرور المفتاح
android.key_password = Subhan2024@Secure

# (str) اسم الـ Keystore
android.keystore_filename = subhan.keystore

# (str) اسم المفتاح
android.key_alias = subhan_app

# ====== خيارات إضافية ======
# (bool) تمكين دعم السجلات (Logs)
android.log_enable = True

# (bool) عرض سجلات البناء بالتفصيل
android.verbose = False

# (list) المكتبات المحلية المضمنة
android.add_libs_armeabi_v7a = 
android.add_libs_arm64_v8a =

# (str) هيكل التطبيق
android.manifest_application_attributes = android:usesCleartextTraffic="true"

[buildozer]

# (int) مستوى التسجيل (1-3، 3 للأكثر تفصيلاً)
log_level = 2

# (bool) تحذير عند التشغيل كجذر (root)
warn_on_root = 1android.aidl = /usr/local/android-sdk/build-tools/30.0.3/aidl
