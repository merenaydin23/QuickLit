# QuickLIT

QuickLIT, akademik literatür araştırması ve PDF özetleme için geliştirilmiş bir projedir. İki ana bileşenden oluşur:

1. **Scopus** - Akademik makale arama aracı
2. **Cohere** - PDF dönüştürme ve özetleme aracı

## Kurulum

Projeyi kullanmak için aşağıdaki adımları izleyin:

1. Python 3.8 veya daha yüksek bir sürümü yükleyin.
2. Virtual environment oluşturun:
   ```
   python -m venv .venv
   ```
3. Virtual environment'ı aktifleştirin:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Gerekli paketleri yükleyin:
   ```
   pip install -r scopus/requirements.txt
   ```

## API Anahtarı Yapılandırması

Bu proje çeşitli API servisleri kullanır. Güvenlik için API anahtarları `.env` dosyasında saklanır.

### .env Dosyası Oluşturma

1. Proje kök dizininde `.env.example` dosyasını `.env` olarak kopyalayın:

   ```
   cp .env.example .env
   ```

2. `.env` dosyasını düzenleyin ve API anahtarlarınızı ekleyin:

   ```
   # API Anahtarları
   SCOPUS_API_KEY=your_scopus_api_key_here
   COHERE_API_KEY=your_cohere_api_key_here

   # Firebase Yapılandırması
   FIREBASE_API_KEY=your_firebase_api_key
   FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   FIREBASE_PROJECT_ID=your_project_id
   FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
   FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   FIREBASE_APP_ID=your_app_id
   FIREBASE_MEASUREMENT_ID=your_measurement_id
   ```

### API Anahtarları Nasıl Alınır

- **Scopus API**: [Elsevier Developer Portal](https://dev.elsevier.com/) üzerinden ücretsiz hesap oluşturun
- **Cohere API**: [Cohere](https://cohere.ai/) platformuna kaydolun
- **Firebase**: [Firebase Console](https://console.firebase.google.com/) üzerinden proje oluşturun

**⚠️ Güvenlik Uyarısı**: `.env` dosyasını asla GitHub'a yüklemeyin. Bu dosya `.gitignore` listesinde bulunur.

## Çalıştırma

QuickLIT uygulamasını basitçe şu komutla çalıştırabilirsiniz:

```
python run.py
```

Bu komut Scopus uygulamasını `http://localhost:3000` adresinde başlatır.

### Scopus Uygulamasını Doğrudan Çalıştırma

Scopus uygulamasını doğrudan çalıştırmak için:

```
cd scopus
python run.py
```

### Cohere Uygulamasını Çalıştırma

Cohere uygulamasını çalıştırmak için (ayrı bir terminal penceresinde):

1. Node.js bağımlılıklarını yükleyin:

   ```
   cd Cohere
   npm install
   ```

2. Cohere klasöründe `.env` dosyası oluşturun:

   ```
   COHERE_API_KEY=your_cohere_api_key_here
   PORT=3000
   ```

3. Uygulamayı başlatın:
   ```
   npm start
   ```

## Bağımlılık Uyumluluğu

QuickLIT, aşağıdaki spesifik sürümleri kullanır:

- Flask: 2.0.1
- Werkzeug: 2.0.1

Bu sürümler arasında uyumluluk gereklidir.

## Sorun Giderme

1. Eğer uygulamayı çalıştırırken `ImportError: cannot import name 'url_quote'` hatası alırsanız:

   ```
   pip uninstall -y flask werkzeug
   pip install flask==2.0.1 werkzeug==2.0.1
   ```

2. API anahtarı hataları alıyorsanız `.env` dosyasının doğru konumda olduğundan emin olun.

3. Uygulama başlamazsa, doğru dizinde olduğunuzdan emin olun.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır.
