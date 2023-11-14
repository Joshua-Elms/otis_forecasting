import numpy as np
from scipy.ndimage import sobel

def land_edges(mask_array):
    # Apply Sobel operator for edge detection
    edges_x = sobel(mask_array, axis=0, mode='constant')
    edges_y = sobel(mask_array, axis=1, mode='constant')

    # Combine horizontal and vertical edges
    edges = np.hypot(edges_x, edges_y)

    # Threshold to get binary edges
    edges_binary = edges > 0.1  # Adjust the threshold as needed

    return edges_binary.astype(int)

if __name__ == "__main__":
    land_sea_path = "/N/u/jmelms/BigRed200/FCN_Otis/land_sea_mask.npy"
    land_sea_arr = np.load(land_sea_path)[:720].round(0)
    new = land_edges(land_sea_arr)
    np.save("/N/u/jmelms/BigRed200/FCN_Otis/land_sea_edges_mask.npy", new)
    print("Converted mask to edge mask")