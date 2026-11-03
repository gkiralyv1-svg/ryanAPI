def classify_swell(swell_height, swell_period):
    """
    Classify swell conditions into four tourist-level categories.

    Returns:
        0: Low
        1: Moderate
        2: High
        3: Very high
    """

    if swell_height is None or swell_period is None:
        return None

    if swell_height >= 6 and swell_period >= 14:
        return 3

    elif swell_height >= 4 and swell_period >= 13:
        return 2

    elif swell_height >= 3 and swell_period >= 12:
        return 1

    return 0