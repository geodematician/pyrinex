"""
Epoch class container.
"""

class Epoch:
    """
    Epoch, or GPS time.
    """
    def __init__(
        self, year = 1980, month = 1, day = 1, hour = 0,
        minute = 0, second = 0, timesystem = 'GPS'
        ):
        self.Year = year
        self.Month = month
        self.Day = day
        self.Hour = hour
        self.Minute = minute
        self.Second = second
        #TODO: timesystem implementation

    def __str__(self):
        """
        String transformer.
        """
        return "%02d/%02d/%4d %02d:%02d:%04.1f" % (self.Day, self.Month, self.Year, self.Hour, self.Minute, self.Second)
    
    def __hash__(self):
        """
        Hash on the epoch.
        """
        return hash(str(self))
    
    def __eq__(self, s):
        """
        Equality operator.
        """
        return ((self.Year==s.Year) and (self.Month==s.Month) and (self.Day==s.Day)
            and (self.Hour==s.Hour) and (self.Minute==s.Minute) and (self.Second==s.Second) )
    
    def __lt__(self, s):
        """
        Less than.
        """
        if self.ModifiedJulianDate() < s.ModifiedJulianDate():
            return True
        elif self.ModifiedJulianDate() > s.ModifiedJulianDate():
            return False
        else:
            if self.GPSSec() < s.GPSSec():
                return True
            else:
                return False
            
    def __ge__(self, s):
        """
        Greater than.
        """
        if not self < s:
            if not self == s:
                return True
        return False
    
    def JulianDate(self):
        """
        Julian date.
        """
        if self.Month <= 2:
            Y = self.Year - 1
            M = self.Month + 12
        else:
            Y = self.Year
            M = self.Month
        JD = int(365.25*Y) + int(30.6001 * (M+1)) + self.Day +(float(self.Hour)/24.0) + 1720981.5
        return JD
    
    def ModifiedJulianDate(self):
        """
        Modified Julian date
        """
        return self.JulianDate() - 2400000.5
    
    def GPSSec(self):
        """
        Number of elapsed seconds from the beginning of the GPS day.
        """
        s = self.Second
        s += self.Minute * 60
        s += self.Hour * (60*60)
        return s
    
    def GPSDay(self):
        """
        Return the GPS day.
        """
        return int(self.JulianDate()+1.5) % 7
    
    def GPSWeek(self):
        """
        Return the GPS Week.
        """
        return int((self.JulianDate()-2444244.5)/7)
    
    def GPSTimeOfWeek(self):
        """
        Return number of seconds elapsed from the beginning of the GPS week.
        """
        return self.GPSDay()*86400 + self.GPSSec()

    def Print(self):
        print(str(self))