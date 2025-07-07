#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import re
from getpass import getpass
from time import sleep
import importlib.util
import time
import socket

# =====================
# Global Constants
# =====================

# Official Passbolt URLs
PASSBOLT_INSTALLER_URL = 'https://download.passbolt.com/ce/installer/passbolt-repo-setup.ce.sh'
DOCKER_COMPOSE_URL = 'https://download.passbolt.com/ce/docker/docker-compose-ce.yaml'
DOCKER_COMPOSE_SUM_URL = 'https://github.com/passbolt/passbolt_docker/releases/latest/download/docker-compose-ce-SHA512SUM.txt'

# Downloaded file names
INSTALLER_FILE = '/tmp/passbolt-repo-setup.ce.sh'
DOCKER_COMPOSE_FILE = 'docker-compose-ce.yaml'
DOCKER_COMPOSE_SUM_FILE = 'docker-compose-ce-SHA512SUM.txt'

# Default timeout to wait for database
DB_READY_TIMEOUT = 60

# Database service name in Docker Compose
DB_SERVICE_NAME = 'db'

# Terminal output colors
class bcolors:
    HEADER = '\033[97m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[97m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run_command(command, description, shell=True, capture_output=False):
    """Run a command with error handling."""
    print(f"{bcolors.OKBLUE}▶ {description}...{bcolors.ENDC}")
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=True,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            text=True
        )
        print(f"{bcolors.OKGREEN}✔ Done!{bcolors.ENDC}\n")
        return result
    except subprocess.CalledProcessError as e:
        print(f"{bcolors.FAIL}❌ Error ({e.returncode}): {e.stderr if capture_output else 'Check the logs'}{bcolors.ENDC}")
        sys.exit(1)

def check_root():
    """Check if the script is being run as root/sudo."""
    if os.geteuid() != 0:
        print(f"{bcolors.FAIL}✖ This script must be run as root/sudo.{bcolors.ENDC}")
        sys.exit(1)

def detect_distro():
    """Detect the Linux distribution."""
    try:
        distro_id = None
        # Try /etc/os-release first
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        distro_id = line.strip().split('=')[1].strip('"').lower()
                        # For openSUSE, ID can be 'opensuse-leap' or 'opensuse-tumbleweed'
                        if 'opensuse' in distro_id:
                            distro_id = 'opensuse'
                        break
        # If not found, try /etc/SuSE-release (for older versions)
        if distro_id is None and os.path.exists('/etc/SuSE-release'):
            distro_id = 'opensuse'
        if distro_id in ['debian', 'ubuntu', 'rocky', 'almalinux', 'opensuse']:
            return distro_id
        else:
            print(f"{bcolors.FAIL}✖ Distribution '{distro_id}' not supported.{bcolors.ENDC}")
            sys.exit(1)
    except Exception as e:
        print(f"{bcolors.FAIL}✖ Error detecting distribution: {e}{bcolors.ENDC}")
        sys.exit(1)

def install_dependencies(distro):
    """Install packages specific to each distribution."""
    print(f"{bcolors.OKCYAN}🔧 Installing dependencies for {distro.capitalize()}...{bcolors.ENDC}")
    # Update system
    if distro in ['debian', 'ubuntu']:
        run_command("apt-get update -y", "Updating repositories")
        run_command("apt-get upgrade -y", "Upgrading existing packages")
    elif distro in ['rocky', 'almalinux']:
        run_command("dnf upgrade -y", "Upgrading existing packages")
    elif distro == 'opensuse':
        run_command("zypper refresh", "Refreshing repositories")
        run_command("zypper update -y", "Upgrading existing packages")
    # Install dependencies
    if distro in ['debian', 'ubuntu']:
        run_command("apt-get install -y curl gnupg apt-transport-https", "Installing basic dependencies")
    elif distro in ['rocky', 'almalinux']:
        run_command("dnf install -y epel-release", "Installing EPEL repository")
        run_command("dnf install -y curl", "Installing basic dependencies")
    elif distro == 'opensuse':
        run_command("zypper install -y curl", "Installing basic dependencies")

