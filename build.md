# Build do executavel

## Pre-requisitos
    pip install -r requirements-dev.txt

## Gerar o .exe
    pyinstaller --noconfirm --clean "automatizador_holerites 2.0.spec"

O arquivo `.spec` inclui o ícone e força a inclusão do Tcl/Tk, necessária
quando o PyInstaller não detecta corretamente o `tkinter` instalado.

O executavel sai em `dist/`.

## OCR (opcional)
O app renderiza paginas escaneadas com `pypdfium2` (empacotado junto) e le o
texto com `pytesseract`, que POR SUA VEZ EXIGE o motor Tesseract OCR
instalado na maquina e no PATH, COM o pacote de idioma portugues (`por`).
Sem o Tesseract instalado, PDFs escaneados vao para a lista "revisar
manualmente" e o app nao trava.
