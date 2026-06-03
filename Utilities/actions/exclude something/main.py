# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

excludeRegion = [{'pingNumber': 150797}, {'pingNumber': 155313}]

lsss.post('/lsss/regions/exclusion', json=excludeRegion)

# and then remove it. Need to use a parameter to tell LSSS to remove it
# lsss.post('/lsss/regions/exclusion', params={'exclude': False},
#          json=excludeRegion)
