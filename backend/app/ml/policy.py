from typing import Dict, List, Any, Tuple

class PolicyEngine:
    """The Deterministic Policy Engine.
    
    Houses the safety constraints that govern all plan modifications.
    Takes output from ML Core & LLM suggestions, filters them, and outputs
    the final safe state. These rules override LLM proposals.
    """
    
    @staticmethod
    def enforce_readiness_rules(
        readiness_tier: str, 
        intervals_json: List[Dict[str, Any]],
        hrv_z: float,
        rhr_z: float
    ) -> Tuple[List[Dict[str, Any]], List[str], str]:
        """Enforces heart rate / HRV readiness safety constraints on a single workout main set.
        
        Rules:
        - RED: Strip all Zone 4 (Threshold), Zone 5 (VO2Max), Zone 6 (Anaerobic) intervals.
               Convert them to Zone 1 (Recovery) or Zone 2 (Endurance).
               If extremely suppressed (HRV Z <= -2.0 and RHR Z >= 2.0), convert entire workout to Rest.
        - YELLOW: Suggest reduction of intensity of intervals by 10-15% (scaled power targets).
        - GREEN: Maintain intervals as prescribed.
        """
        rules_triggered = []
        modified_intervals = []
        explanation = ""
        
        if readiness_tier == "red":
            # Severe suppression check
            if hrv_z <= -2.0 and rhr_z >= 2.0:
                rules_triggered.append("CRITICAL_RED_FORCE_REST")
                # Return empty list representing a rest day (no intervals)
                explanation = "Your recovery signals indicate severe physiological stress (HRV Z <= -2.0, RHR Z >= 2.0). A rest day is safety-enforced."
                return [], rules_triggered, explanation
                
            rules_triggered.append("RED_TIER_REMOVE_HIGH_INTENSITY")
            explanation = "Your recovery signals dropped significantly (Red readiness). All high-intensity blocks have been converted to easy recovery (Zone 1)."
            
            # Filter intervals to remove Zone 4/5/6 blocks
            for block in intervals_json:
                block_type = block.get("type", "active")
                target_power_pct = block.get("target_power_pct", 100)
                
                # Coggan Zone 3 ends around 90% FTP. Any active target > 90% FTP is high intensity.
                if block_type == "active" and target_power_pct > 90:
                    # Convert to active recovery (55% FTP)
                    modified_block = block.copy()
                    modified_block["target_power_pct"] = 55
                    modified_block["title"] = "Recovery Interval"
                    modified_intervals.append(modified_block)
                else:
                    modified_intervals.append(block)
                    
        elif readiness_tier == "yellow":
            rules_triggered.append("YELLOW_TIER_SCALED_INTENSITY")
            explanation = "Your recovery signals show mild stress (Yellow readiness). High-intensity intervals are dialed down by 10% to prevent overtraining."
            
            for block in intervals_json:
                block_type = block.get("type", "active")
                target_power_pct = block.get("target_power_pct", 100)
                
                # Scale down any intensity > 85% FTP by 10%
                if block_type == "active" and target_power_pct > 85:
                    modified_block = block.copy()
                    modified_block["target_power_pct"] = int(round(target_power_pct * 0.90))
                    modified_intervals.append(modified_block)
                else:
                    modified_intervals.append(block)
        else:
            # Green tier - pass-through
            modified_intervals = intervals_json
            
        return modified_intervals, rules_triggered, explanation

    @staticmethod
    def enforce_weekly_tss_guardrail(
        planned_weekly_tss: float,
        proposed_weekly_tss: float,
        max_tss_change_pct: float = 0.20
    ) -> Tuple[float, List[str], str]:
        """Limits changes in weekly TSS to +/- 20% to prevent excessive spikes or drops.
        
        If proposed weekly TSS is outside the guardrail bounds, caps it at the limit.
        """
        rules_triggered = []
        explanation = ""
        capped_tss = proposed_weekly_tss
        
        if planned_weekly_tss <= 0:
            return proposed_weekly_tss, rules_triggered, explanation
            
        max_allowed = planned_weekly_tss * (1.0 + max_tss_change_pct)
        min_allowed = planned_weekly_tss * (1.0 - max_tss_change_pct)
        
        if proposed_weekly_tss > max_allowed:
            rules_triggered.append("WEEKLY_TSS_SPIKE_CAP")
            capped_tss = max_allowed
            explanation = f"Proposed weekly training volume is capped at {capped_tss:.1f} TSS to prevent ramp volume spikes."
        elif proposed_weekly_tss < min_allowed:
            rules_triggered.append("WEEKLY_TSS_DROP_FLOOR")
            capped_tss = min_allowed
            explanation = f"Proposed weekly training volume is set to a minimum floor of {capped_tss:.1f} TSS to maintain base training."
            
        return float(capped_tss), rules_triggered, explanation

    @staticmethod
    def enforce_ctl_ramp_cap(
        current_ctl: float,
        proposed_ctl_after_week: float,
        max_ramp_rate: float = 7.0
    ) -> Tuple[bool, List[str]]:
        """Ensures that the planned workouts do not cause the CTL to ramp faster than +7 points per week."""
        rules_triggered = []
        ramp_rate = proposed_ctl_after_week - current_ctl
        
        if ramp_rate > max_ramp_rate:
            rules_triggered.append("CTL_RAMP_RATE_CAP_TRIGGERED")
            return True, rules_triggered
            
        return False, rules_triggered
