# system_monitor_i2c.py
import smbus2
import time
import psutil
import socket
import subprocess
from datetime import datetime

class SSD1306_I2C:
    def __init__(self, width=128, height=64, address=0x3C, bus=1):
        self.width = width
        self.height = height
        self.address = address
        self.bus = smbus2.SMBus(bus)
        self.buffer = [0] * (width * height // 8)
        self.init_display()
    
    def write_cmd(self, cmd):
        """Komut yaz"""
        try:
            self.bus.write_byte_data(self.address, 0x00, cmd)
        except:
            pass
    
    def write_data(self, data):
        """Veri yaz"""
        try:
            self.bus.write_byte_data(self.address, 0x40, data)
        except:
            pass
    
    def init_display(self):
        """SSD1306 başlatma"""
        commands = [
            0xAE, 0x20, 0x00, 0xB0, 0xC8, 0x00, 0x10, 0x40, 0x81, 0xFF,
            0xA1, 0xA6, 0xA8, 0x3F, 0xD3, 0x00, 0xD5, 0xF0, 0xD9, 0x22,
            0xDA, 0x12, 0xDB, 0x20, 0x8D, 0x14, 0xAF
        ]
        for cmd in commands:
            self.write_cmd(cmd)
        self.clear()
        self.update()
    
    def clear(self):
        """Ekranı temizle"""
        self.buffer = [0] * (self.width * self.height // 8)
    
    def set_pixel(self, x, y, color=1):
        """Pixel ayarla"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if color:
                self.buffer[x + (y // 8) * self.width] |= (1 << (y % 8))
            else:
                self.buffer[x + (y // 8) * self.width] &= ~(1 << (y % 8))
    
    def draw_text(self, text, x, y, size=1):
        """Basit font ile text çiz"""
        font = {
            '0': [0x3E, 0x51, 0x49, 0x45, 0x3E], '1': [0x00, 0x42, 0x7F, 0x40, 0x00],
            '2': [0x42, 0x61, 0x51, 0x49, 0x46], '3': [0x21, 0x41, 0x45, 0x4B, 0x31],
            '4': [0x18, 0x14, 0x12, 0x7F, 0x10], '5': [0x27, 0x45, 0x45, 0x45, 0x39],
            '6': [0x3C, 0x4A, 0x49, 0x49, 0x30], '7': [0x01, 0x71, 0x09, 0x05, 0x03],
            '8': [0x36, 0x49, 0x49, 0x49, 0x36], '9': [0x06, 0x49, 0x49, 0x29, 0x1E],
            'A': [0x7C, 0x12, 0x11, 0x12, 0x7C], 'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
            'C': [0x3E, 0x41, 0x41, 0x41, 0x22], 'D': [0x7F, 0x41, 0x41, 0x22, 0x1C],
            'E': [0x7F, 0x49, 0x49, 0x49, 0x41], 'F': [0x7F, 0x09, 0x09, 0x09, 0x01],
            'G': [0x3E, 0x41, 0x49, 0x49, 0x7A], 'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
            'I': [0x00, 0x41, 0x7F, 0x41, 0x00], 'J': [0x20, 0x40, 0x41, 0x3F, 0x01],
            'K': [0x7F, 0x08, 0x14, 0x22, 0x41], 'L': [0x7F, 0x40, 0x40, 0x40, 0x40],
            'M': [0x7F, 0x02, 0x0C, 0x02, 0x7F], 'N': [0x7F, 0x04, 0x08, 0x10, 0x7F],
            'O': [0x3E, 0x41, 0x41, 0x41, 0x3E], 'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
            'Q': [0x3E, 0x41, 0x51, 0x21, 0x5E], 'R': [0x7F, 0x09, 0x19, 0x29, 0x46],
            'S': [0x46, 0x49, 0x49, 0x49, 0x31], 'T': [0x01, 0x01, 0x7F, 0x01, 0x01],
            'U': [0x3F, 0x40, 0x40, 0x40, 0x3F], 'V': [0x1F, 0x20, 0x40, 0x20, 0x1F],
            'W': [0x3F, 0x40, 0x38, 0x40, 0x3F], 'X': [0x63, 0x14, 0x08, 0x14, 0x63],
            'Y': [0x07, 0x08, 0x70, 0x08, 0x07], 'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00], ':': [0x00, 0x36, 0x36, 0x00, 0x00],
            '.': [0x00, 0x60, 0x60, 0x00, 0x00], '%': [0x23, 0x13, 0x08, 0x64, 0x62],
            '°': [0x06, 0x09, 0x09, 0x06, 0x00], 'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
            'M': [0x7F, 0x02, 0x0C, 0x02, 0x7F], 'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
            '/': [0x60, 0x10, 0x08, 0x04, 0x03], '↑': [0x08, 0x1C, 0x2A, 0x08, 0x08],
            '↓': [0x08, 0x08, 0x2A, 0x1C, 0x08], '→': [0x08, 0x04, 0x7E, 0x04, 0x08],
            '←': [0x08, 0x10, 0x7E, 0x10, 0x08]
        }
        
        for char in text.upper():
            if char in font:
                char_data = font[char]
                for col in range(5):
                    col_data = char_data[col]
                    for row in range(7):
                        if col_data & (1 << row):
                            self.set_pixel(x, y + row)
                    x += 1
                x += 1  # Karakter arası boşluk
    
    def draw_progress_bar(self, x, y, width, height, percentage):
        """Progress bar çiz"""
        # Arkaplan
        for i in range(width):
            for j in range(height):
                self.set_pixel(x + i, y + j)
        
        # Doluluk
        fill_width = int(width * percentage / 100)
        for i in range(fill_width):
            for j in range(height):
                self.set_pixel(x + i, y + j, 0)  # Beyaz doluluk
    
    def update(self):
        """Ekranı güncelle"""
        for page in range(8):
            self.write_cmd(0xB0 + page)
            self.write_cmd(0x00)
            self.write_cmd(0x10)
            
            start = page * 128
            end = start + 128
            for i in range(start, end):
                self.write_data(self.buffer[i])

class SystemMonitor:
    def __init__(self):
        self.display = SSD1306_I2C()
        self.cpu_prev = [0, 0, 0, 0]
        
    def get_cpu_usage(self):
        """CPU kullanımı"""
        return psutil.cpu_percent(interval=0.5)
    
    def get_cpu_temp(self):
        """CPU sıcaklığı"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return float(f.read().strip()) / 1000.0
        except:
            return 0.0
    
    def get_ram_usage(self):
        """RAM kullanımı"""
        return psutil.virtual_memory().percent
    
    def get_disk_usage(self):
        """Disk kullanımı"""
        return psutil.disk_usage('/').percent
    
    def get_network_usage(self):
        """Network kullanımı"""
        net_io = psutil.net_io_counters()
        upload = net_io.bytes_sent / 1024  # KB
        download = net_io.bytes_recv / 1024
        return upload, download
    
    def get_uptime(self):
        """Sistem uptime"""
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours:02d}:{minutes:02d}"
    
    def get_ip_address(self):
        """IP adresi"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "No IP"
    
    def draw_dashboard(self):
        """Ana dashboard'u çiz"""
        self.display.clear()
        
        # Sistem bilgilerini al
        cpu = self.get_cpu_usage()
        temp = self.get_cpu_temp()
        ram = self.get_ram_usage()
        disk = self.get_disk_usage()
        uptime = self.get_uptime()
        ip = self.get_ip_address()
        
        # Başlık
        self.display.draw_text("RPI MONITOR", 5, 0)
        
        # CPU Bilgisi
        self.display.draw_text(f"CPU:{cpu:5.1f}%", 0, 10)
        self.display.draw_progress_bar(45, 10, 40, 6, cpu)
        
        # Sıcaklık
        self.display.draw_text(f"TEMP:{temp:4.1f}C", 0, 20)
        
        # RAM
        self.display.draw_text(f"RAM:{ram:5.1f}%", 0, 30)
        self.display.draw_progress_bar(45, 30, 40, 6, ram)
        
        # Disk
        self.display.draw_text(f"DSK:{disk:5.1f}%", 0, 40)
        self.display.draw_progress_bar(45, 40, 40, 6, disk)
        
        # Alt bilgi
        self.display.draw_text(f"UP:{uptime}", 0, 52)
        self.display.draw_text(f"IP:{ip.split('.')[-1]}", 70, 52)
        
        self.display.update()
    
    def draw_detailed_view(self, view_type="cpu"):
        """Detaylı görünüm"""
        self.display.clear()
        
        if view_type == "cpu":
            cpu = self.get_cpu_usage()
            temp = self.get_cpu_temp()
            load = psutil.getloadavg()
            
            self.display.draw_text("CPU DETAIL", 5, 0)
            self.display.draw_text(f"Usage: {cpu:5.1f}%", 0, 12)
            self.display.draw_text(f"Temp:  {temp:4.1f}C", 0, 22)
            self.display.draw_text(f"Load:  {load[0]:.2f}", 0, 32)
            self.display.draw_text(f"Cores: {psutil.cpu_count()}", 0, 42)
            
        elif view_type == "memory":
            ram = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            self.display.draw_text("MEMORY INFO", 5, 0)
            self.display.draw_text(f"RAM: {ram.percent:5.1f}%", 0, 12)
            self.display.draw_text(f"Used: {ram.used//1024//1024:3d}M", 0, 22)
            self.display.draw_text(f"Free: {ram.free//1024//1024:3d}M", 0, 32)
            self.display.draw_text(f"Swap: {swap.percent:5.1f}%", 0, 42)
            
        elif view_type == "network":
            upload, download = self.get_network_usage()
            net_io = psutil.net_io_counters()
            
            self.display.draw_text("NETWORK", 5, 0)
            self.display.draw_text(f"UP: {upload:7.1f}K", 0, 12)
            self.display.draw_text(f"DOWN: {download:5.1f}K", 0, 22)
            self.display.draw_text(f"Pkts: {net_io.packets_sent}", 0, 32)
            self.display.draw_text(f"IP: {self.get_ip_address()}", 0, 42)
        
        self.display.update()
    
    def run(self):
        """Ana döngü"""
        print("I2C Sistem Monitörü Başlatıldı")
        print("GPIO2 (SDA) - Pin 3")
        print("GPIO3 (SCL) - Pin 5")
        print("Çıkmak için Ctrl+C")
        
        view_mode = "dashboard"
        view_counter = 0
        
        try:
            while True:
                if view_mode == "dashboard":
                    self.draw_dashboard()
                elif view_mode == "cpu_detail":
                    self.draw_detailed_view("cpu")
                elif view_mode == "memory_detail":
                    self.draw_detailed_view("memory")
                elif view_mode == "network_detail":
                    self.draw_detailed_view("network")
                
                # Her 10 iterasyonda bir view değiştir
                view_counter += 1
                if view_counter >= 10:
                    if view_mode == "dashboard":
                        view_mode = "cpu_detail"
                    elif view_mode == "cpu_detail":
                        view_mode = "memory_detail"
                    elif view_mode == "memory_detail":
                        view_mode = "network_detail"
                    else:
                        view_mode = "dashboard"
                    view_counter = 0
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\nMonitör durduruldu")
            self.display.clear()
            self.display.update()

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run()
