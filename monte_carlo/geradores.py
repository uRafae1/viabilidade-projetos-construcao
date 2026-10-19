"""Geradores de variáveis aleatórias sem bibliotecas de distribuições prontas.

Uniforme: congruencial linear da aula, sem usar `random`.
Normal: Box-Muller. LogNormal: transformação da Normal. PERT: Beta por
razão de Gammas (Marsaglia-Tsang), com parâmetros clássicos da PERT.
"""
import math


class GeradorAleatorio:
    def __init__(self, seed=42):
        if not isinstance(seed, int) or isinstance(seed, bool) or not 0 < seed < 2147483647:
            raise ValueError("A semente deve ser um inteiro entre 1 e 2147483646.")
        self.estado = seed

    def uniforme(self):
        # Nunca retorna 0 ou 1: evita log(0) no Box-Muller e na Gamma.
        self.estado = (16807 * self.estado) % 2147483647
        return self.estado / 2147483647

    def bernoulli(self, p):
        if not 0 <= p <= 1:
            raise ValueError(f"Probabilidade inválida: {p}")
        return 1 if self.uniforme() < p else 0

    def normal_padrao(self):
        u1 = self.uniforme()
        u2 = self.uniforme()
        return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

    def normal(self, media, desvio):
        if desvio < 0:
            raise ValueError("O desvio padrão não pode ser negativo.")
        if desvio == 0:
            return float(media)
        # Um custo Normal pode ocasionalmente ser negativo. Mantemos a
        # distribuição especificada pelo enunciado e sinalizamos isso na análise.
        return media + desvio * self.normal_padrao()

    def lognormal(self, mu_ln, sigma_ln):
        if sigma_ln < 0:
            raise ValueError("O sigma da LogNormal não pode ser negativo.")
        if sigma_ln == 0:
            return math.exp(mu_ln)
        return math.exp(mu_ln + sigma_ln * self.normal_padrao())

    def beta(self, alpha, beta):
        """Amostra Beta(alpha,beta) via relação Gamma, usando Marsaglia-Tsang."""
        if alpha <= 0 or beta <= 0:
            raise ValueError("Parâmetros da Beta devem ser positivos.")
        x = self._gamma(alpha)
        y = self._gamma(beta)
        # O MESMO x precisa aparecer no numerador e no denominador.
        return x / (x + y)

    def _gamma(self, shape):
        """Amostragem Gamma para shape > 0, método Marsaglia-Tsang."""
        if shape < 1:
            # Identidade: Gamma(a) = Gamma(a+1) * U^(1/a)
            return self._gamma(shape + 1) * (self.uniforme() ** (1.0 / shape))
        d = shape - 1.0 / 3.0
        c = 1.0 / math.sqrt(9.0 * d)
        while True:
            x = self.normal_padrao()
            v = 1.0 + c * x
            if v <= 0:
                continue
            v = v ** 3
            u = self.uniforme()
            if u < 1.0 - 0.0331 * (x ** 4):
                return d * v
            if math.log(u) < 0.5 * x * x + d * (1.0 - v + math.log(v)):
                return d * v

    def pert(self, otimista, mais_provavel, pessimista, lamb=4.0):
        """PERT clássica: Beta(alpha,beta) escalada para [otimista,pessimista]."""
        o, m, p = otimista, mais_provavel, pessimista
        if not math.isfinite(lamb) or lamb < 0:
            raise ValueError("O peso da PERT deve ser finito e não negativo.")
        if not (o <= m <= p):
            raise ValueError(f"PERT exige otimista <= moda <= pessimista: {(o,m,p)}")
        if o == p:
            return float(o)
        amplitude = p - o
        alpha = 1.0 + lamb * (m - o) / amplitude
        beta = 1.0 + lamb * (p - m) / amplitude
        return o + amplitude * self.beta(alpha, beta)
