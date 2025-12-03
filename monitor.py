import psutil
import shutil
import time
import subprocess
from utils import format_file_size

class SystemMonitor:
    def __init__(self):
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()

    def get_gpu_info(self):
        """Get NVIDIA GPU stats silently."""
        try:
            # Run nvidia-smi silently
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            cmd = ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                startupinfo=startupinfo,
                creationflags=0x08000000 # CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                output = result.stdout.strip().split(',')
                if len(output) >= 2:
                    return float(output[0]), float(output[1])
        except:
            pass
        return 0, 0

    def get_system_info(self):
        """Get comprehensive system usage statistics."""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # Memory
        memory = psutil.virtual_memory()
        
        # Disk
        try:
            total, used, free = shutil.disk_usage("C:\\")
            disk_percent = round((used / total) * 100, 1)
        except:
            disk_percent = 0
            
        # GPU
        gpu_percent, gpu_temp = self.get_gpu_info()

        # Network
        net_io = psutil.net_io_counters()
        current_time = time.time()
        time_delta = current_time - self.last_time
        
        if time_delta > 0:
            upload_speed = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_delta
            download_speed = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_delta
        else:
            upload_speed = 0
            download_speed = 0
            
        self.last_net_io = net_io
        self.last_time = current_time

        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': format_file_size(memory.available),
            'memory_total': format_file_size(memory.total),
            'disk_usage': disk_percent,
            'gpu_usage': round(gpu_percent, 1),
            'gpu_temp': gpu_temp,
            'upload_speed': format_file_size(upload_speed) + "/s",
            'download_speed': format_file_size(download_speed) + "/s"
        }

# Global instance
monitor = SystemMonitor()

def get_system_info():
    return monitor.get_system_info()

def get_disk_usage():
    """Get detailed disk usage."""
    try:
        total, used, free = shutil.disk_usage("C:\\")
        return {
            'total': format_file_size(total),
            'used': format_file_size(used),
            'free': format_file_size(free),
            'percent': round((used / total) * 100, 1)
        }
    except:
        return None
