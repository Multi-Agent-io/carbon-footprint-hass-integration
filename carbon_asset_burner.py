"""
This file contains functions to burn carbon assets in IPCI network and update burns history in local DB.
"""

from logging import getLogger
from scalecodec.types import GenericCall, GenericExtrinsic
from substrateinterface import SubstrateInterface, Keypair, ExtrinsicReceipt

from .constants import CARBON_ASSET_ID, IPCI_REMOTE_WS
from .substrate_utils import create_keypair, create_instance

logger = getLogger(__name__)


def burn_carbon_asset(seed: str, tokens_to_burn: float) -> tuple:
    """
    Burn carbon assets in IPCS Substrate network.
    :param seed: Offsetting agent account seed in any form.
    :param tokens_to_burn: Number of tokens to burn.
    :return: transaction hash.
    """

    keypair: Keypair = create_keypair(seed)
    interface: SubstrateInterface = create_instance()

    call: GenericCall = interface.compose_call(
        call_module="CarbonAssets",
        call_function="self_burn",
        call_params=dict(id=CARBON_ASSET_ID, amount=tokens_to_burn),
    )

    signed_extrinsic: GenericExtrinsic = interface.create_signed_extrinsic(call=call, keypair=keypair)
    receipt: ExtrinsicReceipt = interface.submit_extrinsic(
        signed_extrinsic, wait_for_inclusion=True, wait_for_finalization=False
    )

    return (receipt.is_success,
        receipt.extrinsic_hash, 
        f"https://polkadot.js.org/apps/?rpc={IPCI_REMOTE_WS[: IPCI_REMOTE_WS.find('://')]}%3A%2F%2F"
        f"{IPCI_REMOTE_WS[IPCI_REMOTE_WS.find('://')+3:]}#/explorer/query/{receipt.block_hash}",
    )