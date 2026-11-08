# ADR-0076 — Reparação contextual, proporcional e rastreável após injustiças

- **Decisão:** **DEC-081, opção C**, aprovada expressamente pelo idealizador em **2026-11-07**.
- **Estado:** **APROVADA como arquitetura no Discovery v7.7 — NÃO IMPLEMENTADA**.
- **Documento técnico:** `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`, com **66 testes candidatos T081-01..66 — NÃO EXECUTADOS**.
- **Integridade histórica:** todas as DEC-060 a DEC-080 permanecem integralmente aprovadas e **todos os ADRs anteriores, em especial ADR-0055..0075, preservados byte a byte**; não se alteram decisões antigas.

## Contexto

A DEC-080/C permite revogar ou retificar uma ordem versionada, mas rejeita rollback universal de atos passados. Uma prisão injusta, acusação equivocada, confisco, perda de oportunidade ou dano reputacional só pode ser remediado se houver **dano realmente confirmado**, nexo causal, procedimento e autoridade competente no contexto temporal, e eventual capacidade mecânica comprovada. Revogação não cria restituição, reparação não torna todos os NPCs informados, e corrupção/má-fé de uma autoridade ficcional não substitui evidências de gameplay. Precisamos tratar correção como **novo processo causal**, não sobrescrita do estado histórico.

## Alternativas

- **A — Somente cessar efeitos futuros:** rejeitada como política geral, por eliminar a possibilidade de restituição, reabilitação e reconhecimento de injustiças onde cabíveis.
- **B — Rollback automático e integral:** rejeitada por apagar consequências legítimas, desrespeitar história individual, economias e relações, e presumir capacidade de reverter o BG2:EE/EEex.
- **C — Reparação contextual proporcional com rastreabilidade e autorização:** **APROVADA**.

## Regras vinculantes

