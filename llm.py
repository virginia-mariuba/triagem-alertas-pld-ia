"""Classificação de alertas com um modelo de linguagem (LLM).

Usa a API da Anthropic por padrão (variável ANTHROPIC_API_KEY).
A função extrair_json não depende de rede e pode ser testada sozinha.
"""
import json
import os
import re
import time
import unicodedata
from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "classificar_alerta.md"
MODELO_PADRAO = os.getenv("MODELO_LLM", "claude-sonnet-5-5")
NIVEIS = {"baixo", "medio", "alto"}
CAMPOS_ENTRADA = [
    "tipo_operacao", "valor", "ocupacao", "renda_mensal",
    "descricao_alerta", "justificativa_cliente",
]  # o rótulo risco_esperado NUNCA é enviado ao modelo


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def extrair_json(texto):
    """Extrai e valida o JSON da resposta do modelo."""
    achado = re.search(r"\{.*\}", texto, re.S)
    if not achado:
        raise ValueError("resposta sem JSON")
    obj = json.loads(achado.group(0))
    risco = _sem_acento(str(obj.get("risco", "")).strip().lower())
    if risco not in NIVEIS:
        raise ValueError(f"risco inválido: {risco!r}")
    return {
        "risco": risco,
        "motivo": str(obj.get("motivo", "")).strip(),
        "acao_sugerida": str(obj.get("acao_sugerida", "")).strip(),
        "confianca": _sem_acento(str(obj.get("confianca", "")).strip().lower()),
    }


def criar_cliente():
    from anthropic import Anthropic  # importado aqui para o resto rodar sem a biblioteca
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("Defina a variável de ambiente ANTHROPIC_API_KEY para usar o modo llm.")
    return Anthropic()


def classificar(alerta, cliente, modelo=MODELO_PADRAO, tentativas=3):
    sistema = PROMPT_PATH.read_text(encoding="utf-8")
    entrada = {k: alerta[k] for k in CAMPOS_ENTRADA}
    ultimo_erro = None
    for t in range(tentativas):
        try:
            resp = cliente.messages.create(
                model=modelo,
                max_tokens=300,
                system=sistema,
                messages=[{"role": "user", "content": json.dumps(entrada, ensure_ascii=False)}],
            )
            return extrair_json(resp.content[0].text)
        except Exception as e:  # tenta de novo em erro de rede ou JSON inválido
            ultimo_erro = e
            time.sleep(1.5 * (t + 1))
    return {"risco": "medio", "motivo": f"falha na classificação automática: {ultimo_erro}",
            "acao_sugerida": "Revisar manualmente.", "confianca": "baixa"}
