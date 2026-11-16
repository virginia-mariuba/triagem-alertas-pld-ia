"""Testes simples, sem rede. Rode com: python tests/test_extrair_json.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from llm import extrair_json  # noqa: E402
from regras import pontuar  # noqa: E402


def test_json_limpo():
    r = extrair_json('{"risco":"alto","motivo":"x","acao_sugerida":"y","confianca":"alta"}')
    assert r["risco"] == "alto"


def test_json_com_texto_em_volta_e_acento():
    r = extrair_json('Claro! {"risco":"Médio","motivo":"x","acao_sugerida":"y","confianca":"média"} Pronto.')
    assert r["risco"] == "medio" and r["confianca"] == "media"


def test_risco_invalido():
    try:
        extrair_json('{"risco":"gravissimo"}')
    except ValueError:
        return
    raise AssertionError("deveria falhar")


def test_sem_json():
    try:
        extrair_json("não consegui")
    except ValueError:
        return
    raise AssertionError("deveria falhar")


def test_regras_alto_e_baixo():
    alto = {"valor": "47500", "renda_mensal": "1500",
            "descricao_alerta": "Cinco depósitos, possível fracionamento",
            "justificativa_cliente": "Cliente não apresentou justificativa"}
    baixo = {"valor": "2000", "renda_mensal": "5000",
             "descricao_alerta": "Pagamento de aluguel recorrente",
             "justificativa_cliente": "Contrato de locação anexado"}
    assert pontuar(alto)[0] == "alto"
    assert pontuar(baixo)[0] == "baixo"


if __name__ == "__main__":
    testes = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in testes:
        t()
        print("ok", t.__name__)
    print(f"{len(testes)} testes passaram")
