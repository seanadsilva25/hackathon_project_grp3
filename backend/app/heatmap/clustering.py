import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

# Earth radius in kilometers for Haversine distance calculations
EARTH_RADIUS_KM = 6371.0088

def perform_geographical_clustering(complaints_data, radius_meters=500, min_samples=3):
    """
    Performs DBSCAN geographical clustering on latitude and longitude coordinates.

    :param complaints_data: pandas DataFrame or list of dicts with 'latitude' and 'longitude' fields
    :param radius_meters: Maximum distance between two samples for one to be considered in the neighborhood of the other (default 500m)
    :param min_samples: Minimum number of samples in a neighborhood for a point to be considered as a core point
    :return: DataFrame with an added 'cluster_label' column (-1 indicates noise/isolated complaints)
    """
    if isinstance(complaints_data, list):
        df = pd.DataFrame(complaints_data).copy()
    else:
        df = complaints_data.copy()

    # Ensure latitude and longitude columns exist
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        raise ValueError("Complaints data must contain 'latitude' and 'longitude' columns.")

    # Convert coordinates to numeric, coercion to NaN for invalid data
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    # Filter valid coordinates
    valid_mask = (
        df['latitude'].notna() &
        df['longitude'].notna() &
        (df['latitude'] >= -90) & (df['latitude'] <= 90) &
        (df['longitude'] >= -180) & (df['longitude'] <= 180)
    )

    # Initialize all cluster labels to -1 (noise)
    df['cluster_label'] = -1

    valid_coords = df.loc[valid_mask, ['latitude', 'longitude']].values

    if len(valid_coords) >= min_samples:
        # Convert latitude and longitude from degrees to radians for Haversine metric
        coords_rad = np.radians(valid_coords)

        # Convert radius in meters to radians
        eps_radians = (radius_meters / 1000.0) / EARTH_RADIUS_KM

        # Run DBSCAN
        db = DBSCAN(
            eps=eps_radians,
            min_samples=min_samples,
            metric='haversine'
        ).fit(coords_rad)

        df.loc[valid_mask, 'cluster_label'] = db.labels_

    return df
