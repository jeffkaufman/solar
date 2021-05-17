import csv
import os
import pytz
from datetime import datetime

raw_data = []
with open("tmp.dates") as dinf:
  for dline in dinf:
    d = dline.strip()
    fname = os.path.join("data", d + ".txt")
    if os.path.exists(fname):
      with open(fname) as inf:
        year, month, day = d.split('-')
        for i, line in enumerate(csv.reader(inf)):
          if i:
            time, watts = line
            hr, mn = time.split(':')
            raw_data.append(
              (int(year), int(month), int(day), int(hr), int(mn), int(watts)))

tz = pytz.timezone('America/New_York')
dst_adj_data = []
for year, month, day, hr, mn, watts in raw_data:
  if tz.localize(datetime(year, month, day), is_dst=None).tzinfo._dst.seconds:
    hr -= 1
  dst_adj_data.append((year, month, day, hr, mn, watts))

#  2019-03-24 12:00 to 2019-03-27 23:00
#  2019-04-10 13:00 to 2019-04-15 00:00
#  2019-04-16 00:00 to 2019-04-16 23:00
#  2019-04-24 00:00 to 2019-04-24 23:00
#  2019-04-26 00:00 to 2019-04-26 23:00
#  2019-08-17 15:00 to 2019-08-28 11:00
#  2020-02-17 12:00 to 2020-04-02 11:00
#  2020-05-10 13:00 to 2020-05-16 17:00
#  2020-06-23 13:00 to 2020-06-29 23:00
#  2020-07-02 16:00 to 2020-07-12 13:00
#  2020-08-03 13:00 to 2020-08-05 15:00
#  2020-08-08 16:00 to 2020-08-11 15:00
broken_periods = [
  ((2019,03,24,12), (2019,03,27,23)),
  ((2019,04,10,13), (2019,04,15,00)),
  ((2019,04,16,00), (2019,04,16,23)),
  ((2019,04,24,00), (2019,04,24,23)),
  ((2019,04,26,00), (2019,04,26,23)),
  ((2019,08,17,15), (2019,08,28,11)),
  ((2020,02,17,12), (2020,04,02,11)),
  ((2020,05,10,13), (2020,05,16,17)),
  ((2020,06,23,13), (2020,06,29,23)),
  ((2020,07,02,16), (2020,07,12,13)),
  ((2020,08,03,13), (2020,08,05,15)),
  ((2020,08,08,16), (2020,08,11,15))]

def is_broken(year, month, day, hr):
  for start, end in broken_periods:
    if (start[0] <= year <= end[0] and
        start[1] <= month <= end[1] and
        start[2] <= day <= end[2] and
        start[3] <= hr <= end[3]):
      return True
  return False

clean_data = []
for year, month, day, hr, mn, watts in raw_data:
  if not is_broken(year, month, day, hr):
    clean_data.append((year, month, day, hr, mn, watts))


  
