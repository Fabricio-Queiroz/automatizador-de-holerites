# Automatizador de Holerites 2.0 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruir o utilitário de holerites com interface moderna (CustomTkinter), processo não-destrutivo, ordenação por competência e OCR opcional.

**Architecture:** Lógica pura em `core/` (sem dependência de UI, 100% testável) orquestrada por `core/pipeline.py`, que devolve um `Relatorio`. A GUI em `gui/app.py` (CustomTkinter) roda o pipeline numa thread e apenas apresenta progresso/resultado. Ponto de entrada em `main.py`.

**Tech Stack:** Python 3.12+, CustomTkinter (GUI), tkinterdnd2 (arrastar-e-soltar), pdfplumber (texto), pypdf (merge), pytesseract (OCR opcional), pytest (testes), PyInstaller (empacotamento).

## Global Constraints

- Python 3.12 ou superior.
- **Não-destrutivo:** nenhum código pode remover, renomear ou sobrescrever arquivos na pasta de origem. Só leitura na origem; escrita apenas na pasta de saída.
- Merge de PDFs usa **pypdf** (não PyMuPDF).
- OCR é **opcional em runtime**: ausência de `pytesseract`/Tesseract nunca lança exceção fatal — degrada para `None`.
- Competência é a tupla `(ano: int, mes: int)`.
- Nome do PDF final: exatamente `HOLERITES COMPLETOS.pdf` (sem espaço extra).
- Padrão de arquivo renomeado: `AAAA-MM.pdf` (ex.: `2025-07.pdf`); conflito de conteúdo na mesma competência: `AAAA-MM (2).pdf`, `AAAA-MM (3).pdf`, …
- Pasta de saída padrão: `HOLERITES ORGANIZADOS/` dentro da pasta de origem.
- Modos: `"renomear_e_juntar"` e `"somente_juntar"`.
- Textos de UI em português.

---

## File Structure

```
main.py                         → ponto de entrada; abre a GUI
core/__init__.py
core/models.py                  → dataclasses: Competencia helpers, Relatorio, ResultadoArquivo
core/extract.py                 → extrair_competencia(pdf_path) -> tuple[int,int] | None
core/dedup.py                   → hash_arquivo(path) -> str
core/merge.py                   → juntar(paths, destino) -> int (nº de páginas)
core/pipeline.py                → processar(origem, saida, modo, progress_cb) -> Relatorio
gui/__init__.py
gui/app.py                      → AppHolerites(ctk.CTk): janela, thread, progresso, resumo
tests/__init__.py
tests/conftest.py               → fixture que gera holerites sintéticos numa tmp_path
tests/fixtures/gen.py           → gerador de holerites sintéticos (reportlab)
tests/test_extract.py
tests/test_dedup.py
tests/test_merge.py
tests/test_pipeline.py
requirements.txt
requirements-dev.txt
build.md                        → instruções de empacotamento PyInstaller
```

---

## Task 1: Projeto base, dependências e gerador de fixtures

**Files:**
- Create: `requirements.txt`, `requirements-dev.txt`
- Create: `core/__init__.py`, `gui/__init__.py`, `tests/__init__.py`
- Create: `tests/fixtures/gen.py`
- Create: `tests/conftest.py`

**Interfaces:**
- Produces: `gerar_holerite(path, ano, mes, pagamento, admissao, comp_style="num", nome="MARIA S. OLIVEIRA")` em `tests/fixtures/gen.py`. `comp_style` ∈ {`"num"` → `Competencia: MM/AAAA`, `"mesnome"` → `Referencia: MESNOME/AAAA`, `"mesano"` → `Mes/Ano: Mesnome de AAAA`}.
- Produces: pytest fixture `pasta_holerites` (em `conftest.py`) que cria 6 holerites em competências 07..12/2025 (nomes de arquivo embaralhados) + 1 duplicado exato de agosto, numa `tmp_path`, e devolve essa pasta.

- [ ] **Step 1: Criar os arquivos de requirements**

