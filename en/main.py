import sys
import csv

# -------------------------------------------------------------
# ATTENTION: This script requires pymongo 3.12.3 to function correctly.
# Command: pip3 install pymongo==3.12.3
# If pymongo is already installed and you face errors, uninstall
# the current version and install the specified one: pip3 uninstall pymongo
# -------------------------------------------------------------

def check_pymongo_version():
    try:
        import pymongo
        if not pymongo.__version__.startswith("3."):
            print("ERROR: Incompatible PyMongo version. 3.x is required.")
            sys.exit(1)
    except ImportError:
        print("ERROR: PyMongo is not installed.")
        sys.exit(1)

check_pymongo_version()

from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27117)
db = client['ace']
devices_col = db['device']
sites_col = db['site']
settings_col = db['setting']

hostname = "unknown"
try:
    for setting in settings_col.find():
        hostname = setting.get("hostname", "unknown")
        break
except Exception:
    pass

sites_dict = {}
try:
    for site in sites_col.find():
        site_id = str(site["_id"])
        sites_dict[site_id] = {
            "desc": site.get("desc", "No Description"),
            "name": site.get("name", "default")
        }
except Exception:
    pass

device_rows = []
for device in devices_col.find():
    try:
        device_name = device.get("name", "")
        if not device_name:
            device_name = device.get("mac", "Unknown")

        site_id = device.get("site_id")
        site_info = sites_dict.get(site_id, {"desc": "Unknown", "name": "default"})
        
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
        print(device_row)
    except Exception:
        pass

try:
    with open('devices.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Model", "Mac", "Firmware", "Site", "LTS", "EOL", "Adopted", "Link"])
        writer.writerows(device_rows)
    print("File saved: devices.csv")
except Exception as e:
    print(f"Error: {e}")