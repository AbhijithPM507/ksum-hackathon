import json
from datetime import datetime
from pathlib import Path

ANCHOR_FILE = Path("data_layer/blockchain/anchor_log.json")


def create_anchor(latest_hash: str):
    """
    Stores latest chain hash externally.
    Strengthens integrity.
    """

    anchor_record = {
        "anchor_time": datetime.utcnow().isoformat(),
        "latest_hash": latest_hash
    }
    
    with open(ANCHOR_FILE, "a") as f:
        json.dump(anchor_record, f)
        f.write("\n")