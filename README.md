# Simulação de Monte Carlo — Viabilidade de obras

Implementação modular do trabalho prático de Introdução à Simulação.

## Requisitos

- Python 3.10 ou superior
- `matplotlib` para gráficos (`pip install -r requirements.txt`)
- Não são usadas bibliotecas prontas para gerar Normal, LogNormal, PERT ou Bernoulli.
  O módulo `random` é usado apenas como fonte de números pseudoaleatórios uniformes.

## Executar

Na pasta do projeto:

```bash
python main.py
```

Os resultados são gravados em `resultados/resumo_cenarios.csv` e os gráficos em
`resultados/graficos/`.

## Organização

- A seed utilizada é 42
- É executada 100.000 simulações

- `monte_carlo/geradores.py`: Bernoulli, Normal (Box–Muller), LogNormal e PERT.
- `monte_carlo/modelos.py`: estruturas dos parâmetros dos cenários e resultados.
- `monte_carlo/cenarios.py`: dados dos três cenários.
- `monte_carlo/simulacao.py`: fase, obra completa, replicações e métricas.
- `monte_carlo/relatorios.py`: resumo no terminal e histogramas.
- `main.py`: execução dos três cenários.

## Hipóteses e observações importantes

1. **Parâmetros LogNormal:** o documento apresenta a LogNormal como `LogNormal(µ_ln, σ_ln)`
   na tabela de notação, mas as tabelas dos cenários mostram valores monetários típicos de
   média e desvio-padrão na escala original. Esta implementação assume que os valores das
   tabelas são média e desvio-padrão monetários e os converte para os parâmetros logarítmicos:
   `sigma_ln² = ln(1 + (desvio/media)²)` e `mu_ln = ln(media) - sigma_ln²/2`.

2. **Normal para custos:** os custos de mão de obra são sorteados da Normal.
   A distribuição Normal não é limitada a valores positivos. Os parâmetros apresentados tornam
   valores negativos muito improváveis, mas o código não os trunca para preservar a distribuição
   especificada. Se o professor exigir custo sempre positivo, a regra deve ser acordada e documentada.

3. **PERT:** usada a PERT clássica com `lambda=4`, baseada em uma Beta escalada ao intervalo
   otimista/pessimista. A média resultante é `(o + 4m + p)/6`.

4. **Multa média:** é a média das multas apenas nas rodadas com atraso.
   Se nenhuma rodada atrasar, o resultado aparece como não definido.

5. **Viabilidade:** cenários 1 e 3 exigem limite de prejuízo e limite de multa média. O cenário 2
   só define limite de probabilidade de prejuízo; por isso, a decisão usa apenas esse critério.
   O cenário 1 usa comparação estrita `<`, pois o documento diz “inferior a”; o cenário 3 usa `<=`, pois diz “não exceder”.

6. **Pintura:** a probabilidade de escolha da empresa A e a probabilidade de chuva são sorteadas
   independentemente, conforme a descrição do pseudocódigo. A chuva muda apenas a duração.

7. A soma dos tempos das fases é feita sequencialmente, conforme o modelo do documento.
