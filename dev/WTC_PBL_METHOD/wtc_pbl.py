# pblh_wavelet.py

"""
Module to calculate the Planetary Boundary Layer Height (PBLH) using the Wavelet Covariance Transform (WCT)
with Haar wavelets from LIDAR backscatter profiles.

This module is structured with good programming practices and is designed to work with xarray datasets
containing time, range (height), and channel dimensions.

Author: Your Name
Date: YYYY-MM-DD
"""

import pdb
import numpy as np
import xarray as xr
import netCDF4 as nc 
from scipy import signal
import matplotlib.pyplot as plt

def haar_wavelet(scale, range_array, shift):
    """
    Generate a Haar wavelet function scaled by 'scale' and shifted by 'shift' over the 'range_array'.

    Parameters:
    - scale (float): The dilation parameter for the Haar wavelet.
    - range_array (numpy.ndarray): Array of range (height) values.
    - shift (float): The translation parameter for the Haar wavelet.

    Returns:
    - numpy.ndarray: The scaled and shifted Haar wavelet function.
    """
    # Calculate the positions of the step change
    left = shift - scale / 2
    right = shift + scale / 2

    # Create the wavelet function
    wavelet = np.piecewise(
        range_array,
        [range_array >= left, range_array > right],
        [1, -1, 0]
    )
    # Adjust for scale normalization
    return wavelet / np.sqrt(scale)

def wavelet_covariance_transform(signal_profile, range_array, scales):
    """
    Apply the Wavelet Covariance Transform (WCT) using Haar wavelets to a signal profile.

    Parameters:
    - signal_profile (numpy.ndarray): The LIDAR backscatter signal profile.
    - range_array (numpy.ndarray): Array of range (height) values.
    - scales (list or numpy.ndarray): List of scales (dilation parameters) to use (in meters).

    Returns:
    - numpy.ndarray: The wavelet covariance coefficients at each scale and range (2D array).
    """
    coefficients = []
    delta_r = range_array[1] - range_array[0]  # Range resolution in meters
    for scale in scales:
        # Calculate wavelet length in number of points
        wavelet_length = int(scale / delta_r)
        if wavelet_length < 2:
            continue  # Skip scales that are too small
        if wavelet_length % 2 != 0:
            wavelet_length += 1  # Ensure even length
        half_length = wavelet_length // 2

        # Create the wavelet
        wavelet = np.concatenate([
            np.ones(half_length),
            -np.ones(half_length)
        ])
        wavelet = wavelet / np.sqrt(scale)

        # Compute the covariance using convolution
        covariance = np.convolve(signal_profile, wavelet, mode='same')
        coefficients.append(covariance)
    if not coefficients:
        raise ValueError("No valid scales were used. Please adjust your scales.")
    return np.array(coefficients)


def find_pbl_height(wct_coefficients, range_array):
    """
    Identify the Planetary Boundary Layer Height (PBLH) from the WCT coefficients.

    Parameters:
    - wct_coefficients (numpy.ndarray): Wavelet covariance coefficients (2D array: scales x range).
    - range_array (numpy.ndarray): Array of range (height) values.

    Returns:
    - float: Estimated PBL height.
    """
    # Sum over scales or take the maximum over scales
    summed_coefficients = np.sum(wct_coefficients, axis=0)
    # Find the index of the maximum covariance
    max_index = np.argmax(summed_coefficients)
    pbl_height = range_array[max_index]
    return pbl_height

def process_lidar_profile(signal_profile, range_array, scales, plot_wct=False):
    """
    Process a single LIDAR signal profile to estimate the PBL height.

    Parameters:
    - signal_profile (numpy.ndarray): The LIDAR backscatter signal profile.
    - range_array (numpy.ndarray): Array of range (height) values.
    - scales (list or numpy.ndarray): List of scales (dilation parameters) to use.
    - plot_wct (bool): If True, plot the WCT coefficients.

    Returns:
    - float: Estimated PBL height.
    """
    wct_coefficients = wavelet_covariance_transform(signal_profile, range_array, scales)
    
    if plot_wct:
        plt.figure(figsize=(10, 6))
        plt.imshow(
            wct_coefficients,
            extent=[range_array[0], range_array[-1], scales[-1], scales[0]],
            aspect='auto',
            cmap='jet'
        )
        plt.colorbar(label='WCT Coefficient')
        plt.xlabel('Height (m)')
        plt.ylabel('Scale (m)')
        plt.title('Wavelet Covariance Transform (WCT)')
        plt.show()
    
    pbl_height = find_pbl_height(wct_coefficients, range_array)
    return pbl_height

def process_lidar_dataset(dataset, signal_variable, range_variable, time_variable, scales):
    """
    Process an xarray Dataset containing LIDAR profiles over time to estimate the PBL height at each time step.

    Parameters:
    - dataset (xarray.Dataset): The dataset containing LIDAR profiles.
    - signal_variable (str): Name of the variable in the dataset that contains the signal profile.
    - range_variable (str): Name of the range (height) coordinate in the dataset.
    - time_variable (str): Name of the time coordinate in the dataset.
    - scales (list or numpy.ndarray): List of scales (dilation parameters) to use.

    Returns:
    - xarray.DataArray: Estimated PBL heights over time.
    """
    pbl_heights = []
    times = dataset[time_variable].values
    range_array = dataset[range_variable].values

    for i, t in enumerate(times):
        signal_profile = dataset[signal_variable].sel({time_variable: t}).values
        
        # Plot WCT every 100 profiles
        plot_wct = (i % 100 == 0)
        pbl_height = process_lidar_profile(signal_profile, range_array, scales, plot_wct=plot_wct)
        pbl_heights.append(pbl_height)

    return xr.DataArray(pbl_heights, coords={time_variable: times}, dims=[time_variable])

# Example usage
if __name__ == "__main__":
    # Load your dataset

    filename = '/home/medico_eafit/WORKSPACES/sebastian_carmona/data/EAFIT/Dataset1/LiMon_Raw_Data_cc/2022/04/13/RS/LPP_OUT/RS_L0_L1_L2.nc'
    ncfile = nc.Dataset(filename)
    group = ncfile.groups['L2_Data']
    dataset = xr.open_dataset(xr.backends.NetCDF4DataStore(group))

    start_time = dataset.Start_Time_AVG_L2.values.astype('float32') // 10**9
    stop_time = dataset.Stop_Time_AVG_L2.values

    avg_time = (start_time + stop_time) / 2

    datetime_ns = np.array(avg_time, dtype='datetime64[s]')
    datetime_ns = datetime_ns.astype('datetime64[ns]') 

    dataset = dataset.assign_coords(time=datetime_ns)

    dataset = dataset.sel(channels=0, range=slice(100, 2500))

    signal_variable = 'Range_Corrected_Lidar_Signal_L2'  # Replace with your signal variable name
    range_variable = 'range'  # Replace with your range variable name
    time_variable = 'time'  # Replace with your time variable name

    # Define scales to use (in km)
    scales = np.linspace(0.1, 1.0, 10)

    # pdb.set_trace()    

    # Process the dataset
    pbl_heights = process_lidar_dataset(
        dataset,
        signal_variable,
        range_variable,
        time_variable,
        scales
    )

    # Save the PBL heights to a new NetCDF file
    pbl_heights.to_netcdf('/home/medico_eafit/WORKSPACES/sebastian_carmona/dev/WTC_PBL_METHOD/outputs/pbl_heights.nc')
