# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

r = lsss.get('/lsss/data/ping', params={'time': '2017-10-07T08:02:00Z', 
                                        'minDepth': 50, 'maxDepth': 55,
                                        'sv': True})
print(r['channels'][0]) # the data for channel 0

r = lsss.get('/lsss/data/pings', params={'time': '2017-10-07T08:02:00Z', 
                                        'pingCount': 10})