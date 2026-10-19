"""Estruturas de dados para os cenários e resultados."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ParametrosCusto:
    media: float
    desvio: float


@dataclass(frozen=True)
class ParametrosDuracao:
    otimista: float
    mais_provavel: float
    pessimista: float


@dataclass(frozen=True)
class FasePadrao:
    nome: str
    duracao: ParametrosDuracao
    material: ParametrosCusto
    mao_obra: ParametrosCusto
    retrabalho_prob: float = 0.0
    retrabalho_custo: float = 0.0
    retrabalho_dias: float = 0.0
    empresa_a_prob: Optional[float] = None
    alternativa_b: Optional["FasePadrao"] = None
    evento_geo_prob: float = 0.0
    evento_geo_custo: float = 0.0
    evento_geo_dias: float = 0.0
    duracao_bom: Optional[ParametrosDuracao] = None
    duracao_chuva: Optional[ParametrosDuracao] = None
    prob_chuva: float = 0.0


@dataclass(frozen=True)
class Cenario:
    nome: str
    preco_contrato: float
    prazo_contrato: float
    multa_por_dia: float
    limite_prejuizo: float
    limite_multa_media: Optional[float]
    fases: list
    multa_limite_inclusivo: bool = True


@dataclass
class ResultadoRodada:
    duracao_total: float
    custo_sem_multa: float
    multa: float
    custo_total: float
    lucro: float
    detalhamento: list = field(default_factory=list)
