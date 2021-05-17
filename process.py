import csv
import os
import pytz
from datetime import datetime
import collections

Record = collections.namedtuple(
  "Record", ["year", "month", "day", "hr", "mn", "watts"])

def compare(year, month, day, hr, record):
  if year < record.year:
    return -1
  if year > record.year:
    return 1

  if month < record.month:
    return -1
  if month > record.month:
    return 1

  if day < record.day:
    return -1
  if day > record.day:
    return 1

  if hr < record.hr:
    return -1
  if hr > record.hr:
    return 1

  return 0

def after(year, month, day, hr, record):
  return compare(year, month, day, hr, record) <= 0

def before(year, month, day, hr, record):
  return compare(year, month, day, hr, record) > 0

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
  ((2019,3,24,12), (2019,3,27,23)),
  ((2019,4,10,13), (2019,4,15,0)),
  ((2019,4,16,0),  (2019,4,16,23)),
  ((2019,4,24,0),  (2019,4,24,23)),
  ((2019,4,26,0),  (2019,4,26,23)),
  ((2019,8,17,15), (2019,8,28,11)),
  ((2020,2,17,12), (2020,4,2,11)),
  ((2020,5,10,13), (2020,5,16,17)),
  ((2020,6,23,13), (2020,6,29,23)),
  ((2020,7,2,16),  (2020,7,12,13)),
  ((2020,8,3,13),  (2020,8,5,15)),
  ((2020,8,8,16),  (2020,8,11,15))]

def is_broken(record):
  for start, end in broken_periods:
    if after(*start, record) and before(*end, record):
      return True
  return False

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
            raw_data.append(Record(
              int(year), int(month), int(day), int(hr), int(mn), int(watts)))

tz = pytz.timezone('America/New_York')
dst_adj_data = []
for record in raw_data:
  if tz.localize(datetime(record.year, record.month, record.day),
                 is_dst=None).tzinfo._dst.seconds:
    record = Record(record.year, record.month, record.day,
                    record.hr - 1, record.mn, record.watts)
  dst_adj_data.append(record)

clean_data = [record for record in raw_data
              if not is_broken(record)]

whmin = [record.watts for record in clean_data]
whmin.sort()
with open("whmin_percentiles.tsv", "w") as outf:
  for i in range(100):
    perc = i / 100
    outf.write("%.2f\t%s\n" % (
      perc, whmin[int(perc * len(whmin))]))

# (y,m,d) -> total watt-minutes (total watts)
day_watt_minutes = collections.defaultdict(int)
for record in clean_data:
  day_watt_minutes[record.year, record.month, record.day] += record.watts

kWh_day = [
  (watt_minutes / 60 / 1000, year, month, day)
  for ((year, month, day), watt_minutes) in day_watt_minutes.items()]

with open("kwh_percentiles.tsv", "w") as outf:
  for i, (kWh, year, month, day) in enumerate(sorted(kWh_day)):
    outf.write("%.2f\t%.3f\t%s-%s-%s\n" % (i / len(kWh_day),
                                           kWh, year, month, day))

md_kWh = [
  (month, day, watt_minutes / 60 / 1000)
  for ((year, month, day), watt_minutes) in day_watt_minutes.items()]

with open("kwh_scatter.tsv", "w") as outf:
  for month, day, kWh in sorted(md_kWh):
    outf.write("%s/%s\t%.3f\n" % (month, day, kWh))
