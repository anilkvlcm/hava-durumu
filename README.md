# 🌦️ Hava Durumu Uygulaması

Bu proje, Python ile geliştirilen bir masaüstü hava durumu uygulamasıdır. Kullanıcı kayıt/giriş sistemi içerir ve OpenWeatherMap API'si üzerinden canlı hava durumu verilerini gösterir. Ayrıca yapılan sorgular kullanıcı bazlı olarak yerel veritabanına kaydedilir.

## 🔧 Kullanılan Teknolojiler

- **Python 3**
- **SQLite3** (Veritabanı)
- **Tkinter** (Arayüz)
- **Pillow** (Görsel desteği)
- **Requests** (API çağrıları)
- **OpenWeatherMap API**

## 🧰 Özellikler

- ✅ Kullanıcı kayıt ve giriş sistemi  
- ✅ Ülke → Eyalet → Şehir seçimli konum sistemi  
- ✅ OpenWeatherMap üzerinden hava durumu sorgulama  
- ✅ Sorgu sonuçlarını ikon ve açıklamalarla görselleştirme  
- ✅ Kullanıcı bazlı sorgu geçmişi kaydı  
- ✅ SQLite veritabanı ile veri saklama  

## 📝 Kurulum Adımları

1. **Python 3** yüklü değilse [python.org](https://www.python.org/downloads/) üzerinden indirip kurun.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install pillow requests
