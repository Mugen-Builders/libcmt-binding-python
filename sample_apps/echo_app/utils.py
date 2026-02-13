from eth_abi_lite import decode_abi, encode_abi
# from eth_abi import decode as decode_abi, encode as encode_abi


# Bytecode for solidity transfer(address,uint256)
ERC20_TRANSFER_FUNCTION_SELECTOR_FUNSEL = b'\xa9\x05\x9c\xbb'
# Bytecode for solidity safeTransferFrom(address,address,uint256)
ERC721_TRANSFER_FUNCTION_SELECTOR_FUNSEL = b'B\x84.\x0e'
# Bytecode for solidity safeTransferFrom(address,address,uint256,uint256,bytes)
ERC1155_SINGLE_TRANSFER_FUNCTION_SELECTOR_FUNSEL = b'\xf2BC*'
# Bytecode for solidity safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)
ERC1155_BATCH_TRANSFER_FUNCTION_SELECTOR_FUNSEL = b'.\xb2\xc2\xd6'

###
# Aux Functions

def binary2hex(binary):
    """
    Encode a binary as an hex string
    """
    return "0x" + binary.hex()

###
# Decode Aux Functions

def decode_ether_deposit(binary):
    sender = binary[:20]
    amount = int.from_bytes(binary[20:52], "big")
    data = binary[52:]
    return {
        "sender":binary2hex(sender),
        "amount":amount,
        "data":data
    }

def decode_erc20_deposit(binary):
    token_address = binary[:20]
    sender = binary[20:40]
    amount = int.from_bytes(binary[40:72], "big")
    data = binary[72:]
    return {
        "sender":binary2hex(sender),
        "token_address":binary2hex(token_address),
        "amount":amount,
        "data":data
    }

def decode_erc721_deposit(binary):
    token_address = binary[:20]
    sender = binary[20:40]
    token_id = int.from_bytes(binary[40:72], "big")
    data = binary[72:]
    print(f"{sender=}")
    print(f"{token_address=}")
    print(f"{token_id=}")
    print(f"{data=}")
    base_layer_data, exec_layer_data = decode_abi(["bytes","bytes"],data)
    return {
        "token_address":binary2hex(token_address),
        "sender":binary2hex(sender),
        "token_id":token_id,
        "base_layer_data":base_layer_data,
        "exec_layer_data":exec_layer_data,
    }

def decode_erc1155_single_deposit(binary):
    token_address = binary[:20]
    sender = binary[20:40]
    token_id = int.from_bytes(binary[40:72], "big")
    amount = int.from_bytes(binary[72:104], "big")
    data = binary[104:]
    base_layer_data, exec_layer_data = decode_abi(["bytes","bytes"],data)
    return {
        "token_address":binary2hex(token_address),
        "sender":binary2hex(sender),
        "token_id":token_id,
        "amount":amount,
        "base_layer_data":base_layer_data,
        "exec_layer_data":exec_layer_data,
    }

def decode_erc1155_batch_deposit(binary):
    token_address = binary[:20]
    sender = binary[20:40]
    data = binary[40:]
    token_ids, amounts, base_layer_data, exec_layer_data = decode_abi(["uint256[]","uint256[]","bytes","bytes"],data)
    return {
        "token_address":binary2hex(token_address),
        "sender":binary2hex(sender),
        "token_ids":token_ids,
        "amounts":amounts,
        "base_layer_data":base_layer_data,
        "exec_layer_data":exec_layer_data,
    }

###
# Create Voucher Aux Functions

# Bytecode for solidity transfer(address,uint256)
ERC20_TRANSFER_FUNCTION_SELECTOR_FUNSEL = b'\xa9\x05\x9c\xbb'
# Bytecode for solidity safeTransferFrom(address,address,uint256)
ERC721_TRANSFER_FUNCTION_SELECTOR_FUNSEL = b'B\x84.\x0e'
# Bytecode for solidity safeTransferFrom(address,address,uint256,uint256,bytes)
ERC1155_SINGLE_TRANSFER_FUNCTION_SELECTOR_FUNSEL = b'\xf2BC*'
# Bytecode for solidity safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)
ERC1155_BATCH_TRANSFER_FUNCTION_SELECTOR_FUNSEL = b'.\xb2\xc2\xd6'

def create_erc20_transfer_voucher(receiver,amount):
    data = encode_abi(['address', 'uint256'], [receiver,amount])
    return ERC20_TRANSFER_FUNCTION_SELECTOR_FUNSEL + data

def create_erc721_safetransfer_voucher(sender,receiver,token_id):
    print(f"{sender=}")
    print(f"{receiver=}")
    print(f"{token_id=}")
    data = encode_abi(['address', 'address', 'uint256'], [sender,receiver,token_id])
    return ERC721_TRANSFER_FUNCTION_SELECTOR_FUNSEL + data

def create_erc1155_single_safetransfer_voucher(sender,receiver,token_id,amount,data):
    data = encode_abi(['address', 'address', 'uint256', 'uint256', 'bytes'], [sender,receiver,token_id,amount,data])
    return ERC1155_SINGLE_TRANSFER_FUNCTION_SELECTOR_FUNSEL + data

def create_erc1155_batch_safetransfer_voucher(sender,receiver,token_ids,amounts,data):
    data = encode_abi(['address', 'address', 'uint256[]', 'uint256[]', 'bytes'], [sender,receiver,token_ids,amounts,data])
    return ERC1155_SINGLE_TRANSFER_FUNCTION_SELECTOR_FUNSEL + data
