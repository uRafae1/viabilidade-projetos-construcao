"""Verificações do modelo e dos erros corrigidos. Executar: python -m unittest discover -s tests -v"""
import csv
import json
import math
import statistics
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from monte_carlo.cenarios import cenario_1, cenario_2, cenario_3
from monte_carlo.geradores import GeradorAleatorio
from monte_carlo.modelos import ParametrosCusto, ResultadoRodada
from monte_carlo.relatorios import salvar_resultados
from monte_carlo.simulacao import executar_simulacao, simular_fase, simular_uma_obra, sortear_custo


class TestGeradores(unittest.TestCase):
    def conferir_momentos(self, valores, media, variancia):
        self.assertLess(abs(statistics.mean(valores) - media), 6 * math.sqrt(variancia / len(valores)))
        self.assertLess(abs(statistics.variance(valores) / variancia - 1), 0.08)

    def test_uniforme_sequencia_e_limites(self):
        g = GeradorAleatorio(1)
        self.assertEqual([round(g.uniforme() * 2147483647) for _ in range(3)],
                         [16807, 282475249, 1622650073])
        self.assertTrue(all(0 < g.uniforme() < 1 for _ in range(10000)))
        for seed in [0, -1, 2147483647, 1.5, True]:
            with self.assertRaises(ValueError):
                GeradorAleatorio(seed)

    def test_beta_reutiliza_o_mesmo_sorteio(self):
        g = GeradorAleatorio(42)
        with patch.object(g, '_gamma', side_effect=[2.0, 3.0]) as gamma:
            self.assertEqual(g.beta(2, 3), 0.4)
            self.assertEqual(gamma.call_count, 2)

    def test_gamma_beta_normal_lognormal_bernoulli(self):
        g = GeradorAleatorio(42)
        for shape in [0.5, 1, 3]:
            with self.subTest(gamma=shape):
                self.conferir_momentos([g._gamma(shape) for _ in range(30000)], shape, shape)
        beta = [g.beta(2, 3) for _ in range(30000)]
        self.assertTrue(all(0 <= v <= 1 for v in beta))
        self.conferir_momentos(beta, 2/5, 2*3/(5*5*6))
        self.conferir_momentos([g.normal(5, 2) for _ in range(30000)], 5, 4)
        valores = [sortear_custo(g, ParametrosCusto(120000, 30000), 'lognormal') for _ in range(30000)]
        self.assertTrue(all(v > 0 for v in valores))
        self.conferir_momentos(valores, 120000, 30000**2)
        self.conferir_momentos([g.bernoulli(.18) for _ in range(30000)], .18, .18*.82)
        self.assertEqual(g.bernoulli(0), 0)
        self.assertEqual(g.bernoulli(1), 1)
        with self.assertRaises(ValueError):
            sortear_custo(g, ParametrosCusto(100, -2), 'lognormal')

    def test_todas_as_pert_das_tabelas(self):
        parametros = set()
        for c in [cenario_1(), cenario_2(), cenario_3()]:
            for fase in c.fases:
                for f in [fase, fase.alternativa_b]:
                    if f is not None:
                        for d in [f.duracao, f.duracao_bom, f.duracao_chuva]:
                            if d is not None:
                                parametros.add((d.otimista, d.mais_provavel, d.pessimista))
        for a, m, b in sorted(parametros):
            with self.subTest(pert=(a, m, b)):
                g = GeradorAleatorio(42)
                valores = [g.pert(a, m, b) for _ in range(10000)]
                self.assertTrue(all(a <= v <= b for v in valores))
                alfa, beta = 1+4*(m-a)/(b-a), 1+4*(b-m)/(b-a)
                variancia = (b-a)**2*alfa*beta/((alfa+beta)**2*(alfa+beta+1))
                self.conferir_momentos(valores, (a+4*m+b)/6, variancia)
        self.assertEqual(GeradorAleatorio(42).pert(3, 3, 3), 3)


class GeradorControlado:
    """Respostas fixas para testar cada ramo sem depender da sorte."""
    def __init__(self, eventos):
        self.eventos = iter(eventos)

    def bernoulli(self, p):
        return next(self.eventos)

    def pert(self, o, m, p):
        return (o + 4*m + p)/6

    def normal(self, media, desvio):
        return media

    def lognormal(self, mu, sigma):
        return math.exp(mu + sigma*sigma/2)


