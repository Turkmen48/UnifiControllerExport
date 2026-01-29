import sys
import csv

# --- SÜRÜM KONTROLÜ BAŞLANGICI ---
# Bu blok sadece kontrol yapar, yükleme yapmaz.
def check_pymongo_version():
    try:
        import pymongo
        version = pymongo.__version__
        
        # Eğer sürüm 3 ile başlamıyorsa (Örn: 4.6.1 ise) hata verip çıkar
        if not version.startswith("3."):
            print("\n" + "!"*60)
            print("KRİTİK HATA: UYUMSUZ PYMONGO SÜRÜMÜ!")
            print(f"Sistemdeki Sürüm: {version}")
            print("Bu script Unifi veritabanı ile konuşmak için PyMongo 3.x gerektirir.")
            print("-" * 60)
            print("LÜTFEN TERMİNALDE ŞU KOMUTLARI ELLE ÇALIŞTIRIN:")
            print("1. pip3 uninstall pymongo -y")
            print("2. pip3 install pymongo==3.12.3")
            print("!"*60 + "\n")
            sys.exit(1) # Kod burada durur, devam etmez.
            
        print(f"PyMongo Sürümü Uygun: {version}. İşleme devam ediliyor...")

    except ImportError:
        print("\n" + "!"*60)
        print("HATA: PyMongo kütüphanesi hiç bulunamadı!")
        print("Lütfen şu komutu çalıştırın: pip3 install pymongo==3.12.3")
        print("!"*60 + "\n")
        sys.exit(1)

# Kontrolü en başta çalıştır
check_pymongo_version()
# --- SÜRÜM KONTROLÜ BİTİŞİ ---

from pymongo import MongoClient

# Bağlantı Ayarları
# Script Unifi OS Container içinde çalışıyorsa (nsenter ile) '127.0.0.1' kullanılır.
client = MongoClient('127.0.0.1', 27117)

db = client['ace']
devices = db['device']
sites = db['site']
settings = db['setting']
device_rows = []
sites_dict = {}
hostname = "unknown"

# Hostname Bulma
try:
    for setting in settings.find():
        hostname = setting.get("hostname", "unknown")
        break
except Exception as e:
    print(f"Hostname hatası: {e}")

# Siteleri Listeleme
print("Siteler işleniyor...")
for site in sites.find():
    try:
        site_id = str(site["_id"])
        sites_dict[site_id] = {"desc": site.get("desc", "no-desc"), "name": site.get("name", "default")}
    except Exception as e:
        print(f"Site hatası: {e}")

# Cihazları Listeleme
print("Cihazlar işleniyor...")
for device in devices.find():
    try:
        device_name = device.get("name", "")
        if not device_name:
            device_name = device.get("mac", "Unknown")

        site_id = device.get("site_id")
        site_info = sites_dict.get(site_id, {"desc": "Unknown", "name": "default"})
        
        # Link oluşturma
        manage_link = f"https://{hostname}:8443/manage/{site_info['name']}/devices"

        device_row = [
            device_name, 
            device.get("model", ""), 
            device.get("mac", ""), 
            device.get("version", ""), 
            site_info["desc"], 
            device.get("model_in_lts", ""), 
            device.get("model_in_eol", ""), 
            device.get("adopted", ""), 
            manage_link
        ]
        device_rows.append(device_row)
        print(f"Bulundu: {device_name}") # Ekrana yazdırır
    except Exception as e:
        print(f"Cihaz döngüsünde hata: {e}")

# CSV Kaydetme
# Dosyayı /mnt/data içine kaydediyoruz ki WinSCP ile rahatça alabilesiniz.
save_path = '/mnt/data/devices.csv'

try:
    with open(save_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Model", "Mac", "Firmware", "Site", "LTS", "EOL", "Adopted", "Link"])
        for device_row in device_rows:
            writer.writerow(device_row)
    print("\n" + "="*50)
    print(f"İŞLEM BAŞARILI! Dosya kaydedildi: {save_path}")
    print("Bu dosyayı WinSCP ile '/mnt/data' klasöründen alabilirsiniz.")
    print("="*50)
except Exception as e:
    print(f"Dosya yazma hatası: {e}")
    # Eğer /mnt/data'ya yazamazsa olduğu yere yazmayı dener
    try:
        with open('devices.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(device_rows)
        print("Dosya '/mnt/data' yerine scriptin olduğu klasöre 'devices.csv' olarak kaydedildi.")
    except:
        pass