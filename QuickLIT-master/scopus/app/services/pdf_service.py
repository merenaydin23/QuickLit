import os
import requests
import mimetypes
from xml.etree import ElementTree as ET
from ..config import Config
import traceback

class PDFService:
    @staticmethod
    def download_pdf(scopus_id):
        pdf_filename = f'article_{scopus_id}.pdf'
        
        # Klasörün varlığını kontrol et ve oluştur
        if not os.path.exists(Config.ARTICLES_FOLDER):
            try:
                os.makedirs(Config.ARTICLES_FOLDER)
                print(f"ARTICLES_FOLDER oluşturuldu: {Config.ARTICLES_FOLDER}")
            except Exception as e:
                print(f"Klasör oluşturma hatası: {e}")
                return {
                    "status": "error",
                    "message": f"PDF dosyaları için klasör oluşturulamadı: {str(e)}"
                }
        
        pdf_path = os.path.join(Config.ARTICLES_FOLDER, pdf_filename)
        print(f"PDF indirilecek yol: {pdf_path}")

        try:
            # Önce Scopus API üzerinden meta verileri al
            headers = {
                "X-ELS-APIKey": Config.API_KEY,
                "Accept": "application/json"
            }
            metadata_url = f"https://api.elsevier.com/content/abstract/scopus_id/{scopus_id}"
            
            print(f"Metadata URL: {metadata_url}")
            metadata_response = requests.get(metadata_url, headers=headers, timeout=30)
            
            if metadata_response.status_code != 200:
                print(f"Metadata API yanıt kodu: {metadata_response.status_code}")
                print(f"Metadata API yanıtı: {metadata_response.text}")
                return {
                    "status": "error",
                    "message": f"Scopus API'den makale bilgileri alınamadı (Kod: {metadata_response.status_code})"
                }
                
            metadata = metadata_response.json()

            # Makale bilgilerini al
            abstract_data = metadata.get('abstracts-retrieval-response', {})
            coredata = abstract_data.get('coredata', {})
            doi = coredata.get('prism:doi')
            pii = coredata.get('pii')
            title = coredata.get('dc:title', 'Unknown Title')
            
            print(f"Makale bilgileri: DOI={doi}, PII={pii}, Başlık={title}")
            
            # Scopus URL'ini al
            scopus_url = None
            links = abstract_data.get('link', [])
            for link in links:
                if isinstance(link, dict) and link.get('@rel') == 'scopus':
                    scopus_url = link.get('@href')
                    break

            # Farklı API endpointlerini dene
            endpoints = []
            
            # 1. Doğrudan PDF endpoint'i
            if doi:
                endpoints.append({
                    'url': f"https://api.elsevier.com/content/article/doi/{doi}",
                    'headers': {
                        "X-ELS-APIKey": Config.API_KEY,
                        "Accept": "application/pdf"
                    }
                })
            
            # 2. ScienceDirect API endpoint'i
            if pii:
                endpoints.append({
                    'url': f"https://api.elsevier.com/content/article/pii/{pii}",
                    'headers': {
                        "X-ELS-APIKey": Config.API_KEY,
                        "Accept": "application/pdf"
                    }
                })
            
            # 3. Scopus ID ile deneme
            endpoints.append({
                'url': f"https://api.elsevier.com/content/article/scopus_id/{scopus_id}",
                'headers': {
                    "X-ELS-APIKey": Config.API_KEY,
                    "Accept": "application/pdf",
                    "X-ELS-ResourceVersion": "FULL"
                }
            })

            success = False
            for endpoint in endpoints:
                try:
                    print(f"Endpoint deneniyor: {endpoint['url']}")
                    response = requests.get(endpoint['url'], headers=endpoint['headers'], timeout=30)
                    
                    print(f"API yanıt kodu: {response.status_code}")
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('Content-Type', '')
                        print(f"İçerik türü: {content_type}")
                        
                        # PDF içeriğini kaydet
                        with open(pdf_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Dosya boyutu kontrolü
                        file_size = os.path.getsize(pdf_path)
                        print(f"İndirilen dosya boyutu: {file_size} bytes")
                        
                        if file_size > 1000 and (content_type.startswith('application/pdf') or PDFService._is_pdf_content(response.content[:5])):
                            success = True
                            print("PDF başarıyla indirildi.")
                            return {"status": "success", "filename": pdf_filename}
                        else:
                            print("İndirilen dosya geçerli bir PDF değil.")
                            if os.path.exists(pdf_path):
                                os.remove(pdf_path)
                    
                except Exception as e:
                    print(f"Endpoint hatası ({endpoint['url']}): {str(e)}")
                    traceback.print_exc()
                    continue

            # Hiçbir endpoint çalışmadıysa, makale sayfasına yönlendir
            if scopus_url:
                print(f"PDF indirilemedi, Scopus URL'sine yönlendirilecek: {scopus_url}")
                return {
                    "status": "redirect",
                    "url": scopus_url,
                    "message": f"'{title}' başlıklı makale için PDF doğrudan indirilemedi. Makale sayfasına yönlendiriliyorsunuz."
                }
            elif doi:
                print(f"PDF indirilemedi, DOI'ye yönlendirilecek: {doi}")
                return {
                    "status": "redirect",
                    "url": f"https://doi.org/{doi}",
                    "message": f"'{title}' başlıklı makale için PDF doğrudan indirilemedi. DOI sayfasına yönlendiriliyorsunuz."
                }
            else:
                print("PDF indirilemedi, yönlendirilecek URL bulunamadı.")
                raise Exception("Makale için indirme bağlantısı bulunamadı. Lütfen Scopus üzerinden erişmeyi deneyin.")

        except Exception as e:
            print(f"PDF indirme hatası: {str(e)}")
            traceback.print_exc()
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            return {
                "status": "error",
                "message": f"PDF indirme hatası: {str(e)}"
            }

    @staticmethod
    def _is_pdf_content(content):
        """İçeriğin PDF olup olmadığını kontrol et"""
        return content.startswith(b'%PDF')

    @staticmethod
    def _is_valid_pdf(file_path):
        """PDF dosyasının geçerli olup olmadığını kontrol et"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)
                return header.startswith(b'%PDF')
        except Exception as e:
            print(f"PDF doğrulama hatası: {str(e)}")
            return False

    @staticmethod
    def _extract_pdf_url_from_xml(xml_content):
        """
        XML yanıtından PDF URL'sini çıkarır.
        """
        try:
            root = ET.fromstring(xml_content)
            namespaces = {
                'dtd': 'http://www.elsevier.com/xml/svapi/abstract/dtd',
                'xlink': 'http://www.w3.org/1999/xlink'
            }
            link_elements = root.findall(".//dtd:link", namespaces)
            for link in link_elements:
                if link.attrib.get('rel') == 'scopus' or link.attrib.get('rel') == 'full-text':
                    return link.attrib.get('{http://www.w3.org/1999/xlink}href')
        except ET.ParseError as e:
            print(f"XML parse hatası: {str(e)}")
        return None
