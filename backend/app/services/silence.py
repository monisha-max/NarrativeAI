"""Silence Detection — detecting abnormal quiet periods in story arcs."""

from datetime import datetime, timedelta


def calculate_silence_baseline(
    event_dates: list[datetime],
    archetype: str | None = None,
) -> float:
    """Calculate normal publication cadence (events per day) for a dossier."""
    if len(event_dates) < 2:
        return 0.0

    sorted_dates = sorted(event_dates)
    total_span = (sorted_dates[-1] - sorted_dates[0]).days
    if total_span == 0:
        return float(len(event_dates))

    return len(event_dates) / total_span


def detect_silence(
    event_dates: list[datetime],
    baseline_rate: float,
    archetype: str | None = None,
) -> dict | None:
    """Detect if the current silence period is anomalous.

    Returns silence alert dict or None if normal.
    """
    if not event_dates or baseline_rate <= 0:
        return None

    last_event = max(event_dates)
    now = datetime.now(last_event.tzinfo)
    days_silent = (now - last_event).days

    # Expected events in silence period
    expected_events = baseline_rate * days_silent

    # Flag if we expected 3+ events but got none
    if expected_events >= 3.0:
        return {
            "days_silent": days_silent,
            "baseline_rate": baseline_rate,
            "expected_events": round(expected_events, 1),
            "last_event_date": last_event.isoformat(),
            "severity": "high" if expected_events >= 5 else "medium",
            "archetype": archetype,
        }

    return None
