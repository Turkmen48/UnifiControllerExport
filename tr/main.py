import csv
from pymongo import MongoClient

# -------------------------------------------------------------
# DİKKAT: Bu kodun çalışması için sistemde pymongo 3.12.3 yüklü olmalıdır.
# Komut: pip3 install pymongo==3.12.3
# Eğer pymongo yüklüyse ve hata alıyorsanız, mevcut pymongo sürümünü kaldırıp
# belirtilen sürümü yükleyin: pip3 uninstall pymongo
# -------------------------------------------------------------

# Bağlantı Ayarları
try:
    client = MongoClient('127.0.0.1', 27117, serverSelectionTimeoutMS=5000)
    # Bağlantıyı test et
    client.server_info()
except Exception as e:
    print(f"Veritabanı Bağlantı Hatası: {e}")
    print("Lütfen pymongo sürümünün 3.12.3 olduğundan emin olun.")
    exit(1)

# Veritabanı Tanımları
db = client['ace']
devices_col = db['device']
sites_col = db['site']
settings_col = db['setting']

# Hostname'i bul (Controller IP/Domain)
hostname = "unknown"
try:
    # Genellikle tek bir ayar dökümanı olur, ilkini alıyoruz
    setting = settings_col.find_one()
    if setting and "hostname" in setting:
        hostname = setting["hostname"]
except Exception as e:
    print(f"Hostname alınamadı: {e}")

# Site bilgilerini hafızaya al (ID -> İsim eşleşmesi için)
sites_dict = {}
print("Siteler taranıyor...")
for site in sites_col.find():
    site_id = str(site["_id"])
    sites_dict[site_id] = {
        "desc": site.get("desc", "No Description"),
        "name": site.get("name", "default")
    }

print(f"Bulunan Siteler: {sites_dict}")

# Cihazları topla
device_rows = []
print("Cihazlar taranıyor...")

for device in devices_col.find():
    try:
        # Verileri güvenli şekilde al (.get kullanarak hata riskini azaltıyoruz)
        name = device.get("name", "")
        if not name:
            name = device.get("mac", "Unknown Device") # İsmi yoksa MAC adresini yaz

        model = device.get("model", "Unknown")
        mac = device.get("mac", "")
        version = device.get("version", "")
        
        # Site ID üzerinden site bilgilerini çek
        site_id = device.get("site_id", "")
        site_info = sites_dict.get(site_id, {"desc": "Unknown Site", "name": "default"})
        
        site_desc = site_info["desc"]
        site_name = site_info["name"]

        is_lts = device.get("model_in_lts", False)
        is_eol = device.get("model_in_eol", False)
        is_adopted = device.get("adopted", False)

        # Yönetim URL'ini oluştur
        link = f"https://{hostname}:8443/manage/{site_name}/devices"

        device_row = [name, model, mac, version, site_desc, is_lts, is_eol, is_adopted, link]
        device_rows.append(device_row)
        
    except Exception as e:
        print(f"Cihaz işlenirken hata: {e}")

# CSV dosyasına yaz
csv_filename = 'devices.csv'
try:
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Model", "Mac", "Firmware", "Site", "LTS", "EOL", "Adopted", "Link"])
        writer.writerows(device_rows)
    print(f"\nBaşarılı! {len(device_rows)} cihaz '{csv_filename}' dosyasına kaydedildi.")
except IOError as e:
    print(f"Dosya yazma hatası: {e}")