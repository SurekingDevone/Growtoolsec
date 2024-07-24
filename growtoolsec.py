import subprocess
import sys
import ctypes
import os

# Define menus for different languages
menus = {
    'en': {
        'scan_file': '1. Scan file for backdoors',
        'disable_shutdown': '2. Disable shutdown access',
        'enable_shutdown': '3. Enable shutdown access',
        'monitor_rdp': '4. Monitor RDP activity',
        'restrict_rdp': '5. Restrict RDP access by time',
        'exit': '6. Exit',
        'input_choice': 'Enter your choice: ',
        'input_file_name': 'Enter the file name to scan: ',
        'input_start_time': 'Enter start time (HH:MM): ',
        'input_end_time': 'Enter end time (HH:MM): ',
        'final_message': 'Exiting program. Goodbye!',
        'error_invalid_option': 'Invalid option, please try again.',
        'repeat_prompt': 'Do you want to perform another action? (yes/no): '
    },
    'id': {
        'scan_file': '1. Pindai file untuk backdoor',
        'disable_shutdown': '2. Nonaktifkan akses shutdown',
        'enable_shutdown': '3. Aktifkan akses shutdown',
        'monitor_rdp': '4. Pantau aktivitas RDP',
        'restrict_rdp': '5. Batasi akses RDP berdasarkan waktu',
        'exit': '6. Keluar',
        'input_choice': 'Masukkan pilihan Anda: ',
        'input_file_name': 'Masukkan nama file untuk dipindai: ',
        'input_start_time': 'Masukkan waktu mulai (HH:MM): ',
        'input_end_time': 'Masukkan waktu akhir (HH:MM): ',
        'final_message': 'Keluar dari program. Selamat tinggal!',
        'error_invalid_option': 'Opsi tidak valid, silakan coba lagi.',
        'repeat_prompt': 'Apakah Anda ingin melakukan tindakan lain? (iya/tidak): '
    }
}


# Hardcoded credentials for login (for demonstration purposes)
VALID_USERNAME = 'admin'
VALID_PASSWORD = 'growtoolsec'

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    script = sys.argv[0]
    params = ' '.join(sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, f'{script} {params}', None, 1)

def run_command(command):
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.stderr}")

def run_powershell_script(script):
    try:
        result = subprocess.run(
            ["powershell", "-Command", script],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running PowerShell script: {e.stderr}")

def monitor_rdp_activity(language):
    if not is_admin():
        print("This script needs to be run as administrator." if language == 'en' else "Skrip ini perlu dijalankan sebagai administrator.")
        run_as_admin()
        sys.exit(0)

    print("Monitoring RDP activity..." if language == 'en' else "Memantau aktivitas RDP...")
    command = ["powershell", "-Command", "$startTime = (Get-Date).AddMinutes(-30); Get-EventLog -LogName Security -InstanceId 4624 -After $startTime | Where-Object {$_.ReplacementStrings[5] -eq '10'} | Format-Table -AutoSize"]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        else:
            print("No recent RDP activity found." if language == 'en' else "Tidak ada aktivitas RDP terbaru yang ditemukan.")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.stderr}")

def disable_shutdown_services(language):
    if not is_admin():
        print("This script needs to be run as administrator." if language == 'en' else "Skrip ini perlu dijalankan sebagai administrator.")
        run_as_admin()
        sys.exit(0)

    print("Disabling shutdown access on Windows..." if language == 'en' else "Menonaktifkan akses shutdown di Windows...")
    powershell_script = """
    # Set registry key to disable shutdown
    $regPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force
    }
    Set-ItemProperty -Path $regPath -Name "DisableShutdown" -Value 1
    """
    try:
        run_powershell_script(powershell_script)
        print("Shutdown access has been successfully disabled." if language == 'en' else "Akses shutdown telah berhasil dinonaktifkan.")
    except Exception as e:
        print(f"Failed to disable shutdown access: {e}")

def enable_shutdown_services(language):
    if not is_admin():
        print("This script needs to be run as administrator." if language == 'en' else "Skrip ini perlu dijalankan sebagai administrator.")
        run_as_admin()
        sys.exit(0)

    print("Enabling shutdown access on Windows..." if language == 'en' else "Mengaktifkan akses shutdown di Windows...")
    powershell_script = """
    # Remove registry key to re-enable shutdown
    $regPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
    Remove-ItemProperty -Path $regPath -Name "DisableShutdown" -ErrorAction SilentlyContinue
    """
    try:
        run_powershell_script(powershell_script)
        print("Shutdown access has been successfully enabled." if language == 'en' else "Akses shutdown telah berhasil diaktifkan.")
    except Exception as e:
        print(f"Failed to enable shutdown access: {e}")

