def classify_waste(pH, flash_point, toxicity):
    """
    Classifies hazardous waste based on pH, flash point, and toxicity.
    Returns: 'Flammable', 'Corrosive', 'Toxic', or 'General'
    """
    if flash_point < 37:
        return "Flammable"
    elif pH < 3 or pH > 11:
        return "Corrosive"
    elif toxicity.lower() == "high":
        return "Toxic"
    else:
        return "General"
def classify_waste(pH, flash_point, toxicity):
    if flash_point < 37:
        return "Flammable"
    elif pH < 3 or pH > 11:
        return "Corrosive"
    elif toxicity.lower() == "high":
        return "Toxic"
    else:
        return "General"