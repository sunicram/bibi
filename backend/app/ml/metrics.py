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

def calculate_teq_score(power_series: List[int], intervals: List[dict], ftp: int, tolerance_pct: float = 0.05) -> float:
    """Calculates the Training Execution Quality (TEQ) score for a workout.
    
    For steps >= 1 minute (60s):
    - Applies 10s transition buffer (ignores first 10s).
    - Checks 10s SMA deviation from target power range [target*(1-tol), target*(1+tol)].
    
    For steps < 1 minute:
    - Checks deviation of step average power from target power range.
    """
    if not power_series or not intervals or ftp <= 0:
        return 100.0

    current_idx = 0
    step_weighted_teq_sum = 0.0
    total_analyzed_duration = 0
    
    for step in intervals:
        step_dur = int(step.get("duration_seconds", 0))
        if step_dur <= 0:
            continue
            
        # Extract step actual power
        step_power = power_series[current_idx : current_idx + step_dur]
        current_idx += step_dur
        
        if not step_power:
            continue
            
        target_pct = float(step.get("target_power_pct", 100.0))
        target_power = ftp * (target_pct / 100.0)
        p_min = target_power * (1.0 - tolerance_pct)
        p_max = target_power * (1.0 + tolerance_pct)
        
        actual_step_len = len(step_power)
        
        if actual_step_len >= 60:
            # Step >= 1 minute: apply 10s transition buffer and 10s SMA
            # Ignores first 10 seconds of the step
            errors = []
            for i in range(10, actual_step_len):
                # Calculate 10s SMA ending at i
                sma_val = sum(step_power[i-9 : i+1]) / 10.0
                if sma_val < p_min:
                    err = (p_min - sma_val) / p_min
                elif sma_val > p_max:
                    err = (sma_val - p_max) / p_max
                else:
                    err = 0.0
                errors.append(err)
            
            step_error = sum(errors) / len(errors) if errors else 0.0
            step_teq = max(0.0, 1.0 - step_error) * 100.0
        else:
            # Step < 1 minute: use step average power
            avg_p = sum(step_power) / len(step_power)
            if avg_p < p_min:
                err = (p_min - avg_p) / p_min
            elif avg_p > p_max:
                err = (avg_p - p_max) / p_max
            else:
                err = 0.0
            step_teq = max(0.0, 1.0 - err) * 100.0
            
        step_weighted_teq_sum += step_teq * actual_step_len
        total_analyzed_duration += actual_step_len

    if total_analyzed_duration <= 0:
        return 100.0
        
    return float(step_weighted_teq_sum / total_analyzed_duration)

def calculate_workout_stimulus_score(intervals: List[dict], tss: float) -> float:
    """Calculates the Stimulus Weight (WS) for a workout.
    Formula: WS = (T_target_zone * W_intensity) + (TSS * 0.2)
    """
    if not intervals:
        return float(tss * 0.2)
        
    ws_intervals = 0.0
    for step in intervals:
        duration_sec = int(step.get("duration_seconds", 0))
        target_pct = float(step.get("target_power_pct", 100.0))
        
        # Map target_pct to Coggan zone intensity weight (W_intensity)
        # Z5+ (VO2 Max / Anaerobic) -> 2.0
        # Z3/Z4 (Sweet Spot / Threshold) -> 1.5
        # Z2 (Endurance) -> 0.5
        # Z1 (Active Recovery) -> 0.0
        if target_pct >= 106.0: # Z5+
            w_intensity = 2.0
        elif target_pct >= 76.0: # Z3/Z4
            w_intensity = 1.5
        elif target_pct >= 56.0: # Z2
            w_intensity = 0.5
        else: # Z1
            w_intensity = 0.0
            
        duration_min = duration_sec / 60.0
        ws_intervals += duration_min * w_intensity
        
    return float(ws_intervals + (tss * 0.2))

