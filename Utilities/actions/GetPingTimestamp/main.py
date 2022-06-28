# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

import pyperclip

# When activated with the cursor in the echogram, copies the ping timestamp

d = lsss.get('/lsss/module/NumericalViewModule/data')

dt = d['ping']['time']
# Remove trailing timezone (Z)
dt = dt[0:-1]

pyperclip.copy(dt)