1. **Reparação não é revogação.** `LegalOrderEvent(REVOKE/ANNUL/CORRECT)` é o fato jurídico/administrativo; `RemedyCase` é processo separado que analisa dano e possibilidade de reparação. Uma revogação posterior não prova que a ordem original era inválida quando emitida, que houve dano ou quem foi responsável; exigir evidências adicionais.
2. **Gatilho documentado:** caso de reparação só deve ser proposto a partir de decisão/revisão válida, danos confirmados ou reclamação autorizada, com `campaign_id`, `branch_id`, `legal_case_id`, ordem/revisão, `world_time_dr`, fonte, `checkpoint_epoch`, `knowledge_pack_revision` e `causal_event_ids`. Não inventar prisão, confisco ou perda só porque a ordem foi emitida.
3. **Quatro planos distintos:** (a) fato histórico da campanha; (b) conhecimento e crença das autoridades/NPCs; (c) avaliação de dano e responsabilidade; (d) medidas narrativas ou mecânicas autorizadas. Não converter desculpa oficial em itens adicionados ao inventário ou presunção de inocência mecânica.
4. **Taxonomia de danos:** `MATERIAL`, `ITEM_OR_CUSTODY`, `REPUTATIONAL`, `RELATIONAL`, `OPPORTUNITY`, `LIBERTY`, `QUEST_IMPACT`, `PERSONAL` e `UNKNOWN` são categorias candidatas, com prova, titular, intensidade, reversibilidade e eventuais danos mistos. Não usar números/valores de compensação arbitrários gerados por LLM.
5. **Nexo causal e não duplicação:** cada dano referenciará um ou mais `ConfirmedDamageEvent`, a ação/decisão que o causou e recibos quando mecânico. Correlação temporal não equivale a causalidade. O mesmo dano não poderá gerar pagamentos ou ajustes repetidos por diversas jurisdições sem política de compensação cruzada.
6. **Competência curada, não direito moderno genérico:** queixas, audiências, fóruns, recursos, restituição e obrigações variam por governo/facção/região/ano DR. Exigir fontes DEC-060–063 e política de jurisdição DEC-078/079. Sem evidência de competência/processo local, manter `PENDING_POLICY`/narrativa não vinculante, não inventar tribunal universal.
7. **Autoridades podem ser injustas:** interpretação, recusa ou demora de um NPC corrupto podem existir como **decisões e crenças da ficção**, mas verdade, obrigação, condenação ou sanção não são determinadas apenas pelo LLM. Decisões injustas podem abrir histórias posteriores sem superar os gates mecânicos.
8. **Remédios possíveis, não automáticos:** `ACKNOWLEDGEMENT`, `PUBLIC_CORRECTION`, `APOLOGY`, `SOCIAL_REHABILITATION`, `ITEM_RETURN`, `COMPENSATION_PROPOSAL`, `RELEASE_REQUEST`, `QUEST_REVIEW`, `NO_REMEDY_AVAILABLE` são **propostas** que exigem validação individual. Não prometer ressuscitar NPC, recuperar tempo perdido ou desfazer uma quest nativa sem teste e autorização específica.
9. **Restituição de itens e ouro sob ownership:** conferir o estado atual do host, a titularidade verificável, transferências DEC-073, valor original, duplicações e fonte de custeio. Repor item que já foi devolvido ou pertence legitimamente a terceiro é proibido. Nenhuma transferência mecânica por escrita direta de save ou texto LLM.
10. **Reparação social não significa esquecimento universal:** retratação, reconhecimento público ou reabilitação seguem canais DEC-029/074 e crenças DEC-064/075. NPCs distantes podem continuar acreditando na acusação anterior; publicar uma correção não apaga recordações nem atualiza todas as reputações de imediato.
11. **Proteção de privacidade e identidade:** vítimas, testemunhas, pseudônimos e PCs protegidos por DEC-019/028/041/045/046/066/076/077. Corrigir acusação pública não deve automaticamente expor a identidade secreta do beneficiário. Publicação define público, consentimento, finalidade e riscos.
12. **Direitos e escolhas dos jogadores:** não impor que um PC aceite desculpas, perdoe uma facção ou receba compensação que afete seu personagem sem consentimento quando aplicável. Um PC ausente não consente automaticamente. Cooperação e delegação mantêm titular e controlador distintos.
13. **Risco LOW/MEDIUM/HIGH pelo efeito agregado:** reconhecimento narrativo LOW pode ser allowlisted; MEDIUM requer autorização contextual; HIGH — perda/ganho de itens, grandes somas, prisão/libertação mecânica, alteração de quests, condenação de NPC, morte, mudança histórica — default-deny até gate especial e confirmação pertinente. Vários LOW não podem contornar HIGH.
14. **Authority separation:** código determinístico primeiro para validação de provas, revisões e idempotência; LLM local opcional para diálogos, petições e justificativas. O modelo não julga autonomamente competência, causalidade, valor monetário, veredito ou execução de remédio.
15. **Host como autoridade mecânica:** pedido de reparação não é receipt. Toda mudança de engine BG2:EE exige Action Gateway tipado DEC-012, capabilities demonstradas por build DEC-051/052 e recibos do host DEC-011; sem isso, proposta narrativa ou `BLOCKED_UNSUPPORTED`. Sem POC de restituição, soltura, atualização de quests, reputação ou dinheiro em multiplayer.
16. **Idempotência e operações incertas:** `remedy_id`, `damage_id`, `resolution_epoch`, revisão de plano, `idempotency_key`, target e effect_kind no `RemedyEffectLedger`. Timeout `UNCERTAIN`, restore, fork ou duplicidade bloqueiam retry cego. Reavaliar ownership, item, valor, consentimento e status antes de qualquer nova tentativa.
17. **Revisão, recurso e reparação parcial:** um caso pode propor múltiplos remédios com estados separados, parciais ou negados, mantendo razão, evidência e autoridade por remédio. Revisão de negativa ou correção do dano gera evento adicional; não apaga decisão/efeito anterior nem automaticamente compensa resultado já consumado.
18. **Tempo e história:** mandado revogado hoje não reescreve o passado; NPCs mantêm memórias verificáveis e consequências confirmadas, inclusive oportunidades perdidas. Atualizações propagam no relógio DEC-022, rotas DEC-069, com data DR, não por telepatia ou rewind.
19. **Cânone fisicamente segmentado:** DEC-060 exige `knowledge/periods/<ANO>-DR/` em pastas distintas. Provas editoriais DEC-061/062 e Knowledge Pack DEC-063 permanecem versionados. Queixas, dano, restituições e relatos derivados do jogo ficam no **overlay da campanha/ramo**, nunca nas pastas de lore canônico.
20. **Checkpoint, recuperação e migração:** coordenar com DEC-053/054/055, validar build/checkpoint, idempotência e recibos. Restore não importa compensações de futuro abandonado; mod/quest alterados invalidam operações pendentes. Auditoria registra o que foi pedido, autorizado, negado, executado ou incerto.
21. **Limites de processamento:** DEC-056 permite filas e prioridades por urgência, especialmente medidas que evitem prejuízos futuros, mas não acelera relógio, não inventa resposta de autoridade e não emite compensação sem receipt. Logs/telemetria respeitam ACL e minimização.
22. **Repercussão e consequências secundárias:** medidas de reparação podem gerar oportunidades de história, alteração social e responsabilização de agentes, mas cada repercussão exige causalidade e gates DEC-029–034/074/075; responsabilização institucional detalhada **permanece DEC-082 aberta**.
23. **Processo evolutivo:** POCs em ordem: ledger e snapshots sintéticos, regras de competência/causalidade sem engine, fluxos de pedido/decisão/retificação narrativos, teste read-only host e validação de estados, teste de efeito mecânico benigno isolado com autorização, save/load e host+dois clientes. Nada é considerado funcional pela mera existência da especificação.

