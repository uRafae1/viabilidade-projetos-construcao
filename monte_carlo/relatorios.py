"""Tabelas de resumo e gráficos."""
from pathlib import Path
import csv
import json
import math
import statistics


def histograma(valores, largura):
    """Classes de mesma largura; cada frequência é contagem / N."""
    inicio = math.floor(min(valores) / largura) * largura
    contagens = [0] * (math.floor((max(valores) - inicio) / largura) + 1)
    for valor in valores:
        contagens[int((valor - inicio) / largura)] += 1
    return {"inicio": inicio, "largura": largura, "contagens": contagens,
            "frequencias": [q / len(valores) for q in contagens]}


def estatisticas(valores):
    ordenados = sorted(valores)
    return {"media": statistics.mean(valores), "mediana": statistics.median(valores),
            "minimo": ordenados[0], "maximo": ordenados[-1],
            "desvio_padrao": statistics.stdev(valores) if len(valores) > 1 else None,
            "p90": ordenados[math.ceil(0.90 * len(valores)) - 1]}


def salvar_resultados(resultados, pasta="resultados"):
    """Salva a tabela comparativa, os dados completos e as frequências dos slides."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    resumos = []
    vetores = {"custos", "duracoes", "multas_atrasos", "rodadas"}
    for numero, resultado in enumerate(resultados, start=1):
        resumo = {k: v for k, v in resultado.items() if k not in vetores}
        resumo["custo"] = estatisticas(resultado["custos"])
        resumo["duracao"] = estatisticas(resultado["duracoes"])
        resumo["hist_custo"] = histograma(resultado["custos"], [1_000_000, 400_000, 1_000_000][numero-1])
        resumo["hist_duracao"] = histograma(resultado["duracoes"], [20, 10, 20][numero-1])
        resumos.append(resumo)
        with (pasta / f"rodadas_cenario_{numero}.csv").open("w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f, delimiter=";")
            escritor.writerow(["rodada", "duracao_dias", "custo_sem_multa_reais", "multa_reais",
                               "custo_total_reais", "lucro_reais", "prejuizo"])
            for i, rodada in enumerate(resultado["rodadas"], start=1):
                escritor.writerow([i, f"{rodada.duracao_total:.6f}", f"{rodada.custo_sem_multa:.2f}",
                                   f"{rodada.multa:.2f}", f"{rodada.custo_total:.2f}",
                                   f"{rodada.lucro:.2f}", int(rodada.lucro < 0)])
    (pasta / "resumo.json").write_text(json.dumps(resumos, ensure_ascii=False, indent=2), encoding="utf-8")
    with (pasta / "resumo_cenarios.csv").open("w", newline="", encoding="utf-8-sig") as f:
        campos = [k for k, v in resumos[0].items() if not isinstance(v, dict)]
        escritor = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore", delimiter=";")
        escritor.writeheader()
        escritor.writerows(resumos)

def salvar_graficos(resultado, pasta="resultados"):
    # Importação local: é possível simular e gerar tabelas sem Matplotlib.
    import matplotlib.pyplot as plt

    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    nome = resultado["cenario"].split("—")[0].strip().replace(" ", "_").lower()

    plt.figure()
    plt.hist([v / 1_000_000 for v in resultado["custos"]], bins=50, color="#006466")
    plt.axvline(resultado["preco_contrato"] / 1_000_000, linestyle="--", color="#9B4C32",
                label="Preço do contrato")
    plt.xlabel("Custo total, incluindo multa (R$ milhões)")
    plt.ylabel("Número de obras")
    plt.title(f"Distribuição do custo — {resultado['cenario']}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(pasta / f"{nome}_custos.png", dpi=150)
    plt.close()

    plt.figure()
    plt.hist(resultado["duracoes"], bins=50, color="#006466")
    plt.axvline(resultado["prazo_contrato_dias"], linestyle="--", color="#9B4C32",
                label="Prazo contratual")
    plt.xlabel("Duração total (dias)")
    plt.ylabel("Número de obras")
    plt.title(f"Distribuição da duração — {resultado['cenario']}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(pasta / f"{nome}_duracoes.png", dpi=150)
    plt.close()


def imprimir_resumo(resultado):
    def moeda(valor):
        if valor is None:
            return "não definido"
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    print("\n" + "=" * 72)
    print(resultado["cenario"])
    print("=" * 72)
    print(f"Rodadas: {resultado['n']:,}".replace(",", "."))
    print(f"Preço do contrato: {moeda(resultado['preco_contrato'])}")
    print(f"Prazo contratual: {resultado['prazo_contrato_dias']:.1f} dias")
    print(f"Probabilidade de prejuízo: {resultado['probabilidade_prejuizo_pct']:.2f}% "
          f"(limite: {resultado['limite_prejuizo_pct']:.2f}%)")
    print(f"Probabilidade de atraso: {resultado['probabilidade_atraso_pct']:.2f}%")
    print(f"Multa média, apenas nas rodadas atrasadas: "
          f"{moeda(resultado['multa_media_condicional_atraso'])}")
    if resultado["limite_multa_media"] is not None:
        print(f"Limite de multa média: {moeda(resultado['limite_multa_media'])}")
    print(f"Custo total médio: {moeda(resultado['custo_medio_total'])}")
    print(f"Duração média: {resultado['duracao_media_dias']:.2f} dias")
    print(f"Lucro médio: {moeda(resultado['lucro_medio'])}")
    print(f"Recomendação: {resultado['recomendacao']}")
