"""Tabelas de resumo e gráficos."""
from pathlib import Path
import matplotlib.pyplot as plt

def salvar_graficos(resultado, pasta="resultados"):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    nome = resultado["cenario"].split("—")[0].strip().replace(" ", "_").lower()

    plt.figure()
    plt.hist(resultado["custos"], bins=50)
    plt.axvline(resultado["preco_contrato"], linestyle="--",
                label="Preço do contrato")
    plt.xlabel("Custo total (R$)")
    plt.ylabel("Frequência")
    plt.title(f"Distribuição do custo — {resultado['cenario']}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(pasta / f"{nome}_custos.png", dpi=150)
    plt.close()

    plt.figure()
    plt.hist(resultado["duracoes"], bins=50)
    plt.axvline(resultado["prazo_contrato_dias"], linestyle="--",
                label="Prazo contratual")
    plt.xlabel("Duração total (dias)")
    plt.ylabel("Frequência")
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
