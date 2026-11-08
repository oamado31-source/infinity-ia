# Handoff Discovery → SPECs e primeiro desenvolvimento verificável — proposta para aprovação em lote

**Baseline:** Discovery v10.6, DEC-110/C e ADR-0105. **Estado:** PROPOSTA; não equivale a aprovação da Constitution, nem afirma que há POC de jogo executada.

## Avaliação da maturidade

O Discovery contém 105 ADRs arquiteturais, cuja maioria descreve restrições e cenários de domínio, mas ainda não demonstra suporte mecânico BG2:EE/EEex. O MVP deve privilegiar capacidades observáveis testadas. Existem sete DECs antigas abertas (006, 007, 013, 015, 016, 017, 018) e escolhas novas de implementação. Adiar toda a programação até esgotar decisões narrativas seria ineficiente. O projeto poderá implementar infraestrutura com SPECs aprovadas, enquanto mantém features dependentes da build bloqueadas.

## Recomendações de decisão / estimativa

| Alvo | Deliberações estimadas | Justificativa | Condição de avanço |
|---|---|---|---|
| **Primeiras SPECs e POCs** | ~8–12 decisões/grupos, Q01–Q12 | Ambiente, autoridade, UI mínima, LLM runtime, persistência, testes e recuperação. | P0 respondido + Constitution + SPEC aceitas. |
| **MVP demonstrável** | +6–10 escolhas de priorização P1 | Memória NPC, conteúdo, eventos e UX, dentro de capacidades verificadas. | Gates P0–P4 e aceites por feature. |
| **V1 delimitada** | +6–10 escolhas P1 | Matriz de FR, facções, economia, quests e saves, sem reabrir decisões já aprovadas. | POCs e desempenho reproduzíveis. |
| **Futuro / Living World ampliado** | Indeterminado | Dependências reais e mudança de escopo. | Abrir ADR apenas para mudanças materiais, não toda tarefa. |

## Sequência de SPECs (candidatas; validação e escopo dependem das respostas)

| SPEC candidata | Conteúdo observável | Pré-condição | Gate/aceite mínimo |
|---|---|---|---|
| SPEC-001 `bridge-observacao` | Versão/hash, handshake read-only, respostas tipadas, ausência de mutação | Q02–Q05 e Q10–Q11 | P0/P1/P2 com logs e `UNKNOWN` quando não observado |
| SPEC-002 `autoridade-multiplayer` | Host único, dois clientes, action IDs, consentimento e reconciliador | Q03/Q05/Q09/Q10 | P4 host+2 clients/safe save-load, sem desync |
| SPEC-003 `estado-memoria` | Evento privado por campanha, snapshot/epoch, NPC recordação consentida | Q01/Q08/Q09/Q15 | Dois clientes e reboot sem mistura de memória |
| SPEC-004 `dialogo-dinamico` | Interface degradável, contexto minimizado, LLM local-first | Q06/Q07/Q20/Q26 | Falha do modelo sem mutação ou leak |
| SPEC-005 `eventos-regionais` | Regras declarativas 096/097, propostas de efeitos e materialização guardada | Q16–Q18/Q23 | Sem spawn se capability não demonstrada |
| SPEC-006 `quests-originais` | 100–104 read-only → mapeamento → reconciliação → consequências | Q19/Q24 | Sem spoiler, sem overwrite de quest |
| SPEC-007 `contratos-e-recursos` | 107–110; negociação, obrigações, DAG, escrow somente após POC | Q13 e decisões já aprovadas | Nem promessa nem elegibilidade = transferência |

**O primeiro PR de código não precisa implementar todas essas SPECS.** Iniciar por SPEC-001, primeiro com um adapter sintético de referência e só depois pela bridge real read-only com build fixada e logs.

## Definição de pronto mínima para cada SPEC

- Requisito identificado com ligação DEC/ADR.
- Estados `UNKNOWN`, erro, recuperação, segurança e privacidade descritos.
- Interface tipada e versão de schema; teste de contrato.
- *Given/When/Then* ou EARS por comportamento observável.
- Gate de host, build e autoridade quando necessário.
- Matriz sintético vs. POC real; nenhum teste não executado marcado como aprovado.
- Sinais de falha, rollback e regressão definidos.
- Evidência associada a versão/hash e dois clientes quando multiplayer.

## Registro de mudança pós-SPEC

Para mudanças de regra: `CR-ID`, motivação, ADR atingido, SPEC e requisito atingidos, alterações de schema, plano de migração, testes novos/afetados e aprovação. Publicar nova revisão da SPEC e somente depois alterar código. Proibir reescrever ADR antigo; criar novo ADR que o complementa ou substitui, mantendo a proveniência.

## Primeiras ações após receber o questionário respondido

1. Interpretar respostas P0 e P1; registrar exceções em vez de presumir todos os padrões.
2. Consolidar as sete DECs abertas com aprovações do usuário, mapear novas decisões e produzir Constitution.
3. Criar SPEC-001 formal e demais SPECS priorizadas, com plan e tasks executáveis.
4. Rodar POC Windows BG2:EE limpo (P0) e EEex loader (P1), sem alterações no save original.
5. Provar read-only bridge (P2), depois mutação reversível em save descartável (P3) e dois clientes (P4).
6. Só então permitir materialização e recursos mais sofisticados; continuar domínio narrativo paralelamente, sem bloquear testes.

## Restrições imutáveis

Local-first; host como autoridade mecânica; NPCs sem onisciência; cronologia DR e Knowledge Packs com proveniência; isolamento de campanhas e saves; nenhum efeito HIGH com decisão LLM autônoma; ownership e privacidade; BG2 original protegido; regra de código antes de modelo; ausência de capabilities não preenchida por suposição.
