
from monte_carlo.cenarios import cenario_1, cenario_2, cenario_3
from monte_carlo.simulacao import executar_simulacao
from monte_carlo.relatorios import imprimir_resumo, salvar_graficos


def main():
    # Os cenários são passados como parâmetros para a mesma função de simulação.
    cenarios = [cenario_1(), cenario_2(), cenario_3()]
    for cenario in cenarios:
        resultado = executar_simulacao(cenario, 100_000, 42)
        imprimir_resumo(resultado)
        salvar_graficos(resultado)


if __name__ == "__main__":
    main()
