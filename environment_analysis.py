# environment_analysis.py
import platform
import psutil
import json
from PyQt6.QtCore import QThread, pyqtSignal

class EnvironmentAnalysisThread(QThread):
    progress_update = pyqtSignal(int)
    result_ready = pyqtSignal(str)

    def run(self):
        result = {}
        
        # Análisis del sistema operativo
        self.progress_update.emit(10)
        result['os'] = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
        
        # Análisis de CPU
        self.progress_update.emit(30)
        cpu_freq = psutil.cpu_freq()
        result['cpu'] = {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "max_frequency": f"{cpu_freq.max:.2f}Mhz",
            "min_frequency": f"{cpu_freq.min:.2f}Mhz",
            "current_frequency": f"{cpu_freq.current:.2f}Mhz",
            "usage_per_core": [f"{percentage:.1f}%" for percentage in psutil.cpu_percent(percpu=True, interval=1)]
        }
        
        # Análisis de memoria
        self.progress_update.emit(50)
        mem = psutil.virtual_memory()
        result['memory'] = {
            "total": f"{mem.total / (1024**3):.2f} GB",
            "available": f"{mem.available / (1024**3):.2f} GB",
            "used": f"{mem.used / (1024**3):.2f} GB",
            "percentage": f"{mem.percent}%"
        }
        
        # Análisis de disco
        self.progress_update.emit(70)
        disk = psutil.disk_usage('/')
        result['disk'] = {
            "total": f"{disk.total / (1024**3):.2f} GB",
            "used": f"{disk.used / (1024**3):.2f} GB",
            "free": f"{disk.free / (1024**3):.2f} GB",
            "percentage": f"{disk.percent}%"
        }
        
        # Análisis de red
        self.progress_update.emit(90)
        net_io = psutil.net_io_counters()
        result['network'] = {
            "bytes_sent": f"{net_io.bytes_sent / (1024**2):.2f} MB",
            "bytes_recv": f"{net_io.bytes_recv / (1024**2):.2f} MB",
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
        
        self.progress_update.emit(100)
        
        # Evaluación de optimización
        cpu_optimal = result['cpu']['total_cores'] >= 4 and float(result['cpu']['max_frequency'][:-3]) > 2000
        memory_optimal = float(result['memory']['total'][:-3]) >= 8
        disk_optimal = float(result['disk']['total'][:-3]) >= 100 and float(result['disk']['percentage'][:-1]) < 80
        
        optimization_score = (cpu_optimal + memory_optimal + disk_optimal) / 3 * 100
        result['optimization'] = f"{optimization_score:.1f}%"
        
        self.result_ready.emit(json.dumps(result, indent=2))
