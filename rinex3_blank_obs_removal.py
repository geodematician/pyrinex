#! C:\Anaconda\python.exe

"""Remove blank observations from satellite systems unclaimed in the
header in a given RINEX 3 file.
"""

# python 2.7.5

__author__ = 'APK'

SYSTEM_IDENTIFIERS = {'G':'GPS',
                      'R':'GLONASS',
                      'S':'SBAS payload',
                      'E':'Galileo',
                      'C':'BeiDou',
                      'J':'QZSS'
                     }

class R3_Header:
    """A header for a Rinex 3 file"""
    def __init__(self, lines):
        def find_observables():
            observables = []
            for line in self.data:
                if line.startswith('SYS / # / OBS TYPES', 60):
                    observables.append(line[:60])
            return observables

        def satellite_systems():
            satellite_systems = []
            for line in self.all_observables:
                satellite_systems.append(line[0])
            return satellite_systems

        self.data = []
        self.index = len(self.data)
        for line in lines:
            self.data.append(line)
        self.all_observables = find_observables()
        self.systems = satellite_systems()

    def len(self):
        return len(self.data)
    def write(self):
        return self.data
    def sat_sys(self):
        return self.systems
    def satellite_systems(self):
        constellations = []
        for system in self.systems:
            constellations.append(SYSTEM_IDENTIFIERS[system])
        return constellations
    def all_observables(self):
        return self.all_observables
    def sys_observables(self, system):
        for line in self.all_observables:
            if line.startswith(system):
                return line[7:60].split()

# class R3_Observations:
    # """The observations in a Rinex 3 file"""
    # def num_epochs(self):
        # counter = 0
        # for line in self.data:
            # if line[0] == '>':
                # counter += 1
        # return counter

class R3_Epoch:
    """A single epoch of observations in a Rinex 3 file"""
    def __init__(self, lines):
        self.data = []
        for line in lines:
            self.data.append(line)
    def len(self):
        return len(self.data)
    def epoch_header(self):
        if self.data[0][0] == '>':
            return self.data[0]
        else:
            print 'Error in Epoch class header.'
    def name(self):
        return self.data[0][2:29]
    def flag(self):
        return self.data[0][31]
    def num_sats(self):
        return self.data[0][33:35]
    def write(self):
        return self.data

class R3_Single_Obs:
    """A single observation in Rinex 3 format"""
    def __init__(self, line):
        self.data = line
    def len(self):
        return len(self.data)
    def sat_sys(self):
        return self.data[0]
    def write(self):
        return self.data

def parse_arguments():
    """First positional argument taken as absolute or relative path to file.
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str,
                        help="Relative or absolute path to file to process"
                        )
    return parser.parse_args()

def split_file(file_name):
    """Return a header object and an epochs object from a Rinex 3 file
    object.
    """
    header_end = 'END OF HEADER'
    header_lines = []
    epochs_lines = []
    with open(file_name, 'r') as f:
        lines = f.readlines()
    for index, line in enumerate(lines):
        header_lines.append(line)
        if header_end in line:
            header_end_line = index
            break
    for line in lines[header_end_line+1:]:
        epochs_lines.append(line)
    epochs_list = create_epochs_list(epochs_lines)
    epochs = []
    for epoch in epochs_list:
        epochs.append(R3_Epoch(epoch))
    return R3_Header(header_lines), epochs
    # Gah, not the best...
    # TODO: need to associate the Header object with each Epoch object somehow

###############################################################################
# # # Interesting approach for computing efficiency, but incompletely
# # # implemented for the moment:
# def split_file(file_name):
    # """Return a header object and an epochs object from a Rinex 3 file
    # object.
    # """
    # header_end = 'END OF HEADER'
    # header_lines = []
    # epochs_lines = []
    # # Open the data file
    # with open(file_name, 'r') as f:
        # while True:
            # # Read each line one at a time
            # read_line = f.readline()
            # if not read_line:
                # break
            # # Put everything into the header...
            # header_lines.append(read_line)
            # # ...until END OF HEADER is reached
            # if header_end in read_line:
                # # f.tell() method returns current location in file
                # # in bytes from the beginning of the file.
                # header_end_index = f.tell()
                # break
        # # Go to the end of the header
        # f.seek(header_end_index)
        # epoch_counter = 0
        # epoch_string = ''
        # while True:
            # read_line = f.readline()
            # if line.startswith('>'):
                # if epoch_string:
                    # epochs_list[epoch_counter].append(epoch_string)
                    # epoch_string = ''
                # epoch_string = line
                # epoch_counter += 1
                # epochs_list.append([])
            # elif line:
                # epoch_string += line
                # # counter += 1
            # else:
                # epochs_list[epoch_counter].append(epoch_string)
                # break
        # return R3_Header(header_lines), R3_Observations(epochs_list)
###############################################################################

def create_epochs_list(lines):
    """Return a list of epochs (header, several observations) from a
    given list of lines.
    """
    counter = 0
    epochs_list = [[]]
    for line in lines:
        if line.startswith('>'):
            epochs_list[counter].append(line)
            counter += 1
            epochs_list.append([])
        else:
            epochs_list[counter - 1].append(line)
    epochs_list.pop()
    return epochs_list

if __name__ == '__main__':
    args = parse_arguments()
    import os, sys
    if os.path.isfile(args.file):
        print 'Processing file "{}"...'.format(args.file)
    else:
        raw_input('Error, file not found: {}'.format(args.file))


    