import shutil
import pytest
from tests.fixtures.gen import gerar_holerite


@pytest.fixture
def pasta_holerites(tmp_path):
    """6 holerites (07..12/2025) com nomes embaralhados + 1 duplicado de agosto."""
    origem = tmp_path / "origem"
    origem.mkdir()
    jobs = [
        ("documento (3).pdf", 9, 2025, "05/10/2025", "10/02/2022", "num"),
        ("scan_0001.pdf", 7, 2025, "05/08/2025", "10/02/2022", "mesnome"),
        ("holerite final.pdf", 12, 2025, "05/01/2026", "10/02/2022", "num"),
        ("aaa.pdf", 8, 2025, "05/09/2025", "10/02/2022", "mesano"),
        ("Recibo-2.pdf", 10, 2025, "05/11/2025", "10/02/2022", "num"),
        ("xyz copia.pdf", 11, 2025, "05/12/2025", "10/02/2022", "mesnome"),
    ]
    for fn, m, a, pg, adm, st in jobs:
        gerar_holerite(str(origem / fn), a, m, pg, adm, st)
    # Duplicado byte-a-byte de aaa.pdf (copia real de arquivo, como no mundo real).
    # NAO regerar com reportlab: cada render embute CreationDate/ID diferente,
    # entao dois renders do "mesmo" holerite teriam MD5 diferente e o dedup
    # nao os detectaria. A copia garante bytes identicos.
    shutil.copy2(str(origem / "aaa.pdf"), str(origem / "duplicado.pdf"))
    return origem
