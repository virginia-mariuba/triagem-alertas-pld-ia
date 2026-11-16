# Roteiro no-code: o mesmo fluxo no n8n, Make ou Zapier

Escolha **uma** ferramenta e confira o plano gratuito e os limites dela. Os nomes de nós e menus mudam entre versões, então siga o que aparecer na tela e use este roteiro como guia da lógica.

## Visão geral do fluxo

```
Planilha (nova linha) → IA classifica → trata a resposta → se risco alto: avisa → grava resultado na planilha
```

## Passo a passo

1. **Prepare a planilha (Google Sheets).**
   - Importe `data/alertas_sinteticos.csv`.
   - Crie as colunas: `risco_ia`, `motivo_ia`, `acao_ia`, `confianca_ia`.
   - Deixe `risco_esperado` na planilha só para a conferência no final. **Não envie essa coluna para a IA.**

2. **Gatilho.** Use "nova linha na planilha" ou um gatilho manual que processa todas as linhas. Comece com **10 linhas** para testar.

3. **Nó de IA.** Use o nó do provedor que você tem (Anthropic, OpenAI, etc.) ou um nó de requisição HTTP.
   - **Instruções do sistema:** cole o conteúdo de `prompts/classificar_alerta.md`.
   - **Mensagem do usuário:** monte um JSON só com `tipo_operacao`, `valor`, `ocupacao`, `renda_mensal`, `descricao_alerta` e `justificativa_cliente`.

4. **Tratar a resposta.** A IA deve devolver um JSON. Extraia os campos `risco`, `motivo`, `acao_sugerida` e `confianca` (nó de código, de dados ou de análise de JSON). Se falhar, grave `risco_ia = medio` e `motivo_ia = revisar manualmente`.

5. **Ramificação.** Se `risco = alto`, envie um aviso (e-mail, Slack ou Telegram) com o ID do alerta e o motivo. Os demais seguem direto para a gravação.

6. **Gravar na planilha.** Atualize a linha com `risco_ia`, `motivo_ia`, `acao_ia` e `confianca_ia`.

7. **Testar e medir.**
   - Rode 10 linhas, confira à mão, ajuste o prompt se preciso e depois rode as 90.
   - Calcule a taxa de acerto no Sheets comparando `risco_ia` com `risco_esperado`, por exemplo: `=SOMARPRODUTO(--(I2:I91=K2:K91))/CONT.VALORES(I2:I91)` (ajuste as letras das colunas à sua planilha).
   - Meça o tempo: cronometre a triagem **manual** de 10 alertas e o tempo total do fluxo automático. Anote no README.

8. **Evidências para o portfólio.** Salve capturas de tela do fluxo e da planilha preenchida, e se possível um vídeo curto de 1 minuto rodando. Coloque na pasta `docs/` e referencie no README.

## Cuidados

- Use **apenas dados fictícios**.
- Verifique o custo de chamadas à API antes de rodar o lote completo.
- Se a IA errar em padrões específicos, acrescente exemplos ao prompt e rode de novo.
