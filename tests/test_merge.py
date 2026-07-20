from pypdf import PdfReader
from core.merge import juntar
from tests.fixtures.gen import gerar_holerite


def test_juntar_soma_paginas(tmp_path):
    p1 = str(tmp_path / "1.pdf")
    p2 = str(tmp_path / "2.pdf")
    gerar_holerite(p1, 2025, 7, "05/08/2025", "10/02/2022", "num")
    gerar_holerite(p2, 2025, 8, "05/09/2025", "10/02/2022", "num")
    destino = str(tmp_path / "final.pdf")
    total = juntar([p1, p2], destino)
    assert total == 2
    assert len(PdfReader(destino).pages) == 2


def test_juntar_pula_pdf_ilegivel(tmp_path):
    bom = str(tmp_path / "bom.pdf")
    ruim = str(tmp_path / "ruim.pdf")
    gerar_holerite(bom, 2025, 7, "05/08/2025", "10/02/2022", "num")
    (tmp_path / "ruim.pdf").write_bytes(b"isso nao e um pdf")
    destino = str(tmp_path / "final.pdf")
    total = juntar([bom, ruim], destino)
    assert total == 1
    assert len(PdfReader(destino).pages) == 1


def test_juntar_pdf_ilegivel_no_inicio_nao_impede_os_bons(tmp_path):
    # Um PDF ilegivel LOGO NO INICIO nao pode impedir os arquivos bons seguintes.
    ruim = str(tmp_path / "ruim.pdf")
    bom = str(tmp_path / "bom.pdf")
    (tmp_path / "ruim.pdf").write_bytes(b"isso nao e um pdf")
    gerar_holerite(bom, 2025, 7, "05/08/2025", "10/02/2022", "num")
    destino = str(tmp_path / "final.pdf")
    total = juntar([ruim, bom], destino)
    assert total == 1
    assert len(PdfReader(destino).pages) == 1
