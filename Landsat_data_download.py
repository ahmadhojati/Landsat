#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import ee
ee.Authenticate()
ee.Initialize()

def Landsat_Surface_Reflectance(longitude, latitude, start_date, end_date,
                                collection_address='LANDSAT/LC08/C02/T1_L2',
                                bands=['SR_B4', 'SR_B3', 'SR_B2'],
                                max_cloud_cover=10,
                                scale=30):
    
    """
    Retrieve Landsat surface reflectance data for a specific geographic point.

    Args:
        longitude (float): The longitude coordinate of the specific point of interest.
        latitude (float): The latitude coordinate of the specific point of interest.
        start_date (str): The start date in "YYYY-MM-DD" format for the time range of Landsat data collection.
        end_date (str): The end date in "YYYY-MM-DD" format for the time range of Landsat data collection.
        collection_address (str, optional): The GEE collection address for Landsat imagery.
            Default is 'LANDSAT/LC08/C02/T1_L2' (Landsat 8, Collection 2, Tier 1 data).
        bands (list of str, optional): A list of band names to retrieve. Default includes optical bands.
        max_cloud_cover (int, optional): The maximum acceptable cloud cover percentage for selected images.
            Default is 10.
        scale (int, optional): The scale in meters for the spatial resolution of the retrieved data.
            Default is 30.

    Returns:
        pd.DataFrame: A Pandas DataFrame with Landsat data for the specified location and time range.

    Example:
    ```python
    import pandas as pd
    import ee

    # Define the coordinates of the point of interest
    longitude = -122.431
    latitude = 37.773

    # Define the time range for data collection
    start_date = '2022-01-01'
    end_date = '2022-12-31'

    # Call the function with the specified parameters
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

    # The result is a Pandas DataFrame containing Landsat data for the specified location and time range
    print(result)
    ```
    """
    # Define the specific point of interest (longitude, latitude)
    point_of_interest = ee.Geometry.Point(longitude, latitude)

    # Filter Landsat imagery based on the specific point and time range
    landsat = ee.ImageCollection(collection_address)         .select(bands)         .filterBounds(point_of_interest)         .filterDate(ee.Date(start_date), ee.Date(end_date))         .filterMetadata('CLOUD_COVER', 'less_than', max_cloud_cover)

    # Check if any data is available
    if landsat.size().getInfo() == 0:
        # No data found, return an empty DataFrame with NaN values
        empty_df = pd.DataFrame(columns=['Date','Coordinate'] + bands + ['CloudCover'])
        for i in range(len(empty_df.columns)):
            empty_df.loc[0] = [None] * len(empty_df.columns)
        return empty_df

    # Create an empty DataFrame
    df = pd.DataFrame(columns=['Date','Coordinate'] + bands + ['CloudCover'])

    # List of available images
    image_list = landsat.toList(landsat.size())

    # Iterate through the images in the collection
    for i in range(image_list.size().getInfo()):
        image = ee.Image(image_list.get(i))
        properties = image.getInfo()['properties']
        date = properties['DATE_ACQUIRED']
        cloud_cover = properties['CLOUD_COVER']
        M = properties['REFLECTANCE_MULT_BAND_2']  # Multiplication factor for converting DN to Surface Reflectance
        A = properties['REFLECTANCE_ADD_BAND_2']  # Addition factor for converting DN to Surface Reflectance

        # Sample the specific point for each image
        sampled_data = image.multiply(M).add(A).sampleRegions(
            collection=ee.FeatureCollection([point_of_interest]),  # Use the specific point as a FeatureCollection
            scale=scale,
            geometries=True
        )

        # Extract and append the date, cloud cover, and values to the DataFrame
        sampled_values = sampled_data.getInfo()['features']
        for feature in sampled_values:
            properties = feature['properties']

            data_row = {
                'Coordinate': point_of_interest['coordinates'],
                'Date': date,
                'CloudCover': cloud_cover
            }

            # Add the values for each band to the data row
            for band in bands:
                data_row[band] = properties[band]

            df = df.append(data_row, ignore_index=True)

    return df

