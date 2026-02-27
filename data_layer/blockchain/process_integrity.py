from typing import Dict
from .hash_chain import create_block
from .anchor import create_anchor


def process_integrity(
    complaint_id: str,
    redacted_text: str,
    previous_hash: str,
    total_blocks: int
) -> Dict:
    """
    Main integrity function.
    Called by backend after redaction.
    """

    block = create_block(
        complaint_id=complaint_id,
        redacted_text=redacted_text,
        previous_hash=previous_hash
    )

    # Anchor every 5 blocks
    if (total_blocks + 1) % 5 == 0:
        create_anchor(block["data_hash"])

    return block