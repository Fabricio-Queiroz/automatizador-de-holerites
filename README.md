# Automatizador de Holerites

Junta holerites em PDF num arquivo unico e, opcionalmente, renomeia cada um em
ordem cronologica. Os arquivos originais nunca sao apagados nem alterados.

Nao e preciso instalar Python. Os executaveis estao na pasta
[`executaveis/`](executaveis) e tambem em
[Releases](https://github.com/Fabricio-Queiroz/automatizador-de-holerites/releases).

## Versoes

### v3.0 cronologica - recomendada

`automatizador-holerites-cronologico-v3.0.exe`

Ordena pela **competencia** do holerite - o mes a que ele se refere - lida do
proprio documento. Renomeia para `AAAA-MM.pdf`, formato em que a ordem
alfabetica coincide com a cronologica.

- Detecta duplicados pelo conteudo do arquivo, nao pelo nome
- Le holerites escaneados por OCR ou pelo padrao do nome (`03-2001.pdf`)
- O que nao for identificado vai para uma lista "revisar manualmente", sem
  interromper o processamento
- Resultado na subpasta `HOLERITES ORGANIZADOS`

O codigo deste repositorio corresponde a esta versao. 29 testes automatizados.

### v2.0 e v2.1 - legado

`automatizador-holerites-comum-v2.0.exe`
`automatizador-holerites-comum-v2.1-intuitivo.exe`

Distribuidas apenas como executavel, mantidas para quem depende do
comportamento anterior. Renomeiam pela data de pagamento, e nao pela
competencia: como o holerite de dezembro costuma ser pago em janeiro, a
sequencia pode nao ficar cronologica na virada do ano.

A `2.1 intuitivo` abre direto nas duas opcoes; a `2.0` pede um clique em
`Iniciar` antes. Resultado na subpasta `holerites_processados`.

## Como usar

1. Abra o executavel.
2. Selecione a pasta com os holerites (um PDF por holerite).
3. Escolha `Renomear e Juntar` ou `Somente Juntar`.
4. Clique em Processar.

## Desenvolvimento

    pip install -r requirements-dev.txt
    pytest -v
    python main.py

Build do executavel: veja [`build.md`](build.md).

### OCR (opcional)

Para holerites escaneados sem camada de texto, instale o
[Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) com o pacote de
idioma portugues (`por`) disponivel no PATH. Sem ele, esses arquivos apenas
seguem para a lista "revisar manualmente".
