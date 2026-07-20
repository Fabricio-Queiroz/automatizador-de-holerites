from core.dedup import hash_arquivo


def test_mesmo_conteudo_mesmo_hash(tmp_path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"conteudo identico")
    b.write_bytes(b"conteudo identico")
    assert hash_arquivo(str(a)) == hash_arquivo(str(b))


def test_conteudo_diferente_hash_diferente(tmp_path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"conteudo um")
    b.write_bytes(b"conteudo dois")
    assert hash_arquivo(str(a)) != hash_arquivo(str(b))
