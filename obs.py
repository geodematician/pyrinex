"""
Contains Observation and Observations classes.
"""
__author__ = 'Costin Gamenț'
__email__ = 'costin.gament@gmail.com'
__license__ = 'GPL'

from epoch import Epoch

class ObsType:
    """
    Observation type.
    """
    
    def __init__(self, s = "0000"):
        """
        *s* is the observation type text from Rinex3.
        """
        self.SatelliteSystem = 'G'
        if len(s) > 4 or len(s) < 3:
            #TODO: raise exception
            return -1
        elif len(s) == 4:
            self.SatelliteSystem = s[0]
            s = s[1:]
        self.ObservationType = s[0]
        self.Band = int(s[1])
        self.Attribute = s[2]
        
    def __repr__(self):
        r = str(self.SatelliteSystem)
        r += str(self.ObservationType)
        r += str(self.Band)
        r += str(self.Attribute)
        return r
    
    def __eq__(self, o):
        """
        Equality.
        """
        return ((self.SatelliteSystem==o.SatelliteSystem) and
            (self.ObservationType==o.ObservationType) and
            (self.Band==o.Band) and (self.Attribute == o.Attribute))
    
    def ToStr(self):
        return self.ObservationType+str(self.Band)+self.Attribute

class Observation:
    """
    Rinex observation -- one epoch, one satellite.
    """
    
    def __init__(self, obtype, epoch, System, Satellite, Value, EpochFlag,
                 ClockOffset, SignalStrength, LossOfLock = None):
        """
        """
        self.obtype = obtype
        self.epoch = epoch
        self.System = System
        self.Satellite = Satellite
        self.Value = Value
        self.SignalStrength = SignalStrength
        self.LossOfLock = LossOfLock
        self.EpochFlag = EpochFlag
        self.ClockOffset = ClockOffset
    
    def Print(self):
        """
        Nice output.
        """
        self.epoch.Print()
        #for t in self.values:
        #    print '%s%02d [%s]: %f' % (self.values[t]['System'], self.values[t]['Satellite'], t, self.values[t]['Value'])
        print '%s%02d: %f' % (self.System, self.Satellite, self.Value)
    def exportRinexHeader(self):
        """
        Returns a pair of lines containing Rinex3 format epoch and data.
        """
        e = '> %4d %2d %2d %2d %2d %2.7f %2d %2d' % (
            self.epoch.Year,
            self.epoch.Month,
            self.epoch.Day,
            self.epoch.Hour,
            self.epoch.Minute,
            self.epoch.Second,
            self.EpochFlag,
            self.ClockOffset
            )
        return e        

class Observations:
    """
    A collection of Observation objects.
    """
    
    def __init__(self, obs_list = [ ]):
        """
        Init the class with the list of observations provided.
        """
        self.obslist = obs_list
    
    def fromRinex(self, lines, obstypes):
        """
        Add the lines to the observations list and look for *obstypes*
        observation types. Input format is Rinex3.
        """
        for l in lines:
            if l != '':
                if l.strip()[0] == '>':
                    headline = l
                else:
                    self.obslist.extend(
                        self._lineFromRinex(headline, l, obstypes)
                    )
    
    def _lineFromRinex(self, obshead, obs, obstypes):
        """
        Add lines from Rinex files.
        *obshead* is the "header" of the observation group ('>' line with epoch)
        *obs* is the actual observation for one satellite
        *obstypes* is a list of ObsType containing what we want to read
        """
        retobs = [ ]
        tokens = obshead.split()
        epoch = Epoch(
            year = int(tokens[1]),
            month = int(tokens[2]),
            day = int(tokens[3]),
            hour = int(tokens[4]),
            minute = int(tokens[5]),
            second = float(tokens[6]),
            )
        EpochFlag = int(tokens[7])
        ClockOffset = float(0)
        if len(tokens) > 8:
            #TODO: is this really Clock Offset?
            ClockOffset = float(tokens[8])
        
        self.values = { }
        
        k = 3
        for t in obstypes:
            if len(obs[k:k+16])<16:
                #print("Warning: %s%d%s for %s%s is missing." %(i.ObservationType, i.Band, i.Attribute, i.SatelliteSystem, line[1:3]))
                break
            System = obs[0]
            Satellite = int(obs[1:3])
            Value = float(obs[k:k+14])
            if obs[k+14] != ' ':
                LossOfLock = int(obs[k+14])
            SignalStrength = int(obs[k+15])
            k=k+16
            #TODO: do something about LossOfLock
            retobs.append(
                Observation(t, epoch, System, Satellite, Value, EpochFlag,
                            ClockOffset, SignalStrength)
                )
        return retobs
    
    def getSatellite(self, sat, sys = 'G'):
        """
        Return all the observations from satellite *sat*.
        """
        r = [ ]
        for o in self.obslist:
            for t in o.values:
                if o.values[t]['Satellite'] == int(sat) and o.values[t]['System'] == sys:
                    r.append(o)
        return r
    
    def getEpoch(self, epoch):
        """
        Return all the entries on epoch.
        """
        r = [ ]
        for o in self.obslist:
            if o.epoch == epoch:
                r.append(o)
        return r
    
    def getGroups(self):
        """
        Return a key-value pair with the key as the epoch and the value a list
        of satellites (Rinex-style)
        """
        ret = { }
        for i in self.obslist:
            try:
                ret[str(i.epoch)]
            except:
                ret[str(i.epoch)] = [ ]
            ret[str(i.epoch)].append(i)
                
        return ret
    
