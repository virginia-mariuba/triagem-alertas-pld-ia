"""Classificação de base por regras simples (sem IA).

Serve de comparação: mostra o que um filtro fixo consegue e onde a IA
ajuda a entender texto livre e contexto.
"""

PADROES_GRAVES = ["fracionamento", "jurisdição de atenção", "passagem de recursos"]
SEM_JUSTIFICATIVA = [
    "sem comprovação", "sem justificativa", "não apresentou",
    "não respondeu", "sem detalhes",
]
DOCUMENTACAO = [
    "contrato", "nota fiscal", "notas fiscais", "folha",
    "mesma titularidade", "boleto",
]


def pontuar(alerta):
    """Devolve (risco, motivo) para um alerta (dict)."""
    pontos = 0
    motivos = []

    valor = float(alerta["valor"])
    renda = float(alerta["renda_mensal"]) or 1.0
    razao = valor / renda
    if razao >= 10:
        pontos += 3
        motivos.append(f"valor {razao:.0f}x a renda mensal declarada")
    elif razao >= 4:
        pontos += 1
        motivos.append(f"valor {razao:.1f}x a renda mensal declarada")

    texto = f"{alerta['descricao_alerta']} {alerta['justificativa_cliente']}".lower()
    if any(p in texto for p in PADROES_GRAVES):
        pontos += 3
        motivos.append("padrão típico de risco na descrição")
    if any(p in texto for p in SEM_JUSTIFICATIVA):
        pontos += 2
        motivos.append("justificativa ausente ou sem comprovação")
    if any(p in texto for p in DOCUMENTACAO):
        pontos -= 2
        motivos.append("há documentação de apoio citada")

    if pontos >= 4:
        risco = "alto"
    elif pontos >= 2:
        risco = "medio"
    else:
        risco = "baixo"
    return risco, "; ".join(motivos) or "sem sinais relevantes"