`requirements.txt`:
```
customtkinter>=5.2
tkinterdnd2>=0.4
pdfplumber>=0.11
pypdf>=4.0
pytesseract>=0.3
```

`requirements-dev.txt`:
```
-r requirements.txt
pytest>=8.0
reportlab>=4.0
pyinstaller>=6.0
```

- [ ] **Step 2: Criar os `__init__.py` vazios**

Crie `core/__init__.py`, `gui/__init__.py`, `tests/__init__.py` (arquivos vazios).

- [ ] **Step 3: Escrever o gerador de fixtures**

`tests/fixtures/gen.py`:
```python
"""Gera holerites ficticios (Recibo de Pagamento de Salario) para teste."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

MESES = ["JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO",
         "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]


def gerar_holerite(path, ano, mes, pagamento, admissao,
                   comp_style="num", nome="MARIA S. OLIVEIRA"):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    y = h - 25 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, y, "NITATORI ADVOGADOS ASSOCIADOS")
    c.setFont("Helvetica", 8)
    c.drawString(20 * mm, y - 5 * mm, "CNPJ: 12.345.678/0001-90")
    c.drawRightString(w - 20 * mm, y, "Recibo de Pagamento de Salario")

    y -= 18 * mm
    c.setFont("Helvetica", 9)
    if comp_style == "num":
        comp_txt = f"Competencia: {mes:02d}/{ano}"
    elif comp_style == "mesnome":
        comp_txt = f"Referencia: {MESES[mes - 1]}/{ano}"
    else:
        comp_txt = f"Mes/Ano: {MESES[mes - 1].capitalize()} de {ano}"
    c.drawString(20 * mm, y, comp_txt)

    y -= 10 * mm
    c.drawString(20 * mm, y, f"Nome: {nome}")
    c.drawString(120 * mm, y, "CPF: 123.456.789-00")
    y -= 6 * mm
    c.drawString(20 * mm, y, "Cargo: Assistente Juridico")
    c.drawString(120 * mm, y, f"Admissao: {admissao}")

    y -= 12 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20 * mm, y, "Descricao")
    c.drawString(120 * mm, y, "Vencimentos")
    c.setFont("Helvetica", 9)
    for desc, v in [("Salario base", "3.500,00"), ("INSS", ""), ("IRRF", "")]:
        y -= 6 * mm
        c.drawString(20 * mm, y, desc)
        if v:
            c.drawString(120 * mm, y, v)

    y -= 12 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Liquido a Receber: R$ 3.017,50")

    y -= 20 * mm
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, y, f"Sao Paulo, {pagamento}")
    c.save()
```

- [ ] **Step 4: Escrever a fixture pytest compartilhada**

`tests/conftest.py`:
```python
import os
import pytest
from tests.fixtures.gen import gerar_holerite


@pytest.fixture
def pasta_holerites(tmp_path):
    """6 holerites (07..12/2025) com nomes embaralhados + 1 duplicado de agosto."""
    jobs = [
        ("documento (3).pdf", 9, 2025, "05/10/2025", "10/02/2022", "num"),
        ("scan_0001.pdf", 7, 2025, "05/08/2025", "10/02/2022", "mesnome"),
        ("holerite final.pdf", 12, 2025, "05/01/2026", "10/02/2022", "num"),
        ("aaa.pdf", 8, 2025, "05/09/2025", "10/02/2022", "mesano"),
        ("Recibo-2.pdf", 10, 2025, "05/11/2025", "10/02/2022", "num"),
        ("xyz copia.pdf", 11, 2025, "05/12/2025", "10/02/2022", "mesnome"),
    ]
    for fn, m, a, pg, adm, st in jobs:
        gerar_holerite(str(tmp_path / fn), a, m, pg, adm, st)
    # duplicado exato de aaa.pdf (mesmo conteudo, nome diferente)
    gerar_holerite(str(tmp_path / "duplicado.pdf"), 2025, 8,
                   "05/09/2025", "10/02/2022", "mesano")
    return tmp_path
```
> Nota: a assinatura de `gerar_holerite` é `(path, ano, mes, ...)`. Repare que o `jobs` acima lista `(fn, mes, ano, ...)` e é remapeado na chamada — mantenha a ordem `a, m` (ano, mês) exatamente como no `gerar_holerite(...)` do duplicado.

