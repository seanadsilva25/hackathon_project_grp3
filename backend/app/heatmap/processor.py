import uuid
import numpy as np
import pandas as pd
from .clustering import perform_geographical_clustering
from .scoring import calculate_cluster_severity

def calculate_haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Calculates Haversine distance between two lat/lon points in meters."""
    R = 6371008.8  # Earth radius in meters
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    
    a = np.sin(dphi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0)**2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return R * c

def process_heatmap_pipeline(complaints_data, radius_meters=500, min_samples=3):
    """
    Executes end-to-end heatmap processing pipeline:
    1. Runs DBSCAN clustering on complaint coordinates
    2. Groups complaints into geographical clusters
    3. Calculates cluster centroid, approximate radius, dominant category, and authority
    4. Computes deterministic severity risk score (Low, Medium, High)
    5. Formats records for heatmap_zones and heatmap_data_points tables

    :param complaints_data: DataFrame or list of complaint dicts
    :param radius_meters: DBSCAN neighborhood distance parameter in meters
    :param min_samples: DBSCAN minimum samples parameter
    :return: dict with summary, heatmap_zones, heatmap_data_points, and noise_complaints
    """
    # 1. Perform DBSCAN geographical clustering
    df_clustered = perform_geographical_clustering(
        complaints_data,
        radius_meters=radius_meters,
        min_samples=min_samples
    )

    total_count = len(df_clustered)
    valid_mask = df_clustered['latitude'].notna() & df_clustered['longitude'].notna()
    valid_count = int(valid_mask.sum())

    heatmap_zones = []
    heatmap_data_points = []
    
    # Separate noise complaints (cluster label -1)
    noise_df = df_clustered[df_clustered['cluster_label'] == -1]

    # Process valid clusters (cluster labels >= 0)
    cluster_labels = [label for label in df_clustered['cluster_label'].unique() if label != -1]
    # Sort cluster labels numerically
    cluster_labels.sort()

    for label in cluster_labels:
        cdf = df_clustered[df_clustered['cluster_label'] == label].copy()
        
        # Calculate cluster centroid
        center_lat = float(cdf['latitude'].mean())
        center_lon = float(cdf['longitude'].mean())

        # Calculate approximate cluster radius in meters (max distance from centroid)
        distances = calculate_haversine_distance_meters(
            center_lat, center_lon,
            cdf['latitude'].values, cdf['longitude'].values
        )
        calculated_radius = float(np.max(distances)) if len(distances) > 0 else float(radius_meters)
        # Ensure a minimum visible radius of 100 meters
        approx_radius_meters = max(int(np.ceil(calculated_radius)), 100)

        # Determine dominant complaint category for zone_type
        if 'category' in cdf.columns and not cdf['category'].dropna().empty:
            dominant_category = str(cdf['category'].dropna().mode()[0])
        else:
            dominant_category = 'general'

        # Determine assigned authority ID if available
        assigned_authority = None
        if 'assigned_authority_id' in cdf.columns and not cdf['assigned_authority_id'].dropna().empty:
            auth_val = cdf['assigned_authority_id'].dropna().mode()
            if not auth_val.empty:
                assigned_authority = str(auth_val[0])

        # Compute cluster severity score
        score_result = calculate_cluster_severity(cdf)

        # Generate unique zone ID
        zone_id = str(uuid.uuid4())

        zone_record = {
            'id': zone_id,
            'zone_type': dominant_category,
            'latitude': round(center_lat, 6),
            'longitude': round(center_lon, 6),
            'radius_meters': approx_radius_meters,
            'severity': score_result['severity'],
            'risk_score': score_result['risk_score'],
            'assigned_authority_id': assigned_authority,
            'complaint_count': len(cdf),
            'breakdown': score_result['breakdown']
        }
        heatmap_zones.append(zone_record)

        # Map complaints to heatmap_data_points
        for _, row in cdf.iterrows():
            data_point_record = {
                'id': str(uuid.uuid4()),
                'heatmap_zone_id': zone_id,
                'source_type': 'complaint',
                'source_id': str(row['id']) if 'id' in row and pd.notna(row['id']) else str(uuid.uuid4()),
                'created_at': str(row.get('created_at', ''))
            }
            heatmap_data_points.append(data_point_record)

    noise_list = noise_df.to_dict(orient='records')

    return {
        'summary': {
            'total_complaints': total_count,
            'valid_coordinates': valid_count,
            'clusters_detected': len(heatmap_zones),
            'noise_complaints': len(noise_list)
        },
        'heatmap_zones': heatmap_zones,
        'heatmap_data_points': heatmap_data_points,
        'noise_complaints': noise_list
    }
