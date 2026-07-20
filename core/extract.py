import re
import unicodedata

import pdfplumber

from core.models import MESES_PT

_LABEL = re.compile(r"(compet|referenc|mes\s*/?\s*ano|mes\s+e\s+ano)", re.I)
_NUM_MMYYYY = re.compile(r"\b(0?[1-9]|1[0-2])\s*/\s*(20\d{2})\b")
_NOME_ANO = re.compile(
    r"(" + "|".join(MESES_PT) + r")\s*(?:/|\s+de\s+)\s*(20\d{2})", re.I
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
        if _LABEL.search(linha):
            m = _NOME_ANO.search(linha)
            if m:
                return (int(m.group(2)), MESES_PT[m.group(1)])
            m = _NUM_MMYYYY.search(linha)
            if m:
                return (int(m.group(2)), int(m.group(1)))
    m = _NOME_ANO.search(ntexto)
    if m:
        return (int(m.group(2)), MESES_PT[m.group(1)])
    return None


def extrair_competencia(pdf_path: str) -> tuple[int, int] | None:
    texto = _texto_primeira_pagina(pdf_path)
    resultado = _procurar(normalizar(texto))
    if resultado is not None:
        return resultado
    if not texto.strip():
        ocr = _ocr_primeira_pagina(pdf_path)
        if ocr.strip():
            return _procurar(normalizar(ocr))
    return None
