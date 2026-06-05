"""
ai_atik_tanima.py
─────────────────
Atik Avcisi uygulamasi icin AI tabanli gercek zamanli atik tanima modulu.

Kullanilan teknolojiler:
  • OpenCV  – kamera karelerini yakalama ve gorsellestirme
  • TensorFlow Lite (tflite-runtime) – MobileNetV2 tabanli siniflandirma
  • threading + Kivy Clock – UI donmadan arka plan analizi
"""

import threading
import time
import numpy as np

# ── Opsiyonel kutuphaneler: yuklenemediyse simule edilir ──────────────────────
try:
    import cv2
    CV2_OK = True
except ImportError:
    CV2_OK = False
    print("[AI] OpenCV bulunamadi – simule mod aktif.")

try:
    import tflite_runtime.interpreter as tflite
    TFLITE_OK = True
except ImportError:
    try:
        # TensorFlow icindeki Lite interpreter
        import tensorflow as tf
        tflite = tf.lite
        TFLITE_OK = True
    except ImportError:
        TFLITE_OK = False
        print("[AI] TFLite bulunamadi – simule mod aktif.")

from kivy.clock import Clock
from kivy.graphics.texture import Texture

# ── Sabitleri ──────────────────────────────────────────────────────────────────

# Uygulama icindeki WASTE_TYPES anahtarlariyla eslestirilmis etiketler.
# Gercek modelinizin cikti etiketlerini buraya ekleyin.
LABEL_HARITASI = {
    # MobileNetV2 ImageNet etiketleri (ornek alt kumesi)
    "cigarette":      "Izmarit",
    "butt":           "Izmarit",
    "plastic_bag":    "Plastik",
    "plastic bottle": "Plastik",
    "water bottle":   "Plastik",
    "wine bottle":    "Cam",
    "beer bottle":    "Cam",
    "glass":          "Cam",
    "battery":        "Pil",
    "paper":          "Kagit",
    "newspaper":      "Kagit",
    "cardboard":      "Kagit",
    # Turkce etiketi direkt gecmek isterseniz:
    "Izmarit":  "Izmarit",
    "Plastik":  "Plastik",
    "Cam":      "Cam",
    "Pil":      "Pil",
    "Kagit":    "Kagit",
}

GUVEN_ESIGI = 0.80          # %80 alti sonuclar goz ardi edilir
ANALIZ_ARALIGI = 1.5        # Her kac saniyede bir analiz yapilir
MODEL_BOYUT = (224, 224)    # MobileNetV2 giris boyutu

# Renk haritasi (BGR – OpenCV icin)
RENK_HARITASI = {
    "Izmarit": (0,   80,  255),
    "Pil":     (0,  140,  255),
    "Plastik": (255, 191,  0),
    "Cam":     (255, 255,  0),
    "Kagit":   (0,  255,  170),
}
VARSAYILAN_RENK = (0, 255, 127)


