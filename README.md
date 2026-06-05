# ♻️ Atık Avcısı v1.0

**Yapay Zeka Destekli Çevre Bilinci ve Atık Yönetimi Oyunlaştırma Yazılımı**

Atık Avcısı, çevre kirliliğiyle mücadeleyi dijital bir avcılık ve ödül mekanizmasına dönüştüren yenilikçi bir mobil platformdur. Bu proje, geri dönüşümü sıkıcı bir zorunluluk olmaktan çıkarıp, ölçülebilir ve ödüllendirilebilir bir alışkanlık haline getirmeyi hedeflemektedir.

## 📌 Proje Vizyonu ve İhtiyaç Analizi
Günümüzde geri dönüşümün önündeki temel engel motivasyon eksikliğidir. Özellikle Iğdır gibi çevre kirliliğinin kritik seviyelerde olduğu bölgelerde atık yönetimi konusunda yenilikçi adımlara ihtiyaç duyulmaktadır. 

Temel amacımız; kullanıcıların topladıkları atıkları yapay zeka destekli kamera aracılığıyla "avlamasını", bu verileri doğrulanmış puanlara (XP) dönüştürmesini ve oyunlaştırılmış bir seviye sistemi üzerinden sürdürülebilir alışkanlıklar kazanmasını sağlamaktır.

## 🛠 Kullanılan Teknolojiler
* **Programlama Dili:** Python
* **Kullanıcı Arayüzü (UI):** Kivy
* **Görüntü İşleme & Yapay Zeka:** OpenCV, NumPy
* **Veri Yönetimi:** JSON

## 🚀 Teknik Altyapı ve Sistem Mimarisi
Proje, MVC (Model-View-Controller) prensibine uygun olarak geliştirilmiştir. Model kısmında çevrimdışı çalışma kabiliyetini optimize eden JSON verileri, View kısmında Kivy arayüzü ve Controller kısmında ise AI metotları birbirinden bağımsız şekilde kurgulanmıştır.

### 🧠 Yapay Zeka (AI) ile Atık Tanımlama
Projenin en kritik teknolojik bileşeni, kamera aracılığıyla alınan görüntüleri analiz eden yapay zeka tabanlı nesne tanıma sistemidir.
* **Akıllı Teşhis:** Taranan materyaller (plastik, kağıt, cam vb.) eğitilmiş veri modelleri üzerinden geçirilerek yüksek doğruluk oranıyla otomatik olarak teşhis edilir.
* **Güven Skoru (Confidence Score):** AI kamera modülü, nesneyi görsel olarak doğrulamadan ve %80 üzeri bir güven skoru almadan puan eklenmesine izin vermez. Güven oranı düşükse sistem otomatik onay vermez ve kullanıcıdan "Yeniden Tara"ması istenir.
* **Hatalı Veri Önleme:** Kullanıcı onayı mekanizması sayesinde hatalı girişler engellenir ve makine öğrenmesi süreci desteklenir.

### 🎮 Oyunlaştırma ve Kullanıcı Paneli
* **Anlık Geri Bildirim:** Kullanıcılar, her atık için kazandıkları XP'yi ve seviye ilerlemelerini dinamik olarak takip edebilir. XP katsayıları, atıkların doğada yok olma süreleri temel alınarak hesaplanmıştır.
* **Ekolojik Farkındalık:** Kullanıcılara anlık eğitici veriler sunulur (Örn: Bir pil 400 litre suyu zehirler).

## 📊 Proje Yönetimi Metodolojisi
Geliştirme sürecinde Çevik (Agile) yönetim yaklaşımı esas alınmıştır. Projenin iş kırılım yapısı (WBS); Analiz, Tasarım, AI Geliştirme ve Validasyon olmak üzere dört ana hiyerarşik faza bölünmüştür. Süreç boyunca görev takibi "Yapılacaklar", "Devam Edenler" ve "Bitenler" listeleri üzerinden dinamik olarak yürütülmüştür.

## 🌍 Gelecek Vizyonu ve Ölçeklendirme
* **IoT (Akıllı Konteyner) Entegrasyonu:** Gelecek aşamalarda geri dönüşüm kutularına eklenecek akıllı sensörler ile anlık dijital doğrulama yapılması.
* **Ödül Ağı:** Toplanan puanların (XP) iş ortaklıkları üzerinden indirimlere, dijital cüzdan bakiyesine veya nakit iade (cashback) sistemine dönüştürülmesi.
* **AI Kapsamının Genişletilmesi:** Modelin eğitilerek elektronik atık ve tekstil gibi türleri de tanıması.

---
**👩‍💻 Geliştirici:** Selenay Tuna  
*Iğdır Üniversitesi - Bilgisayar Mühendisliği*  
*Proje Yönetimi ve Girişimcilik Dersi Kapsamında Hazırlanmıştır.*
