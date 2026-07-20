# Automatizador de Holerites 2.0 — Design

**Data:** 2026-07-20
**Autor:** Fabricio Queiroz (com Claude Code)
**Status:** Aprovado para planejamento

## Contexto

Existe hoje um utilitário Windows (`automatizador_holerites 1.2.exe`, PyInstaller/Python 3.13)
distribuído apenas como executável — sem código-fonte. A interface é tkinter/ttk puro,
janela fixa de 400x300 com tema padrão do Windows (visual datado). Vamos reconstruir do zero:
interface moderna + correção de três problemas de comportamento identificados ao analisar o
executável atual.

### O que a versão 1.2 faz (extraído do binário)

1. Usuário escolhe uma pasta com vários PDFs (um holerite por arquivo).
2. Para cada PDF, extrai a **primeira** data `dd/mm/aaaa` do texto (`pdfplumber`); se for
   escaneado, cai para OCR (`pytesseract` + `pdf2image`/Poppler).
3. Renomeia cada arquivo para `AAAA-MM-DD.pdf` e remove duplicados (hash MD5).
4. Ordena pelo nome (data ISO → cronológico).
5. Junta tudo num único `HOLERITES COMPLETOS .pdf` (PyMuPDF).

Dois modos: "Renomear e Juntar" e "Somente Juntar".

### Problemas da versão 1.2 (o que corrigir)

1. **Destrutivo:** apaga do disco (`os.remove`) duplicados, conflitos de data e qualquer
   PDF onde não achou data. Opera in-place na pasta original.
2. **Data errada:** pega a primeira `dd/mm/aaaa` do texto — pode ser admissão ou pagamento,
   não a competência. Ordena errado.
3. **OCR obrigatório frágil:** depende de Tesseract + Poppler instalados na máquina.

## Objetivos

- Interface gráfica moderna (CustomTkinter), tema claro/escuro, arrastar-e-soltar.
- Processo **não-destrutivo**: originais nunca são apagados.
- Ordenação por **competência** (mês de referência), com detecção robusta.
- OCR **opcional**, com degradação graciosa quando indisponível.
- Distribuição como `.exe` único via PyInstaller.

## Decisões de escopo (confirmadas com o usuário)

- Escopo: UI nova **+** corrigir os 3 problemas.
- Tecnologia da UI: **CustomTkinter**.
- Ordenação: por **competência** (mês de referência), não por data de pagamento.
- Fixtures de teste: geradas sinteticamente (holerites fictícios), não dados reais.

## Arquitetura

Separação estrita entre lógica (testável, sem UI) e interface.

```
main.py                 → ponto de entrada; abre a GUI
core/
  extract.py            → extrai competência (ano, mês) de um PDF. Texto + OCR opcional. Puro.
  dedup.py              → hash MD5 de arquivo; detecção de duplicados idênticos.
  merge.py              → junta uma lista ordenada de PDFs num só (pypdf).
  pipeline.py           → orquestra o processo e devolve um Relatório. Zero código de UI.
gui/
  app.py                → janela CustomTkinter; roda o pipeline numa thread; mostra progresso.
tests/
  fixtures/             → holerites sintéticos (múltiplos formatos de competência).
  test_extract.py, test_pipeline.py, test_dedup.py, test_merge.py
```

Cada módulo de `core/` é usável e testável isoladamente, sem importar nada de GUI.

### `core/extract.py`

- Função principal: `extrair_competencia(pdf_path) -> Competencia | None`, onde
  `Competencia = (ano: int, mes: int)`.
- Estratégia:
  1. Extrai texto da 1ª página (`pdfplumber`), normaliza (remove acentos, minúsculas).
  2. Procura **linhas com rótulo** de competência: `compet`, `referenc`, `mes/ano`, `mes e ano`.
     Dentro dessas linhas, casa:
     - `MM/AAAA` (`(0?[1-9]|1[0-2])/20\d{2}`), ou
     - `MESNOME/AAAA` / `MESNOME de AAAA` (janeiro..dezembro).
  3. Fallback: primeiro `MESNOME + AAAA` em qualquer lugar do texto.
  4. Se nada casar e o PDF não tiver texto: tenta OCR (ver abaixo). Se ainda nada: `None`.
- **Não** deve casar datas de admissão/pagamento (`dd/mm/aaaa`) como competência.
- Validado contra fixtures nos 3 formatos.

### `core/extract.py` — OCR opcional

