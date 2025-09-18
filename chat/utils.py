import hashlib


def pair_key_for_users(a_id: int, b_id: int) -> str:
    x, y = sorted([int(a_id), int(b_id)])
    return hashlib.sha256(f"pair:{x}:{y}".encode()).hexdigest()
