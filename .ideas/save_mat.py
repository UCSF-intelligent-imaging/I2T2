from scipy.io import savemat
import h5py
import os

path = '/data/knee_mri4/pferreira/1_repos/knee-anomaly-inference_V4/src/results/trial_929faf1c/segmentation/output_ckpt290/'
exam3037_4 = path+'seg5class_imgdict_exam3037_4.h5'
exam3038_5 = path+'seg5class_imgdict_exam3038_5.h5'

exam3037_4_h5 = h5py.File(exam3037_4, 'r')
exam3038_5_h5 = h5py.File(exam3038_5, 'r')

dict_data_exam3037_4_h5 = {'img':exam3037_4_h5.get('img').value, 'seg':exam3037_4_h5.get('seg').value}
dict_data_exam3038_5_h5 = {'img':exam3038_5_h5.get('img').value, 'seg':exam3038_5_h5.get('seg').value}
