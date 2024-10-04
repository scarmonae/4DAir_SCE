# pblh_wavelet_visualization.py

"""
Module to calculate the Planetary Boundary Layer Height (PBLH) using the Wavelet Covariance Transform (WCT)
with Haar wavelets from LIDAR backscatter profiles.

This module includes detailed visualizations at each step to help validate the method and compare
the PBLH estimated by summing over scales and by taking the overall maximum.

Author: Your Name
Date: YYYY-MM-DD
"""

import numpy as np
import xarray as xr
import netCDF4 as nc
import matplotlib.pyplot as plt
from tqdm import tqdm

def haar_wavelet(scale, range_array, shift):
    """
    Genera una función wavelet de Haar escalada por 'scale' y desplazada por 'shift' sobre 'range_array'.

    Parámetros:
    - scale (float): Parámetro de escala del wavelet de Haar.
    - range_array (numpy.ndarray): Arreglo de valores de altura.
    - shift (float): Parámetro de desplazamiento para el wavelet de Haar.

    Retorna:
    - numpy.ndarray: La función wavelet de Haar escalada y desplazada.
    """
    # Definir los puntos clave
    left = shift - scale / 2
    center = shift
    right = shift + scale / 2

    # Crear la función wavelet
    wavelet = np.piecewise(
        range_array,
        [
            range_array < left,
            (range_array >= left) & (range_array < center),
            (range_array >= center) & (range_array < right),
            range_array >= right
        ],
        [0, 1, -1, 0]
    )

    # Normalizar el wavelet para que tenga norma unitaria
    norm_factor = np.sqrt(np.sum(wavelet ** 2) * (range_array[1] - range_array[0]))
    wavelet /= norm_factor

    return wavelet


def wavelet_covariance_transform(signal_profile, range_array, scales):
    """
    Aplica la Transformada de Covarianza Wavelet (WCT) utilizando wavelets de Haar a un perfil de señal.

    Parámetros:
    - signal_profile (numpy.ndarray): El perfil de señal LIDAR normalizado.
    - range_array (numpy.ndarray): Arreglo de valores de altura.
    - scales (list o numpy.ndarray): Lista de escalas (parámetros de dilatación) a utilizar.

    Retorna:
    - numpy.ndarray: Los coeficientes de covarianza wavelet en cada escala y altura (arreglo 2D).
    """
    coefficients = []
    delta_r = range_array[1] - range_array[0]  # Resolución en altura

    for scale in tqdm(scales, desc="Iterating over dilatations..."):
        covariance = []
        for shift in range_array:
            # Generar el wavelet para esta escala y desplazamiento
            wavelet = haar_wavelet(scale, range_array, shift)

            # Calcular la covarianza (producto punto)
            cov = np.sum(signal_profile * wavelet) * delta_r
            covariance.append(cov)
        coefficients.append(covariance)

    if not coefficients:
        raise ValueError("No se utilizaron escalas válidas. Por favor, ajusta tus escalas.")

    return np.array(coefficients)


def find_pbl_height(wct_coefficients, range_array, scales):
    """
    Identify the PBLH by summing over scales and also by finding the overall maximum.

    Parameters:
    - wct_coefficients (numpy.ndarray): Wavelet covariance coefficients (2D array: scales x range).
    - range_array (numpy.ndarray): Array of range (height) values.
    - scales (numpy.ndarray): Array of scales used in the WCT.

    Returns:
    - dict: A dictionary containing the PBL heights estimated by both methods.
    """
    # Method 1: Sum over scales and find the maximum
    summed_coefficients = np.sum(wct_coefficients, axis=0)
    max_index_sum = np.argmax(summed_coefficients)
    pbl_height_sum = range_array[max_index_sum]

    # Method 2: Find the overall maximum in the WCT coefficients
    max_scale_idx, max_range_idx = np.unravel_index(np.argmax(wct_coefficients), wct_coefficients.shape)
    pbl_height_max = range_array[max_range_idx]
    max_scale = scales[max_scale_idx]

    return {
        'pbl_height_sum': pbl_height_sum,
        'max_index_sum': max_index_sum,
        'pbl_height_max': pbl_height_max,
        'max_index_max': max_range_idx,
        'max_scale': max_scale,
        'max_scale_idx': max_scale_idx
    }

