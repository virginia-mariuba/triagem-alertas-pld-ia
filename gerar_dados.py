"""Gera alertas FICTÍCIOS de PLD para demonstração.

Nenhum dado aqui é real: nomes, valores e situações são inventados para
testar a automação sem expor informação de ninguém.
"""
import argparse
import csv
import os
import random
from datetime import date, timedelta

OCUPACOES = [
    ("Professor(a)", 4500),
    ("Motorista de aplicativo", 3800),
    ("Analista administrativo", 5200),
    ("Autônomo(a) no comércio", 6000),
    ("Estudante", 1500),
    ("Engenheiro(a)", 12000),
    ("Médico(a)", 22000),
    ("Aposentado(a)", 3200),
    ("Dono(a) de pequeno negócio", 15000),
]

# (tipo, descricao_alerta, justificativa_cliente, faixa_de_valor, risco_esperado)
BAIXO = [
    ("Pix", "Pix recebido acima do padrão do mês", "Venda de veículo usado, contrato de compra e venda anexado", (15000, 45000)),
    ("TED", "Crédito de 13º salário e férias", "Pagamento do empregador, constam em folha", (3000, 9000)),
    ("Pix", "Pagamento de aluguel recorrente a terceiro", "Aluguel mensal, contrato de locação anexado", (1200, 3500)),
    ("TED", "Transferência entre contas do próprio cliente", "Movimentação entre contas de mesma titularidade", (2000, 20000)),
    ("Saque", "Saque em espécie acima da média", "Pagamento de reforma residencial, notas fiscais disponíveis", (6000, 12000)),
]
MEDIO = [
    ("Depósito", "Depósitos incomuns para o perfil do cliente", "Venda de produtos em feira, sem comprovação formal", (12000, 28000)),
    ("Pix", "Aumento súbito de movimentação via Pix", "Cliente abriu um pequeno negócio recentemente, aguardando documentação", (20000, 50000)),
    ("Pix", "Recebimentos de várias pessoas sem relação aparente", "Cliente diz organizar um bolão entre amigos", (8000, 20000)),
    ("TED", "Transferência internacional de valor moderado", "Pagamento de curso no exterior, boleto da instituição enviado", (6000, 18000)),
]
ALTO = [
    ("Depósito", "Cinco depósitos em espécie logo abaixo do limite de comunicação em 48 horas, possível fracionamento", "Cliente não apresentou justificativa", (46000, 49500)),
    ("Pix", "Valor recebido muito acima da renda declarada e repassado a terceiros em seguida", "Cliente diz ser empréstimo de um amigo, sem comprovação", (80000, 250000)),
    ("TED", "Transferências para jurisdição de atenção (fictícia) sem relação com o perfil do cliente", "Cliente não respondeu ao contato", (30000, 120000)),
    ("Pix", "Conta recém-aberta recebe vários Pix e saca tudo no mesmo dia, indício de passagem de recursos", "Cliente alega ajuda a familiares, sem detalhes", (25000, 90000)),
]


def gerar(n, semente):
    rng = random.Random(semente)
    linhas = []
    base = date(2026, 3, 1)
    pesos = [("baixo", BAIXO, 0.55), ("medio", MEDIO, 0.25), ("alto", ALTO, 0.20)]
    for i in range(1, n + 1):
        nivel, modelos, _ = rng.choices(pesos, weights=[p[2] for p in pesos])[0]
        tipo, desc, just, (vmin, vmax) = rng.choice(modelos)
        ocupacao, renda_base = rng.choice(OCUPACOES)
        renda = round(renda_base * rng.uniform(0.85, 1.25), -1)
        valor = round(rng.uniform(vmin, vmax), -1)
        linhas.append({
            "id_alerta": f"AL-{i:04d}",
            "data": (base + timedelta(days=rng.randint(0, 200))).isoformat(),
            "tipo_operacao": tipo,
            "valor": f"{valor:.2f}",
            "ocupacao": ocupacao,
            "renda_mensal": f"{renda:.2f}",
            "descricao_alerta": desc,
            "justificativa_cliente": just,
            "risco_esperado": nivel,
        })
    return linhas


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=90, help="quantidade de alertas")
    ap.add_argument("--semente", type=int, default=7, help="semente aleatória (reprodutível)")
    ap.add_argument("--saida", default="data/alertas_sinteticos.csv")
    args = ap.parse_args()

    linhas = gerar(args.n, args.semente)
    os.makedirs(os.path.dirname(args.saida) or ".", exist_ok=True)
    with open(args.saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"{len(linhas)} alertas fictícios gravados em {args.saida}")


if __name__ == "__main__":
    main()
