from datetime import datetime
from . import general, clean, convert

def initTimecrawl() -> datetime:
   return general.initTimecrawl()

def checkDate(date: str) -> bool:
   return general.checkDate(date)


# ---------------- clean ----------------

def cleanTemperature(value: str | None) -> float | None:
   return clean.cleanTemperature(value)


def cleanWindSpeed(value: str | None) -> float | None:
   return clean.cleanWindSpeed(value)


def cleanWindDirection(value: str | None) -> str | None:
   return clean.cleanWindDirection(value)


def cleanPrecipitation(value: str | None) -> float | None:
   return clean.cleanPrecipitation(value)


def cleanCloudiness(value: str | None) -> int | None:
   return clean.cleanCloudiness(value)


def cleanHumidity(value: str | None) -> int | None:
   return clean.cleanHumidity(value)


def cleanAirPressure(value: str | None) -> float | None:
   return clean.cleanAirPressure(value)


def cleanWeatherCondition(value: str | None) -> str | None:
   return clean.cleanWeatherCondition(value)


# ---------------- convert ----------------

def createDay(day: str, month: str) -> str | None:
   return convert.createDay(day, month)

def convert_live_meteo(text: str) -> str | None:
   return convert.convert_live_meteo(text)

def translate_weather(phrase: str) -> str | None:
   return convert.translate_weather(phrase)

def convertWindDir(wind_dir: str) -> str | None:
   return convert.convertWindDir(wind_dir)
