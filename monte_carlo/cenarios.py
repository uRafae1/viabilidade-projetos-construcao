"""Parâmetros dos três cenários transcritos das tabelas do documento."""
from .modelos import (
    Cenario, FasePadrao, ParametrosCusto as C, ParametrosDuracao as D
)


def fase(nome, duracao, mat, mao, **kwargs):
    return FasePadrao(nome, D(*duracao), C(*mat), C(*mao), **kwargs)


def fundacao(nome, A, B, pA, geo_custo, geo_dias, pG):
    # A probabilidade pA representa escolher a empresa A; B é escolhida no caso contrário.
    b = fase(nome + " (B)", B[0], B[1], B[2])
    return fase(
        nome + " (A)", A[0], A[1], A[2],
        empresa_a_prob=pA, alternativa_b=b,
        evento_geo_prob=pG, evento_geo_custo=geo_custo, evento_geo_dias=geo_dias
    )


def pintura(nome, A, B, pA, p_chuva):
    # Durações no documento: cada empresa tem PERT para tempo bom e chuva.
    b = fase(nome + " (B)", B[0], B[1], B[2],
             duracao_bom=D(*B[3]), duracao_chuva=D(*B[4]))
    return fase(
        nome + " (A)", A[0], A[1], A[2],
        empresa_a_prob=pA, alternativa_b=b,
        duracao_bom=D(*A[3]), duracao_chuva=D(*A[4]),
        prob_chuva=p_chuva
    )


def cenario_1():
    fases = [
        fase("Preparação do terreno", (10,14,20), (120000,30000), (150000,35000)),
        fundacao("Fundação",
            ((30,40,55),(2700000,300000),(2300000,250000)),
            ((25,34,48),(3000000,350000),(2100000,260000)),
            .6, 700000, 25, .18),
        fase("Laje", (80,100,130), (2400000,300000), (1800000,200000)),
        fase("Alvenaria", (60,75,95), (900000,120000), (1600000,200000),
             retrabalho_prob=.12, retrabalho_custo=300000, retrabalho_dias=12),
        fase("Acabamento interno", (80,110,150), (2500000,350000), (2500000,400000)),
        pintura("Pintura externa",
            ((12,16,22),(300000,50000),(280000,40000),(12,16,22),(16,20,28)),
            ((10,14,18),(320000,60000),(260000,45000),(10,14,18),(14,18,24)),
            .6, .2),
    ]
    return Cenario("Cenário 1 — Edifício residencial", 19_000_000, 360, 3000,
                   .30, 200_000, fases, multa_limite_inclusivo=False)


def cenario_2():
    fases = [
        fase("Preparação do terreno", (5,7,12), (50000,12000), (80000,18000)),
        fundacao("Fundação",
            ((18,22,30),(1200000,180000),(700000,120000)),
            ((15,19,25),(1300000,200000),(650000,110000)),
            .7, 200000, 10, .08),
        fase("Laje", (18,24,32), (1000000,150000), (600000,100000)),
        fase("Alvenaria", (8,10,14), (125000,25000), (160000,30000),
             retrabalho_prob=.05, retrabalho_custo=60000, retrabalho_dias=4),
        fase("Acabamento", (14,18,26), (200000,35000), (300000,50000)),
        pintura("Pintura externa",
            ((6,7,9),(40000,7000),(50000,8000),(6,7,9),(8,9,12)),
            ((5,7,8),(45000,8000),(45000,7000),(5,7,8),(7,8,11)),
            .5, .3),
    ]
    return Cenario("Cenário 2 — Galpão logístico", 4_300_000, 150, 5000,
                   .25, None, fases)


def cenario_3():
    fases = [
        fase("Preparação do terreno", (8,12,18), (90000,20000), (120000,25000)),
        fundacao("Fundação",
            ((28,36,48),(1800000,220000),(1400000,180000)),
            ((25,32,44),(1900000,260000),(1350000,170000)),
            .5, 800000, 30, .25),
        fase("Laje", (30,40,55), (1200000,170000), (900000,120000)),
        fase("Alvenaria", (50,65,85), (600000,90000), (1300000,160000),
             retrabalho_prob=.15, retrabalho_custo=400000, retrabalho_dias=15),
        fase("Acabamento interno", (70,95,130), (2000000,300000), (2200000,300000)),
        pintura("Pintura externa",
            ((10,13,16),(120000,20000),(100000,18000),(10,13,16),(14,18,22)),
            ((9,12,15),(130000,22000),(95000,16000),(9,12,15),(12,16,20)),
            .4, .25),
    ]
    return Cenario("Cenário 3 — Centro de saúde", 12_500_000, 300, 4000,
                   .15, 50_000, fases)
