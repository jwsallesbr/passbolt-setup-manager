# 🔐 Passbolt Setup Manager

![Passbolt](https://www.passbolt.com/img/logo/logo.svg)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Debian](https://img.shields.io/badge/Debian-A81D33?style=for-the-badge&logo=debian&logoColor=white)
![Rocky Linux](https://img.shields.io/badge/Rocky%20Linux-10B981?style=for-the-badge&logo=rockylinux&logoColor=white)
![AlmaLinux](https://img.shields.io/badge/AlmaLinux-262626?style=for-the-badge&logo=almalinux&logoColor=white)
![openSUSE](https://img.shields.io/badge/openSUSE-73BA25?style=for-the-badge&logo=openSUSE&logoColor=white)

---

## 🎯 Overview

**Passbolt Setup Manager** is an interactive tool that automates the installation and configuration of Passbolt, an open-source password manager for teams, on various Linux distributions. It is ideal for administrators seeking convenience, security, and speed.

- **Compatible with multiple Linux distributions:** Supports Debian, Ubuntu, Rocky Linux, AlmaLinux, and openSUSE.
- **Docker installation:** Automatically downloads, validates, and configures the Docker environment for Passbolt.
- **Package installation:** Follows the official repository installation method, with automatic distribution detection.
- **Interactive and secure configuration:** User-friendly prompts for essential data entry, avoiding common mistakes.
- **Automatic dependency installation:** Ensures all prerequisites are present before starting the installation.

---

## 📋 Supported Distributions and Official References

Check the official Passbolt documentation for each installation method and supported distribution:

| Distribution      | Tested Version     | Official Documentation |
|-------------------|--------------------|----------------------|
| 🐳 Docker         | All                | [Docker](https://www.passbolt.com/docs/hosting/install/ce/docker/) |
| ☢️ Ubuntu         | 24.04 LTS          | [Ubuntu](https://www.passbolt.com/docs/hosting/install/ce/ubuntu/) |
| 🐧 Debian         | 12                 | [Debian](https://www.passbolt.com/docs/hosting/install/ce/debian/) |
| ❇️ Rocky Linux    | 9                  | [RockyLinux](https://www.passbolt.com/docs/hosting/install/ce/rockylinux/) |
| ♻️ AlmaLinux      | 9                  | [AlmaLinux](https://www.passbolt.com/docs/hosting/install/ce/almalinux/) |
| 🦎 openSUSE       | Leap/Tumbleweed    | [openSUSE](https://www.passbolt.com/docs/hosting/install/ce/opensuse/) |

---

## 🚀 Getting Started

Follow these steps to quickly install Passbolt on your Linux server.

### Prerequisites
- Linux server with one of the supported distributions
- **Root access**
- **Internet connection** (for downloading packages)
- **Python 3.6+** (pre-installed on most distributions)

## ⚡️ Quick Installation

Clone the repository or download the script:
```bash
git clone https://github.com/jwsallesbr/passbolt-setup-manager.git
cd passbolt-setup-manager
```

Make the script executable:
```bash
chmod +x passbolt_setup_manager.py
```

Run the script as root/sudo:
```bash
sudo python3 passbolt_setup_manager.py
```

## ⚙️ When running the script, you will see a menu like this:

```
╔════════════════════════════════════════════════╗
║         🔐 PASSBOLT SETUP MANAGER 🔐          ║
╚════════════════════════════════════════════════╝
       ____                  __          ____
      / __ \____ ___________/ /_  ____  / / /_
     / /_/ / __ `/ ___/ ___/ __ \/ __ \/ / __/
    / ____/ /_/ /__  /__  / /_/ / /_/ / / /_
   /_/    \__,_/____/____/_.___/\____/_/\__/
    Open source password manager for teams
        🔗 https://www.passbolt.com
___________________________________________________

[1] 🐳  Install Passbolt via Docker
[2] 📦  Install Passbolt via Packages
[0] 🚪  Exit
👉 Choose an option:
```

- **🐳 Install via Docker:**
  - Downloads the official `docker-compose-ce.yaml` file and validates its integrity.
  - Installs Docker/Docker Compose automatically if needed.
  - Interactive configuration of essential variables (DB, SMTP, URL, etc).

- **📦 Install via Packages:**
  - Downloads the official `passbolt-repo-setup.ce.sh` file and validates its integrity.
  - Installs dependencies and Passbolt via official repositories.
  - Interactive configuration (DB, NGINX, etc).

- **🚪 Exit:**
  - Exits the script.

---

## 🔒 Security Recommendations and Best Practices

- **🔑📦 Keep your private key in a safe place:**  
  The private key is essential to restore administrative access in case of password loss.

- **🔒🌐 Enable SSL (highly recommended):**  
  Using HTTPS is crucial to protect credentials and sensitive data transmitted by Passbolt.  
  Install Certbot and set up a free SSL certificate:
  ```bash
  # For Debian/Ubuntu:
  sudo apt install certbot python3-certbot-nginx
  ```

  ```bash
  # For Rocky/AlmaLinux:
  sudo dnf install certbot python3-certbot-nginx
  ```

  ```bash
  # For openSUSE:
  sudo zypper install certbot python3-certbot-nginx
  ```
  
  ```bash
  sudo certbot --nginx -d your-domain
  ```

  [🏋️‍♂️ Learn more about Certbot](https://certbot.eff.org/)

- **🔐📱 Enable two-factor authentication (2FA) via TOTP:**  
  Increase account security by requiring a second authentication factor.  
  Go to Passbolt settings and follow the instructions to enable 2FA for all users.  
  [How to enable 2FA (TOTP) in Passbolt](https://www.passbolt.com/docs/admin/authentication/mfa/totp/)

---

<div align="center">

## 🔑📲 Download the official Passbolt app:

Scan the QR code or click the link below to download the official Passbolt app for your device:

| <img src="docs/qr-play-store.png" width="120"/> | <img src="docs/qr-app-store.png" width="120"/> |
|:-----------------------------------------------:|:---------------------------------------------:|
| [Download for Android](https://play.google.com/store/apps/details?id=com.passbolt.mobile.android)  | [Download for iOS](https://apps.apple.com/app/id1569629432) |

🔒 Securely access your passwords on your mobile device.

</div>

---