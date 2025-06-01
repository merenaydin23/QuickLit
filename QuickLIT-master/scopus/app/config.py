import os
import json
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv('SCOPUS_API_KEY')  # Scopus API Anahtarı
    SCOPUS_BASE_URL = "https://api.elsevier.com/content/search/scopus"
    
    # Mutlak yol kullanarak articles klasörünü belirle
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ARTICLES_FOLDER = os.path.join(BASE_DIR, 'articles')
    
    # Uygulama başlangıcında klasörün oluşturulduğundan emin ol
    os.makedirs(ARTICLES_FOLDER, exist_ok=True)
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # Firebase yapılandırması
    FIREBASE_CONFIG = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID'),
        "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID')
    }
    
    # Firebase Admin SDK yapılandırması
    CREDENTIALS_PATH = os.path.join(BASE_DIR, 'firebase-credentials.json')
    
    @staticmethod
    def get_firebase_credentials():
        try:
            with open(Config.CREDENTIALS_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Firebase credentials yüklenirken hata: {e}")
            return None
    
    @staticmethod
    def init_app(app):
        # Ana articles klasörünü oluştur
        if not os.path.exists(Config.ARTICLES_FOLDER):
            try:
                os.makedirs(Config.ARTICLES_FOLDER)
                print(f"Ana articles klasörü oluşturuldu: {Config.ARTICLES_FOLDER}")
            except Exception as e:
                print(f"Articles klasörü oluşturma hatası: {e}")
        
        # Alt klasörleri oluştur
        subfolders = ['pdf', 'other']
        for folder in subfolders:
            folder_path = os.path.join(Config.ARTICLES_FOLDER, folder)
            if not os.path.exists(folder_path):
                try:
                    os.makedirs(folder_path)
                    print(f"Alt klasör oluşturuldu: {folder_path}")
                except Exception as e:
                    print(f"Alt klasör oluşturma hatası ({folder}): {e}")
