"""
main.py  –  Atik Avcisi (AI Kamera Entegreli)
Python + Kivy  |  AI: TFLite + OpenCV
"""

import json
import os
import random
import math
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import (
    Color, Rectangle, RoundedRectangle, Ellipse, Mesh
)
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty, BooleanProperty

from ai_atik_tanima import AtikTanimaMotoru

# ─── Renkler ───────────────────────────────────────────────────────────────────
C_BG_KOYU    = get_color_from_hex("#0A1A0A")
C_BG_OTA     = get_color_from_hex("#0D2B0D")
C_BG_CARD    = get_color_from_hex("#0F3D1A")
C_BG_CARD2   = get_color_from_hex("#122E18")

C_YESIL_NEON = get_color_from_hex("#00FF7F")
C_YESIL_ACIK = get_color_from_hex("#7FFF7F")
C_SARI       = get_color_from_hex("#AAFF00")
C_TURUNCU    = get_color_from_hex("#FF8C00")
C_TOPRAK     = get_color_from_hex("#8B6914")
C_GOKCE      = get_color_from_hex("#00CFCF")
C_KIRMIZI    = get_color_from_hex("#FF4455")

C_BEYAZ      = get_color_from_hex("#E8FFE8")
C_SOLUK      = get_color_from_hex("#5A8A5A")

DATA_FILE = "atik_avcisi.json"

WASTE_TYPES = {
    "Izmarit": {"puan": 25, "renk": "#FF4444"},
    "Pil":     {"puan": 50, "renk": "#FF8C00"},
    "Plastik": {"puan": 15, "renk": "#00BFFF"},
    "Cam":     {"puan": 20, "renk": "#00FFFF"},
    "Kagit":   {"puan": 10, "renk": "#AAFF00"},
}

BILGI = [
    "Bir izmarit 500 litre suyu kirletir!",
    "Bir pil 400 litre suyu zehirler!",
    "Plastik dogada 450 yilda cozunur.",
    "1 ton kagit geri donusu 17 agaci kurtarir.",
    "Cam yuzde 100 geri donusturulebilir!",
    "Her yil 8 milyon ton plastik okyanuslara karisiyor.",
    "Geri donusum enerjiyi yuzde 70 azaltir.",
    "Turkiye'de yilda kisi basi 29 kg atik uretilir.",
    "Bir aluminyum kutu sonsuz kez geri donusturulur.",
]

BASE_XP  = 150
XP_ARTIS = 1.30

# Hangi ekran gosterilecek: "ana" veya "kamera"
EKRAN_ANA    = "ana"
EKRAN_KAMERA = "kamera"


# ─── Veri ──────────────────────────────────────────────────────────────────────
def veri_yukle():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"toplam_puan": 0, "mevcut_seviye": 1,
            "hedef_puan": BASE_XP, "kayitlar": []}


