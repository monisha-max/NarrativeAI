"""Fog of War — information density and source diversity calculation."""


def calculate_fog_density(
    source_count: int,
    source_diversity: int,
    has_official_source: bool,
    has_conflicting_reports: bool,
) -> float:
    """Calculate fog density for a time segment.

    Returns 0.0 (clear, well-sourced) to 1.0 (foggy, uncertain).
    """
    density = 1.0

    # More sources = clearer
    if source_count >= 5:
        density -= 0.4
    elif source_count >= 3:
        density -= 0.25
    elif source_count >= 1:
        density -= 0.1

    # Source diversity matters
    if source_diversity >= 3:
        density -= 0.3
    elif source_diversity >= 2:
        density -= 0.15

    # Official sources add clarity
    if has_official_source:
        density -= 0.2

    # Conflicting reports increase fog
    if has_conflicting_reports:
        density += 0.2

    return max(0.0, min(1.0, density))


def compute_timeline_fog(events: list[dict]) -> list[dict]:
    """Compute fog density for each segment of a timeline.

    Groups events by time period and calculates fog per segment.
    """
    # TODO: Implement proper time-segmented fog calculation
    fog_data = []
    for event in events:
        fog_data.append({
            "event_id": event.get("id"),
            "occurred_at": event.get("occurred_at"),
            "fog_density": event.get("fog_density", 0.5),
        })
    return fog_data
