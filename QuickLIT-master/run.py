#!/usr/bin/env python
"""
QuickLIT ana çalıştırma dosyası
Scopus uygulamasını çalıştırır
"""

import os
import sys
import subprocess

def main():
    """
    Scopus uygulamasını çalıştırır
    """
    print("QuickLIT Scopus uygulaması başlatılıyor...")
    
    # Scopus dizinine git
    os.chdir('scopus')
    
    # Uygulamayı çalıştır
    try:
        subprocess.run([sys.executable, 'run.py'], check=True)
    except KeyboardInterrupt:
        print("\nUygulama kapatıldı.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == '__main__':
    main() 