def process_lidar_profile(signal_profile, range_array, scales, plot_wct=False):
    """
    Process a single LIDAR signal profile to estimate the PBL height.

    Parameters:
    - signal_profile (numpy.ndarray): The LIDAR backscatter signal profile.
    - range_array (numpy.ndarray): Array of range (height) values.
    - scales (list or numpy.ndarray): List of scales (dilation parameters) to use.
    - plot_wct (bool): If True, plot the WCT coefficients and intermediate steps.

    Returns:
    - dict: Estimated PBL heights using both methods.
    """

    # Normalizar el perfil de señal
    signal_profile = (signal_profile - np.mean(signal_profile)) / np.std(signal_profile)

    # Plot the original signal profile
    if plot_wct:
        plt.figure(figsize=(6, 8))
        plt.plot(signal_profile, range_array, label='LIDAR Signal')
        plt.xlabel('Backscatter Signal')
        plt.ylabel('Height (m)')
        plt.title('Original LIDAR Signal Profile')
        plt.legend()
        plt.show()

    wct_coefficients = wavelet_covariance_transform(signal_profile, range_array, scales)

    # Plot the WCT coefficients with height on y-axis and scale on x-axis
    if plot_wct:
        plt.figure(figsize=(10, 6))
        plt.imshow(
            wct_coefficients.T,  # Transpose to swap axes
            extent=[scales[0], scales[-1], range_array[0], range_array[-1]],
            aspect='auto',
            cmap='jet',
            origin='lower'  # Ensure that the height axis is displayed correctly
        )
        plt.colorbar(label='WCT Coefficient')
        plt.xlabel('Scale (m)')
        plt.ylabel('Height (m)')
        plt.title('Wavelet Covariance Transform (WCT)')

        # Find the indices of the maximum coefficient
        max_scale_idx = np.argmax(np.max(wct_coefficients, axis=1))
        max_range_idx = np.argmax(wct_coefficients[max_scale_idx, :])

        # Get the corresponding height and scale values
        max_height = range_array[max_range_idx]
        max_scale = scales[max_scale_idx]

        # Mark the maximum point (x: scale, y: height)
        plt.plot(max_scale, max_height, 'ko', markersize=8, label='Overall Maximum')

        # Annotate the point
        plt.text(max_scale, max_height, f'  ({max_scale:.1f} m, {max_height:.1f} m)', color='white', fontsize=9)

        plt.legend()
        plt.show()

    # Find PBL heights using both methods
    pbl_results = find_pbl_height(wct_coefficients, range_array, scales)
    pbl_height_sum = pbl_results['pbl_height_sum']
    pbl_height_max = pbl_results['pbl_height_max']
    max_scale = pbl_results['max_scale']
    max_scale_idx = pbl_results['max_scale_idx']
    max_index_max = pbl_results['max_index_max']

    # Plot the summed coefficients and mark PBL heights
    if plot_wct:
        summed_coefficients = np.sum(wct_coefficients, axis=0)
        plt.figure(figsize=(6, 8))
        plt.plot(summed_coefficients, range_array, label='Summed WCT Coefficients')
        plt.axhline(pbl_height_sum, color='r', linestyle='--', label=f'PBL Height (Sum): {pbl_height_sum:.1f} m')
        plt.axhline(pbl_height_max, color='k', linestyle='--', label=f'PBL Height (Max): {pbl_height_max:.1f} m')
        plt.xlabel('Summed WCT Coefficient')
        plt.ylabel('Height (m)')
        plt.title('Summed WCT Coefficients with PBL Heights')
        plt.legend()
        plt.show()

        # Overlay PBL heights on original signal
        plt.figure(figsize=(6, 8))
        plt.plot(signal_profile, range_array, label='LIDAR Signal')
        plt.axhline(pbl_height_sum, color='r', linestyle='--', label=f'PBL Height (Sum): {pbl_height_sum:.1f} m')
        plt.axhline(pbl_height_max, color='k', linestyle='--', label=f'PBL Height (Max): {pbl_height_max:.1f} m')
        plt.xlabel('Backscatter Signal')
        plt.ylabel('Height (m)')
        plt.title('LIDAR Signal with PBL Heights')
        plt.legend()
        plt.show()

        # Generate the Haar wavelet corresponding to the maximum covariance
        wavelet_at_max = haar_wavelet(max_scale, range_array, pbl_height_max)

        # Normalize the wavelet for visualization purposes
        wavelet_scaled = wavelet_at_max * np.max(signal_profile) / np.max(wavelet_at_max)

        # Plot the LIDAR signal and the corresponding Haar wavelet
        plt.figure(figsize=(6, 8))
        plt.plot(signal_profile, range_array, label='LIDAR Signal')
        plt.plot(wavelet_scaled, range_array, label='Haar Wavelet at Max Covariance')
        plt.xlabel('Signal Amplitude')
        plt.ylabel('Height (m)')
        plt.title('LIDAR Signal and Haar Wavelet at Max Covariance')
        plt.legend()
        plt.show()

    return pbl_results

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
    - xarray.Dataset: Estimated PBL heights over time using both methods.
    """
    pbl_heights_sum = []
    pbl_heights_max = []
    times = dataset[time_variable].values
    range_array = dataset[range_variable].values

    for i, t in tqdm(enumerate(times), desc="Proccesing profiles..."):
        signal_profile = dataset[signal_variable].sel({time_variable: t}).values

        # Plot WCT and intermediate steps for selected profiles
        plot_wct = (i % 100 == 0)  # Adjust as needed
        pbl_results = process_lidar_profile(signal_profile, range_array, scales, plot_wct=plot_wct)
        pbl_heights_sum.append(pbl_results['pbl_height_sum'])
        pbl_heights_max.append(pbl_results['pbl_height_max'])

    # Create a Dataset with both PBL height estimates
    pbl_dataset = xr.Dataset(
        {
            'pbl_height_sum': (time_variable, pbl_heights_sum),
            'pbl_height_max': (time_variable, pbl_heights_max)
        },
        coords={time_variable: times}
    )

    return pbl_dataset

# Example usage
if __name__ == "__main__":
    # Load your dataset

    filename = '/path/to/your/datafile.nc'
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

    # Define scales to use (in meters)
    delta_r = dataset[range_variable].values[1] - dataset[range_variable].values[0]
    scales = np.linspace(4 * delta_r, 1000, 50)  # Adjust scales as needed

    # Process the dataset
    pbl_dataset = process_lidar_dataset(
        dataset,
        signal_variable,
        range_variable,
        time_variable,
        scales
    )

    # Save the PBL heights to a new NetCDF file
    pbl_dataset.to_netcdf('/path/to/save/pbl_heights.nc')
