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

class RINEX_302_Object:
    """A Rinex 3.02 object"""
    def __init__(self, file_name):
    
        def split_file(lines):
            """Return a list of header lines and non-header lines from
            a list of Rinex 3.02 lines.
            """
            header_end = 'END OF HEADER'
            header = []
            epochs_lines = []
            for index, line in enumerate(lines):
                header.append(line)
                if header_end in line:
                    break
            for line in lines[index+1:]:
                epochs_lines.append(line)
            epochs = create_epochs_list(epochs_lines)
            epochs_list = []
            for epoch in epochs:
                epochs_list.append(R302_Epoch_Record(epoch))
            return header, epochs_list

        def find_observables(header_lines):
            observables = []
            for line in header_lines:
                if line.startswith('SYS / # / OBS TYPES', 60):
                    observables.append(line[:60])
            observables.sort()
            return observables

        def create_epochs_list(lines):
            """Return a list of epochs (title line, several observations)
            from a given list of lines.
            """
            counter = 0
            epochs = [[]]
            for line in lines:
                if line.startswith('>'):
                    epochs[counter].append(line)
                    counter += 1
                    epochs.append([])
                else:
                    epochs[counter - 1].append(line)
            epochs.pop()
            return epochs

        def create_sys_obs_dict(observables):
            sys_obs = dict()
            for obs in observables:
                sys_obs[obs[0]] = obs[7:].split()
                if not sys_obs[obs[0]]:
                    del sys_obs[obs[0]]
            return sys_obs

        with open(file_name, 'r') as f:
            self.data = f.readlines()

        self.index = len(self.data)
        self.header, self.observations = split_file(self.data)
        self.observables = find_observables(self.header)
        self.systems = [obs[0] for obs in self.observables]
        self.sys_obs_dict = create_sys_obs_dict(self.observables)

    def len(self):
        return len(self.data)
    def sat_sys(self):
        return self.systems
    def satellite_systems(self):
        constellations = []
        for system in self.systems:
            constellations.append(SYSTEM_IDENTIFIERS[system])
        return constellations
    def all_observables(self):
        return self.observables
    def sys_observables(self, system):
        for line in self.observables:
            if line.startswith(system):
                return line[7:60].split()
    def write(self):
        # Return list of header, epoch headers, and observations
        writing = []
        writing.append(self.header)
        for epoch in self.observations:
            writing.append(epoch.write()[0])
            for observation in epoch.write()[1]:
                writing.append(observation)
        return writing

class R302_Epoch_Record:
    """A single epoch of observations in a Rinex 3.02 file"""
    def __init__(self, lines):
        from collections import deque
        deque_data = deque()
        for line in lines:
            deque_data.append(line)
        self.head_line = deque_data.popleft()
        self.data = list(deque_data)
    def flag(self):
        return self.head_line[31]
    def metadata_line(self):
        return self.head_line
    def num_obs_actual(self):
        return str(len(self.data))
    def num_obs_reported(self):
        return self.head_line[33:35]
    def update_num_obs(self, num_obs):
        self.head_line = self.head_line[:33] + str(num_obs) +\
                         self.head_line[35:]
    def update_obs(self, lines):
        self.data = lines
    def time_stamp(self):
        return self.head_line[2:29]
    def write(self):
        return self.head_line, self.data

def clean_epochs(rinex_obj):
    """Checks each epoch's observation lines against header's list of
    GNSS systems and removes observations to unannounced systems.
    """
    cleaned_epochs = []
    for epoch in rinex_obj.observations:
        for observation in epoch.data:
            if observation[0] in rinex_obj.sys_obs_dict:
                cleaned_epochs.append(observation)
        epoch.update_obs(cleaned_epochs)
        cleaned_epochs = []
        epoch.update_num_obs(epoch.num_obs_actual())

def write_new_file(new_file_name, rinex_obj):
    with open(new_file_name, 'w') as f:
        for line in rinex_obj.write():
            f.writelines(line)

def get_rinex_version(file_name):
    with open(file_name, 'r') as f:
        return f.readline()[:12].strip()

def parse_arguments():
    """First positional argument taken as absolute or relative path to file.
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str,
                        help="Relative or absolute path to file to process"
                        )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    import os, sys
    if os.path.isfile(args.file):
        print 'Processing file "{}"...'.format(args.file)
    else:
        raw_input('Error, file not found: {}'.format(args.file))
