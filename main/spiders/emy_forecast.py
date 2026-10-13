import scrapy, os, sys
from datetime import datetime as dt

from ..database.connection import DBConnection
from ..preprocessing import *
from ..logger.setup import Logger

class EmyForecastSpider(scrapy.Spider):
    name = "emy_forecast"

    # Ρυθμίσεις αποκλειστικά για αυτό το spider
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 2, 
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1, 
        'ROBOTSTXT_OBEY': False 
    }

    logs = Logger("emy.gr", "logger/emy_forecast.log")
    db_connection = DBConnection()

    def start_requests(self):
        self.logs.info(f"------------------------------------------ Starting scraping... ------------------------------------------")

        # Λίστα με τα URLs της ΕΜΥ
        cities = [
            {'url': 'http://oldportal.emy.gr/emy/el/forecast/meteogramma_emy?perifereia=Peloponnese&poli=Tripoli', 'city': 'Τρίπολη'},
            {'url': 'http://oldportal.emy.gr/emy/el/forecast/meteogramma_emy?perifereia=Peloponnese&poli=Pyrgela', 'city': 'Άργος'},
            {'url': 'http://oldportal.emy.gr/emy/el/forecast/meteogramma_emy?perifereia=Peloponnese&poli=Kalamata', 'city': 'Καλαμάτα'},
            {'url': 'http://oldportal.emy.gr/emy/el/forecast/meteogramma_emy?perifereia=Peloponnese&poli=Korinthos', 'city': 'Κόρινθος'},
            {'url': 'http://oldportal.emy.gr/emy/el/forecast/meteogramma_emy?perifereia=Peloponnese&poli=sparti', 'city': 'Σπάρτη'},
        ]

        for item in cities:
            yield scrapy.Request(url=item['url'], callback=self.parse, meta={"city": item['city']})

    def parse(self, response):
        try:
            src = "emy.gr"
            city = response.meta["city"]
            timecrawl = initTimecrawl() 

            # Βρίσκουμε ΟΛΑ τα "κουτάκια" (blocks) των ωρών
            hourly_blocks = response.xpath('//div[contains(@class, "col-md-1 text text-center")]')

            for block in hourly_blocks:
                raw_hour = block.xpath('.//h6[@class="imnia"]/text()').get()
                
                if not raw_hour:
                    continue
                
                hour = raw_hour.split()[-1] 

                raw_day = block.xpath('./preceding::h3[@class="prognosi_kairou"][1]/text()').get()
                day = raw_day.split(" ")[1] if raw_day else None

                # 1. Θερμοκρασία
                raw_temp = block.xpath('.//span[@class="stylered"]/text()').get()
                temperature = cleanTemperature(raw_temp)

                # 2. Καιρικές Συνθήκες
                weather_image = block.xpath('.//img[@class="eikona-kairou"]/@src').get()
                weather_cond = None
                if weather_image:
                    icon_num = weather_image.split('/')[-1].replace('.png', '')
                    emy_weather_map = {
                        "01": "Καθαρός", "02": "Λίγα σύννεφα", "03": "Αραιή συννεφιά", "04": "Συννεφιά",
                        "05": "Συννεφιά", "06": "Ομίχλη", "07": "Ομίχλη", "08": "Ασθενής Βροχή",
                        "09": "Βροχή", "10": "Ισχυρή Βροχή", "11": "Καταιγίδα", "12": "Ισχυρή Καταιγίδα",
                        "14": "Χιονόνερο", "15": "Χιόνι", "16": "Ισχυρή Χιονόπτωση",
                        "51": "Καθαρός", "52": "Λίγα σύννεφα", "53": "Αραιή συννεφιά", "54": "Συννεφιά",
                        "55": "Συννεφιά", "56": "Ομίχλη", "57": "Ομίχλη", "58": "Ασθενής Βροχή",
                        "59": "Βροχή", "60": "Ισχυρή Βροχή", "61": "Καταιγίδα", "62": "Ισχυρή Καταιγίδα",
                        "64": "Χιονόνερο", "65": "Χιόνι", "66": "Ισχυρή Χιονόπτωση"
                    }
                    weather_cond = emy_weather_map.get(icon_num, f"Άγνωστο ({icon_num})")

                # 3. Ταχύτητα Ανέμου (Μετατροπή Κόμβων σε χλμ/ώρα)
                raw_wind_kt = block.xpath('.//h6[contains(text(), "kt")]/text()').get()
                wind_km = None
                if raw_wind_kt:
                    import re
                    knots_match = re.search(r'(\d+)', raw_wind_kt)
                    if knots_match:
                        knots = int(knots_match.group(1))
                        # Μετατροπή: 1 Κόμβος = 1.852 χλμ/ώρα
                        wind_km = round(knots * 1.852, 1)

                # 4. Κατεύθυνση Ανέμου
                wind_style = block.xpath('.//img[@class="eikona-anemou"]/@style').get()
                wind_dir = None
                if wind_style:
                    import re
                    try:
                        dir_degrees = float(re.search(r'rotate\(([\d.]+)deg\)', wind_style).group(1))
                        idx = int((dir_degrees + 11.25) // 22.5) % 16
                        sectors = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
                        wind_dir = cleanWindDirection(sectors[idx])
                    except:
                        wind_dir = None

                # 5. Υγρασία 
                humidity = None

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
            self.logs.info(f"Successful scraped '{city}' city and stored to db from '{src}'.")

        except Exception as e:
            self.exception_triggered(response, e)

    def exception_triggered(self, response, e):
        self.logs.scrapingStatus.increment_failed()
        _, _, tb = sys.exc_info()
        self.logs.error(f"Scraping '{response.meta['city']}' city. Line {tb.tb_lineno} with message: [{e.args[0]}]")

    def closed(self, spider):
        self.logs.info(f"------------------------------------------ Scraping finished. Success: {self.logs.scrapingStatus.success} | Failed: {self.logs.scrapingStatus.failed} | Database failed inserts: {self.logs.scrapingStatus.failed_database} | Total: {self.logs.scrapingStatus.total} ------------------------------------------\n")