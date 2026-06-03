# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

for z in [5,6,7,8,9,12]:
    line = [{"time": "2025-06-07T00:07:00Z", "z": z},
            {"time": "2025-06-07T00:10:00Z", "z": z}]
    lsss.post('/lsss/module/PelagicEchogramModule/horizontal-layer-boundary',
              json=line)

