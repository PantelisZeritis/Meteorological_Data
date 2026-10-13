def createDay(day: str, month: str) -> str | None:
   months = {
      "ιαν": 1,
      "φεβ": 2,
      "μαρ": 3,
      "μάρ": 3,
      "απρ": 4,
      "μαι": 5,
      "μάι": 5,
      "ιουν": 6,
      "ιουλ": 7,
      "αυγ": 8,
      "αύγ": 8,
      "σεπ": 9,
      "οκτ": 10,
      "νοε": 11,
      "νοέ": 11,
      "δεκ": 12,

      "jan": 1,
      "feb": 2,
      "mar": 3,
      "apr": 4,
      "may": 5,
      "jun": 6,
      "jul": 7,
      "aug": 8,
      "sep": 9,
      "sept": 9,
      "oct": 10,
      "nov": 11,
      "dec": 12
   }

   month = month.lower()

   for key, value in months.items():
      if key in month:
         return f"{day}/{value}"

   return None

def convert_live_meteo(text: str) -> str | None:
   switcher = {
      'Argos': 'Άργος',
      'Tripoli': 'Τρίπολη',
      'Kalamata': 'Καλαμάτα',
      'Corinth': 'Κόρινθος',
      'Sparti': 'Σπάρτη',
      'Molaoi': 'Γύθειο',
      'Megalopoli': 'Μεγαλόπολη',
      'Aigio': 'Αίγιο',
      'Pirgos': 'Πύργος (Αμαλιάδα)'
   }

   for city_en, city_gr in switcher.items():
      if city_en in text:
         return city_gr

   return None

def translate_weather(phrase):
   phrase_map = {
      "isolated thunderstorms": "Απομονωμένες καταιγίδες",
      "scattered thunderstorms": "Σποραδικές καταιγίδες",
      "few showers": "Λίγες μπόρες",
      "partly cloudy": "Λίγη συννεφιά",
      "mostly cloudy": "Αρκετή συννεφιά",
      "overcast": "Πλήρης συννεφιά",
      "mostly sunny": "Κυρίως ηλιόλουστος",
      "mostly clear": "Κυρίως αίθριος",
      "broken clouds": "Διακεκομμένη συννεφιά",
      "few clouds": "Λίγα σύννεφα",
      "clear sky": "Αίθριος ουρανός",
      "light rain": "Ελαφριά βροχή",
      "heavy rain": "Έντονη βροχή",
      "moderate rain": "Μέτρια βροχή",
      "light snow": "Ελαφρύ χιόνι",
      "moderate snow": "Μέτριο χιόνι",
      "heavy snow": "Έντονο χιόνι"
   }

   phrase = phrase.lower()
   for key in phrase_map:
      if key in phrase:
         return phrase_map[key].capitalize()

   word_map = {
      "thunderstorm": "Καταιγίδα",
      "thunderstorms": "Καταιγίδες",
      "shower": "Μπόρα",
      "showers": "Μπόρες",
      "cloudy": "Συννεφιά",
      "cloud": "Σύννεφο",
      "rain": "Βροχή",
      "sunny": "Ηλιόλουστος",
      "sun": "Ήλιος",
      "fog": "Ομίχλη",
      "mist": "Ομίχλη",
      "snow": "Χιόνι",
      "wind": "Άνεμος",
      "hail": "Χαλάζι",
      "sleet": "Χιονόνερο",
      "tornado": "Τυφώνας",
      "dust": "Σκόνη",
      "haze": "Ομίχλη",
      "smoke": "Καπνός",
      "hot": "Ζέστη",
      "cold": "Κρύο",
      "freezing": "Παγετός",
      "drizzle": "Ψιχάλες",
      "clear": "Αίθριος",
      "breeze": "Αύρα",
      "gale": "Θύελλα",
      "gust": "Ριπή",
      "ice": "Πάγος"
   }

   for key in word_map:
      if key in phrase:
         return word_map[key].capitalize()

   return phrase

def convertWindDir(wind_dir):
   switcher = {
      'N':   'Β',
      'NNE': 'ΒΒΑ',
      'NE':  'ΒΑ',
      'ENE': 'ΑΒΑ',
      'E':   'Α',
      'ESE': 'ΑΝΑ',
      'SE':  'ΝΑ',
      'SSE': 'ΝΝΑ',
      'S':   'Ν',
      'SSW': 'ΝΝΔ',
      'SW':  'ΝΔ',
      'WSW': 'ΔΝΔ',
      'W':   'Δ',
      'WNW': 'ΔΒΔ',
      'NW':  'ΒΔ',
      'NNW':'ΒΒΔ',
   }

   if switcher.get(wind_dir) is not None:
      return switcher.get(wind_dir)
   else:
      return wind_dir
