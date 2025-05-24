# AI Müzik Kontrolü

Bilgisayar görüşü ve yapay zeka kullanarak kafa hareketleriyle sistem genelinde medya kontrolü sağlayan bir Python uygulaması.

🎥 **Demo Videosu:**
[![Watch the video](https://img.youtube.com/vi/gYeDIzXR20M/0.jpg)](https://youtu.be/gYeDIzXR20M)

## Özellikler

- Gerçek zamanlı yüz algılama ve yüz işaretleri takibi
- Kafa hareketleriyle medya kontrolü:
  - Kafayı sağa çevirme: Sonraki şarkı
  - Kafayı sola çevirme: Önceki şarkı
  - Kafayı yukarı/aşağı hareket ettirme: Oynat/Duraklat
  - Özel hareket algılama: Sessiz/Sesli geçiş
- Kullanıcı dostu arayüz, video akışı ve günlük konsolu
- Spotify, YouTube, Apple Music gibi herhangi bir medya uygulamasını kontrol edebilme

## Gereksinimler

- Python 3.7+
- Webcam
- requirements.txt dosyasında listelenen bağımlılıklar

## Kurulum

1. Bu depoyu klonlayın
2. Bağımlılıkları yükleyin:
   ```
   pip install -r requirements.txt
   ```

## Kullanım

1. Önce kontrol etmek istediğiniz medya uygulamasını açın (Spotify, YouTube, vb.)
2. Ardından uygulamayı çalıştırın:
   ```
   python main.py
   ```
3. Kafa hareketlerinizle medya kontrolünü sağlayın

## Proje Yapısı

- `main.py`: Uygulama giriş noktası
- `face_detector.py`: Yüz algılama ve işaret takibi modülü
- `music_controller.py`: Medya kontrolü modülü (sistem genelinde medya tuşlarını simüle eder)
- `gui.py`: PyQt5 tabanlı grafik kullanıcı arayüzü
- `utils.py`: Yardımcı fonksiyonlar

## Lisans

Detaylar için LICENSE dosyasına bakın.

## Ortam (Environment) Kurulumu

### 1. Python Sürümü
- **Python 3.10.x** önerilir. (MediaPipe ve bazı kütüphaneler için 3.11 ve üstü uyumsuz olabilir.)
- [Python İndir](https://www.python.org/downloads/release/python-3100/)

### 2. Sanal Ortam Oluşturma
Proje dizininde terminal açıp:

```bash
python -m venv venv
```

### 3. Sanal Ortamı Aktifleştirme
- **Windows:**
  ```bash
  .\venv\Scripts\activate
  ```
- **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 4. Bağımlılıkları Yükleme

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Not:** Eğer `mediapipe` veya `opencv-python` yüklenmezse, pip ve setuptools'u güncellediğinizden emin olun.

### 5. Uygulamayı Çalıştırma

```bash
python main.py
```

---

## Ekstra Notlar
- **Kamera erişimi** gereklidir.
- **Windows** sistemlerde medya tuşları için ek izin gerekmez.
- Eğer başka bir ortamda çalıştıracaksanız, `requirements.txt` ve Python sürümünü kontrol edin.

---

## Sorun Giderme
- `mediapipe` yüklenmiyorsa, Python sürümünüzü kontrol edin (3.10.x önerilir).
- `cv2` (OpenCV) bulunamıyorsa, sanal ortamın aktif olduğundan ve doğru pip ile yüklediğinizden emin olun.
- Kamera açılmıyorsa, başka bir uygulamanın kamerayı kullanmadığından emin olun.

---

Her türlü soru ve katkı için issue veya pull request açabilirsiniz! 

