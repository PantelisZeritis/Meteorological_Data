import re

def cleanTemperature(value: str) -> float | None:
   # if not value:
   #     raise ValueError("Invalid Temperature")

   value = value.lower()

   try:
      if "," in value:
         value = value.replace(',', '.').strip()

      if 'f' in value:
         value = value.replace('f', '').strip()
         value = round(((float(value) - 32) / 1.8), 1)
      elif '°' in value:
         value = value.replace('°c', '').strip()
      elif 'c' in value:
         value = value.replace('°c', '').strip()
      elif 'º' in value:
         value = value.replace('º', '').strip()

      return float(value)
   except Exception as e:
      return None

def cleanWindSpeed(value: str | None) -> float:
   if not value:
      return 0.0
   
   value = value.lower()

   try:
      if "," in value:
         value = value.replace(',', '.').strip()

      if 'μπ' in value:
         output = value.replace('μπ', '').strip()
         output = 3.01 * (float(output) ** 1.5)
      elif 'km/h' in value:
         output = value.replace('km/h', '').strip()
      elif 'm/s' in value or 'ms' in value:
         output = value.replace('m/s', '').replace('ms', '').strip()
         output = float(output) * 3.6
      elif 'mph' in value:
         output = value.replace('mph', '').strip()
         output = float(output) * 1.60934
      elif 'kt' in value or 'kn' in value:
         output = value.replace('kt', '').replace('kn', '').strip()
         output = float(output) * 1.852

      return round(float(output), 1)
   except Exception as e:
      return None

def cleanWindDirection(value: str | None) -> str | None:
   if not value:
      return None
   
   try:
      if "-" in value:
         value = value.replace("-", "").strip()

      if 'wind1' in value:
         value = value.replace('wind1', '').strip()
      elif 'wind2' in value:
         value = value.replace('wind2', '').strip()

      return str(value) if value else None
   except Exception as e:
      return None

def cleanPrecipitation(value: str) -> float | None:
   if not value:
      raise ValueError("Invalid Precipitation")
   
   try:
      if "," in value:
         value = value.replace(',', '.').strip()

      if 'mm' in value:
         output = value.replace('mm', '').strip()
      if 'in' in value:
         output = value.replace('in', '').strip()

      return float(output)
   except Exception as e:
      return None

def cleanCloudiness(value: str) -> int | None:
   # if not value:
   #     raise ValueError("Invalid Humidity")

   try:
      value = re.sub(r"\s+", " ", value).strip()

      if '%' in value:
         value = value.replace('%', '').strip()

      return int(value)
   except Exception as e:
      return None

def cleanHumidity(value: str) -> int | None:
   # if not value:
   #     raise ValueError("Invalid Humidity")

   try:
      value = re.sub(r"\s+", " ", value).strip()

      if '%' in value:
            value = value.replace('%', '').strip()

      return int(value)
   except Exception as e:
      return None

def cleanAirPressure(value: str | None) -> float | None:
   if not value:
      return None
   #     raise ValueError("Invalid Air Pressure")

   value = value.lower()

   try:
      if "," in value:
         value = value.replace(',', '.').strip()

      if 'hpa' in value:
         output = value.replace('hpa', '').strip()
      elif 'in' in value:
         output = value.replace('in', '').strip()
         output = float(output) * 33.86389

      return round(float(output), 1)
   except Exception as e:
      return None

def cleanWeatherCondition(value: str) -> str | None:
   # if not value:
   #     raise ValueError("Invalid Weather Condition")

   try:
      value = value.strip().replace("\n", "").replace("\t", "").strip()
      return str(value)
   except Exception as e:
      return None