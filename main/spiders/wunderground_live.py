import scrapy, psycopg2, re, os, sys, time

from ..database.connection import DBConnection
from ..preprocessing import *
from ..logger.setup import Logger

config = {
    'urls': [
        {'path': 'https://www.wunderground.com/weather/gr/pallantio/IPALLA34',  'city': 'Τρίπολη'},
        {'path': 'https://www.wunderground.com/weather/gr/argos',               'city': 'Άργος'},
        {'path': 'https://www.wunderground.com/weather/gr/kalamata',            'city': 'Καλαμάτα'},
        {'path': 'https://www.wunderground.com/weather/gr/corinth',             'city': 'Κόρινθος'},
        {'path': 'https://www.wunderground.com/weather/gr/sparti',              'city': 'Σπάρτη'},
        {'path': 'https://www.wunderground.com/weather/gr/gythio',              'city': 'Γύθειο'},
        {'path': 'https://www.wunderground.com/weather/gr/megalopoli',          'city': 'Μεγαλόπολη'},
        {'path': 'https://www.wunderground.com/weather/gr/aegion/IAEGIO2',      'city': 'Αίγιο'},
        {'path': 'https://www.wunderground.com/weather/gr/amalias',             'city': 'Πύργος (Αμαλιάδα)'}
    ],
    
    'measurements': [
        {'path': './/span[contains(@class,"last-updated")]/text()',                                                                 'item': 'get_last_updated'},
        {'path': './/p[contains(@class,"timestamp")]/span/strong/text()',                                                           'item': 'get_day'},
        {'path': './/div[contains(@class,"columns small-12 city-header")]/h1/span/text()',                                          'item': 'get_city'},
        {'path': './/p[contains(@class,"timestamp")]/span/strong/text()',                                                           'item': 'get_timestamp'},
        {'path': './/span[contains(@class,"test-true wu-unit wu-unit-temperature is-degree-visible")]/span/text()',                 'item': 'get_temp'},
        {'path': './/div[contains(@class,"wind-compass")]/@style',                                                                  'item': 'get_wind_dir'},
        {'path': './/span[contains(@class,"test-false wu-unit wu-unit-speed")]/span//text()',                                       'item': 'get_wind_speed'},
        {'path': './/span[contains(@class,"test-false wu-unit wu-unit-humidity")]/span/text()',                                     'item': 'get_humidity'},
        {'path': './/div[contains(@class,"condition-icon")]/p/text()',                                     'item': 'get_weather_cond'},
        {'path': './/span[contains(@class,"test-false wu-unit wu-unit-pressure")]/span/text()',                                     'item': 'get_pressure'},
        {'path': './/span[contains(@class,"test-false wu-unit wu-unit-rain")]/span/text()',                                         'item': 'get_yetos'}
    ]
}

