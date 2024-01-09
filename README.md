# Landsat
Landsat Surface Reflectance Data Retrieval

This Python script provides a convenient way to retrieve Landsat surface reflectance data for a specific geographic point within a given time range using Google Earth Engine (GEE). The script returns the data in the form of a Pandas DataFrame.

Prerequisites

Before using the script, make sure to install the required libraries and authenticate with GEE.

pip install pandas earthengine-api

Usage:
Set up your Python environment by importing the necessary libraries and initializing the GEE API.

import pandas as pd
import ee

ee.Authenticate()
ee.Initialize()

Define the geographic coordinates of the point of interest, the time range for data collection, and any optional parameters.

longitude = -122.431
latitude = 37.773
start_date = '2022-01-01'
end_date = '2022-12-31'

Call the Landsat_Surface_Reflectance function with the specified parameters.

result = Landsat_Surface_Reflectance(
    longitude,
    latitude,
    start_date,
    end_date,
    collection_address='LANDSAT/LC08/C02/T1_L2',  # Landsat 8, Collection 2, Tier 1
    bands=['SR_B4', 'SR_B3', 'SR_B2'],  # Optical bands
    max_cloud_cover=10,  # Maximum acceptable cloud cover
    scale=30  # Spatial resolution
)

print(result)
