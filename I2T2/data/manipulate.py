# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_data.manipulate.ipynb (unless otherwise specified).

__all__ = ['dcm2array']

# Cell
from fastscript import call_parse,Param,bool_arg
import numpy as np
import os
import pandas as pd
import pydicom

# Cell
def dcm2array(path_to_dicom_dir=None, sort_by_slice_location=True):
    """
    Transform DICOM data into numpy array.

    Attributes:
        path_to_dicom_dir (str): Path to folder containing all dicom files for one patient
        sort_by_slice_location (bool): Whether to return array ordered by slice location

    Returns:
        pixel_array (arr): Array of pixel data
    ---
    """
    try:
        import gdcm

    except ImportError:
        print("GDCM needs to be installed.")
        print("Try: conda install -c conda-forge gdcm")

    else:
        df = pd.DataFrame()
        df['filename']= os.listdir(path_to_dicom_dir)
        df['pathname']= path_to_dicom_dir + df['filename']

        df['DS']=[pydicom.dcmread(x) for x in df['pathname']]
        df['SOPInstanceUID'] = [x.SOPInstanceUID for x in df['DS']]
        df['SliceLoc'] = [x.InstanceNumber for x in df['DS']]
        df['Pixels'] = [x.pixel_array for x in df['DS']]
        tempo = df['DS'][0]
        im_at = tempo.AcquisitionMatrix, tempo.PixelSpacing

        if sort_by_slice_location == True:
            df = df.sort_values(by=['SliceLoc'])
        pixel_array = np.dstack(np.asarray(df['Pixels']))

        return pixel_array
    return None