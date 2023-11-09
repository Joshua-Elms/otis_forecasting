# ## Imports
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

def process_fcn_output():
        
    ######### START CONFIG ###########
    ## Paths ##

    input_data_dir_str = "/N/slate/jmelms/FCN_output" # path to forecasts
    output_data_dir_str = "N/slate/jmelms/otis_analysis" # path to desired output location
    which_data = "6t" # options are 6t or 16t, determines number of forecasted timestamps per ic
    lat_path_str = "/N/u/jmelms/BigRed200/FCN_Otis/latitude.npy"
    lon_path_str = "/N/u/jmelms/BigRed200/FCN_Otis/longitude.npy"
    stats_dir_str = "/N/slate/jmelms/FourCastNetData/stats_v0/"

    ## Temporal ##

    # start time of initial condition 0 
    init_time = dict( 
        year=2023,
        month=10,
        day=15,
        hour=0,
    )
    timestep_hours = 6 # 

    ## Channels ##
    channels = np.array([
    'u10',
    'v10',
    't2m',
    'sp',
    'mslp',
    't850',
    'u1000',
    'v1000',
    'z1000',
    'u850',
    'v850',
    'z850',
    'u500',
    'v500',
    'z500',
    't500',
    'z50',
    'r500',
    'r850',
    'tcwv'
    ])

    ## Don't Touch

    input_data = Path(input_data_dir_str) / f"otis{which_data}" / "autoregressive_predictions_z500_vis.nc"
    output_data_dir = Path(output_data_dir_str)
    lat_path = Path(lat_path_str)
    lon_path = Path(lon_path_str)
    global_means_path = Path(stats_dir_str) / "global_means.npy"
    global_stds_path = Path(stats_dir_str) / "global_stds.npy"

    ############## END CONFIG ##############

    # ## Reading Data

    ds = xr.open_dataset(input_data)
    pred = ds["predicted"]

    # ## Creating a Temporal Array for Reference
    # 
    # Because the inference driver I'm using for FCN doesn't intend for forecasts to be overlapping in time, there's no easy solution proposed for adding timesteps of the data. I don't think that a coordinate system in xarray would really work here because the coordinates for dim t would vary according to the value of dim ic, which doesn't sound consistent with coordinates. Instead, I will simply produce an array of shape (ic x t) that contains the timestamps for each initial condition and lead time run. Future code can interface with this array for time information.

    init_time = pd.Timestamp(**init_time)
    dims = pred.sizes

    # create one ic's worth of time coordinates (times for just one forecast, with t timesteps), then extract and reshape those values for downstream modification
    init_ic_time_coords = xr.cftime_range(start=init_time, periods=dims['t'], freq=f'{timestep_hours}H').values[np.newaxis, :] #

    # can't directly multiply time coords by a vector, only a scalar - therefore, iteratively add to the array ic_num * timestep_hours and stack into np.ndarray
    ic_time_coords = np.vstack([init_ic_time_coords.copy() + pd.Timedelta(hours = timestep_hours * i) for i in range(dims["ic"])])

    # example: at ic=18, forecast was initialized using 12z Oct. 19 2023 conditions from ERA5
    # ic_time_coords[18]

    # ## Adding Spatial & Channel Coordinates
    # 
    # I could never remember the coordinate system used - fortunately, there is an array that contains all of the necessary coordinates hardcoded, which I will simply apply to the data here.

    lat_arr = np.load(lat_path)[:720] # FCN truncates 721th line of ERA5 for ... some reason, I'm sure
    lon_arr = np.load(lon_path)
    pred = pred.rename(dict(
        x = "lat",
        y = "lon"  
    ))
    pred = pred.assign_coords(lat=lat_arr)
    pred = pred.assign_coords(lon=lon_arr)
    pred = pred.assign_coords(channel=channels)
    
    ## De-Normalizing
    # 
    # Forecasts are for $\frac{x - \mu}{\sigma}$ applied, so I will undo that.
    
    means = np.load(global_means_path).squeeze()[:len(channels)].reshape(1, 1, len(channels), 1, 1)
    stds = np.load(global_stds_path).squeeze()[:len(channels)].reshape(1, 1, len(channels), 1, 1)
    pred = (pred * stds) + means
    # test to check whether values are reasonable: mslp @ bloomington IN in october around 1021 hPa? Seems legit.
    # pred.sel(ic=0, t=0, channel="mslp", lat=slice(45, 35), lon=slice(270, 280)).values
    
    ds.close()
    
    return pred, ic_time_coords
    

