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
