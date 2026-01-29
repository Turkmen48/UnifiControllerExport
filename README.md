# Unifi Controller Device Exporter

This tool connects to the local MongoDB database running on **UniFi OS** (UDM Pro, UDM SE, Cloud Key Gen2, etc.), retrieves a list of all managed devices, and exports them to a CSV format.

On UniFi OS systems, the database runs within an isolated network namespace. Therefore, this script must be executed using a special `nsenter` command rather than the standard Python command.

## 📋 Prerequisites

**PyMongo 3.x** is strictly required for this script to function. The older MongoDB version (v3.6) used by UniFi is incompatible with newer PyMongo versions (4.x+).

After connecting via SSH, run the following commands to prepare the environment:

```bash
# 1. Install pip package manager (if not present)
apt-get update && apt-get install python3-pip -y

# 2. Uninstall incompatible version if it exists
pip3 uninstall pymongo -y

# 3. Install the compatible version (3.12.3)
pip3 install pymongo==3.12.3

```

---

## 📥 Installation

Create a directory on your server and download the script using the commands below:

```bash
# Create directory and enter it
mkdir -p /home/unifiExporter
cd /home/unifiExporter

# Download the script
wget https://raw.githubusercontent.com/Turkmen48/UnifiControllerExport/refs/heads/main/en/main.py

```

---

## 🚀 Usage (Execution)

Since the database is isolated from the host network, you must inject the script into the UniFi service's network namespace to run it.

Copy and paste the following command into your terminal:

```bash
sudo nsenter -t $(pgrep -f ace.jar | head -n 1) -n python3 /home/unifiExporter/main.py

```

### Command Breakdown

* `pgrep -f ace.jar`: Finds the Process ID (PID) of the running UniFi (Java) application.
* `nsenter ... -n`: Runs Python from within the network namespace of the UniFi application. This allows the script to access the database at `localhost:27117`.

---

## 📄 Output & Retrieving the File

Upon successful execution, the script will create a file named **`devices.csv`** in the same directory where the script is located.

To retrieve the file to your computer:

1. Use **WinSCP** or **FileZilla** to download it from `/home/unifiExporter/devices.csv`.
2. Or print the content to the terminal and copy it:
```bash
cat devices.csv

```



---

## ⚠️ Troubleshooting

| Error Message | Solution |
| --- | --- |
| **Server reports wire version 6...** | Your PyMongo version is too new. Follow the uninstall/install commands in the "Prerequisites" section. |
| **Connection refused** | You tried to run the script without `nsenter` (e.g., `python3 main.py`). Please use the `sudo nsenter...` command provided above. |
| **No module named 'pymongo'** | The library is missing. Run `pip3 install pymongo==3.12.3`. |