# ─────────────────────────────────────────────────────────────────────────────
class AtikTanimaMotoru:
    """
    Arka plan threadi ile kamera kareleri uzerinde TFLite siniflandirmasi yapar.

    Kullanim:
        motor = AtikTanimaMotoru(model_yolu="model.tflite", etiket_yolu="labels.txt")
        motor.baslat()
        ...
        motor.durdur()

    Geri cagrimlar:
        motor.on_tespit = lambda tur, guven, bbox: ...
        motor.on_kare   = lambda texture: ...      # Kivy Texture (annotated frame)
    """

    def __init__(self, model_yolu: str = "model.tflite",
                 etiket_yolu: str = "labels.txt",
                 kamera_id: int = 0):

        self.model_yolu  = model_yolu
        self.etiket_yolu = etiket_yolu
        self.kamera_id   = kamera_id

        self.on_tespit = None   # (tur:str, guven:float, bbox:tuple|None) -> None
        self.on_kare   = None   # (texture: Texture) -> None

        self._aktif     = False
        self._thread    = None
        self._interpreter = None
        self._etiketler   = []
        self._cap         = None

        # Simule mod icin sahte detektor
        self._simule     = not (CV2_OK and TFLITE_OK)
        self._son_analiz = 0.0

    # ── Baslatma / Durdurma ───────────────────────────────────────────────────

    def baslat(self):
        if self._aktif:
            return
        self._aktif = True
        self._model_yukle()
        self._thread = threading.Thread(target=self._dongu, daemon=True)
        self._thread.start()
        print("[AI] Motor baslatildi.")

    def durdur(self):
        self._aktif = False
        if self._cap and CV2_OK:
            self._cap.release()
        print("[AI] Motor durduruldu.")

    # ── Model yukleme ──────────────────────────────────────────────────────────

    def _model_yukle(self):
        if self._simule:
            print("[AI] Simule mod: model yuklenmiyor.")
            return
        try:
            self._interpreter = tflite.Interpreter(model_path=self.model_yolu)
            self._interpreter.allocate_tensors()
            self._giris  = self._interpreter.get_input_details()
            self._cikis  = self._interpreter.get_output_details()
            print(f"[AI] Model yuklendi: {self.model_yolu}")
        except Exception as e:
            print(f"[AI] Model yuklenemedi: {e} – simule moda gecildi.")
            self._simule = True

        try:
            with open(self.etiket_yolu, "r", encoding="utf-8") as f:
                self._etiketler = [l.strip() for l in f.readlines()]
        except Exception:
            # ImageNet sinif adlarinin kucuk bir ornegi
            self._etiketler = list(LABEL_HARITASI.keys())

    # ── Ana dongu (ayri thread) ────────────────────────────────────────────────

    def _dongu(self):
        if not self._simule:
            self._cap = cv2.VideoCapture(self.kamera_id)
            if not self._cap.isOpened():
                print("[AI] Kamera acilamadi – simule moda gecildi.")
                self._simule = True

        while self._aktif:
            if self._simule:
                self._simule_kare()
                time.sleep(ANALIZ_ARALIGI)
                continue

            ret, frame = self._cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            simdi = time.time()
            if simdi - self._son_analiz >= ANALIZ_ARALIGI:
                self._son_analiz = simdi
                tur, guven, bbox = self._siniflandir(frame)
                if tur and guven >= GUVEN_ESIGI:
                    self._cizim_yap(frame, tur, guven, bbox)
                    if self.on_tespit:
                        Clock.schedule_once(
                            lambda dt, t=tur, g=guven, b=bbox: self.on_tespit(t, g, b)
                        )

            # Kare -> Kivy Texture
            texture = self._frame_to_texture(frame)
            if self.on_kare:
                Clock.schedule_once(lambda dt, tx=texture: self.on_kare(tx))

            time.sleep(1 / 30)

    # ── Siniflandirma ──────────────────────────────────────────────────────────

    def _siniflandir(self, frame):
        """Frame'i TFLite modelinden gecirir; (tur, guven, bbox) dondurur."""
        try:
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            kucuk = cv2.resize(rgb, MODEL_BOYUT)
            giris = np.expand_dims(kucuk.astype(np.float32) / 255.0, axis=0)

            self._interpreter.set_tensor(self._giris[0]['index'], giris)
            self._interpreter.invoke()
            cikis = self._interpreter.get_tensor(self._cikis[0]['index'])[0]

            en_iyi_idx  = int(np.argmax(cikis))
            guven       = float(cikis[en_iyi_idx])
            ham_etiket  = (self._etiketler[en_iyi_idx]
                           if en_iyi_idx < len(self._etiketler)
                           else "bilinmiyor")

            tur = self._etiket_eslestir(ham_etiket)
            # Siniflandirici modelde bbox yok; basit merkez kutu donduruyoruz
            h, w = frame.shape[:2]
            bbox = (w // 4, h // 4, w * 3 // 4, h * 3 // 4)
            return tur, guven, bbox

        except Exception as e:
            print(f"[AI] Siniflandirma hatasi: {e}")
            return None, 0.0, None

    def _etiket_eslestir(self, ham: str) -> str | None:
        """Ham etiketi uygulama atik turune donusturur."""
        ham_lower = ham.lower()
        for anahtar, deger in LABEL_HARITASI.items():
            if anahtar.lower() in ham_lower:
                return deger
        return None

    # ── Gorsel cizimleri ───────────────────────────────────────────────────────

    def _cizim_yap(self, frame, tur, guven, bbox):
        if not CV2_OK or bbox is None:
            return
        renk = RENK_HARITASI.get(tur, VARSAYILAN_RENK)
        x1, y1, x2, y2 = bbox

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), renk, 3)

        # Etiket arka plani
        metin = f"{tur}  {guven*100:.0f}%"
        (tw, th), _ = cv2.getTextSize(metin, cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2)
        cv2.rectangle(frame, (x1, y1 - th - 14), (x1 + tw + 10, y1), renk, -1)

        # Etiket metni
        cv2.putText(frame, metin, (x1 + 5, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)

    @staticmethod
    def _frame_to_texture(frame) -> Texture:
        """OpenCV BGR frame'i Kivy Texture'a cevirir."""
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb   = cv2.flip(rgb, 0)          # Kivy Y-ekseni ters
        h, w  = rgb.shape[:2]
        tex   = Texture.create(size=(w, h), colorfmt='rgb')
        tex.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        return tex

    # ── Simule mod ─────────────────────────────────────────────────────────────

    def _simule_kare(self):
        """OpenCV/TFLite olmadanda UI'in test edilebilmesi icin sahte tespit."""
        import random
        turler = ["Izmarit", "Plastik", "Cam", "Pil", "Kagit"]
        tur    = random.choice(turler)
        guven  = random.uniform(0.82, 0.98)
        bbox   = (60, 80, 260, 320)
        print(f"[SIM] Tespit: {tur}  %{guven*100:.1f}")
        if self.on_tespit:
            Clock.schedule_once(
                lambda dt, t=tur, g=guven, b=bbox: self.on_tespit(t, g, b)
            )
