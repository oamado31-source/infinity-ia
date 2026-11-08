# SPEC-001 (RASCUNHO NÃO APROVADO) — Bridge de observação somente-leitura

**Status:** RASCUNHO dependente das respostas P0 do questionário e de POC Windows BG2:EE/EEex. **Não é uma funcionalidade implementada.**

## Intenção

Permitir que o host da sessão teste, em build versionada, uma leitura não invasiva do motor e devolva somente dados allowlisted, tipados e minimizados, sem mudança de save, flags de quest, NPC ou inventário.

## Requisitos candidatos

- REQ-BRIDGE-001: QUANDO a sessão iniciar, DEVERÁ registrar fingerprint exato da build/modpack/bridge e host epoch; mismatch → `BLOCKED_CAPABILITY`.
- REQ-BRIDGE-002: QUANDO uma observação for permitida, DEVERÁ usar allowlist/versionamento, proveniência de host e timestamp; ausência de capability → `UNKNOWN`, sem inferência.
- REQ-BRIDGE-003: QUANDO um cliente diferente do host requisitar ação, DEVERÁ respeitar identidade, autorização, RPC e regras de sessão; não haver mutação implícita.
- REQ-BRIDGE-004: QUANDO um estado técnico puder revelar spoilers, DEVERÁ filtrar a projeção semântica para o destinatário correto (DEC-028/100/101).
- REQ-BRIDGE-005: QUANDO houver falha de comunicação, DEVERÁ registrar resultado e permitir recuperação sem repetir comandos perigosos; nesse primeiro corte não existem comandos de escrita.
- REQ-BRIDGE-006: QUANDO o modelo de IA estiver indisponível, a bridge read-only continuará funcionando sem dependências de LLM.

## Cenários de aceite candidatos

1. `Given` BG2:EE limpo em Windows reproduzível, `When` o adapter inicializa, `Then` manifesta build e reporta capabilities sem escrever save.
2. `Given` EEex não instalado/versão incompatível, `When` o adapter consulta a capability, `Then` retorna `BLOCKED_CAPABILITY` sem estado inventado.
3. `Given` dado técnico ausente, `When` uma consulta allowlisted é executada, `Then` retorna `UNKNOWN` sem afirmar conclusão de quest.
4. `Given` dois clientes conectados, `When` ambos recebem um marco permitido, `Then` os registros do host e da sessão serão comparáveis, sem vazamento de segredos.
5. `Given` solicitação de mutação pelo modelo, `When` o componente read-only recebe o texto, `Then` rejeita, não despacha comando e registra evidência sanitizada.
6. `Given` save/reload, `When` a sessão retorna, `Then` epochs e origem das observações são atualizados, sem confundir restore com progresso narrativo.

## Plano / tarefas

Ainda não aprovados. Primeiro: aprovar Q01–Q12 → Constitution v1 → interfaces tipadas → simulador de adapter → POC P0 BG2 puro → POC P1 EEex → POC P2 leitura limitada → POC P4 dois clientes. Nenhum teste real foi feito.