def veri_kaydet(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def seviye_hesapla(s):
    return round(BASE_XP * (XP_ARTIS ** (s - 1)))


# ─── Dogal Arka Plan ───────────────────────────────────────────────────────────
class DoğaArkaplan(Widget):
    zaman = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._ciz, size=self._ciz, zaman=self._ciz)
        Clock.schedule_interval(self._guncelle, 1 / 30)

    def _guncelle(self, dt):
        self.zaman += dt

    def _ciz(self, *args):
        self.canvas.clear()
        w, h = self.width, self.height
        t = self.zaman
        with self.canvas:
            for i in range(20):
                oran = i / 19
                r = 0.02 + oran * 0.03
                g = 0.05 + oran * 0.15
                b = 0.08 + oran * 0.05
                Color(r, g, b, 1)
                Rectangle(pos=(self.x, self.y + h * (1 - (i + 1) / 20)),
                          size=(w, h / 20 + 1))

            random.seed(42)
            for _ in range(60):
                sx = self.x + random.random() * w
                sy = self.y + h * 0.55 + random.random() * h * 0.45
                pk = 0.4 + 0.6 * abs(math.sin(t * 1.5 + random.random() * 10))
                Color(1, 1, 0.8, pk)
                Ellipse(pos=(sx - 1, sy - 1), size=(2, 2))
            random.seed()

            ay_x = self.x + w * 0.82
            ay_y = self.y + h * 0.82
            Color(1.0, 0.98, 0.85, 0.95)
            Ellipse(pos=(ay_x - 18, ay_y - 18), size=(36, 36))
            Color(0.05, 0.12, 0.05, 0.85)
            Ellipse(pos=(ay_x - 12, ay_y - 14), size=(28, 28))

            Color(0.04, 0.14, 0.06, 1)
            daglar = [(0, 0.32), (0.18, 0.55), (0.35, 0.38),
                      (0.52, 0.62), (0.72, 0.42), (0.88, 0.58), (1.0, 0.34)]
            pts = []
            for ox, oy in daglar:
                pts += [self.x + ox * w, self.y + h * oy]
            pts += [self.x + w, self.y, self.x, self.y]
            n = len(pts) // 2
            verts = []
            for i in range(n):
                verts += [pts[i*2], pts[i*2+1], 0, 0]
            fan = []
            for i in range(1, n - 1):
                fan += [0, i, i + 1]
            if fan:
                Mesh(vertices=verts, indices=fan, mode='triangles')

            Color(0.03, 0.10, 0.04, 1)
            on_daglar = [(0, 0.22), (0.12, 0.40), (0.28, 0.25),
                         (0.45, 0.45), (0.60, 0.28), (0.78, 0.42),
                         (0.92, 0.26), (1.0, 0.22)]
            pts2 = []
            for ox, oy in on_daglar:
                pts2 += [self.x + ox * w, self.y + h * oy]
            pts2 += [self.x + w, self.y, self.x, self.y]
            n2 = len(pts2) // 2
            v2 = []
            for i in range(n2):
                v2 += [pts2[i*2], pts2[i*2+1], 0, 0]
            f2 = []
            for i in range(1, n2 - 1):
                f2 += [0, i, i + 1]
            if f2:
                Mesh(vertices=v2, indices=f2, mode='triangles')

            for ax in [0.05, 0.15, 0.25, 0.60, 0.70, 0.80, 0.90, 0.97]:
                self._agac_ciz(self.x + ax * w, self.y + h * 0.22,
                               dp(6), dp(30), t)

            Color(0.04, 0.18, 0.06, 1)
            Rectangle(pos=(self.x, self.y), size=(w, h * 0.20))
            Color(0.06, 0.28, 0.08, 1)
            Rectangle(pos=(self.x, self.y), size=(w, h * 0.12))

            random.seed(7)
            for i in range(12):
                bx = random.random() * w
                by = random.random() * h * 0.5
                hiz = 0.3 + random.random() * 0.5
                gen = 20 + random.random() * 40
                lx = self.x + (bx + gen * math.sin(t * hiz + i)) % w
                ly = self.y + (by + t * 15 * hiz) % (h * 0.8)
                Color(0.2, 0.8, 0.2, 0.5)
                Ellipse(pos=(lx - 4, ly - 2), size=(8, 5))
            random.seed()

    def _agac_ciz(self, x, y, govde_r, yukseklik, t):
        Color(0.35, 0.22, 0.08, 1)
        gw = govde_r * 0.8
        Rectangle(pos=(x - gw / 2, y), size=(gw, yukseklik * 0.5))
        for kat, (oy, r, gv) in enumerate([(0.45, 1.2, 0.55),
                                            (0.60, 0.95, 0.65),
                                            (0.75, 0.7,  0.75)]):
            sal = math.sin(t * 0.8 + kat * 1.2) * dp(2)
            Color(0.05, gv, 0.1, 0.9)
            yr = govde_r * r * 2.5
            Ellipse(pos=(x - yr + sal, y + yukseklik * oy - yr * 0.5),
                    size=(yr * 2, yr * 1.6))


# ─── UI Yardimcilari ───────────────────────────────────────────────────────────
def etiket(text, font_size=15, color=None, bold=False, halign="center", **kwargs):
    color = color or C_BEYAZ
    lbl = Label(text=text, font_size=dp(font_size), color=color,
                bold=bold, halign=halign, valign="middle", **kwargs)
    lbl.bind(size=lbl.setter("text_size"))
    return lbl


