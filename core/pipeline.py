import os
import shutil

from core.dedup import hash_arquivo
from core.extract import extrair_competencia
from core.merge import juntar
from core.models import Relatorio, nome_arquivo_competencia

NOME_FINAL = "HOLERITES COMPLETOS.pdf"


def _listar_pdfs(pasta: str) -> list[str]:
    return sorted(
        os.path.join(pasta, n)
        for n in os.listdir(pasta)
        if n.lower().endswith(".pdf")
    )


def processar(pasta_origem: str, pasta_saida: str, modo: str,
              progress_cb=None) -> Relatorio:
    rel = Relatorio(pasta_saida=pasta_saida)
    pdfs = _listar_pdfs(pasta_origem)
    total = len(pdfs)

    if total == 0:
        return rel  # pasta sem PDFs: nao cria nada, pdf_final continua None

    itens = []          # (path, competencia)
    hashes_vistos = {}  # hash -> path ja aceito

    for i, path in enumerate(pdfs, 1):
        nome = os.path.basename(path)
        if progress_cb:
            progress_cb(i, total, nome)

        comp = extrair_competencia(path)
        if comp is None:
            rel.revisar_manualmente.append(path)
            continue

        h = hash_arquivo(path)
        if h in hashes_vistos:
            rel.duplicados_ignorados.append(path)
            continue
        hashes_vistos[h] = path
        itens.append((path, comp))

    itens.sort(key=lambda t: t[1])
    rel.organizados = list(itens)

    os.makedirs(pasta_saida, exist_ok=True)

    if modo == "renomear_e_juntar":
        usados = {}  # base "AAAA-MM" -> quantidade
        for path, comp in itens:
            base = nome_arquivo_competencia(*comp)
            n = usados.get(base, 0)
            usados[base] = n + 1
            destino_nome = f"{base}.pdf" if n == 0 else f"{base} ({n + 1}).pdf"
            if n > 0:
                rel.conflitos.append((path, comp))
            shutil.copy2(path, os.path.join(pasta_saida, destino_nome))

    destino_final = os.path.join(pasta_saida, NOME_FINAL)
    juntar([p for p, _ in itens], destino_final)
    rel.pdf_final = destino_final
    return rel
