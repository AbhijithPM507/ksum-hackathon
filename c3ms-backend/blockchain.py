import hashlib
import json
from datetime import datetime


def generate_hash(data: dict) -> str:
    """
    Generate SHA-256 hash for complaint data
    """
    encoded_data = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(encoded_data).hexdigest()


def create_block(data: dict, previous_hash: str = "0") -> dict:
    """
    Create blockchain-style block
    """
    block = {
        "timestamp": str(datetime.utcnow()),
        "data": data,
        "previous_hash": previous_hash,
    }

    block_hash = generate_hash(block)
    block["hash"] = block_hash

    return block