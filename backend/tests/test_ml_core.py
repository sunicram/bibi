import pytest
from datetime import date
from app.ml.metrics import calculate_normalized_power, calculate_intensity_factor, calculate_tss, calculate_aerobic_decoupling
from app.ml.pmc import calculate_next_day_pmc, calculate_history_pmc
from app.ml.wbal import calculate_wbal_series
from app.ml.wellness import calculate_z_score, determine_readiness_tier, calculate_sleep_debt
from app.ml.policy import PolicyEngine

# --- Test metrics.py ---
def test_normalized_power_steady_state():
    # Steady 200W ride should have NP close to 200W
    power = [200] * 300
    np_val = calculate_normalized_power(power)
    assert abs(np_val - 200.0) < 1.0

def test_normalized_power_variable():
    # Variable ride should have NP > Average Power (e.g., 5-minute blocks)
    power = [150] * 300 + [250] * 300
    avg_power = sum(power) / len(power)
    np_val = calculate_normalized_power(power)
    assert np_val > avg_power

def test_tss_calculation():
    # 1 hour (3600s) at 200W NP with FTP of 200 (IF=1.0) should be exactly 100 TSS
    tss = calculate_tss(3600, 200.0, 1.0, 200)
    assert tss == 100

def test_aerobic_decoupling():
    # Steady HR and Power -> 0% decoupling
    power = [200] * 200
    hr = [150] * 200
    dec = calculate_aerobic_decoupling(power, hr)
    assert abs(dec) < 0.1

# --- Test pmc.py ---
def test_pmc_calculations():
    # Test next day transition with 100 TSS
    ctl, atl, tsb = calculate_next_day_pmc(0.0, 0.0, 100.0)
    assert abs(ctl - 100.0/42.0) < 0.01
    assert abs(atl - 100.0/7.0) < 0.01
    assert tsb == ctl - atl

def test_pmc_history():
    history = [
        (date(2026, 6, 1), 100.0),
        (date(2026, 6, 3), 50.0)
    ]
    pmc = calculate_history_pmc(history, starting_ctl=50.0, starting_atl=40.0)
    assert len(pmc) == 3 # June 1, 2, 3
    assert pmc[0]["tss"] == 100.0
    assert pmc[1]["tss"] == 0.0
    assert pmc[2]["tss"] == 50.0

# --- Test wbal.py ---
def test_wbal_depletion():
    # Riding above FTP (200W) at 300W for 10 seconds should deplete 1000 Joules
    power = [300] * 10
    wbal, depleted = calculate_wbal_series(power, ftp=200, w_prime_initial=20000)
    assert wbal[-1] == 19000
    assert not depleted

def test_wbal_full_depletion():
    # Riding above FTP (200W) at 400W for 150 seconds should deplete 30,000 Joules (w_prime is 20,000)
    power = [400] * 150
    wbal, depleted = calculate_wbal_series(power, ftp=200, w_prime_initial=20000)
    assert depleted
    assert wbal[-1] <= 0

# --- Test wellness.py ---
def test_z_score():
    past = [50.0, 60.0, 70.0, 50.0, 60.0, 70.0]
    z = calculate_z_score(90.0, past)
    assert z > 0.0

def test_readiness_tiers():
    # Normal readiness
    assert determine_readiness_tier(0.0, 0.0) == "green"
    # HRV drop -> Red
    assert determine_readiness_tier(-1.6, 0.0) == "red"
    # RHR spike -> Red
    assert determine_readiness_tier(0.0, 1.6) == "red"
    # Mild stress -> Yellow
    assert determine_readiness_tier(-0.8, 0.0) == "yellow"

def test_sleep_debt():
    history = [480, 480, 480] # 8 hours each
    debt = calculate_sleep_debt(history, 540) # target 9 hours
    assert debt == 180 # 60 mins short per night * 3 nights

