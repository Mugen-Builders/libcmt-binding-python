import logging
import traceback
from pycmt import Rollup
from utils import decode_ether_deposit, decode_erc20_deposit, \
    decode_erc721_deposit, decode_erc1155_single_deposit, decode_erc1155_batch_deposit, \
    create_erc20_transfer_voucher, create_erc721_safetransfer_voucher, create_erc1155_single_safetransfer_voucher, create_erc1155_batch_safetransfer_voucher

ETHER_PORTAL_ADDRESS = "0xA632c5c05812c6a6149B7af5C56117d1D2603828"[2:].lower()
ERC20_PORTAL_ADDRESS = "0xACA6586A0Cf05bD831f2501E7B4aea550dA6562D"[2:].lower()
ERC721_PORTAL_ADDRESS = "0x9E8851dadb2b77103928518846c4678d48b5e371"[2:].lower()
ERC1155_SINGLE_PORTAL_ADDRESS = "0x18558398Dd1a8cE20956287a4Da7B76aE7A96662"[2:].lower()
ERC1155_BATCH_PORTAL_ADDRESS = "0xe246Abb974B307490d9C6932F48EbE79de72338A"[2:].lower()

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

def handle_advance(rollup):
    try:
        advance = rollup.read_advance_state()
        msg_sender = advance['msg_sender'].hex().lower()
        logger.info(f"[app] Received advance request from {msg_sender=} with length {len(advance['payload']['data'])}")

        # logger.info(f"[app]{advance.get('payload',{}).get('data')=}")

        if msg_sender == ETHER_PORTAL_ADDRESS:
            logger.info("[app] Ether deposit")
            deposit = decode_ether_deposit(advance['payload']['data'])
            logger.info(f"[app] Ether deposit decoded {deposit}")

            rollup.emit_voucher(deposit['sender'], deposit['amount'], b'')
            logger.info("[app] Ether voucher emitted")
            return True

        if msg_sender == ERC20_PORTAL_ADDRESS:
            logger.info("[app] ERC20 deposit")
            deposit = decode_erc20_deposit(advance['payload']['data'])
            logger.info(f"[app] ERC20 deposit decoded {deposit}")

            voucher_payload = create_erc20_transfer_voucher(deposit['sender'], deposit['amount'])
            logger.info(f"[app]{voucher_payload.hex()=}")

            rollup.emit_voucher(deposit['token_address'], 0, voucher_payload)
            logger.info("[app] Erc20 voucher emitted")
            return True

        if msg_sender == ERC721_PORTAL_ADDRESS:
            logger.info("[app] ERC721 deposit")
            deposit = decode_erc721_deposit(advance['payload']['data'])
            logger.info(f"[app] ERC721 deposit decoded {deposit}")

            voucher_payload = create_erc721_safetransfer_voucher(advance['app_contract'], deposit['sender'], deposit['token_id'])
            rollup.emit_voucher(deposit['token_address'], 0, voucher_payload)
            logger.info("[app] Erc721 voucher emitted")
            return True

        if msg_sender == ERC1155_SINGLE_PORTAL_ADDRESS:
            logger.info("[app] ERC1155 single deposit")
            deposit = decode_erc1155_single_deposit(advance['payload']['data'])
            logger.info(f"[app] ERC1155_single deposit decoded {deposit}")

            voucher_payload = create_erc1155_single_safetransfer_voucher(advance['app_contract'], deposit['sender'], deposit['token_id'], deposit['amount'], b'')
            rollup.emit_voucher(deposit['token_address'], 0, voucher_payload)
            logger.info("[app] Erc1155_single voucher emitted")
            return True

        if msg_sender == ERC1155_BATCH_PORTAL_ADDRESS:
            logger.info("[app] ERC1155 batch deposit")
            deposit = decode_erc1155_batch_deposit(advance['payload']['data'])
            logger.info(f"[app] ERC1155_batch deposit decoded {deposit}")

            voucher_payload = create_erc1155_batch_safetransfer_voucher(advance['app_contract'], deposit['sender'], deposit['token_ids'], deposit['amounts'], b'')
            rollup.emit_voucher(deposit['token_address'], 0, voucher_payload)
            logger.info("[app] Erc1155_batch voucher emitted")
            return True

        logger.info("[app] Unindentified advance")
        rollup.emit_report(advance['payload'].get('data',b''))
        logger.info("[app] Echo report emitted")
        return True
    except Exception as e:
        logger.error(f"[app] Failed to process advance: {e}")
        logger.error(traceback.format_exc())
        return False

def handle_inspect(rollup):
    inspect = rollup.read_inspect_state()
    logger.info(f"Received inspect request length {len(inspect['payload']['data'])}")

    rollup.emit_report(inspect['payload'].get('data',b''))
    logger.info("[app] Echo report emitted")
    return True

handlers = {
    "advance": handle_advance,
    "inspect": handle_inspect,
}

###
# Main
if __name__ == "__main__":
    rollup = Rollup()
    accept_previous_request = True

    # Main loop
    while True:
        logger.info("[app] Sending finish")

        next_request_type = rollup.finish(accept_previous_request)

        logger.info(f"[app] Received input of type {next_request_type}")

        accept_previous_request = handlers[next_request_type](rollup)

    exit(-1)
