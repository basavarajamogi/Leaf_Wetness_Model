# --------------------------------------------------------------------------------
# Authors: Basavaraj Amogi, Rajkumar Dhakar, Sean Hill
# Date: 2024-08-07 [Sean Hill started this as a module of a web based API]
# Last Modified: 
#   2024-08-07 [v 1.0]
#
# Description:
# The script was written to estimate leaf wetness (mm) using the model was developed by Rajkumar Dhakar.
# --------------------------------------------------------------------------------



import pandas as pd
import numpy as np
import json
import sys

# Configuration dictionary containing model parameters and constants
config = {
    "Z_reference": 200,  # Reference height in cm
    "Zc": 150,  # Canopy height in cm
    "alpha": 1.3,  # Wind profile exponent
    "LAI": 2.88,  # Leaf Area Index
    "Wmax": 0.5,  # Maximum water storage capacity on the leaf surface
    "Wf": 0.3,  # Fraction of Wmax to use
    "shape_scale_film_cf": 1.78577026808484,  # Shape scale for film water
    "shape_scale_drop_cd": 4.23057517532205,  # Shape scale for drop water
    "dimension_of_leaf_m": 0.126563029533657,  # Leaf length in meters
    "width_of_leaf_m": 0.12,  # Leaf width in meters
    "n": 196232004,  # Number of stomata per square meter
    "mean_length_of_pore_l": 0.000025,  # Mean length of pore in meters
    "diameter_of_pore_d": 0.00000623,  # Diameter of pore in meters
    "critical_DPD": 1.845,  # Critical Dew Point Depression
    "psychr_constant_mbar": 0.670680828,  # Psychrometric constant in mbar
    "density_of_air_g_cm3": 0.001225,  # Density of air in g/cm³
    "specific_heat_of_air_Jg_C": 1.012,  # Specific heat of air in J/g°C
    "latent_heat_of_vaporization_J_g": 2450,  # Latent heat of vaporization in J/g
    "kinematic_viscosity_of_air": 0.0000156,  # Kinematic viscosity of air in m²/s
    "emissivity": 0.99,  # Emissivity of leaf surface
    "stefan_boltzmann_constant": 5.67037E-08,  # Stefan-Boltzmann constant in W/(m²K⁴)
    "density_of_air_kg_m3": 1.293,  # Density of air in kg/m³
    "specific_heat_of_air_J_kg_K": 1005,  # Specific heat of air in J/(kgK)
    "diffusion_coefficient_of_water_vapor_D": 0.0000212,  # Diffusion coefficient of water vapor in m²/s
    "latent_heat_of_condensation_J_kg": 2257000,  # Latent heat of condensation in J/kg
    "psychrometer_constant_Pa_K": 0.245670633  # Psychrometric constant in Pa/K
}

