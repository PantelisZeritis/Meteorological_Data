import scrapy, os, sys

from ..database.connection import DBConnection
from ..preprocessing import *
from ..logger.setup import Logger

class OkairosHourlySpider(scrapy.Spider):
    name = os.path.splitext(os.path.basename(__file__))[0]

    logs = Logger("okairos.gr", "logger/okairos_forecast.log")
    db_connection = DBConnection()

    def parse(self, response):
        try:
            src = 'okairos.gr'
            city = response.meta["city"]
            timecrawl = initTimecrawl()

            for d in response.xpath('//div[@class="wnfp"]/h3'):
                raw_day = d.xpath("text()").get()
                table = d.xpath('following-sibling::*[1]')

                data = raw_day.split()
                day = createDay(data[1], data[2])

                for item in table.xpath(".//tr"):
                    if item.xpath(".//th").get():
                        continue

                    hour = item.xpath(".//td[@class='hour']/text()").get()

                    temperature = cleanTemperature(item.xpath(".//td[@class='temp']/div/text()").get())
                    wind_km = cleanWindSpeed(f"{item.xpath(".//td[@class='wind-speed']/text()").get()}{item.xpath(".//td[@class='wind-speed']/small/text()").get()}")
                    wind_dir = cleanWindDirection(item.xpath(".//td[@class='wind-direction']/div/@class").get())
                    humidity = cleanHumidity(item.xpath(".//td[@class='relative-moist']/text()").get())
                    yetos = cleanPrecipitation(item.xpath(".//td[@class='precipitation']/text()").get())
                    air_pressure = cleanAirPressure(item.xpath(".//td[10]/text()").get())
                    weather_cond = cleanWeatherCondition(item.xpath(".//td[2]/div/@title").get())
                    cloudiness = cleanCloudiness(item.xpath(".//td[8]/text()").get())

                    yield {
                        'src': src,
                        'city': city,
                        'timecrawl': timecrawl,
                        'day': day,
                        'hour': hour,
                        'weather_cond': weather_cond,
                        'temperature': temperature,
                        'wind_km': wind_km,
                        'wind_dir': wind_dir,
                        'yetos': yetos,
                        'cloudiness': cloudiness,
                        'humidity': humidity,
                        'air_pressure': air_pressure
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

            data_columns = "(src, city, timecrawl, day, hour,  weather_cond, temperature, wind_km, wind_dir, yetos, cloudiness, humidity, air_pressure)"
            values = (src, city, timecrawl, day, hour, weather_cond, temperature, wind_km, wind_dir, yetos, cloudiness, humidity, air_pressure)

            query = f"INSERT INTO okairosdata {data_columns} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

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

        yield scrapy.Request('https://www.okairos.gr/τρίπολη.html?v=ωριαία', callback = self.parse, meta = {"city": "Τρίπολη"})
        yield scrapy.Request('https://www.okairos.gr/γύθειο.html?v=ωριαία', callback = self.parse, meta = {"city": "Γύθειο"})
        yield scrapy.Request('https://www.okairos.gr/καλαμάτα.html?v=ωριαία', callback = self.parse, meta = {"city": "Καλαμάτα"})
        yield scrapy.Request('https://www.okairos.gr/κόρινθος.html?v=ωριαία', callback = self.parse, meta = {"city": "Κόρινθος"})
        yield scrapy.Request('https://www.okairos.gr/μεγαλόπολη.html?v=ωριαία', callback = self.parse, meta = {"city": "Μεγαλόπολη"})
        yield scrapy.Request('https://www.okairos.gr/ναύπλιο.html?v=ωριαία', callback = self.parse, meta = {"city": "Ναύπλιο"})
        yield scrapy.Request('https://www.okairos.gr/πάτρα.html?v=ωριαία', callback = self.parse, meta = {"city": "Πάτρα"})
        yield scrapy.Request('https://www.okairos.gr/σπάρτη.html?v=ωριαία', callback = self.parse, meta = {"city": "Σπάρτη"})
        yield scrapy.Request('https://www.okairos.gr/αίγιο.html?v=ωριαία', callback = self.parse, meta = {"city": "Αίγιο"})
