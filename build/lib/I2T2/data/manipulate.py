# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_data.manipulate.ipynb (unless otherwise specified).

__all__ = ['dcm2array', 'crop', 'pad', 'resample', 'resample_by']

# Cell
from fastscript import call_parse,Param,bool_arg
from scipy import ndimage

import math
import matplotlib.pyplot as plt
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

# Cell
def crop(image_array, final_dims_in_pixels, zero_fill_mode=False):
    """
    Crop image data to final_dim_in_pixels

    Attributes:
        image_array (float, np.array): 3D numpy array containing image data
        final_dim_in_pixels    (list): Final number of pixels in xyz dimensions. Example: [256, 256, 80]
        zero_fill_mode         (bool): If True, returns array filled with zeros

    Returns:
        cropped_image_array (arr): Resized array containing image data
    """

    dims = len(final_dims_in_pixels)
    original_dims_in_pixels = [image_array.shape[d] for d in range(len(image_array.shape))]

    # test if input and output dimensions match
    if dims != len(original_dims_in_pixels):
        raise ValueError("Dimensions of the input (" + str(len(image_array.shape)) +
                        ") do not match those of output (" + str(len(final_dims_in_pixels))+ ")")

    # test if desired final image is smaller than original
    if any(final_dims_in_pixels[d] > original_dims_in_pixels[d] for d in range(dims)):
        raise ValueError("Final dimensions are larger than original. Did you mean to `pad`?")


    cropped_image_array = np.zeros(image_array.shape)
    new_first_pixel = [0 for i in range(dims)]
    new_last_pixel = [0 for i in range(dims)]

    for dim in range(dims):
        new_first_pixel[dim] = int(math.floor((original_dims_in_pixels[dim] - final_dims_in_pixels[dim]) / 2))
        new_last_pixel[dim] = new_first_pixel[dim] + final_dims_in_pixels[dim]

    #for 2D:
    if dims == 2:
        cropped_image_array = image_array[new_first_pixel[0] : new_last_pixel[0],
                                          new_first_pixel[1] : new_last_pixel[1]]
    elif dims == 3:
        cropped_image_array = image_array[new_first_pixel[0] : new_last_pixel[0],
                                          new_first_pixel[1] : new_last_pixel[1],
                                          new_first_pixel[2] : new_last_pixel[2]]
    if zero_fill_mode:
        cropped_image_array = cropped_image_array*0.

    return(cropped_image_array)

# Cell
def pad(image_array, final_dims_in_pixels, zero_fill_mode=False):
    """
    Pad image data to final_dim_in_pixels

    Attributes:
        image_array (float, np.array): 3D numpy array containing image data
        final_dim_in_pixels    (list): Final number of pixels in xyz dimensions. Example: [256, 256, 80]
        zero_fill_mode         (bool): If True, returns array filled with zeros

    Returns:
        padded_image_array (arr): Resized array containing image data
    """

    dims = len(final_dims_in_pixels)
    original_dims_in_pixels = [image_array.shape[d] for d in range(len(image_array.shape))]

    # test if input and output dimensions match
    if dims != len(original_dims_in_pixels):
        raise ValueError("Dimensions of the input (" + str(len(image_array.shape)) +
                        ") do not match those of output (" + str(len(final_dims_in_pixels))+ ")")

    # test if desired final image is larger than original
    if any(final_dims_in_pixels[d] < original_dims_in_pixels[d] for d in range(dims)):
        raise ValueError("Final dimensions are smaller than original. Did you mean to `crop`?")

    padded_image_array = np.zeros(final_dims_in_pixels)
    new_first_image_pixel = [0 for i in range(dims)]
    new_last_image_pixel = [0 for i in range(dims)]

    for dim in range(dims):
        new_first_image_pixel[dim] = int(math.floor((final_dims_in_pixels[dim] - original_dims_in_pixels[dim]) / 2))
        new_last_image_pixel[dim] = new_first_image_pixel[dim] + original_dims_in_pixels[dim]

    #for 2D:
    if dims == 2:
        padded_image_array [new_first_image_pixel[0] : new_last_image_pixel[0],
                            new_first_image_pixel[1] : new_last_image_pixel[1]] = image_array
    elif dims == 3:
        padded_image_array [new_first_image_pixel[0] : new_last_image_pixel[0],
                            new_first_image_pixel[1] : new_last_image_pixel[1],
                            new_first_image_pixel[2] : new_last_image_pixel[2]] = image_array
    if zero_fill_mode:
        padded_image_array = padded_image_array*0.

    return(padded_image_array)

# Cell
def resample(image_array, goal_pixel_dims_list, is_seg=False):
    """
    Resamples `image` to new resolution according to a compression factor using scipy's `ndimage`

    Attributes:
        image_array (float, np.array) : Array of voxel values for image
        goal_pixel_dims_list (list)   : Goals for dimensions of final image (e.g. [256, 256, 128])
        is_seg (bool)                 : Whether or not the image is a segmentation (i.e. pixel values are int)

    Returns:
        resampled_image_array (arr): Resampled array containing image data
    """
    # if dealing with segmentation images, do not interpolate
    # this is done by choosing interpolation order == 0
    order = 0 if is_seg == True else 3

    original_dims_in_pixels = [image_array.shape[d] for d in range(len(image_array.shape))]
    compression_list = [goal_pixel_dims_list[d] / original_dims_in_pixels[d] for d in range(len(image_array.shape))]

    if (is_seg):
        resized_image = ndimage.interpolation.zoom(image_array, zoom=compression_list, order=order, cval=0)
        return resized_image
    else:
        resized_image = ndimage.interpolation.zoom(image_array, zoom=compression_list, order=order, cval=0)
        return resized_image

# Cell
def resample_by(image_array, compression_factor_list, is_seg=False):
    """
    Resamples `image` to new resolution according to a compression factor using scipy's `ndimage`

    Attributes:
        image_array (float, np.array)  : Array of voxel values for image
        compression_factor_list (list) : Compression or expansino factor (e.g. [0.1, 10.0, 1.0])
        is_seg (bool)                  : Whether or not the image is a segmentation (i.e. pixel values are int)

    Returns:
        resampled_image_array (arr): Resampled array containing image data
    """
    original_dims_in_pixels = [image_array.shape[d] for d in range(len(image_array.shape))]
    goal_pixel_dims_list = [int(math.floor(compression_factor_list[d] * original_dims_in_pixels[d]))
                             for d in range(len(image_array.shape))]

    resized_image = resample(image_array, goal_pixel_dims_list, is_seg)

    return(resized_image)