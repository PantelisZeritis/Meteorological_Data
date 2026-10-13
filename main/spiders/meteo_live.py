import scrapy, json, sys, os

from ..database.connection import DBConnection
from ..preprocessing import *
from ..logger.setup import Logger

argos = '{ "path": "https://penteli.meteo.gr/stations/argos/", "city": "Άργος"}'
tripoli = '{"path": "https://penteli.meteo.gr/stations/tripoli/", "city": "Τρίπολη"}'
kalamata = '{"path": "https://penteli.meteo.gr/stations/kalamata/", "city": "Καλαμάτα"}'
isthmos = '{"path": "https://penteli.meteo.gr/stations/isthmos/", "city": "Κόρινθος"}'
sparti = '{"path": "https://penteli.meteo.gr/stations/sparti/", "city": "Σπάρτη"}'
molaoi = '{"path": "https://penteli.meteo.gr/stations/molaoi/", "city": "Γύθειο"}'
megalopoli = '{"path": "https://penteli.meteo.gr/stations/megalopoli/", "city": "Μεγαλόπολη"}'
aigio = '{"path": "https://penteli.meteo.gr/stations/aigio/", "city": "Αίγιο"}'
pirgos = '{"path": "https://penteli.meteo.gr/stations/pirgos/", "city": "Πύργος (Αμαλιάδα)"}'


class Meteo_Live_Data(scrapy.Spider):
    name = os.path.splitext(os.path.basename(__file__))[0]

    logs = Logger("meteo.gr live", "logger/meteo_live.log")
    db_connection = DBConnection()

    def parse(self, response):
        try:
            if response.xpath('//div[contains(@class,"offline boxshadow")]/span/text()').get() is not None:
                print("Station is offline, skipping...")
                return
            
            src = 'meteo.gr'
            city = convert_live_meteo(self.get_city(response))
            timecrawl = initTimecrawl()

            # ------ day, hour ------

            day_hour = self.get_day_and_hour(response)
            day = f"{day_hour.split("/")[0]}/{day_hour.split("/")[1]}"

            hour = day_hour.split()[1]

            # -----------------------------

            for row in self.get_line_data(response):
                label = row.xpath('.//div[contains(@class,"lleft")]/span[1]/text()').get()
                value = row.xpath('.//div[contains(@class,"lright")]/span/text()').get()

                match label:
                    case "Temperature":
                        temperature = cleanTemperature(value)
                        
                    case "Humidity":
                        humidity = cleanHumidity(value)

                    case "Wind":
                        split_value = value.split(" ")
                        wind_km = self.checker(cleanWindSpeed(f"{split_value[0]}{split_value[1]}"))
                        wind_direction = self.checker(cleanWindDirection(split_value[3]))

                    case "Barometer":
                        air_pressure = cleanAirPressure(value)

                    case "Today's Rain":
                        yetos = cleanPrecipitation(value)

                    case "Rain Rate":
                        weather_cond = cleanPrecipitation(value)

            yield {
                'src': src,
                'city': city,
                'timecrawl': timecrawl,
                'day': day,
                'hour': hour,
                'temperature': temperature,
                'humidity': humidity,
                'wind_km': wind_km,
                'wind_dir': wind_direction,
                'weather_cond': weather_cond,
                'air_pressure': air_pressure,
                'yetos': yetos
            }

            # time.sleep(2)

            self.logs.scrapingStatus.increment_success()
            self.logs.info(f"Successful scraped '{convert_live_meteo(self.get_city(response))}' city and stored to csv from '{src}' source.")
        except Exception as e:
            self.exception_triggered(response, e)


        try:
            connect = self.db_connection.connect()
            if connect.get("success") is None:
                self.logs.error(f"Error occurred while opening database connection to city '{convert_live_meteo(self.get_city(response))}' from '{src}' source. Error Message: '{connect.get("error")}'")

            data_columns = "(src, city, timecrawl, day, hour, temperature, humidity, wind_km, wind_dir, weather_cond, air_pressure, yetos)"
            values = (src, city, timecrawl, day, hour, temperature, humidity, wind_km, wind_direction, weather_cond, air_pressure, yetos)            

            query = "INSERT INTO meteodata_live {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(data_columns)

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
        self.logs.error(f"Scraping '{convert_live_meteo(self.get_city(response))}' city. Line {tb.tb_lineno} with message: [{e.args[0]}]")

    def get_line_data(self, response):
        static = response.xpath('//div[contains(@class,"line")]')
        return self.checker(static)

    def get_city(self, response):
        static = response.xpath('.//span[contains(@class,"station_name")][2]/b/text()')
        return self.checker(static.get().strip())
    
    def get_day_and_hour(self, response):
        static = response.xpath('.//div[contains(@class,"headline gradient")]/span[2]/text()')
        return self.checker(static.get().strip())
    
    # ----------- check specific message -----------
    def checker(self, msg):
        return None if (msg is None or msg == '' or msg == ' ') else msg
    # -----------------------------------------------

    def closed(self, spider):
        self.logs.info(f"------------------------------------------ Scarping finished. Success: {self.logs.scrapingStatus.success} | Failed: {self.logs.scrapingStatus.failed} | Database failed inserts: {self.logs.scrapingStatus.failed_database} | Total: {self.logs.scrapingStatus.total} ------------------------------------------\n")

    def start_requests(self):
        self.logs.info(f"------------------------------------------ Starting scarping... ------------------------------------------")

        yield scrapy.Request(json.loads(argos)["path"], self.parse)  # Άργος
        yield scrapy.Request(json.loads(tripoli)["path"], self.parse)  # Τρίπολη
        yield scrapy.Request(json.loads(kalamata)["path"], self.parse)  # Καλαμάτα
        yield scrapy.Request(json.loads(isthmos)["path"], self.parse)  # Ισθμός - Κόρινθος
        yield scrapy.Request(json.loads(sparti)["path"], self.parse)  # Σπάρτη
        yield scrapy.Request(json.loads(molaoi)["path"], self.parse)  # Γύθειο
        yield scrapy.Request(json.loads(megalopoli)["path"], self.parse)  # Μεγαλόπολη
        yield scrapy.Request(json.loads(aigio)["path"], self.parse)  # Αίγιο
        yield scrapy.Request(json.loads(pirgos)["path"], self.parse)  # Αμαλιάδα (είναι εκτός λειτουργίας της Αμαλιάδας και πήρα του Πύργου)
