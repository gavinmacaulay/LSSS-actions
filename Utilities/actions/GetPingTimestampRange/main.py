# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

import pyperclip

# When activated with the cursor in the echogram, copies the ping timestamp and range

d = lsss.get('/lsss/module/PelagicEchogramModule/current-echogram-point')

# Remove trailing timezone (Z)
dt = d['time'][0:-1]

r = d['z']

pyperclip.copy(f'{dt},{r}')
