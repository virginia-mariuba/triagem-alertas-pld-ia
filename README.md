# Triagem de alertas de PLD com IA (dados fictícios)

Automação que lê alertas de movimentações financeiras, classifica o risco (baixo, médio ou alto), explica o motivo e sugere a próxima ação, entregando uma **fila priorizada** para o analista.

> **Aviso:** todos os dados são **100% fictícios**, criados para demonstração. A ferramenta é um apoio à triagem; **a decisão é sempre do analista humano**. Não use dados reais de clientes.

## O problema

Em prevenção à lavagem de dinheiro (PLD), os sistemas geram muitos alertas, e boa parte é falso positivo. O analista gasta tempo lendo cada justificativa para decidir o que merece atenção primeiro.

## A solução

1. Entrada: planilha de alertas (valor, perfil do cliente, descrição, justificativa).
2. Um modelo de IA recebe cada alerta, com um prompt que define critérios e formato.
3. Saída: risco, motivo, ação sugerida e confiança.
4. Relatório com os alertas de alto risco no topo.

```
alertas (CSV/planilha) → regras (base) ─┐
                       → IA (prompt) ───┼→ risco + motivo + ação → fila priorizada
                                         └→ comparação com o rótulo esperado
```

Duas versões do mesmo fluxo:
- **Código (Python):** esta pasta `src/`.
- **No-code (n8n, Make ou Zapier):** passo a passo em [`docs/roteiro_no_code.md`](docs/roteiro_no_code.md).

## Estrutura

```
data/        alertas fictícios (gerados por src/gerar_dados.py)
prompts/     prompt de classificação usado pela IA
src/         gerar_dados.py · regras.py · llm.py · triagem.py
tests/       testes simples, sem rede
docs/        roteiro no-code
```

## Como rodar

```bash
python src/gerar_dados.py              # gera 90 alertas fictícios
python tests/test_extrair_json.py      # testes
python src/triagem.py --modo regras    # classificação por regras (sem IA)

# com IA (precisa de chave de API; gera custo, comece com poucos alertas)
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sua-chave"   # no Windows: set ANTHROPIC_API_KEY=sua-chave
python src/triagem.py --modo llm --limite 10
python src/triagem.py --modo ambos     # compara regras e IA
```

O modelo pode ser trocado com a variável `MODELO_LLM`. Os resultados ficam em `output/` (`triagem.csv` e `relatorio.md`).

## Resultados

**Base por regras simples** (rodado nos 90 alertas fictícios):

| Esperado \ Previsto | alto | médio | baixo |
|---|---|---|---|
| alto | 21 | 2 | 0 |
| médio | 0 | 6 | 8 |
| baixo | 0 | 0 | 53 |

Acerto geral de 80/90 (89%). As regras acertam bem os extremos, mas **perdem a maioria dos casos médios** (6 de 14 corretos), que dependem de ler o texto livre e entender o contexto. É nesse ponto que a IA deve agregar.

**IA (LLM):** [preencher depois de rodar `--modo llm` ou o fluxo no-code: acertos e matriz de confusão].

> Os rótulos esperados vêm do próprio gerador de dados fictícios, que segue padrões parecidos com os das regras. Por isso os números são **otimistas** e não representam desempenho em alertas reais.

### Tempo economizado (preencher só com medições reais)

| Medida | Valor |
|---|---|
| Alertas usados no teste | [ ] |
| Tempo para triar manualmente (minutos por alerta, medido em amostra de 10) | [ ] |
| Tempo com a automação (minutos no total) | [ ] |
| Estimativa de horas economizadas por 1.000 alertas | [ ] |

## Limitações e cuidados

- Dados fictícios e padrões simplificados; não há validação com casos reais.
- Modelos de linguagem podem errar ou inventar justificativas; por isso o prompt manda usar só as informações recebidas e a saída é sempre revisada por uma pessoa.
- O rótulo `risco_esperado` nunca é enviado ao modelo (veja `CAMPOS_ENTRADA` em `src/llm.py`).
- Em uso real, seria preciso tratar privacidade e sigilo dos dados (LGPD) e a política da instituição.

## Próximos passos

- Medir a taxa de acerto da IA e ajustar o prompt com os erros.
- Testar mais exemplos no prompt e comparar modelos.
- Publicar uma versão com interface simples (por exemplo, no Lovable) para o analista colar um alerta e ver a classificação.

## Transparência

A estrutura inicial do projeto foi montada com apoio de uma IA (Claude) e **revisada e adaptada por mim**. Os números de tempo e acerto da IA acima são os que eu medi ao rodar o projeto.