class Kart(BoxLayout):
    def __init__(self, kenar=None, arka=None, **kwargs):
        super().__init__(**kwargs)
        self._kenar = kenar or C_YESIL_NEON
        self._arka  = arka  or C_BG_CARD
        self.bind(pos=self._ciz, size=self._ciz)

    def _ciz(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._arka, 0.85)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            Color(*self._kenar, 0.9)
            RoundedRectangle(pos=(self.x + dp(1), self.y + dp(1)),
                             size=(self.width - dp(2), self.height - dp(2)),
                             radius=[dp(14)])
            Color(*self._arka, 0.88)
            RoundedRectangle(pos=(self.x + dp(2.5), self.y + dp(2.5)),
                             size=(self.width - dp(5), self.height - dp(5)),
                             radius=[dp(12)])


class YesilButon(Button):
    def __init__(self, renk=None, **kwargs):
        self._renk = renk or C_YESIL_NEON
        kwargs.setdefault("background_color", [0, 0, 0, 0])
        kwargs.setdefault("color", C_BG_KOYU)
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", dp(15))
        super().__init__(**kwargs)
        self.bind(pos=self._ciz, size=self._ciz)

    def _ciz(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._renk, 1.0)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(*self._renk, 0.3)
            RoundedRectangle(pos=(self.x + dp(2), self.y + dp(2)),
                             size=(self.width - dp(4), self.height - dp(4)),
                             radius=[dp(10)])
            Color(self._renk[0], min(1, self._renk[1] + 0.2), self._renk[2], 0.9)
            RoundedRectangle(pos=(self.x + dp(3), self.y + dp(3)),
                             size=(self.width - dp(6), self.height - dp(6)),
                             radius=[dp(9)])

    def on_press(self):
        anim = Animation(opacity=0.5, duration=0.07) + Animation(opacity=1.0, duration=0.07)
        anim.start(self)


# ─── AI Kamera Paneli ─────────────────────────────────────────────────────────
class KameraPaneli(BoxLayout):
    """
    AI kamera ekrani:
      • Canli goruntu akisi (KivyImage + Texture)
      • Tespit durumu gostergesi
      • Manuel onay / iptal butonlari
    """

    def __init__(self, on_kabul, on_kapat, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(8), padding=dp(10),
            **kwargs
        )
        self.on_kabul  = on_kabul    # (tur, guven) -> None
        self.on_kapat  = on_kapat    # () -> None

        self._motor    = AtikTanimaMotoru(
            model_yolu="model.tflite",
            etiket_yolu="labels.txt",
            kamera_id=0
        )
        self._son_tespit_tur   = None
        self._son_tespit_guven = 0.0

        self._ui_olustur()
        self._motor.on_tespit = self._tespit_alindi
        self._motor.on_kare   = self._kare_guncelle
        self._motor.baslat()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _ui_olustur(self):
        # Baslik satiri
        ust = BoxLayout(orientation="horizontal",
                        size_hint_y=None, height=dp(44), spacing=dp(8))
        ust.add_widget(etiket("AI Kamera", font_size=17,
                              color=C_YESIL_NEON, bold=True, halign="left"))
        kapat_btn = YesilButon(renk=C_KIRMIZI, text="X  Kapat",
                               size_hint_x=None, width=dp(90))
        kapat_btn.bind(on_press=self._kapat)
        ust.add_widget(kapat_btn)
        self.add_widget(ust)

        # Kamera goruntusu
        cam_kart = Kart(kenar=C_GOKCE, arka=C_BG_KOYU)
        self._cam_img = KivyImage(allow_stretch=True, keep_ratio=True)
        cam_kart.add_widget(self._cam_img)
        self.add_widget(cam_kart)

        # Tespit durum kartı
        durum_kart = Kart(kenar=C_SARI, arka=C_BG_KOYU,
                          size_hint_y=None, height=dp(64),
                          orientation="vertical", padding=dp(6))
        self._lbl_durum = etiket("Kamera baslatiliyor…",
                                 font_size=13, color=C_SARI)
        self._lbl_guven = etiket("", font_size=11, color=C_SOLUK)
        durum_kart.add_widget(self._lbl_durum)
        durum_kart.add_widget(self._lbl_guven)
        self.add_widget(durum_kart)

        # Guven progress bar
        pb_kart = Kart(kenar=C_YESIL_NEON, arka=C_BG_KOYU,
                       size_hint_y=None, height=dp(36),
                       orientation="vertical", padding=[dp(8), dp(6)])
        self._pb_guven = ProgressBar(max=100, value=0,
                                     size_hint_y=None, height=dp(16))
        pb_kart.add_widget(self._pb_guven)
        self.add_widget(pb_kart)

        # Onay / iptal butonlari
        btn_satir = BoxLayout(orientation="horizontal",
                              size_hint_y=None, height=dp(50), spacing=dp(10))
        self._btn_onayla = YesilButon(
            renk=C_YESIL_NEON, text="✓  Onayla & Kaydet",
            disabled=True
        )
        self._btn_onayla.bind(on_press=self._onayla)
        btn_iptal = YesilButon(renk=C_TURUNCU, text="↺  Yeniden Tara")
        btn_iptal.bind(on_press=self._yeniden_tara)
        btn_satir.add_widget(self._btn_onayla)
        btn_satir.add_widget(btn_iptal)
        self.add_widget(btn_satir)

    # ── Geri cagrimlar ────────────────────────────────────────────────────────

    def _kare_guncelle(self, texture):
        """AI motorundan gelen texture'i canli goruntude gunceller."""
        self._cam_img.texture = texture

    def _tespit_alindi(self, tur, guven, bbox):
        """AI motorundan gelen tespit sonucunu UI'a yansitir."""
        self._son_tespit_tur   = tur
        self._son_tespit_guven = guven

        pct = int(guven * 100)
        self._lbl_durum.text  = f"Tespit: {tur}"
        self._lbl_durum.color = C_YESIL_NEON
        self._lbl_guven.text  = f"Guven orani: %{pct}"
        self._pb_guven.value  = pct

        # Onay butonunu etkinlestir
        self._btn_onayla.disabled = False
        self._btn_onayla.opacity  = 1.0

        # 3 saniye sonra otomatik kapat ve kaydet
        Clock.schedule_once(self._otomatik_kaydet, 3)

    def _otomatik_kaydet(self, dt):
        if self._son_tespit_tur:
            self._onayla(None)

    def _onayla(self, *args):
        if self._son_tespit_tur and self.on_kabul:
            self.on_kabul(self._son_tespit_tur, self._son_tespit_guven)
        self._kapat()

    def _yeniden_tara(self, *args):
        self._son_tespit_tur   = None
        self._son_tespit_guven = 0.0
        self._lbl_durum.text   = "Tarama baslatildi…"
        self._lbl_durum.color  = C_SARI
        self._lbl_guven.text   = ""
        self._pb_guven.value   = 0
        self._btn_onayla.disabled = True

    def _kapat(self, *args):
        self._motor.durdur()
        if self.on_kapat:
            self.on_kapat()

    def on_parent(self, widget, parent):
        """Widget agactan cikarilirsa motoru durdur."""
        if parent is None:
            self._motor.durdur()


