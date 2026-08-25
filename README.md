# Automatizador de Holerites

Junta holerites em PDF num arquivo unico e, opcionalmente, renomeia cada um.
Os arquivos originais nunca sao apagados nem alterados.

Nao e preciso instalar Python. Os executaveis estao na pasta
[`executaveis/`](executaveis) e tambem em
[Releases](https://github.com/Fabricio-Queiroz/automatizador-de-holerites/releases).

## Qual versao baixar

### Cronologica (v3.0) - recomendada

`automatizador-holerites-cronologico-v3.0.exe`

Ordena pela **competencia** do holerite (o mes a que ele se refere), lida do
proprio documento. Renomeia para `AAAA-MM.pdf`, formato em que a ordem
alfabetica coincide com a cronologica.

- Ignora duplicados (compara o conteudo, nao o nome)
- PDFs escaneados: le pelo nome do arquivo (`03-2001.pdf`) ou por OCR
- O que nao conseguir identificar vai para uma lista "revisar manualmente",
  sem travar o processamento
- Saida na subpasta `HOLERITES ORGANIZADOS`

### Comum (v2.0 e v2.1) - legado

`automatizador-holerites-comum-v2.0.exe`
`automatizador-holerites-comum-v2.1-intuitivo.exe`

Versao anterior. Renomeia pela **data de pagamento**, nao pela competencia.
Como o holerite de dezembro costuma ser pago em janeiro, a ordem final pode
nao ficar cronologica na virada do ano. Use a v3.0 salvo se voce depende do
comportamento antigo.

A `2.1 intuitivo` abre direto nas duas opcoes; a `2.0` pede um clique em
`Iniciar` antes. Saida na subpasta `holerites_processados`.

> **O codigo-fonte destas duas versoes se perdeu.** Apenas os executaveis
> foram preservados. O codigo neste repositorio corresponde somente a v3.0.

## Como usar

1. Abra o `.exe`.
2. Escolha a pasta com os holerites (um PDF por holerite).
3. Escolha `Renomear e Juntar` ou `Somente Juntar`.
4. Clique em Processar.

## Desenvolvimento

    pip install -r requirements-dev.txt
    pytest -v          # 29 testes
    python main.py

Build do `.exe`: veja `build.md`.

### OCR (opcional)

Para holerites escaneados sem camada de texto, instale o
[Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) com o pacote de
idioma portugues (`por`) e deixe-o no PATH. Sem ele, esses arquivos apenas vao
para a lista "revisar manualmente".