def estimate_leaf_wetness(data, config):
    """
    Estimate leaf wetness based on weather data and model parameters.

    Parameters:
    - data (pd.DataFrame): Weather data input
    - config (dict): Configuration dictionary with model parameters

    Returns:
    - List of dictionaries with estimated leaf wetness and other relevant metrics
    """

    # Extract and compute necessary parameters from the configuration
    Zc = config["Zc"]
    Z_reference = config["Z_reference"]
    alpha = config["alpha"]
    Wmax = config["Wmax"]
    Wf = config["Wf"]
    shape_scale_film_cf = config["shape_scale_film_cf"]
    shape_scale_drop_cd = config["shape_scale_drop_cd"]
    dimension_of_leaf_m = config["dimension_of_leaf_m"]
    width_of_leaf_m = config["width_of_leaf_m"]
    n = config["n"]
    mean_length_of_pore_l = config["mean_length_of_pore_l"]
    diameter_of_pore_d = config["diameter_of_pore_d"]
    critical_DPD = config["critical_DPD"]
    latent_heat_of_vaporization_J_g = config["latent_heat_of_vaporization_J_g"]
    kinematic_viscosity_of_air = config["kinematic_viscosity_of_air"]
    emissivity = config["emissivity"]
    stefan_boltzmann_constant = config["stefan_boltzmann_constant"]
    density_of_air_kg_m3 = config["density_of_air_kg_m3"]
    specific_heat_of_air_J_kg_K = config["specific_heat_of_air_J_kg_K"]
    diffusion_coefficient_of_water_vapor_D = config["diffusion_coefficient_of_water_vapor_D"]
    latent_heat_of_condensation_J_kg = config["latent_heat_of_condensation_J_kg"]

    Zo = Z_reference * 0.1  # Roughness length in cm
    D = 0.66 * Zc  # Zero plane displacement
    W = Wmax * Wf
    c = (Wmax * shape_scale_film_cf) + ((1 - Wmax) * shape_scale_drop_cd)
    Surface_Area = width_of_leaf_m * dimension_of_leaf_m
    rS = (4 * (mean_length_of_pore_l + (np.pi * diameter_of_pore_d) / 8)) / (np.pi * n * (diameter_of_pore_d ** 2) * diffusion_coefficient_of_water_vapor_D)

    # Convert temperatures from Fahrenheit to Celsius
    data["AIR_TEMP_C"] = (data["AIR_TEMP_F"] - 32) * 5/9
    data["DEWPOINT_C"] = (data["DEWPOINT_F"] - 32) * 5/9
    data["DPD"] = data["AIR_TEMP_C"] - data["DEWPOINT_C"]

    # Calculate Saturation Vapor Pressure (SVP)
    data["SVP"] = 0.6108 * np.exp((17.27 * data["AIR_TEMP_C"]) / (data["AIR_TEMP_C"] + 237.3))

    # Calculate Slope of SVP curve
    data["Slope_kPa"] = (4098 * data["SVP"]) / ((data["AIR_TEMP_C"] + 237.3) ** 2)
    data["Slope_mbar"] = data["Slope_kPa"] * 10

    # Calculate Actual Vapor Pressure (AVP)
    data["AVP"] = data["SVP"] * (data["RELATIVE_HUMIDITY_%"] / 100)

    # Calculate wind speed at the reference height
    data["Uz"] = 2682.4 * data["WIND_SPEED_2M_MPH"]

    # Calculate wind speed at the canopy height
    data["Uc"] = data["Uz"] * (np.log((Zc - D) / Zo) / np.log((Z_reference - D) / Zo)) * (1 + alpha * ((1 - Zc) / Z_reference)) ** -2

    # Calculate the transfer coefficient
    data["Transfer_Coefficient (cm min^-1)"] = c * (data["Uc"] ** 0.5)

    # Calculate potential evapotranspiration (Ep)
    data["Ep"] = (data["Slope_mbar"] / (latent_heat_of_vaporization_J_g * (data["Slope_mbar"] + config["psychr_constant_mbar"]))) * \
                 (config["density_of_air_g_cm3"] * config["specific_heat_of_air_Jg_C"] * (data["Transfer_Coefficient (cm min^-1)"] / data["Slope_mbar"]))\
                 * ((data["SVP"] - data["AVP"]) * 10)

    # Calculate evaporation rate (E)
    data["E (cm/min)"] = data["Ep"] * W

    # Convert wind speed from mph to m/s
    data["Wind Speed (m/s)"] = data["WIND_SPEED_2M_MPH"].apply(lambda x: 0.44704 * x if x > 0 else 0.001)

    # Calculate Reynolds number
    data["Reynolds Number"] = (data["Wind Speed (m/s)"] * dimension_of_leaf_m) / kinematic_viscosity_of_air

    # Calculate Nusselt number
    data["Nusselt Number"] = 0.72 * (data["Reynolds Number"] ** 0.6)

    # Calculate boundary layer resistance to convective heat (rB)
    data["rB (s/m)"] = dimension_of_leaf_m / (0.0000215 * data["Nusselt Number"])

    # Calculate long-wave radiative heat transfer coefficient (hLW)
    data["hLW"] = 4 * emissivity * stefan_boltzmann_constant * (data["AIR_TEMP_C"] + 273.15) ** 3

    # Calculate convective heat transfer coefficient (hH)
    data["hH"] = (density_of_air_kg_m3 * specific_heat_of_air_J_kg_K) / data["rB (s/m)"]

    # Calculate Slope of SVP curve in Pa/K
    data["Slope_Pa_K"] = (data["Slope_kPa"] * 1000) / 273

    # Calculate total heat transfer coefficient (hET)
    data["hET"] = density_of_air_kg_m3 * specific_heat_of_air_J_kg_K * (data["Slope_Pa_K"] / (config["psychrometer_constant_Pa_K"] * (data["rB (s/m)"] + rS)))

    # Calculate total leaf heat transfer coefficient
    data["Leaf Heat Transfer Coefficient (W/m^2/K)"] = data["hLW"] + data["hH"] + data["hET"]

    # Calculate sensible heat exchange (Rhe)
    data["Rhe (J/s)"] = data["Leaf Heat Transfer Coefficient (W/m^2/K)"] * Surface_Area * (data["AIR_TEMP_C"] - data["DEWPOINT_C"])

    # Calculate potential condensation of dew
    data["Potential condensation of dew (g/s)"] = (data["Rhe (J/s)"] / latent_heat_of_condensation_J_kg) * 1000
    data["Potential condensation of dew (mm)"] = (data["Potential condensation of dew (g/s)"] / (Surface_Area * 10000)) * 10 * 60 * 15 * 2

    # Apply Dew Point Depression constraint
    data["Potential condensation of dew (mm)"] = np.where(data["DPD"] < critical_DPD, data["Potential condensation of dew (mm)"], 0)

    # Calculate rain interception
    data["Rain Interception (mm)"] = np.where(data["PRECIP_INCHES"] > 0, 0.6, 0)

    # Calculate evaporation
    data["Evaporation (mm)"] = data["E (cm/min)"] * 10 * 15

    # Estimate leaf wetness
    data["Estimated Leaf Wetness (mm)"] = data.apply(
        lambda row: (row["Potential condensation of dew (mm)"] + row["Rain Interception (mm)"]) - row["Evaporation (mm)"]
                    if row["AIR_TEMP_F"] > 32 else 0,
        axis=1
    )

    # Ensure no negative values for estimated leaf wetness
    data["Estimated Leaf Wetness (mm)"] = np.where(data["Estimated Leaf Wetness (mm)"] > 0, data["Estimated Leaf Wetness (mm)"], 0)

    # Convert the result to a dictionary
    result_dict = data[["AIR_TEMP_F", "DEWPOINT_F", "WIND_SPEED_2M_MPH", "RELATIVE_HUMIDITY_%", "Potential condensation of dew (mm)", "Estimated Leaf Wetness (mm)"]].to_dict(orient="records")
    return result_dict

def main():
    """
    Main function to run the leaf wetness estimation.
    Takes weather data as input from the command line, estimates leaf wetness, and outputs as JSON.
    """

    # Read the input weather data from the command line argument
    weather_data_json = sys.argv[1]

    # Parse the input JSON string into a pandas DataFrame
    weather_data = pd.read_json(weather_data_json)

    # Estimate leaf wetness using the provided data and configuration
    result = estimate_leaf_wetness(weather_data, config)

    # Output the result as a JSON string
    print(json.dumps(result, skipkeys=True, allow_nan=True, indent=6))

if __name__ == "__main__":
    main()
