from core.models import MESES_PT, nome_arquivo_competencia, Relatorio


def test_meses_pt_cobre_12_meses():
    assert MESES_PT["janeiro"] == 1
    assert MESES_PT["dezembro"] == 12
    assert len(MESES_PT) == 12


def test_nome_arquivo_competencia_formata_com_zero_a_esquerda():
    assert nome_arquivo_competencia(2025, 7) == "2025-07"
    assert nome_arquivo_competencia(2025, 12) == "2025-12"


def test_relatorio_defaults_vazios():
    r = Relatorio()
    assert r.organizados == []
    assert r.duplicados_ignorados == []
    assert r.revisar_manualmente == []
    assert r.pdf_final is None