# ─── Ana Ekran ─────────────────────────────────────────────────────────────────
class AtikAvcisiUI(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = veri_yukle()
        self._bilgi_i = random.randint(0, len(BILGI) - 1)
        self._aktif_ekran = EKRAN_ANA
        self._kamera_paneli = None

        # Arka plan (her zaman gozukur)
        self._arka = DoğaArkaplan(size_hint=(1, 1))
        self.add_widget(self._arka)

        # Ana icerik
        self._ana_kutu = BoxLayout(
            orientation="vertical",
            spacing=dp(7), padding=dp(10),
            size_hint=(1, 1),
        )
        self.add_widget(self._ana_kutu)
        self._ui_olustur()

        self.bind(pos=self._boyutla, size=self._boyutla)
        Clock.schedule_interval(self._bilgi_dontur, 7)

    def _boyutla(self, *args):
        self._arka.pos  = self.pos
        self._arka.size = self.size

    # ─── Ana UI ───────────────────────────────────────────────────────────────

    def _ui_olustur(self):
        self._baslik()
        self._bilgi_paneli()
        self._stat_satiri()
        self._ilerleme()
        self._giris_paneli()
        self._gecmis()

    def _baslik(self):
        h = Kart(kenar=C_YESIL_NEON, arka=C_BG_KOYU,
                 size_hint_y=None, height=dp(58),
                 orientation="horizontal", padding=[dp(12), dp(6)])
        h.add_widget(etiket("Atik Avcisi", font_size=23,
                            color=C_YESIL_NEON, bold=True, halign="left"))
        h.add_widget(etiket("Dogayi Koru!", font_size=13,
                            color=C_SARI, halign="right"))
        self._ana_kutu.add_widget(h)

    def _bilgi_paneli(self):
        kart = Kart(kenar=C_GOKCE, arka=C_BG_KOYU,
                    size_hint_y=None, height=dp(48), padding=[dp(10), dp(4)])
        self._bilgi_lbl = etiket(BILGI[self._bilgi_i], font_size=12, color=C_GOKCE)
        kart.add_widget(self._bilgi_lbl)
        self._ana_kutu.add_widget(kart)

    def _stat_satiri(self):
        satir = BoxLayout(orientation="horizontal",
                          size_hint_y=None, height=dp(78), spacing=dp(7))
        for baslik, attr, renk in [
            ("SEVIYE",   "_lbl_seviye", C_SARI),
            ("TOPLAM XP","_lbl_puan",   C_YESIL_NEON),
            ("HEDEF XP", "_lbl_hedef",  C_TURUNCU),
        ]:
            k = Kart(kenar=renk, arka=C_BG_KOYU,
                     orientation="vertical", padding=dp(5))
            k.add_widget(etiket(baslik, font_size=9, color=C_SOLUK))
            deger = {
                "_lbl_seviye": str(self.data["mevcut_seviye"]),
                "_lbl_puan":   str(self.data["toplam_puan"]),
                "_lbl_hedef":  str(self.data["hedef_puan"]),
            }[attr]
            lbl = etiket(deger, font_size=25, color=renk, bold=True)
            setattr(self, attr, lbl)
            k.add_widget(lbl)
            satir.add_widget(k)
        self._ana_kutu.add_widget(satir)

    def _ilerleme(self):
        kart = Kart(kenar=C_YESIL_NEON, arka=C_BG_KOYU,
                    size_hint_y=None, height=dp(48),
                    orientation="vertical", padding=[dp(10), dp(4)])
        seviye = self.data["mevcut_seviye"]
        onceki = seviye_hesapla(seviye - 1) if seviye > 1 else 0
        hedef  = self.data["hedef_puan"]
        mevcut = self.data["toplam_puan"]
        pct    = min(100, max(0, (mevcut - onceki) / max(1, hedef - onceki) * 100))

        ust = BoxLayout(orientation="horizontal")
        ust.add_widget(etiket("Seviye Ilerleme:", font_size=11,
                              color=C_SOLUK, halign="left"))
        self._lbl_pct = etiket(f"{pct:.0f}%", font_size=11,
                               color=C_YESIL_NEON, halign="right")
        ust.add_widget(self._lbl_pct)
        kart.add_widget(ust)

        self._pb = ProgressBar(max=100, value=pct,
                               size_hint_y=None, height=dp(18))
        kart.add_widget(self._pb)
        self._ana_kutu.add_widget(kart)

    def _giris_paneli(self):
        panel = Kart(kenar=C_TURUNCU, arka=C_BG_KOYU,
                     orientation="vertical",
                     size_hint_y=None, height=dp(185),
                     padding=dp(10), spacing=dp(7))
        panel.add_widget(etiket("Atik Kaydet", font_size=14,
                                color=C_TURUNCU, bold=True, halign="left"))

        spin_satir = BoxLayout(orientation="horizontal", spacing=dp(7),
                               size_hint_y=None, height=dp(40))
        self._spin_tur = Spinner(
            text="Tur Sec", values=list(WASTE_TYPES.keys()),
            size_hint_x=0.55, background_color=C_BG_CARD2,
            color=C_YESIL_NEON, font_size=dp(13))
        self._spin_miktar = Spinner(
            text="1", values=[str(i) for i in range(1, 101)],
            size_hint_x=0.25, background_color=C_BG_CARD2,
            color=C_SARI, font_size=dp(13))
        spin_satir.add_widget(self._spin_tur)
        spin_satir.add_widget(etiket("Adet:", font_size=12,
                                     color=C_SOLUK, halign="right"))
        spin_satir.add_widget(self._spin_miktar)
        panel.add_widget(spin_satir)

        self._lbl_onizleme = etiket("Kazanilacak XP: --",
                                    font_size=13, color=C_SARI)
        self._spin_tur.bind(text=self._onizle)
        self._spin_miktar.bind(text=self._onizle)
        panel.add_widget(self._lbl_onizleme)

        # ── Buton satiri: Manuel + AI Kamera ──────────────────────────────
        btn_satir = BoxLayout(orientation="horizontal", spacing=dp(8),
                              size_hint_y=None, height=dp(44))

        btn_kaydet = YesilButon(renk=C_YESIL_NEON, text="KAYDET")
        btn_kaydet.bind(on_press=self._kaydet)

        btn_ai = YesilButon(renk=C_GOKCE, text="📷  AI Kamera")
        btn_ai.bind(on_press=self._kamera_ac)

        btn_satir.add_widget(btn_kaydet)
        btn_satir.add_widget(btn_ai)
        panel.add_widget(btn_satir)

        # AI durum etiketi
        self._lbl_ai_durum = etiket("", font_size=11, color=C_GOKCE,
                                    size_hint_y=None, height=dp(22))
        panel.add_widget(self._lbl_ai_durum)

        self._ana_kutu.add_widget(panel)

    def _gecmis(self):
        self._ana_kutu.add_widget(etiket("Son Kayitlar", font_size=12,
                                         color=C_SOLUK,
                                         size_hint_y=None, height=dp(22)))
        scroll = ScrollView()
        self._glist = BoxLayout(orientation="vertical",
                                size_hint_y=None, spacing=dp(4))
        self._glist.bind(minimum_height=self._glist.setter("height"))
        scroll.add_widget(self._glist)
        self._ana_kutu.add_widget(scroll)
        self._guncelle_gecmis()

    # ─── Kamera / AI ──────────────────────────────────────────────────────────

    def _kamera_ac(self, *args):
        """AI kamera panelini FloatLayout uzerine bindirme olarak goster."""
        if self._aktif_ekran == EKRAN_KAMERA:
            return

        self._aktif_ekran = EKRAN_KAMERA
        self._kamera_paneli = KameraPaneli(
            on_kabul=self._ai_kabul,
            on_kapat=self._kamera_kapat,
            size_hint=(1, 1),
            pos=self.pos,
        )
        # Arka plani daha koyu goster
        with self._kamera_paneli.canvas.before:
            Color(0.04, 0.10, 0.04, 0.96)
            self._kam_bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._kambg_guncelle, size=self._kambg_guncelle)
        self.add_widget(self._kamera_paneli)

    def _kambg_guncelle(self, *args):
        if hasattr(self, "_kam_bg"):
            self._kam_bg.pos  = self.pos
            self._kam_bg.size = self.size

    def _ai_kabul(self, tur, guven):
        """AI motorunun tespit ettigi atigi otomatik olarak Spinner'a yazar."""
        if tur in WASTE_TYPES:
            self._spin_tur.text  = tur
            self._lbl_ai_durum.text = (
                f"AI Tespit: {tur}  (%{int(guven*100)}) – "
                f"+{WASTE_TYPES[tur]['puan']} XP hazir"
            )
            self._lbl_onizleme.text = (
                f"+{WASTE_TYPES[tur]['puan']} XP kazanirsiniz  "
                f"({tur} x {self._spin_miktar.text})"
            )
            # Otomatik kaydet
            self._kaydet(None)

    def _kamera_kapat(self):
        if self._kamera_paneli:
            self.remove_widget(self._kamera_paneli)
            self._kamera_paneli = None
        self._aktif_ekran = EKRAN_ANA

    # ─── Olaylar ──────────────────────────────────────────────────────────────

    def _bilgi_dontur(self, dt):
        self._bilgi_i = (self._bilgi_i + 1) % len(BILGI)
        self._bilgi_lbl.text = BILGI[self._bilgi_i]

    def _onizle(self, *args):
        tur    = self._spin_tur.text
        miktar = int(self._spin_miktar.text) if self._spin_miktar.text.isdigit() else 1
        if tur in WASTE_TYPES:
            xp = WASTE_TYPES[tur]["puan"] * miktar
            self._lbl_onizleme.text = f"+{xp} XP kazanirsiniz  ({tur} x {miktar})"
        else:
            self._lbl_onizleme.text = "Kazanilacak XP: --"

    def _kaydet(self, *args):
        tur = self._spin_tur.text
        if tur not in WASTE_TYPES:
            self._popup("Hata", "Lutfen bir atik turu secin!")
            return

        miktar = int(self._spin_miktar.text) if self._spin_miktar.text.isdigit() else 1
        xp     = WASTE_TYPES[tur]["puan"] * miktar
        now    = datetime.now().strftime("%d.%m.%Y %H:%M")

        self.data["kayitlar"].insert(0, {
            "tarih": now, "tur": tur, "miktar": miktar, "xp": xp
        })
        self.data["toplam_puan"] += xp

        level_up = False
        while self.data["toplam_puan"] >= self.data["hedef_puan"]:
            self.data["mevcut_seviye"] += 1
            self.data["hedef_puan"] = seviye_hesapla(self.data["mevcut_seviye"])
            level_up = True

        veri_kaydet(self.data)
        self._stats_guncelle()
        self._guncelle_gecmis()

        if level_up:
            self._popup(
                "SEVIYE ATLADIN!",
                f"Tebrikler! Seviye {self.data['mevcut_seviye']} oldun!\n"
                f"Yeni hedef: {self.data['hedef_puan']} XP"
            )
        else:
            self._popup("Kaydedildi!", f"+{xp} XP kazandin!\n({tur} x {miktar})")

    def _stats_guncelle(self):
        self._lbl_seviye.text = str(self.data["mevcut_seviye"])
        self._lbl_puan.text   = str(self.data["toplam_puan"])
        self._lbl_hedef.text  = str(self.data["hedef_puan"])

        seviye = self.data["mevcut_seviye"]
        onceki = seviye_hesapla(seviye - 1) if seviye > 1 else 0
        pct    = min(100, max(0,
            (self.data["toplam_puan"] - onceki) /
            max(1, self.data["hedef_puan"] - onceki) * 100
        ))
        self._pb.value     = pct
        self._lbl_pct.text = f"{pct:.0f}%"

    def _guncelle_gecmis(self):
        self._glist.clear_widgets()
        kayitlar = self.data["kayitlar"][:15]

        if not kayitlar:
            self._glist.add_widget(
                etiket("Henuz kayit yok. Ilk atigini ekle!",
                       font_size=12, color=C_SOLUK,
                       size_hint_y=None, height=dp(38))
            )
            return

        for k in kayitlar:
            renk_hex = WASTE_TYPES.get(k["tur"], {}).get("renk", "#00FF7F")
            renk = get_color_from_hex(renk_hex)
            satir = Kart(kenar=renk, arka=C_BG_KOYU,
                         orientation="horizontal",
                         size_hint_y=None, height=dp(42),
                         padding=[dp(8), dp(3)], spacing=dp(6))
            satir.add_widget(etiket(f"{k['tur']} x{k['miktar']}",
                                   font_size=12, color=C_BEYAZ, halign="left"))
            satir.add_widget(etiket(f"+{k['xp']} XP", font_size=13,
                                   color=renk, halign="center", bold=True))
            satir.add_widget(etiket(k["tarih"], font_size=10,
                                   color=C_SOLUK, halign="right"))
            self._glist.add_widget(satir)

    def _popup(self, baslik, mesaj):
        icerik = BoxLayout(orientation="vertical",
                           padding=dp(14), spacing=dp(10))
        with icerik.canvas.before:
            Color(*C_BG_KOYU, 0.97)
            Rectangle(pos=icerik.pos, size=icerik.size)
        icerik.bind(
            pos=lambda w, v: setattr(w.canvas.before.children[1], 'pos', v),
            size=lambda w, v: setattr(w.canvas.before.children[1], 'size', v),
        )
        icerik.add_widget(etiket(mesaj, font_size=14, color=C_BEYAZ))
        btn = YesilButon(text="Tamam", renk=C_YESIL_NEON,
                         size_hint_y=None, height=dp(42))
        icerik.add_widget(btn)
        popup = Popup(
            title=baslik, title_color=C_YESIL_NEON, title_size=dp(16),
            content=icerik, size_hint=(0.82, 0.32),
            background_color=C_BG_KOYU, separator_color=C_YESIL_NEON,
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()


# ─── App ───────────────────────────────────────────────────────────────────────
class AtikAvcisiApp(App):
    def build(self):
        Window.clearcolor = C_BG_KOYU
        Window.size       = (400, 750)
        self.title        = "Atik Avcisi"
        return AtikAvcisiUI()


if __name__ == "__main__":
    AtikAvcisiApp().run()
