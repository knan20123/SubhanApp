# -*- coding: utf-8 -*-
"""
نقطة الدخول الرئيسية لتطبيق سُبْحَان.
هذا الملف مصمم عمدًا ليكون بسيطًا جدًا، بحيث يلتقط أي خطأ يحدث
حتى أثناء استيراد app_core.py (أخطاء الاستيراد، تعريف الكلاسات، إلخ)
وليس فقط الأخطاء أثناء تشغيل التطبيق.
"""

import os
import sys
import traceback


def _show_crash_screen(error_text):
    """يعرض نص الخطأ مباشرة على الشاشة كملاذ أخير، لا يعتمد على أي صلاحيات."""
    try:
        from kivy.app import App as _App
        from kivy.uix.scrollview import ScrollView as _ScrollView
        from kivy.uix.label import Label as _Label

        class CrashApp(_App):
            def build(self):
                sv = _ScrollView()
                lbl = _Label(
                    text=error_text,
                    size_hint_y=None,
                    text_size=(400, None),
                    halign="left",
                    valign="top",
                    color=(1, 1, 1, 1),
                )
                lbl.bind(texture_size=lambda i, v: setattr(lbl, "height", v[1]))
                sv.add_widget(lbl)
                return sv

        CrashApp().run()
    except Exception:
        pass


def _write_crash_file(error_text):
    """يحاول كتابة الخطأ في ملف نصي بعدة مسارات محتملة."""
    possible_paths = []
    try:
        from android.storage import primary_external_storage_path
        possible_paths.append(os.path.join(primary_external_storage_path(), "Download", "subhan_crash.txt"))
    except Exception:
        pass
    possible_paths.append("/sdcard/Download/subhan_crash.txt")
    possible_paths.append("/sdcard/subhan_crash.txt")
    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths.append(os.path.join(app_dir, "subhan_crash.txt"))
    except Exception:
        pass

    for path in possible_paths:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(error_text)
        except Exception:
            continue


def _handle_crash(exc_type, exc_value, exc_traceback):
    error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print("=" * 40)
    print("CRASH TRACEBACK:")
    print(error_text)
    print("=" * 40)
    _write_crash_file(error_text)
    _show_crash_screen(error_text)


# نفعّل معالج الأخطاء العام فورًا، قبل أي استيراد إضافي
sys.excepthook = _handle_crash

try:
    print("بدء تطبيق سُبْحَان...")
    print(f"مسار الملف: {os.path.abspath(__file__)}")

    # الاستيراد نفسه محاط بمعالجة صريحة، لأن sys.excepthook
    # لا يلتقط دائمًا أخطاء تحدث أثناء عملية import في بعض بيئات أندرويد
    try:
        from app_core import SubhanApp
    except Exception:
        _handle_crash(*sys.exc_info())
        raise

    print("تم استيراد app_core بنجاح، بدء التشغيل...")
    SubhanApp().run()

except Exception:
    _handle_crash(*sys.exc_info())