# --- Test policy.py ---
def test_policy_engine_red_tier():
    intervals = [
        {"type": "warmup", "duration_seconds": 600, "target_power_pct": 60},
        {"type": "active", "duration_seconds": 240, "target_power_pct": 115}, # High intensity VO2Max
        {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 55}
    ]
    
    modified, rules, exp = PolicyEngine.enforce_readiness_rules("red", intervals, hrv_z=-1.6, rhr_z=1.6)
    
    assert "RED_TIER_REMOVE_HIGH_INTENSITY" in rules
    # VO2max (115%) should be scaled to Active Recovery (55%)
    assert modified[1]["target_power_pct"] == 55
    assert modified[1]["title"] == "Recovery Interval"

def test_policy_engine_yellow_tier():
    intervals = [
        {"type": "warmup", "duration_seconds": 600, "target_power_pct": 60},
        {"type": "active", "duration_seconds": 600, "target_power_pct": 90}, # SST block
        {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 55}
    ]
    
    modified, rules, exp = PolicyEngine.enforce_readiness_rules("yellow", intervals, hrv_z=-0.8, rhr_z=0.0)
    
    assert "YELLOW_TIER_SCALED_INTENSITY" in rules
    # SST block (90%) should be scaled down by 10% (90% * 0.9 = 81%)
    assert modified[1]["target_power_pct"] == 81

def test_policy_weekly_tss_cap():
    # Target 400. Proposed 500 (+25% spike). Should cap to 480 (+20%)
    capped, rules, exp = PolicyEngine.enforce_weekly_tss_guardrail(400.0, 500.0, 0.20)
    assert capped == 480.0
    assert "WEEKLY_TSS_SPIKE_CAP" in rules

# --- Test new functions (TEQ, WS, Simplified ReadyScore) ---
def test_teq_score_steady():
    from app.ml.metrics import calculate_teq_score
    # Target power 200W (FTP = 200, target_power_pct = 100)
    intervals = [
        {"duration_seconds": 60, "target_power_pct": 100}
    ]
    # Perfect execution (all 200W)
    power = [200] * 60
    score = calculate_teq_score(power, intervals, ftp=200)
    assert score == 100.0

def test_teq_score_deviation():
    from app.ml.metrics import calculate_teq_score
    intervals = [
        {"duration_seconds": 60, "target_power_pct": 100}
    ]
    # Under-target execution (all 150W -> 25% error)
    power = [150] * 60
    score = calculate_teq_score(power, intervals, ftp=200)
    # The first 10 seconds is transition buffer (ignored).
    # From sec 10 to 59, the power is 150W.
    # Target range is [200*0.95, 200*1.05] = [190, 210].
    # Error for each second = (190 - 150) / 190 = 40/190 = 0.2105
    # So TEQ should be ~ 78.9%
    assert abs(score - 78.94) < 0.1

def test_teq_sprints():
    from app.ml.metrics import calculate_teq_score
    intervals = [
        {"duration_seconds": 30, "target_power_pct": 150} # sprint < 1 min
    ]
    # FTP = 200 -> target = 300W. tolerance range = [285, 315]
    # Average power is 300W
    power = [300] * 30
    score = calculate_teq_score(power, intervals, ftp=200)
    assert score == 100.0

def test_workout_stimulus_score():
    from app.ml.metrics import calculate_workout_stimulus_score
    intervals = [
        {"duration_seconds": 600, "target_power_pct": 110}, # 10 mins Z5+ -> W = 2.0 -> WS_int = 20.0
        {"duration_seconds": 1200, "target_power_pct": 90}   # 20 mins Z3/Z4 -> W = 1.5 -> WS_int = 30.0
    ]
    # Total WS = 20.0 + 30.0 + 100 * 0.2 = 70.0
    score = calculate_workout_stimulus_score(intervals, tss=100.0)
    assert score == 70.0

def test_simplified_readyscore():
    from app.ml.wellness import calculate_simplified_readyscore
    # Last 3 workouts: one too hard (3), two ok (2)
    # rpe_scores: 30, 100, 100 -> RPE trend = 30*0.5 + 100*0.3 + 100*0.2 = 15 + 30 + 20 = 65
    # morning feeling: 4 -> 4 * 20 = 80
    # last reserve: 1 (No) -> 0
    # ReadyScore = 65 * 0.4 + 80 * 0.4 + 0 * 0.2 = 26 + 32 + 0 = 58
    score = calculate_simplified_readyscore([3, 2, 2], morning_feeling=4, last_reserve=1)
    assert score == 58.0

