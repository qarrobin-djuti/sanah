import ephem
from datetime import datetime, timedelta
from kivymd.app import MDApp
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.screen import MDScreen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from geopy.geocoders import Nominatim
import pytz
from timezonefinder import TimezoneFinder

# Membuat objek observer di lokasi Anda (misal, Hegra, Mada-in Shalih)
observer = ephem.Observer()
observer.lat, observer.lon = '26.7916', '37.9528'  # Koordinat Hegra

# Menentukan batas waktu perhitungan (misal, periode 19 tahun dari 1512 hingga 2044)
start_date = datetime(1970, 3, 1)
end_date = datetime(2999, 3, 31)

# Fungsi untuk mencari bulan baru
def find_new_moon(date):
    observer.date = date  # Mengatur tanggal observer
    new_moon = ephem.next_new_moon(date)
    return new_moon.datetime()

# Memeriksa setiap bulan baru dalam periode 19 tahun
date = start_date
new_moon_dates = []
while date <= end_date:
    new_moon_date = find_new_moon(date)
    new_moon_dates.append(new_moon_date)
    date = new_moon_date + timedelta(days=1)

# Daftar nama bulan Imlek
bulan_imlek = [
    "rabi-u l-awwal (abiyb)", "rabi-u l-tsaaniy (ziw)", "jumadi l-uwlaa (siywan)", "jumadi l-akhir (rabiy'iy)",
    "rajab (hamiysyiy)", "sya'baan (ab)", "ramadhaan (aluwl)", "syawaal (ataniym)",
    "dzu l-qa'ida (buwl)", "dzu l-hijja (kisluw)", "muharram (tabat)", "safar (syibat)"
]

# Menentukan apakah tahun tertentu memiliki bulan kabisat
def is_leap_year(year):
    # Siklus Metonik: terdapat bulan kabisat pada tahun ke-11, 14, 17, 19, 3, 6, dan 8
    return year % 19 in [2, 5, 8, 10, 13, 16, 18]

# Menyisipkan bulan kabisat dalam daftar bulan Imlek
def get_bulan_imlek_with_leap(year):
    bulan = bulan_imlek.copy()
    if is_leap_year(year):
        # Menyisipkan bulan kabisat, contoh setelah bulan ke-8
        bulan.insert(8, "Adzaar")
    return bulan

class TharihSanahApp(MDApp):
    def build(self):
        self.screen = MDScreen()

        # Top Toolbar
        self.toolbar = MDTopAppBar(
        title = "Tharih Sanah",
        pos_hint = {"top": 1})
        self.screen.add_widget(self.toolbar)

        self.input_year = MDTextField(
            hint_text = "Masukkan Tahun dari 1970 hingga 2999",
            size_hint = (0.8, 1),
            pos_hint = {"center_x": 0.5, "center_y": 0.8},
            input_filter = "int"
        )
        self.screen.add_widget(self.input_year)

        self.input_location = MDTextField(
            hint_text = "Masukkan Nama Wilayah",
            size_hint = (0.8, 1),
            pos_hint = {"center_x": 0.5, "center_y": 0.7}
        )
        self.screen.add_widget(self.input_location)

        self.button = MDRaisedButton(
            text = "Cari New Moon",
            pos_hint = {"center_x": 0.5, "center_y": 0.6},
            on_release = self.show_new_moon_dates
        )
        self.screen.add_widget(self.button)

        self.scroll_view = ScrollView(
            pos_hint = {"center_x": 0.5, "center_y": 0.3},
            size_hint = (0.9, 0.4)
        )
        self.list_view = MDList()
        self.scroll_view.add_widget(self.list_view)
        self.screen.add_widget(self.scroll_view)
        return self.screen

    def show_new_moon_dates(self, *args):
        try:
            year = int(self.input_year.text)
            location_name = self.input_location.text

            # Menggunakan geopy untuk mendapatkan koordinat
            geolocator = Nominatim(user_agent="lunisolar_app")
            location = geolocator.geocode(location_name)
            if not location:
                raise ValueError("Nama wilayah tidak ditemukan")
            
            latitude = location.latitude
            longitude = location.longitude

            # Menggunakan TimezoneFinder untuk mendapatkan zona waktu
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
            if not timezone_str:
                raise ValueError("Zona waktu tidak ditemukan")
            
            local_timezone = pytz.timezone(timezone_str)

            # Mengatur posisi observer berdasarkan koordinat
            observer = ephem.Observer()
            observer.lat = str(latitude)
            observer.lon = str(longitude)

            start_date = datetime(year, 3, 1)
            end_date = datetime(year+1, 3, 31)

            # Fungsi untuk mencari bulan baru
            def find_new_moon(date):
                observer.date = date  # Mengatur tanggal observer
                new_moon = ephem.next_new_moon(date)
                return new_moon.datetime()

            # Memeriksa setiap bulan baru dalam periode 19 tahun
            date = start_date
            new_moon_dates = []
            while date <= end_date:
                new_moon_date = find_new_moon(date)
                new_moon_dates.append(new_moon_date)
                date = new_moon_date + timedelta(days=1)

            # Menampilkan hasil
            self.list_view.clear_widgets()
            bulan_index = 0

            # Menampilkan daftar lengkap bulan dalam satu tahun dengan tanggal bulan baru yang sesuai
            list_item = TwoLineListItem(
            text=f"\nDaftar new moon di kalender Sanah tahun {start_date.year} hingga {end_date.year}:",
            secondary_text=f"\nLintang : {observer.lat}, Bujur : {observer.lon}"
            )
            self.list_view.add_widget(list_item)
            for year in range(start_date.year, end_date.year + 1):
                bulan_dengan_kabisat = get_bulan_imlek_with_leap(year)
                list_item = OneLineListItem(text=f"\nTahun {year} :")
                self.list_view.add_widget(list_item)
                for bulan in bulan_dengan_kabisat:
                    if bulan_index < len(new_moon_dates):
                        # Mengonversi waktu new moon dari UTC ke waktu lokal
                        new_moon_utc = new_moon_dates[bulan_index]
                        new_moon_local = new_moon_utc.astimezone(local_timezone)
                        list_item = OneLineListItem(text=f"{new_moon_local.strftime('%Y-%m-%d %H+7:%M:%S')} : {bulan}")
                        self.list_view.add_widget(list_item)
                        bulan_index += 1
                    else:
                        list_item = OneLineListItem(text=f"Tidak ada tanggal bulan baru : {bulan}")
                        self.list_view.add_widget(list_item)
        except (ValueError, AttributeError) as e:
            dialog = MDDialog(
                title = "Input Error",
                text = "Masukkan data yang valid!",
                size_hint = (0.8, 0.2)
            )
            dialog.open()
        

if __name__ == "__main__":
    TharihSanahApp().run()
