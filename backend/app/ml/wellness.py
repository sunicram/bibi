from typing import List, Optional, Dict
import numpy as np

def calculate_z_score(today_val: float, past_values: List[float]) -> float:
    """Calculates standard Z-score against a list of past values.
    
    Z = (today - mean) / stddev
    Defaults to 0.0 if not enough data or stddev is 0.
    """
    if not past_values or len(past_values) < 3:
        return 0.0
    
    mean = np.mean(past_values)
    std = np.std(past_values)
    
    if std <= 0.0001:
        return 0.0
        
    return float((today_val - mean) / std)

def determine_readiness_tier(hrv_z: float, rhr_z: float) -> str:
    """Maps HRV and RHR Z-scores to readiness tiers.
    
    Tiers:
    - Red: HRV Z <= -1.5 OR RHR Z >= +1.5 (High fatigue/suppression)
    - Yellow: -1.5 < HRV Z < -0.5 OR +0.5 < RHR Z < +1.5 (Mild stress)
    - Green: HRV Z >= -0.5 AND RHR Z <= +0.5 (No restriction)
    """
    if hrv_z <= -1.5 or rhr_z >= 1.5:
        return "red"
    elif hrv_z < -0.5 or rhr_z > 0.5:
        return "yellow"
    else:
        return "green"

def calculate_sleep_debt(sleep_history: List[int], target_sleep_minutes: int) -> int:
    """Calculates sleep debt over the last 3 nights compared to onboarding target.
    
    sleep_history: Sleep durations in minutes for the last 3 nights.
    """
    if not sleep_history:
        return 0
    
    # Restrict to last 3 nights
    last_3 = sleep_history[-3:]
    total_sleep = sum(last_3)
    target_total = target_sleep_minutes * len(last_3)
    
    debt = target_total - total_sleep
    return max(0, debt) # only positive debt matters

def compute_daily_wellness_metrics(
    today_hrv: Optional[float],
    today_rhr: Optional[int],
    today_sleep: Optional[int],
    past_7d_hrv: List[float],
    past_7d_rhr: List[int],
    past_3d_sleep: List[int],
    target_sleep_minutes: int
) -> Dict:
    """Combines all daily wellness calculations and computes the readiness tier.
    
    Handles missing values gracefully.
    """
    hrv_z = 0.0
    rhr_z = 0.0
    sleep_debt = 0
    
    if today_hrv is not None and past_7d_hrv:
        hrv_z = calculate_z_score(today_hrv, past_7d_hrv)
        
    if today_rhr is not None and past_7d_rhr:
        # Convert RHR list to float to compute Z-score
        past_rhr_float = [float(x) for x in past_7d_rhr]
        rhr_z = calculate_z_score(float(today_rhr), past_rhr_float)
        
    if today_sleep is not None:
        sleep_history = past_3d_sleep + [today_sleep]
        sleep_debt = calculate_sleep_debt(sleep_history, target_sleep_minutes)
        
    tier = determine_readiness_tier(hrv_z, rhr_z)
    
    return {
        "hrv_z_score": hrv_z,
        "rhr_z_score": rhr_z,
        "sleep_debt_minutes": sleep_debt,
        "readiness_tier": tier
    }

def calculate_simplified_readyscore(
    rpe_history: List[Optional[int]],
    morning_feeling: Optional[int],
    last_reserve: Optional[int]
) -> float:
    """Calculates a simplified readiness score (0.0 to 100.0) when wearables are missing.
    
    Formula: ReadyScore = (RPE_trend * 0.4) + (feeling_val * 0.4) + (reserve_val * 0.2)
    - RPE_trend: based on difficulty_after (1-3) of last 3 workouts (1/2 -> 100, 3 -> 30) weighted [0.5, 0.3, 0.2]
    - morning_feeling: 1-5 mapped to 20-100
    - last_reserve: 1-2 mapped to 0-100 (1 -> 0, 2 -> 100)
    """
    # 1. Morning feeling: 1-5 -> 20-100
    feeling_val = 60.0 # default/neutral
    if morning_feeling is not None:
        feeling_val = float(morning_feeling) * 20.0
        
    # 2. Last reserve: 1-2 -> 0-100 (1: No -> 0, 2: Yes -> 100)
    reserve_val = 100.0 # default
    if last_reserve is not None:
        reserve_val = 100.0 if last_reserve == 2 else 0.0
        
    # 3. RPE trend from last 3 workouts (newest first)
    # Map difficulty_after to scores: 1 (easy) -> 100, 2 (planned) -> 100, 3 (too hard) -> 30
    rpe_scores = []
    for val in rpe_history:
        if val is not None:
            if val == 3:
                rpe_scores.append(30.0)
            else:
                rpe_scores.append(100.0)
                
    # Pad to 3 elements with 100.0 (neutral/good)
    while len(rpe_scores) < 3:
        rpe_scores.append(100.0)
        
    # Take first 3 and apply weights [0.5, 0.3, 0.2]
    rpe_trend = rpe_scores[0] * 0.5 + rpe_scores[1] * 0.3 + rpe_scores[2] * 0.2
    
    # Final ReadyScore
    readyscore = (rpe_trend * 0.4) + (feeling_val * 0.4) + (reserve_val * 0.2)
    return float(readyscore)

