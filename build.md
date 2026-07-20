# Build do executavel

## Pre-requisitos
    pip install -r requirements-dev.txt

## Gerar o .exe
    pyinstaller --onefile --windowed --name "automatizador_holerites 2.0" ^
      --collect-all customtkinter ^
      main.py

O executavel sai em `dist/`.

## OCR (opcional)
O app renderiza paginas escaneadas com `pypdfium2` (empacotado junto) e le o
texto com `pytesseract`, que POR SUA VEZ EXIGE o motor Tesseract OCR
instalado na maquina e no PATH, COM o pacote de idioma portugues (`por`).
Sem o Tesseract instalado, PDFs escaneados vao para a lista "revisar
manualmente" e o app nao trava.
