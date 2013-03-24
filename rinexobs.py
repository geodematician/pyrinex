"""
Module containing RinexObservation object.
"""
import logging
from datetime import datetime
from rinex import Rinex
from epoch import Epoch
from obs import Observation, Observations, ObsType


class ObsHeader:
    """
    Rinex Header elements.
    """
    def __init__(self, data):
        """
        *data* is supposed to be a list of text lines.
        """
        self.GPSObsTypes = [ ]
        for l in data:
            self.parseline(l[:60], l[59:])

    def todict(self):
        """
        Return a dictionary of values.
        """
        keyvalues = [
            'Version', 'FileType', 'SatelliteSystem', 'Program', 'FileAgency',
            'CreationDateTime', 'MarkerName', 'MarkerNumber', 'MarkerType',
            'Observer', 'ObserverAgency', 'ReceiverNumber', 'ReceiverType',
            'ReceiverVersion', 'AntennaNumber', 'AntennaType', 'AntennaHeight',
            'AntennaEccentricityE', 'AntennaEccentricityN', 'GPSObsTypes',
            'ApproxX', 'ApproxY', 'ApproxZ',
        ]
        ret = { }
        for k in keyvalues:
            try:
                exec 'ret[k] = self.%s' % k
            except:
                pass
        return ret

    def parseline(self, data, label):
        """
        Parses and adds data to Header from a Rinex line.
        *data* is from the begging to the 60'th column;
        *label* is from the 61's column to the end.
        """
        label = label.strip()
        if label == "RINEX VERSION / TYPE":
            self.Version = float(data[0:20])
            self.FileType = data[20]
            self.SatelliteSystem = data[40]
        elif label == "PGM / RUN BY / DATE":
            self.Program = data[0:20].strip()
            self.FileAgency = data[20:40].strip()
            tmp = data[40:].strip()
            self.CreationDateTime = datetime.strptime(tmp, '%d-%b-%y %H:%M %Z')
            del tmp
        elif label == "MARKER NAME":
            self.MarkerName = data.strip()
        elif label == "MARKER NUMBER":
            self.MarkerNumber = data[0:20].strip()
        elif label == "MARKER TYPE":
            tmp = data[0:20].strip()
            if tmp == "GEODETIC":
                self.MarkerType = 1
            elif tmp == "NON_GEODETIC":
                self.MarkerType = 2
            else:
                self.MarkerType = 0
            del tmp
        elif label == "OBSERVER / AGENCY":
            self.Observer = data[0:20].strip()
            self.ObserverAgency = data[20:].strip()
        elif label == "REC # / TYPE / VERS":
            self.ReceiverNumber = data[0:20].strip()
            self.ReceiverType = data[0:20].strip()
            self.ReceiverVersion = data[0:20].strip()
        elif label == "ANT # / TYPE":
            self.AntennaNumber = data[0:20].strip()
            self.AntennaType = data[20:40].strip()
        elif label == "ANTENNA: DELTA H/E/N":
            self.AntennaHeight = float(data[0:14])
            self.AntennaEccentricityE = float(data[14:28])
            self.AntennaEccentricityN = float(data[28:])
        elif label == "SYS / # / OBS TYPES":
            satsys = str(data[0])
            obsno = int(data[3:6])
            if satsys == 'G':
                desc_list = data[6:].split()
                for i in range(0,obsno):
                    self.GPSObsTypes.append( ObsType(desc_list[i]) )
            del satsys, obsno
        elif label == 'TIME OF FIRST OBS':
            self.FirstObs = Epoch(
                year = int(data[0:6]),
                month = int(data[6:12]),
                day = int(data[12:18]),
                hour = int(data[18:24]),
                minute = int(data[24:30]),
                second = float(data[30:43]),
                timesystem = str(data[43:])
                )
        elif label == 'TIME OF LAST OBS':
            self.LastObs = Epoch(
                year = int(data[0:6]),
                month = int(data[6:12]),
                day = int(data[12:18]),
                hour = int(data[18:24]),
                minute = int(data[24:30]),
                second = float(data[30:43]),
                timesystem = str(data[43:])
                )
        elif label == "APPROX POSITION XYZ":
            split = data.split()
            self.ApproxX = float(split[0])
            self.ApproxY = float(split[1])
            self.ApproxZ = float(split[2])
            del split
    def headerterminator(self):
        """
        Output the header terminator for Rinex3 ("END OF HEADER").
        """
        t = '%60sEND OF HEADER%6s' % ('', '')
        return t
    
class RinexObservation(Rinex):
    """
    Class containing RINEX Observation file.
    """
    def _getheader(self):
        """
        Read header.
        """
        self.header = ObsHeader(self.headerlines)
        if len(self.header.GPSObsTypes) <= 0:
            logging.error('No valid observation types found in %s header.' % self.filename)
            #TODO: throw exception
            return None
    def _getcontents(self):
        """
        Read observations.
        """
        self.observations = Observations()
        self.observations.fromRinex(self.lines, self.header.GPSObsTypes)
    def _extrainit(self):
        """
        Nothing to do here.
        """
        pass
    def export(self, filename):
        """
        Export the Rinex object to *filename*. The format is Rinex3.
        """
        try:
            f = open(filename, 'w')
        except:
            # throw my own exception
            return False
        # write header
        #TODO: header export implementation
        self.writelines(self.headerlines, f)
        self.writelines( [ self.header.headerterminator() ], f)
        # write observations
        #for O in self.observations:
        #    l = [ O.obslist[0].exportRinexHeader() ]
        #    self.writelines(l, f)
        f.close()
        return True
    