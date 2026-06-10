from typing import List, Tuple, Dict
from datetime import date

def calculate_next_day_pmc(yesterday_ctl: float, yesterday_atl: float, tss_today: float) -> Tuple[float, float, float]:
    """Calculates today's CTL, ATL, and TSB from yesterday's values and today's TSS.
    
    Formula (Exponentially Weighted Moving Average):
    CTL_today = CTL_yesterday + (TSS_today - CTL_yesterday) / 42
    ATL_today = ATL_yesterday + (TSS_today - ATL_yesterday) / 7
    TSB_today = CTL_yesterday - ATL_yesterday
    """
    ctl_today = yesterday_ctl + (tss_today - yesterday_ctl) / 42.0
    atl_today = yesterday_atl + (tss_today - yesterday_atl) / 7.0
    tsb_today = ctl_today - atl_today
    return float(ctl_today), float(atl_today), float(tsb_today)

def calculate_history_pmc(
    tss_history: List[Tuple[date, float]], 
    starting_ctl: float = 0.0, 
    starting_atl: float = 0.0
) -> List[Dict]:
    """Calculates the historical progression of CTL, ATL, and TSB over time.
    
    tss_history is a list of tuples: (activity_date, tss_value).
    Sorts chronologically, fills in missing days with 0 TSS, and calculates PMC.
    """
    if not tss_history:
        return []

    # Sort history by date
    sorted_history = sorted(tss_history, key=lambda x: x[0])
    start_date = sorted_history[0][0]
    end_date = sorted_history[-1][0]
    
    # Map dates to TSS
    tss_map = {}
    for d, tss in sorted_history:
        tss_map[d] = tss_map.get(d, 0.0) + tss

    pmc_history = []
    current_ctl = starting_ctl
    current_atl = starting_atl
    
    # Iterate every day from start to end (inclusive)
    from datetime import timedelta
    current_date = start_date
    while current_date <= end_date:
        daily_tss = tss_map.get(current_date, 0.0)
        current_ctl, current_atl, current_tsb = calculate_next_day_pmc(current_ctl, current_atl, daily_tss)
        
        pmc_history.append({
            "date": current_date,
            "tss": daily_tss,
            "ctl": current_ctl,
            "atl": current_atl,
            "tsb": current_tsb
        })
        current_date += timedelta(days=1)
        
    return pmc_history
