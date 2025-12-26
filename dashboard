# system_data_collector.py
import psutil
import platform
import socket
import uuid
import re
import subprocess
import json
import time
from datetime import datetime
import os
import sys

class SystemDataCollector:
    """Tüm sistem verilerini toplayan sınıf"""
    
    def __init__(self):
        self.data = {}
        self.previous_net_io = psutil.net_io_counters()
        self.start_time = time.time()
        
    def collect_all_data(self):
        """Tüm verileri topla"""
        self.data = {
            'timestamp': self._get_timestamp(),
            'uptime': self._get_uptime(),
            'system_info': self._get_system_info(),
            'cpu_data': self._get_cpu_data(),
            'memory_data': self._get_memory_data(),
            'disk_data': self._get_disk_data(),
            'network_data': self._get_network_data(),
            'process_data': self._get_process_data(),
            'sensor_data': self._get_sensor_data(),
            'usb_data': self._get_usb_data(),
            'gpio_data': self._get_gpio_data(),
            'docker_data': self._get_docker_data(),
            'performance_score': self._calculate_performance_score(),
            'warnings': self._check_warnings()
        }
        return self.data
    
    def _get_timestamp(self):
        """Zaman damgası"""
        return {
            'iso': datetime.now().isoformat(),
            'unix': time.time(),
            'readable': datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        }
    
    def _get_uptime(self):
        """Sistem çalışma süresi"""
        uptime_seconds = time.time() - self.start_time
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        return {
            'seconds': uptime_seconds,
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'formatted': f"{int(days)}g {int(hours)}s {int(minutes)}d"
        }
    
    def _get_system_info(self):
        """Sistem bilgileri"""
        return {
            'system': platform.system(),
            'node_name': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'hostname': socket.gethostname(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'mac_address': ':'.join(re.findall('..', '%012x' % uuid.getnode())),
            'python_version': platform.python_version(),
            'os_name': os.name,
            'cpu_count': {
                'physical': psutil.cpu_count(logical=False),
                'logical': psutil.cpu_count(logical=True)
            }
        }
    
    def _get_cpu_data(self):
        """CPU verileri"""
        cpu_percent = psutil.cpu_percent(interval=0.5, percpu=True)
        
        try:
            cpu_freq = psutil.cpu_freq()
            freq_current = cpu_freq.current if cpu_freq else 0
            freq_max = cpu_freq.max if cpu_freq else 0
        except:
            freq_current = 0
            freq_max = 0
        
        cpu_stats = psutil.cpu_stats()
        
        return {
            'usage_percent': {
                'total': psutil.cpu_percent(interval=0.1),
                'per_core': cpu_percent,
                'average': sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0
            },
            'frequency': {
                'current_mhz': freq_current,
               
