# Copyright © 2021 United States Government as represented by the Administrator of the National Aeronautics and Space Administration.  All Rights Reserved.

from collections.abc import Iterable
import io
import requests
import numpy as np
from scipy.io import loadmat
import zipfile

# Map of battery to url for data
urls = {
    'RW1': "https://ti.arc.nasa.gov/c/27/",
    'RW2': "https://ti.arc.nasa.gov/c/27/",
    'RW3': "https://ti.arc.nasa.gov/c/26/",
    'RW4': "https://ti.arc.nasa.gov/c/26/",
    'RW5': "https://ti.arc.nasa.gov/c/26/",
    'RW6': "https://ti.arc.nasa.gov/c/26/",
    'RW7': "https://ti.arc.nasa.gov/c/27/",
    'RW8': "https://ti.arc.nasa.gov/c/27/",
    'RW9': "https://ti.arc.nasa.gov/c/25/",
    'RW10': "https://ti.arc.nasa.gov/c/25/",
    'RW11': "https://ti.arc.nasa.gov/c/25/",
    'RW12': "https://ti.arc.nasa.gov/c/25/",
    'RW13': "https://ti.arc.nasa.gov/c/31/",
    'RW14': "https://ti.arc.nasa.gov/c/31/",
    'RW15': "https://ti.arc.nasa.gov/c/31/",
    'RW16': "https://ti.arc.nasa.gov/c/31/",
    'RW17': "https://ti.arc.nasa.gov/c/29/",
    'RW18': "https://ti.arc.nasa.gov/c/29/",
    'RW19': "https://ti.arc.nasa.gov/c/29/",
    'RW20': "https://ti.arc.nasa.gov/c/29/",
    'RW21': "https://ti.arc.nasa.gov/c/30/",
    'RW22': "https://ti.arc.nasa.gov/c/30/",
    'RW23': "https://ti.arc.nasa.gov/c/30/",
    'RW24': "https://ti.arc.nasa.gov/c/30/",
    'RW25': "https://ti.arc.nasa.gov/c/28/",
    'RW26': "https://ti.arc.nasa.gov/c/28/",
    'RW27': "https://ti.arc.nasa.gov/c/28/",
    'RW28': "https://ti.arc.nasa.gov/c/28/",
}

cache = {}  # Cache for downloaded data
# Cache is used to prevent files from being downloaded twice

def load_data(batt_id):
    """Loads data from URL using requests"""
    if isinstance(batt_id, Iterable) and not isinstance(batt_id, str):
        return [load_data(id_i) for id_i in batt_id]
    if isinstance(batt_id, int):
        # Convert to string
        batt_id = 'RW' + str(batt_id)

    if batt_id not in urls:
        raise ValueError('Unknown battery ID: {}'.format(batt_id))

    url = urls[batt_id]

    if url not in cache:
        # Download data
        response = requests.get(url, allow_redirects=True)

        # Unzip response
        cache[url] = zipfile.ZipFile(io.BytesIO(response.content))

    f = cache[url].open(f'{cache[url].infolist()[0].filename}Matlab/{batt_id}.mat')

    # Load matlab file
    result = loadmat(f)['data']['step'][0,0]

    # Reformat
    run_details = [
        {
            'type': run_type[0], 
            'desc': desc[0]
        } for (run_type, desc) in zip(result['type'][0], result['comment'][0])
    ]
    result = [
        np.array([
            result[key][0, i][0] for key in ('relativeTime', 'current', 'voltage', 'temperature')
        ], np.float64).T for i in range(result.shape[1])
    ]

    return {'run_details': run_details, 'data': result}
