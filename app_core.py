# -*- coding: utf-8 -*-
"""
تطبيق سُبْحَان - النسخة المتكاملة مع واجهة حية ومتحركة
النسخة المحسنة 3.0.0 - مع تأثيرات ديناميكية وألوان نابضة بالحياة
"""

import json
import os
import random
from datetime import date, datetime, timedelta
import logging
import math
from functools import lru_cache

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, PushMatrix, PopMatrix, Rotate
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.effects.scroll import ScrollEffect
from kivy.properties import NumericProperty, ColorProperty, StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
import colorsys

# ========== التسجيل ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== المكتبات الخارجية ==========
try:
    from plyer import vibrator
    HAS_VIBRATOR = True
except Exception:
    HAS_VIBRATOR = False

try:
    from plyer import share
    HAS_SHARE = True
except Exception:
    HAS_SHARE = False

try:
    from plyer import clipboard
    HAS_CLIPBOARD = True
except Exception:
    HAS_CLIPBOARD = False

try:
    from plyer import notification
    HAS_NOTIFICATION = True
except Exception:
    HAS_NOTIFICATION = False

# ========== دعم اللغة العربية ==========
try:
    import arabic_reshaper
    HAS_ARABIC_SUPPORT = True
except Exception:
    HAS_ARABIC_SUPPORT = False

try:
    from bidi.algorithm import get_display
    HAS_BIDI_SUPPORT = True
except Exception:
    HAS_BIDI_SUPPORT = False

def ar(text):
    if not HAS_ARABIC_SUPPORT or not text:
        return text
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        if HAS_BIDI_SUPPORT:
            lines = reshaped_text.split('\n')
            result_lines = [get_display(line) for line in lines]
            return '\n'.join(result_lines)
        else:
            lines = reshaped_text.split('\n')
            result_lines = [line[::-1] for line in lines]
            return '\n'.join(result_lines)
    except Exception:
        return text

# ========== مسارات الخطوط ==========
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoNaskhArabic-Regular.ttf")
FONT_BOLD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoNaskhArabic-Bold.ttf")
FONT_REGULAR = FONT_PATH if os.path.exists(FONT_PATH) else None
FONT_BOLD = FONT_BOLD_PATH if os.path.exists(FONT_BOLD_PATH) else None

EMOJI_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoEmoji-Regular.ttf")
EMOJI_FONT = EMOJI_FONT_PATH if os.path.exists(EMOJI_FONT_PATH) else None

import re as _re
_EMOJI_PATTERN = _re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F000-\U0001F0FF"
    "\U00002190-\U000021FF"
    "\U00002B00-\U00002BFF"
    "\U0000FE0F"
    "]+",
    flags=_re.UNICODE,
)


def split_emoji_text(text):
    """يفصل النص إلى أجزاء: (نوع, محتوى) حيث نوع هو 'emoji' أو 'text'.
    يحافظ على ترتيب الظهور الأصلي في النص."""
    parts = []
    last_end = 0
    for match in _EMOJI_PATTERN.finditer(text):
        if match.start() > last_end:
            parts.append(("text", text[last_end:match.start()]))
        parts.append(("emoji", match.group()))
        last_end = match.end()
    if last_end < len(text):
        parts.append(("text", text[last_end:]))
    return parts

# ========== ألوان نابضة بالحياة ==========
COLOR_BG = (0.02, 0.05, 0.08, 1)
COLOR_CARD = (0.08, 0.15, 0.20, 1)
COLOR_PRIMARY = (0.20, 0.70, 0.60, 1)
COLOR_ACCENT = (1.00, 0.75, 0.20, 1)
COLOR_TEXT = (0.98, 0.98, 0.95, 1)
COLOR_TEXT_MUTED = (0.60, 0.75, 0.80, 1)
COLOR_DANGER = (0.85, 0.25, 0.25, 1)
COLOR_SUCCESS = (0.20, 0.85, 0.40, 1)
COLOR_PURPLE = (0.60, 0.30, 0.80, 1)
COLOR_ORANGE = (1.00, 0.55, 0.10, 1)
COLOR_PINK = (0.95, 0.40, 0.60, 1)

NIGHT_BG = (0.01, 0.01, 0.03, 1)
NIGHT_CARD = (0.05, 0.05, 0.10, 1)
NIGHT_PRIMARY = (0.10, 0.40, 0.35, 1)
NIGHT_ACCENT = (0.85, 0.60, 0.15, 1)
NIGHT_TEXT = (0.90, 0.90, 0.95, 1)
NIGHT_TEXT_MUTED = (0.50, 0.60, 0.70, 1)
NIGHT_DANGER = (0.70, 0.20, 0.20, 1)
NIGHT_SUCCESS = (0.15, 0.70, 0.30, 1)
NIGHT_PURPLE = (0.40, 0.20, 0.60, 1)
NIGHT_ORANGE = (0.80, 0.40, 0.08, 1)
NIGHT_PINK = (0.75, 0.25, 0.45, 1)

current_colors = {}

def apply_theme(night_mode=False):
    global current_colors
    if night_mode:
        current_colors = {
            "bg": NIGHT_BG, "card": NIGHT_CARD, "primary": NIGHT_PRIMARY,
            "accent": NIGHT_ACCENT, "text": NIGHT_TEXT, "text_muted": NIGHT_TEXT_MUTED,
            "danger": NIGHT_DANGER, "success": NIGHT_SUCCESS,
            "purple": NIGHT_PURPLE, "orange": NIGHT_ORANGE, "pink": NIGHT_PINK
        }
        Window.clearcolor = NIGHT_BG
    else:
        current_colors = {
            "bg": COLOR_BG, "card": COLOR_CARD, "primary": COLOR_PRIMARY,
            "accent": COLOR_ACCENT, "text": COLOR_TEXT, "text_muted": COLOR_TEXT_MUTED,
            "danger": COLOR_DANGER, "success": COLOR_SUCCESS,
            "purple": COLOR_PURPLE, "orange": COLOR_ORANGE, "pink": COLOR_PINK
        }
        Window.clearcolor = COLOR_BG

apply_theme(False)

# ========== ألوان العداد المتغيرة ==========
COUNTER_COLORS = [
    (1.00, 0.84, 0.00, 1),  # 0-99: ذهبي
    (0.20, 0.85, 0.40, 1),  # 100-199: أخضر
    (0.20, 0.50, 0.90, 1),  # 200-299: أزرق
    (0.60, 0.30, 0.80, 1),  # 300-399: بنفسجي
    (0.90, 0.20, 0.30, 1),  # 400-499: أحمر
    (1.00, 0.55, 0.10, 1),  # 500-599: برتقالي
    (0.95, 0.40, 0.60, 1),  # 600+: وردي
]

def get_counter_color(count):
    index = min(count // 100, len(COUNTER_COLORS) - 1)
    return COUNTER_COLORS[index]

# ========== مكونات ديناميكية ==========

class GradientBackground(Widget):
    """خلفية متدرجة متحركة"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0
        self.bind(pos=self.update, size=self.update)
        Clock.schedule_interval(self.animate, 0.05)
    
    def animate(self, dt):
        self.angle += 0.3
        self.update()
    
    def update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            c1 = current_colors["bg"]
            c2 = current_colors["card"]
            # تحريك الألوان
            r1 = c1[0] + 0.02 * math.sin(math.radians(self.angle))
            g1 = c1[1] + 0.02 * math.sin(math.radians(self.angle + 30))
            b1 = c1[2] + 0.02 * math.sin(math.radians(self.angle + 60))
            r2 = c2[0] + 0.02 * math.sin(math.radians(self.angle + 90))
            g2 = c2[1] + 0.02 * math.sin(math.radians(self.angle + 120))
            b2 = c2[2] + 0.02 * math.sin(math.radians(self.angle + 150))
            
            Color(min(max(r1, 0), 1), min(max(g1, 0), 1), min(max(b1, 0), 1), 1)
            Rectangle(pos=self.pos, size=self.size)

class AnimatedButton(ButtonBehavior, Widget):
    """زر مع تأثيرات نبض وحركة"""
    text = StringProperty("")
    color = ColorProperty((1, 1, 1, 1))
    bg_color = ColorProperty(current_colors["primary"])
    font_size = NumericProperty(14)
    bold = NumericProperty(0)
    radius = NumericProperty(10)
    scale = NumericProperty(1)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(45)
        self.pulse_anim = Animation(scale=1.05, duration=0.3) + Animation(scale=1, duration=0.3)
        self.pulse_anim.repeat = True
        self.bind(on_press=self.on_press_anim)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        Clock.schedule_once(self.start_pulse, 0.5)
    
    def start_pulse(self, dt):
        self.pulse_anim.start(self)
    
    def on_press_anim(self, *args):
        anim = Animation(scale=0.9, duration=0.1) + Animation(scale=1, duration=0.1)
        anim.start(self)
        self.pulse_anim.stop()
        Clock.schedule_once(lambda dt: self.pulse_anim.start(self), 0.3)
    
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

        self.canvas.clear()
        if not self.text:
            return

        parts = split_emoji_text(self.text)
        if not parts:
            return

        # نبني قائمة textures لكل جزء (نص عربي بخطه، إيموجي بخطه)
        textures = []
        for kind, chunk in parts:
            if kind == "text" and not chunk.strip():
                continue
            if kind == "emoji" and EMOJI_FONT:
                lbl = Label(text=chunk, font_size=self.font_size)
                lbl.font_name = EMOJI_FONT
            else:
                display_text = chunk if kind == "emoji" else ar(chunk)
                lbl = Label(text=display_text, color=self.color, font_size=self.font_size,
                           bold=bool(self.bold))
                if FONT_BOLD and self.bold:
                    lbl.font_name = FONT_BOLD
                elif FONT_REGULAR:
                    lbl.font_name = FONT_REGULAR
            lbl.texture_update()
            if lbl.texture:
                textures.append(lbl.texture)

        if not textures:
            return

        # نعرض الأجزاء بترتيب RTL (يمين لليسار) مطابقًا لاتجاه النص العربي
        total_width = sum(t.width for t in textures) + dp(2) * (len(textures) - 1)
        start_x = self.x + (self.width - total_width) / 2
        max_height = max(t.height for t in textures)

        with self.canvas:
            Color(1, 1, 1, 1)
            cur_x = start_x
            for tex in reversed(textures):
                pos_y = self.y + (self.height - tex.height) / 2
                Rectangle(texture=tex, pos=(cur_x, pos_y), size=tex.size)
                cur_x += tex.width + dp(2)

class ParticleEffect(Widget):
    """تأثير جزيئات متطايرة"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        self.bind(pos=self.update, size=self.update)
    
    def burst(self, pos, color):
        for _ in range(25):
            angle = random.uniform(0, 360)
            speed = random.uniform(50, 150)
            size = random.uniform(3, 8)
            life = random.uniform(0.5, 1.5)
            self.particles.append({
                'x': pos[0], 'y': pos[1],
                'vx': speed * math.cos(math.radians(angle)),
                'vy': speed * math.sin(math.radians(angle)),
                'size': size,
                'life': life,
                'max_life': life,
                'color': color
            })
        Clock.schedule_interval(self.update_particles, 0.02)
    
    def update_particles(self, dt):
        self.canvas.clear()
        to_remove = []
        for i, p in enumerate(self.particles):
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] -= 200 * dt
            p['life'] -= dt
            if p['life'] <= 0:
                to_remove.append(i)
                continue
            alpha = p['life'] / p['max_life']
            with self.canvas:
                Color(p['color'][0], p['color'][1], p['color'][2], alpha)
                RoundedRectangle(pos=(p['x'] - p['size']/2, p['y'] - p['size']/2),
                                size=(p['size'], p['size']), radius=[p['size']/2])
        
        for i in reversed(to_remove):
            del self.particles[i]
        
        if not self.particles:
            Clock.unschedule(self.update_particles)
    
    def update(self, *args):
        pass

