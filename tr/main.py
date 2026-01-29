import csv
from pymongo import MongoClient

# -------------------------------------------------------------
# DİKKAT: Bu kodun çalışması için sistemde pymongo 3.12.3 yüklü olmalıdır.
# Komut: pip3 install pymongo==3.12.3
# Eğer pymongo yüklüyse ve hata alıyorsanız, mevcut pymongo sürümünü kaldırıp
# belirtilen sürümü yükleyin: pip3 uninstall pymongo
# -------------------------------------------------------------

# Bağlantı Ayarları
# Script Unifi OS Container içinde çalışıyorsa '127.0.0.1' kullanılır.
# Eğer dışarıdan bağlanıyorsanız buraya Unifi IP adresini yazın.
client = MongoClient('127.0.0.1', 27117)

# Veritabanı Tanımları
db = client['ace']
devices_col = db['device']
sites_col = db['site']
settings_col = db['setting']

# 1. Hostname Bilgisini Çekme
hostname = "unknown"
try:
    # Ayarlardan hostname'i bulmaya çalış, yoksa hata vermeden geç
    for setting in settings_col.find():
        hostname = setting.get("hostname", "unknown")
        break
except Exception as e:
    print(f"Uyarı: Hostname alınamadı ({e})")

# 2. Site Bilgilerini Hafızaya Alma (ID -> İsim eşleşmesi için)
sites_dict = {}
print("Siteler taranıyor...")
try:
    for site in sites_col.find():
        site_id = str(site["_id"])
        # .get kullanarak veri yoksa varsayılan değer atıyoruz
        sites_dict[site_id] = {
            "desc": site.get("desc", "No Description"), 
            "name": site.get("name", "default")
        }
    print(f"Bulunan Siteler: {sites_dict}")
except Exception as e:
    print(f"Hata: Siteler okunurken sorun oluştu: {e}")

# 3. Cihazları Listeleme ve Verileri Hazırlama
device_rows = []
print("Cihazlar taranıyor...")

for device in devices_col.find():
    try:
        # Cihaz ismini güvenli şekilde al
        device_name = device.get("name", "")
        if not device_name:
            device_name = device.get("mac", "Unknown Device") # İsim yoksa MAC adresini kullan

        # Site bilgisini eşleştir
        site_id = device.get("site_id", "")
        site_info = sites_dict.get(site_id, {"desc": "Unknown Site", "name": "default"})
        
        # Link oluşturma
        manage_link = f"https://{hostname}:8443/manage/{site_info['name']}/devices"

        # Satır verisini oluştur
        device_row = [
            device_name, 
            device.get("model", ""), 
            device.get("mac", ""), 
            device.get("version", ""), 
            site_info["desc"], 
            device.get("model_in_lts", False), 
            device.get("model_in_eol", False), 
            device.get("adopted", False), 
            manage_link
        ]
        
        device_rows.append(device_row)
        print(device_row) # Ekrana da yazdıralım

    except Exception as e:
        print(f"Hata: Bir cihaz işlenirken sorun oluştu: {e}")

# 4. CSV Dosyasına Yazma
csv_filename = 'devices.csv'
try:
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Başlık satırı
        writer.writerow(["Name", "Model", "Mac", "Firmware", "Site", "LTS", "EOL", "Adopted", "Link"])
        # Veri satırları
        writer.writerows(device_rows)
    print(f"\nBaşarılı! {len(device_rows)} cihaz '{csv_filename}' dosyasına kaydedildi.")
except IOError as e:
    print(f"Kritik Hata: Dosya yazılamadı: {e}")