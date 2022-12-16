import asyncio
from logging import getLogger

from scalecodec.types import GenericCall, GenericExtrinsic
from substrateinterface import ExtrinsicReceipt, Keypair, SubstrateInterface

from .const import CARBON_ASSET_ID, STATEMINE_REMOTE_WS, STATEMINE_SS58_ADDRESS_TYPE

logger = getLogger(__name__)


async def burn_carbon_asset_async(seed: str, tokens_to_burn: float) -> tuple:
    return await asyncio.to_thread(burn_carbon_asset, seed, tokens_to_burn)


def burn_carbon_asset(seed: str, tokens_to_burn: float) -> tuple:
    """
    Burn carbon assets in Statemine Substrate network.
    :param seed: Offsetting agent account seed in any form.
    :param tokens_to_burn: Number of tokens to burn.
    :return: transaction hash.
    """

    if seed.startswith("0x"):
        keypair: Keypair = Keypair.create_from_seed(
            seed_hex=hex(int(seed, 16)), ss58_format=STATEMINE_SS58_ADDRESS_TYPE
        )
    else:
        keypair: Keypair = Keypair.create_from_mnemonic(seed, ss58_format=STATEMINE_SS58_ADDRESS_TYPE)
    interface = SubstrateInterface(url=STATEMINE_REMOTE_WS, ss58_format=STATEMINE_SS58_ADDRESS_TYPE)
    call: GenericCall = interface.compose_call(
        call_module="Assets",
        call_function="burn",
        call_params={"id": CARBON_ASSET_ID, "who": {"Id": keypair.ss58_address}, "amount": tokens_to_burn},
    )
    signed_extrinsic: GenericExtrinsic = interface.create_signed_extrinsic(call=call, keypair=keypair)
    receipt: ExtrinsicReceipt = interface.submit_extrinsic(
        signed_extrinsic, wait_for_inclusion=True, wait_for_finalization=False
    )
    return (
        receipt.extrinsic_hash,
        f"https://polkadot.js.org/apps/?rpc={STATEMINE_REMOTE_WS.lstrip('wss://')}%3A%2F%2F"
        f"{STATEMINE_REMOTE_WS.lstrip('wss://')}#/explorer/query/{receipt.block_hash}",
    )
