# 📚 Scopus Academic Finder

Scopus API kullanarak akademik makale arama ve PDF indirme uygulaması. Araştırmacılar için geliştirilmiş, kullanıcı dostu bir arayüz sunar.

## 🌟 Özellikler

### 🔍 Arama Özellikleri

- Gelişmiş anahtar kelime araması
- Sonuç sayısı özelleştirme (1-100 aralığında)
- Anlık sonuç gösterimi

### 📖 Makale Yönetimi

- Makale başlığı, yazar ve yayın tarihi görüntüleme
- Scopus sayfasına doğrudan erişim
- PDF indirme ve otomatik organize etme
- İndirilen makaleleri yerel klasörde saklama

### 💻 Teknik Özellikler

- Modüler ve bakımı kolay kod yapısı
- Responsive tasarım
- Hata yönetimi ve bildirim sistemi
- RESTful API entegrasyonu

## ⚙️ Kurulum

### Gereksinimler

```bash
Python 3.7+
Flask
Requests
```

### Kurulum Adımları

1. Projeyi klonlayın:

```bash
git clone https://github.com/username/scopus-academic-finder.git
cd scopus-academic-finder
```

2. Sanal ortam oluşturun:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Bağımlılıkları yükleyin:

```bash
pip install flask requests
```

4. Yapılandırma:
   - `app/config.py` dosyasında:
     - `API_KEY`: Scopus API anahtarınızı girin
     - `SECRET_KEY`: Güvenli bir anahtar belirleyin

## 🚀 Kullanım

1. Uygulamayı başlatın:

```bash
python run.py
```

2. Tarayıcıda açın:

```
http://localhost:5000
```

## 📁 Proje Yapısı

```
scopus-academic-finder/
├── app/
│   ├── __init__.py          # Flask app yapılandırması
│   ├── config.py            # Konfigürasyon ayarları
│   ├── services/            # Servis katmanı
│   │   ├── scopus_service.py    # Scopus API işlemleri
│   │   ├── pdf_service.py       # PDF indirme işlemleri
│   ├── static/              # Statik dosyalar
│   │   └── css/
│   └── templates/           # HTML şablonları
├── makaleler/               # İndirilen PDF'ler
├── run.py                   # Başlatma scripti
```

## ❗ Hata Çözümleri

### Sık Karşılaşılan Sorunlar

1. **API Hataları**
   - API anahtarınızın geçerliliğini kontrol edin.
   - İstek limitinizi kontrol edin.

2. **PDF İndirme Sorunları**
   - Makalenin açık erişimli olduğundan emin olun.
   - Disk alanınızı kontrol edin.

3. **Uygulama Hataları**
   - Flask debug modunda hata mesajlarını kontrol edin.
   - Konsol çıktılarını inceleyin.

## 🔄 Güncelleme Geçmişi

- **v1.0.0**: İlk sürüm
  - Temel arama fonksiyonu
  - PDF indirme özelliği
  - Modern arayüz tasarımı

## 📝 Notlar

- API kullanımı için Scopus hesabı gereklidir.
- Bazı makaleler ücretli veya kısıtlı erişimli olabilir.
- PDF indirme özelliği sadece açık erişimli makalelerde çalışır.
