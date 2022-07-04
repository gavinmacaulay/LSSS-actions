# --- Begin generated header ---
import os
import sys
sys.path.append(os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../include'))
import lsss
# --- End generated header ---

# Code to get an echogram from LSSS using the LSSS API. 
#
# Sets the echogram up to be suitable for publications.
# Also does the same with the map.
#
# If you are running LSSS on a Windows computer and using the Anaconda python
# distribution, you need to create a file called 'conda_python.bat', which 
# has a single line in it (change the path to suit your installation): 
#  c:\users\gavin\anaconda3\Scripts\conda.exe run -n base python %*
# and configure LSSS to use that script when running python actions.

import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageOps
import requests
import shutil

# Need to have a UI to allow the user to set this.
default_save_dir = Path.home()

def saveEchogram(save_dir=default_save_dir, figure_label='test', image_dpi=300):

    doEchogram = True
    doMap = False
    
    # sometimes save_dir is just a string
    save_dir = Path(save_dir)
    
    # echogram overlays to keep on
    overlaysToKeep = ['DepthMarkerOverlay', 'VerticalLineOverlay', 'EchogramImageOverlay', 'RegionDisplayOverlay']
    # and same for the map
    mapOverlaysToKeep = ['BackgroundMapOverlay', 'LatLonOverlay', 'SurveyLineOverlay']
    
    # Settings to change
    depth_marker_font_size = 20 # [points]
    vertical_line_marker_font_size = 20 # [points]
    vertical_line_text_type = 'Distance' # Distance, Time, or Ping
    
    map_axis_font_size = 20 # [points]
    
    # applies to both echogram and the map
    image_width = 90 # [mm]
    
    # output goes here
    echogram_image_file = save_dir.joinpath(f'Figure_{figure_label}_echogram.png')
    map_image_file = save_dir.joinpath(f'Figure_{figure_label}_map.png')
    
    ########################################################
    # Setup up the echogram
    if doEchogram:
        image_width_pixels = int(image_width / 25.4 * image_dpi) # [pixels]
        
        # Get the echogram config
        d = lsss.get('/lsss/module/PelagicEchogramModule/config/xml')
        
        # and turn off everything we don't want
        root = ET.fromstring(d)
        
        for child in root[0]:
            if child.attrib['name'] in overlaysToKeep:
                child.attrib['enabled'] = 'true'
            else:
                child.attrib['enabled'] = 'false'
        
        # Put our altered config to lsss
        lsss.post('/lsss/module/PelagicEchogramModule/config/xml', data=ET.tostring(root))
        
        # and adjust some specific things
        p = '/lsss/module/PelagicEchogramModule/overlay/'
        lsss.post(p+'DepthMarkerOverlay/config/parameter/FontSize', json={'value': depth_marker_font_size})
        lsss.post(p+'VerticalLineOverlay/config/parameter/FontSize', json={'value': vertical_line_marker_font_size})
        
        lsss.post(p+'VerticalLineOverlay/config/parameter/Text', json={'value': vertical_line_text_type})
        lsss.post(p+'VerticalLineOverlay/config/parameter/ShowSa', json={'value': False})
        
        lsss.post(p+'RegionDisplayOverlay/config/parameter/ShowConnectors', json={'value': False})
        
        #################################################
        # get the screen grab of the echogram
        echogram_url = lsss.baseUrl + '/lsss/module/PelagicEchogramModule/image'
        eg_img = Image.open(requests.get(echogram_url, stream=True).raw)
        # trim off the vertical scroll bar, which is 16 pixels wide
        border = (0, 0, 16, 0) # pixels to remove off the left, top, right, bottom edges
        eg_img = ImageOps.crop(eg_img, border)
        
        # get the colourbar
        colourbar_url = lsss.baseUrl + '/lsss/module/ColorBarModule/image'
        cb_img = Image.open(requests.get(colourbar_url, stream=True).raw)
        # trim off the threshold labels at the bottom, each of which is 22 pixels high
        v = lsss.get('/lsss/survey/config/unit/SurveyMiscConf/parameter/AdditionalLowerThresholds')
        num_labels = 1 + len(v['value'].split(','))
        cb_img = ImageOps.crop(cb_img, (0, 0, 0, 22*num_labels))
        
        # and add the colourbar to the right hand side of the echogram
        width = eg_img.size[0] + cb_img.size[0]
        height = max(eg_img.size[1], cb_img.size[1])
        
        line_width = 2 # [pixels]
        
        img = Image.new('RGB', (width+line_width, height), color='white')
        img.paste(eg_img, (0,0))
        img.paste(cb_img, (eg_img.size[0]+line_width, 0))
        
        # now resample the image and give a higher dpi, as often asked for by journals.
        img = img.resize((image_width_pixels, int(img.size[1] * image_width_pixels / img.size[0])), Image.BICUBIC)
        img.save(echogram_image_file, dpi=(image_dpi, image_dpi), optimize=True)
    
    ###################################################
    # Do the map figure
    
    if doEchogram:
        
        # Get the map config
        d = lsss.get('/lsss/module/MapModule/config/xml')
        
        # and turn off everything we don't want
        root = ET.fromstring(d)
        
        for child in root[1]:
            if child.attrib['name'] in mapOverlaysToKeep:
                child.attrib['enabled'] = 'true'
            else:
                child.attrib['enabled'] = 'false'
        
        # Put our altered config to lsss
        lsss.post('/lsss/module/MapModule/config/xml', data=ET.tostring(root))
        
        # and adjust some specific things
        p = '/lsss/module/MapModule/overlay/'
        lsss.post(p+'LatLonOverlay/config/parameter/FontSize', json={'value': map_axis_font_size})
        
        map_url = lsss.baseUrl + '/lsss/module/MapModule/image'
        map_img = Image.open(requests.get(map_url, stream=True).raw)
        map_img = map_img.resize((image_width_pixels, int(map_img.size[1] * image_width_pixels / map_img.size[0])), Image.BICUBIC)
        map_img.save(map_image_file, dpi=(image_dpi, image_dpi), optimize=True)
    
if __name__ == "__main__":
    
    #raise Exception(f'{lsss.input}')
    saveEchogram(**lsss.input)
    
