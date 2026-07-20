import os
from pypdf import PdfReader
from core.pipeline import processar


def _origem_intacta(pasta):
    return set(os.listdir(pasta)) == {
        "documento (3).pdf", "scan_0001.pdf", "holerite final.pdf",
        "aaa.pdf", "Recibo-2.pdf", "xyz copia.pdf", "duplicado.pdf",
    }


def test_nao_destrutivo_origem_intacta(pasta_holerites, tmp_path):
    saida = str(tmp_path / "out")
    processar(str(pasta_holerites), saida, "renomear_e_juntar")
    assert _origem_intacta(str(pasta_holerites))


def test_ordena_por_competencia_e_gera_final(pasta_holerites, tmp_path):
    saida = str(tmp_path / "out")
    rel = processar(str(pasta_holerites), saida, "renomear_e_juntar")
    comps = [c for _, c in rel.organizados]
    assert comps == sorted(comps)
    assert comps[0] == (2025, 7)
    assert comps[-1] == (2025, 12)
    assert rel.pdf_final == os.path.join(saida, "HOLERITES COMPLETOS.pdf")
    assert os.path.exists(rel.pdf_final)


def test_dedup_ignora_duplicado(pasta_holerites, tmp_path):
    saida = str(tmp_path / "out")
    rel = processar(str(pasta_holerites), saida, "renomear_e_juntar")
    # 7 arquivos, 1 e duplicado exato de agosto -> 6 organizados, 1 ignorado
    assert len(rel.organizados) == 6
    assert len(rel.duplicados_ignorados) == 1


def test_renomeia_com_padrao_competencia(pasta_holerites, tmp_path):
    saida = str(tmp_path / "out")
    processar(str(pasta_holerites), saida, "renomear_e_juntar")
    nomes = set(os.listdir(saida))
    assert "2025-07.pdf" in nomes
    assert "2025-12.pdf" in nomes


def test_modo_somente_juntar_nao_cria_renomeados(pasta_holerites, tmp_path):
    saida = str(tmp_path / "out")
    processar(str(pasta_holerites), saida, "somente_juntar")
    nomes = set(os.listdir(saida))
    assert nomes == {"HOLERITES COMPLETOS.pdf"}


def test_pdf_sem_competencia_vai_para_revisar(pasta_holerites, tmp_path):
    from reportlab.pdfgen import canvas
    sem = str(pasta_holerites / "sem_comp.pdf")
    c = canvas.Canvas(sem)
    c.drawString(50, 50, "documento qualquer sem competencia")
    c.save()
    saida = str(tmp_path / "out")
    rel = processar(str(pasta_holerites), saida, "renomear_e_juntar")
    assert any(p.endswith("sem_comp.pdf") for p in rel.revisar_manualmente)


def test_nao_destrutivo_com_saida_dentro_da_origem(pasta_holerites):
    # Topologia REAL do app: a pasta de saida fica DENTRO da pasta de origem.
    # Os originais devem continuar todos presentes; a unica coisa nova e a
    # subpasta de saida (o pipeline nao deve reprocessar a propria saida).
    originais = set(os.listdir(str(pasta_holerites)))
    saida = os.path.join(str(pasta_holerites), "HOLERITES ORGANIZADOS")
    processar(str(pasta_holerites), saida, "renomear_e_juntar")
    depois = set(os.listdir(str(pasta_holerites)))
    assert originais.issubset(depois)
    assert depois - originais == {"HOLERITES ORGANIZADOS"}


def test_conflito_mesma_competencia_conteudo_diferente(tmp_path):
    # Dois holerites da MESMA competencia (2025-07) com conteudo diferente:
    # ambos sao preservados, o segundo vira "2025-07 (2).pdf".
    from tests.fixtures.gen import gerar_holerite
    origem = tmp_path / "origem"
    origem.mkdir()
    gerar_holerite(str(origem / "a.pdf"), 2025, 7, "05/08/2025",
                   "10/02/2022", "num", nome="FULANO A")
    gerar_holerite(str(origem / "b.pdf"), 2025, 7, "05/08/2025",
                   "10/02/2022", "num", nome="BELTRANO B")
    saida = str(tmp_path / "out")
    rel = processar(str(origem), saida, "renomear_e_juntar")
    nomes = set(os.listdir(saida))
    assert "2025-07.pdf" in nomes
    assert "2025-07 (2).pdf" in nomes
    assert len(rel.conflitos) == 1


def test_pasta_vazia_nao_faz_nada(tmp_path):
    # Pasta sem PDFs: nao cria pasta de saida nem PDF; relatorio vazio.
    origem = tmp_path / "vazia"
    origem.mkdir()
    saida = str(tmp_path / "out")
    rel = processar(str(origem), saida, "renomear_e_juntar")
    assert rel.organizados == []
    assert rel.pdf_final is None
    assert not os.path.exists(saida)
