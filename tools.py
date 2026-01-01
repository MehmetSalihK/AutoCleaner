import psutil
import winreg
import os
import shutil
import platform
import shutil
import platform
import subprocess
import ctypes
from logs import logger

class ProcessManager:
    @staticmethod
    def get_processes(limit=50, sort_by='memory'):
        """Get list of running processes sorted by usage."""
        procs = []
        try:
            for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
                try:
                    with p.oneshot():
                        # Calculate memory in MB
                        mem = p.memory_info().rss / (1024 * 1024)
                        
                        procs.append({
                            'pid': p.pid,
                            'name': p.name(),
                            'cpu': p.cpu_percent(), # Note: First call after interval=None is 0, need 2nd call or interval
                            'memory': mem
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            logger.error(f"Error fetching processes: {e}")

        # Sort
        if sort_by == 'memory':
            procs.sort(key=lambda x: x['memory'], reverse=True)
        elif sort_by == 'cpu':
            procs.sort(key=lambda x: x['cpu'], reverse=True)
            
        return procs[:limit]

    @staticmethod
    def kill_process(pid, tree=False):
        """Terminate a process by PID. Option to kill tree."""
        try:
            p = psutil.Process(pid)
            if tree:
                # Murder the entire family
                children = p.children(recursive=True)
                for child in children:
                    child.kill()
                p.kill()
                return True, f"Arborescence processus {pid} terminée."
            else:
                p.terminate()
                return True, f"Processus {pid} terminé."
        except psutil.NoSuchProcess:
            return False, "Processus introuvable."
        except psutil.AccessDenied:
            return False, "Accès refusé. Essayez en mode Admin."
        except Exception as e:
            return False, str(e)

class StartupManager:
    @staticmethod
    def get_startup_items():
        """Get list of startup programs from Registry and Startup Folder."""
        items = []
        
        # 1. Registry - HKCU
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    items.append({
                        'name': name,
                        'path': value,
                        'source': 'Registry (User)',
                        'enabled': True # Registry items are generally enabled if present
                    })
                    i += 1
                except WindowsError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            logger.error(f"Error reading HKCU startup: {e}")

        # 2. Registry - HKLM (Needs Admin)
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    items.append({
                        'name': name,
                        'path': value,
                        'source': 'Registry (System)',
                        'enabled': True
                    })
                    i += 1
                except WindowsError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass # Likely access denied if not admin

        # 3. Startup Folder (User)
        startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        if os.path.exists(startup_path):
            for file in os.listdir(startup_path):
                items.append({
                    'name': file,
                    'path': os.path.join(startup_path, file),
                    'source': 'Startup Folder',
                    'enabled': True
                })

        return items

    @staticmethod
    def delete_item(item):
        """Remove a startup item."""
        try:
            if item['source'] == 'Registry (User)':
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
                winreg.DeleteValue(key, item['name'])
                winreg.CloseKey(key)
                return True, "Item retiré du registre (Utilisateur)."
                
            elif item['source'] == 'Registry (System)':
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(key, item['name'])
                    winreg.CloseKey(key)
                    return True, "Item retiré du registre (Système)."
                except OSError:
                    return False, "Accès refusé. Mode Admin requis."
                    
            elif item['source'] == 'Startup Folder':
                if os.path.exists(item['path']):
                    os.remove(item['path'])
                    return True, "Raccourci de démarrage supprimé."
                    
            return False, "Source inconnue ou introuvable."
        except Exception as e:
            return False, str(e)

class AppManager:
    @staticmethod
    def get_installed_apps():
        """Get list of installed applications from Registry."""
        apps = []
        roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for root, subkey_path in roots:
            try:
                key = winreg.OpenKey(root, subkey_path, 0, winreg.KEY_READ)
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, f"{subkey_path}\\{subkey_name}")
                        
                        try:
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            
                            # Get Version
                            try:
                                version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                            except OSError:
                                version = "Unknown"
                                
                            # Get Size
                            try:
                                size_kb = winreg.QueryValueEx(subkey, "EstimatedSize")[0]
                                if size_kb > 1024 * 1024:
                                    size_str = f"{size_kb / (1024*1024):.1f} GB"
                                elif size_kb > 1024:
                                    size_str = f"{size_kb / 1024:.1f} MB"
                                else:
                                    size_str = f"{size_kb} KB"
                            except OSError:
                                size_str = "N/A"

                            # Get Uninstall String
                            try:
                                uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0]
                            except OSError:
                                uninstall_string = None

                            apps.append({
                                'name': name,
                                'version': version,
                                'size': size_str,
                                'uninstall_string': uninstall_string
                            })
                        except OSError:
                            pass # No DisplayName, valuable hidden key or system component
                        
                        winreg.CloseKey(subkey)
                    except OSError:
                        pass
                winreg.CloseKey(key)
            except OSError:
                continue
                
        # Sort by Name
        apps.sort(key=lambda x: x['name'].lower())
        return apps

    @staticmethod
    def uninstall_app(app):
        """Launch the uninstaller for the app."""
        if not app.get('uninstall_string'):
            return False, "Aucune commande de désinstallation."
            
        try:
            cmd = app['uninstall_string']
            subprocess.Popen(cmd, shell=True)
            return True, "Désinstallateur lancé."
        except Exception as e:
            return False, f"Erreur: {e}"

        return apps


