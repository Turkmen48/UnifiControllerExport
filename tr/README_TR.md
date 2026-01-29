# Unifi Controller Cihaz Dışa Aktarıcı (Device Export)

Bu araç, UniFi OS (UDM Pro, UDM SE, Cloud Key Gen2 vb.) üzerinde çalışan yerel MongoDB veritabanına bağlanır, yönetilen tüm cihazların listesini çeker ve bunları CSV formatında dışa aktarır.

UniFi OS sistemlerinde veritabanı izole bir ağ alanında (network namespace) çalıştığı için, bu script standart Python komutuyla değil, özel bir `nsenter` komutuyla çalıştırılmalıdır.

## 📋 Ön Gereksinimler

Scriptin çalışabilmesi için **PyMongo 3.x** sürümü zorunludur. UniFi'nin kullandığı eski MongoDB sürümü (v3.6), yeni PyMongo sürümleriyle (4.x+) uyumlu değildir.

SSH ile bağlandıktan sonra ortamı hazırlamak için şu komutları uygulayın:

```bash
# 1. Pip paket yöneticisini kurun (eğer yoksa)
apt-get update && apt-get install python3-pip -y

# 2. Eğer varsa uyumsuz sürümü kaldırın
pip3 uninstall pymongo -y

# 3. Uyumlu sürümü (3.12.3) yükleyin
pip3 install pymongo==3.12.3

```

---

## 📥 Kurulum

Scripti sunucunuza indirmek için bir klasör oluşturun ve dosyayı çekin:

```bash
# Klasörü oluştur ve içine gir
mkdir -p /home/unifiExporter
cd /home/unifiExporter

# Scripti indir
wget [https://raw.githubusercontent.com/Turkmen48/UnifiControllerExport/refs/heads/main/tr/main.py](https://raw.githubusercontent.com/Turkmen48/UnifiControllerExport/refs/heads/main/tr/main.py)

```

---

## 🚀 Çalıştırma (Kullanım)

Veritabanı dışarıya kapalı olduğu için scripti UniFi servisinin "içine" (ağ alanına) enjekte ederek çalıştırmanız gerekir.

Aşağıdaki komutu kopyalayıp terminale yapıştırın:

```bash
sudo nsenter -t $(pgrep -f ace.jar | head -n 1) -n python3 /home/unifiExporter/main.py

```

### Komutun Açıklaması

* `pgrep -f ace.jar`: Çalışan UniFi uygulamasının işlem ID'sini bulur.
* `nsenter ... -n`: Python'u, UniFi uygulamasının gördüğü ağ penceresinden (namespace) çalıştırır. Böylece script `localhost:27117` adresindeki veritabanına erişebilir.

---

## 📄 Çıktı ve Dosyayı Alma

Script başarıyla çalıştığında, scriptin bulunduğu dizine **`devices.csv`** adında bir dosya oluşturur.

Dosyayı bilgisayarınıza almak için:

1. **WinSCP** veya **FileZilla** kullanarak `/home/unifiExporter/devices.csv` yolundan indirebilirsiniz.
2. Veya dosya içeriğini terminale yazdırıp kopyalayabilirsiniz:
```bash
cat devices.csv

```



---

## ⚠️ Sık Karşılaşılan Hatalar

| Hata Mesajı | Çözüm |
| --- | --- |
| **Server reports wire version 6...** | PyMongo sürümünüz çok yeni. "Ön Gereksinimler" adımındaki kaldırma ve yükleme komutlarını uygulayın. |
| **Connection refused** | Scripti `nsenter` olmadan direkt `python3 main.py` ile çalıştırmayı denediniz. Lütfen yukarıdaki `sudo nsenter...` komutunu kullanın. |
| **No module named 'pymongo'** | Kütüphane eksik. `pip3 install pymongo==3.12.3` komutunu çalıştırın. |