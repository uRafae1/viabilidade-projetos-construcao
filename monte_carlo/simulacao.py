"""Simulação de uma obra, replicações Monte Carlo e métricas."""
import math
from .geradores import GeradorAleatorio
from .modelos import ResultadoRodada


def sortear_custo(gerador, parametros, distribuicao):
    media, desvio = parametros.media, parametros.desvio
    if desvio < 0:
        raise ValueError("O desvio padrão não pode ser negativo.")
    if distribuicao == "normal":
        return gerador.normal(media, desvio)
    if distribuicao == "lognormal":
        if media <= 0:
            raise ValueError("A média da LogNormal deve ser positiva.")
        sigma2 = math.log(1 + (desvio / media) ** 2)
        sigma_ln = sigma2 ** 0.5
        mu_ln = math.log(media) - sigma2 / 2
        return gerador.lognormal(mu_ln, sigma_ln)
    raise ValueError(f"Distribuição desconhecida: {distribuicao}")


def simular_fase(fase, gerador):
    selecionada = fase
    empresa = "padrão"
    if fase.empresa_a_prob is not None:
        if gerador.bernoulli(fase.empresa_a_prob):
            empresa = "A"
        else:
            selecionada = fase.alternativa_b
            empresa = "B"

    if fase.duracao_bom is not None:
        chuva = gerador.bernoulli(fase.prob_chuva) == 1
        if empresa == "A":
            dur_params = fase.duracao_chuva if chuva else fase.duracao_bom
        else:
            dur_params = (selecionada.duracao_chuva if chuva else selecionada.duracao_bom)
        clima = "chuva" if chuva else "tempo bom"
    else:
        dur_params = selecionada.duracao
        clima = None

    duracao = gerador.pert(dur_params.otimista, dur_params.mais_provavel,
                           dur_params.pessimista)
    material = sortear_custo(gerador, selecionada.material, "lognormal")
    mao_obra = sortear_custo(gerador, selecionada.mao_obra, "normal")
    custo_extra = 0.0
    dias_extra = 0.0
    eventos = []

    if fase.evento_geo_prob > 0 and gerador.bernoulli(fase.evento_geo_prob):
        custo_extra += fase.evento_geo_custo
        dias_extra += fase.evento_geo_dias
        eventos.append("evento geológico")

    if fase.retrabalho_prob > 0 and gerador.bernoulli(fase.retrabalho_prob):
        custo_extra += fase.retrabalho_custo
        dias_extra += fase.retrabalho_dias
        eventos.append("retrabalho")

    return {
        "fase": selecionada.nome,
        "empresa": empresa,
        "clima": clima,
        "duracao": duracao + dias_extra,
        "material": material,
        "mao_obra": mao_obra,
        "custo_extra": custo_extra,
        "custo": material + mao_obra + custo_extra,
        "dias_extra": dias_extra,
        "eventos": eventos,
    }


def simular_uma_obra(cenario, gerador, guardar_detalhes=True):
    detalhes = [simular_fase(fase, gerador) for fase in cenario.fases]
    duracao_total = sum(item["duracao"] for item in detalhes)
    custo_sem_multa = sum(item["custo"] for item in detalhes)
    atraso = max(0.0, duracao_total - cenario.prazo_contrato)
    multa = atraso * cenario.multa_por_dia
    custo_total = custo_sem_multa + multa
    return ResultadoRodada(
        duracao_total=duracao_total,
        custo_sem_multa=custo_sem_multa,
        multa=multa,
        custo_total=custo_total,
        lucro=cenario.preco_contrato - custo_total,
        detalhamento=detalhes if guardar_detalhes else [],
    )


def executar_simulacao(cenario, n, seed):
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError("O número de rodadas deve ser um inteiro positivo.")
    gerador = GeradorAleatorio(seed)
    # O detalhamento continua disponível para estudar uma obra isolada.
    # Nas replicações, guardar só os totais evita centenas de milhares de dicionários.
    rodadas = [simular_uma_obra(cenario, gerador, guardar_detalhes=False) for _ in range(n)]

    prejuizos = sum(r.custo_total > cenario.preco_contrato for r in rodadas)
    atrasadas = [r for r in rodadas if r.duracao_total > cenario.prazo_contrato]
    custos = [r.custo_total for r in rodadas]
    duracoes = [r.duracao_total for r in rodadas]
    multas = [r.multa for r in atrasadas]

    prob_prejuizo = prejuizos / n
    multa_media_atraso = sum(multas) / len(multas) if multas else None
    media_custo = sum(custos) / n
    media_duracao = sum(duracoes) / n
    taxa_atraso = len(atrasadas) / n
    lucro_medio = sum(r.lucro for r in rodadas) / n

    atende_prejuizo = prob_prejuizo < cenario.limite_prejuizo
    if cenario.limite_multa_media is None:
        atende_multa = None
        viavel = atende_prejuizo
    elif multa_media_atraso is None:
        # Não comparar None com dinheiro nem inventar uma média condicional zero.
        atende_multa = None
        viavel = None if atende_prejuizo else False
    else:
        comparacao_multa = (multa_media_atraso <= cenario.limite_multa_media
                            if cenario.multa_limite_inclusivo else
                            multa_media_atraso < cenario.limite_multa_media)
        atende_multa = (multa_media_atraso is not None and comparacao_multa)
        viavel = atende_prejuizo and atende_multa

    resumo = {
        "cenario": cenario.nome,
        "n": n,
        "semente": seed,
        "preco_contrato": cenario.preco_contrato,
        "prazo_contrato_dias": cenario.prazo_contrato,
        "probabilidade_prejuizo": prob_prejuizo,
        "probabilidade_prejuizo_pct": 100 * prob_prejuizo,
        "probabilidade_atraso_pct": 100 * taxa_atraso,
        "multa_media_condicional_atraso": multa_media_atraso,
        "custo_medio_total": media_custo,
        "duracao_media_dias": media_duracao,
        "lucro_medio": lucro_medio,
        "custo_medio_sem_multa": sum(r.custo_sem_multa for r in rodadas) / n,
        "multa_media_geral": sum(r.multa for r in rodadas) / n,
        "rodadas_com_prejuizo": prejuizos,
        "rodadas_com_atraso": len(atrasadas),
        "limite_prejuizo_pct": 100 * cenario.limite_prejuizo,
        "limite_multa_media": cenario.limite_multa_media,
        "atende_criterio_prejuizo": atende_prejuizo,
        "atende_criterio_multa": atende_multa,
        "recomendacao": ("INCONCLUSIVO" if viavel is None else
                         "ACEITAR" if viavel else "RECUSAR"),
        "custos": custos,
        "duracoes": duracoes,
        "multas_atrasos": multas,
        "rodadas": rodadas,
    }
    return resumo
