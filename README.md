# Leaf Wetness Estimation

This repository contains a Python script for estimating leaf wetness using weather data inputs. The model was developed by Rajkumar Dhakar and is designed to integrate into a web-based API for real-time leaf wetness estimation.

## Authors

- **Basavaraj Amogi**
- **Rajkumar Dhakar**
- **Sean Hill**

## Project Overview

The leaf wetness estimation model (Developed by Rajkumar Dhakar) calculates the potential leaf wetness in millimeters based on various weather parameters such as air temperature, dew point, wind speed, relative humidity, and precipitation. The script processes the input weather data and outputs the estimated leaf wetness as a JSON object.

### Key Features

- **Python-based model**: The script is written in Python and uses pandas and numpy for data processing and numerical calculations.
- **Configurable parameters**: The model parameters and constants are stored in a configuration dictionary, making it easy to adjust the model as needed.
- **Real-time estimation**: The script is designed for integration into web-based APIs for real-time leaf wetness estimation.

## Usage

### Prerequisites

- Python 3.x
- Required Python packages: `pandas`, `numpy`

You can install the necessary packages using pip:

```bash
pip install pandas numpy


### Running the Script

- You can run the script from the command line by passing a JSON file containing the weather data as an argument:

```bash

python awn_leaf_wetness.py input_weather_data.json


# Example Input

- The input JSON file should contain weather data in the following format:


[
    {
        "AIR_TEMP_F": 70,
        "DEWPOINT_F": 60,
        "WIND_SPEED_2M_MPH": 5,
        "RELATIVE_HUMIDITY_%": 80,
        "PRECIP_INCHES": 0
    },
    {
        "AIR_TEMP_F": 68,
        "DEWPOINT_F": 59,
        "WIND_SPEED_2M_MPH": 3,
        "RELATIVE_HUMIDITY_%": 85,
        "PRECIP_INCHES": 0.1
    }
]

# Output

- The script will output a JSON object containing the estimated leaf wetness:

[
    {
        "AIR_TEMP_F": 70,
        "DEWPOINT_F": 60,
        "WIND_SPEED_2M_MPH": 5,
        "RELATIVE_HUMIDITY_%": 80,
        "Potential condensation of dew (mm)": 0.1,
        "Estimated Leaf Wetness (mm)": 0.3
    },
    {
        "AIR_TEMP_F": 68,
        "DEWPOINT_F": 59,
        "WIND_SPEED_2M_MPH": 3,
        "RELATIVE_HUMIDITY_%": 85,
        "Potential condensation of dew (mm)": 0.05,
        "Estimated Leaf Wetness (mm)": 0.4
    }
]

# License

- This project is licensed under the MIT License - see the LICENSE file for details.



