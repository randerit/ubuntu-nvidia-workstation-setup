# 7. Specific Setup for Analytics Workstations

> [Index](../../README_en.md#index) · [Previous: 6. Specific Setup for Compression Workstations](06-compression-workstations.md) · [Next: 8. Managing the Graphical Interface](08-graphical-interface.md) · [Español](../07-estaciones-analitica.md)

> **Note:** This section installs tools for analytics/machine learning, assuming Ubuntu 24.04.1 LTS with CUDA installed. Install only what's necessary.

## Configuring MongoDB (Database and User)

### Step 1: Access Console
```bash
mongosh
```

### Step 2: Create Database and User
Replace placeholders:
```javascript
use DATABASE_NAME
db.createUser({
  user: "USERNAME",
  pwd: "PASSWORD",
  roles: [
    {
      role: "readWrite",
      db: "DATABASE_NAME"
    }
  ]
})
```

Exit with `exit`.

### Step 3: Enable Authorization
Edit config:
```bash
sudo nano /etc/mongod.conf
```

Add under `security:`:
```yaml
security:
  authorization: enabled
```

Save and restart:
```bash
sudo systemctl restart mongod
```

**Verification:**
```bash
mongosh -u USERNAME -p PASSWORD --authenticationDatabase DATABASE_NAME
# Should connect
```

## Installing Node-RED

### Step 1: Run Installation Script
> **Security warning:** Review the script contents before running it. You can download it first with `wget` and inspect it.

```bash
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```

### Step 2: Enable and Start Service
```bash
sudo systemctl enable nodered
sudo systemctl start nodered
```

**Verification:**
```bash
sudo systemctl status nodered
# Dashboard at http://localhost:1880
```

## Installing Python and Machine Learning Libraries

### Step 1: Install Python and Pip
```bash
sudo apt install -y python3 python3-pip
```

### Step 2: Upgrade Pip
```bash
pip3 install --upgrade pip --break-system-packages
```

> If this step dies with `Cannot uninstall pip ... RECORD file not found`, it is the same case Step 3
> explains: apply the recipe there using `pip` as the conflicting package.

### Step 3: Install Libraries
> **Note:** `--break-system-packages` installs system-wide, so any Python script can import these
> without activating a virtualenv.

```bash
pip3 install --break-system-packages pandas numpy scikit-learn paho-mqtt ultralytics
```

> **If it dies with `ERROR: Cannot uninstall typing_extensions 4.10.0, RECORD file not found`:** this
> is expected on Ubuntu 24.04, not your mistake. `ultralytics` pulls `torch`, which requires a newer
> `typing_extensions` than the distro ships. `apt` put that package in
> `/usr/lib/python3/dist-packages` **without a `RECORD` file** -- dpkg does not write one -- so pip
> cannot tell which files to delete in order to replace it and **aborts the whole install**: not one
> of the five libraries ends up installed, even though the log lists dozens of downloads.
>
> Install your own copy of the conflicting package and retry:
>
> ```bash
> pip3 install --break-system-packages --ignore-installed typing_extensions
> pip3 install --break-system-packages pandas numpy scikit-learn paho-mqtt ultralytics
> ```
>
> `--ignore-installed` does **not** delete apt's file: dpkg stays intact and system packages that
> depend on it keep working. It installs the new copy in `/usr/local/lib/python3.12/dist-packages`,
> which comes first in `sys.path` and wins at import time. That is why
> `sudo apt remove python3-typing-extensions` is **not** the way out: it takes system packages with
> it.
>
> If the conflicting package has a different name, change it in the first line. Since 2.8.9,
> the analytics-profile installer (`workstation-analytics` in 2.x, today
> `workstation-dependencies --perfil analitica`) performs this retry on its own.

**Verification:**
```bash
python3 -c "import pandas, numpy, sklearn; print('Libraries OK')"
# Should print without errors
```

## Configuring Ports for Analytics Workstations (Optional)
If using firewall, open ports:

| Application | Ports | Protocol | Command |
|------------|---------|-----------|---------|
| MongoDB | 27017 | TCP | `sudo ufw allow 27017/tcp` |
| Node-RED | 1880 | TCP | `sudo ufw allow 1880/tcp` |

**Verification:**
```bash
sudo ufw status
```

## General Tips
- For your own projects, use virtual environments: `python3 -m venv ml_env && source ml_env/bin/activate`. The Step 3 libraries are installed system-wide on purpose, so any script sees them without activating anything.
- Upgrade libraries: `pip3 install --break-system-packages --upgrade <lib>`.

## Troubleshooting
- **MongoDB auth failing:** Check config in `/etc/mongod.conf`.
- **`mongosh` cannot connect because `mongod` will not start:** If the journal shows `MongoDB cannot start: Linux kernel versions 6.19 and newer...`, it is the HWE 7.0 kernel, not the auth config. Apply [Section 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-fails-to-start-on-hwe-kernel-70).
- **Node-RED not starting:** Check logs: `sudo journalctl -u nodered`.
- **Pip installing slow:** Use mirror: `pip3 install --break-system-packages --index-url https://pypi.org/simple <lib>`.
- **`Cannot uninstall <package>, RECORD file not found`:** the package was installed by `apt`, not pip, and it aborts the entire transaction. See the callout in Step 3.

> **Additional Resources:**
> * [Node-RED Docs](https://nodered.org/docs/)
> * [MongoDB Docs](https://www.mongodb.com/docs/)
> * [Pandas Docs](https://pandas.pydata.org/docs/)

---

> [Index](../../README_en.md#index) · [Previous: 6. Specific Setup for Compression Workstations](06-compression-workstations.md) · [Next: 8. Managing the Graphical Interface](08-graphical-interface.md) · [Español](../07-estaciones-analitica.md)