def install_passbolt(distro):
    """Download and run the official Passbolt installer."""
    print(f"{bcolors.OKCYAN}🚀 Downloading Passbolt CE installer...{bcolors.ENDC}")
    installer_file = f"/tmp/passbolt-repo-setup.ce.sh"
    run_command(
        f"curl -s -L {PASSBOLT_INSTALLER_URL} -o {installer_file}",
        "Downloading official Passbolt installer"
    )
    if not os.path.exists(installer_file) or os.path.getsize(installer_file) < 1000:
        print(f"{bcolors.FAIL}✖ The installer was not downloaded correctly.{bcolors.ENDC}")
        sys.exit(1)
    run_command(f"chmod +x {installer_file}", "Making installer executable")
    run_command(f"bash {installer_file} --accept-license", "Preparing Passbolt installer")
    if distro in ['debian', 'ubuntu']:
        run_command(f"apt install -y passbolt-ce-server", "Installing Passbolt CE server")
    elif distro in ['rocky', 'almalinux']:
        run_command("dnf install -y passbolt-ce-server", "Installing Passbolt CE server")
        run_command("/usr/local/bin/passbolt-configure", "Configuring Passbolt CE server")
    elif distro == 'opensuse':
        run_command("zypper install -y passbolt-ce-server", "Installing Passbolt CE server")
        run_command("/usr/local/bin/passbolt-configure", "Configuring Passbolt CE server")

def post_install_instructions(distro):
    """Show post-installation instructions."""
    print(f"\n{bcolors.OKGREEN}✅ Passbolt installed successfully!{bcolors.ENDC}")

def command_exists(cmd):
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except Exception:
        return False

def install_docker():
    print(f"{bcolors.WARNING}Docker and Docker Compose not found. Installing...{bcolors.ENDC}")
    distro = ""
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release') as f:
                for line in f:
                    if line.startswith('ID='):
                        distro = line.strip().split('=')[1].strip('"').lower()
                        break
    except Exception:
        pass
    if distro in ['rocky', 'almalinux']:
        run_command('dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo', 'Adding official Docker repository')
        run_command('dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin', 'Installing Docker and Docker Compose (plugin)')
        run_command('systemctl enable --now docker', 'Enabling Docker service')
    elif distro in ['debian', 'ubuntu']:
        run_command('apt update', 'Updating repositories')
        run_command('apt install -y docker.io docker-compose', 'Installing Docker and Docker Compose')
        run_command('systemctl enable --now docker', 'Enabling Docker service')
    elif distro == 'opensuse':
        run_command('zypper refresh', 'Refreshing repositories')
        run_command('zypper install -y docker docker-compose', 'Installing Docker and Docker Compose')
        run_command('systemctl enable --now docker', 'Enabling Docker service')
    else:
        print(f"{bcolors.FAIL}Automatic Docker installation not supported for this distribution: {distro}. Please install manually and try again.{bcolors.ENDC}")
        sys.exit(1)
    print(f"{bcolors.OKGREEN}✔ Docker installed!{bcolors.ENDC}")

def install_docker_dependencies():
    docker_ok = command_exists('docker --version')
    compose_ok = command_exists('docker compose version') or command_exists('docker-compose --version')
    if docker_ok and compose_ok:
        return True
    print(f"{bcolors.WARNING}Docker or Docker Compose are not installed.{bcolors.ENDC}")
    choice = input("Do you want to install Docker and Docker Compose now? [y/N]: ").strip().lower()
    if choice == 'y':
        install_docker()
        return command_exists('docker --version') and (command_exists('docker compose version') or command_exists('docker-compose --version'))
    else:
        print(f"{bcolors.FAIL}Docker installation cancelled. Please install Docker manually to use this option.{bcolors.ENDC}")
        return False