- [ ] **Step 5: Instalar dependências de desenvolvimento**

Run: `pip install -r requirements-dev.txt`
Expected: instala customtkinter, tkinterdnd2, pdfplumber, pypdf, pytesseract, pytest, reportlab, pyinstaller sem erro.

- [ ] **Step 6: Verificar que a fixture gera PDFs**

Run: `python -c "from reportlab.pdfgen import canvas; print('reportlab ok')"`
Expected: `reportlab ok`

- [ ] **Step 7: Commit**

```bash
git add requirements.txt requirements-dev.txt core/__init__.py gui/__init__.py tests/__init__.py tests/fixtures/gen.py tests/conftest.py
git commit -m "chore: projeto base, dependencias e gerador de fixtures"
```

---

## Task 2: Modelos de dados (`core/models.py`)

**Files:**
- Create: `core/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Produces:
  - `MESES_PT: dict[str,int]` — nome de mês normalizado (sem acento, minúsculo) → número (1..12).
  - `nome_arquivo_competencia(ano, mes) -> str` → `"AAAA-MM"` (sem extensão).
  - `@dataclass ResultadoArquivo`: `origem: str`, `competencia: tuple[int,int] | None`, `hash: str | None`.
  - `@dataclass Relatorio`: `organizados: list[tuple[str, tuple[int,int]]]`, `duplicados_ignorados: list[str]`, `revisar_manualmente: list[str]`, `conflitos: list[tuple[str, tuple[int,int]]]`, `pdf_final: str | None`, `pasta_saida: str | None`.

- [ ] **Step 1: Escrever o teste**

`tests/test_models.py`:
```python
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
```

- [ ] **Step 2: Rodar o teste e ver falhar**

Run: `pytest tests/test_models.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.models'`

- [ ] **Step 3: Implementar `core/models.py`**

```python
from dataclasses import dataclass, field

MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def nome_arquivo_competencia(ano: int, mes: int) -> str:
    return f"{ano:04d}-{mes:02d}"


@dataclass
class ResultadoArquivo:
    origem: str
    competencia: tuple[int, int] | None = None
    hash: str | None = None


@dataclass
class Relatorio:
    organizados: list = field(default_factory=list)
    duplicados_ignorados: list = field(default_factory=list)
    revisar_manualmente: list = field(default_factory=list)
    conflitos: list = field(default_factory=list)
    pdf_final: str | None = None
    pasta_saida: str | None = None
```

- [ ] **Step 4: Rodar o teste e ver passar**

Run: `pytest tests/test_models.py -v`
Expected: PASS (3 testes)

- [ ] **Step 5: Commit**

```bash
git add core/models.py tests/test_models.py
git commit -m "feat: modelos de dados (Competencia helpers e Relatorio)"
```

---

## Task 3: Extração de competência (`core/extract.py`)

**Files:**
- Create: `core/extract.py`
- Test: `tests/test_extract.py`

**Interfaces:**
- Consumes: `core.models.MESES_PT`.
- Produces:
  - `normalizar(texto: str) -> str` (remove acentos, minúsculas).
  - `extrair_competencia(pdf_path: str) -> tuple[int,int] | None` — devolve `(ano, mes)` ou `None`.

- [ ] **Step 1: Escrever os testes**

`tests/test_extract.py`:
```python
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
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_extract.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.extract'`

- [ ] **Step 3: Implementar `core/extract.py`**

```python
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
```
> Nota: o OCR usa `pypdfium2` (já disponível) para rasterizar e `pytesseract` para reconhecer. Se qualquer um faltar, retorna `""` — nunca lança.

- [ ] **Step 4: Rodar e ver passar**

Run: `pytest tests/test_extract.py -v`
Expected: PASS (6 testes)

