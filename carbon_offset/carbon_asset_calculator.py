"""
Perform various carbon asset burning process calculations.
"""

import asyncio
import csv
from logging import getLogger

from geopy.geocoders import Nominatim

from .const import CO2_INTENSITY_TABLE_PATH, WORLD_CO2_INTENSITY

logger = getLogger(__name__)


async def calculate_compensation_amt_tokens_async(kwh: float, geo: str) -> float:
    return await asyncio.to_thread(calculate_compensation_amt_tokens, kwh, geo)


def _get_co2_intensity_for_location(country: str) -> float:
    logger.info(f"Country based on geo: {country}.")
    logger.info(f"Getting CO2 intensity in g/kWh for {country}.")
    with open(CO2_INTENSITY_TABLE_PATH) as intensity:
        intensity_csv = csv.reader(intensity)
        for row in intensity_csv:
            if row[0] == country:
                return float(row[1])
    logger.warning(
        f"Failed to find CO2 intensity for country {country}. Using global coefficient: {WORLD_CO2_INTENSITY} g/kWh."
    )
    return WORLD_CO2_INTENSITY


def calculate_compensation_amt_tokens(kwh: float, geo: str) -> float:
    """
    Get an amount of carbon assets to burn based on a number of kWt*h burnt and country of residence.
        Source:
        CO2 emission intensity by countries: https://ourworldindata.org/electricity-mix#carbon-intensity-of-electricity
        DISCLAIMER: THIS IS NOT INTENDED TO BE A COMPLETELY ACCURATE CALCULATION. THE FINAL RESULT HEAVILY DEPENDS ON
        THE TYPE OF COAL USED. ALSO, THE STATISTICS DATA MAY BE INCORRECT/OUTDATED. THEREFORE, DO NOT TREAT THIS AS
        A SCIENTIFIC RESEARCH.
    :param kwh: Number of kWt*h to compensate.
    :param geo: Coordinates of the household.
    :return: Number of carbon assets to burn.
    """
    logger.info(f"Getting country by geo: {geo}.")
    geolocator = Nominatim(user_agent="geoapiExercises")

    if location := geolocator.reverse(geo, language="en"):
        country: str = location.raw["address"]["country"]
        co2_intensity: float = _get_co2_intensity_for_location(location)
        logger.info(f"CO2 intensity for {country}: {co2_intensity} g/kWh.")
    else:
        co2_intensity = WORLD_CO2_INTENSITY
        logger.info(f"No country was determined. Using global coefficient: {WORLD_CO2_INTENSITY} g/kWh.")

    tons_co2 = kwh * co2_intensity / 10**6  # Table shows how many grams of CO2 produced per kWh generated in country.
    logger.info(f"Number of metric tons of CO2 / Carbon assets to burn for {kwh} kWh: {tons_co2}.")
    return tons_co2 * 10**9  # 1 Carbon asset per metric tonn of co2, decimal of 9 for the asset in the blockchain