class SparkleEffect(Widget):
    """تأثير بريق متلألئ"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sparkles = []
        self.angle = 0
        Clock.schedule_interval(self.update, 0.05)
    
    def add_sparkle(self, pos):
        self.sparkles.append({
            'x': pos[0], 'y': pos[1],
            'size': random.uniform(2, 5),
            'phase': random.uniform(0, 360),
            'speed': random.uniform(2, 5)
        })
    
    def update(self, dt):
        self.canvas.clear()
        self.angle += 2
        for s in self.sparkles[:]:
            s['phase'] += s['speed']
            if s['phase'] > 720:
                self.sparkles.remove(s)
                continue
            alpha = abs(math.sin(math.radians(s['phase'])))
            with self.canvas:
                Color(current_colors["accent"][0], current_colors["accent"][1],
                      current_colors["accent"][2], alpha * 0.8)
                size = s['size'] * (0.5 + 0.5 * math.sin(math.radians(s['phase'])))
                RoundedRectangle(pos=(s['x'] - size/2, s['y'] - size/2),
                                size=(size, size), radius=[size/2])

# ========== البيانات ==========
AZKAR = {
    "* الصباح": [
        {"text": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ رَبِّ الْعَالَمِينَ", "count": 1},
        {"text": "رَضِيتُ بِاللَّهِ رَبًّا وَبِالْإِسْلَامِ دِينًا وَبِمُحَمَّدٍ نَبِيًّا", "count": 1},
        {"text": "اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا، وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ النُّشُورُ", "count": 1},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَافِيَةَ فِي الدُّنْيَا وَالْآخِرَةِ", "count": 1},
        {"text": "حَسْبِيَ اللَّهُ لَا إِلَهَ إِلَّا هُوَ عَلَيْهِ تَوَكَّلْتُ", "count": 7},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ عِلْمًا نَافِعًا وَرِزْقًا طَيِّبًا وَعَمَلًا مُتَقَبَّلًا", "count": 1},
        {"text": "اللَّهُمَّ مَا أَصْبَحَ بِي مِنْ نِعْمَةٍ فَمِنْكَ وَحْدَكَ لَا شَرِيكَ لَكَ", "count": 1},
        {"text": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ عَدَدَ خَلْقِهِ وَرِضَا نَفْسِهِ وَزِنَةَ عَرْشِهِ وَمِدَادَ كَلِمَاتِهِ", "count": 3},
    ],
    ") المساء": [
        {"text": "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ رَبِّ الْعَالَمِينَ", "count": 1},
        {"text": "اللَّهُمَّ إِنِّي أَمْسَيْتُ أُشْهِدُكَ وَأُشْهِدُ حَمَلَةَ عَرْشِكَ", "count": 1},
        {"text": "اللَّهُمَّ مَا أَمْسَى بِي مِنْ نِعْمَةٍ فَمِنْكَ وَحْدَكَ لَا شَرِيكَ لَكَ", "count": 1},
        {"text": "أَعُوذُ بِكَلِمَاتِ اللَّهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ", "count": 3},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ خَيْرَ هَذِهِ اللَّيْلَةِ وَخَيْرَ مَا فِيهَا", "count": 1},
        {"text": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ عَدَدَ خَلْقِهِ وَرِضَا نَفْسِهِ", "count": 3},
    ],
    "۩ بعد الصلاة": [
        {"text": "أَسْتَغْفِرُ اللَّهَ", "count": 3},
        {"text": "اللَّهُمَّ أَنْتَ السَّلَامُ وَمِنْكَ السَّلَامُ تَبَارَكْتَ يَا ذَا الْجَلَالِ وَالْإِكْرَامِ", "count": 1},
        {"text": "سُبْحَانَ اللَّهِ", "count": 33},
        {"text": "الْحَمْدُ لِلَّهِ", "count": 33},
        {"text": "اللَّهُ أَكْبَرُ", "count": 34},
        {"text": "لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ", "count": 1},
        {"text": "اللَّهُمَّ لَا مَانِعَ لِمَا أَعْطَيْتَ وَلَا مُعْطِيَ لِمَا مَنَعْتَ", "count": 1},
    ],
    ") النوم": [
        {"text": "بِاسْمِكَ رَبِّي وَضَعْتُ جَنْبِي وَبِكَ أَرْفَعُهُ", "count": 1},
        {"text": "اللَّهُمَّ قِنِي عَذَابَكَ يَوْمَ تَبْعَثُ عِبَادَكَ", "count": 1},
        {"text": "سُبْحَانَ اللَّهِ", "count": 33},
        {"text": "الْحَمْدُ لِلَّهِ", "count": 33},
        {"text": "اللَّهُ أَكْبَرُ", "count": 34},
        {"text": "اللَّهُمَّ بِاسْمِكَ أَمُوتُ وَأَحْيَا", "count": 1},
        {"text": "اللَّهُمَّ أَسْلَمْتُ نَفْسِي إِلَيْكَ وَوَجَّهْتُ وَجْهِي إِلَيْكَ", "count": 1},
    ],
    "# أذكار الحج والعمرة": [
        {"text": "لَبَّيْكَ اللَّهُمَّ لَبَّيْكَ، لَبَّيْكَ لَا شَرِيكَ لَكَ لَبَّيْكَ، إِنَّ الْحَمْدَ وَالنِّعْمَةَ لَكَ وَالْمُلْكَ لَا شَرِيكَ لَكَ", "count": 1},
        {"text": "سُبْحَانَ اللَّهِ وَالْحَمْدُ لِلَّهِ وَلَا إِلَهَ إِلَّا اللَّهُ وَاللَّهُ أَكْبَرُ", "count": 100},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ فِي الدُّنْيَا وَالْآخِرَةِ", "count": 1},
    ],
}

ADIYA = {
    "# قرآنية": [
        {"text": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ", "source": "البقرة 201"},
        {"text": "رَبِّ اشْرَحْ لِي صَدْرِي وَيَسِّرْ لِي أَمْرِي", "source": "طه 25-26"},
        {"text": "رَبِّ زِدْنِي عِلْمًا", "source": "طه 114"},
        {"text": "رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا وَهَبْ لَنَا مِنْ لَدُنْكَ رَحْمَةً", "source": "آل عمران 8"},
        {"text": "رَبَّنَا اغْفِرْ لَنَا وَلِإِخْوَانِنَا الَّذِينَ سَبَقُونَا بِالْإِيمَانِ", "source": "الحشر 10"},
        {"text": "رَبَّنَا لَا تُؤَاخِذْنَا إِن نَّسِينَا أَوْ أَخْطَأْنَا", "source": "البقرة 286"},
        {"text": "رَبَّنَا وَلَا تَحْمِلْ عَلَيْنَا إِصْرًا كَمَا حَمَلْتَهُ عَلَى الَّذِينَ مِن قَبْلِنَا", "source": "البقرة 286"},
        {"text": "رَبَّنَا وَلَا تُحَمِّلْنَا مَا لَا طَاقَةَ لَنَا بِهِ ۖ وَاعْفُ عَنَّا وَاغْفِرْ لَنَا وَارْحَمْنَا", "source": "البقرة 286"},
        {"text": "رَبَّنَا أَفْرِغْ عَلَيْنَا صَبْرًا وَثَبِّتْ أَقْدَامَنَا وَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ", "source": "البقرة 250"},
        {"text": "رَبَّنَا لَا تَجْعَلْنَا فِتْنَةً لِّلَّذِينَ كَفَرُوا وَاغْفِرْ لَنَا رَبَّنَا ۖ إِنَّكَ أَنتَ الْعَزِيزُ الْحَكِيمُ", "source": "الممتحنة 5"},
        {"text": "رَبَّنَا أَتِمْمْ لَنَا نُورَنَا وَاغْفِرْ لَنَا ۖ إِنَّكَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ", "source": "التحريم 8"},
    ],
    "۩ نبوية": [
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْهُدَى وَالتُّقَى وَالْعَفَافَ وَالْغِنَى", "source": "مسلم"},
        {"text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ وَالْعَجْزِ وَالْكَسَلِ", "source": "البخاري"},
        {"text": "اللَّهُمَّ أَعِنِّي عَلَى ذِكْرِكَ وَشُكْرِكَ وَحُسْنِ عِبَادَتِكَ", "source": "أبو داود"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْجَنَّةَ وَأَعُوذُ بِكَ مِنَ النَّارِ", "source": "أبو داود"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ حُبَّكَ وَحُبَّ مَنْ يُحِبُّكَ وَالْعَمَلَ الَّذِي يُبَلِّغُنِي حُبَّكَ", "source": "الترمذي"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ بِأَنَّ لَكَ الْحَمْدُ لَا إِلَهَ إِلَّا أَنْتَ", "source": "أبو داود"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الصِّحَّةَ وَالْعَافِيَةَ وَالْأَمَانَ", "source": "أحمد"},
    ],
    "۩ أدعية الأنبياء": [
        {"text": "رَبِّ إِنِّي لِمَا أَنزَلْتَ إِلَيَّ مِنْ خَيْرٍ فَقِيرٌ", "source": "موسى - القصص 24"},
        {"text": "رَبِّ اشْرَحْ لِي صَدْرِي وَيَسِّرْ لِي أَمْرِي", "source": "موسى - طه 25-26"},
        {"text": "رَبِّ هَبْ لِي حُكْمًا وَأَلْحِقْنِي بِالصَّالِحِينَ", "source": "إبراهيم - الشعراء 83"},
        {"text": "رَبَّنَا آمَنَّا بِمَا أَنزَلْتَ وَاتَّبَعْنَا الرَّسُولَ فَاكْتُبْنَا مَعَ الشَّاهِدِينَ", "source": "آل عمران 53"},
        {"text": "رَبِّ أَوْزِعْنِي أَنْ أَشْكُرَ نِعْمَتَكَ الَّتِي أَنْعَمْتَ عَلَيَّ", "source": "النمل 19"},
        {"text": "رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ", "source": "إبراهيم 41"},
    ],
    "<3 التفريج والهم": [
        {"text": "لَا إِلَهَ إِلَّا أَنْتَ سُبْحَانَكَ إِنِّي كُنتُ مِنَ الظَّالِمِينَ", "source": "الأنبياء 87"},
        {"text": "اللَّهُمَّ إِنِّي عَبْدُكَ وَابْنُ عَبْدِكَ نَاصِيَتِي بِيَدِكَ", "source": "ابن ماجه"},
        {"text": "اللَّهُمَّ اكْشِفْ عَنِّي الْغَمَّ وَالْهَمَّ وَالْحَزَنَ", "source": "ابن حبان"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَافِيَةَ مِنَ الْبَلَاءِ", "source": "الترمذي"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْفَرَجَ الْقَرِيبَ وَالصَّبْرَ الْجَمِيلَ", "source": "ابن السني"},
    ],
    "# السفر": [
        {"text": "اللَّهُمَّ إِنَّا نَسْأَلُكَ فِي سَفَرِنَا هَذَا الْبِرَّ وَالتَّقْوَى", "source": "مسلم"},
        {"text": "اللَّهُمَّ هَوِّنْ عَلَيْنَا سَفَرَنَا هَذَا وَاطْوِ عَنَّا بُعْدَهُ", "source": "مسلم"},
        {"text": "اللَّهُمَّ أَنْتَ الصَّاحِبُ فِي السَّفَرِ وَالْخَلِيفَةُ فِي الْأَهْلِ", "source": "مسلم"},
        {"text": "آيِبُونَ تَائِبُونَ عَابِدُونَ لِرَبِّنَا حَامِدُونَ", "source": "مسلم"},
        {"text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ وَعْثَاءِ السَّفَرِ وَكَآبَةِ الْمُنْقَلَبِ", "source": "مسلم"},
    ],
    "$ الرزق": [
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ رِزْقًا طَيِّبًا وَعِلْمًا نَافِعًا وَعَمَلًا مُتَقَبَّلًا", "source": "ابن ماجه"},
        {"text": "اللَّهُمَّ اكْفِنِي بِحَلَالِكَ عَنْ حَرَامِكَ وَأَغْنِنِي بِفَضْلِكَ عَمَّنْ سِوَاكَ", "source": "الترمذي"},
        {"text": "اللَّهُمَّ بَارِكْ لَنَا فِيمَا رَزَقْتَنَا وَقِنَا عَذَابَ النَّارِ", "source": "الحاكم"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ مِنَ الْخَيْرِ عَاجِلِهِ وَآجِلِهِ", "source": "أحمد"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الرِّزْقَ الْوَاسِعَ وَالْعَمَلَ النَّافِعَ", "source": "ابن السني"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْغِنَى وَالْعَافِيَةَ", "source": "الترمذي"},
    ],
    "+ الشفاء": [
        {"text": "اللَّهُمَّ رَبَّ النَّاسِ أَذْهِبِ الْبَأْسَ وَاشْفِ أَنْتَ الشَّافِي لَا شِفَاءَ إِلَّا شِفَاؤُكَ", "source": "البخاري"},
        {"text": "أَسْأَلُ اللَّهَ الْعَظِيمَ رَبَّ الْعَرْشِ الْعَظِيمِ أَنْ يَشْفِيَكَ", "source": "الترمذي"},
        {"text": "بِسْمِ اللَّهِ أَرْقِيكَ، مِنْ كُلِّ شَيْءٍ يُؤْذِيكَ", "source": "مسلم"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَافِيَةَ فِي الدُّنْيَا وَالْآخِرَةِ", "source": "أبو داود"},
        {"text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْبَرَصِ وَالْجُنُونِ وَالْجُذَامِ وَسَيِّئِ الْأَسْقَامِ", "source": "أبو داود"},
        {"text": "اللَّهُمَّ اشْفِ مَرْضَانَا وَارْحَمْ مَوْتَانَا", "source": "أحمد"},
    ],
    "۩ المسجد": [
        {"text": "اللَّهُمَّ افْتَحْ لِي أَبْوَابَ رَحْمَتِكَ", "source": "مسلم"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ مِنْ فَضْلِكَ", "source": "مسلم"},
        {"text": "سُبْحَانَ اللَّهِ وَالْحَمْدُ لِلَّهِ وَلَا إِلَهَ إِلَّا اللَّهُ وَاللَّهُ أَكْبَرُ", "source": "البخاري"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ بِأَنَّ لَكَ الْحَمْدُ لَا إِلَهَ إِلَّا أَنْتَ", "source": "أحمد"},
        {"text": "اللَّهُمَّ اجْعَلْنَا مِنَ الَّذِينَ يَسْتَمِعُونَ الْقَوْلَ فَيَتَّبِعُونَ أَحْسَنَهُ", "source": "الزمر 18"},
    ],
    "<3 الطمأنينة": [
        {"text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ", "source": "البخاري"},
        {"text": "حَسْبِيَ اللَّهُ لَا إِلَهَ إِلَّا هُوَ عَلَيْهِ تَوَكَّلْتُ", "source": "التوبة 129"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ رُوحَ الرَّاحَةِ وَالسَّكِينَةَ", "source": "ابن حبان"},
        {"text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْجُوعِ وَالْفَقْرِ", "source": "أبو داود"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْيُسْرَ بَعْدَ الْعُسْرِ", "source": "أحمد"},
    ],
}

# ========== أدعية المناسبات ==========
OCCASIONS = {
    "🌙 رمضان": [
        {"text": "اللَّهُمَّ بَلِّغْنَا رَمَضَانَ وَأَعِنَّا عَلَى صِيَامِهِ وَقِيَامِهِ", "source": "دعاء رمضان"},
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ بِرَحْمَتِكَ الَّتِي وَسِعَتْ كُلَّ شَيْءٍ أَنْ تَغْفِرَ لِي", "source": "دعاء رمضان"},
        {"text": "اللَّهُمَّ أَعِتْ رِقَابَنَا مِنَ النَّارِ فِي هَذَا الشَّهْرِ الْكَرِيمِ", "source": "دعاء رمضان"},
        {"text": "اللَّهُمَّ اجْعَلْنَا فِي هَذَا الشَّهْرِ مِنَ الْمُسْتَغْفِرِينَ وَالْمُتَّقِينَ", "source": "دعاء رمضان"},
    ],
    "🎉 العيد": [
        {"text": "تَقَبَّلَ اللَّهُ مِنَّا وَمِنْكُمْ", "source": "دعاء العيد"},
        {"text": "اللَّهُمَّ أَعِدْ عَلَيْنَا هَذَا الْيَوْمَ بِالْخَيْرِ وَالْبَرَكَةِ", "source": "دعاء العيد"},
        {"text": "اللَّهُمَّ اجْعَلْنَا مِنَ الْعَائِدِينَ الْفَائِزِينَ", "source": "دعاء العيد"},
    ],
    "⬛ الحج والعمرة": [
        {"text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ حَجًّا مَبْرُورًا وَسَعْيًا مَشْكُورًا", "source": "دعاء الحج"},
        {"text": "اللَّهُمَّ اغْفِرْ لِلْحَاجِّ وَلِمَنِ اسْتَغْفَرَ لَهُ", "source": "دعاء الحج"},
        {"text": "اللَّهُمَّ تَقَبَّلْ مِنَ الْحُجَّاجِ وَاعْفُ عَنْهُمْ", "source": "دعاء الحج"},
    ],
    "📅 الجمعة": [
        {"text": "اللَّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَعَلَى آلِ مُحَمَّدٍ", "source": "دعاء الجمعة"},
        {"text": "اللَّهُمَّ اغْفِرْ لِلْمُؤْمِنِينَ وَالْمُؤْمِنَاتِ", "source": "دعاء الجمعة"},
        {"text": "اللَّهُمَّ أَعِزَّ الْإِسْلَامَ وَالْمُسْلِمِينَ", "source": "دعاء الجمعة"},
    ],
    "💑 الزواج": [
        {"text": "اللَّهُمَّ بَارِكْ لَهُمَا وَبَارِكْ عَلَيْهِمَا وَاجْمَعْ بَيْنَهُمَا فِي خَيْرٍ", "source": "دعاء الزواج"},
        {"text": "اللَّهُمَّ أَلِّفْ بَيْنَ قُلُوبِهِمَا وَاجْعَلْ بَيْنَهُمَا مَوَدَّةً وَرَحْمَةً", "source": "دعاء الزواج"},
        {"text": "اللَّهُمَّ ارْزُقْهُمَا الذُّرِّيَّةَ الصَّالِحَةَ", "source": "دعاء الزواج"},
    ],
}

# ========== التواريخ الهجرية للمناسبات ==========
OCCASION_DATES = {
    "🌙 رمضان": {"hijri": (9, 1), "gregorian": (3, 10)},
    "🎉 العيد": {"hijri": (10, 1), "gregorian": (4, 10)},
    "⬛ الحج والعمرة": {"hijri": (12, 1), "gregorian": (6, 10)},
    "📅 الجمعة": {"special": "friday"},
    "💑 الزواج": {"special": "any"},
}

# ========== التاريخ الهجري ==========
H_MONTHS = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة",
            "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]

def gregorian_to_hijri(g_date: date):
    jd = g_date.toordinal() + 1721424.5
    jd = int(jd) + 0.5
    l_ = int(jd) - 1948440 + 10632
    n_ = (l_ - 1) // 10631
    l_ = l_ - 10631 * n_ + 354
    j_ = ((10985 - l_) // 5316) * ((50 * l_) // 17719) + (l_ // 5670) * ((43 * l_) // 15238)
    l_ = l_ - ((30 - j_) // 15) * ((17719 * j_) // 50) - (j_ // 16) * ((15238 * j_) // 43) + 29
    month = (24 * l_) // 709
    day = l_ - (709 * month) // 24
    year = 30 * n_ + j_ - 30
    month = max(1, min(12, month))
    day = max(1, day)
    return int(day), H_MONTHS[month - 1], int(year)

def get_hijri_date_str():
    d, m, y = gregorian_to_hijri(date.today())
    return f"# {d} {m} {y} هـ"

# ========== التخزين ==========
def get_storage_path():
    try:
        app = App.get_running_app()
        base = app.user_data_dir if app else "."
    except Exception:
        base = "."
    return os.path.join(base, "subhan_data.json")

def get_custom_storage_path():
    try:
        app = App.get_running_app()
        base = app.user_data_dir if app else "."
    except Exception:
        base = "."
    return os.path.join(base, "custom_azkar.json")

DEFAULT_DATA = {
    "target": 33,
    "count": 0,
    "yesterday": 0,
    "total_all_time": 0,
    "last_active_date": str(date.today()),
    "favorites": [],
    "last_zikr": "سبحان الله",
    "night_mode": False,
    "auto_night_mode": True,
    "notifications_enabled": True,
    "notification_time": "08:00",
    "notification_prayer": False,
    "achievements": [],
    "sound_enabled": True,
    "vibration_enabled": True,
    "auto_reset": True,
    "recent_azkar": [],
    "custom_azkar": [],
    "custom_duaa": [],
}

def load_data():
    path = get_storage_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in DEFAULT_DATA.items():
            data.setdefault(k, v)
        return check_daily_reset(data)
    except Exception:
        return dict(DEFAULT_DATA)

def save_data(data):
    path = get_storage_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        logger.error(f"خطأ أثناء حفظ البيانات: {e}")

def check_daily_reset(data):
    today_str = str(date.today())
    if data.get("last_active_date") != today_str:
        data["yesterday"] = data.get("count", 0)
        if data.get("auto_reset", True):
            data["count"] = 0
        data["last_active_date"] = today_str
        save_data(data)
    return data

def send_daily_notification():
    if not HAS_NOTIFICATION:
        return
    data = load_data()
    if not data.get("notifications_enabled", True):
        return
    try:
        notification.notify(
            title="* سُبْحَان",
            message="لا تنسى ذكر الله اليوم! سبحان الله وبحمده",
            timeout=10,
            app_name="سُبْحَان"
        )
    except Exception as e:
        logger.error(f"خطأ في الإشعار: {e}")

# ========== الإنجازات ==========
ACHIEVEMENTS = {
    "first_zikr": {"name": "بداية مباركة", "description": "أول تسبيحة", "icon": "🌟"},
    "ten_zikr": {"name": "عشرة تسبيحات", "description": "10 تسبيحات", "icon": "🔟"},
    "hundred_zikr": {"name": "مئة تسبيحة", "description": "100 تسبيحة", "icon": "💯"},
    "thousand_zikr": {"name": "ألف تسبيحة", "description": "1000 تسبيحة", "icon": "✨"},
    "ten_thousand_zikr": {"name": "عشرة آلاف", "description": "10000 تسبيحة", "icon": "👑"},
    "daily_goal": {"name": "هدف اليوم", "description": "إكمال الهدف اليومي", "icon": "🎯"},
    "seven_days": {"name": "أسبوع من الذكر", "description": "7 أيام متتالية", "icon": "📅"},
    "month_zikr": {"name": "شهر من الذكر", "description": "شهر من التسبيح", "icon": "🌙"},
}

def check_achievements(data):
    unlocked = []
    achievements_data = {
        "first_zikr": data.get("total_all_time", 0) >= 1,
        "ten_zikr": data.get("total_all_time", 0) >= 10,
        "hundred_zikr": data.get("total_all_time", 0) >= 100,
        "thousand_zikr": data.get("total_all_time", 0) >= 1000,
        "ten_thousand_zikr": data.get("total_all_time", 0) >= 10000,
        "daily_goal": data.get("count", 0) >= data.get("target", 33),
        "seven_days": data.get("total_all_time", 0) >= 33 * 7,
        "month_zikr": data.get("total_all_time", 0) >= 33 * 30,
    }
    for key, achieved in achievements_data.items():
        if achieved and key not in data.get("achievements", []):
            unlocked.append(ACHIEVEMENTS[key])
    return unlocked

def show_achievement_popup(achievement, app):
    content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
    content.add_widget(styled_label(
        text=f"{achievement['icon']} {achievement['name']}",
        bold=True, color=current_colors["accent"], font_size="24sp"
    ))
    content.add_widget(styled_label(
        text=achievement["description"],
        color=current_colors["text"], font_size="16sp"
    ))
    btn = styled_button("رائع!", bg=current_colors["primary"], size_hint_y=None, height=dp(45))
    content.add_widget(btn)
    popup = Popup(title="🎉 إنجاز جديد!", content=content, size_hint=(0.8, 0.5), auto_dismiss=True)
    btn.bind(on_release=popup.dismiss)
    popup.open()

# ========== دوال مساعدة ==========
def styled_button(text, bg=None, color=None, bold=False, **kwargs):
    if bg is None:
        bg = current_colors["primary"]
    if color is None:
        color = current_colors["text"]

    # إن كان النص بالكامل إيموجي (بلا نص عربي مصاحب)، نستخدم خط الإيموجي مباشرة
    is_pure_emoji = bool(EMOJI_FONT and text and not _EMOJI_PATTERN.sub("", text).strip())

    btn = Button(
        text=text if is_pure_emoji else ar(text),
        background_normal="",
        background_down="",
        background_color=bg,
        color=color,
        **kwargs
    )
    if is_pure_emoji:
        btn.font_name = EMOJI_FONT
    elif bold and FONT_BOLD:
        btn.font_name = FONT_BOLD
    elif FONT_REGULAR:
        btn.font_name = FONT_REGULAR
    return btn

class EmojiLabel(BoxLayout):
    """يحاكي واجهة Label (خاصية .text قابلة للقراءة/الكتابة، .color)
    لكنه يعرض الإيموجي بخط منفصل عن النص العربي.
    يمكن استخدامه في كل مكان بدل Label بأمان تام، بما في ذلك
    التحديث الديناميكي عبر widget.text = "نص جديد"."""

    def __init__(self, text="", bold=False, color=None, font_size="14sp",
                 halign="right", **kwargs):
        size_hint_y = kwargs.pop("size_hint_y", None)
        height = kwargs.pop("height", None)
        super().__init__(orientation="horizontal", spacing=dp(4), **kwargs)
        if size_hint_y is not None:
            self.size_hint_y = size_hint_y
        if height is not None:
            self.height = height
        elif size_hint_y is None:
            self.size_hint_y = None
            self.height = dp(28)

        self._bold = bold
        self._color = color if color is not None else current_colors["text"]
        self._font_size = font_size
        self._halign = halign
        self._text = ""
        self.text = text  # يستدعي setter الذي يبني العناصر

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value or ""
        self.clear_widgets()
        parts = split_emoji_text(self._text)
        if self._halign == "right":
            parts = list(reversed(parts))

        if not parts:
            return

        for kind, chunk in parts:
            if kind == "text" and not chunk.strip():
                continue
            if kind == "emoji" and EMOJI_FONT:
                sub = Label(text=chunk, font_size=self._font_size, size_hint_x=None)
                sub.font_name = EMOJI_FONT
                sub.texture_update()
                sub.width = sub.texture_size[0] if sub.texture_size[0] else dp(24)
            else:
                # إيموجي بدون خط متاح، أو نص عادي: نعرضه كنص عربي عادي
                display_text = chunk if kind == "emoji" else ar(chunk)
                sub = Label(text=display_text, color=self._color,
                            font_size=self._font_size, halign=self._halign)
                if self._bold and FONT_BOLD:
                    sub.font_name = FONT_BOLD
                elif FONT_REGULAR:
                    sub.font_name = FONT_REGULAR
            self.add_widget(sub)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        # نعيد بناء العناصر لتطبيق اللون الجديد على أجزاء النص
        self.text = self._text


def styled_label(text, bold=False, **kwargs):
    kwargs.setdefault("halign", "right")

    # إن لم يحتوِ النص إيموجي، أو لم يتوفر خط الإيموجي، نستخدم Label بسيط كالسابق
    if not EMOJI_FONT or not _EMOJI_PATTERN.search(text or ""):
        lbl = Label(text=ar(text), **kwargs)
        if bold and FONT_BOLD:
            lbl.font_name = FONT_BOLD
        elif FONT_REGULAR:
            lbl.font_name = FONT_REGULAR
        return lbl

    # النص يحتوي إيموجي: نستخدم EmojiLabel الذي يحاكي واجهة Label بأمان
    return EmojiLabel(text=text, bold=bold, **kwargs)

def animate_card(card, delay=0):
    def _animate(dt):
        card.opacity = 0
        anim = Animation(opacity=1, duration=0.3)
        anim.start(card)
    if delay:
        Clock.schedule_once(_animate, delay)
    else:
        _animate(0)

def share_zikr(text):
    share_text = f"* {text}\n\nشارك معنا على تطبيق سُبْحَان"
    if HAS_SHARE:
        try:
            share.share(text=share_text)
            return True
        except Exception:
            pass
    if HAS_CLIPBOARD:
        try:
            clipboard.copy(text)
            return True
        except Exception:
            pass
    return False

def set_screen(name):
    app = App.get_running_app()
    sm = app.sm
    sm.current = name

# ========== شاشة البطاقات المخصصة ==========
class AnimatedCard(BoxLayout):
    """بطاقة متحركة مع تأثيرات"""
    scale = NumericProperty(1)
    bg_color = ColorProperty((0, 0, 0, 0))
    radius = NumericProperty(14)

    def __init__(self, bg_color=None, radius=dp(14), elevation=True, **kwargs):
        if bg_color is None:
            bg_color = current_colors["card"]
        super().__init__(**kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.elevation = elevation
        self.opacity = 0
        
        with self.canvas.before:
            if elevation:
                Color(0, 0, 0, 0.15)
                self._shadow_rect = RoundedRectangle(
                    pos=(self.x + dp(2), self.y - dp(2)),
                    size=(self.width - dp(4), self.height + dp(4)),
                    radius=[radius]
                )
            Color(*bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        # تأثير توهج خفيف
        self.glow_anim = Animation(bg_color=(bg_color[0]+0.05, bg_color[1]+0.05, bg_color[2]+0.05, 1), duration=0.5)
        self.glow_anim += Animation(bg_color=bg_color, duration=0.5)
        self.glow_anim.repeat = True
        Clock.schedule_once(lambda dt: self.glow_anim.start(self), 1)
    
    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        if hasattr(self, '_shadow_rect'):
            self._shadow_rect.pos = (self.x + dp(2), self.y - dp(2))
            self._shadow_rect.size = (self.width - dp(4), self.height + dp(4))
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(scale=0.97, duration=0.1)
            anim.start(self)
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(scale=1, duration=0.1)
            anim.start(self)
        return super().on_touch_up(touch)

# ========== الشاشات ==========
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        self._particle_effect = None
        self._sparkle_effect = None
    
    def build_ui(self):
        self.clear_widgets()
        data = load_data()
        
        main_layout = FloatLayout()
        
        # خلفية متحركة
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        # تأثيرات
        self._particle_effect = ParticleEffect()
        main_layout.add_widget(self._particle_effect)
        self._sparkle_effect = SparkleEffect()
        main_layout.add_widget(self._sparkle_effect)
        
        # محتوى رئيسي
        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12))
        layout.size_hint = (1, 1)
        
        # الهيدر مع تأثير بريق
        header = BoxLayout(size_hint_y=None, height=dp(50))
        title = styled_label(text="✨ سُبْحَان ✨", bold=True, color=current_colors["accent"], font_size="28sp")
        header.add_widget(title)
        
        btn_search = styled_button("🔍", bg=(0,0,0,0), size_hint_x=None, width=dp(45))
        btn_search.bind(on_release=lambda x: set_screen("search"))
        header.add_widget(btn_search)
        
        btn_favorites = styled_button("❤️", bg=(0,0,0,0), size_hint_x=None, width=dp(45))
        btn_favorites.bind(on_release=lambda x: set_screen("favorites"))
        header.add_widget(btn_favorites)
        
        btn_settings = styled_button("🔧", bg=(0,0,0,0), size_hint_x=None, width=dp(50))
        btn_settings.bind(on_release=lambda x: set_screen("settings"))
        header.add_widget(btn_settings)
        layout.add_widget(header)
        
        # سكرول المحتوى
        scroll = ScrollView(effect_cls=ScrollEffect)
        content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # بطاقة التاريخ مع توهج
        card1 = AnimatedCard(orientation="vertical", size_hint_y=None, height=dp(110), padding=dp(12), spacing=dp(4))
        card1.add_widget(styled_label(text="۩ بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", bold=True, color=current_colors["accent"]))
        card1.add_widget(styled_label(text=get_hijri_date_str(), color=current_colors["text"]))
        card1.add_widget(styled_label(text=date.today().strftime("%Y-%m-%d"), color=current_colors["text_muted"], font_size="12sp"))
        content.add_widget(card1)
        animate_card(card1, 0.1)
        
        # الإحصائيات
        stats = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(80))
        stats.add_widget(self._stat_box("🌟 اليوم", data.get("count", 0)))
        stats.add_widget(self._stat_box("📅 الأمس", data.get("yesterday", 0)))
        stats.add_widget(self._stat_box("🏆 الإجمالي", data.get("total_all_time", 0)))
        stats.add_widget(self._stat_box("❤️ المفضلة", len(data.get("favorites", []))))
        content.add_widget(stats)
        
        # شريط التقدم
        target = max(data.get("target", 33), 1)
        count = data.get("count", 0)
        pct = min(count * 100 // target, 100)
        target_box = AnimatedCard(orientation="vertical", size_hint_y=None, height=dp(90), padding=dp(12), spacing=dp(6))
        target_box.add_widget(styled_label(text="🎯 الهدف اليومي", color=current_colors["text"], bold=True))
        prog = ProgressBar(max=100, value=pct, size_hint_y=None, height=dp(14))
        target_box.add_widget(prog)
        target_box.add_widget(styled_label(text=f"+ {count} / {target}  ({pct}%)", color=current_colors["text_muted"], font_size="12sp"))
        content.add_widget(target_box)
        animate_card(target_box, 0.2)
        
        # دعاء اليوم مع تأثير
        all_duas = [d for cat in ADIYA.values() for d in cat]
        dua_of_day = all_duas[date.today().toordinal() % len(all_duas)]
        dua_box = AnimatedCard(orientation="vertical", size_hint_y=None, height=dp(120), padding=dp(12), spacing=dp(6))
        dua_box.add_widget(styled_label(text="🌙 دعاء اليوم", bold=True, color=current_colors["accent"]))
        dua_box.add_widget(styled_label(
            text=dua_of_day["text"], color=current_colors["text"], halign="center",
            text_size=(Window.width - dp(60), None)
        ))
        content.add_widget(dua_box)
        animate_card(dua_box, 0.3)
        
        # آخر ذكر
        last_zikr = data.get("last_zikr", "سبحان الله")
        last_box = AnimatedCard(orientation="vertical", size_hint_y=None, height=dp(60), padding=dp(10))
        last_box.add_widget(styled_label(
            text=f"📝 آخر ذكر: {last_zikr}",
            color=current_colors["text_muted"],
            font_size="14sp"
        ))
        content.add_widget(last_box)
        animate_card(last_box, 0.4)
        
        # الأزرار الرئيسية - بتأثير نبض
        btns = GridLayout(cols=3, spacing=dp(10), size_hint_y=None, height=dp(70))
        b1 = AnimatedButton(text="✨\nالمسبحة", bg_color=current_colors["primary"], bold=1, font_size=dp(14))
        b1.bind(on_press=lambda x: set_screen("tasbih"))
        btns.add_widget(b1)
        
        b2 = AnimatedButton(text="📖\nالأذكار", bg_color=current_colors["primary"], bold=1, font_size=dp(14))
        b2.bind(on_press=lambda x: set_screen("azkar"))
        btns.add_widget(b2)
        
        b3 = AnimatedButton(text="🙏\nالأدعية", bg_color=current_colors["primary"], bold=1, font_size=dp(14))
        b3.bind(on_press=lambda x: set_screen("duaa"))
        btns.add_widget(b3)
        content.add_widget(btns)
        
        # أزرار إضافية
        extra_btns = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(60))
        b4 = AnimatedButton(text="⏰\nمؤقت", bg_color=current_colors["card"], font_size=dp(11))
        b4.bind(on_press=lambda x: set_screen("timer"))
        b5 = AnimatedButton(text="📊\nإحصاءات", bg_color=current_colors["card"], font_size=dp(11))
        b5.bind(on_press=lambda x: set_screen("stats"))
        b6 = AnimatedButton(text="🔍\nبحث", bg_color=current_colors["card"], font_size=dp(11))
        b6.bind(on_press=lambda x: set_screen("search"))
        b7 = AnimatedButton(text="ℹ️\nعن التطبيق", bg_color=current_colors["card"], font_size=dp(11))
        b7.bind(on_press=lambda x: set_screen("about"))
        extra_btns.add_widget(b4)
        extra_btns.add_widget(b5)
        extra_btns.add_widget(b6)
        extra_btns.add_widget(b7)
        content.add_widget(extra_btns)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        main_layout.add_widget(layout)
        self.add_widget(main_layout)
    
    def _stat_box(self, title, value):
        box = AnimatedCard(orientation="vertical", padding=dp(6))
        box.add_widget(styled_label(text=title, color=current_colors["text_muted"], font_size="10sp"))
        box.add_widget(styled_label(text=str(value), color=current_colors["text"], bold=True, font_size="16sp"))
        return box
    
    def on_enter(self):
        self.build_ui()

class TasbihScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target = 33
        self.count = 0
        self.zikr = "سبحان الله"
        self.build_ui()
        self._particle_effect = None
        self._timer = None

    def build_ui(self):
        self.clear_widgets()
        
        main_layout = FloatLayout()
        
        # خلفية
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        # تأثير الجزيئات
        self._particle_effect = ParticleEffect()
        main_layout.add_widget(self._particle_effect)
        
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        layout.size_hint = (1, 1)

        top = BoxLayout(size_hint_y=None, height=dp(50))
        back = AnimatedButton(text="< رجوع", bg_color=(0,0,0,0), font_size=dp(14))
        back.bind(on_press=lambda x: set_screen("home"))
        top.add_widget(back)
        layout.add_widget(top)

        # الذكر الحالي
        self.zikr_label = styled_label(text=self.zikr, bold=True, font_size="24sp", color=current_colors["accent"])
        layout.add_widget(self.zikr_label)

        # العداد بلون متغير
        color = get_counter_color(self.count)
        self.counter_label = styled_label(text=str(self.count), font_size="64sp", bold=True, color=color)
        layout.add_widget(self.counter_label)

        self.target_label = styled_label(text=f"🎯 الهدف: {self.target}", color=current_colors["text_muted"])
        layout.add_widget(self.target_label)

        # أزرار الهدف
        target_box = GridLayout(cols=4, spacing=dp(5), size_hint_y=None, height=dp(45))
        for t in [33, 66, 99, 100]:
            b = AnimatedButton(text=str(t), bg_color=current_colors["card"])
            b.bind(on_press=lambda x, val=t: self.set_target(val))
            target_box.add_widget(b)
        layout.add_widget(target_box)

        # أزرار الأذكار
        zikr_box = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(100))
        for z in ["سبحان الله", "الحمد لله", "الله أكبر", "لا إله إلا الله"]:
            b = AnimatedButton(text=z, bg_color=current_colors["card"])
            b.bind(on_press=lambda x, val=z: self.change_zikr(val))
            zikr_box.add_widget(b)
        layout.add_widget(zikr_box)

        # زر التسبيح الرئيسي
        main_btn = AnimatedButton(
            text="✨ تسبيح ✨",
            bg_color=current_colors["primary"],
            bold=1,
            font_size=dp(22),
            height=dp(90)
        )
        main_btn.bind(on_press=lambda x: self.increment())
        layout.add_widget(main_btn)

        # أزرار التحكم
        ctrl = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(50))
        reset_btn = AnimatedButton(text="🔄 إعادة", bg_color=current_colors["danger"])
        reset_btn.bind(on_press=lambda x: self.reset())
        ctrl.add_widget(reset_btn)
        
        share_btn = AnimatedButton(text="📤 مشاركة", bg_color=current_colors["accent"])
        share_btn.bind(on_press=lambda x: self.share_current())
        ctrl.add_widget(share_btn)
        layout.add_widget(ctrl)

        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def set_target(self, val):
        self.target = val
        self.target_label.text = ar(f"🎯 الهدف: {self.target}")

    def change_zikr(self, z):
        self.zikr = z
        self.zikr_label.text = ar(z)
        # إضافة للحديث
        data = load_data()
        recent = data.get("recent_azkar", [])
        if z in recent:
            recent.remove(z)
        recent.insert(0, z)
        if len(recent) > 5:
            recent = recent[:5]
        data["recent_azkar"] = recent
        save_data(data)

    def _vibrate(self, ms=30):
        data = load_data()
        if not data.get("vibration_enabled", True):
            return
        if HAS_VIBRATOR:
            try:
                vibrator.vibrate(ms / 1000)
            except Exception:
                pass

    def increment(self):
        self.count += 1
        color = get_counter_color(self.count)
        self.counter_label.color = color
        self.counter_label.text = str(self.count)
        
        # تأثير تكبير (نحرك حجم الخط بدل scale لأن Label لا يملك خاصية scale)
        try:
            base_size = 64
            anim = Animation(font_size=str(base_size * 1.15) + "sp", duration=0.1) + \
                   Animation(font_size=str(base_size) + "sp", duration=0.1)
            anim.start(self.counter_label)
        except Exception:
            pass
        
        # تأثير جزيئات
        if self._particle_effect:
            pos = (Window.width/2, Window.height/2)
            self._particle_effect.burst(pos, color)
        
        self._vibrate()
        
        if self.target > 0 and self.count >= self.target:
            self._commit(self.count)
            self.count = 0
            self.counter_label.text = "0"
            self.counter_label.color = get_counter_color(0)
            self._vibrate(120)
            # تأثير إكمال
            self.target_label.text = ar("🎉 أكملت الهدف! 🎉")
            Clock.schedule_once(lambda dt: self.target_label.__setattr__("text", ar(f"🎯 الهدف: {self.target}")), 2)

    def reset(self):
        if self.count > 0:
            self._commit(self.count)
        self.count = 0
        self.counter_label.text = "0"
        self.counter_label.color = get_counter_color(0)

    def _commit(self, amount):
        if amount <= 0:
            return
        data = load_data()
        data["count"] = data.get("count", 0) + amount
        data["total_all_time"] = data.get("total_all_time", 0) + amount
        data["last_zikr"] = self.zikr
        save_data(data)
        
        # التحقق من الإنجازات
        unlocked = check_achievements(data)
        if unlocked:
            for achievement in unlocked:
                data["achievements"] = data.get("achievements", []) + [achievement["name"]]
                save_data(data)
                Clock.schedule_once(lambda dt, a=achievement: show_achievement_popup(a, self), 0.5)

    def share_current(self):
        share_zikr(self.zikr)

    def on_enter(self):
        self.count = 0
        if hasattr(self, "counter_label"):
            self.counter_label.text = "0"
            self.counter_label.color = get_counter_color(0)

    def on_leave(self):
        if self.count > 0:
            self._commit(self.count)
            self.count = 0

class AzkarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_cat = "* الصباح"
        self.menu_open = False
        self.build_ui()
        self._search_timer = None

    def build_ui(self, category=None):
        if category:
            self.current_cat = category
        self.clear_widgets()
        
        main_layout = FloatLayout()
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        # قائمة جانبية
        self.side_menu = self.create_side_menu()
        self.side_menu.width = 0
        main_layout.add_widget(self.side_menu)
        
        # المحتوى الرئيسي
        layout = BoxLayout(orientation="vertical")
        layout.size_hint = (1, 1)

        top = BoxLayout(size_hint_y=None, height=dp(50), padding=(dp(10), dp(5)))
        
        menu_btn = AnimatedButton(text="📋", bg_color=(0,0,0,0), size_hint_x=None, width=dp(50))
        menu_btn.bind(on_press=self.toggle_menu)
        top.add_widget(menu_btn)
        
        title = styled_label(self.current_cat, bold=True, color=current_colors["accent"], font_size="18sp")
        top.add_widget(title)
        
        back = AnimatedButton(text="<", bg_color=(0,0,0,0), size_hint_x=None, width=dp(50))
        back.bind(on_press=lambda x: set_screen("home"))
        top.add_widget(back)
        layout.add_widget(top)

        # شريط بحث
        search_box = BoxLayout(size_hint_y=None, height=dp(45), padding=(dp(6), dp(4)))
        self.search_input = TextInput(
            hint_text="🔍 ابحث في الأذكار...",
            size_hint_x=0.9,
            height=dp(40),
            multiline=False,
            background_color=current_colors["card"],
            foreground_color=current_colors["text"],
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        self.search_input.bind(text=self.on_search)
        search_box.add_widget(self.search_input)
        
        clear_btn = AnimatedButton(text="❌", bg_color=(0,0,0,0), size_hint_x=None, width=dp(40))
        clear_btn.bind(on_press=lambda x: self.clear_search())
        search_box.add_widget(clear_btn)
        layout.add_widget(search_box)

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # عرض الأذكار المخصصة أولاً إذا كان التصنيف هو "📝 أذكاري"
        items = []
        if self.current_cat == "📝 أذكاري":
            data = load_data()
            custom = data.get("custom_azkar", [])
            for item in custom:
                items.append({"text": item.get("text", ""), "count": item.get("count", 1), "custom": True})
        else:
            items = AZKAR.get(self.current_cat, [])
        
        if hasattr(self, 'search_text') and self.search_text:
            items = [item for item in items if self.search_text in item["text"]]
        
        if not items:
            content.add_widget(styled_label(
                text="لا توجد نتائج",
                color=current_colors["text_muted"],
                size_hint_y=None,
                height=dp(50)
            ))
        
        for idx, item in enumerate(items):
            card = self._zikr_card(item)
            content.add_widget(card)
            animate_card(card, idx * 0.05)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def create_side_menu(self):
        menu = BoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=dp(250),
            padding=dp(10),
            spacing=dp(5)
        )
        
        with menu.canvas.before:
            Color(*current_colors["card"])
            menu.rect = RoundedRectangle(pos=menu.pos, size=menu.size, radius=[0, dp(14), dp(14), 0])
        menu.bind(pos=self._update_menu_rect, size=self._update_menu_rect)
        
        menu.add_widget(styled_label(
            "📖 الأذكار",
            bold=True,
            color=current_colors["accent"],
            font_size="18sp",
            size_hint_y=None,
            height=dp(40)
        ))
        
        # تصنيفات الأذكار
        for cat in AZKAR:
            is_active = cat == self.current_cat
            btn = AnimatedButton(
                text=cat,
                bg_color=current_colors["primary"] if is_active else current_colors["card"],
                font_size=dp(13),
                height=dp(40)
            )
            btn.bind(on_press=lambda x, c=cat: self.select_category(c))
            menu.add_widget(btn)
        
        # إضافة تصنيف الأذكار المخصصة
        is_active = self.current_cat == "📝 أذكاري"
        btn = AnimatedButton(
            text="📝 أذكاري",
            bg_color=current_colors["primary"] if is_active else current_colors["card"],
            font_size=dp(13),
            height=dp(40)
        )
        btn.bind(on_press=lambda x: self.select_category("📝 أذكاري"))
        menu.add_widget(btn)
        
        # زر إضافة ذكر جديد
        add_btn = AnimatedButton(
            text="➕ إضافة ذكر",
            bg_color=current_colors["success"],
            font_size=dp(13),
            height=dp(40)
        )
        add_btn.bind(on_press=lambda x: self.show_add_zikr_popup())
        menu.add_widget(add_btn)
        
        close_btn = AnimatedButton(
            text="❌ إغلاق",
            bg_color=current_colors["danger"],
            font_size=dp(13),
            height=dp(40)
        )
        close_btn.bind(on_press=self.toggle_menu)
        menu.add_widget(close_btn)
        
        return menu

    def _update_menu_rect(self, *args):
        if hasattr(self.side_menu, 'rect'):
            self.side_menu.rect.pos = self.side_menu.pos
            self.side_menu.rect.size = self.side_menu.size

    def toggle_menu(self, *args):
        self.menu_open = not self.menu_open
        target_width = dp(250) if self.menu_open else 0
        anim = Animation(width=target_width, duration=0.3)
        anim.start(self.side_menu)

    def select_category(self, category):
        self.current_cat = category
        self.menu_open = False
        anim = Animation(width=0, duration=0.3)
        anim.start(self.side_menu)
        self.build_ui(category)

    def on_search(self, instance, value):
        if self._search_timer:
            self._search_timer.cancel()
        self._search_timer = Clock.schedule_once(lambda dt: self.do_search(value), 0.3)

    def do_search(self, value):
        self.search_text = value.strip()
        self.build_ui(self.current_cat)

    def clear_search(self):
        self.search_input.text = ""
        self.search_text = ""
        self.build_ui(self.current_cat)

    def _zikr_card(self, item):
        is_custom = item.get("custom", False)
        card = AnimatedCard(orientation="vertical", size_hint_y=None, height=dp(110), padding=dp(12), spacing=dp(6))
        
        lbl = styled_label(text=item["text"], color=current_colors["text"], halign="center", valign="middle",
                    text_size=(Window.width - dp(60), None))
        card.add_widget(lbl)
        
        bottom = BoxLayout(size_hint_y=None, height=dp(30))
        if item["count"] > 1:
            bottom.add_widget(styled_label(text=f"🔄 التكرار: {item['count']}", color=current_colors["accent"], font_size="12sp"))
        else:
            bottom.add_widget(Widget())
        
        share_btn = AnimatedButton(text="📤", bg_color=(0,0,0,0), size_hint_x=None, width=dp(35))
        share_btn.bind(on_press=lambda x, t=item["text"]: share_zikr(t))
        bottom.add_widget(share_btn)
        
        data = load_data()
        favs = data.get("favorites", [])
        fav_icon = "❤️" if item["text"] in favs else "💙"
        fav_btn = AnimatedButton(text=fav_icon, bg_color=(0,0,0,0), size_hint_x=None, width=dp(40))
        fav_btn.bind(on_press=lambda x, t=item["text"], b=fav_btn: self.toggle_favorite(t, b))
        bottom.add_widget(fav_btn)
        
        if is_custom:
            del_btn = AnimatedButton(text="♻️", bg_color=(0,0,0,0), size_hint_x=None, width=dp(35))
            del_btn.bind(on_press=lambda x, t=item["text"]: self.delete_custom_zikr(t))
            bottom.add_widget(del_btn)
        
        card.add_widget(bottom)
        return card

    def toggle_favorite(self, text, btn):
        data = load_data()
        favs = data.get("favorites", [])
        if text in favs:
            favs.remove(text)
            btn.text = "💙"
        else:
            favs.append(text)
            btn.text = "❤️"
        data["favorites"] = favs
        save_data(data)

    def delete_custom_zikr(self, text):
        data = load_data()
        custom = data.get("custom_azkar", [])
        custom = [item for item in custom if item["text"] != text]
        data["custom_azkar"] = custom
        save_data(data)
        self.build_ui(self.current_cat)

    def show_add_zikr_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))
        
        content.add_widget(styled_label("➕ إضافة ذكر جديد", bold=True, color=current_colors["accent"], font_size="18sp"))
        
        text_input = TextInput(
            hint_text="نص الذكر...",
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            background_color=current_colors["card"],
            foreground_color=current_colors["text"]
        )
        content.add_widget(text_input)
        
        count_input = TextInput(
            hint_text="عدد التكرارات (مثال: 33)",
            input_filter="int",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=current_colors["card"],
            foreground_color=current_colors["text"],
            text="1"
        )
        content.add_widget(count_input)
        
        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        save_btn = AnimatedButton(text="💾 حفظ", bg_color=current_colors["success"])
        cancel_btn = AnimatedButton(text="❌ إلغاء", bg_color=current_colors["danger"])
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)
        
        popup = Popup(title="", content=content, size_hint=(0.9, 0.6), auto_dismiss=False)
        
        def save_callback(x):
            text = text_input.text.strip()
            if not text:
                return
            try:
                count = int(count_input.text) if count_input.text else 1
            except:
                count = 1
            data = load_data()
            custom = data.get("custom_azkar", [])
            custom.append({"text": text, "count": count})
            data["custom_azkar"] = custom
            save_data(data)
            popup.dismiss()
            self.build_ui(self.current_cat)
        
        save_btn.bind(on_press=save_callback)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def on_enter(self):
        self.build_ui(self.current_cat)

class DuaaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_cat = "# قرآنية"
        self.menu_open = False
        self.build_ui()
        self._search_timer = None

    def build_ui(self, category=None):
        if category:
            self.current_cat = category
        self.clear_widgets()
        
        main_layout = FloatLayout()
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        # قائمة جانبية
        self.side_menu = self.create_side_menu()
        self.side_menu.width = 0
        main_layout.add_widget(self.side_menu)
        
        layout = BoxLayout(orientation="vertical")
        layout.size_hint = (1, 1)

        top = BoxLayout(size_hint_y=None, height=dp(50), padding=(dp(10), dp(5)))
        
        menu_btn = AnimatedButton(text="📋", bg_color=(0,0,0,0), size_hint_x=None, width=dp(50))
        menu_btn.bind(on_press=self.toggle_menu)
        top.add_widget(menu_btn)
        
        title = styled_label(self.current_cat, bold=True, color=current_colors["accent"], font_size="18sp")
        top.add_widget(title)
        
        back = AnimatedButton(text="<", bg_color=(0,0,0,0), size_hint_x=None, width=dp(50))
        back.bind(on_press=lambda x: set_screen("home"))
        top.add_widget(back)
        layout.add_widget(top)

        search_box = BoxLayout(size_hint_y=None, height=dp(45), padding=(dp(6), dp(4)))
        self.search_input = TextInput(
            hint_text="🔍 ابحث في الأدعية...",
            size_hint_x=0.9,
            height=dp(40),
            multiline=False,
            background_color=current_colors["card"],
            foreground_color=current_colors["text"],
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        self.search_input.bind(text=self.on_search)
        search_box.add_widget(self.search_input)
        
        clear_btn = AnimatedButton(text="❌", bg_color=(0,0,0,0), size_hint_x=None, width=dp(40))
        clear_btn.bind(on_press=lambda x: self.clear_search())
        search_box.add_widget(clear_btn)
        layout.add_widget(search_box)

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        items = []
        if self.current_cat == "📝 أدعيتي":
            data = load_data()
            custom = data.get("custom_duaa", [])
            for item in custom:
                items.append({"text": item.get("text", ""), "source": item.get("source", "مخصص"), "custom": True})
        elif self.current_cat == "📅 المناسبات":
            items = []
            for cat, duas in OCCASIONS.items():
                for d in duas:
                    items.append({"text": d["text"], "source": f"{cat} - {d.get('source', '')}"})
        else:
            items = ADIYA.get(self.current_cat, [])
        
        if hasattr(self, 'search_text') and self.search_text:
            items = [item for item in items if self.search_text in item["text"]]
        
        if not items:
            content.add_widget(styled_label(
                text="لا توجد نتائج",
                color=current_colors["text_muted"],
                size_hint_y=None,
                height=dp(50)
            ))
        
        for idx, item in enumerate(items):
            card = self._dua_card(item)
            content.add_widget(card)
            animate_card(card, idx * 0.05)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def create_side_menu(self):
        menu = BoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=dp(250),
            padding=dp(10),
            spacing=dp(5)
        )
        
        with menu.canvas.before:
            Color(*current_colors["card"])
            menu.rect = RoundedRectangle(pos=menu.pos, size=menu.size, radius=[0, dp(14), dp(14), 0])
        menu.bind(pos=self._update_menu_rect, size=self._update_menu_rect)
        
        menu.add_widget(styled_label(
            "🙏 الأدعية",
            bold=True,
            color=current_colors["accent"],
            font_size="18sp",
            size_hint_y=None,
            height=dp(40)
        ))
        
        # تصنيفات الأدعية
        for cat in ADIYA:
            is_active = cat == self.current_cat
            btn = AnimatedButton(
                text=cat,
                bg_color=current_colors["primary"] if is_active else current_colors["card"],
                font_size=dp(13),
                height=dp(40)
            )
            btn.bind(on_press=lambda x, c=cat: self.select_category(c))
            menu.add_widget(btn)
        
        # تصنيف المناسبات
        is_active = self.current_cat == "📅 المناسبات"
        btn = AnimatedButton(
            text="📅 المناسبات",
            bg_color=current_colors["primary"] if is_active else current_colors["card"],
            font_size=dp(13),
            height=dp(40)
        )
        btn.bind(on_press=lambda x: self.select_category("📅 المناسبات"))
        menu.add_widget(btn)
        
        # تصنيف الأدعية المخصصة
        is_active = self.current_cat == "📝 أدعيتي"
        btn = AnimatedButton(
            text="📝 أدعيتي",
            bg_color=current_colors["primary"] if is_active else current_colors["card"],
            font_size=dp(13),
            height=dp(40)
        )
        btn.bind(on_press=lambda x: self.select_category("📝 أدعيتي"))
        menu.add_widget(btn)
        
        # زر إضافة دعاء جديد
        add_btn = AnimatedButton(
            text="➕ إضافة دعاء",
            bg_color=current_colors["success"],
            font_size=dp(13),
            height=dp(40)
        )
        add_btn.bind(on_press=lambda x: self.show_add_duaa_popup())
        menu.add_widget(add_btn)
        
        close_btn = AnimatedButton(
            text="❌ إغلاق",
            bg_color=current_colors["danger"],
            font_size=dp(13),
            height=dp(40)
        )
        close_btn.bind(on_press=self.toggle_menu)
        menu.add_widget(close_btn)
        
        return menu

    def _update_menu_rect(self, *args):
        if hasattr(self.side_menu, 'rect'):
            self.side_menu.rect.pos = self.side_menu.pos
            self.side_menu.rect.size = self.side_menu.size

    def toggle_menu(self, *args):
        self.menu_open = not self.menu_open
        target_width = dp(250) if self.menu_open else 0
        anim = Animation(width=target_width, duration=0.3)
        anim.start(self.side_menu)

    def select_category(self, category):
        self.current_cat = category
        self.menu_open = False
        anim = Animation(width=0, duration=0.3)
        anim.start(self.side_menu)
        self.build_ui(category)

    def on_search(self, instance, value):
        if self._search_timer:
            self._search_timer.cancel()
        self._search_timer = Clock.schedule_once(lambda dt: self.do_search(value), 0.3)

    def do_search(self, value):
        self.search_text = value.strip()
        self.build_ui(self.current_cat)

    def clear_search(self):
        self.search_input.text = ""
        self.search_text = ""
        self.build_ui(self.current_cat)

    def _dua_card(self, item):
        is_custom = item.get("custom", False)
        card = AnimatedCard(orientation="vertical", size_hint_y=None, height=dp(130), padding=dp(12), spacing=dp(6))
        
        lbl = styled_label(text=item["text"], color=current_colors["text"], halign="center", valign="middle",
                    text_size=(Window.width - dp(60), None))
        card.add_widget(lbl)
        
        bottom = BoxLayout(size_hint_y=None, height=dp(30))
        source = item.get("source", "")
        if source:
            bottom.add_widget(styled_label(text=f"📖 {source}", color=current_colors["text_muted"], font_size="12sp"))
        else:
            bottom.add_widget(Widget())
        
        share_btn = AnimatedButton(text="📤", bg_color=(0,0,0,0), size_hint_x=None, width=dp(35))
        share_btn.bind(on_press=lambda x, t=item["text"]: share_zikr(t))
        bottom.add_widget(share_btn)
        
        data = load_data()
        favs = data.get("favorites", [])
        fav_icon = "❤️" if item["text"] in favs else "💙"
        fav_btn = AnimatedButton(text=fav_icon, bg_color=(0,0,0,0), size_hint_x=None, width=dp(40))
        fav_btn.bind(on_press=lambda x, t=item["text"], b=fav_btn: self.toggle_favorite(t, b))
        bottom.add_widget(fav_btn)
        
        if is_custom:
            del_btn = AnimatedButton(text="♻️", bg_color=(0,0,0,0), size_hint_x=None, width=dp(35))
            del_btn.bind(on_press=lambda x, t=item["text"]: self.delete_custom_duaa(t))
            bottom.add_widget(del_btn)
        
        card.add_widget(bottom)
        return card

    def toggle_favorite(self, text, btn):
        data = load_data()
        favs = data.get("favorites", [])
        if text in favs:
            favs.remove(text)
            btn.text = "💙"
        else:
            favs.append(text)
            btn.text = "❤️"
        data["favorites"] = favs
        save_data(data)

    def delete_custom_duaa(self, text):
        data = load_data()
        custom = data.get("custom_duaa", [])
        custom = [item for item in custom if item["text"] != text]
        data["custom_duaa"] = custom
        save_data(data)
        self.build_ui(self.current_cat)

    def show_add_duaa_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))
        
        content.add_widget(styled_label("🙏 إضافة دعاء جديد", bold=True, color=current_colors["accent"], font_size="18sp"))
        
        text_input = TextInput(
            hint_text="نص الدعاء...",
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            background_color=current_colors["card"],
            foreground_color=current_colors["text"]
        )
        content.add_widget(text_input)
        
        source_input = TextInput(
            hint_text="المصدر (اختياري)...",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=current_colors["card"],
            foreground_color=current_colors["text"]
        )
        content.add_widget(source_input)
        
        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        save_btn = AnimatedButton(text="💾 حفظ", bg_color=current_colors["success"])
        cancel_btn = AnimatedButton(text="❌ إلغاء", bg_color=current_colors["danger"])
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)
        
        popup = Popup(title="", content=content, size_hint=(0.9, 0.6), auto_dismiss=False)
        
        def save_callback(x):
            text = text_input.text.strip()
            if not text:
                return
            source = source_input.text.strip() or "مخصص"
            data = load_data()
            custom = data.get("custom_duaa", [])
            custom.append({"text": text, "source": source})
            data["custom_duaa"] = custom
            save_data(data)
            popup.dismiss()
            self.build_ui(self.current_cat)
        
        save_btn.bind(on_press=save_callback)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def on_enter(self):
        self.build_ui(self.current_cat)

class FavoritesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        data = load_data()
        favorites = data.get("favorites", [])
        
        main_layout = FloatLayout()
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12))
        layout.size_hint = (1, 1)
        
        top = BoxLayout(size_hint_y=None, height=dp(50))
        back = AnimatedButton(text="< رجوع", bg_color=(0,0,0,0))
        back.bind(on_press=lambda x: set_screen("home"))
        top.add_widget(back)
        layout.add_widget(top)
        
        layout.add_widget(styled_label(
            "❤️ المفضلة",
            bold=True,
            color=current_colors["accent"],
            font_size="24sp",
            size_hint_y=None,
            height=dp(50)
        ))
        
        if not favorites:
            layout.add_widget(styled_label(
                "لا توجد عناصر مفضلة",
                color=current_colors["text_muted"],
                font_size="16sp",
                size_hint_y=None,
                height=dp(100)
            ))
        else:
            scroll = ScrollView()
            content = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
            content.bind(minimum_height=content.setter('height'))
            
            for idx, item in enumerate(favorites):
                card = AnimatedCard(orientation="vertical", size_hint_y=None, height=dp(80), padding=dp(12), spacing=dp(4))
                
                lbl = styled_label(
                    item[:60] + "..." if len(item) > 60 else item,
                    color=current_colors["text"],
                    font_size="14sp",
                    halign="center",
                    text_size=(Window.width - dp(80), None)
                )
                card.add_widget(lbl)
                
                bottom = BoxLayout(size_hint_y=None, height=dp(25))
                bottom.add_widget(Widget())
                
                remove_btn = AnimatedButton(text="❌", bg_color=(0,0,0,0), size_hint_x=None, width=dp(35))
                remove_btn.bind(on_press=lambda x, t=item: self.remove_from_favorites(t))
                bottom.add_widget(remove_btn)
                
                share_btn = AnimatedButton(text="📤", bg_color=(0,0,0,0), size_hint_x=None, width=dp(35))
                share_btn.bind(on_press=lambda x, t=item: share_zikr(t))
                bottom.add_widget(share_btn)
                
                card.add_widget(bottom)
                content.add_widget(card)
                animate_card(card, idx * 0.03)
            
            scroll.add_widget(content)
            layout.add_widget(scroll)
        
        main_layout.add_widget(layout)
        self.add_widget(main_layout)
    
    def remove_from_favorites(self, text):
        data = load_data()
        favs = data.get("favorites", [])
        if text in favs:
            favs.remove(text)
            data["favorites"] = favs
            save_data(data)
            self.build_ui()
    
    def on_enter(self):
        self.build_ui()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        data = load_data()
        
        main_layout = FloatLayout()
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12))
        layout.size_hint = (1, 1)

        top = BoxLayout(size_hint_y=None, height=dp(50))
        back = AnimatedButton(text="< رجوع", bg_color=(0,0,0,0))
        back.bind(on_press=lambda x: set_screen("home"))
        top.add_widget(back)
        layout.add_widget(top)

        layout.add_widget(styled_label("🔧 الإعدادات", bold=True, color=current_colors["accent"], font_size="24sp",
                                 size_hint_y=None, height=dp(50)))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, padding=dp(5))
        content.bind(minimum_height=content.setter('height'))

        # الهدف اليومي
        content.add_widget(styled_label("🎯 الهدف اليومي:", color=current_colors["text"], size_hint_y=None, height=dp(30)))
        self.target_input = TextInput(
            text=str(data.get("target", 33)), input_filter="int",
            size_hint_y=None, height=dp(45), multiline=False,
            background_color=current_colors["card"], foreground_color=current_colors["text"],
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        content.add_widget(self.target_input)
        save_btn = AnimatedButton(text="💾 حفظ الهدف", bg_color=current_colors["primary"], height=dp(45))
        save_btn.bind(on_press=lambda x: self.save_target())
        content.add_widget(save_btn)

        self.msg_label = styled_label(text="", color=current_colors["accent"], size_hint_y=None, height=dp(25))
        content.add_widget(self.msg_label)

        # الوضع الليلي
        content.add_widget(styled_label("🌙 الوضع الليلي:", color=current_colors["text"], size_hint_y=None, height=dp(30)))
        night_status = "✅ مفعل" if data.get("night_mode", False) else "❌ غير مفعل"
        self.night_btn = AnimatedButton(
            text=f"تبديل ({night_status})",
            bg_color=current_colors["primary"] if data.get("night_mode", False) else current_colors["card"],
            height=dp(45)
        )
        self.night_btn.bind(on_press=lambda x: self.toggle_night_mode())
        content.add_widget(self.night_btn)

        # الليل الذكي
        auto_night_status = "✅ مفعل" if data.get("auto_night_mode", True) else "❌ غير مفعل"
        auto_night_btn = AnimatedButton(
            text=f"🌙 الليل الذكي ({auto_night_status})",
            bg_color=current_colors["primary"] if data.get("auto_night_mode", True) else current_colors["card"],
            height=dp(45)
        )
        auto_night_btn.bind(on_press=lambda x: self.toggle_auto_night())
        content.add_widget(auto_night_btn)

        # الإشعارات
        content.add_widget(styled_label("🔔 الإشعارات:", color=current_colors["text"], size_hint_y=None, height=dp(30)))
        notif_status = "✅ مفعل" if data.get("notifications_enabled", True) else "❌ غير مفعل"
        self.notif_btn = AnimatedButton(
            text=f"تبديل ({notif_status})",
            bg_color=current_colors["primary"] if data.get("notifications_enabled", True) else current_colors["card"],
            height=dp(45)
        )
        self.notif_btn.bind(on_press=lambda x: self.toggle_notifications())
        content.add_widget(self.notif_btn)

        # الصوت والاهتزاز
        settings_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(50))
        sound_status = "✅" if data.get("sound_enabled", True) else "❌"
        sound_btn = AnimatedButton(
            text=f"🔊 صوت {sound_status}",
            bg_color=current_colors["primary"] if data.get("sound_enabled", True) else current_colors["card"],
            font_size=dp(12)
        )
        sound_btn.bind(on_press=lambda x: self.toggle_sound())
        settings_grid.add_widget(sound_btn)
        
        vib_status = "✅" if data.get("vibration_enabled", True) else "❌"
        vib_btn = AnimatedButton(
            text=f"📳 اهتزاز {vib_status}",
            bg_color=current_colors["primary"] if data.get("vibration_enabled", True) else current_colors["card"],
            font_size=dp(12)
        )
        vib_btn.bind(on_press=lambda x: self.toggle_vibration())
        settings_grid.add_widget(vib_btn)
        content.add_widget(settings_grid)

        # إعادة ضبط تلقائي
        reset_status = "✅" if data.get("auto_reset", True) else "❌"
        auto_reset_btn = AnimatedButton(
            text=f"♻️ إعادة ضبط تلقائي ({reset_status})",
            bg_color=current_colors["primary"] if data.get("auto_reset", True) else current_colors["card"],
            height=dp(45),
            font_size=dp(12)
        )
        auto_reset_btn.bind(on_press=lambda x: self.toggle_auto_reset())
        content.add_widget(auto_reset_btn)

        # المفضلة والإنجازات
        fav_count = len(data.get("favorites", []))
        content.add_widget(styled_label(f"❤️ المفضلة: {fav_count} عنصر", color=current_colors["text_muted"], size_hint_y=None, height=dp(25)))
        
        grid2 = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(45))
        clear_fav_btn = AnimatedButton(text="♻️ مسح المفضلة", bg_color=current_colors["danger"])
        clear_fav_btn.bind(on_press=lambda x: self.clear_favorites())
        grid2.add_widget(clear_fav_btn)
        
        ach_btn = AnimatedButton(text="🏆 الإنجازات", bg_color=current_colors["primary"])
        ach_btn.bind(on_press=lambda x: set_screen("achievements"))
        grid2.add_widget(ach_btn)
        content.add_widget(grid2)

        # الإحصائيات
        content.add_widget(styled_label(
            f"🏆 إجمالي التسبيحات: {data.get('total_all_time', 0)}",
            color=current_colors["text_muted"], size_hint_y=None, height=dp(25)
        ))
        content.add_widget(styled_label(
            f"📅 أيام المتابعة: {self.get_active_days(data)}",
            color=current_colors["text_muted"], size_hint_y=None, height=dp(25)
        ))

        # عن التطبيق
        about_btn = AnimatedButton(text="ℹ️ عن التطبيق", bg_color=current_colors["card"], height=dp(45))
        about_btn.bind(on_press=lambda x: set_screen("about"))
        content.add_widget(about_btn)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def get_active_days(self, data):
        total = data.get("total_all_time", 0)
        if total == 0:
            return 0
        return max(1, total // 33)

    def save_target(self):
        data = load_data()
        try:
            val = int(self.target_input.text) if self.target_input.text else 0
        except ValueError:
            val = 0
        data["target"] = max(val, 1)
        save_data(data)
        self.msg_label.text = ar("✅ تم الحفظ بنجاح")
        Clock.schedule_once(lambda dt: setattr(self.msg_label, "text", ""), 2)

    def toggle_night_mode(self):
        data = load_data()
        data["night_mode"] = not data.get("night_mode", False)
        save_data(data)
        apply_theme(data["night_mode"])
        self.build_ui()
        app = App.get_running_app()
        for screen in app.sm.screens:
            if hasattr(screen, 'build_ui'):
                screen.build_ui()

    def toggle_auto_night(self):
        data = load_data()
        data["auto_night_mode"] = not data.get("auto_night_mode", True)
        save_data(data)
        self.build_ui()
        if data["auto_night_mode"]:
            self.check_auto_night()

    def check_auto_night(self):
        hour = datetime.now().hour
        is_night = hour < 6 or hour >= 18
        data = load_data()
        if data.get("night_mode", False) != is_night:
            data["night_mode"] = is_night
            save_data(data)
            apply_theme(is_night)
            app = App.get_running_app()
            for screen in app.sm.screens:
                if hasattr(screen, 'build_ui'):
                    screen.build_ui()

    def toggle_notifications(self):
        data = load_data()
        data["notifications_enabled"] = not data.get("notifications_enabled", True)
        save_data(data)
        self.build_ui()
        if data["notifications_enabled"]:
            send_daily_notification()

    def toggle_sound(self):
        data = load_data()
        data["sound_enabled"] = not data.get("sound_enabled", True)
        save_data(data)
        self.build_ui()

    def toggle_vibration(self):
        data = load_data()
        data["vibration_enabled"] = not data.get("vibration_enabled", True)
        save_data(data)
        self.build_ui()

    def toggle_auto_reset(self):
        data = load_data()
        data["auto_reset"] = not data.get("auto_reset", True)
        save_data(data)
        self.build_ui()

    def clear_favorites(self):
        data = load_data()
        data["favorites"] = []
        save_data(data)
        self.build_ui()

    def on_enter(self):
        self.build_ui()
        # التحقق من الوضع الليلي التلقائي
        data = load_data()
        if data.get("auto_night_mode", True):
            self.check_auto_night()

class SearchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        self._search_timer = None

    def build_ui(self):
        self.clear_widgets()
        
        main_layout = FloatLayout()
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
        layout.size_hint = (1, 1)

        top = BoxLayout(size_hint_y=None, height=dp(50))
        back = AnimatedButton(text="< رجوع", bg_color=(0,0,0,0))
        back.bind(on_press=lambda x: set_screen("home"))
        top.add_widget(back)
        layout.add_widget(top)

        layout.add_widget(styled_label("🔍 بحث", bold=True, color=current_colors["accent"], font_size="24sp"))

        self.search_input = TextInput(
            hint_text="اكتب كلمة للبحث...",
            size_hint_y=None, height=dp(45), multiline=False,
            background_color=current_colors["card"], foreground_color=current_colors["text"],
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        self.search_input.bind(text=self.on_search)
        layout.add_widget(self.search_input)

        self.result_count = styled_label(text="", color=current_colors["text_muted"], size_hint_y=None, height=dp(25))
        layout.add_widget(self.result_count)

        self.results_scroll = ScrollView()
        self.results_content = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.results_content.bind(minimum_height=self.results_content.setter('height'))
        self.results_scroll.add_widget(self.results_content)
        layout.add_widget(self.results_scroll)

        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def on_search(self, instance, value):
        if self._search_timer:
            self._search_timer.cancel()
        self._search_timer = Clock.schedule_once(lambda dt: self.do_search(value), 0.3)

    def do_search(self, value):
        self.results_content.clear_widgets()
        query = value.strip()
        
        if not query:
            self.result_count.text = ""
            return

        results = []
        for cat, items in AZKAR.items():
            for item in items:
                if query in item["text"]:
                    results.append(("📖", cat, item["text"]))
        
        for cat, items in ADIYA.items():
            for item in items:
                if query in item["text"]:
                    results.append(("🙏", cat, item["text"]))
        
        for cat, items in OCCASIONS.items():
            for item in items:
                if query in item["text"]:
                    results.append(("🌙", cat, item["text"]))
        
        self.result_count.text = f"🔍 {len(results)} نتيجة"
        
        for idx, (icon, cat, text) in enumerate(results[:30]):
            card = AnimatedCard(size_hint_y=None, height=dp(80), padding=dp(10))
            box = BoxLayout(orientation="horizontal")
            label_text = f"{icon} {text[:50]}..."
            if len(text) > 50:
                label_text += "..."
            lbl = styled_label(
                label_text,
                color=current_colors["text"],
                font_size="12sp",
                halign="center",
                text_size=(Window.width - dp(120), None)
            )
            box.add_widget(lbl)
            share_btn = AnimatedButton(text="📤", bg_color=(0,0,0,0), size_hint_x=None, width=dp(35))
            share_btn.bind(on_press=lambda x, t=text: share_zikr(t))
            box.add_widget(share_btn)
            card.add_widget(box)
            self.results_content.add_widget(card)
            animate_card(card, idx * 0.02)

class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        data = load_data()
        
        main_layout = FloatLayout()
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12))
        layout.size_hint = (1, 1)

        top = BoxLayout(size_hint_y=None, height=dp(50))
        back = AnimatedButton(text="< رجوع", bg_color=(0,0,0,0))
        back.bind(on_press=lambda x: set_screen("home"))
        top.add_widget(back)
        layout.add_widget(top)

        layout.add_widget(styled_label("📊 الإحصاءات", bold=True, color=current_colors["accent"], font_size="24sp"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, padding=dp(5))
        content.bind(minimum_height=content.setter('height'))

        stats = [
            ("🏆 إجمالي التسبيحات", data.get("total_all_time", 0)),
            ("🌟 تسبيحات اليوم", data.get("count", 0)),
            ("📅 تسبيحات الأمس", data.get("yesterday", 0)),
            ("🎯 الهدف اليومي", data.get("target", 33)),
            ("❤️ المفضلة", len(data.get("favorites", []))),
            ("🏆 الإنجازات", len(data.get("achievements", []))),
        ]

        for label, value in stats:
            card = AnimatedCard(size_hint_y=None, height=dp(50), padding=dp(10))
            box = BoxLayout(orientation="horizontal")
            box.add_widget(styled_label(text=label, color=current_colors["text"]))
            box.add_widget(styled_label(text=str(value), color=current_colors["accent"], bold=True, size_hint_x=None, width=dp(80)))
            card.add_widget(box)
            content.add_widget(card)

        total = data.get("total_all_time", 0)
        days_active = max(1, total // 33) if total > 0 else 0
        content.add_widget(styled_label(
            f"📅 أيام النشاط: {days_active} يوم",
            color=current_colors["text_muted"],
            size_hint_y=None, height=dp(30)
        ))

        last_zikr = data.get("last_zikr", "سبحان الله")
        content.add_widget(styled_label(
            f"📝 آخر ذكر: {last_zikr}",
            color=current_colors["text_muted"],
            size_hint_y=None, height=dp(30)
        ))

        share_stats_btn = AnimatedButton(text="📤 مشاركة الإحصائيات", bg_color=current_colors["accent"], height=dp(45))
        share_stats_btn.bind(on_press=lambda x: self.share_stats(data))
        content.add_widget(share_stats_btn)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def share_stats(self, data):
        message = f"""
