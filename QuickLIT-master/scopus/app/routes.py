from flask import Flask, render_template, request, jsonify, send_from_directory, Blueprint
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from .config import Config
import time
from functools import lru_cache
import json

app = Flask(__name__)
CORS(app)
load_dotenv()

# Blueprint oluştur
main = Blueprint('main', __name__)

# Scopus API yapılandırması
SCOPUS_API_KEY = Config.API_KEY
SCOPUS_BASE_URL = Config.SCOPUS_BASE_URL

# Cohere API anahtarı
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

# Cache süresi (saniye)
CACHE_DURATION = 3600  # 1 saat

# Cache için sözlük
cache = {}

# Son istek zamanını takip etmek için
last_request_time = 0
MIN_REQUEST_INTERVAL = 2  # İstekler arası minimum süre (saniye)

def get_cached_data(cache_key):
    if cache_key in cache:
        timestamp, data = cache[cache_key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
    return None

def set_cached_data(cache_key, data):
    cache[cache_key] = (time.time(), data)

def wait_for_rate_limit():
    global last_request_time
    current_time = time.time()
    time_since_last_request = current_time - last_request_time
    
    if time_since_last_request < MIN_REQUEST_INTERVAL:
        sleep_time = MIN_REQUEST_INTERVAL - time_since_last_request
        time.sleep(sleep_time)
    
    last_request_time = time.time()

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/discover')
def discover():
    return render_template('discover.html')

@main.route('/api/latest_articles', methods=['POST'])
def get_latest_articles():
    try:
        data = request.get_json()
        category = data.get('category', '')  # Seçilen kategori

        # Cache key oluştur
        cache_key = f"category_{category}"
        
        # Cache'den veriyi kontrol et
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return jsonify(cached_data)

        # Rate limiting için bekle
        wait_for_rate_limit()

        # Kategori bazlı sorgu oluştur
        category_mapping = {
            'computer_science': 'TITLE-ABS-KEY("artificial intelligence" OR "machine learning" OR "deep learning" OR "computer science")',
            'medicine': 'TITLE-ABS-KEY("medicine" OR "health" OR "clinical" OR "medical research")',
            'engineering': 'TITLE-ABS-KEY("engineering" OR "mechanical" OR "electrical" OR "civil engineering")',
            'physics': 'TITLE-ABS-KEY("physics" OR "quantum" OR "mechanics" OR "physical science")',
            'chemistry': 'TITLE-ABS-KEY("chemistry" OR "chemical" OR "molecular" OR "biochemistry")',
            'biology': 'TITLE-ABS-KEY("biology" OR "genetics" OR "molecular biology" OR "biotechnology")',
            'mathematics': 'TITLE-ABS-KEY("mathematics" OR "algebra" OR "calculus" OR "statistics")',
            'social_sciences': 'TITLE-ABS-KEY("social science" OR "sociology" OR "psychology" OR "anthropology")'
        }

        # Scopus API isteği için parametreler
        params = {
            'query': category_mapping.get(category, ''),
            'apiKey': SCOPUS_API_KEY,
            'httpAccept': 'application/json',
            'count': 5,  # Her kategoride 5 makale
            'sort': 'date'  # En yeni makaleler
        }

        headers = {
            'Accept': 'application/json'
        }

        print("API İsteği Parametreleri:", params)  # Debug log
        response = requests.get(SCOPUS_BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        print("API Yanıtı:", json.dumps(data, indent=2))  # Debug log
        
        articles = []

        if 'search-results' in data and 'entry' in data['search-results']:
            for entry in data['search-results']['entry']:
                print("İşlenen Makale:", json.dumps(entry, indent=2))  # Debug log
                
                # Scopus URL'ini bul
                scopus_url = ''
                for link in entry.get('link', []):
                    if link.get('@ref') == 'scopus':
                        scopus_url = link.get('@href', '')
                        break

                # Yazar bilgisini daha detaylı işle
                author = entry.get('dc:creator', '')
                if isinstance(author, list):
                    author = ', '.join(author)
                elif not author:
                    author = 'Yazar belirtilmemiş'

                # Başlık kontrolü
                title = entry.get('dc:title', '')
                if not title:
                    title = 'Başlık yok'

                # Dergi kontrolü
                journal = entry.get('prism:publicationName', '')
                if not journal:
                    journal = 'Dergi belirtilmemiş'

                # Tarih kontrolü
                pub_date = entry.get('prism:coverDate', '')
                if not pub_date:
                    pub_date = 'Tarih belirtilmemiş'

                article = {
                    'id': entry.get('dc:identifier', '').split(':')[-1],
                    'title': title,
                    'author': author,
                    'publicationDate': pub_date,
                    'journal': journal,
                    'scopusUrl': scopus_url
                }
                print("İşlenmiş Makale:", json.dumps(article, indent=2))  # Debug log
                articles.append(article)

        result = {'articles': articles}
        
        # Sonuçları cache'e kaydet
        set_cached_data(cache_key, result)
        
        return jsonify(result)

    except requests.exceptions.RequestException as e:
        print("API Hatası:", str(e))  # Debug log
        if '429' in str(e):
            return jsonify({
                'error': 'API istek limiti aşıldı. Lütfen birkaç dakika bekleyin.',
                'retry_after': 60
            }), 429
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print("Genel Hata:", str(e))  # Debug log
        return jsonify({'error': str(e)}), 500

@main.route('/article/<article_id>')
def get_article(article_id):
    # Scopus API'den makale detaylarını al
    # Bu örnek için basit bir yanıt döndürüyoruz
    return jsonify({
        'title': 'Makale Başlığı',
        'author': 'Yazar Adı'
    })

@main.route('/summarize', methods=['GET', 'POST'])
def summarize():
    if request.method == 'GET':
        return render_template('summarize.html')
        
    try:
        data = request.get_json()
        text = data.get('text')
        length = data.get('length', 'medium')
        format = data.get('format', 'paragraph')
        prompt = data.get('prompt')

        if not text or not text.strip():
            return jsonify({'error': 'Metin boş olamaz'}), 400

        if len(text) > 100000:
            return jsonify({'error': 'Metin çok uzun (max: 100,000 karakter)'}), 400

        # API key kontrolü
        if not COHERE_API_KEY:
            return jsonify({'error': 'Cohere API anahtarı bulunamadı'}), 500

        # Cohere API isteği
        response = requests.post(
            'https://api.cohere.ai/v1/summarize',
            json={
                'text': text,
                'length': length,
                'format': format,
                'model': 'summarize-xlarge',
                'prompt': prompt,
                'temperature': 0.7,
                'additional_command': f'Focus on: {prompt}' if prompt else None
            },
            headers={
                'Authorization': f'Bearer {COHERE_API_KEY}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )

        response.raise_for_status()
        return jsonify(response.json())

    except requests.Timeout:
        return jsonify({'error': 'Zaman aşımı: API yanıt vermedi. Lütfen tekrar deneyin.'}), 408
    except requests.RequestException as e:
        error_msg = e.response.json().get('message') if e.response else str(e)
        return jsonify({'error': error_msg}), e.response.status_code if e.response else 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Blueprint'i kaydet
app.register_blueprint(main) 