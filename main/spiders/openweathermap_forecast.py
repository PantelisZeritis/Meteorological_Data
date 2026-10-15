import scrapy, os, sys, json
from datetime import datetime

from ..database.connection import DBConnection
from ..preprocessing import *
from ..logger.setup import Logger

class OWMForecastSpider(scrapy.Spider):
    name = "openweathermap_forecast"

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2
    }

    logs = Logger("openweathermap.org", "logger/owm_forecast.log")
    db_connection = DBConnection()

    API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with your actual OpenWeatherMap API key

    def start_requests(self):
        self.logs.info(f"------------------------------------------ Starting OWM API scraping... ------------------------------------------")

        cities = [
            {'query': 'Tripoli,GR', 'city': 'Τρίπολη'},
            {'query': 'Argos,GR', 'city': 'Άργος'},
            {'query': 'Kalamata,GR', 'city': 'Καλαμάτα'},
            {'query': 'Corinth,GR', 'city': 'Κόρινθος'},
            {'query': 'Sparta,GR', 'city': 'Σπάρτη'},
            {'query': 'Gytheio,GR', 'city': 'Γύθειο'},
            {'query': 'Megalopoli,GR', 'city': 'Μεγαλόπολη'},
            {'query': 'Aigio,GR', 'city': 'Αίγιο'},
            {'query': 'Amaliada,GR', 'city': 'Αμαλιάδα'},
        ]

        for item in cities:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={item['query']}&appid={self.API_KEY}&units=metric&lang=el"
            yield scrapy.Request(url=url, callback=self.parse, meta={"city": item['city']})

    def parse(self, response):
        try:
            src = "openweathermap.org"
            city = response.meta["city"]
            timecrawl = initTimecrawl() 

            data = json.loads(response.text)

            if str(data.get("cod")) != "200":
                self.logs.error(f"API Error for {city}: {data.get('message')}")
                return

            # Η λίστα 'list' περιέχει τις προβλέψεις ανά 3ωρο
            for item in data.get('list', []):
                
                # 1. Ημερομηνία και Ώρα (Το OWM τα δίνει σε μορφή 'YYYY-MM-DD HH:MM:SS')
                dt_txt = item.get('dt_txt', '')
                if dt_txt:
                    date_obj = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                    day = date_obj.strftime("%d/%m/%Y") # Το κάνουμε DD/MM/YYYY
                    hour = date_obj.strftime("%H:%M")
                else:
                    continue

                # 2. Θερμοκρασία (έρχεται σε Celsius λόγω units=metric)
                temp_raw = item.get('main', {}).get('temp')
                temperature = round(float(temp_raw), 1) if temp_raw is not None else None

                # 3. Υγρασία 
                humidity = item.get('main', {}).get('humidity')

                # 4. Ταχύτητα Ανέμου
                wind_speed_ms = item.get('wind', {}).get('speed')
                wind_km = round(float(wind_speed_ms) * 3.6, 1) if wind_speed_ms is not None else None

                # 5. Κατεύθυνση Ανέμου 
                wind_deg = item.get('wind', {}).get('deg')
                wind_dir = None
                if wind_deg is not None:
                    idx = int((float(wind_deg) + 11.25) // 22.5) % 16
                    sectors = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
                    wind_dir = cleanWindDirection(sectors[idx])

                # 6. Καιρικές Συνθήκες 
                weather_arr = item.get('weather', [])
                weather_cond = None
                if weather_arr:
                    weather_cond = str(weather_arr[0].get('description', '')).capitalize()
                    weather_cond = cleanWeatherCondition(weather_cond)

                # JSON εξαγωγή
                yield {
                    'src': src,
                    'city': city,
                    'timecrawl': timecrawl,
                    'day': day,
                    'hour': hour,
                    'temperature': temperature,
                    'humidity': humidity,
                    'wind_km': wind_km,
                    'wind_dir': wind_dir,
                    'weather_cond': weather_cond,
                }

                # ------------ Αποθήκευση στη Βάση ------------
                try:
                    connect = self.db_connection.connect()
                    if connect.get("success") is None:
                        self.logs.error(f"Error occurred while opening database connection...")

                    data_columns = '(src, city, timecrawl, day, hour, temperature, humidity, wind_km, wind_dir, weather_cond)'
                    values = (src, city, timecrawl, day, hour, temperature, humidity, wind_km, wind_dir, weather_cond)

                    query = "INSERT INTO meteodata {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(data_columns)

                    if self.db_connection.get_cursor() is not None and self.db_connection.get_connection() is not None:
                        self.db_connection.get_cursor().execute(query, values)
                        self.db_connection.get_connection().commit()
                except Exception as db_err:
                    self.logs.scrapingStatus.increment_failed_database()
                # -----------------------------------------------

            self.logs.scrapingStatus.increment_success()
            self.logs.info(f"Successful fetched '{city}' city and stored to db from '{src}'.")

        except Exception as e:
            self.exception_triggered(response, e)

    def exception_triggered(self, response, e):
        self.logs.scrapingStatus.increment_failed()
        _, _, tb = sys.exc_info()
        self.logs.error(f"Scraping '{response.meta['city']}' city. Line {tb.tb_lineno} with message: [{e.args[0]}]")

    def closed(self, spider):
        self.logs.info(f"------------------------------------------ API Fetching finished. Success: {self.logs.scrapingStatus.success} | Failed: {self.logs.scrapingStatus.failed} | Database failed inserts: {self.logs.scrapingStatus.failed_database} | Total: {self.logs.scrapingStatus.total} ------------------------------------------\n")