class wunderground_live(scrapy.Spider):
    name = os.path.splitext(os.path.basename(__file__))[0]

    logs = Logger("wunderground.gr live", "logger/wunderground_live.log")
    db_connection = DBConnection()

    def start_requests(self):
        self.logs.info(f"------------------------------------------ Starting scarping... ------------------------------------------")

        for item in config["urls"]:
            yield scrapy.Request(item["path"], callback = self.parse, meta = {"city": item["city"]}) 

    def closed(self, spider):
        self.logs.info(f"------------------------------------------ Scarping finished. Success: {self.logs.scrapingStatus.success} | Failed: {self.logs.scrapingStatus.failed} | Database failed inserts: {self.logs.scrapingStatus.failed_database} | Total: {self.logs.scrapingStatus.total} ------------------------------------------\n")

    def parse(self, response):
        try:
            src = "wunderground.com"
            city = response.meta["city"]
            timecrawl = initTimecrawl()
            day = self.getDay(response)

            if not day:
                return

            hour = self.getHour(self.getTimestamp(response))

            temperature = cleanTemperature(self.getTemperature(response))
            wind_dir = cleanWindDirection(self.getWindDirection(response))
            wind_km = cleanWindSpeed(self.getWindSpeed(response))
            humidity = cleanHumidity(self.getHumidity(response))
            weather_cond = cleanWeatherCondition(self.getWeatherCondition(response))
            air_pressure = cleanAirPressure(self.getAirPressure(response))
            yetos = cleanPrecipitation(self.getPrecipitation(response))

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
                'air_pressure': air_pressure,
                'yetos': yetos
            }
        
            # time.sleep(2)

            self.logs.scrapingStatus.increment_success()
            self.logs.info(f"Successful scraped '{response.meta["city"]}' city and stored to csv from '{src}' source.")
        except Exception as e:
            self.exception_triggered(response, e)
            
        try:
            connect = self.db_connection.connect()
            if connect.get("success") is None:
                self.logs.error(f"Error occurred while opening database connection to city '{response.meta["city"]}' from '{src}' source. Error Message: '{connect.get("error")}'")

            data_columns = '(src, city, timecrawl, day, hour, temperature, humidity, wind_km, wind_dir, weather_cond, air_pressure, yetos)'
            values = (src, city, timecrawl, day, hour, temperature, humidity, wind_km, wind_dir, weather_cond, air_pressure, yetos)

            query = 'INSERT INTO wudata_live {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(data_columns)

            if self.db_connection.get_cursor() is None:
                self.logs.error(f"Database cursor is not available to city '{response.meta["city"]}' from '{src}' source.")

            if self.db_connection.get_connection() is None:
                self.logs.error(f"Database connection is not available to city '{response.meta["city"]}' from '{src}' source.")

            self.db_connection.get_cursor().execute(query, values)
            self.db_connection.get_connection().commit()
        except Exception as e:
            self.logs.scrapingStatus.increment_failed_database()



    def exception_triggered(self, response, e):
        self.logs.scrapingStatus.increment_failed()
        _, _, tb = sys.exc_info()
        self.logs.error(f"Scraping '{response.meta["city"]}' city. Line {tb.tb_lineno} with message: [{e.args[0]}]")

    def get_path(self, item):
        for iitem in config['measurements']:
            if iitem['item'] == item:
                return iitem['path']

        return None

    def getDay(self, response) -> str | None:
        if not self.checkLastUpdated(response):
            return None

        day = response.xpath(self.get_path('get_day')).get().lower().replace(',', '').split()
        return createDay(str(day[5]), str(day[4]))

    def checkLastUpdated(self, response) -> bool:
        last_updated = response.xpath(self.get_path('get_last_updated')).get().lower().split()

        if ('minutes' in last_updated) or ('hours' in last_updated):
            if ('minutes' in last_updated and int(last_updated[1]) > 10) or ('hours' in last_updated and int(last_updated[1]) > 0):
                print('Error! Meteorological stations have not been updated.')
                return False

        return True

    def getCity(self, response):
        return response.xpath(self.get_path('get_city')).get().split(',')[0]
    
    def getTimestamp(self, response):
        return response.xpath(self.get_path('get_timestamp')).get()

    def getHour(self, timestamp):
        timestamp = timestamp.lower()

        h, m, arr = None, None, timestamp.split()[0].split(':')
        
        h = int(arr[0])
        m = int(arr[1])

        if 'pm' in timestamp:
            if h != 12:
                h += 12
        elif 'am' in timestamp:
            if h == 12:
                h = 0
        
        return f'{h:02d}:{m:02d}' # 05:01 or 09:14

    def getTemperature(self, response):
        path = response.xpath(self.get_path('get_temp')).get()

        return f"{(int(path) - 32) / 1.8:.1f}" # convert f to c
    
    def getWindDirection(self, response) -> str | None:
        # https://en.wikipedia.org/wiki/Cardinal_direction
        # https://en.wikipedia.org/wiki/Compass_rose

        try:
            path = response.xpath(self.get_path('get_wind_dir')).get()
            dir = float(re.search(r'rotate\(([\d.]+)deg\)', path).group(1))
            idx = int((dir + 11.25) // 22.5) % 16

            sectors = [
                "N", "NNE", "NE", "ENE",
                "E", "ESE", "SE", "SSE",
                "S", "SSW", "SW", "WSW",
                "W", "WNW", "NW", "NNW"
            ]

            return convertWindDir(sectors[idx])
        except:
            return None

    def getWindSpeed(self, response) -> str | None:
        path = response.xpath(self.get_path('get_wind_speed')).get()
        return f"{path}mph" if path else None

    def getHumidity(self, response) -> str:
        return response.xpath(self.get_path('get_humidity')).get()

    def getWeatherCondition(self, response) -> str:
        return response.xpath(self.get_path('get_weather_cond')).get()
    
    def getAirPressure(self, response) -> str | None:
        return f"{response.xpath(self.get_path('get_pressure')).get()}in"
    
    def getPrecipitation(self, response) -> str:
        return f"{response.xpath(self.get_path('get_yetos')).get()}in"
