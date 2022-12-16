"""Constants for Solarweb integration."""
from os import path

# This is the internal name of the integration, it should also match the directory
# name for the integration.
DOMAIN = "solarweb"
SEED = "seed_secret"
EMAIL_ADDRESS = "email_address"
PASSWORD = "password"
IPCI_TYPE_REGISTRY = {
    "types": {
        "AccountInfo": "AccountInfoWithRefCount",
        "Address": "AccountId",
        "LookupSource": "AccountId",
        "RefCount": "u8",
        "Record": "Vec<u8>",
        "TechnicalParam": "Vec<u8>",
        "TechnicalReport": "Vec<u8>",
        "EconomicalParam": "{}",
        "ProofParam": "MultiSignature",
        "LiabilityIndex": "u64",
    }
}
IPCI_SS58_ADDRESS_TYPE = 32
IPCI_REMOTE_WS = "wss://kusama.rpc.ipci.io"
CARBON_ASSET_ID = "0xcbf2d1c28581201dc468e312fd44413e0000000000000065"
CO2_INTENSITY_TABLE_PATH = path.join(
    path.abspath(path.dirname(__file__)), "co2_intensity", "carbon-intensity-electricity-01-09-2022_cropped.csv"
)
WORLD_CO2_INTENSITY = 425.23486328125