- Se a 1ª página não tiver texto extraível, tenta OCR **apenas se** `pytesseract` e o binário
  do Tesseract estiverem disponíveis (checagem defensiva, sem exceção fatal).
- Se indisponível, retorna `None` (o arquivo cai na lista "revisar manualmente"). O app nunca
  trava por falta de OCR.

### `core/dedup.py`

- `hash_arquivo(path) -> str` (MD5 do conteúdo).
- Dois arquivos com o mesmo hash = duplicados idênticos → mantém um, ignora o resto.

### `core/merge.py`

- `juntar(paths_ordenados, destino)` usando `pypdf` (evita dependência de PyMuPDF).
- Erros de leitura de um PDF individual não abortam o lote: o arquivo é pulado e reportado.

### `core/pipeline.py`

- `processar(pasta_origem, pasta_saida, modo, progress_cb) -> Relatorio`
- Passos:
  1. Lista `*.pdf` da pasta de origem.
  2. Para cada um, extrai competência (emite progresso via `progress_cb`).
  3. Ordena por `(ano, mes)` — ordenação estável.
  4. Deduplica idênticos por hash.
  5. Conforme o modo:
     - **renomear_e_juntar:** copia cada PDF para `pasta_saida` como `AAAA-MM.pdf`
       (conflito de conteúdo na mesma competência → `AAAA-MM (2).pdf`), e gera
       `HOLERITES COMPLETOS.pdf` na ordem cronológica.
     - **somente_juntar:** gera apenas `HOLERITES COMPLETOS.pdf` (sem cópias renomeadas).
  6. Devolve `Relatorio`.
- **Não-destrutivo:** só lê da origem e escreve na saída. Nunca remove/renomeia na origem.

### `Relatorio` (dataclass)

- `organizados: list[(arquivo, competencia)]`
- `duplicados_ignorados: list[arquivo]`
- `revisar_manualmente: list[arquivo]` (sem competência / ilegíveis)
- `conflitos: list[(arquivo, competencia)]` (mesma competência, conteúdo diferente)
- `pdf_final: path`

## Interface (gui/app.py)

- CustomTkinter, tema claro/escuro (segue o sistema, com toggle).
- Uma janela única:
  - Área grande de **arrastar-e-soltar** a pasta (via `tkinterdnd2`), com botão alternativo
    "Escolher pasta…".
  - Seletor de **pasta de saída** (padrão: `HOLERITES ORGANIZADOS/` dentro da pasta de origem).
  - Dois botões-toggle de modo: **Renomear e Juntar** / **Somente Juntar**.
  - Botão **Processar** → roda o pipeline numa **thread** (UI não congela); barra de progresso real.
  - Ao fim: **resumo** ("X organizados, Y duplicados ignorados, Z para revisar") + botão
    "Abrir pasta de saída".
- Erros aparecem em diálogo amigável, nunca stack trace cru.

## Tratamento de erros

- Pasta vazia / sem PDFs → mensagem amigável, não faz nada.
- PDF corrompido → pulado, listado no relatório.
- Sem competência → `revisar_manualmente`, arquivo intacto, fora do PDF juntado.
- Falha ao escrever a saída (permissão) → diálogo claro pedindo outra pasta.

## Testes

- `pytest` sobre fixtures sintéticas (geradas por script versionado).
- `test_extract`: cada formato de competência (`MM/AAAA`, `MESNOME/AAAA`, `MesNome de AAAA`);
  garante que admissão/pagamento NÃO são confundidas.
- `test_pipeline`: ordenação cronológica correta; **originais permanecem intactos**
  (não-destrutivo); contagem de páginas do PDF final; duplicados ignorados; conflitos mantidos.
- `test_dedup`: mesmo conteúdo → mesmo hash; conteúdos diferentes → hashes diferentes.
- `test_merge`: soma de páginas confere; PDF ilegível é pulado sem abortar.

## Distribuição

- PyInstaller `--onefile`, sem exigir Poppler/Tesseract (OCR é opcional em runtime).
- Ícone próprio; nome do executável `automatizador_holerites 2.0.exe`.

## Fora de escopo (YAGNI)

- Separar um PDF único de vários holerites em arquivos por competência.
- Agrupar por funcionário / múltiplos funcionários no mesmo lote.
- Envio por e-mail, integração com sistema de folha, banco de dados.
- Empacotar Tesseract dentro do `.exe`.