class TestModelo(unittest.TestCase):
    def test_fundacao_b_com_geologia(self):
        f = simular_fase(cenario_1().fases[1], GeradorControlado([0, 1]))
        self.assertEqual(f['empresa'], 'B')
        self.assertIn('(B)', f['fase'])
        self.assertAlmostEqual(f['duracao'], (25+4*34+48)/6+25)
        self.assertAlmostEqual(f['custo'], 3000000+2100000+700000)

    def test_chuva_so_altera_duracao_e_retrabalho_soma_uma_vez(self):
        fase = cenario_1().fases[5]
        bom = simular_fase(fase, GeradorControlado([0, 0]))
        chuva = simular_fase(fase, GeradorControlado([0, 1]))
        self.assertEqual(chuva['custo'], bom['custo'])
        self.assertAlmostEqual(chuva['duracao'], (14+4*18+24)/6)
        alvenaria = cenario_1().fases[3]
        normal = simular_fase(alvenaria, GeradorControlado([0]))
        retrabalho = simular_fase(alvenaria, GeradorControlado([1]))
        self.assertAlmostEqual(retrabalho['custo']-normal['custo'], 300000)
        self.assertAlmostEqual(retrabalho['duracao']-normal['duracao'], 12)

    def test_soma_fases_e_multa_fracionaria(self):
        c = replace(cenario_1(), prazo_contrato=0)
        r = simular_uma_obra(c, GeradorAleatorio(42))
        self.assertEqual(len(r.detalhamento), 6)
        self.assertAlmostEqual(r.duracao_total, sum(f['duracao'] for f in r.detalhamento))
        self.assertAlmostEqual(r.custo_total, r.custo_sem_multa+r.multa)
        self.assertAlmostEqual(r.multa, r.duracao_total*c.multa_por_dia)

    def test_condicional_e_limites_de_decisao(self):
        c = replace(cenario_1(), preco_contrato=1000, prazo_contrato=10,
                    limite_prejuizo=.25, limite_multa_media=20)
        rodadas = [ResultadoRodada(12, 990, 20, 1010, -10)]
        rodadas += [ResultadoRodada(8, 900, 0, 900, 100)] * 3
        with patch('monte_carlo.simulacao.simular_uma_obra', side_effect=rodadas):
            r = executar_simulacao(c, 4, 42)
        self.assertEqual(r['multa_media_condicional_atraso'], 20)
        self.assertEqual(r['multa_media_geral'], 5)
        self.assertFalse(r['atende_criterio_prejuizo'])  # Igual ao limite não passa.
        self.assertFalse(r['atende_criterio_multa'])
        c = replace(c, limite_prejuizo=.30, multa_limite_inclusivo=True)
        with patch('monte_carlo.simulacao.simular_uma_obra', side_effect=rodadas):
            self.assertEqual(executar_simulacao(c, 4, 42)['recomendacao'], 'ACEITAR')

    def test_sem_atrasos_e_n_invalido(self):
        c = replace(cenario_1(), prazo_contrato=100000, preco_contrato=1e12)
        r = executar_simulacao(c, 5, 42)
        self.assertIsNone(r['multa_media_condicional_atraso'])
        self.assertIsNone(r['atende_criterio_multa'])
        self.assertEqual(r['recomendacao'], 'INCONCLUSIVO')
        for n in [0, -1, 2.5, True]:
            with self.assertRaises(ValueError):
                executar_simulacao(c, n, 42)

    def test_reprodutibilidade_galpao_e_exportacao(self):
        c = cenario_2()
        r = executar_simulacao(c, 1000, 43)
        self.assertEqual(r['custos'], executar_simulacao(c, 1000, 43)['custos'])
        self.assertTrue(all(v <= 140 for v in r['duracoes']))
        self.assertEqual(r['rodadas_com_atraso'], 0)
        self.assertIsNone(r['atende_criterio_multa'])
        resultados = [executar_simulacao(c, 20, 42+i) for i, c in
                      enumerate([cenario_1(), cenario_2(), cenario_3()])]
        with tempfile.TemporaryDirectory() as tmp:
            salvar_resultados(resultados, tmp)
            dados = json.loads((Path(tmp)/'resumo.json').read_text(encoding='utf-8'))
            self.assertEqual(len(dados), 3)
            for i, d in enumerate(dados, 1):
                self.assertEqual(sum(d['hist_custo']['contagens']), 20)
                self.assertAlmostEqual(sum(d['hist_duracao']['frequencias']), 1)
                with (Path(tmp)/f'rodadas_cenario_{i}.csv').open(encoding='utf-8') as f:
                    self.assertEqual(len(list(csv.DictReader(f, delimiter=';'))), 20)


if __name__ == '__main__':
    unittest.main()