## Exemplo hipotético

Um aventureiro foi detido **e a detenção foi confirmada** no ledger; depois, o mandado é revogado. Nova avaliação, com prova da detenção e do erro, pode abrir um pedido de reabilitação e, sob regras da autoridade regional, uma proposta de devolução de item com ownership comprovado. A retratação poderá chegar a determinada guilda por mensageiro, sem que toda a cidade saiba de imediato. Caso o item já tenha retornado ao dono, o sistema deve impedir duplicação. Caso o BG2:EE não forneça capacidade de devolver ou soltar, **não** declarar a mudança ocorrida: manter narrativa condicionada ou pendência.

## Consequências e trade-offs

- **Benefícios:** reparar injustiças sem apagar histórias, respeitar economia/identidade, criar oportunidades de contestação e responsabilização com trilha auditável.
- **Custos:** ledger de danos e remédios, múltiplos estados por tipo, provas/competência/revisão e gates de host por build.
- **Limitação consciente:** reparação pode ficar parcial, recusada ou impossível. A campanha não garante restituição justa ou recuperação completa; fatos históricos não são apagados e o motor não é assumido reversível.

## Evidências e pendências

**Somente decisão arquitetural aprovada; nenhum teste executado e nenhuma POC de BG2:EE/EEex/multiplayer realizada.** Documento 81 traz **66 testes candidatos `T081-01..T081-66`**, cuja execução exige SPECS e provas de capacidades. DEC-006/007/013/015/017/018 continuam abertas.

## Próxima decisão — DEC-082 (EM ABERTO)

**Fiscalização e responsabilização de autoridades e organizações por abusos comprovados:** A) limitar-se a reparação do indivíduo; B) alterar automaticamente liderança, poder e punições de agentes; **C recomendada)** procedimento contextual de investigação institucional, atribuição causal, competência, provas, direito de contestação, consequências proporcionais e gates HIGH; nenhum golpe, prisão de autoridade, exoneração mecânica ou reforma política por LLM. **Ainda não aprovada.**
