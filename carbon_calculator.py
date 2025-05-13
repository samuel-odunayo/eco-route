from config import Config

def calculate_carbon_emissions(transport_mode, distance):
    """
    Calculate carbon emissions in grams of CO2 for a given transport mode and distance
    
    Args:
        transport_mode (str): Type of transportation
        distance (float): Distance in kilometers
        
    Returns:
        float: Carbon emissions in grams of CO2
    """
    emissions_per_km = Config.EMISSIONS.get(transport_mode, 0)
    return emissions_per_km * distance

def calculate_carbon_savings(chosen_mode, alternative_mode, distance):
    """
    Calculate carbon savings by choosing one transport mode over another
    
    Args:
        chosen_mode (str): Selected transportation mode
        alternative_mode (str): Alternative transportation mode
        distance (float): Distance in kilometers
        
    Returns:
        float: Carbon savings in grams of CO2
    """
    chosen_emissions = calculate_carbon_emissions(chosen_mode, distance)
    alternative_emissions = calculate_carbon_emissions(alternative_mode, distance)
    
    return max(0, alternative_emissions - chosen_emissions)

def get_environmental_impact(carbon_saved):
    """
    Convert carbon savings to equivalent environmental impact metrics
    
    Args:
        carbon_saved (float): Carbon savings in grams
        
    Returns:
        dict: Dictionary of equivalent environmental impacts
    """

    TREE_ABSORPTION_YEARLY = 21000  
    DRIVING_EMISSIONS_PER_KM = 170  
    
    carbon_saved_kg = carbon_saved / 1000
    
    return {
        'tree_days': carbon_saved / (TREE_ABSORPTION_YEARLY / 365),
        'car_km_equivalent': carbon_saved / DRIVING_EMISSIONS_PER_KM,
        'carbon_kg': carbon_saved_kg
    }