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


def test_competencia_e_data_na_mesma_linha_nao_confunde(tmp_path):
    # Rotulo de competencia e uma data dd/mm/aaaa (admissao) na MESMA linha extraida.
    # Nao pode ler o dia/mes da admissao como competencia.
    from reportlab.pdfgen import canvas
    p = str(tmp_path / "mesma_linha.pdf")
    c = canvas.Canvas(p)
    y = 700
    c.drawString(40, y, "Admissao: 10/02/2022")
    c.drawString(260, y, "Competencia: 07/2025")
    c.save()
    assert extrair_competencia(p) == (2025, 7)


def test_extrai_competencia_do_nome_de_scan(tmp_path):
    # Scans sem camada de texto ainda devem entrar na ordem correta.
    p = str(tmp_path / "01-2012.pdf")
    (tmp_path / "01-2012.pdf").write_bytes(b"scan")
    assert extrair_competencia(p) == (2012, 1)


def test_nome_do_arquivo_prevalece_sobre_data_do_conteudo(tmp_path):
    p = str(tmp_path / "12-2012.pdf")
    gerar_holerite(p, 2025, 7, "05/08/2025", "10/02/2022", "num")
    assert extrair_competencia(p) == (2012, 12)


def test_nome_com_varios_meses_usa_o_primeiro_mes(tmp_path):
    p = str(tmp_path / "03 e 04-2001 (Início).pdf")
    (tmp_path / "03 e 04-2001 (Início).pdf").write_bytes(b"scan")
    assert extrair_competencia(p) == (2001, 3)


def test_ocr_helper_nunca_levanta_em_caminho_invalido():
    # OCR opcional: caminho invalido nunca pode lancar excecao; retorna "".
    from core.extract import _ocr_primeira_pagina
    assert _ocr_primeira_pagina("caminho/que/nao/existe.pdf") == ""
