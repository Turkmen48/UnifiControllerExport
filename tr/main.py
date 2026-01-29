import sys
import subprocess
import time

# -------------------------------------------------------------
# DİKKAT: Bu kodun çalışması için sistemde pymongo 3.12.3 yüklü olmalıdır.
# Komut: pip3 install pymongo==3.12.3
# Eğer pymongo yüklüyse ve hata alıyorsanız, mevcut pymongo sürümünü kaldırıp
# belirtilen sürümü yükleyin: pip3 uninstall pymongo
# -------------------------------------------------------------

# Bağlantı Ayarları
# Script Unifi OS Container içinde çalışıyorsa '127.0.0.1' kullanılır.
# Eğer dışarıdan bağlanıyorsanız buraya Unifi IP adresini yazın.

def install_correct_pymongo():
    print("PyMongo sürümü kontrol ediliyor...")
    try:
        import pymongo
        version = pymongo.__version__
        print(f"Mevcut PyMongo Sürümü: {version}")
        
        # Eğer sürüm 3 ile başlamıyorsa (Örn: 4.x.x ise)
        if not version.startswith("3."):
            print("UYUMSUZ SÜRÜM TESPİT EDİLDİ! Otomatik düzeltme başlatılıyor...")
            print("Mevcut sürüm kaldırılıyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "pymongo", "-y"])
            
            print("Uyumlu sürüm (3.12.3) yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pymongo==3.12.3"])
            
            print("Yükleme tamamlandı! Scriptin yeni kütüphaneyi görmesi için lütfen bu scripti TEKRAR ÇALIŞTIRIN.")
            sys.exit(0) # İşlem bitti, kullanıcı tekrar başlatsın diye çıkıyoruz.
            
    except ImportError:
        print("PyMongo hiç yüklü değil. Yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymongo==3.12.3"])
        print("Yükleme bitti. Lütfen scripti tekrar çalıştırın.")
        sys.exit(0)

# Bu fonksiyonu en başta çağırıyoruz
install_correct_pymongo()
# --- OTOMATİK DÜZELTME BİTİŞİ ---

import csv
from pymongo import MongoClient

# ... KODUNUZUN GERİ KALANI BURADAN DEVAM EDİYOR ...

# Bağlantı ayarları (Unifi OS Container içindeyse 127.0.0.1, dışındaysa IP)
# Eğer scripti container içine taşıdıysanız burası 127.0.0.1 kalmalı.
client = MongoClient('127.0.0.1', 27117)

db = client['ace']
devices = db['device']
sites = db['site']
settings = db['setting']
device_rows = []
sites_dict = {}
hostname = "unknown"

# Settings kısmında hata almamak için koruma
try:
    for setting in settings.find():
        hostname = setting.get("hostname", "unknown")
        break
except Exception as e:
    print(f"Hostname hatası: {e}")

# Siteleri çekme
print("Siteler işleniyor...")
for site in sites.find():
    try:
        site_id = str(site["_id"])
        sites_dict[site_id] = {"desc": site.get("desc", "no-desc"), "name": site.get("name", "default")}
    except Exception as e:
        print(f"Site hatası: {e}")

# Cihazları çekme
print("Cihazlar işleniyor...")
for device in devices.find():
    try:
        device_name = device.get("name", "")
        if not device_name:
            device_name = device.get("mac", "Unknown") # İsim yoksa mac yazsın

        # Güvenli veri çekme (Hata verirse boş string koyar)
        site_id = device.get("site_id")
        site_info = sites_dict.get(site_id, {"desc": "Unknown", "name": "default"})
        
        device_row = [
            device_name, 
            device.get("model", ""), 
            device.get("mac", ""), 
            device.get("version", ""), 
            site_info["desc"], 
            device.get("model_in_lts", ""), 
            device.get("model_in_eol", ""), 
            device.get("adopted", ""), 
            "https://" + hostname + ":8443/manage/" + site_info["name"] + "/devices"
        ]
        device_rows.append(device_row)
        print(device_row)
    except Exception as e:
        print(f"Cihaz döngüsünde hata: {e}")

# CSV Kaydetme
try:
    with open('devices.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Model", "Mac", "Firmware", "Site", "LTS", "EOL", "Adopted", "Link"])
        for device_row in device_rows:
            writer.writerow(device_row)
    print("İşlem Başarılı. devices.csv oluşturuldu.")
except Exception as e:
    print(f"Dosya yazma hatası: {e}")