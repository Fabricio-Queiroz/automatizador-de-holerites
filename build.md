# Build do executavel

## Pre-requisitos
    pip install -r requirements-dev.txt

## Gerar o .exe
    pyinstaller --onefile --windowed --name "automatizador_holerites 2.0" ^
      --collect-all customtkinter ^
      main.py

O executavel sai em `dist/`.

## OCR (opcional)
O OCR so funciona se o Tesseract estiver instalado na maquina e no PATH,
com o pacote de idioma `por`. Sem ele, PDFs escaneados vao para a lista
"revisar manualmente" — o app nao trava.
