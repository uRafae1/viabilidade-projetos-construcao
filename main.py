
"""Execute python main.py. IA auxiliou a revisão e os materiais do grupo."""
from pathlib import Path
from monte_carlo.cenarios import cenario_1, cenario_2, cenario_3
from monte_carlo.simulacao import executar_simulacao
from monte_carlo.relatorios import imprimir_resumo, salvar_graficos, salvar_resultados

N = 100_000
SEMENTE = 42
PASTA_RESULTADOS = Path(__file__).resolve().parent / "resultados"


def main():
    cenarios = [cenario_1(), cenario_2(), cenario_3()]
    resultados = []
    for indice, cenario in enumerate(cenarios):
        resultado = executar_simulacao(cenario, N, SEMENTE + indice)
        resultados.append(resultado)
        imprimir_resumo(resultado)
    salvar_resultados(resultados, PASTA_RESULTADOS)
    try:
        for resultado in resultados:
            salvar_graficos(resultado, PASTA_RESULTADOS)
    except ModuleNotFoundError as erro:
        if erro.name != "matplotlib":
            raise
        print("\nResultados salvos. Para os PNGs, instale: python -m pip install -r requirements.txt")
        print("Depois execute python main.py novamente (as sementes reproduzem os resultados).")


if __name__ == "__main__":
    main()
