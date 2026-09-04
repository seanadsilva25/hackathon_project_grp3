from datetime import datetime, timezone
import pandas as pd

def calculate_cluster_severity(cluster_df, reference_date=None):
    """
    Calculates deterministic risk score and severity level (Low, Medium, High) for a cluster of complaints.

    Signals evaluated:
    1. Complaint Density (Count): up to 40 pts
    2. Upvote Impact: up to 25 pts
    3. Unresolved/Open Status: up to 20 pts
    4. Recency of Complaints: up to 15 pts

    :param cluster_df: DataFrame containing complaints for a single cluster
    :param reference_date: Optional datetime reference for calculating recency (defaults to now)
    :return: dict with 'risk_score', 'severity', and score breakdown
    """
    count = len(cluster_df)
    if count == 0:
        return {
            'risk_score': 0.0,
            'severity': 'LOW',
            'breakdown': {'density': 0, 'upvotes': 0, 'unresolved': 0, 'recency': 0}
        }

    # 1. Density Score (Max 40 pts)
    # Scaling: 20+ complaints reaches max 40 points
    density_score = min(count / 20.0, 1.0) * 40.0

    # 2. Upvote Impact Score (Max 25 pts)
    total_upvotes = pd.to_numeric(cluster_df.get('upvote_count', 0), errors='coerce').fillna(0).sum()
    # Scaling: 150+ total upvotes reaches max 25 points
    upvote_score = min(total_upvotes / 150.0, 1.0) * 25.0

    # 3. Unresolved/Open Status Score (Max 20 pts)
    status_series = cluster_df.get('status', pd.Series(['open'] * count)).astype(str).str.lower()
    unresolved_mask = status_series.isin(['open', 'in_progress', 'pending'])
    unresolved_count = unresolved_mask.sum()
    unresolved_ratio = unresolved_count / float(count)
    unresolved_score = unresolved_ratio * 20.0

    # 4. Recency Score (Max 15 pts)
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    recency_scores = []
    created_at_series = pd.to_datetime(cluster_df.get('created_at'), errors='coerce', utc=True)

    for dt in created_at_series:
        if pd.isna(dt):
            recency_scores.append(0.5) # default neutral weight if missing timestamp
            continue
        
        days_diff = (reference_date - dt).total_seconds() / (24 * 3600)
        if days_diff <= 7:
            recency_scores.append(1.0)
        elif days_diff <= 14:
            recency_scores.append(0.8)
        elif days_diff <= 30:
            recency_scores.append(0.5)
        else:
            recency_scores.append(0.2)

    avg_recency_factor = sum(recency_scores) / float(count)
    recency_score = avg_recency_factor * 15.0

    # Total Risk Score (0 to 100)
    risk_score = round(density_score + upvote_score + unresolved_score + recency_score, 2)

    # Determine Severity Category
    if risk_score >= 60.0:
        severity = 'HIGH'
    elif risk_score >= 30.0:
        severity = 'MEDIUM'
    else:
        severity = 'LOW'

    return {
        'risk_score': risk_score,
        'severity': severity,
        'breakdown': {
            'density': round(density_score, 2),
            'upvotes': round(upvote_score, 2),
            'unresolved': round(unresolved_score, 2),
            'recency': round(recency_score, 2),
            'complaint_count': count,
            'total_upvotes': int(total_upvotes),
            'unresolved_count': int(unresolved_count)
        }
    }
