import hashlib


def hash_arquivo(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()
