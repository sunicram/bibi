# BIBI — Be Better
## Cycling Training Platform
### Product Requirements Document — v2.0 (Consolidated)

---

> **Document status:** Consolidated specification, ready for architectural planning
> **Supersedes:** PRD v1.0; consolidated proposals v1.1 (OpenAI) and v1.2 (Nemotron/Perplexity); commentary from Copilot, Gemini, Perplexity
> **Last updated:** June 2026
> **Primary scope:** v1 — Web application (Friends & Family MVP)
> **Future scope:** v2 — Native mobile apps
> **Positioning:** Fully autonomous, cost-optimised AI cycling coach with a two-model safety architecture

---

## What changed in v2.0

This version consolidates four independent reviews. The single biggest architectural change:

**The human coaching panel (3 trainers + coordinator) is removed.** It is operationally unviable for a Friends & Family MVP with no budget for coaching staff, and all four reviewers independently recommended against it for the core product. It is replaced by a **two-model AI architecture (Coach + Reviewer) governed by a deterministic policy engine** — fully autonomous, cost-controlled, and safe.

| Area | v2.0 decision | Source consensus |
|---|---|---|
| Coaching intelligence | Two-model AI: Coach (Actor) + Reviewer (Critic) + deterministic Policy Engine | All four reviewers |
| Human panel | Removed from core; optional premium extension in distant future only | All four reviewers |
| Cost model | Cheap LLM for daily Coach chat; expensive LLM for Reviewer, invoked only on structural changes | Gemini |
| Wellness | Personal rolling baselines (7/21-day) + Z-scores + Green/Yellow/Red tiers; never raw values. Sources: Garmin (native) + Apple Watch (via iPhone bridge app) | Gemini, Perplexity, v1.2 |
| Advanced modeling | W′/W′bal energy model in ML Core (enhancement; can defer to v1.x) | Gemini, v1.2 |
| Inbound integration | Intervals.icu primary; Strava fallback; manual FIT recovery | All four reviewers |
| Feedback UX | Compact 3-step inline-button flow; optional voice notes via Whisper | Gemini, v1.2 |
| Scope | Web-only v1, API-first; native mobile v2 | v1.1, v1.2 |

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Product Scope](#2-product-scope)
3. [User Management](#3-user-management)
4. [Onboarding Interview](#4-onboarding-interview)
5. [Training Plan System](#5-training-plan-system)
6. [AI Coaching Architecture](#6-ai-coaching-architecture)
7. [Wellness Intelligence](#7-wellness-intelligence)
8. [Advanced Performance Modeling — W′bal](#8-advanced-performance-modeling--wbal)
9. [Plan Amendment Governance](#9-plan-amendment-governance)
10. [Post-Workout Feedback](#10-post-workout-feedback)
11. [Metrics & Analytics](#11-metrics--analytics)
12. [Integration Architecture](#12-integration-architecture)
13. [n8n Automation Workflows](#13-n8n-automation-workflows)
14. [Notifications & Communication](#14-notifications--communication)
15. [Workout & Plan Export](#15-workout--plan-export)
16. [Mobile-Ready Architecture](#16-mobile-ready-architecture)
17. [Non-Functional Requirements](#17-non-functional-requirements)
18. [Technology Stack](#18-technology-stack)
19. [Monetization](#19-monetization)
20. [Implementation Roadmap](#20-implementation-roadmap)
21. [Open Decisions & Future Considerations](#21-open-decisions--future-considerations)

---

## 1. Product Overview

### 1.1 Vision

Bibi (Be Better) is a web-based cycling training platform that combines structured training plan generation, adaptive AI coaching, and seamless device integration into a single product. It is designed for cyclists who already train with power and/or heart rate data and want something more dynamic than a static plan. Bibi continuously learns from workouts, wellness signals, subjective feedback, and adherence patterns to refine its coaching over time.

**v2.0 product statement:**

> Bibi uses a two-layer AI coaching system. A **Coach model** produces training guidance and proposes plan adjustments, while an independent **Reviewer model** validates safety, consistency, and policy compliance. A **deterministic policy engine** has final authority over hard safety constraints and keeps the system conservative whenever athlete well-being is uncertain. Version 1 is delivered as a web application; native mobile apps are part of the v2 roadmap.

### 1.2 Friends & Family MVP Positioning

v1 is built as a **Friends & Family MVP** — a closed group of users, no paid human coaching staff, and tight cost control. This shapes three core principles:

1. **Fully autonomous** — no human in the loop is required for any routine operation
2. **Cost-optimised** — expensive LLM calls are reserved for safety-critical decisions only
3. **Safety-first** — a deterministic rules engine prevents the AI from ever producing a physiologically dangerous recommendation

### 1.3 Core Value Proposition

- Personalised plans from onboarding data and methodology choice
- Adaptive coaching that interprets workouts and explains its decisions in plain language
- Safe plan evolution via a two-model AI architecture plus deterministic safety rules
- Seamless device ecosystem integration, with Intervals.icu as the primary sync layer
- A Telegram-first conversational workflow for low-friction feedback and coaching

### 1.4 Core Training Loop

```
ONBOARDING INTERVIEW
        │
        ▼
PLAN RECOMMENDATION (duration + methodology)
        │
        ▼
PLAN GENERATION → WORKOUTS VISIBLE IN WEB APP
        │
        ▼
EXPORT / SYNC TO DEVICE (via Intervals.icu → Garmin / Wahoo)
        │
        ▼
COMPLETE RIDE → IMPORT ACTIVITY + WELLNESS SIGNALS
        │
        ▼
ML CORE ANALYSIS (metrics, baselines, Z-scores, W′bal, anomaly flags)
        │
        ▼
COMPACT FEEDBACK (Telegram — 3 taps + optional voice note)
        │
        ▼
AI COACH SUMMARY  ── (drafts amendment if needed) ──►  AI REVIEWER
        │                                                  │
        │                                          DETERMINISTIC POLICY ENGINE
        │                                          (final safety authority)
        ▼                                                  │
APPLY AMENDMENT (versioned + decision object) ◄────────────┘
        │
        ▼
[LOOP UNTIL PLAN END] → ARCHIVE PLAN → SEED NEXT PLAN
```

### 1.5 Target User

Committed cyclists using Garmin, Wahoo, or similar ecosystems, training toward FTP improvement, endurance goals, or a specific event. Ideal user follows an 8–16 week structure and regularly syncs rides and provides lightweight feedback.

---

## 2. Product Scope

### 2.1 v1 Scope (Web Application Only)

The v1 web app must be fully responsive on desktop and mobile browsers. No native mobile app in v1.

Included:
- User registration and authentication
- Onboarding interview
- Plan recommendation and generation (3 methodologies × 3 durations)
- Plan calendar, workout detail views, plan history
- Workout import and export
- Telegram-based feedback and coaching communication
- Two-model AI workflow (Coach + Reviewer) + deterministic policy layer
- Wellness ingestion with personal baselines and readiness interpretation
- Core analytics and plan amendment logic

### 2.2 Explicitly Out of Scope for v1

- Native mobile application (v2)
- Human coaching panel (removed entirely; possible distant premium extension only)
- Multi-sport expansion
- Marketplace for human coaches
- Advanced social features
- Communication channels beyond Telegram and email

### 2.3 v2 Direction

Native iOS and Android apps planned for v2. The v1 system must remain **API-first** so a future mobile client reuses the same backend, auth, plan, notification, and export services without redesigning business logic.

---

## 3. User Management

### 3.1 Registration & Authentication

- Email + password registration; email verification; password reset
- JWT authentication with access tokens (15–60 min) and refresh tokens (30 days)
- Server-side storage of all third-party OAuth tokens (Intervals.icu, Strava)
- Multi-session support at the API layer (future-ready for v2 mobile)

### 3.2 User Profile

Initially populated from onboarding; editable later. Any update to physiologically relevant fields (FTP, weight, zones, target event, training availability) triggers plan re-evaluation.

| Category | Fields |
|---|---|
| Identity | Email, display name, photo |
| Personal | Age, weight, height, gender |
| Physiology | FTP, FTP/kg, VO2max (if known), max HR, resting HR, HR zones, power zones, thresholds, W′ (if known/estimated) |
| Equipment — cycling | Bike computer (Garmin Edge / Wahoo ELEMNT / other), power meter, HR device, cadence sensor, smart trainer, indoor app |
| Equipment — wearable | Wearable (Garmin Fenix / Forerunner / Venu / Apple Watch / other / none), wellness data availability flag, HRV metric type (RMSSD / SDNN), wellness bridge app (Apple Watch only) |
| Activity profile | Training history, weekly availability, long ride day, preferred training time |
| Health | Known issues, mobility limitations, dietary profile |
| Integrations | Intervals.icu token, Strava token |
| Consents | Wellness import consent, anonymised ML training consent (opt-in) |
| Preferences | Timezone, notifications, Telegram chat ID, export format |

### 3.3 Plan Ownership Rules

- One active plan at a time
- Cancel → archived; Complete → archived; archived plans remain in history
- New plan can be created after archiving
- New plans seeded with updated athlete state and prior model learnings

### 3.4 Account Deletion

GDPR-compliant full removal: profile, plans, plan versions, workouts, FIT files, wellness records, coaching history, feedback, decision objects. Data export offered before deletion. Raw S3 payloads purged within 30 days.

---

## 4. Onboarding Interview

Mandatory before plan generation. Seeds the athlete profile, cold-start recommendation, and initial safety baselines.

### 4.1 Personal & Health Data
Age, weight, height; occupation activity level; known health conditions; mobility restrictions.

### 4.2 Training History
Years cycling; previous sports; teenage activity level; current weekly frequency and hours; typical terrain; rider preference (shorter/faster vs longer/steady); commuting behaviour.

### 4.3 Recovery & Nutrition
Eating approach; typical sleep duration (used as the baseline for sleep-debt calculation); sleep quality; HRV tracking availability; recovery devices/readiness systems used.

### 4.4 Equipment
Cycling computer; **wearable device** (Garmin Fenix/Forerunner/Venu, Apple Watch, other, or none — determines wellness data availability and pathway, see Section 7); power meter; HR monitor; cadence sensor; smart trainer; indoor platform.

For **Apple Watch** users, onboarding includes an extra guided step to set up a wellness bridge app (e.g. HealthFit or Intervals.icu Companion) on their iPhone, since Apple Health does not sync to Intervals.icu natively (see Section 7.2).

### 4.5 Current Metrics
FTP; VO2max (if known); max HR; resting HR; existing HR/power zones (if known); W′ (optional, if known); preferred evaluation KPI (power / HR / both).

### 4.6 Goals & Constraints
Primary goal (FTP gain / event / endurance / weight loss / general fitness / maintenance); optional event (name, date, distance, elevation); preferred duration (8/12/16 weeks); days/week available; long ride day; max session duration; indoor availability.

### 4.7 Consents
- Wellness import consent (unlocks wellness-based coaching)
- Anonymised ML training consent (opt-in, optional)
- Timestamps stored; editable in settings at any time

---

## 5. Training Plan System

### 5.1 Plan Generation Flow

1. User completes onboarding
2. System recommends a duration and methodology with reasoning
3. Three methodologies shown with plain-language explanations + suitability notes + compatibility warnings
4. User selects a methodology
5. System generates the plan
6. User reviews and confirms
7. Plan becomes active in the calendar

### 5.2 Training Methodologies

| Methodology | Principle | Best for |
|---|---|---|
| **Polarized (80/20)** | ~80% low intensity (Z1–Z2), ~20% high (Z4–Z5), minimal Z3 | Experienced riders with more training time and good data |
| **Sweet Spot** | Most time in Z3–Z4 (88–93% FTP); high stimulus per hour | Time-crunched riders; fastest FTP build (higher fatigue risk) |
| **Traditional Periodization** | Base → Build → Peak → Taper progression | Event-oriented riders, beginners, return after break |

### 5.3 Plan Durations

| Duration | Label | Recovery weeks | FTP tests | Best for |
|---|---|---|---|---|
| 8 weeks | Short Block | 1 | 2 (start + end) | Maintenance, sharpening, return after break |
| 12 weeks | Standard Block | 2 | 2 (start + wk 7) | Balanced improvement, event ~3 months out |
| 16 weeks | Full Block | 2 | 3 (start + wk 8 + end) | Major improvement, full base-to-peak build |

Compatibility warnings shown (non-blocking) when goal and duration mismatch. If a target event date is declared, the system calculates backward and highlights the best-fit duration.

### 5.4 Phase Structure Per Duration

**8-week**
```
Wk 1: FTP test + adaptation | Wk 2–4: Build | Wk 4: deload
Wk 5–7: Peak | Wk 8: Taper + final FTP test
```
> Coach note: "8 weeks can't build a full aerobic base — this plan sharpens your current fitness."

**12-week**
```
Wk 1–4: Base | Wk 3: deload | Wk 5–9: Build | Wk 7: FTP retest
Wk 8: deload | Wk 10–11: Peak | Wk 12: Taper + final FTP test
```

**16-week**
```
Wk 1–6: Base | Wk 3: deload | Wk 7–12: Build | Wk 8: FTP retest
Wk 10: deload | Wk 13–15: Peak | Wk 16: Taper + final FTP test
```

### 5.5 Workout Types
Recovery ride (Z1), Endurance/Z2, Tempo (Z3), Sweet spot (Z3–Z4), Threshold (Z4), VO2max (Z5), Anaerobic/sprint (Z6–Z7), FTP test.

### 5.6 Workout Structure
Each workout: optional warm-up; main set (N intervals — duration, power target % FTP ±5% range, HR reference, effort type); optional recovery intervals; optional cooldown; human-readable title; stable workout ID (W001…).

### 5.7 Plan Visualization
Calendar view; chronological list view; weekly summary (TSS, hours, zone distribution, phase); workout detail page (interval graph); phase overview; archive view; **plan version indicator** with change log.

### 5.8 Plan Versioning
Every amendment increments the plan version and links a decision object (Section 9.4). Version history viewable in the web app: version number, timestamp, source (`auto` / `reviewer_approved`), diff, and reasoning summary. Users see what changed and why; they cannot revert.

### 5.9 Plan Chaining
Completed plans seed the next: updated FTP/profile, ending CTL as new starting baseline, learned personal response patterns, updated methodology recommendation, AI summary of the prior cycle, and the last 30 days of wellness baselines carried into anomaly thresholds.

---

## 6. AI Coaching Architecture

### 6.1 Four-Component Architecture

Bibi's intelligence is a layered system. Numerical decisions never live inside an LLM.

```
┌──────────────────────────────────────────────────────────────────┐
│  1. ML CORE (Python / FastAPI — deterministic, free to run)        │
│     Parses FIT, computes TSS/IF/NP/CTL/ATL/TSB, wellness Z-scores, │
│     W′bal, anomaly flags, adherence, candidate amendment actions.  │
└───────────────────────────┬──────────────────────────────────────┘
                            │ structured numeric JSON + hard flags
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  2. DETERMINISTIC POLICY ENGINE (Python rules — final authority)   │
│     Hard safety constraints. Overrides both LLMs. Cannot be        │
│     overridden by any AI output.                                   │
└───────────────────────────┬──────────────────────────────────────┘
                            │ constraints + permitted action space
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  3. AI COACH — "Actor" (cheap LLM: Claude Haiku / GPT-4o-mini)     │
│     User-facing. Daily chat, workout summaries, motivation,        │
│     drafts candidate amendments as structured JSON.                │
└───────────────────────────┬──────────────────────────────────────┘
                            │ candidate structural amendment (JSON)
                            ▼ (invoked ONLY on structural changes)
┌──────────────────────────────────────────────────────────────────┐
│  4. AI REVIEWER — "Critic" (smart LLM: Claude Sonnet / GPT-4o)     │
│     Background safety auditor. Validates Coach's structural        │
│     proposals against ML Core metrics + policy constraints.        │
│     Returns: approve | modify | reject (structured JSON).          │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 Design Principles

- LLMs do not own raw numerical decision-making — all quantitative work is in ML Core
- The Coach is optimised for communication quality; the Reviewer for safety and consistency
- Hard policy rules override both LLMs
- The expensive Reviewer model runs **only** when a structural plan change is proposed — daily chat is handled by the cheap Coach model (cost control)

### 6.3 ML Core Responsibilities (deterministic, no LLM)

- Parse FIT files; compute TSS, IF, NP, power/HR zone distribution, decoupling, cadence
- Maintain CTL, ATL, TSB
- Compute wellness rolling baselines and Z-scores (Section 7)
- Compute W′bal and detect battery-depletion / underestimated-FTP events (Section 8)
- Run anomaly detection (overtraining, illness, injury, burnout signals)
- Compute plan adherence
- Generate candidate amendment **actions** as hard flags (e.g. `[REDUCE_VOLUME_30]`, `[REST_DAY_REQUIRED]`, `[CONVERT_TO_Z1]`)

### 6.4 AI Coach Responsibilities (Actor — cheap model)

- Interpret structured ML Core output (never raw telemetry)
- Produce post-workout summaries
- Answer free-text user questions in Telegram and web chat
- Interpret loose / emotional comments and voice-note transcripts
- Draft candidate plan amendments as structured JSON
- Translate ML Core flags and policy constraints into supportive, plain language

The Coach does not decide *what* to change when a hard flag is present — it decides *how to communicate* the required change. It may propose discretionary changes within the permitted action space, which then go to the Reviewer.

### 6.5 AI Reviewer Responsibilities (Critic — smart model)

- Validate structural amendments before publication
- Check guardrail compliance against ML Core metrics + policy constraints
- Detect contradictions or over-aggressive changes
- Confirm the Coach has not left hard intervals in place when wellness/fatigue signals are negative
- Return a structured verdict: `approve` / `modify` / `reject` with rationale

### 6.6 Reviewer Trigger Conditions

The Reviewer is invoked only when:
- The change affects **structure** (not just wording)
- Weekly TSS impact crosses the guardrail threshold
- Multiple signals indicate fatigue, illness, or injury risk
- A key session is added, removed, or swapped
- Signals are contradictory and conservative validation is needed

All non-structural messages (daily chat, summaries, motivation) bypass the Reviewer entirely — keeping cost minimal.

### 6.7 Cost Model

| Interaction | Model used | Frequency | Relative cost |
|---|---|---|---|
| Daily chat, summaries, feedback interpretation | Coach (cheap) | Many per week | Very low |
| Structural amendment validation | Reviewer (smart) | Rare (key decisions only) | Moderate, infrequent |
| Quantitative analysis (all of it) | ML Core (no LLM) | Every activity | Zero LLM cost |

Net effect: a premium-feeling autonomous coach at a few cents per user per day.

### 6.8 No Human Panel

Bibi v1 does not include a standing panel of human coaches. The architecture is fully AI-driven (two models + deterministic rules). A human element is explicitly out of scope and would only ever be a distant premium extension, never a dependency.

---

## 7. Wellness Intelligence

### 7.1 Philosophy

Raw wellness numbers are never interpreted in isolation. An HRV of 40 ms may signal deep fatigue in one athlete and full freshness in another. Readiness logic relies on **deviation from the athlete's own baseline**, trend direction, data quality, and multi-signal confirmation.

### 7.2 Data Source

Wellness data comes from the athlete's **wearable**. Two wearable families are supported in v1, with different data pathways:

**Garmin (Fenix / Forerunner / Venu) — native pathway**
Syncs to Intervals.icu natively. Bibi reads it from ICU for the activity day plus the 2 prior days. Zero extra setup beyond connecting Intervals.icu. Provides the full metric set including Body Battery and RMSSD HRV.

**Apple Watch — bridge pathway**
Apple Health data lives in HealthKit on the iPhone and has no web API, so it does **not** sync to Intervals.icu natively. Apple Watch users set up a lightweight **bridge app** on their iPhone (e.g. HealthFit, Intervals.icu Companion) during onboarding. The bridge reads HealthKit each morning and pushes wellness data to the Intervals.icu wellness log, which Bibi then reads through the same pipeline as Garmin. Bibi builds nothing Apple-specific for v1 — it relies on the established bridge + ICU path.

**Semantics differences handled by ML Core:**
- **HRV type:** Garmin reports RMSSD; Apple natively reports SDNN (bridges can also compute overnight RMSSD). Because readiness logic is a Z-score against the athlete's *own* baseline, both work — but ML Core stores the HRV metric type per record and never mixes SDNN and RMSSD within a single baseline.
- **Body Battery:** Garmin-only; Apple has no equivalent. It remains an optional, nullable supplementary signal. The Green/Yellow/Red tier system is driven primarily by HRV and resting-HR Z-scores, both available from Apple, so the tier system functions for both wearables.

The cycling computer (Garmin Edge / Wahoo ELEMNT) does not capture wellness data. Users without any compatible wearable fall back to manual subjective feedback only; ML Core degrades gracefully.

> **v2 note:** Bibi's native iOS app can read HealthKit directly, removing the bridge-app dependency for Apple Watch users.

### 7.3 Wellness Inputs

Resting heart rate; HRV (RMSSD); sleep total minutes; sleep efficiency; sleep stages; sleep debt; Body Battery (or equivalent readiness score); stress score; overnight average HR; resting respiration rate; SpO2; skin temperature delta; weight (if tracked).

### 7.4 Personal Baselines & Z-Scores

ML Core maintains, per athlete, per metric, rolling windows and standardised deviation:

| Computed field | Definition |
|---|---|
| `hrv_baseline_7d` | 7-day rolling mean of HRV RMSSD |
| `hrv_baseline_21d` | 21-day rolling mean (reference trend) |
| `hrv_z_score` | (today − 7d mean) ÷ 7d standard deviation |
| `rhr_baseline_7d` | 7-day rolling mean of resting HR |
| `rhr_z_score` | standardised resting HR deviation |
| `sleep_debt_minutes` | cumulative sleep deficit over last 3 nights vs onboarding-declared need |

**Z-score formula:**
```
HRV_Z = (HRV_today − HRV_mean_7d) / HRV_stddev_7d
```

### 7.5 Readiness Tier System (Green / Yellow / Red)

ML Core maps Z-scores to a readiness tier that the Policy Engine acts on:

| Tier | Condition | System action |
|---|---|---|
| 🟢 **Green** | HRV Z ≥ −0.5 | No restriction. Full plan as prescribed. |
| 🟡 **Yellow** | −1.5 < HRV Z < −0.5 | ML Core auto-recommends 10–15% intensity reduction. Coach suggests a light modification. |
| 🔴 **Red** | HRV Z ≤ −1.5 **or** RHR Z ≥ +1.5 | Autonomic suppression. Policy Engine **automatically removes** Z4/Z5/VO2max from the next session, converting it to Z1 recovery or rest. Reviewer auto-approves the safe path. |

> Tier thresholds are configurable in the safety specification but default to the above conservative values. Critical (Red) actions require either `measured` data or multi-day corroboration before triggering.

### 7.6 Data Quality Rules

Each wellness record carries a quality flag: `measured` / `estimated` / `missing`. Critical plan actions never rely on a single noisy or missing signal — ML Core requires `measured` data or a corroborated multi-day trend before driving high-impact changes.

### 7.7 Wellness Data Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "wellness_data",
  "type": "object",
  "required": ["user_id", "date", "device_source", "sync_timestamp"],
  "properties": {
    "user_id":              { "type": "string", "format": "uuid" },
    "date":                 { "type": "string", "format": "date" },
    "device_source":        { "type": "string", "enum": ["garmin","apple_health","intervals.icu","strava","other"] },
    "device_model":         { "type": "string" },
    "sync_timestamp":       { "type": "string", "format": "date-time" },
    "resting_heart_rate":   { "type": ["integer","null"], "minimum": 20, "maximum": 220 },
    "hrv_rmssd":            { "type": ["number","null"], "minimum": 0 },
    "hrv_sdnn":             { "type": ["number","null"], "minimum": 0 },
    "hrv_type":             { "type": ["string","null"], "enum": ["rmssd","sdnn",null] },
    "sleep_total_minutes":  { "type": ["integer","null"], "minimum": 0 },
    "sleep_efficiency":     { "type": ["number","null"], "minimum": 0, "maximum": 1 },
    "sleep_stages":         { "type": ["object","null"] },
    "body_battery":         { "type": ["integer","null"], "minimum": 0, "maximum": 100 },
    "stress_score":         { "type": ["number","null"], "minimum": 0 },
    "overnight_avg_hr":     { "type": ["integer","null"], "minimum": 20, "maximum": 220 },
    "resting_resp_rate":    { "type": ["number","null"], "minimum": 0 },
    "spo2":                 { "type": ["number","null"], "minimum": 0, "maximum": 100 },
    "skin_temp_delta":      { "type": ["number","null"] },
    "weight_kg":            { "type": ["number","null"], "minimum": 20 },
    "hrv_baseline_7d":      { "type": ["number","null"] },
    "hrv_z_score":          { "type": ["number","null"] },
    "rhr_baseline_7d":      { "type": ["number","null"] },
    "rhr_z_score":          { "type": ["number","null"] },
    "sleep_debt_minutes":   { "type": ["integer","null"] },
    "readiness_tier":       { "type": ["string","null"], "enum": ["green","yellow","red",null] },
    "data_quality_flag":    { "type": "string", "enum": ["measured","estimated","missing"] },
    "raw_payload_s3_key":   { "type": ["string","null"] }
  },
  "additionalProperties": false
}
```

### 7.8 Storage (wellness_daily)

```sql
CREATE TABLE wellness_daily (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id              UUID NOT NULL,
  date                 DATE NOT NULL,
  device_source        TEXT NOT NULL,
  device_model         TEXT,
  sync_timestamp       TIMESTAMPTZ NOT NULL,
  resting_heart_rate   INTEGER,
  hrv_rmssd            DOUBLE PRECISION,
  hrv_sdnn             DOUBLE PRECISION,
  hrv_type             TEXT,            -- 'rmssd' (Garmin) | 'sdnn' (Apple)
  sleep_total_minutes  INTEGER,
  sleep_efficiency     DOUBLE PRECISION,
  sleep_stages         JSONB,
  body_battery         INTEGER,
  stress_score         DOUBLE PRECISION,
  overnight_avg_hr     INTEGER,
  resting_resp_rate    DOUBLE PRECISION,
  spo2                 DOUBLE PRECISION,
  skin_temp_delta      DOUBLE PRECISION,
  weight_kg            DOUBLE PRECISION,
  -- computed baseline/readiness fields
  hrv_baseline_7d      DOUBLE PRECISION,
  hrv_z_score          DOUBLE PRECISION,
  rhr_baseline_7d      DOUBLE PRECISION,
  rhr_z_score          DOUBLE PRECISION,
  sleep_debt_minutes   INTEGER,
  readiness_tier       TEXT,
  data_quality_flag    TEXT,
  raw_payload_s3_key   TEXT,
  version              INTEGER NOT NULL DEFAULT 1,
  is_latest            BOOLEAN NOT NULL DEFAULT TRUE,
  created_at           TIMESTAMPTZ DEFAULT now(),
  updated_at           TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX ux_wellness_user_date_source_version
  ON wellness_daily (user_id, date, device_source, version);
CREATE INDEX ix_wellness_user_date_latest
  ON wellness_daily (user_id, date) WHERE is_latest = TRUE;
```

Store raw device payloads in encrypted S3 referenced by `raw_payload_s3_key`. Maintain 3/7/21-day aggregates as materialized views for low-latency ML Core access. Use TimescaleDB hypertable at scale.

### 7.9 v1 Wellness Sources
v1 supports the **Garmin** ecosystem (native ICU sync) and **Apple Watch** (via iPhone bridge app → ICU). Oura, Whoop, Coros, and Suunto are v1.x / v2 integration work. Source differences are handled per `device_source` and `hrv_type`.

---

## 8. Advanced Performance Modeling — W′bal

> **Status:** ML Core enhancement. Strongly recommended for the "ultra-professional" feel, but not a hard v1 dependency — can defer to v1.x if delivery pressure requires.

### 8.1 What W′ Is

W′ (W-prime, in kilojoules) is a rider's finite energy capacity for work above FTP (critical power) — the anaerobic "battery". It depletes during efforts above FTP and recharges during efforts below it. W′bal is the dynamic, second-by-second model of this battery's state.

### 8.2 Application — Adherence Intelligence

Amateurs often fail to complete hard interval sets (e.g. 4×4 min VO2max) and get flagged "incomplete" by naïve algorithms, causing frustration. ML Core runs differential W′bal analysis on the FIT file instead:

- If the model shows W′bal hit **0 kJ** mid-set (battery fully drained), the athlete gave a true 100% effort, but their **profile FTP or W′ is underestimated**.
- **System action:** rather than penalising, the Coach sends an encouraging message and ML Core flags an FTP/W′ profile correction for review:

> *"I saw you cut the power on the 2nd rep — the maths shows your anaerobic battery hit zero, so you gave everything you had. Great work. I'm bumping your profile up, because you're stronger than we thought."*

### 8.3 Integration

W′bal events are computed in ML Core and exposed as structured flags (e.g. `[WBAL_DEPLETION_EVENT]`, `[FTP_UNDERESTIMATED]`) to the Coach and Reviewer. They never live inside the LLM layer.

---

## 9. Plan Amendment Governance

### 9.1 Philosophy
Adaptive but conservative. Prefer minimal safe changes over frequent oscillation.

### 9.2 Core Guardrails (deterministic)

| Guardrail | Default limit |
|---|---|
| Weekly TSS change per amendment | within ±15–20% of planned weekly TSS |
| Structural amendments per week | 1–2 (further changes limited to minor parameter tweaks) |
| Anti-oscillation | no flip-flopping a key session hard/easy across consecutive days |
| CTL ramp rate cap | +7 CTL points/week |
| Min interval between amendments | 48 hours |
| Conflict handling | when signals conflict, default toward lower intensity / rest |
| Aligned negative readiness | auto-downgrade intensity/volume when Red tier + high fatigue align |

Exact thresholds are configurable in the safety spec but default to these conservative ranges.

### 9.3 Policy Engine Examples
- Block high-intensity sessions when multiple negative readiness signals align (depressed HRV baseline + elevated RHR)
- Convert the next hard workout to endurance/recovery/rest when illness risk is elevated
- Pause structural auto-amendments and hold a safe pattern when critical data is missing or contradictory
- Require Reviewer approval before publishing any amendment exceeding TSS or structural thresholds

### 9.4 Decision Object

Every amendment ends in a structured, immutable decision object:

```json
{
  "amendment_id": "uuid",
  "plan_id": "uuid",
  "plan_version": 5,
  "decision_type": "auto_applied | reviewer_approved | reviewer_modified | rejected",
  "trigger_type": "ml_flag | anomaly | user_request | wellness_red",
  "risk_level": "low | medium | high",
  "ml_inputs": {
    "ctl": 72.3, "atl": 58.1, "tsb": 14.2,
    "hrv_z_score": -1.7, "rhr_z_score": 1.6,
    "readiness_tier": "red", "wbal_event": true,
    "wellness_data_quality": "measured"
  },
  "policy_rule_triggered": "RED_TIER_REMOVE_HIGH_INTENSITY",
  "coach_recommendation": "convert_wed_vo2_to_z1_recovery",
  "reviewer_verdict": { "decision": "approve", "rationale": "Safe path; matches policy." },
  "user_facing_explanation": "Wednesday's VO2max session is now an easy Z1 ride — your HRV dropped sharply and your resting HR is up, so your body needs recovery.",
  "created_at": "2026-06-03T12:00:00Z"
}
```

Stored in the audit log; summarised in user notifications; used for debugging, trust, and future model improvement.

### 9.5 Versioning & Auditability
Every published amendment creates a new plan version. Prior versions, timestamps, key inputs, and reasoning summaries are preserved.

### 9.6 Suspension State
On injury, illness, or major fatigue, an active plan may enter a **suspended** state rather than being cancelled. The system later proposes a safe re-entry ramp (reduced load 1–2 weeks) when the athlete is ready, shifting the plan end date accordingly.

---

## 10. Post-Workout Feedback

### 10.1 Principles
Low-friction, mobile-friendly, fast. Long multi-step surveys are avoided — they cause survey fatigue and users mute the bot. (This explicitly replaces the earlier 8-question sequence.)

### 10.2 Default Feedback UX — Compact 3-Step Flow

Delivered via Telegram with inline-button keyboards. 12-hour response window.

**Step 1 — Session outcome**
```
Bibi: "Hi! I see today's ride (TSS: 75). How did it go?"
[ 🟢 Nailed it ]  [ 🟡 Hard / shortened ]  [ 🔴 Cut power / failed ]
```

**Step 2 — Combined effort + leg feel** (shown after Step 1)
```
[ 3 — Easy / fresh legs ]
[ 6 — Moderate / normal ]
[ 8 — Very hard / heavy legs ]
[ 10 — Maxed / no fuel ]
```

**Step 3 — External factors**
```
Bibi: "Anything off the bike affect today?"
[ ❌ All good ]  [ 😴 Low sleep ]  [ 💼 Work stress ]  [ 🍕 Poor fuel ]
```

### 10.3 Optional Voice Notes (Killer Feature)
If the user taps 🟡 or 🔴, the bot offers: *"Record a quick voice note — tell me what happened."* The audio is transcribed via OpenAI Whisper (cheap, in an n8n node) and passed to the Coach model, which extracts context ("knee hurt", "brutal headwind"). Optional; never mandatory.

### 10.4 Late Feedback
Still accepted via Telegram or web app, marked as late, and given lower weight / reduced impact on structural amendments.

---

## 11. Metrics & Analytics

### 11.1 Core Objective Metrics (ML Core)
TSS, IF, NP; power and HR zone distributions; power-to-HR decoupling; cadence; temperature/elevation context; adherence indicators; W′bal events.

### 11.2 Longitudinal Metrics
FTP trend; CTL/ATL/TSB; plan adherence; power curve progression; HR-at-given-power over time; W/kg evolution.

### 11.3 Dashboard (Web App Home)
- Today's workout card (type, duration, intervals, TSS target, export)
- Weekly strip calendar (colour-coded, completion status)
- Fitness status (CTL/ATL/TSB with trend arrows)
- Readiness widget (Green/Yellow/Red tier, HRV trend, Body Battery) — when wearable connected
- AI Coach last note (link to full)
- Plan progress (week N, phase, % complete, version indicator)

### 11.4 Analytics Views
PMC (CTL/ATL/TSB over time, amendment events pinned); power curve (with historical overlay); zone distribution; weekly load (actual vs planned + adherence); FTP progression; HR efficiency trend; wellness trends (30-day HRV/RHR/sleep/Body Battery, when available).

---

## 12. Integration Architecture

### 12.1 Primary Strategy — Intervals.icu

Intervals.icu is the **primary** synchronization layer for both directions. It aggregates uncompressed FIT files directly from Garmin Connect, Wahoo Cloud, Suunto, and Coros, and exposes richer data than Strava's free API — including second-by-second power/HR, left/right balance, temperature, and overnight HRV from the wearable. Authentication via OAuth 2.0.

**Outbound (planned workout → device):**
```
Bibi → POST /api/v1/athlete/{id}/events → ICU → Garmin Connect → Edge / Fenix
                                              → Wahoo Cloud   → ELEMNT / Bolt
```
Wahoo constraint: workouts must include power targets in at least one step.

**Inbound (completed activity + wellness → Bibi):**
```
Garmin / Wahoo → Garmin Connect / Wahoo Cloud → Intervals.icu → Bibi webhook
```
Both Garmin and Wahoo connect **natively** to Intervals.icu in both directions — workout push and completed-activity pull — so neither requires Strava for the core loop. (Strava remains an optional secondary inbound path.)

### 12.2 Secondary & Fallback Paths
- **Strava** — secondary inbound only. Respects the November 2024 API restriction (athlete-only data visibility; no coach-visibility pathway). Not used for workout delivery.
- **Manual FIT upload** — always-available recovery path via the web app.
- External activity IDs stored to prevent duplicate processing.

### 12.3 Device Support Matrix

| Device | Workout delivery | Activity inbound | Wellness data |
|---|---|---|---|
| Garmin Edge 530/540/830/840/1040 | ✅ | ✅ | ❌ (not a wearable) |
| Garmin Fenix 6/7/8, Epix 2 | ✅ | ✅ | ✅ Full |
| Garmin Forerunner 255/265/955/965 | ✅ | ✅ | ✅ Full |
| Apple Watch (Series 6+ / SE / Ultra) | ⚠️ Limited (see note) | ✅ (via Strava) | ✅ via iPhone bridge app → ICU (HRV as SDNN; no Body Battery) |
| Wahoo ELEMNT / Bolt / Roam | ✅ (full two-way, native via ICU) | ✅ (native via ICU; Strava optional) | ❌ (not a wearable) |
| Other devices | ❌ auto | ✅ via Strava | ❌ |
| No device | ❌ | Manual FIT upload | ❌ |

> **Apple Watch note:** Apple Watch is strong for *wellness capture* (via bridge app) and *activity inbound* (via Strava), but structured workout *delivery* to the watch is limited — Apple Watch is not a primary target for pushing interval workouts the way Garmin Edge/Fenix and Wahoo head units are. Apple Watch users are expected to ride with a head unit or follow workouts via the web app / indoor app, while using the watch primarily for wellness and recording. Native structured-workout delivery to Apple Watch is a v2 consideration tied to Bibi's native iOS app.

### 12.4 Deduplication
Match incoming activity by date + duration (±60s) + sport type; store external IDs (ICU, Strava) to prevent reprocessing if a webhook fires twice.

### 12.5 Reliability
Retry transient failures; preserve raw payloads in S3 for audit/replay; expose manual upload fallback if third-party services fail; monitor webhook failures and sync gaps. n8n is used for routing and scheduling only — it never embeds ML or business rules.

### 12.6 Phase 2 — Garmin Health API
Apply for direct partnership once the platform is live with active users; enables direct workout push and activity pull, removing the ICU dependency. ICU integration retained as an option.

---

## 13. n8n Automation Workflows

n8n is the orchestration backbone — scheduling, webhooks, routing, Telegram messaging, Whisper transcription. It does **not** run ML inference or business rules (those live in ML Core / Policy Engine).

### Workflow A — Inbound Activity & Actor-Critic Pipeline

```
[Webhook]  Intervals.icu (or Strava) new-activity notification
   │
[HTTP → ML Core]  parse FIT; compute TSS/NP/IF/zones/W′bal;
   │              fetch wellness (day + 2 prior, 2 retries, 10s timeout);
   │              compute baselines + Z-scores + readiness tier;
   │              run anomaly detection + guardrail evaluation
   │              → returns numeric JSON + hard safety flags
   │
[Dedupe]  by date + duration (±60s) + sport; discard duplicates
   │
[Store]  TimescaleDB (activity + wellness_daily); raw payloads → S3
   │
[Switch — ROUTER]
   ├── Scenario A: no anomaly, no structural change needed
   │     → Telegram: compact 3-step feedback (Section 10.2)
   │     → Coach (cheap LLM): post-workout summary → Telegram
   │
   └── Scenario B: anomaly / incomplete / Red tier / structural change
         → Coach (cheap LLM): draft amendment + message (gets hard flags
           as non-negotiable constraints)
         → Reviewer (smart LLM): validate against ML metrics + policy
              → if APPROVE/MODIFY: write amendment + decision object;
                 increment plan version; Telegram notify user
              → if REJECT: keep plan safe; Coach explains, no change
```

### Workflow B — Voice Note Transcription
Triggered when user taps 🟡/🔴 and records audio → [OpenAI Whisper node] transcribe → pass text to Coach for emotional/context analysis → fold into feedback record.

### Workflow C — Daily Workout Reminder
Cron at user's preferred time → query today's workout → Telegram message with details + [Export to Garmin] [Mark as Rest] [Ask Coach]; if yesterday unlogged → missed-workout check-in.

### Workflow D — Weekly Digest
Cron Monday (timezone-aware) → compile last 7 days (TSS, CTL change, wellness averages, adherence) → preview next 7 days → Coach generates digest → Telegram with [View full week] [Export all].

### Workflow E — Conversational Coach
User free-text to Telegram → retrieve 14-day context → Coach (cheap LLM) responds. Escalates to Reviewer only if the user's request implies a structural plan change.

### Workflow F — Amendment Notification
On any published amendment → format decision-object summary (what changed, why, source) → Telegram → update web app plan version.

---

## 14. Notifications & Communication

### 14.1 Channels (v1)
Telegram (primary coaching channel) + Email (auth, digests fallback, completion).

### 14.2 Notification Types
Daily workout reminder; post-workout feedback prompt; wellness import notice (once); AI Coach summary; weekly digest; plan amendment alert; readiness/safety alert (Red tier); FTP retest reminder; plan completion; follow-on plan suggestion; auth/security emails.

### 14.3 Telegram Templates

**Wellness import notice (once):**
```
📊 Wellness connected — I'll use your sleep, resting HR, HRV and
Body Battery (last 3 days) as supporting signals. Disable any time
in Settings > Privacy.
```

**Low-impact amendment (auto):**
```
🔧 Small tweak: [what changed]. Reason: [one line]. Applied
automatically, within safe limits. [View plan]
```

**Reviewer-approved amendment:**
```
📋 Plan adjusted
• What changed: [e.g. Wed VO2max → Z1 recovery]
• Why: [HRV down sharply, resting HR up — recovery needed]
• Checked by your AI reviewer for safety.
[Accept] [Ask why] [View plan]
```

**Red-tier safety alert:**
```
⚠️ Your recovery signals dropped sharply (HRV well below your
normal, resting HR up). I've replaced today's hard session with
easy recovery. If you feel unwell, please see a doctor before
training. [I'll rest] [I feel fine] [Tell me more]
```

### 14.4 Channel Abstraction
Channel-agnostic dispatcher from day one → Telegram + Email now; native push (FCM/APNs) added in v2 with no redesign.

### 14.5 Interaction Principles
Max 4 short paragraphs per coaching message; inline buttons for all choices; max 3 unsolicited messages/day; deep links to web app for detail; safety alerts always include a doctor-consultation note.

---

## 15. Workout & Plan Export

### 15.1 Internal Format
Platform-agnostic JSON schema; all export formats generated from this single source; exports always reflect the latest plan version.

### 15.2 Single Workout
**.FIT** (Garmin/Wahoo/universal) · **.ZWO** (Zwift/indoor/TrainingPeaks) · **.MRC** (TrainerRoad/%FTP) · **.ERG** (absolute watts). FIT and ZWO primary. Wahoo requires power targets — enforced at export.

### 15.3 Full Plan
**PDF** (visual overview, printable, coach-shareable) · **ZIP of .FIT** (named `W01_D02_Threshold.fit`) · **ZIP of .ZWO** · **iCal** (calendar schedule).

### 15.4 Compatibility Matrix

| Platform | .FIT | .ZWO | .MRC | .ERG |
|---|---|---|---|---|
| Intervals.icu | ✅ | ✅ | ✅ | ✅ |
| Garmin Connect | ✅ | ❌ | ❌ | ❌ |
| Wahoo Cloud | ✅ | ❌ | ✅ | ✅ |
| Zwift | ❌ | ✅ | ❌ | ❌ |
| TrainerRoad | ❌ | ✅ | ✅ | ✅ |
| TrainingPeaks | ✅ | ✅ | ✅ | ❌ |

---

## 16. Mobile-Ready Architecture

### 16.1 API-First
All business logic, ML logic, and policy rules live in backend / ML Core services. Web frontend and n8n are clients/routers against the same API. The future mobile app is another client using identical contracts.

### 16.2 Authentication
JWT + refresh tokens; identical for web, mobile, n8n; biometric hook reserved; multi-device sessions; OAuth tokens server-side only.

### 16.3 Deep Link Scheme
Universal URLs in all Telegram/email links:
`/dashboard` · `/workouts/today` · `/workouts/:id` · `/coach` · `/plan` · `/plan/versions` · `/amendments/:id` · `/digest/:week` · `/profile` — each mapping to `bibi://…` deep links in v2.

### 16.4 Design System
Platform-agnostic design tokens (colours incl. zone colours, typography, spacing, radius) → translate to React (web) and React Native (v2).

### 16.5 Phased Mobile Roadmap
**v1** Web app (responsive) → **v1.x** optional PWA (manifest, service worker offline plan view, Web Push) → **v2** Native React Native app (reuses all existing API/auth/deep-link contracts).

---

## 17. Non-Functional Requirements

### 17.1 Security
TLS 1.3 in transit; AES-256 at rest; sensitive health-data controls; wellness raw payloads encrypted in S3; OAuth tokens server-side only; bcrypt/Argon2 hashing; rate limiting; input validation; policy/ML decisions auditable.

### 17.2 Privacy & GDPR
Explicit consent per processing purpose; Article 9 separate consent for health/wellness data; right to access, deletion (cascade within 30 days; S3 wellness payloads purged), and portability (JSON export); data minimisation; third-party processor disclosure (ICU, Strava, LLM provider, Whisper); wellness consent withdrawable any time (ML reverts to FIT + subjective only); anonymised ML training opt-in and pseudonymised.

### 17.3 Performance Targets
Core page load < 2s; API p95 < 500ms; FIT processing < 30s; wellness fetch < 10s (2 retries); Telegram delivery < 5s; plan generation < 60s.

### 17.4 Availability
99.5% uptime target; graceful degradation (ICU down → manual upload; wellness down → FIT + subjective only); background retries; fully autonomous operation (no human dependency anywhere in the loop).

---

## 18. Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React + TypeScript | v1 responsive web app |
| Backend API | Python FastAPI | Shared ecosystem with ML Core |
| Database | PostgreSQL | Core transactional data |
| Time-series | TimescaleDB | FIT telemetry + wellness trends |
| ML Core | Python (NumPy/Pandas/scikit-learn) | Metrics, baselines, Z-scores, W′bal, anomaly, policy |
| LLM — Coach (Actor) | Cheap model (Claude Haiku / GPT-4o-mini) | Daily chat, summaries, drafts |
| LLM — Reviewer (Critic) | Smart model (Claude Sonnet / GPT-4o) | Structural amendment validation only |
| Automation | Self-hosted n8n | Routing/scheduling/Whisper only — no business logic |
| Speech-to-text | OpenAI Whisper | Voice-note transcription |
| Messaging | Telegram Bot API | Primary coaching channel |
| Storage | S3-compatible (encrypted) | FIT files, exports, raw wellness payloads |
| Auth | JWT + OAuth 2.0 | Mobile-ready |
| Hosting | Cloud / dedicated (cost + privacy driven) | Hetzner viable for MVP |

**Architecture principle:** business logic, ML logic, and policy rules live only in backend/ML Core. Frontend and n8n are clients/routers. LLMs never own numerical decisions.

---

## 19. Monetization

**Free tier:** full onboarding; one limited plan; basic visualization; manual FIT upload only; basic post-workout analysis; limited export.

**Pro tier:** unlimited plans; full Coach + Reviewer flow; adaptive amendments; sync integrations; wellness intelligence; all export formats; Telegram coaching; full analytics; plan chaining + ongoing personalization.

No advertising in any tier. For the Friends & Family MVP, monetization is deferred — the tier model defines the eventual commercial structure. Per-user LLM cost target: a few cents/day via the cheap-Coach / rare-Reviewer split.

---

## 20. Implementation Roadmap

> Friends & Family MVP focus: ship the smallest fully-working autonomous loop first, then layer sophistication.

**Milestone 1 — Core Loop (MVP backbone)**
- Auth, onboarding, profile
- Plan generation (3 methodologies × 3 durations) + calendar/visualization
- Intervals.icu OAuth: outbound workout push + inbound activity webhook
- Manual FIT upload fallback; deduplication
- ML Core: FIT parsing, TSS/IF/NP/CTL/ATL/TSB
- Coach model: post-workout summaries + Telegram compact feedback
- Export: FIT + ZWO

**Milestone 2 — Two-Model Safety & Wellness**
- Deterministic Policy Engine + guardrails + decision object + plan versioning
- Reviewer model + Actor-Critic amendment pipeline (Workflow A)
- Wellness ingestion + baselines + Z-scores + Green/Yellow/Red tiers
- Anomaly detection + Red-tier safety path + suspension state
- Weekly digest; remaining export formats (MRC, ERG, PDF, ZIP, iCal)

**Milestone 3 — Sophistication & Polish**
- W′bal modeling + underestimated-FTP detection
- Voice notes via Whisper
- Full analytics dashboard (PMC, power curve, wellness trends)
- Plan chaining
- Cost telemetry per user

**Milestone 4 — Friends & Family Pilot**
- Closed pilot with a small group of cyclists
- Monitor: amendment acceptance, false-positive Red flags, per-user LLM cost, plan completion, qualitative trust
- Iterate on guardrail thresholds and wellness Z-score weighting

---

## 21. Open Decisions & Future Considerations

### 21.1 Decisions Required Before Build
- FTP test protocol to embed by default (20-min / ramp / 8-min)
- Final power (7-zone Coggan?) and HR (5-zone) model definitions
- Preferred LLM providers for Coach (cheap) and Reviewer (smart)
- Exact guardrail thresholds (within recommended conservative ranges)
- Wellness sources beyond Intervals.icu / Garmin for v1
- Whether W′bal ships in MVP (Milestone 3) or defers to v1.x
- Whether PWA is v1.x or deferred to v2
- Hosting and deployment model

### 21.2 v1.x / v2 Candidates
- PWA packaging; native iOS/Android (React Native); push notifications
- Additional wellness sources (Oura, Whoop, Coros, Suunto)
- Garmin Health API direct partnership; Garmin Connect IQ on-device app
- Zwift direct integration; indoor ERG-mode control
- Multi-sport (running, triathlon); WhatsApp channel
- Optional human-coach premium extension (only if ever commercially justified)

### 21.3 Key Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Intervals.icu API/pricing change | Manual FIT fallback; pursue Garmin partnership later |
| Strava API restrictions | ICU is primary; Strava strictly secondary |
| LLM cost creep | Cheap Coach for chat; Reviewer only on structural changes; ML Core does all maths |
| AI produces unsafe advice | Deterministic Policy Engine has final authority; Reviewer second-checks; Red-tier auto-safe path |
| Wellness over-reliance | Personal baselines + Z-scores + `measured`-only rule + multi-signal confirmation |
| Survey fatigue | Compact 3-tap feedback; optional voice notes |
| Cold-start quality | Onboarding depth + methodology suitability logic; wellness accelerates personalization |
| No wearable → thin wellness data | Graceful degradation to FIT + subjective feedback |
| Apple Watch bridge dependency | Documented onboarding step; bridge apps are mature and community-proven; v2 native iOS app removes the dependency |
| Mixing HRV types (SDNN vs RMSSD) | Store `hrv_type` per record; never mix within one baseline; Z-score is per-athlete per-metric |
| Privacy (health data) | Article 9 consent; encrypted S3; withdrawable consent |

---

*End of document — Bibi PRD v2.0 (Consolidated)*

---

> **Recommended next steps**
> 1. Confirm open decisions in 21.1 (especially LLM provider split and guardrail thresholds)
> 2. Database ERD: users, plans, plan_versions, workouts, activities, wellness_daily, decision_objects
> 3. ML Core specification: metric formulas, baseline/Z-score logic, W′bal model, anomaly rules, policy ruleset
> 4. Coach and Reviewer system prompts + structured JSON contracts (amendment + verdict schemas)
> 5. n8n Workflow A (Actor-Critic) build + Intervals.icu OAuth integration
> 6. Web app wireframes: dashboard, plan calendar, workout detail, analytics
