# Revisão do repositório — 19/10/2026

Base revisada: commit `f68538d`. A organização original foi preservada: `main.py`,
`geradores.py`, `modelos.py`, `cenarios.py`, `simulacao.py` e `relatorios.py`.
As três tabelas de parâmetros e as estruturas de dados estavam corretas e não
precisaram de alteração. Também foram mantidos Box–Muller, a conversão Lognormal,
Marsaglia–Tsang, a soma sequencial das fases e os eventos de risco.

## Correções

1. **Beta e PERT:** a expressão original fazia três sorteios Gamma:
   `gamma(alpha) / (gamma(alpha) + gamma(beta))`. O numerador não era reutilizado.
   Em uma reprodução com semente 42, 1.104 de 10.000 valores de PERT(10,14,20)
   ultrapassaram 20; o máximo chegou a 79,88. Agora sorteia X e Y uma vez e usa
   `X/(X+Y)`, respeitando os limites e momentos da distribuição.
2. **Uniforme próprio:** substituído `random.Random` pelo LCG apresentado na aula,
   para implementar todos os sorteios. O intervalo aberto (0,1) evita `log(0)`.
   O comentário original afirmava evitar zero, mas `random()` podia retorná-lo.
3. **Nenhum atraso:** a comparação de `None` com o limite monetário causava
   `TypeError`. Agora a média permanece não definida. Se necessária para aceitar,
   o resultado fica inconclusivo; uma falha no critério de prejuízo já permite recusar.
4. **Saídas faltantes:** implementados CSV comparativo, JSON e CSVs de todas as rodadas.
   O README prometia um CSV que o programa não gravava. Os caminhos agora são
   relativos ao repositório, não à pasta de onde se abre o terminal.
5. **Uso de memória:** as replicações guardam os totais; o detalhamento das seis
   fases continua disponível ao chamar `simular_uma_obra` isoladamente.
6. **Relatórios e validações:** corrigido o nome da fase quando a empresa B é sorteada,
   importação convencional de `math`, rejeição de N/sementes inválidos e desvio negativo.
   Matplotlib passou a ser opcional e serve apenas aos gráficos.

## Verificação

- Dez testes automatizados passaram. Eles incluem limites e momentos de todas as
  combinações PERT das tabelas, a reutilização exata de X na Beta e ramos do modelo.
- Foram executadas 100.000 obras por cenário, com sementes 42, 43 e 44.
- As 300.000 linhas de resultados, contagens de prejuízo, histogramas e identidades
  de custo/multa foram conferidas.
- Médias teóricas de duração: 364,14; 91,05; 273,67 dias. Observadas: 364,17; 91,05;
  273,61 dias. Custos médios sem multa também ficaram compatíveis com a teoria.
- Intervalos aproximados de 95% para prejuízo: 8,00%–8,34%; 78,24%–78,75%;
  28,47%–29,03%. Todos ficam afastados dos limites de aceitação.

As decisões continuam: aceitar o edifício; recusar galpão e centro de saúde nas
condições atuais. Os números e gráficos dos materiais do Google foram atualizados
para corresponder a este repositório. A explicação da PERT agora acompanha o
método Gamma/Beta preservado do colega. O código anterior fora deste repositório,
seus resultados e cache foram retirados da pasta do trabalho a pedido do grupo,
com uma cópia de recuperação fora do projeto. Este repositório é a
única versão para execução e entrega; o ponto de entrada é `main.py`.

Não foram alterados os contratos nem as probabilidades para favorecer decisões.
A interpretação monetária dos parâmetros da Lognormal continua explícita no README
e no guia, devido à inconsistência de notação do enunciado.
