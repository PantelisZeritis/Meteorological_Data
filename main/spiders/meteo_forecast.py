import scrapy, os, sys
from datetime import datetime as dt

from ..database.connection import DBConnection
from ..preprocessing import *
from ..logger.setup import Logger

class Meteo_Data(scrapy.Spider):
    name = os.path.splitext(os.path.basename(__file__))[0]

    logs = Logger("meteo.gr", "logger/meteo_forecast.log")
    db_connection = DBConnection()

    def parse(self, response):
        try:
            src = "meteo.gr"
            city = response.meta["city"]
            timecrawl = initTimecrawl()
            tables = response.xpath('//div[@class="content"]//table[@id="outerTable"]')

            for table in tables:
                for content in table.xpath("./tbody/tr | ./tr"):
                    if not content:
                        continue

                    date_in_row = content.xpath('./td[1]/div')

                    if date_in_row and not len(date_in_row) == 0:
                        date_outside = date_in_row.xpath('./span[1]/text()').get()

                        if date_outside:
                            date_outside = date_outside.strip()

                            if checkDate(date_outside):
                                day = dt.strptime(date_outside, "%d/%m/%Y")
                            else:
                                day = date_in_row.xpath("./span[1]/text()").get()
                                month = date_in_row.xpath("./span[1]/span[1]/text()").get() or date_in_row.xpath("./span[2]/text()").get()

                                day = createDay(day, month)
                    else:
                        hour = content.xpath('./td[1]//table//tr[1]/td[1]/text()').get()
                        temperature = content.xpath('./td[2]/div/text()').get()
                        humidity = content.xpath('./td[3]//table//tr[1]/td/text()').get()
                        wind_km = content.xpath("./td[4]/table//tr[1]/td[1]/span/text()").get()
                        wind_dir = content.xpath('./td[4]/table//tr[1]/td[1]/text()').get()
                        weather_cond = content.xpath('./td[5]//table//tr[1]/td[1]/text()').get()

                        weather_cond = cleanWeatherCondition(weather_cond)
                        temperature = cleanTemperature(temperature)
                        wind_km = cleanWindSpeed(wind_km)
                        wind_dir = cleanWindDirection(wind_dir.split()[2])
                        humidity = cleanHumidity(humidity.replace("%", "").strip())

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

                    # time.sleep(3)

            self.logs.scrapingStatus.increment_success()
            self.logs.info(f"Successful scraped '{response.meta["city"]}' city and stored to csv from '{src}' source.")
        except Exception as e:
            self.exception_triggered(response, e)

        try:
            connect = self.db_connection.connect()
            if connect.get("success") is None:
                self.logs.error(f"Error occurred while opening database connection to city '{response.meta["city"]}' from '{src}' source. Error Message: '{connect.get("error")}'")

            data_columns = '(src, city, timecrawl, day, hour, temperature, humidity, wind_km, wind_dir, weather_cond)'
            values = (src, city, timecrawl, day, hour, temperature, humidity, wind_km, wind_dir, weather_cond)

            query = "INSERT INTO meteodata {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(data_columns)

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

    def closed(self, spider):
        self.logs.info(f"------------------------------------------ Scarping finished. Success: {self.logs.scrapingStatus.success} | Failed: {self.logs.scrapingStatus.failed} | Database failed inserts: {self.logs.scrapingStatus.failed_database} | Total: {self.logs.scrapingStatus.total} ------------------------------------------\n")

    def start_requests(self):
        self.logs.info(f"------------------------------------------ Starting scarping... ------------------------------------------")

        yield scrapy.Request('https://meteo.gr/cf.cfm?city_id=37', callback = self.parse, meta = {"city": "Άργος"})  # Άργος
        yield scrapy.Request('https://meteo.gr/cf.cfm?city_id=36', callback = self.parse, meta = {"city": "Τρίπολη"})  # Τρίπολη
        yield scrapy.Request('https://meteo.gr/cf.cfm?city_id=15', callback = self.parse, meta = {"city": "Καλαμάτα"})  # Καλαμάτα
        yield scrapy.Request('https://meteo.gr/cf.cfm?city_id=56', callback = self.parse, meta = {"city": "Κόρινθος"})  # Κόρινθος
        yield scrapy.Request('https://meteo.gr/cf.cfm?city_id=58', callback = self.parse, meta = {"city": "Σπάρτη"})  # Σπάρτη
        yield scrapy.Request('https://meteo.gr/cf.cfm?city_id=107', callback = self.parse, meta = {"city": "Γύθειο"})  # Γύθειο
        yield scrapy.Request('https://meteo.gr/cf.cfm?city_id=229', callback = self.parse, meta = {"city": "Μεγαλόπολη"})  # Μεγαλόπολη
        yield scrapy.Request('https://meteo.gr/cf.cfm?city_id=110', callback = self.parse, meta = {"city": "Αίγιο"})  # Αίγιο
        yield scrapy.Request('https://meteo.gr/cf.cfm?city_id=211', callback = self.parse, meta = {"city": "Αμαλιάδα"})  # Αμαλιάδα
