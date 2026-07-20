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
