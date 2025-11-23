import spidev
import RPi.GPIO as GPIO
import time
import psutil
import socket
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.clock import Clock
from datetime import datetime

# Sistem fonksiyonları - class dışında tanımlandı
def get_ram_usage():
    """RAM kullanımı"""
    return psutil.virtual_memory().percent

def get_cpu_usage():
    """CPU kullanımı"""
    return psutil.cpu_percent(interval=0.5)
    
def get_cpu_temp():
    """CPU sıcaklığı"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            return float(f.read().strip()) / 1000.0
    except:
        return 0.0

def get_ip_address():
    """IP adresi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No IP"

cimport spidev
import RPi.GPIO as GPIO
import time

class Display:
    def __init__(self):
        # SPI Ayarları
        self.spi = spidev.SpiDev()
        self.spi_bus = 0
        self.spi_device = 0
        self.spi_speed = 32000000  # 32 MHz
        
        # STANDART GPIO Pin Tanımlamaları
        self.RST_PIN = 25    # Pin 22 - Reset
        self.DC_PIN = 24     # Pin 18 - Data/Command (LCD_RS)  
        self.CS_PIN = 8      # Pin 24 - LCD Chip Select (LCD_CS)
        self.BL_PIN = 18     # Pin 12 - Backlight (NC yerine kullan)
        
        # Dokunmatik ekran pinleri
        self.T_CS_PIN = 7    # Pin 26 - Touch Chip Select
        self.T_IRQ_PIN = 17  # Pin 11 - Touch Interrupt
        
        # Ekran Özellikleri
        self.WIDTH = 480
        self.HEIGHT = 320
        self.COLOR_DEPTH = 16  # 65,536 renk
        
        self.setup_gpio()
        self.setup_spi()
    
    def setup_gpio(self):
        """GPIO pinlerini ayarla"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # LCD Pinleri
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.BL_PIN, GPIO.OUT)
        
        # Dokunmatik Pinleri
        GPIO.setup(self.T_CS_PIN, GPIO.OUT)
        GPIO.setup(self.T_IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Başlangıç durumu
        GPIO.output(self.CS_PIN, GPIO.HIGH)
        GPIO.output(self.T_CS_PIN, GPIO.HIGH)
        GPIO.output(self.BL_PIN, GPIO.HIGH)  # Backlight aç
    
    def setup_spi(self):
        """SPI bağlantısını kur"""
        try:
            self.spi.open(self.spi_bus, self.spi_device)
            self.spi.max_speed_hz = self.spi_speed
            self.spi.mode = 0
            self.spi.bits_per_word = 8
            print("SPI bağlantısı başarılı")
        except Exception as e:
            print(f"SPI hatası: {e}")
    
    def write_command(self, cmd):
        """Komut yaz"""
        GPIO.output(self.DC_PIN, GPIO.LOW)   # Command mode
        GPIO.output(self.CS_PIN, GPIO.LOW)   # CS aktif
        self.spi.writebytes([cmd])
        GPIO.output(self.CS_PIN, GPIO.HIGH)  # CS pasif
    
    def write_data(self, data):
        """Veri yaz"""
        GPIO.output(self.DC_PIN, GPIO.HIGH)  # Data mode
        GPIO.output(self.CS_PIN, GPIO.LOW)   # CS aktif
        self.spi.writebytes([data])
        GPIO.output(self.CS_PIN, GPIO.HIGH)  # CS pasif
    
    def write_data_16bit(self, data):
        """16-bit renk verisi yaz"""
        GPIO.output(self.DC_PIN, GPIO.HIGH)  # Data mode
        GPIO.output(self.CS_PIN, GPIO.LOW)   # CS aktif
        
        # 16-bit renk (RGB565) - 2 byte
        high_byte = (data >> 8) & 0xFF
        low_byte = data & 0xFF
        self.spi.writebytes([high_byte, low_byte])
        
        GPIO.output(self.CS_PIN, GPIO.HIGH)  # CS pasif
    
    def reset_display(self):
        """Ekranı resetle"""
        GPIO.output(self.RST_PIN, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.1)
    
    def init_display(self):
        """TFT ekranı başlat"""
        print("480x320 TFT Ekran Başlatılıyor...")
        
        self.reset_display()
        
        # ILI9486 Başlatma Sequence
        init_commands = [
            (0xE0, [0x00, 0x03, 0x09, 0x08, 0x16, 0x0A, 0x3F, 0x78, 0x4C, 0x09, 0x0A, 0x08, 0x16, 0x1A, 0x0F]),
            (0xE1, [0x00, 0x16, 0x19, 0x03, 0x0F, 0x05, 0x32, 0x45, 0x46, 0x04, 0x0E, 0x0D, 0x35, 0x37, 0x0F]),
            (0xC0, [0x17, 0x15]),
            (0xC1, [0x41]),
            (0xC5, [0x00, 0x12, 0x80]),
            (0x36, [0x48]),  # Memory Access Control
            (0x3A, [0x55]),  # 16-bit pixel format
            (0xB0, [0x00]),
            (0xB1, [0xA0]),
            (0xB4, [0x02]),
            (0xB6, [0x02, 0x02]),
            (0xE9, [0x00]),
            (0xF7, [0x20, 0x00, 0x00, 0x00, 0x00]),
            (0x11, None),  # Sleep Out
        ]
        
        for cmd, data in init_commands:
            self.write_command(cmd)
            if data:
                for byte in data:
                    self.write_data(byte)
        
        time.sleep(0.12)
        self.write_command(0x29)  # Display On
        time.sleep(0.1)
        
        print("TFT Ekran Başlatıldı: 480x320 16-bit")
    
    def set_window(self, x0, y0, x1, y1):
        """Çizim alanı belirle"""
        self.write_command(0x2A)  # Column Address Set
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xFF)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)
        
        self.write_command(0x2B)  # Page Address Set
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xFF)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xFF)
        
        self.write_command(0x2C)  # Memory Write
    
    def fill_screen(self, color):
        """Tüm ekranı renkle doldur"""
        self.set_window(0, 0, self.WIDTH-1, self.HEIGHT-1)
        
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        
        # Hızlı doldurma
        high_byte = (color >> 8) & 0xFF
        low_byte = color & 0xFF
        
        for _ in range(self.WIDTH * self.HEIGHT):
            self.spi.writebytes([high_byte, low_byte])
        
        GPIO.output(self.CS_PIN, GPIO.HIGH)
    
    def draw_rect(self, x, y, width, height, color):
        """Dikdörtgen çiz"""
        self.set_window(x, y, x + width - 1, y + height - 1)
        
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        
        high_byte = (color >> 8) & 0xFF
        low_byte = color & 0xFF
        
        for _ in range(width * height):
            self.spi.writebytes([high_byte, low_byte])
        
        GPIO.output(self.CS_PIN, GPIO.HIGH)
    
    def cleanup(self):
        """Temizlik"""
        self.spi.close()
        GPIO.cleanup()

class Touch:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi_bus = 0
        self.spi_device = 1  # Farklı SPI device
        self.spi_speed = 2000000  # 2 MHz
        
        self.T_CS_PIN = 7    # Pin 26
        self.T_IRQ_PIN = 17  # Pin 11
        
        self.setup_touch()
    
    def setup_touch(self):
        """Dokunmatik ekranı başlat"""
        GPIO.setup(self.T_CS_PIN, GPIO.OUT)
        GPIO.output(self.T_CS_PIN, GPIO.HIGH)
        
        try:
            self.spi.open(self.spi_bus, self.spi_device)
            self.spi.max_speed_hz = self.spi_speed
            self.spi.mode = 0
            print("Dokunmatik SPI bağlantısı başarılı")
        except Exception as e:
            print(f"Dokunmatik SPI hatası: {e}")
    
    def read_touch(self):
        """Dokunmatik verisi oku"""
        if GPIO.input(self.T_IRQ_PIN) == GPIO.LOW:
            GPIO.output(self.T_CS_PIN, GPIO.LOW)
            
            # X koordinatı oku
            x_data = self.spi.xfer2([0x90, 0x00, 0x00])
            x = ((x_data[1] << 8) | x_data[2]) >> 3
            
            # Y koordinatı oku
            y_data = self.spi.xfer2([0xD0, 0x00, 0x00])
            y = ((y_data[1] << 8) | y_data[2]) >> 3
            
            GPIO.output(self.T_CS_PIN, GPIO.HIGH)
            
            # Koordinatları ekran boyutuna çevir
            if x > 100 and y > 100:
                screen_x = int((x - 180) * 480 / (3900 - 180))
                screen_y = int((y - 240) * 320 / (3900 - 240))
                
                screen_x = max(0, min(479, screen_x))
                screen_y = max(0, min(319, screen_y))
                
                return (screen_x, screen_y)
        
        return None

# Renk Tanımlamaları (RGB565)
class Colors:
    BLACK = 0x0000
    WHITE = 0xFFFF
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    GRAY = 0x8410
    YELLOW = 0xFFE0

# Renk Tanımlamaları (RGB565)
class Colors:
    BLACK = 0x0000
    WHITE = 0xFFFF
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    GRAY = 0x8410

class RGBButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):  # DÜZELTİ: nokta yerine virgül
        super().__init__(**kwargs)

        self.images = [
            'rgb_images/state_off.jpg',
            'rgb_images/state_red.jpg',
            'rgb_images/state_green.jpg',
            'rgb_images/state_blue.jpg'
        ]

        self.rgb_index = 0  # gösterilecek resim numarası
        self.source = self.images[self.rgb_index]  # DÜZELTİ: current_index yerine rgb_index

    def on_press(self):
        """Butona basılınca bir sonraki resme geç"""
        self.rgb_index = (self.rgb_index + 1) % len(self.images)
        self.source = self.images[self.rgb_index]

class LightButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.images = [
            'light_images/state_off.jpg',
            'light_images/state_on.jpg'
        ]
        self.light_index = 0
        self.source = self.images[self.light_index]  # DÜZELTİ: current_index yerine light_index

    def on_press(self):
        """Butona basılınca aç/kapat"""
        self.light_index = (self.light_index + 1) % len(self.images)
        self.source = self.images[self.light_index]

class MainPage(App):
    def build(self):
        # TFT ekranı başlat (isteğe bağlı)
        try:
            self.tft = Display()
            self.tft.init_display()
            self.tft.fill_screen(Colors.BLACK)  # Ekranı siyah yap
        except Exception as e:
            print(f"TFT başlatma hatası: {e}")
            self.tft = None
    
        return self.gui()

    def gui(self):
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        # Üst kısım - Saat
        up_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        self.time_label = Label(
            text="00:00:00", 
            font_size='40sp',
            color=(1, 1, 1, 1)
        )
        up_layout.add_widget(self.time_label)
        main_layout.add_widget(up_layout)

        # Orta kısım - Sol taraf (butonlar)
        middle_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.6))
        
        middle_left_layout = GridLayout(cols=1, rows=2, spacing=20, size_hint=(0.3, 1))
        self.rgb_button = RGBButton()
        self.light_button = LightButton()
        middle_left_layout.add_widget(self.rgb_button)
        middle_left_layout.add_widget(self.light_button)
        
        # Buton event'lerini bağla
        self.rgb_button.bind(on_press=self.rgb_control)
        self.light_button.bind(on_press=self.light_control)

        # Orta kısım - Sağ taraf (sistem bilgileri)
        middle_right_layout = GridLayout(cols=2, rows=2, spacing=20, size_hint=(0.7, 1))
        
        self.ram_label = Label(
            text=f'RAM: {get_ram_usage():.1f}%',
            font_size='20sp',
            color=(1, 1, 1, 1)
        )
        self.cpu_label = Label(
            text=f'CPU: {get_cpu_usage():.1f}%',
            font_size='20sp',
            color=(1, 1, 1, 1)
        )
        self.cpu_temp = Label(
            text=f'Sıcaklık: {get_cpu_temp():.1f}°C',
            font_size='20sp',
            color=(1, 1, 1, 1)
        )
        self.ip_label = Label(
            text=f'IP: {get_ip_address()}',
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        
        middle_right_layout.add_widget(self.ram_label)
        middle_right_layout.add_widget(self.cpu_label)
        middle_right_layout.add_widget(self.cpu_temp)
        middle_right_layout.add_widget(self.ip_label)

        # Orta layout'u birleştir
        middle_layout.add_widget(middle_left_layout)
        middle_layout.add_widget(middle_right_layout)
        main_layout.add_widget(middle_layout)

        # Zamanlayıcıyı başlat
        Clock.schedule_interval(self.update_time, 1)
        
        return main_layout  # EKSİK: return ekledim

    def update_time(self, dt):
        """Saniyede bir saati ve sistem bilgilerini güncelle"""
        now = datetime.now()
        
        # Saati güncelle
        time_str = now.strftime('%H:%M:%S')
        self.time_label.text = time_str
        
        # Sistem bilgilerini güncelle
        self.ram_label.text = f'RAM: {get_ram_usage():.1f}%'
        self.cpu_label.text = f'CPU: {get_cpu_usage():.1f}%'
        self.cpu_temp.text = f'Sıcaklık: {get_cpu_temp():.1f}°C'
        self.ip_label.text = f'IP: {get_ip_address()}'

    def rgb_control(self, instance):
        """RGB butonuna tıklanınca"""
        print(f"RGB Butonu: Durum {instance.rgb_index}")
        # Burada TFT ekrana RGB durumunu yazdırabilirsiniz
        # if self.tft:
        #     self.tft.draw_text(f"RGB: {instance.rgb_index}", 10, 10)

    def light_control(self, instance):
        """Işık butonuna tıklanınca"""
        state = "AÇIK" if instance.light_index == 1 else "KAPALI"
        print(f"Işık Butonu: {state}")
        # Burada TFT ekrana ışık durumunu yazdırabilirsiniz

if __name__ == '__main__':
    MainPage().run()