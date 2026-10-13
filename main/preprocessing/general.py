from datetime import datetime
from zoneinfo import ZoneInfo

def initTimecrawl() -> datetime:
   return datetime.now(ZoneInfo("Europe/Athens"))

def checkDate(date_in_row: str) -> bool:
   try:
      datetime.strptime(date_in_row, "%d/%m/%Y")
      return True
   except:
      return False