- [ ] **Step 5: Commit**

```bash
git add core/extract.py tests/test_extract.py
git commit -m "feat: extracao de competencia por rotulo (texto + OCR opcional)"
```

---

## Task 4: Hash de arquivo / dedup (`core/dedup.py`)

**Files:**
- Create: `core/dedup.py`
- Test: `tests/test_dedup.py`

**Interfaces:**
- Produces: `hash_arquivo(path: str) -> str` (MD5 hex do conteúdo, leitura em blocos).

- [ ] **Step 1: Escrever os testes**

`tests/test_dedup.py`:
```python
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
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_dedup.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.dedup'`

- [ ] **Step 3: Implementar `core/dedup.py`**

```python
import hashlib


def hash_arquivo(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()
```

- [ ] **Step 4: Rodar e ver passar**

Run: `pytest tests/test_dedup.py -v`
Expected: PASS (2 testes)

- [ ] **Step 5: Commit**

```bash
git add core/dedup.py tests/test_dedup.py
git commit -m "feat: hash md5 de arquivo para deteccao de duplicados"
```

---

## Task 5: Merge de PDFs (`core/merge.py`)

**Files:**
- Create: `core/merge.py`
- Test: `tests/test_merge.py`

**Interfaces:**
- Produces: `juntar(paths: list[str], destino: str) -> int` — grava o PDF combinado em `destino` na ordem recebida e devolve o total de páginas. PDFs individuais ilegíveis são pulados (não abortam).

- [ ] **Step 1: Escrever os testes**

`tests/test_merge.py`:
```python
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
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_merge.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.merge'`

- [ ] **Step 3: Implementar `core/merge.py`**

```python
from pypdf import PdfReader, PdfWriter


def juntar(paths: list[str], destino: str) -> int:
    writer = PdfWriter()
    total = 0
    for path in paths:
        try:
            reader = PdfReader(path)
        except Exception:
            continue
        for pagina in reader.pages:
            writer.add_page(pagina)
            total += 1
    with open(destino, "wb") as f:
        writer.write(f)
    return total
```

- [ ] **Step 4: Rodar e ver passar**

Run: `pytest tests/test_merge.py -v`
Expected: PASS (2 testes)

- [ ] **Step 5: Commit**

```bash
git add core/merge.py tests/test_merge.py
git commit -m "feat: merge de pdfs com pypdf, pulando arquivos ilegiveis"
```

---

## Task 6: Pipeline orquestrador (`core/pipeline.py`)

**Files:**
- Create: `core/pipeline.py`
- Test: `tests/test_pipeline.py`

**Interfaces:**
- Consumes: `extrair_competencia`, `hash_arquivo`, `juntar`, `nome_arquivo_competencia`, `Relatorio`.
- Produces: `processar(pasta_origem: str, pasta_saida: str, modo: str, progress_cb=None) -> Relatorio`.
  - `modo ∈ {"renomear_e_juntar", "somente_juntar"}`.
  - `progress_cb`, se dado, é chamado como `progress_cb(atual: int, total: int, nome: str)`.
  - Não-destrutivo: só lê de `pasta_origem`, só escreve em `pasta_saida`.

- [ ] **Step 1: Escrever os testes**

