# python 2.7.5

""" Some rinex utilities"""

__author__ = 'Andrew P. Kubiak'

# "Global" constants
SYSTEM_IDENTIFIERS = {'G':'GPS',
                      'R':'GLONASS',
                      'S':'SBAS payload',
                      'E':'Galileo',
                      'C':'BeiDou',
                      'J':'QZSS'
                     }

def get_rinex_version(file_name):
    """Return string denoting RINEX version number label from a file path."""
    # Open the file, read the first 9 bits, strip the white space and
    # return result. Well-formed RINEX returns the 1-4 character version.
    with open(file_name, 'r') as f:
        return f.readline(9).strip()

def split_header_data(lines):
    """Return two lists from one list, splitting on 'END OF HEADER'."""
    # Either Rinex 2 or Rinex 3 (since both use 'END OF HEADER')
    header = []
    epochs = []
    if type(lines) != list:
        err = 'Error : function "split_header_data" in rinexlib.py '
        err += 'requires a list as a parameter.'
        return [err], [err]
    for index, line in enumerate(lines):
        header.append(line)
        if 'END OF HEADER' in line:
            break
        elif 'TIME OF FIRST OBS' in line:
            time_system = line[48:51]
            start_time_index = index

    for line in lines[index+1:]:
        epochs.append(line)
    ## TODO: get time of last obs from bottom of epochs list and add it to the
    ## header
    for line in reversed(epochs):
        if line.startswith('>'):
            endtime = line
            break
    time_of_last = write_end_time(endtime, time_system)
    header.insert(start_time_index+1, time_of_last)
    return header, epochs

def write_end_time(epoch_label_string, time_frame):
    """Return properly formed Rinex 3 string from given epoch time tag"""
    #'  2013    10     8     0     0    0.0000000     GPS         TIME OF FIRST OBS'
    tag = epoch_label_string.split()[1:7]
    tag[-1] = float(tag[-1])
    line = '  {tag[0]}    {tag[1]: >2}    {tag[2]: >2}    {tag[3]: >2}    {tag[4]: >2}    {tag[5]: >f}     {time_frame}         TIME OF LAST OBS\n'.format(tag=tag, time_frame=time_frame)
    return line

def get_R3_observables(header_lines):
    """Return {constellation : observable} dictionary and list of
    all possible observables from header list
    """
    # RINEX 3 ONLY!
    
    from datetime import datetime
    
    # Split up by white space each line that has 'SYS / # / OBS TYPES'
    # at the 61st character to the list, then add the pieces to the
    # blank list 'sys_obs'
    sys_obs = []
    fmt = '%Y %m %d %H %M %S.%f0'
    for line in header_lines:
        if line.startswith('SYS / # / OBS TYPES', 60):
            sys_obs.append(line[:60].split())
        elif line.startswith('INTERVAL', 60):
            interval = line.split()[0]
        elif line.startswith('TIME OF FIRST OBS', 60):
            start_time = line[:60].split()
            time_system = start_time.pop()
            start_time = datetime.strptime(' '.join(start_time), fmt)

    # Create a list of strings representing each observable possible in file
    net_observables = []
    for line in sys_obs:
        for observable in line[2:]:
            if not observable in net_observables:
                net_observables.append(observable)
    net_observables.sort()

    multiindex_2d = get_R3_multiindex(sys_obs, net_observables)

    # Create a dictionary and fill it with the satellite system char
    # as the key, the list of observables as the value, return the dict
    obs_by_sys = {}
    for system in sys_obs:
        obs_by_sys[system[0]] = system[2:]
    return obs_by_sys, net_observables, multiindex_2d, [start_time, interval]

def get_R3_multiindex(sys_obs, net_observables):
    """Return a tuple from two lists of lines"""
    systems = []
    for line in sys_obs:
        systems.append(line[0])
    systems.sort()

    index = [[],[]]
    for system in systems:
        for observable in net_observables:
            index[0].append(system)
            index[1].append(observable)
    return index

def get_R3_epochs(lines):
    """Return a list of epochs (metadata, data) from a given list of lines"""
    # RINEX 3 ONLY!
    from datetime import datetime
    
    counter = 0
    epochs = [[]]
    # indices = []
    # fmt = '%Y %m %d %H %M %S.%f0'
    for line in lines:
        if line.startswith('>'):
            epochs[counter].append(line)
            counter += 1
            epochs.append([])
            # indices.append(datetime.strptime(' '.join(line[2:29].split()), fmt))
        else:
            epochs[counter - 1].append(line)
    epochs.pop()
    return epochs #, indices
