from os import path

CO2_INTENSITY_TABLE_PATH = path.join(
    path.abspath(path.dirname(__file__)),
    "carbon_offset/co2_intensity",
    "carbon-intensity-electricity-01-09-2022_cropped.csv",
)  # FIXME: This won't work
WORLD_CO2_INTENSITY = 425.23486328125

STATEMINE_SS58_ADDRESS_TYPE = 2
STATEMINE_REMOTE_WS = "wss://statemine-rpc.polkadot.io"
CARBON_ASSET_ID = "2050"