def check_and_install_pyyaml():
    try:
        import yaml
    except ImportError:
        print(f"{bcolors.WARNING}The 'pyyaml' module is not installed.{bcolors.ENDC}")
        choice = input("Do you want to install PyYAML now? [y/N]: ").strip().lower()
        if choice == 'y':
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
                print(f"{bcolors.OKGREEN}PyYAML installed successfully!{bcolors.ENDC}")
            except Exception as e:
                print(f"{bcolors.FAIL}Error installing PyYAML: {e}{bcolors.ENDC}")
                sys.exit(1)
        else:
            print(f"{bcolors.FAIL}PyYAML is required to continue. Please install it manually and try again.{bcolors.ENDC}")
            sys.exit(1)

def interactive_edit_docker_compose(compose_file):
    check_and_install_pyyaml()
    import yaml
    with open(compose_file, 'r') as f:
        data = yaml.safe_load(f)
    # Navigate to the environment variables of the passbolt service
    env_list = data['services']['passbolt']['environment']
    env_dict = {}
    for item in env_list:
        if '=' in item:
            k, v = item.split('=', 1)
            env_dict[k] = v
    # Essential variables
    print(f"\nInteractive configuration of essential Passbolt Docker variables:")
    def prompt_env(var, desc, default=None):
        current = env_dict.get(var, default or '')
        if 'PASSWORD' in desc.upper() or 'PASSWORD' in var.upper():
            val = getpass(f"{desc} [{current}]: ").strip()
        else:
            val = input(f"{desc} [{current}]: ").strip()
        return val if val else current
    # Database
    print("\n⚠️  IMPORTANT: For the database host, ALWAYS use 'db' (without quotes), which is the name of the database service in Docker Compose. DO NOT use IP, localhost, or 127.0.0.1!")
    while True:
        db_host = prompt_env('DATASOURCES_DEFAULT_HOST', 'Database host', 'db')
        if db_host.lower() in ['localhost', '127.0.0.1'] or any(c.isdigit() for c in db_host.split('.')):
            print("❗ ERROR: Use only 'db' as the database host for Docker Compose to work!")
        else:
            break
    db_name = prompt_env('DATASOURCES_DEFAULT_DATABASE', 'Database name', 'passboltdb')
    db_user = prompt_env('DATASOURCES_DEFAULT_USERNAME', 'Database user', 'passboltadmin')
    db_pass = prompt_env('DATASOURCES_DEFAULT_PASSWORD', 'Database password', 'passworddb')
    # SMTP and URL
    env_dict['APP_FULL_BASE_URL'] = prompt_env('APP_FULL_BASE_URL', 'Full Passbolt URL (e.g.: https://passbolt.yourdomain.com)')
    env_dict['EMAIL_DEFAULT_FROM'] = prompt_env('EMAIL_DEFAULT_FROM', 'Sender email (e.g.: passbolt@yourdomain.com)')
    env_dict['EMAIL_TRANSPORT_DEFAULT_HOST'] = prompt_env('EMAIL_TRANSPORT_DEFAULT_HOST', 'SMTP Host (e.g.: smtp.yourdomain.com)')
    env_dict['EMAIL_TRANSPORT_DEFAULT_PORT'] = prompt_env('EMAIL_TRANSPORT_DEFAULT_PORT', 'SMTP Port (e.g.: 587)', '587')
    env_dict['EMAIL_TRANSPORT_DEFAULT_USERNAME'] = prompt_env('EMAIL_TRANSPORT_DEFAULT_USERNAME', 'SMTP User (leave blank if not using authentication)')
    env_dict['EMAIL_TRANSPORT_DEFAULT_PASSWORD'] = prompt_env('EMAIL_TRANSPORT_DEFAULT_PASSWORD', 'SMTP Password (leave blank if not using authentication)')
    env_dict['EMAIL_TRANSPORT_DEFAULT_TLS'] = prompt_env('EMAIL_TRANSPORT_DEFAULT_TLS', 'SMTP TLS (true/false, leave blank for default)')
    # Update database in passbolt
    env_dict['DATASOURCES_DEFAULT_HOST'] = db_host
    env_dict['DATASOURCES_DEFAULT_USERNAME'] = db_user
    env_dict['DATASOURCES_DEFAULT_PASSWORD'] = db_pass
    env_dict['DATASOURCES_DEFAULT_DATABASE'] = db_name
    # Update env list
    new_env_list = [f"{k}={v}" for k, v in env_dict.items() if v]
    data['services']['passbolt']['environment'] = new_env_list
    # Update database in db service
    db_env = data['services']['db']['environment']
    db_env_dict = {}
    for item in db_env:
        if '=' in item:
            k, v = item.split('=', 1)
            db_env_dict[k] = v
    db_env_dict['MYSQL_DATABASE'] = db_name
    db_env_dict['MYSQL_USER'] = db_user
    db_env_dict['MYSQL_PASSWORD'] = db_pass
    db_env_dict['MYSQL_ROOT_PASSWORD'] = prompt_env('MYSQL_ROOT_PASSWORD', 'MySQL root password', 'passboltdb')
    new_db_env_list = [f"{k}={v}" for k, v in db_env_dict.items() if v]
    data['services']['db']['environment'] = new_db_env_list
    with open(compose_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    print(f"\nFile {compose_file} updated successfully!\n")

def get_docker_compose_cmd():
    if shutil.which('docker-compose'):
        return 'docker-compose'
    else:
        return 'docker compose'

def create_passbolt_admin(compose_cmd, compose_file):
    print(f"\nAutomatic creation of Passbolt admin user:")
    email = input("Admin email: ").strip()
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    cmd = (
        f'{compose_cmd} -f {compose_file} exec passbolt su -m -c '
        f'"/usr/share/php/passbolt/bin/cake passbolt register_user '
        f'-u {email} -f {first_name} -l {last_name} -r admin" -s /bin/sh www-data'
    )
    print("\nWaiting for the Passbolt container to initialize (10s)...")
    time.sleep(10)
    print(f"\nRunning command to create the admin user...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"\nCommand output:\n{result.stdout}")
        import re
        match = re.search(r'https?://\S+', result.stdout)
        if match:
            print(f"\nAccess the link below to finish the admin registration in your browser:\n{match.group(0)}\n")
        else:
            print(f"\nCould not find the registration link in the output. Please check manually above.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating admin user:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

def wait_for_database_ready(host, port=3306, timeout=60):
    print(f"⏳ Waiting for the database to be ready...")
    import time
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"✅ Database is ready!")
                return True
        except Exception:
            time.sleep(2)
    print(f"❌ Timeout waiting for the database. Check the db container logs.")
    return False

def check_and_install_curl():
    import shutil
    if shutil.which('curl'):
        return True
    print(f"{bcolors.WARNING}The 'curl' command is not installed.{bcolors.ENDC}")
    choice = input("Do you want to install curl now? [y/N]: ").strip().lower()
    if choice == 'y':
        distro = ''
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release') as f:
                for line in f:
                    if line.startswith('ID='):
                        distro = line.strip().split('=')[1].strip('"').lower()
                        break
        if distro in ['debian', 'ubuntu']:
            run_command('apt update', 'Updating repositories')
            run_command('apt install -y curl', 'Installing curl')
        elif distro in ['rocky', 'almalinux']:
            run_command('dnf install -y curl', 'Installing curl')
        elif distro == 'opensuse':
            run_command('zypper install -y curl', 'Installing curl')
        else:
            print(f"{bcolors.FAIL}Automatic curl installation not supported for this distribution: {distro}. Please install manually and try again.{bcolors.ENDC}")
            sys.exit(1)
        return shutil.which('curl') is not None
    else:
        print(f"{bcolors.FAIL}Curl is required to continue. Please install it manually and try again.{bcolors.ENDC}")
        sys.exit(1)

def install_passbolt_docker():
    check_and_install_curl()
    if not install_docker_dependencies():
        return
    print(f"{bcolors.OKCYAN}🚀 Installing Passbolt via Docker (official flow)...{bcolors.ENDC}")
    run_command(f"curl -LO {DOCKER_COMPOSE_URL}", "Downloading official docker-compose-ce.yaml")
    run_command(f"curl -LO {DOCKER_COMPOSE_SUM_URL}", "Downloading SHA512SUM verification file")
    run_command(f"sha512sum -c {DOCKER_COMPOSE_SUM_FILE}", "Verifying integrity of docker-compose-ce.yaml file")
    interactive_edit_docker_compose(DOCKER_COMPOSE_FILE)
    compose_cmd = get_docker_compose_cmd()
    run_command(f"{compose_cmd} -f {DOCKER_COMPOSE_FILE} up -d", "Starting Docker containers")
    check_and_install_pyyaml()
    import yaml
    with open(DOCKER_COMPOSE_FILE, 'r') as f:
        data = yaml.safe_load(f)
    db_env = data['services']['db']['environment']
    db_host = 'db'
    db_port = 3306
    for item in db_env:
        if item.startswith('MYSQL_ROOT_PASSWORD='):
            continue
        if item.startswith('MYSQL_DATABASE='):
            continue
        if item.startswith('MYSQL_USER='):
            continue
        if item.startswith('MYSQL_PASSWORD='):
            continue
        if item.startswith('MYSQL_HOST='):
            db_host = item.split('=',1)[1]
        if item.startswith('MYSQL_PORT='):
            db_port = int(item.split('=',1)[1])
    wait_for_database_ready(db_host, db_port)
    print(f"{bcolors.OKGREEN}✔ Passbolt via Docker started!{bcolors.ENDC}")
    create_passbolt_admin(compose_cmd, DOCKER_COMPOSE_FILE)

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

def interactive_menu():
    while True:
        clear_console()
        print(f"{bcolors.HEADER}╔════════════════════════════════════════════════╗{bcolors.ENDC}")
        print(f"{bcolors.HEADER}║{bcolors.BOLD}         🔐 PASSBOLT SETUP MANAGER 🔐           {bcolors.HEADER}║{bcolors.ENDC}")
        print(f"{bcolors.HEADER}╚════════════════════════════════════════════════╝{bcolors.ENDC}")
        print("       ____                  __          ____")
        print("      / __ \\____ ___________/ /_  ____  / / /_")
        print("     / /_/ / __ `/ ___/ ___/ __ \/ __ \/ / __/")
        print("    / ____/ /_/ /__  /__  / /_/ / /_/ / / /_")
        print("   /_/    \\__,_/____/____/_.___/\____/_/\__/")
        print("    Open source password manager for teams")
        print("        🔗 https://www.passbolt.com")
        print("\n───────────────────────────────────────────────\n")
        print(" [1] 🐳  Install Passbolt via Docker")
        print(" [2] 📦  Install Passbolt via Packages")
        print(" [0] 🚪  Exit\n")
        print("───────────────────────────────────────────────\n")
        choice = input("👉 Choose an option: ")
        if choice == '1':
            print("\n🐳 Starting Docker installation...")
            install_passbolt_docker()
            input("\n🔙 Press Enter to return to the menu...")
        elif choice == '2':
            print("\n📦 Starting package installation...")
            check_root()
            try:
                distro = detect_distro()
                print(f"{bcolors.OKGREEN}✔ Distribution detected: {distro.capitalize()}{bcolors.ENDC}")
                install_dependencies(distro)
                install_passbolt(distro)
                post_install_instructions(distro)
            except KeyboardInterrupt:
                print(f"\n{bcolors.WARNING}⚠️ Installation cancelled by user.{bcolors.ENDC}")
                sys.exit(1)
            except Exception as e:
                print(f"{bcolors.FAIL}✖️ Unexpected error: {str(e)}{bcolors.ENDC}")
                sys.exit(1)
            input("\n🔙 Press Enter to return to the menu...")
        elif choice == '0':
            print(f"{bcolors.OKBLUE}👋 Exiting... See you soon!{bcolors.ENDC}")
            break
        else:
            print(f"{bcolors.WARNING}❗ Invalid option!{bcolors.ENDC}")
            sleep(1)

if __name__ == "__main__":
    clear_console()
    interactive_menu()