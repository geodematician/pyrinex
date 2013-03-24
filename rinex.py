"""
Rinex inheritable object container.
"""

import logging

class Rinex:
    """
    Generic Rinex file class. RinexObservation and RinexNavigation are derived
    from this.
    """
    def __init__(self, filename = ''):
        """
        If *filename* is provided, contents will be read. The type of file
        (navigation/observation) is determined via the file name.
        """
        def readlines(fname):
            """
            Return list of strings containing *fname* file's lines.
            """
            f = open(fname, 'r')
            r = f.read().split('\n')
            f.close()
            for l in r:
                l = l.strip('\n')
            return r
        def getheader(lines):
            """
            Return lines containing header info from a list of *lines*
            """
            for i in range(0, len(lines)):
                if 'END OF HEADER' in lines[i].strip():
                    return lines[0:i]
            return [ ]
        self.filename = filename
        if filename == '':
            # just initialize class
            logging.debug('Starting empty Rinex file.')
        else:
            # reading file
            self.lines = readlines(filename)
            # getting header
            self.headerlines = getheader(self.lines)
            if len(self.headerlines) <= 0:
                logging.error('No valid header terminator found for %s' % self.filename)
                #TODO: throw exception
                return None
            # removing headers
            self.lines = self.lines[ len(self.headerlines) + 1: ]
            # reading header contents
            self._getheader()
            # getting data
            self._getcontents()
            # extra init stuff
            self._extrainit()
    
    def writelines(self, lines, fileobject, eolcheck = True):
        """
        Write list of *lines* to *fileobject*.
        *fileobject* is a file open for write. It is your responsability to
        open/close the file.
        If *eolcheck* is True, add \n as requiered.
        """
        for l in lines:
            if eolcheck and len(l) > 0:
                if l[-1] != '\n':
                    l += '\n'
            fileobject.write(l)
    
    def __extrainit(self):
        """
        If you overload this, you can do more init stuff.
        """
        return
    
    def _getcontents(seld):
        """
        You have to overload this function to provide contents reading.
        """
        #TODO: throw exception
        pass
    
    def _getheader(self):
        """
        You have to overload this function to provide header functionality.
        """
        #TODO: throw exception
        pass