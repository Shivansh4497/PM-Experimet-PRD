import math

def calculate_sample_size(current_value: float, min_detectable_effect: float, confidence: float, power: float) -> int:
    """
    Calculates the required sample size for each variant of an A/B test.
    
    This function uses the standard formula for calculating sample size for a test
    on proportions. It requires the current value, minimum detectable effect,
    desired confidence level (alpha), and statistical power (beta).

    Args:
        current_value (float): The baseline conversion rate (as a proportion).
        min_detectable_effect (float): The minimum relative increase you want to detect (as a percentage).
        confidence (float): The confidence level, typically 0.95.
        power (float): The statistical power, typically 0.80.

    Returns:
        int: The required sample size per variant, rounded up to the nearest integer.
    """
    # Convert percentages to proportions
    p1 = current_value / 100.0
    
    # Calculate the target value based on the MDE
    p2 = p1 * (1 + min_detectable_effect / 100)

    # Calculate the pooled probability
    p_pooled = (p1 + p2) / 2

    # A dictionary for Z-scores. In a more advanced application, a library
    # like scipy would be used to get these values programmatically.
    z_scores = {
        0.99: 2.58,  # Z-score for 99% confidence
        0.95: 1.96,  # Z-score for 95% confidence
        0.90: 1.645, # Z-score for 90% confidence
        0.80: 0.84,  # Z-score for 80% power
        0.90: 1.28,  # Z-score for 90% power
    }
    
    # Get the Z-scores for the given confidence and power levels
    z_alpha = z_scores.get(confidence)
    z_beta = z_scores.get(power)

    if z_alpha is None or z_beta is None:
        raise ValueError("Unsupported confidence or power level. Please use 0.99, 0.95, 0.90, or 0.80.")

    # Calculate the numerator of the sample size formula
    numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    
    # Calculate the denominator of the sample size formula
    denominator = (p2 - p1) ** 2

    # The sample size per variant
    sample_size = numerator / denominator

    # Round up to the nearest whole number and return as an integer
    return math.ceil(sample_size)

def calculate_duration(sample_size: int, daily_active_users: int, coverage: float) -> int:
    """
    Estimates the duration of the A/B test in days.
    
    This calculation now factors in the coverage, which is the percentage of
    daily active users included in the experiment.
    
    Args:
        sample_size (int): The required sample size for a single variant.
        daily_active_users (int): The number of unique users per day.
        coverage (float): The percentage of DAU included in the experiment.
        
    Returns:
        int: The estimated duration in days.
    """
    # The total sample size for both the control and variant groups
    total_sample_size = sample_size * 2
    
    # Calculate the number of eligible users per day
    eligible_users_per_day = daily_active_users * (coverage / 100)
    
    # Calculate the duration and ensure it is at least 1 day
    if eligible_users_per_day > 0:
      duration = math.ceil(total_sample_size / eligible_users_per_day)
    else:
      duration = 0 # Or handle the error appropriately
    
    return max(1, duration)
