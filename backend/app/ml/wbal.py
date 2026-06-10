import math
from typing import List, Tuple

def calculate_wbal_series(
    power_series: List[int], 
    ftp: int, 
    w_prime_initial: int
) -> Tuple[List[int], bool]:
    """Calculates the second-by-second remaining anaerobic battery W'bal (in Joules).
    
    Using the Skiba (2012) model:
    - Depletion (Power > FTP): W'bal(t) = W'bal(t-1) - (Power(t) - FTP)
    - Reconstitution (Power <= FTP): W'bal(t) = W'_0 - (W'_0 - W'bal(t-1)) * e^(-1 / tau)
      where tau = 546 * e^(-0.01 * (FTP - Power(t)))
      
    Returns:
    - List of W'bal values per second.
    - Boolean flag: True if the battery hit zero (or went negative) indicating full depletion.
    """
    w_prime_initial = float(w_prime_initial)
    w_bal = w_prime_initial
    wbal_series = []
    depleted = False

    for p in power_series:
        p = float(p)
        if p > ftp:
            # Depletion
            w_bal -= (p - ftp)
        else:
            # Reconstitution
            d_p = ftp - p # difference below FTP
            # Time constant tau
            try:
                tau = 546.0 * math.exp(-0.01 * d_p)
                # Keep tau realistic
                if tau < 1.0:
                    tau = 1.0
            except OverflowError:
                tau = 9999.0
            
            # Recharge step
            w_bal = w_prime_initial - (w_prime_initial - w_bal) * math.exp(-1.0 / tau)
            
        # Ensure we don't drop past a structural minimum of negative values for tracking,
        # but let's record the raw values. If it goes below zero, flag depletion.
        if w_bal <= 0:
            depleted = True
            
        wbal_series.append(int(round(w_bal)))

    return wbal_series, depleted
