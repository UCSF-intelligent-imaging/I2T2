# Intelligent Imaging Tools and Tasks (I2T2) 
> Library of useful tools for Medical Imaging Handling


Instructions for installation and usage can be found below.

## Install

`pip install I2T2`

## How to use

```
# example usage:
import matplotlib.pyplot as plt
data_path = '../../../3_data/GE/Exam3038_Series5/'
array = dcm2array(path_to_dicom_dir = data_path, sort_by_slice_location=True)
plt.imshow(array[:,:,0])
plt.show()
```




    2


