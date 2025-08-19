import math
from scipy.stats import norm

def calculate_sample_size_proportion(current_value: float, min_detectable_effect: float, confidence: float, power: float) -> int:
    """
    Calculates sample size for proportion-based metrics (e.g., conversion rates).
    Uses a two-proportion z-test formula.
    """
    if current_value <= 0 or current_value >= 100:
        raise ValueError("Current value must be between 0 and 100 for proportion metrics.")
    
    # Convert percentages to proportions
    p1 = current_value / 100.0
    p2 = p1 * (1 + min_detectable_effect / 100.0)

    if p2 >= 1.0:
        p2 = 0.999 # Clamp to avoid math domain errors

    # Pooled probability
    p_pooled = (p1 + p2) / 2

    # Z-scores
    z_alpha = norm.ppf(1 - (1 - confidence) / 2)
    z_beta = norm.ppf(power)

    # Formula components
    numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) +
                 z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    denominator = (p2 - p1) ** 2

    if denominator == 0:
        return float('inf')

    return math.ceil(numerator / denominator)

def calculate_sample_size_continuous(mean: float, std_dev: float, min_detectable_effect: float, confidence: float, power: float) -> int:
    """
    Calculates sample size for continuous metrics (e.g., ARPDAU, time on page).
    Uses a two-sample t-test formula.
    """
    if std_dev <= 0:
        raise ValueError("Standard deviation must be greater than 0 for continuous metrics.")

    # Z-scores
    z_alpha = norm.ppf(1 - (1 - confidence) / 2)
    z_beta = norm.ppf(power)

    # Absolute minimum detectable effect
    delta = mean * (min_detectable_effect / 100.0)

    if delta == 0:
        return float('inf')

    # Formula
    numerator = 2 * (std_dev ** 2) * ((z_alpha + z_beta) ** 2)
    denominator = delta ** 2
    
    return math.ceil(numerator / denominator)

def calculate_duration(sample_size: int, daily_active_users: int, coverage: float) -> int:
    """
    Estimates the duration of the A/B test in days.
    """
    if sample_size == float('inf'):
        return float('inf')
        
    total_sample_size = sample_size * 2  # control + variant
    eligible_users_per_day = daily_active_users * (coverage / 100.0)

    if eligible_users_per_day <= 0:
        return float('inf')

    duration = math.ceil(total_sample_size / eligible_users_per_day)
    return max(1, duration)
