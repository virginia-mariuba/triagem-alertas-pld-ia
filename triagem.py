"""Triagem de alertas de PLD (dados fictícios).

Exemplos:
    python src/triagem.py --modo regras
    python src/triagem.py --modo llm       # precisa de ANTHROPIC_API_KEY
    python src/triagem.py --modo ambos
"""
import argparse
import csv
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from regras import pontuar  # noqa: E402

ORDEM = {"alto": 0, "medio": 1, "baixo": 2}
NIVEIS = ["alto", "medio", "baixo"]


def ler(caminho):
    with open(caminho, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def avaliar(linhas, coluna, nome):
    """Compara a classificação com o rótulo esperado (apenas dados fictícios)."""
    certos = sum(1 for l in linhas if l[coluna] == l["risco_esperado"])
    print(f"\n[{nome}] acertos: {certos}/{len(linhas)} ({certos / len(linhas):.0%})")
    matriz = Counter((l["risco_esperado"], l[coluna]) for l in linhas)
    print("linhas = esperado, colunas = previsto")
    print(f"{'':8}" + "".join(f"{n:>8}" for n in NIVEIS))
    for esp in NIVEIS:
        print(f"{esp:8}" + "".join(f"{matriz[(esp, prev)]:>8}" for prev in NIVEIS))


def salvar(linhas, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)


def relatorio(linhas, coluna, motivo_col, caminho, titulo):
    cont = Counter(l[coluna] for l in linhas)
    prioritarios = sorted(linhas, key=lambda l: ORDEM[l[coluna]])
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"# {titulo}\n\n")
        f.write(f"Total de alertas: {len(linhas)}  \n")
        f.write(f"Alto: {cont['alto']} | Médio: {cont['medio']} | Baixo: {cont['baixo']}\n\n")
        f.write("## Fila priorizada para o analista (alto risco primeiro)\n\n")
        f.write("| Alerta | Valor | Risco | Motivo |\n|---|---|---|---|\n")
        for l in prioritarios[:25]:
            f.write(f"| {l['id_alerta']} | R$ {float(l['valor']):,.2f} | {l[coluna]} | {l[motivo_col]} |\n")
        f.write("\n(Mostrando os 25 primeiros. Dados fictícios.)\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modo", choices=["regras", "llm", "ambos"], default="regras")
    ap.add_argument("--entrada", default="data/alertas_sinteticos.csv")
    ap.add_argument("--saida", default="output")
    ap.add_argument("--limite", type=int, default=0, help="usar só os N primeiros alertas (útil para testar o custo do modo llm)")
    args = ap.parse_args()

    linhas = ler(args.entrada)
    if args.limite:
        linhas = linhas[: args.limite]
    print(f"{len(linhas)} alertas lidos de {args.entrada}")

    if args.modo in ("regras", "ambos"):
        t0 = time.perf_counter()
        for l in linhas:
            l["risco_regras"], l["motivo_regras"] = pontuar(l)
        print(f"Regras processaram em {time.perf_counter() - t0:.3f}s")
        avaliar(linhas, "risco_regras", "regras")

    if args.modo in ("llm", "ambos"):
        from llm import classificar, criar_cliente
        cliente = criar_cliente()
        t0 = time.perf_counter()
        for i, l in enumerate(linhas, 1):
            r = classificar(l, cliente)
            l["risco_llm"], l["motivo_llm"] = r["risco"], r["motivo"]
            l["acao_llm"], l["confianca_llm"] = r["acao_sugerida"], r["confianca"]
            print(f"  {i}/{len(linhas)} {l['id_alerta']}: {r['risco']}")
        print(f"LLM processou em {time.perf_counter() - t0:.1f}s")
        avaliar(linhas, "risco_llm", "llm")

    salvar(linhas, os.path.join(args.saida, "triagem.csv"))
    coluna = "risco_llm" if args.modo in ("llm", "ambos") else "risco_regras"
    motivo = "motivo_llm" if coluna == "risco_llm" else "motivo_regras"
    relatorio(linhas, coluna, motivo, os.path.join(args.saida, "relatorio.md"),
              f"Relatório de triagem (modo {args.modo})")
    print(f"\nArquivos gravados em {args.saida}/ (triagem.csv e relatorio.md)")


if __name__ == "__main__":
    main()
