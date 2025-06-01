# PDF Özetleyici ve Dönüştürücü

Bu proje, PDF dosyalarını metne dönüştüren ve metinleri farklı seviyelerde özetleyen gelişmiş bir web uygulamasıdır. Cohere API kullanarak yapay zeka destekli özetleme yapar.

## 🌟 Özellikler

### PDF İşleme

- PDF dosyalarını metne dönüştürme
- Çok sayfalı PDF desteği
- Otomatik metin temizleme ve formatlama
- Büyük PDF dosyalarını akıllı parçalama

### Özetleme Seçenekleri

- **Yüzeysel Özet**: 4-5 cümlelik kısa özet
- **Orta Seviye**: 2-3 paragraf halinde detaylı özet
- **Ayrıntılı Özet**: 4-5 paragraf halinde kapsamlı özet
- **Kelimeye Göre Özet**: Belirli bir anahtar kelimeye odaklanan özel özet

### Performans Özellikleri

- Akıllı önbellekleme sistemi
- Paralel işleme desteği
- Otomatik hata yönetimi
- Zaman aşımı kontrolü

## 🚀 Kurulum

### Gereksinimler

- Node.js (v14 veya üzeri)
- npm (v6 veya üzeri)
- Modern bir web tarayıcısı
- Cohere API anahtarı

### Adımlar

1. Projeyi klonlayın:

```bash
git clone [repo-url]
cd pdf-summarizer
```

2. Bağımlılıkları yükleyin:

```bash
npm install
```

3. Cohere API anahtarınızı ayarlayın:

   - `server.js` dosyasında `COHERE_API_KEY` değişkenini güncelleyin
   - veya `.env` dosyası oluşturup `COHERE_API_KEY=your_api_key` şeklinde ekleyin

4. Sunucuyu başlatın:

```bash
node server.js
```

5. Tarayıcınızda `http://localhost:3000` adresini açın

## 💡 Kullanım

### PDF Yükleme

1. "PDF Seç" butonuna tıklayın
2. PDF dosyanızı seçin
3. Dönüştürme işleminin tamamlanmasını bekleyin

### Metin Özetleme

1. Metin kutusuna metninizi yapıştırın veya PDF'den dönüştürülen metni kullanın
2. Özetleme seviyesini seçin:
   - Yüzeysel: Hızlı genel bakış
   - Orta: Dengeli detay seviyesi
   - Ayrıntılı: Kapsamlı analiz
3. "Özetle" butonuna tıklayın

### Kelimeye Göre Özetleme

1. Metin kutusuna metninizi girin
2. Anahtar kelime kutusuna odaklanmak istediğiniz kelimeyi yazın
3. Özet seviyesini seçin
4. "Özetle" butonuna tıklayın

## ⚙️ Teknik Detaylar

### API Entegrasyonu

- Cohere API kullanılarak yapay zeka destekli özetleme
- Özelleştirilmiş promptlar ile kaliteli özetler
- Rate limiting ve hata yönetimi

### Performans Optimizasyonları

- Metin parçalarını önbellekleme
- Paralel API istekleri
- Akıllı metin bölme algoritması
- Otomatik önbellek temizleme

### Güvenlik Özellikleri

- API anahtarı güvenliği
- Rate limiting
- Input validasyonu
- Hata yönetimi

## 🔧 Geliştirme

### Proje Yapısı

```
pdf-summarizer/
├── server.js          # Sunucu kodu
├── script.js          # İstemci tarafı JavaScript
├── index.html         # Ana HTML dosyası
├── styles.css         # Stil dosyası
├── package.json       # Proje bağımlılıkları
└── README.md          # Dokümantasyon
```

### Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🤝 İletişim

Sorularınız veya önerileriniz için:

- GitHub Issues
- Pull Requests
- E-posta: [your-email@example.com]

## 🙏 Teşekkürler

- Cohere API ekibine
- Tüm katkıda bulunanlara
- Açık kaynak topluluğuna
