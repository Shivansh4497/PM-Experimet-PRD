import math
from scipy.stats import norm

def calculate_sample_size(current_value: float, min_detectable_effect: float, confidence: float, power: float) -> int:
    """
    Calculates the required sample size for each variant of an A/B test.

    Uses the standard two-proportion z-test formula.
    Supports arbitrary confidence and power values via scipy.

    Args:
        current_value (float): The baseline conversion rate (as a percentage).
        min_detectable_effect (float): The minimum relative increase you want to detect (as a percentage).
        confidence (float): The desired confidence level (e.g., 0.95 for 95%).
        power (float): The desired power (e.g., 0.80 for 80%).

    Returns:
        int: The required sample size per variant, rounded up.
    """
    # Convert percentages to proportions
    p1 = current_value / 100.0
    p2 = p1 * (1 + min_detectable_effect / 100.0)

    # Pooled probability
    p_pooled = (p1 + p2) / 2

    # Compute Z-scores dynamically
    z_alpha = norm.ppf(1 - (1 - confidence) / 2)  # two-tailed test
    z_beta = norm.ppf(power)

    # Numerator and denominator
    numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) +
                 z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    denominator = (p2 - p1) ** 2

    # Sample size per variant
    sample_size = numerator / denominator

    return math.ceil(sample_size)

def calculate_duration(sample_size: int, daily_active_users: int, coverage: float) -> int:
    """
    Estimates the duration of the A/B test in days.

    Args:
        sample_size (int): Required sample size per variant.
        daily_active_users (int): Total unique users per day.
        coverage (float): Percentage of DAU included in experiment.

    Returns:
        int: Estimated duration in days (at least 1).
    """
    total_sample_size = sample_size * 2  # control + variant
    eligible_users_per_day = daily_active_users * (coverage / 100.0)

    if eligible_users_per_day <= 0:
        return 0

    duration = math.ceil(total_sample_size / eligible_users_per_day)
    return max(1, duration)
