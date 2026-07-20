from core.extract import extrair_competencia, normalizar
from tests.fixtures.gen import gerar_holerite


def test_normalizar_remove_acentos_e_baixa_caixa():
    assert normalizar("Competência JULHO") == "competencia julho"


def test_extrai_competencia_formato_numerico(tmp_path):
    p = str(tmp_path / "a.pdf")
    gerar_holerite(p, 2025, 3, "05/04/2025", "10/02/2022", "num")
    assert extrair_competencia(p) == (2025, 3)


def test_extrai_competencia_formato_mesnome(tmp_path):
    p = str(tmp_path / "b.pdf")
    gerar_holerite(p, 2024, 11, "05/12/2024", "10/02/2022", "mesnome")
    assert extrair_competencia(p) == (2024, 11)


def test_extrai_competencia_formato_mesano(tmp_path):
    p = str(tmp_path / "c.pdf")
    gerar_holerite(p, 2025, 1, "05/02/2025", "10/02/2022", "mesano")
    assert extrair_competencia(p) == (2025, 1)


def test_nao_confunde_com_admissao_ou_pagamento(tmp_path):
    # admissao 10/02/2022, pagamento 05/09/2025, competencia agosto/2025
    p = str(tmp_path / "d.pdf")
    gerar_holerite(p, 2025, 8, "05/09/2025", "10/02/2022", "mesano")
    assert extrair_competencia(p) == (2025, 8)


def test_pdf_sem_competencia_retorna_none(tmp_path):
    from reportlab.pdfgen import canvas
    p = str(tmp_path / "vazio.pdf")
    c = canvas.Canvas(p)
    c.drawString(50, 50, "documento sem competencia aqui")
    c.save()
    assert extrair_competencia(p) is None
