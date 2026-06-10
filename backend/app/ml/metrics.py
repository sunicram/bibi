from typing import List
import numpy as np

def calculate_normalized_power(power_series: List[int]) -> float:
    """Calculates Normalized Power (NP) from a second-by-second power series.
    
    Standard algorithm:
    1. Calculate a 30-second rolling average of power.
    2. Raise the values obtained in Step 1 to the 4th power.
    3. Calculate the average of the values obtained in Step 2.
    4. Take the 4th root of the value obtained in Step 3.
    """
    if not power_series or len(power_series) < 30:
        return float(np.mean(power_series)) if power_series else 0.0

    # 30-second rolling average using NumPy
    power_arr = np.array(power_series, dtype=float)
    kernel = np.ones(30) / 30.0
    # valid boundary mode matches intervals after 30 seconds
    rolling_avg = np.convolve(power_arr, kernel, mode='valid')
    
    # 4th power
    avg_powered = np.power(rolling_avg, 4)
    
    # Average of the 4th powers
    mean_powered = np.mean(avg_powered)
    
    # 4th root
    normalized_power = np.power(mean_powered, 0.25)
    return float(normalized_power)

def calculate_intensity_factor(np_val: float, ftp: int) -> float:
    """Calculates Intensity Factor (IF)."""
    if ftp <= 0:
        return 0.0
    return float(np_val / ftp)

def calculate_tss(duration_seconds: int, np_val: float, if_val: float, ftp: int) -> int:
    """Calculates Training Stress Score (TSS).
    Formula: TSS = (sec * NP * IF) / (FTP * 3600) * 100
    """
    if ftp <= 0 or duration_seconds <= 0:
        return 0
    tss = (duration_seconds * np_val * if_val) / (ftp * 36)
    return int(round(tss))

def calculate_aerobic_decoupling(power_series: List[int], hr_series: List[int]) -> float:
    """Calculates aerobic decoupling (Pw:HR or EF drop) between the first and second half.
    
    Formula:
    1. Divide the active ride into two halves.
    2. For each half, compute Efficiency Factor: EF = Average Power / Average Heart Rate.
    3. Decoupling = (EF_first_half - EF_second_half) / EF_first_half
    """
    if len(power_series) != len(hr_series) or len(power_series) < 60:
        return 0.0

    mid = len(power_series) // 2
    
    p1, p2 = np.array(power_series[:mid]), np.array(power_series[mid:])
    h1, h2 = np.array(hr_series[:mid]), np.array(hr_series[mid:])
    
    avg_p1, avg_p2 = np.mean(p1), np.mean(p2)
    avg_h1, avg_h2 = np.mean(h1), np.mean(h2)
    
    if avg_h1 <= 0 or avg_h2 <= 0:
        return 0.0
        
    ef1 = avg_p1 / avg_h1
    ef2 = avg_p2 / avg_h2
    
    if ef1 <= 0:
        return 0.0
        
    decoupling = (ef1 - ef2) / ef1 * 100
    return float(decoupling)
