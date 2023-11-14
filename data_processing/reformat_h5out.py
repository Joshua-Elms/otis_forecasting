"""
This script will check whether the .h5 output files produced by FCN have the correct format (labeled dimensions, etc). 

If they do not, it will apply that formatting.
"""

import xarray as xr
import os
from time import perf_counter

def main(
    input_file, 
    output_file=None, 
    rewrite=False, 
    display=False
    ):
    """
    reformat_file: str
        Path to .h5 file to be reformatted
    """
    ds = xr.open_dataset(input_file)
    
    # Define dimension labels based on your comment
    ds = ds.rename({
        'phony_dim_0': 'ic',
        'phony_dim_1': 't',
        'phony_dim_2': 'channel',
        'phony_dim_3': 'x',
        'phony_dim_4': 'y'
    })

    # Define dimension names
    ds.ic.attrs['long_name'] = 'Initial Condition'
    ds.t.attrs['long_name'] = 'Time'
    ds.channel.attrs['long_name'] = 'Channel'
    ds.x.attrs['long_name'] = 'X-idx'
    ds.y.attrs['long_name'] = 'Y-idx'
    
    
    if display:
        print("----- Start Dataset -----")
        print(ds)
        print("------ End Dataset ------")
    
    if rewrite: 
        stem = os.path.splitext(input_file)[0] # Split into stem and extension
        ext = os.path.splitext(input_file)[1]
        if output_file:
            output_stem = os.path.splitext(output_file)[0]
            
        if not output_file:
            output_stem = stem
            output_file = output_stem + ".nc" # switch to .nc extension to use xr.to_netcdf
            
        tmp_file = output_stem + ".tmp"
            
        try:
            print("Writing to tmp file: ", end="")
            start = perf_counter()
            ds.to_netcdf(tmp_file)
            stop = perf_counter()
            print(f"{stop - start:.1f}s")
            
        except Exception as e:
            print(f"Error writing to {tmp_file}: {e}")
            return
        
        os.remove(input_file)
        print(f"Writing to output file: ", end="")
        start = perf_counter()
        os.replace(tmp_file, output_file)
        stop = perf_counter()
        print(f"{stop - start:.1f}s\n")
        
        print(f"Dataset at {input_file} written to {output_file}")
        
    
if __name__=="__main__":
    main(
        input_file = "/N/slate/jmelms/FCN_output/otis21t/autoregressive_predictions_z500_vis.h5",
        output_file = "/N/slate/jmelms/FCN_output/otis21t/autoregressive_predictions_z500_vis.nc", # If None, will overwrite input file
        rewrite = True, # Write reformatted dataset to output_file
        display = True, # Display dataset after reformatting
    )