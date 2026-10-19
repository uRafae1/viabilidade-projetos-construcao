# Simulação de Monte Carlo — Viabilidade de obras

Implementação modular do trabalho prático de Introdução à Simulação.

Grupo: Kauan, Lucas e Rafael. Esta é a versão oficial usada nos slides e documentos.
Mantém a estrutura do repositório original, com correções registradas em [REVISAO.md](REVISAO.md).

## Requisitos

- Python 3.10 ou superior
- `matplotlib` para gráficos (`pip install -r requirements.txt`)
- Nenhum sorteio usa bibliotecas prontas, inclusive o uniforme, implementado pelo
  congruencial linear da aula. Normal, LogNormal, PERT e Bernoulli são geradas no código.
- Matplotlib é opcional: sem ele, a simulação e as tabelas funcionam normalmente.

## Executar

Na pasta do projeto:

```bash
python main.py
```

Os resultados são gravados em `resultados/`, dentro deste repositório, mesmo quando
o programa é chamado de outra pasta. Para gerar também as imagens:

```bash
python -m pip install -r requirements.txt
python main.py
```

- `resumo_cenarios.csv`: tabela comparativa dos três cenários.
- `resumo.json`: métricas, estatísticas e frequências usadas nos slides.
- `rodadas_cenario_1.csv`, `rodadas_cenario_2.csv` e `rodadas_cenario_3.csv`: todas as obras simuladas.
- `cenário_1_custos.png` e arquivos equivalentes: seis gráficos, de custo e duração.

Os CSVs usam ponto e vírgula entre colunas e ponto decimal. Os cálculos de decisão
usam os valores antes do arredondamento da exportação. Os PNGs mostram contagens
com 50 classes; os slides agrupam faixas mais largas e mostram percentuais, sobre
as mesmas amostras, sem excluir extremos.

## Organização

- Sementes: 42, 43 e 44, respectivamente, nos cenários 1, 2 e 3.
- São executadas 100.000 simulações por cenário. Constantes em `main.py`.

- `monte_carlo/geradores.py`: Bernoulli, Normal (Box–Muller), LogNormal e PERT.
- `monte_carlo/modelos.py`: estruturas dos parâmetros dos cenários e resultados.
- `monte_carlo/cenarios.py`: dados dos três cenários.
- `monte_carlo/simulacao.py`: fase, obra completa, replicações e métricas.
- `monte_carlo/relatorios.py`: resumo no terminal e histogramas.
- `main.py`: execução dos três cenários.
- `tests/test_simulacao.py`: verificações automatizadas, separadas do código usado na apresentação.

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
   A Beta é `X/(X+Y)`, com duas Gammas independentes de escala 1; o MESMO `X`
   é reutilizado no numerador e denominador. A Gamma usa Marsaglia–Tsang.

4. **Multa média:** é a média das multas apenas nas rodadas com atraso.
   Se nenhuma rodada atrasar, o resultado aparece como não definido.
   Se um cenário exigir essa média e o critério de prejuízo passar, a recomendação
   fica `INCONCLUSIVO`: a ausência de atrasos na amostra não estima a média condicional.
   No galpão não existe esse critério adicional; o prazo máximo teórico é 140 dias,
   abaixo dos 150 contratados, portanto não há atrasos possíveis nesse cenário.

5. **Viabilidade:** cenários 1 e 3 exigem limite de prejuízo e limite de multa média. O cenário 2
   só define limite de probabilidade de prejuízo; por isso, a decisão usa apenas esse critério.
   O cenário 1 usa comparação estrita `<`, pois o documento diz “inferior a”; o cenário 3 usa `<=`, pois diz “não exceder”.

6. **Pintura:** a probabilidade de escolha da empresa A e a probabilidade de chuva são sorteadas
   independentemente, conforme a descrição do pseudocódigo. A chuva muda apenas a duração.

7. A soma dos tempos das fases é feita sequencialmente, conforme o modelo do documento.

## Resultados da versão revisada

| Cenário | Prejuízo | Atraso | Multa média nos atrasos | Decisão |
|---|---:|---:|---:|---|
| Edifício | 8,17% | 56,21% | R$ 57.243,44 | Aceitar |
| Galpão | 78,50% | 0,00% | Não aplicável | Recusar |
| Centro de saúde | 28,75% | 11,20% | R$ 43.436,83 | Recusar |

O centro de saúde tem lucro médio positivo, mas ultrapassa o limite de risco de 15%.
Sugestões de renegociação exigem alterar os parâmetros e simular novamente;
não representam propostas já testadas.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os 10 testes abrangem o erro da Beta, os momentos e limites das distribuições,
eventos de risco, chuva, empresa B, multa condicional, comparações estritas/inclusivas,
ausência de atrasos, repetibilidade e exportação. Usam apenas a biblioteca padrão.

## Materiais no Google

- [Slides](https://docs.google.com/presentation/d/1C9Y0OFVGnEx8enBsdGLJukjvZ2Z77Iuu3F96wbf5nCY/edit)
- [Guia de estudo e relatório](https://docs.google.com/document/d/1n7JcC_eQyf-30hSLjQAYlK0haUhCeDrzscboMqwBgVs/edit)
- [Roteiro e perguntas](https://docs.google.com/document/d/12e43ZgYh-PN6hHzfrqhRkOMAbuk-GAWnGjzNBi3fTHw/edit)
- [Dados dos gráficos](https://docs.google.com/spreadsheets/d/1EevpbR_zFSSsT6h_epegPRV2TNsPD_BRBjw_PrXcll4/edit)

## Fontes

- Enunciado: `../pratico-simulacao-monte-carlo-errata-2026.pdf`, seções 2–6 e Tabelas 2–4.
- Slides da aula: `../../Slides/is-fundamentos.pdf`, LCG e aceitação-rejeição.
- [Box e Muller (1958)](https://doi.org/10.1214/aoms/1177706645).
- [NIST: Lognormal](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3669.htm).
- [Beta-PERT](https://www.riskamp.com/beta-pert/).
- [Art Owen, seção 4.8, algoritmo de Marsaglia–Tsang](https://artowen.su.domains/mc/Ch-nonunifrng.pdf).

Declaração de IA: ChatGPT/Codex auxiliou a revisão do código, os testes, a análise e
a preparação dos materiais. Os resultados foram obtidos executando o programa.