`tests/test_pipeline.py`:
```python
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
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `pytest tests/test_pipeline.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'core.pipeline'`

- [ ] **Step 3: Implementar `core/pipeline.py`**

```python
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
```

- [ ] **Step 4: Rodar e ver passar**

Run: `pytest tests/test_pipeline.py -v`
Expected: PASS (6 testes)

- [ ] **Step 5: Rodar a suíte toda**

Run: `pytest -v`
Expected: PASS (todos os testes das Tasks 2-6)

- [ ] **Step 6: Commit**

```bash
git add core/pipeline.py tests/test_pipeline.py
git commit -m "feat: pipeline nao-destrutivo (extrai, ordena, dedup, renomeia, junta)"
```

---

## Task 7: Interface CustomTkinter (`gui/app.py` + `main.py`)

**Files:**
- Create: `gui/app.py`
- Create: `main.py`

**Interfaces:**
- Consumes: `core.pipeline.processar`, `core.models.Relatorio`.
- Produces: `AppHolerites(ctk.CTk)` e `main()` em `main.py` que instancia e roda `.mainloop()`.

> Esta task é de UI e é validada manualmente (rodando o app), não por pytest. Cada step ainda é pequeno.

- [ ] **Step 1: Escrever `gui/app.py` — esqueleto da janela**

```python
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.pipeline import processar

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class AppHolerites(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Automatizador de Holerites 2.0")
        self.geometry("560x520")
        self.minsize(520, 480)

        self.pasta_origem = None
        self.modo = ctk.StringVar(value="renomear_e_juntar")

        self._montar_ui()

    def _montar_ui(self):
        ctk.CTkLabel(
            self, text="Automatizador de Holerites",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(24, 4))
        ctk.CTkLabel(
            self, text="Junta e renomeia holerites em ordem cronologica",
            text_color=("gray40", "gray70"),
        ).pack(pady=(0, 16))

        self.area = ctk.CTkFrame(self, height=120, corner_radius=12)
        self.area.pack(fill="x", padx=24, pady=8)
        self.lbl_pasta = ctk.CTkLabel(
            self.area, text="Nenhuma pasta selecionada",
            font=ctk.CTkFont(size=13),
        )
        self.lbl_pasta.pack(expand=True, pady=8)
        ctk.CTkButton(
            self.area, text="Escolher pasta com holerites...",
            command=self._escolher_pasta,
        ).pack(pady=(0, 12))

        seg = ctk.CTkSegmentedButton(
            self, values=["Renomear e Juntar", "Somente Juntar"],
            command=self._trocar_modo,
        )
        seg.set("Renomear e Juntar")
        seg.pack(pady=16)

        self.btn = ctk.CTkButton(
            self, text="Processar", height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._processar,
        )
        self.btn.pack(pady=8, padx=24, fill="x")

        self.progresso = ctk.CTkProgressBar(self)
        self.progresso.set(0)
        self.progresso.pack(pady=8, padx=24, fill="x")

        self.status = ctk.CTkLabel(self, text="", justify="left")
        self.status.pack(pady=8, padx=24, fill="x")
```

- [ ] **Step 2: Adicionar os handlers de pasta e modo**

Adicione dentro da classe `AppHolerites`:
```python
    def _escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com os holerites")
        if pasta:
            self.pasta_origem = pasta
            self.lbl_pasta.configure(text=pasta)

    def _trocar_modo(self, valor):
        self.modo.set(
            "renomear_e_juntar" if valor == "Renomear e Juntar" else "somente_juntar"
        )
```

- [ ] **Step 3: Adicionar o processamento em thread + progresso**

Adicione dentro da classe:
```python
    def _processar(self):
        if not self.pasta_origem:
            messagebox.showwarning("Atencao", "Escolha uma pasta primeiro.")
            return
        self.btn.configure(state="disabled")
        self.progresso.set(0)
        self.status.configure(text="Processando...")
        saida = os.path.join(self.pasta_origem, "HOLERITES ORGANIZADOS")
        threading.Thread(
            target=self._rodar, args=(saida,), daemon=True
        ).start()

    def _rodar(self, saida):
        def cb(atual, total, nome):
            frac = atual / total if total else 0
            self.after(0, lambda: self.progresso.set(frac))

        try:
            rel = processar(self.pasta_origem, saida, self.modo.get(), cb)
        except Exception as e:
            self.after(0, lambda: self._erro(str(e)))
            return
        self.after(0, lambda: self._concluir(rel, saida))

    def _erro(self, msg):
        self.btn.configure(state="normal")
        self.status.configure(text="")
        messagebox.showerror("Erro", msg)
```

- [ ] **Step 4: Adicionar o resumo final + abrir pasta**

Adicione dentro da classe:
```python
    def _concluir(self, rel, saida):
        self.progresso.set(1)
        self.btn.configure(state="normal")
        resumo = (
            f"Concluido!\n"
            f"{len(rel.organizados)} organizados  |  "
            f"{len(rel.duplicados_ignorados)} duplicados ignorados  |  "
            f"{len(rel.revisar_manualmente)} para revisar"
        )
        self.status.configure(text=resumo)
        if messagebox.askyesno("Sucesso", resumo + "\n\nAbrir a pasta de saida?"):
            os.startfile(saida)
```
> `os.startfile` é Windows-only (alvo do projeto). Correto aqui.

- [ ] **Step 5: Escrever `main.py`**

```python
from gui.app import AppHolerites


def main():
    app = AppHolerites()
    app.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Rodar o app manualmente e validar o fluxo**

Run: `python main.py`
Ação: escolher a pasta `tests` gerada (ou uma pasta com holerites de teste — gere uma com `python -c "from tests.conftest import *"`... ou copie fixtures), processar em ambos os modos.
Expected: janela moderna abre; barra de progresso anda; resumo aparece; pasta `HOLERITES ORGANIZADOS` criada com `HOLERITES COMPLETOS.pdf`; **originais intactos**.

- [ ] **Step 7: Commit**

```bash
git add gui/app.py main.py
git commit -m "feat: interface CustomTkinter com progresso e resumo"
```

---

## Task 8: Empacotamento PyInstaller + docs

**Files:**
- Create: `build.md`
- Create: `README.md`

**Interfaces:**
- Produces: instruções reproduzíveis para gerar `automatizador_holerites 2.0.exe`.

- [ ] **Step 1: Escrever `build.md`**

```markdown
# Build do executavel

## Pre-requisitos
    pip install -r requirements-dev.txt

## Gerar o .exe
    pyinstaller --onefile --windowed --name "automatizador_holerites 2.0" ^
      --collect-all customtkinter ^
      --collect-all tkinterdnd2 ^
      main.py

O executavel sai em `dist/`.

## OCR (opcional)
O OCR so funciona se o Tesseract estiver instalado na maquina e no PATH,
com o pacote de idioma `por`. Sem ele, PDFs escaneados vao para a lista
"revisar manualmente" — o app nao trava.
```

- [ ] **Step 2: Escrever `README.md`**

```markdown
# Automatizador de Holerites 2.0

Junta e renomeia holerites (PDF) em ordem cronologica pela competencia.

## Como usar
1. Abra o app.
2. Escolha a pasta com os holerites (um PDF por holerite).
3. Escolha o modo: "Renomear e Juntar" ou "Somente Juntar".
4. Clique em Processar.

O resultado sai na subpasta `HOLERITES ORGANIZADOS`. **Os arquivos
originais nunca sao apagados nem alterados.**

## Desenvolvimento
    pip install -r requirements-dev.txt
    pytest -v          # roda os testes
    python main.py     # roda o app

Build do .exe: veja `build.md`.
```

- [ ] **Step 3: Gerar o executável e validar**

Run: `pyinstaller --onefile --windowed --name "automatizador_holerites 2.0" --collect-all customtkinter --collect-all tkinterdnd2 main.py`
Expected: `dist/automatizador_holerites 2.0.exe` criado; ao abrir, a janela aparece e um processamento de teste funciona.

- [ ] **Step 4: Commit**

```bash
git add build.md README.md
git commit -m "docs: instrucoes de build e uso"
```

---

## Notas de execução

- Rode `pytest -v` ao fim de cada task de `core/` — a suíte deve ficar sempre verde.
- Tasks 2-6 são puro TDD e não precisam de interação gráfica.
- Task 7 (UI) e Task 8 (build) exigem validação manual rodando o app/exe.
- `tkinterdnd2` (arrastar-e-soltar) está nas dependências e no build; a integração visual de DnD pode ser adicionada na Task 7 como melhoria, mas o botão "Escolher pasta" já cobre o fluxo — não bloqueia a entrega.
