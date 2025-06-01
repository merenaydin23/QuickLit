from flask import Flask, render_template, request, redirect, flash, jsonify, send_file, session
import os
import firebase_admin
from firebase_admin import credentials, auth, firestore
from .config import Config
from .services.scopus_service import ScopusService
from .services.pdf_service import PDFService
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    
    # CORS desteğini ekle
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Uygulama yapılandırması
    app.config.from_object(Config)
    Config.init_app(app)
    app.secret_key = Config.SECRET_KEY

    # Firebase Admin SDK'yı başlat
    try:
        cred_dict = Config.get_firebase_credentials()
        if cred_dict:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK başarıyla başlatıldı")
        else:
            raise ValueError("Firebase credentials yüklenemedi")
    except Exception as e:
        print(f"Firebase Admin SDK başlatma hatası: {e}")

    # Firestore veritabanı referansı
    try:
        db = firestore.client()
    except Exception as e:
        print(f"Firestore bağlantı hatası: {e}")
        db = None

    @app.route('/firebase_login', methods=['POST'])
    def firebase_login():
        if not db:
            return redirect('/')
            
        id_token = request.form.get('idToken')
        if not id_token:
            return redirect('/')
            
        try:
            # Firebase token'ını doğrula
            decoded_token = auth.verify_id_token(id_token)
            user_id = decoded_token['uid']
            user = auth.get_user(user_id)
            
            # Session'a kullanıcı bilgilerini kaydet
            session['user_id'] = user_id
            session['email'] = user.email
            
            # Profil sayfasına yönlendir
            return redirect('/profile')
        except Exception as e:
            print(f"Firebase token doğrulama hatası: {e}")
            return redirect('/')

    @app.route('/login', methods=['POST'])
    def login():
        if not db:
            return jsonify({'success': False, 'message': 'Firebase bağlantısı kurulamadı'})
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        try:
            # Firebase Authentication ile giriş yap
            user = auth.get_user_by_email(email)
            session['user_id'] = user.uid
            session['email'] = user.email
            return jsonify({'success': True, 'user': {'email': user.email}})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    @app.route('/register', methods=['POST'])
    def register():
        if not db:
            return jsonify({'success': False, 'message': 'Firebase bağlantısı kurulamadı'})
            
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        try:
            # Firebase Authentication ile kullanıcı oluştur
            user = auth.create_user(
                email=email,
                password=password
            )
            
            # Firestore'da kullanıcı verilerini kaydet
            db.collection('users').document(user.uid).set({
                'email': email,
                'created_at': firestore.SERVER_TIMESTAMP,
                'saved_articles': []
            })
            
            return jsonify({'success': True, 'user': {'email': email}})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    @app.route('/check_login')
    def check_login():
        if not db:
            return jsonify({'logged_in': False, 'message': 'Firebase bağlantısı kurulamadı'})
            
        if 'user_id' in session:
            try:
                user = auth.get_user(session['user_id'])
                return jsonify({
                    'logged_in': True,
                    'user': {
                        'email': user.email,
                        'uid': user.uid
                    }
                })
            except:
                session.clear()
                return jsonify({'logged_in': False})
        return jsonify({'logged_in': False})

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/')

    @app.route('/profile')
    def profile():
        if not db:
            flash('Veritabanı bağlantısı kurulamadı.', 'error')
            return redirect('/')
            
        if 'user_id' not in session:
            print("Oturum bilgisi bulunamadı")
            return redirect('/')
            
        try:
            user_id = session['user_id']
            print(f"Profil verisi alınıyor - user_id: {user_id}")
            
            user = auth.get_user(user_id)
            print(f"Firebase kullanıcısı bulundu: {user.email}")
            
            # Kullanıcının kaydedilmiş makalelerini getir
            user_doc = db.collection('users').document(user_id).get()
            
            if not user_doc.exists:
                print(f"Firestore'da kullanıcı verisi bulunamadı: {user_id}")
                # Kullanıcı Firestore'da yok, oluştur
                db.collection('users').document(user_id).set({
                    'email': user.email,
                    'displayName': user.display_name or user.email.split('@')[0],
                    'firstName': '',
                    'lastName': '',
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'savedArticles': []
                })
                saved_articles = []
                display_name = user.display_name or user.email.split('@')[0]
                registration_date = "Yeni Üye"
                print(f"Yeni kullanıcı verisi oluşturuldu: {user_id}")
            else:
                print(f"Firestore'dan kullanıcı verisi alındı: {user_id}")
                # Kaydedilmiş makaleleri ve kullanıcı bilgilerini al
                user_data = user_doc.to_dict()
                
                # Önceki veri yapısına uyumluluk için kontrol - her iki alanı da dene
                if 'savedArticles' in user_data:
                    saved_articles = user_data.get('savedArticles', [])
                    print(f"'savedArticles' alanı bulundu, {len(saved_articles)} makale var")
                elif 'saved_articles' in user_data:
                    saved_articles = user_data.get('saved_articles', [])
                    print(f"'saved_articles' alanı bulundu, {len(saved_articles)} makale var")
                else:
                    saved_articles = []
                    print("Hiçbir makale alanı bulunamadı")
                
                # savedArticles alanının array olduğundan emin ol
                if not isinstance(saved_articles, list):
                    print(f"Profil sayfası uyarı: savedArticles array değil - {type(saved_articles)}")
                    saved_articles = []
                
                # Kullanıcı adını getir
                display_name = user_data.get('displayName', user.display_name) 
                if not display_name:
                    display_name = user.email.split('@')[0]
                
                # Kayıt tarihini formatla
                created_at = user_data.get('created_at')
                if created_at:
                    from datetime import datetime
                    created_timestamp = created_at.timestamp()
                    date_str = datetime.fromtimestamp(created_timestamp).strftime('%d/%m/%Y')
                    registration_date = date_str
                else:
                    registration_date = "Belirtilmemiş"
                
            # Güvenli JSON dönüşümü için değerleri temizle
            cleaned_articles = []
            for article in saved_articles:
                if isinstance(article, dict) and article.get('id'):
                    cleaned_article = {
                        'id': article.get('id', ''),
                        'title': article.get('title', 'Başlık yok'),
                        'author': article.get('author', 'Yazar belirtilmemiş'),
                        'savedAt': article.get('savedAt', ''),
                        'notes': article.get('notes', None)
                    }
                    cleaned_articles.append(cleaned_article)
            
            print(f"Profil sayfası: {len(cleaned_articles)} makale temizlendi ve hazırlandı")
            
            # JSON dönüşümü testi
            from flask import json
            try:
                # JSON dönüşümünü test et
                articles_json = json.dumps(cleaned_articles)
                print(f"JSON dönüşümü başarılı, boyut: {len(articles_json)} byte")
                if len(articles_json) < 200:
                    print(f"Makaleler JSON: {articles_json}")  # Küçükse tamamını logla
                else:
                    print(f"Makaleler JSON (ilk 200 karakter): {articles_json[:200]}...")
            except Exception as json_err:
                print(f"JSON dönüşüm hatası: {json_err}")
                cleaned_articles = []  # Hata durumunda boş liste gönder
                
            return render_template('profile.html', 
                                email=user.email,
                                display_name=display_name,
                                registration_date=registration_date,
                                saved_articles=cleaned_articles)
        except Exception as e:
            print(f"Profil sayfası hatası: {e}")
            import traceback
            traceback.print_exc()  # Hatanın stack trace'ini yazdır
            session.clear()  # Hata durumunda session'ı temizle
            return redirect('/')

    @app.route('/get_saved_articles')
    def get_saved_articles():
        if not db:
            return jsonify({'success': False, 'message': 'Firebase bağlantısı kurulamadı'})
            
        if 'user_id' in session:
            try:
                user_doc = db.collection('users').document(session['user_id']).get()
                saved_articles = user_doc.get('saved_articles', []) if user_doc.exists else []
                return jsonify({'success': True, 'articles': saved_articles})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        return jsonify({'success': False, 'message': 'Not logged in'})

    # Hata yönetimi
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    # API durumu kontrolü
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "ok"})

    # Ana sayfa route'u
    @app.route('/', methods=['GET', 'POST'])
    def home():
        results = None
        error = None
        page = request.args.get('page', 1, type=int)
        per_page = 10
        query = request.form.get('query', request.args.get('query', ''))
        
        if request.method == 'POST' or query:
            try:
                start = (page - 1) * per_page
                results = ScopusService.search_articles(
                    query,
                    per_page,
                    start
                )
            except Exception as e:
                error = str(e)

        return render_template('index.html', 
                             results=results, 
                             error=error,
                             current_page=page,
                             query=query)

    # PDF indirme route'u
    @app.route('/download_pdf/<scopus_id>')
    def download_pdf(scopus_id):
        try:
            result = PDFService.download_pdf(scopus_id)
            
            if result["status"] == "redirect":
                return jsonify({
                    "status": "redirect",
                    "url": result["url"],
                    "message": result.get("message", "PDF doğrudan indirilemedi. Makale sayfasına yönlendiriliyorsunuz.")
                })
            
            if result["status"] == "error":
                return jsonify({
                    "status": "error",
                    "message": result.get("message", "PDF indirilemedi.")
                })
            
            pdf_path = os.path.join(Config.ARTICLES_FOLDER, result["filename"])
            
            if os.path.exists(pdf_path):
                return send_file(
                    pdf_path,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=result["filename"]
                )
            else:
                return jsonify({
                    "status": "error",
                    "message": "PDF dosyası bulunamadı. Lütfen tekrar deneyin."
                })
                
        except Exception as e:
            app.logger.error(f"PDF indirme hatası: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}"
            })

    # Blueprint'i kaydet
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
