import re
import unicodedata
from pathlib import Path

import pdfplumber

from core.models import MESES_PT

_LABEL = re.compile(r"(compet|referenc|mes\s*/?\s*ano|mes\s+e\s+ano)", re.I)
_NUM_MMYYYY = re.compile(r"(?<!\d)(?<!\d/)(0?[1-9]|1[0-2])\s*/\s*(20\d{2})(?!\d)")
_NOME_ANO = re.compile(
    r"(" + "|".join(MESES_PT) + r")\s*(?:/|\s+de\s+)\s*(20\d{2})", re.I
)
_NOME_ARQUIVO_MM_ANO = re.compile(
    r"(?<!\d)(0?[1-9]|1[0-2])"
    r"(?:\s*(?:-|–|—|e)\s*(?:0?[1-9]|1[0-2]))*"
    r"\s*[-/–—]\s*(20\d{2})(?!\d)",
    re.I,
)
_NOME_ARQUIVO_ANO_MM = re.compile(
    r"(?<!\d)(20\d{2})\s*[-/–—]\s*(0?[1-9]|1[0-2])(?!\d)",
    re.I,
)


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def _texto_primeira_pagina(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            return ""
        return pdf.pages[0].extract_text() or ""


def _ocr_primeira_pagina(pdf_path: str) -> str:
    """OCR opcional. Silencioso se Tesseract/pytesseract indisponivel."""
    try:
        import pypdfium2 as pdfium
        import pytesseract
    except Exception:
        return ""
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        pil = pdf[0].render(scale=2).to_pil()
        return pytesseract.image_to_string(pil, lang="por")
    except Exception:
        return ""


def _procurar(ntexto: str) -> tuple[int, int] | None:
    for linha in ntexto.splitlines():
        m_label = _LABEL.search(linha)
        if m_label:
            # Procura o valor apenas no trecho APOS o rotulo, para nao capturar
            # datas (admissao/pagamento) que estejam antes do rotulo na mesma linha.
            sufixo = linha[m_label.end():]
            m = _NOME_ANO.search(sufixo)
            if m:
                return (int(m.group(2)), MESES_PT[m.group(1)])
            m = _NUM_MMYYYY.search(sufixo)
            if m:
                return (int(m.group(2)), int(m.group(1)))
    m = _NOME_ANO.search(ntexto)
    if m:
        return (int(m.group(2)), MESES_PT[m.group(1)])
    return None


def _competencia_no_nome(pdf_path: str) -> tuple[int, int] | None:
    """Lê competência explícita em nomes como ``01-2012.pdf``.

    Holerites digitalizados frequentemente não têm texto extraível. Nesses
    casos, o nome dado ao arquivo é a única informação confiável disponível.
    Em nomes com vários meses (ex.: ``03 e 04-2001``), usa-se o primeiro mês
    para posicionar o documento na sequência cronológica.
    """
    nome = Path(pdf_path).stem
    m = _NOME_ARQUIVO_MM_ANO.search(nome)
    if m:
        return (int(m.group(2)), int(m.group(1)))
    m = _NOME_ARQUIVO_ANO_MM.search(nome)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return None


def extrair_competencia(pdf_path: str) -> tuple[int, int] | None:
    # A pasta pode conter scans sem camada de texto. Quando o arquivo já foi
    # nomeado com MM-AAAA, essa informação deve prevalecer sobre datas de
    # admissão/pagamento encontradas no documento.
    pelo_nome = _competencia_no_nome(pdf_path)
    if pelo_nome is not None:
        return pelo_nome

    texto = _texto_primeira_pagina(pdf_path)
    resultado = _procurar(normalizar(texto))
    if resultado is not None:
        return resultado
    if not texto.strip():
        ocr = _ocr_primeira_pagina(pdf_path)
        if ocr.strip():
            return _procurar(normalizar(ocr))
    return None