class SystemInfo:
    @staticmethod
    def get_info():
        """Get detailed system information."""
        info = {}
        
        # OS
        info['os'] = f"{platform.system()} {platform.release()} ({platform.architecture()[0]})"
        info['version'] = platform.version()
        info['machine'] = platform.machine()
        
        # CPU
        try:
            info['cpu'] = platform.processor()
            info['cpu_cores'] = f"{psutil.cpu_count(logical=False)} Cores / {psutil.cpu_count(logical=True)} Threads"
        except:
            info['cpu'] = "Unknown"
            
        # RAM
        try:
            mem = psutil.virtual_memory()
            info['ram_total'] = f"{mem.total / (1024**3):.1f} GB"
            info['ram_used'] = f"{mem.percent}%"
        except:
            info['ram_total'] = "Unknown"
            
        # GPU (Basic check via wmic if available, else generic)
        try:
            cmd = "wmic path win32_VideoController get name"
            proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if proc.returncode == 0:
                lines = proc.stdout.strip().split('\n')
                if len(lines) > 1:
                    info['gpu'] = lines[1].strip()
                else:
                    info['gpu'] = "Generic Video Controller"
            else:
                info['gpu'] = "Unknown"
        except:
            info['gpu'] = "Unknown"
            
        return info

class SystemOptimizer:
    @staticmethod
    def optimize_ram():
        """Attempts to reduce memory usage of running processes."""
        try:
            # 1. Clear current process memory first
            pid = os.getpid()
            handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
            ctypes.windll.psapi.EmptyWorkingSet(handle)
            ctypes.windll.kernel32.CloseHandle(handle)
            
            # 2. Try to clear other processes (Best effort)
            freed_count = 0
            for p in psutil.process_iter():
                try:
                    h = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, p.pid)
                    if h:
                        ctypes.windll.psapi.EmptyWorkingSet(h)
                        ctypes.windll.kernel32.CloseHandle(h)
                        freed_count += 1
                except:
                    pass
            
            return True, f"RAM Optimisée ! (Processus traités: {freed_count})"
        except Exception as e:
            return False, f"Erreur: {str(e)}"

class DiskAnalyzer:
    @staticmethod
    def scan_large_files(limit_mb=100):
        """Scan user directories for files larger than limit_mb."""
        large_files = []
        limit_bytes = limit_mb * 1024 * 1024
        
        user_dirs = [
            os.path.join(os.path.expanduser("~"), "Downloads"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Videos"),
            os.path.join(os.path.expanduser("~"), "Desktop")
        ]
        
        for root_dir in user_dirs:
            if not os.path.exists(root_dir):
                continue
                
            for dirpath, _, filenames in os.walk(root_dir):
                for f in filenames:
                    try:
                        filepath = os.path.join(dirpath, f)
                        size = os.path.getsize(filepath)
                        if size > limit_bytes:
                            large_files.append({
                                'name': f,
                                'path': filepath,
                                'size': size,
                                'size_fmt': f"{size / (1024*1024):.1f} MB"
                            })
                    except:
                        pass
                        
        large_files.sort(key=lambda x: x['size'], reverse=True)
        return large_files[:50] # Top 50
