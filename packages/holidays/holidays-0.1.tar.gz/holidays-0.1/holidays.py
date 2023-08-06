#  holidays.py
#  -----------
#  A fast, efficient Python library for generating country-specific lists of
#  holidays on the fly which aims to make determining whether a specific date
#  is a hoiday as fast and flexible as possible.
#
#  Author:  ryanss <ryanssdev@icloud.com>
#  Website: https://github.com/ryanss/holidays.py
#  License: MIT (see LICENSE file)

__author__  = 'ryanssdev@icloud.com'
__version__ = '0.1'
__license__ = 'MIT'


from datetime import date, datetime
from dateutil.easter import easter
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta as rd
from dateutil.relativedelta import MO, TH, FR


class Holidays(dict):

    def __init__(self, country="US", prov=None, years=[], expand=True,
                 observed=True):
        self.country = country
        self.prov = prov
        if self.country == "CA" and not self.prov:
            self.prov = "ON"
        self.observed = observed
        self.expand = expand
        self.years = set(years)
        for year in list(self.years):
            self._populate(year)

    def __setattr__(self, key, value):
        if key == 'observed' and len(self) > 0:
            dict.__setattr__(self, key, value)
            if value == True:
                # Add (Observed) dates
                years = list(self.years)
                self.years = set()
                self.clear()
                for year in years:
                    self._populate(year)
            else:
                # Remove (Observed) dates
                for k,v in self.items():
                    if v.find("Observed") >= 0:
                        del self[k]
        else:
            return dict.__setattr__(self, key, value)

    def __keytransform__(self, key):
        if isinstance(key, datetime):
            key = key.date()
        elif isinstance(key, date):
            key = key
        elif isinstance(key, int) or isinstance(key, float):
            key = datetime.fromtimestamp(key).date()
        elif isinstance(key, str) or isinstance(key, unicode):
            try:
                key = parse(key).date()
            except TypeError:
                raise ValueError("Cannot parse date from string '%s'" % key)
        else:
            raise TypeError("Cannot convert type '%s' to date." % type(key))
        # Treat Dec 31 as part of the next year
        # because it can be an Observed date for New Year's Day
        year = (key+rd(days=+1)).year
        if self.expand and year not in self.years:
            self.years.add(year)
            self._populate(year)
        return key

    def __contains__(self, key):
        return dict.__contains__(self, self.__keytransform__(key))

    def __getitem__(self, key):
        return dict.__getitem__(self, self.__keytransform__(key))

    def __setitem__(self, key, value):
        return dict.__setitem__(self, self.__keytransform__(key), value)

    def get(self, key):
        return dict.get(self, self.__keytransform__(key))

    def pop(self, key, default=None):
        if default == None:
            return dict.pop(self, self.__keytransform__(key))
        return dict.pop(self, self.__keytransform__(key), default)

    def _populate(self, year):
        if self.country == "US":
            # New Year's Day
            if year > 1870:
                self[date(year, 1, 1)] = "New Year's Day"
                if self.observed and date(year,1,1).weekday() == 5:
                    self[date(year,1,1)+rd(days=-1)] = "New Year's Day (Observed)"
                elif self.observed and date(year,1,1).weekday() == 6:
                    self[date(year,1,1)+rd(days=+1)] = "New Year's Day (Observed)"

            # Martin Luther King, Jr. Day
            if year >= 1986:
                self[date(year, 1, 1)+rd(weekday=MO(+3))] = "Martin Luther King, Jr. Day"

            # Washington's Birthday
            if year > 1970:
                self[date(year, 2, 1)+rd(weekday=MO(+3))] = "Washington's Birthday"
            elif year >= 1879:
                self[date(year, 2,22)] = "Washington's Birthday"

            # Memorial Day
            if year > 1970:
                self[date(year, 5,31)+rd(weekday=MO(-1))] = "Memorial Day"
            elif year >= 1888:
                self[date(year, 5,30)] = "Memorial Day"

            # Independence Day
            if year > 1870:
                self[date(year, 7, 4)] = "Independence Day"
                if self.observed and date(year,7,4).weekday() == 5:
                    self[date(year,7,4)+rd(days=-1)] = "Independence Day (Observed)"
                elif self.observed and date(year,7,4).weekday() == 6:
                    self[date(year,7,4)+rd(days=+1)] = "Independence Day (Observed)"

            # Labor Day
            if year >= 1894:
                self[date(year, 9, 1)+rd(weekday=MO)] = "Labor Day"

            # Columbus Day
            if year >= 1970:
                self[date(year,10, 1)+rd(weekday=MO(+2))] = "Columbus Day"
            elif year >= 1937:
                self[date(year,10,12)] = "Columbus Day"

            # Veterans Day
            if year > 1953:
                name = "Veterans Day"
            else:
                name = "Armistice Day"
            if 1978 > year > 1970:
                self[date(year,10, 1)+rd(weekday=MO(+4))] = name
            elif year >= 1938:
                self[date(year,11,11)] = name
                if self.observed and  date(year,11,11).weekday() == 5:
                    self[date(year,11,11)+rd(days=-1)] = name + " (Observed)"
                elif self.observed and date(year,11,11).weekday() == 6:
                    self[date(year,11,11)+rd(days=+1)] = name + " (Observed)"

            # Thanksgiving
            if year > 1870:
                self[date(year,11, 1)+rd(weekday=TH(+4))] = "Thanksgiving"

            # Christmas Day
            if year > 1870:
                self[date(year,12,25)] = "Christmas Day"
                if self.observed and  date(year,12,25).weekday() == 5:
                    self[date(year,12,25)+rd(days=-1)] = "Christmas Day (Observed)"
                elif self.observed and date(year,12,25).weekday() == 6:
                    self[date(year,12,25)+rd(days=+1)] = "Christmas Day (Observed)"

        elif self.country == "CA":
            # New Year's Day
            if year >= 1867:
                self[date(year, 1, 1)] = "New Year's Day"
                if self.observed and date(year,1,1).weekday() == 5:
                    self[date(year,1,1)+rd(days=-1)] = "New Year's Day (Observed)"
                elif self.observed and date(year,1,1).weekday() == 6:
                    self[date(year,1,1)+rd(days=+1)] = "New Year's Day (Observed)"

            # Islander Day
            if self.prov == 'PE' and year >= 2010:
                self[date(year,2,1)+rd(weekday=MO(+3))] = "Islander Day"
            elif self.prov == 'PE' and year == 2009:
                self[date(year,2,1)+rd(weekday=MO(+2))] = "Islander Day"

            # Family Day / Louis Riel Day (MB)
            if self.prov in ('AB','SK','ON') and year >= 2008:
                self[date(year,2,1)+rd(weekday=MO(+3))] = "Family Day"
            elif self.prov in ('AB','SK') and year >= 2007:
                self[date(year,2,1)+rd(weekday=MO(+3))] = "Family Day"
            elif self.prov == 'AB' and year >= 1990:
                self[date(year,2,1)+rd(weekday=MO(+3))] = "Family Day"
            elif self.prov == 'BC' and year >= 2013:
                self[date(year,2,1)+rd(weekday=MO(+2))] = "Family Day"
            elif self.prov == 'MB' and year >= 2008:
                self[date(year,2,1)+rd(weekday=MO(+3))] = "Louis Riel Day"

            # St. Patrick's Day
            if self.prov == 'NL' and year >= 1900:
                dt = date(year,3,17)
                # Nearest Monday to March 17
                dt1 = date(year,3,17)+rd(weekday=MO(-1))
                dt2 = date(year,3,17)+rd(weekday=MO(+1))
                if dt2 - dt <= dt - dt1:
                    self[dt2] = "St. Patrick's Day"
                else:
                    self[dt1] = "St. Patrick's Day"

            # Good Friday
            if self.prov != 'QC' and year >= 1867:
                self[easter(year)+rd(weekday=FR(-1))] = "Good Friday"

            # Easter Monday
            if self.prov == 'QC' and year >= 1867:
                self[easter(year)+rd(weekday=MO)] = "Easter Monday"

            # St. George's Day
            if self.prov == 'NL' and year == 2010:
                # 4/26 is the Monday closer to 4/23 in 2010
                # but the holiday was observed on 4/19? Crazy Newfies!
                self[date(2010,4,19)] = "St. George's Day"
            elif self.prov == 'NL' and year >= 1990:
                dt = date(year,4,23)
                # Nearest Monday to April 23
                dt1 = dt+rd(weekday=MO(-1))
                dt2 = dt+rd(weekday=MO(+1))
                if dt2 - dt < dt - dt1:
                    self[dt2] = "St. George's Day"
                else:
                    self[dt1] = "St. George's Day"

            # Victoria Day / National Patriotes Day (QC)
            if self.prov not in ('NB', 'NS', 'PE', 'NL','QC') and year >= 1953:
                self[date(year,5,24)+rd(weekday=MO(-1))] = "Victoria Day"
            elif self.prov == 'QC' and year >= 1953:
                self[date(year,5,24)+rd(weekday=MO(-1))] = "National Patriotes Day"

            # National Aboriginal Day
            if self.prov == 'NT' and year >= 1996:
                self[date(year,6,21)] = "National Aboriginal Day"

            # St. Jean Baptiste Day
            if self.prov == 'QC' and year >= 1925:
                self[date(year,6,24)] = "St. Jean Baptiste Day"
                if self.observed and date(year,6,24).weekday() == 6:
                    self[date(year,6,25)] = "St. Jean Baptiste Day (Observed)"

            # Discovery Day
            if self.prov == 'NL' and year >= 1997:
                dt = date(year,6,24)
                # Nearest Monday to June 24
                dt1 = dt+rd(weekday=MO(-1))
                dt2 = dt+rd(weekday=MO(+1))
                if dt2 - dt <= dt - dt1:
                    self[dt2] = "Discovery Day"
                else:
                    self[dt1] = "Discovery Day"
            elif self.prov == 'YU' and year >= 1912:
                self[date(year,8,1)+rd(weekday=MO(+3))] = "Discovery Day"

            # Canada Day / Memorial Day (NL)
            if self.prov != 'NL' and year >= 1867:
                self[date(year,7,1)] = "Canada Day"
                if self.observed and date(year,7,1).weekday() in (5,6):
                    self[date(year,7,1)+rd(weekday=MO)] = "Canada Day (Observed)"
            elif year >= 1867:
                self[date(year,7,1)] = "Memorial Day"
                if self.observed and date(year,7,1).weekday() in (5,6):
                    self[date(year,7,1)+rd(weekday=MO)] = "Memorial Day (Observed)"

            # Nunavut Day
            if self.prov == 'NU' and year >= 2001:
                self[date(year,7,9)] = "Nunavut Day"
                if self.observed and date(year,7,9).weekday() == 6:
                    self[date(year,7,10)] = "Nunavut Day (Observed)"
            elif self.prov == 'NU' and year == 2000:
                self[date(2000,4,1)] = "Nunavut Day"

            # Civic Holiday
            if self.prov in ('SK','ON','MB','NT') and year >= 1900:
                self[date(year,8,1)+rd(weekday=MO)] = "Civic Holiday"
            elif self.prov in ('BC') and year >= 1974:
                self[date(year,8,1)+rd(weekday=MO)] = "British Columbia Day"

            # Labour Day
            if year >= 1894:
                self[date(year,9,1)+rd(weekday=MO)] = "Labour Day"

            # Thanksgiving
            if self.prov not in ('NB','NS','PE','NL') and year >= 1931:
                self[date(year,10,1)+rd(weekday=MO(+2))] = "Thanksgiving"

            # Remembrance Day
            if self.prov not in ('ON','QC','NS','NL','NT','PE','SK') and year >= 1931:
                self[date(year,11,11)] = "Remembrance Day"
            elif self.prov in ('NS','NL','NT','PE','SK') and year >= 1931:
                self[date(year,11,11)] = "Remembrance Day"
                if self.observed and date(year,11,11).weekday() == 6:
                    self[date(year,11,11)+rd(weekday=MO)] = "Remembrance Day (Observed)"

            # Christmas Day
            if year >= 1867:
                self[date(year,12,25)] = "Christmas Day"
                if self.observed and date(year,12,25).weekday() == 5:
                    self[date(year,12,24)] = "Christmas Day (Observed)"
                elif self.observed and date(year,12,25).weekday() == 6:
                    self[date(year,12,26)] = "Christmas Day (Observed)"

            # Boxing Day
            if year >= 1867:
                if self.observed and date(year,12,26).weekday() in (5,6):
                    self[date(year,12,26)+rd(weekday=MO)] = "Boxing Day (Observed)"
                elif self.observed and date(year,12,26).weekday() == 0:
                    self[date(year,12,27)] = "Boxing Day (Observed)"
                else:
                    self[date(year,12,26)] = "Boxing Day"