📊 *إحصائياتي في سُبْحَان* 📊

🏆 إجمالي التسبيحات: {data.get('total_all_time', 0)}
🌟 تسبيحات اليوم: {data.get('count', 0)}
🎯 الهدف اليومي: {data.get('target', 33)}
🏆 الإنجازات: {len(data.get('achievements', []))}

💫 نسأل الله القبول
"""
        share_zikr(message)

class TimerZikrScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_running = False
        self.time_seconds = 0
        self.zikr = "سبحان الله"
        self.count = 0
        self.build_ui()
        self._timer_event = None

    def build_ui(self):
        self.clear_widgets()
        
        main_layout = FloatLayout()
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        layout.size_hint = (1, 1)

        top = BoxLayout(size_hint_y=None, height=dp(50))
        back = AnimatedButton(text="< رجوع", bg_color=(0,0,0,0))
        back.bind(on_press=lambda x: set_screen("home"))
        top.add_widget(back)
        layout.add_widget(top)

        layout.add_widget(styled_label("⏰ مؤقت الذكر", bold=True, color=current_colors["accent"], font_size="24sp"))

        self.timer_label = styled_label("00:00", font_size="56sp", bold=True, color=current_colors["text"])
        layout.add_widget(self.timer_label)

        self.count_label = styled_label(f"🔄 {self.count}", font_size="20sp", color=current_colors["text_muted"])
        layout.add_widget(self.count_label)

        layout.add_widget(styled_label("اختر الذكر:", color=current_colors["text"], size_hint_y=None, height=dp(25)))
        zikr_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(80))
        for z in ["سبحان الله", "الحمد لله", "الله أكبر", "لا إله إلا الله"]:
            b = AnimatedButton(
                text=z,
                bg_color=current_colors["primary"] if z == self.zikr else current_colors["card"],
                font_size=dp(14)
            )
            b.bind(on_press=lambda x, val=z: self.change_zikr(val))
            zikr_grid.add_widget(b)
        layout.add_widget(zikr_grid)

        control_layout = GridLayout(cols=3, spacing=dp(10), size_hint_y=None, height=dp(50))
        start_btn = AnimatedButton(text="▶️ بدء", bg_color=current_colors["primary"])
        start_btn.bind(on_press=lambda x: self.start_timer())
        pause_btn = AnimatedButton(text="🔴 إيقاف", bg_color=current_colors["accent"])
        pause_btn.bind(on_press=lambda x: self.pause_timer())
        reset_btn = AnimatedButton(text="🔄 إعادة", bg_color=current_colors["danger"])
        reset_btn.bind(on_press=lambda x: self.reset_timer())
        
        control_layout.add_widget(start_btn)
        control_layout.add_widget(pause_btn)
        control_layout.add_widget(reset_btn)
        layout.add_widget(control_layout)

        main_layout.add_widget(layout)
        self.add_widget(main_layout)

    def change_zikr(self, z):
        self.zikr = z
        self.build_ui()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self._timer_event = Clock.schedule_interval(self.update_timer, 1)

    def pause_timer(self):
        self.timer_running = False
        if self._timer_event:
            self._timer_event.cancel()
            self._timer_event = None

    def reset_timer(self):
        self.pause_timer()
        self.time_seconds = 0
        self.count = 0
        self.timer_label.text = "00:00"
        self.count_label.text = "🔄 0"

    def update_timer(self, dt):
        self.time_seconds += 1
        self.count += 1
        minutes = self.time_seconds // 60
        seconds = self.time_seconds % 60
        self.timer_label.text = f"{minutes:02d}:{seconds:02d}"
        self.count_label.text = f"🔄 {self.count}"

        if self.count % 10 == 0 and HAS_VIBRATOR:
            data = load_data()
            if data.get("vibration_enabled", True):
                try:
                    vibrator.vibrate(0.05)
                except Exception:
                    pass

class AchievementsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        data = load_data()
        unlocked = data.get("achievements", [])
        
        main_layout = FloatLayout()
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12))
        layout.size_hint = (1, 1)
        
        top = BoxLayout(size_hint_y=None, height=dp(50))
        back = AnimatedButton(text="< رجوع", bg_color=(0,0,0,0))
        back.bind(on_press=lambda x: set_screen("settings"))
        top.add_widget(back)
        layout.add_widget(top)
        
        layout.add_widget(styled_label(
            "🏆 الإنجازات",
            bold=True,
            color=current_colors["accent"],
            font_size="24sp",
            size_hint_y=None,
            height=dp(50)
        ))
        
        layout.add_widget(styled_label(
            f"تم فتح {len(unlocked)} من {len(ACHIEVEMENTS)} إنجاز",
            color=current_colors["text_muted"],
            size_hint_y=None,
            height=dp(30)
        ))
        
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        for key, achievement in ACHIEVEMENTS.items():
            is_unlocked = key in unlocked
            card = AnimatedCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(70),
                padding=dp(10),
                spacing=dp(4),
                bg_color=current_colors["success"] if is_unlocked else current_colors["card"]
            )
            
            top_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
            top_row.add_widget(styled_label(
                text=f"{achievement['icon']} {achievement['name']}",
                color=current_colors["text"] if is_unlocked else current_colors["text_muted"],
                bold=is_unlocked,
                font_size="15sp"
            ))
            
            status_icon = "✅" if is_unlocked else "🔒"
            top_row.add_widget(styled_label(
                text=status_icon,
                color=current_colors["accent"] if is_unlocked else current_colors["text_muted"],
                size_hint_x=None,
                width=dp(40)
            ))
            card.add_widget(top_row)
            
            card.add_widget(styled_label(
                text=achievement["description"],
                color=current_colors["text_muted"],
                font_size="12sp"
            ))
            
            content.add_widget(card)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        main_layout.add_widget(layout)
        self.add_widget(main_layout)
    
    def on_enter(self):
        self.build_ui()

class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        
        main_layout = FloatLayout()
        bg = GradientBackground()
        main_layout.add_widget(bg)
        
        layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        layout.size_hint = (1, 1)

        top = BoxLayout(size_hint_y=None, height=dp(50))
        back = AnimatedButton(text="< رجوع", bg_color=(0,0,0,0))
        back.bind(on_press=lambda x: set_screen("home"))
        top.add_widget(back)
        layout.add_widget(top)

        layout.add_widget(styled_label(
            "✨ سُبْحَان ✨",
            bold=True,
            color=current_colors["accent"],
            font_size="36sp",
            size_hint_y=None,
            height=dp(70)
        ))

        layout.add_widget(styled_label(
            "تطبيق الأذكار والتسبيح",
            color=current_colors["text_muted"],
            font_size="16sp",
            size_hint_y=None,
            height=dp(30)
        ))

        layout.add_widget(Label(size_hint_y=None, height=dp(10)))

        info_card = AnimatedCard(orientation="vertical", size_hint_y=None, height=dp(200), padding=dp(15), spacing=dp(8))
        
        info_card.add_widget(styled_label(
            "👨‍💻 المطور: د/عاصم النجار",
            color=current_colors["text"],
            bold=True,
            font_size="16sp"
        ))
        
        info_card.add_widget(styled_label(
            "📱 الإصدار: 3.0.0",
            color=current_colors["text_muted"],
            font_size="14sp"
        ))
        
        info_card.add_widget(styled_label(
            "📅 تاريخ الإصدار: 2024",
            color=current_colors["text_muted"],
            font_size="14sp"
        ))
        
        info_card.add_widget(styled_label(
            "۩ نسأل الله القبول",
            color=current_colors["accent"],
            font_size="14sp"
        ))
        
        layout.add_widget(info_card)

        desc_card = AnimatedCard(orientation="vertical", size_hint_y=None, height=dp(120), padding=dp(12), spacing=dp(4))
        desc_card.add_widget(styled_label(
            "📖 حول التطبيق",
            bold=True,
            color=current_colors["accent"],
            size_hint_y=None,
            height=dp(25)
        ))
        desc_card.add_widget(styled_label(
            "تطبيق سُبْحَان يساعدك على ذكر الله والتسبيح والأدعية اليومية",
            color=current_colors["text_muted"],
            font_size="13sp",
            halign="center"
        ))
        layout.add_widget(desc_card)

        layout.add_widget(styled_label(
            "© 2024 جميع الحقوق محفوظة",
            color=current_colors["text_muted"],
            font_size="11sp",
            size_hint_y=None,
            height=dp(30)
        ))

        main_layout.add_widget(layout)
        self.add_widget(main_layout)

# ========== التطبيق الرئيسي ==========
class SubhanApp(App):
    def build(self):
        self.title = "سُبْحَان"
        
        data = load_data()
        
        # التحقق من الوضع الليلي التلقائي
        if data.get("auto_night_mode", True):
            hour = datetime.now().hour
            is_night = hour < 6 or hour >= 18
            if data.get("night_mode", False) != is_night:
                data["night_mode"] = is_night
                save_data(data)
        
        apply_theme(data.get("night_mode", False))
        
        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(TasbihScreen(name="tasbih"))
        self.sm.add_widget(AzkarScreen(name="azkar"))
        self.sm.add_widget(DuaaScreen(name="duaa"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.add_widget(SearchScreen(name="search"))
        self.sm.add_widget(StatsScreen(name="stats"))
        self.sm.add_widget(TimerZikrScreen(name="timer"))
        self.sm.add_widget(AboutScreen(name="about"))
        self.sm.add_widget(FavoritesScreen(name="favorites"))
        self.sm.add_widget(AchievementsScreen(name="achievements"))
        
        if data.get("notifications_enabled", True):
            Clock.schedule_once(lambda dt: send_daily_notification(), 5)
        
        logger.info("✅ تم تشغيل التطبيق بنجاح (الإصدار 3.0.0)")
        return self.sm

