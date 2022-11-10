# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

from pathlib import Path
import pandas as pd
from io import StringIO


# This action exports TS detections for all regions that have been labelled.
# The TS from each unique region label are exported and appended to a 
# single pandas dataframe, which is saved as an HDF5 file in the
# LSSS TS export directory.

# Get a list of all labelled regions
labels = lsss.get('/lsss/regions/label')

# Get TS export directory
ts_directory = Path(lsss.get('/lsss/export/TSExport/config/parameter/Directory')['value'])
ts_filename = ts_directory.joinpath(f'ts-export.h5')
ts_filename.unlink(missing_ok=True)

all_ts = pd.DataFrame([])

# Loop over all region labels
for l in labels:
    
    # Get region id for the current label. Probably only works with one 
    # region per unique label!!!!
    criteria = {'all': True, 'labels': f'["{l}"]'}
    r = lsss.get('/lsss/regions/region', params=criteria)
    region_id = r[0]['id']
    
    # Select the region
    lsss.post('/lsss/regions/selection', json={'ids': [region_id]})
    
    # Export TS data from that region
    ts = lsss.get('/lsss/export/TSExport')    

    # Pick out header info which could be stored somewhere (but isn't at the moment)
    ts_header = [x[2:] for x in ts.split('\r\n') if x.startswith('#') and len(x) > 1]
    
    # Read the ts csv data into a Pandas dataframe and append to previous label exports
    df = pd.read_csv(StringIO(ts), comment='#')
    df['station'] = l
    all_ts = pd.concat([all_ts, df])

# save dataframe to a file
all_ts.to_hdf(ts_filename, key='ts', mode='w')
        