def restrict_rdp_by_time(start_time, end_time, language):
    if not is_admin():
        print("This script needs to be run as administrator." if language == 'en' else "Skrip ini perlu dijalankan sebagai administrator.")
        run_as_admin()
        sys.exit(0)

    print(f"Restricting RDP access to between {start_time} and {end_time}..." if language == 'en' else f"Batasi akses RDP antara {start_time} dan {end_time}...")
    powershell_script = f"""
    $startTime = [datetime]::Parse("{start_time}")
    $endTime = [datetime]::Parse("{end_time}")

    # Define the rule name
    $ruleName = "Restrict RDP Access Time"

    # Add the time-based rule
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow -Enabled True -Program "System" -Schedule @("{startTime.ToString("HH:mm:ss")}-{endTime.ToString("HH:mm:ss")}")
    """
    try:
        run_powershell_script(powershell_script)
        print("RDP access time restriction has been successfully set." if language == 'en' else "Pembatasan waktu akses RDP telah berhasil diatur.")
    except Exception as e:
        print(f"Failed to restrict RDP access time: {e}")

def contains_backdoor_patterns(line):
    import re
    patterns = [
        r"\b(system|exec|passthru|popen|fopen|eval)\s*\(",
        r"\b(os\.system|subprocess\.run|subprocess\.call)\s*\(",
        r"\bimport\s+subprocess\b",
        r"\bimport\s+os\b",
        r"\bexec\(\s*('|\"|\'\'|\"\"\")(.*?)(\'|\"|\'\'|\"\"\")\)",
        r"\bgetattr\(\s*\w+,\s*(\".*?\"|'.*?')\s*\)",
    ]
    return any(re.search(pattern, line) for pattern in patterns)

def scan_file_for_backdoors(filename, language):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            in_multiline_comment = False
            for line_number, line in enumerate(file, start=1):
                stripped_line = line.strip()
                
                if not in_multiline_comment and stripped_line.startswith("/*"):
                    in_multiline_comment = True
                if in_multiline_comment and stripped_line.endswith("*/"):
                    in_multiline_comment = False
                    continue
                if in_multiline_comment:
                    continue
                
                if contains_backdoor_patterns(stripped_line):
                    print(f"Potential backdoor found at line {line_number}: {line.strip()}" if language == 'en' else f"Potensi backdoor ditemukan di baris {line_number}: {line.strip()}")
                
                if stripped_line.startswith("//"):
                    continue

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found." if language == 'en' else f"Error: File '{filename}' tidak ditemukan.")
    except IOError:
        print(f"Error: Unable to read file '{filename}'." if language == 'en' else f"Error: Tidak dapat membaca file '{filename}'.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def login(language):
    print("Login Required")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        print("Login successful!" if language == 'en' else "Login berhasil!")
        return True
    else:
        print("Invalid username or password." if language == 'en' else "Username atau password salah.")
        return False

def display_menu(language):
    menu = menus[language]
    print("Welcome to GrowToolSec")
    print("Join growtool for more information : https://t.me/GrowToolServer")
    print("VERSION 1.1")
    print("\nMenu:")
    print(menu['scan_file'])
    print(menu['disable_shutdown'])
    print(menu['enable_shutdown'])
    print(menu['monitor_rdp'])
    print(menu['restrict_rdp'])
    print(menu['exit'])

def main():
    # Choose language
    print("Welcome to GrowTool Security program")
    language = input("Choose language en = english / id = indonesia (en/id): ").strip().lower()
    if language not in ['en', 'id']:
        print("Invalid language choice. Defaulting to English.")
        language = 'en'

    # Login to the script
    if not login(language):
        print("Exiting program.")
        return
    
    while True:
        os.system('cls')
        display_menu(language)
        choice = input(menus[language]['input_choice']).strip()
        
        if choice == '1':
            filename = input(menus[language]['input_file_name']).strip()
            if not filename:
                print("Error: File not found / not input" if language == 'en' else "Error: File tidak ditemukan / tidak di-input")
                continue
            
            scan_file_for_backdoors(filename, language)
        
        elif choice == '2':
            disable_shutdown_services(language)
        
        elif choice == '3':
            enable_shutdown_services(language)
        
        elif choice == '4':
            monitor_rdp_activity(language)
        
        elif choice == '5':
            start_time = input(menus[language]['input_start_time']).strip()
            end_time = input(menus[language]['input_end_time']).strip()
            if not start_time or not end_time:
                print("Error: Time not provided." if language == 'en' else "Error: Waktu tidak diberikan.")
                continue
            
            restrict_rdp_by_time(start_time, end_time, language)
        
        elif choice == '6':
            print(menus[language]['final_message'])
            break
        
        else:
            print(menus[language]['error_invalid_option'])
           
        try:
            continue_choice = input(menus[language]['repeat_prompt']).strip().lower()
            if continue_choice != 'iya' and continue_choice != 'yes':
                print(menus[language]['final_message'])
                break
        except KeyboardInterrupt:
            print("\nProcess interrupted by user.")
            break

if __name__ == "__main__":
    if not is_admin():
        print("This script requires administrator privileges. Please run as administrator.")
        run_as_admin()
    else:
        main()
