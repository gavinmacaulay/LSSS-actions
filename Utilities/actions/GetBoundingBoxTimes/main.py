"""
Get the bounding box timestamps.

Do this for all selection regions, put them into the clipboard, along
with a simulate transect number, data directory, and dummy snapshot number
"""
import os
import sys
import pyperclip
from pathlib import Path

sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__))
                                 + '/../../../../include'))
import lsss

# Get the directory where the raw files are
dir = lsss.get('/lsss/survey/config/unit/DataConf/parameter/DataDir')
dir = Path(dir['value'])
# if it ends in '-NMEA', remove that
dirName = dir.name.replace('-NMEA', '')
featureName = dirName[11:]  # remove date from the beginning of the directory name

# Dummy value for snapshot
snapshot = '1'

# Get the selected regions
regions = lsss.get('/lsss/regions/selection')

output = ''

# Build up the output string with a line for each region
for i, r in enumerate(regions):
    # Get information about the region
    details = lsss.get(f'/lsss/regions/region/{r}')

    # Extract the bounding box times
    start_time = details['boundingBox'][0]['time'][0:-1]
    end_time = details['boundingBox'][1]['time'][0:-1]

    # Get the filename at the start and end of each region.
    # This is not directly available from the LSSS API...

    # Set the current echogram point to the start of the region
    lsss.post('/lsss/module/PelagicEchogramModule/current-echogram-point',
              json={'time': start_time+'Z', 'z': 10})
    # Get the current filename from the numerical module
    numerical_data = lsss.get('/lsss/module/NumericalViewModule/data')
    start_filename = numerical_data['file']['name']

    # And repeat for the end of the region
    lsss.post('/lsss/module/PelagicEchogramModule/current-echogram-point',
              json={'time': end_time+'Z', 'z': 10})
    numerical_data = lsss.get('/lsss/module/NumericalViewModule/data')
    end_filename = numerical_data['file']['name']

    # Then build the csv line to go into the clipboard
    output += f'{dirName},{featureName},{snapshot},{i+1},{start_time},{end_time},'\
        f'{start_filename},{end_filename}\n'

# copy to clipboard without the trailing newline
pyperclip.copy(output[0:-1])
