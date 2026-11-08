# ADR-0075 — Revogações versionadas e contenção de mandados desatualizados

- **Decisão:** DEC-080, opção **C**, escolhida expressamente pelo idealizador em 2026-11-07.
- **Situação:** **APROVADA apenas como arquitetura no Discovery v7.6; NÃO IMPLEMENTADA**.
- **Documento técnico:** `docs/80-revogacoes-retificacoes-validade-e-reconciliacao-de-mandados-distribuidos.md`; **64 testes candidatos `T080-01..T080-64`, nenhum executado**.
- **Integridade:** preservar **DEC-060 a DEC-079** e todos os ADRs históricos, especialmente **ADR-0055 a ADR-0074**, exatamente como no Discovery v7.5.

## Contexto

DEC-078/C organiza procedimentos jurídicos/faccionais locais; DEC-079/C permite mensagens de cooperação, mandados e conflitos de competência por rotas legítimas e relógio. O emissor pode suspender, retificar, expirar ou revogar uma ordem antes de a autoridade destinatária receber a atualização. A simulação deve distinguir: (a) o **estado autoritativo da ordem na fonte**; (b) o que cada destinatário **sabe ou acredita**; (c) a **elegibilidade segura para realizar uma ação coercitiva**. Confundir esses níveis causa onisciência ou coerção com informação vencida.

## Alternativas

- **A — Revogação instantânea global:** rejeitada por exigir conhecimento imediato em NPCs, contrariando DEC-022/029/069/074.
- **B — Atualizações isoladas sem reconciliação coordenada:** rejeitada por facilitar prisões/confiscos com versões obsoletas e efeitos duplicados.
- **C — Correções versionadas, propagação causal, reconciliação e bloqueio de coerção incerta:** **APROVADA**.

## Regras vinculantes

1. **Ordens como eventos imutáveis e versões:** criar um `LegalOrderEvent` para `ISSUE`, `AMEND`, `SUSPEND`, `REVOKE`, `EXPIRE` e, se autorizada, `REISSUE`/`CORRECT`, vinculando caso, emissor, competência, data DR, razão pública filtrada, revisão e prova de origem. Não sobrescrever evento histórico por alteração de estado.
2. **Separar estado autoritativo, informação recebida e execução:** `AuthoritativeOrderState` no domínio emissor/competente; `RecipientKnowledgeState` por autoridade/região; `CoerciveActionGate` independente para permissão de efeito. Revogação não torna todos os destinatários narrativamente informados.
3. **Precedência e causalidade:** revisão monotônica por `(campaign, branch, case_id, issuer_authority_id, order_id)`; validar cadeia de versões/eventos e competência em cada atualização. Carimbo de tempo isolado ou último mensageiro a chegar não decide precedência. Mudança de emissor/competência não mescla cadeias automaticamente.
4. **Retificação não é sempre revogação:** correção de nome, prazo, alvo ou escopo exige categoria explícita, avaliação do impacto, riscos e necessidade de nova notificação/aceite. `SUSPEND` pausa efeitos, `REVOKE` encerra autoridade futura daquela ordem, `EXPIRE` depende de tempo e política curada; `REISSUE` requer novo gate/identificador e não revive a ordem revogada silenciosamente.
5. **Mensagens causais, não telepáticas:** aviso com origem comprovada, canal, rota/região, emissor, destinatário, clock DEC-022, Knowledge Pack e ACL; a origem do evento e seu recebimento são eventos distintos. Multipath e mensagens fora de ordem não tornam uma revisão antiga a mais recente.
6. **Proteção de ações coercitivas sem onisciência NPC:** o *gateway de segurança* pode consultar revisão/estado autoritativo disponível no ledger da campanha **sem expor essa informação ao NPC**; essa consulta é uma barreira de execução, não um canal de conhecimento ficcional. Se prova suficientemente atual/competente não estiver disponível, bloqueie ou suspenda ação HIGH em vez de inferir validade.
7. **Coerção HIGH fail-closed:** prisão física, confisco, tortura, perseguição/hostilidade mecânica, morte, alteração de quest/romance, retenção de item ou sanção grave exigem competência, ordem vigente, alvo/identity VERIFIED, consentimento pertinente DEC-041/042, risk gate DEC-027/034 e host receipt DEC-011/012. Ausência de confirmação **não** autoriza execução.
8. **Ações narrativas e desinformação:** NPC que ainda não recebeu revogação pode *acreditar* que o mandado vale e pode narrar intenções equivocadas conforme DEC-064/074, mas não forçar efeitos mecânicos sem gate. Pode haver tentativa injusta ou decisão corrupta **na ficção**, sem apresentar o estado incorreto como direito legítimo comprovado.
9. **Sem retroatividade fictícia:** revogação interrompe vigência futura da ordem; não apaga prisões, viagens, diálogos, reputações ou danos efetivamente ocorridos. Decisão reparatória, restituição, desculpas e retificação pública devem ser propostas/avaliadas separadamente na **DEC-081, aberta**.
10. **Idempotência e delivery:** chave conceitual `(campaign, branch, order_id, revision, issuing_authority, recipient_authority, event_type)`. Mensageiros duplicados não aplicam revogação duas vezes; confirmação de entrega não equivale a reconhecimento ou execução.
11. **Anti-ressurreição de ordens:** armazenar tombstone/revisão terminal de revogação/expiração e impedir que pacotes atrasados de emissão/suspensão mais antiga restaurem o status `ACTIVE`. Reabertura/reemissão requer processo novo validado.
12. **Falsificação e conflitos de autoridades:** assinatura/selo/documento suspeito pode existir como alegação na narrativa, mas não altera estado autoritativo sem prova de origem/competência; emitentes rivais com revogações concorrentes entram em `COMPETENCE_DISPUTED` e requerem regra curada, não voto de LLM.
13. **Identidade, pseudônimos e segredo:** DEC-066/075–077; uma correção de mandado sobre alias não identifica automaticamente o PC verdadeiro. Enviar a uma autoridade apenas os campos autorizados de caso/identidade, sem expor backstory/segredo de jogador.
14. **Tempo DR, fontes e lugar:** vigência, prazos e comunicação vinculados à região/época e tratados/facções atestados DEC-060–063/078/079; não inventar direito moderno, aliança, mensageiro instantâneo ou competência universal.
15. **Separação física do cânone:** `knowledge/periods/<ANO>-DR/` permanece segmentado **fisicamente por ano DR** (DEC-060); evidência histórica e curadoria DEC-061/062; Knowledge Packs versionados DEC-063. Mandados, revisões, entregas, crenças e ações são overlays privados da campanha/ramo, nunca reescrevem lore canônico.
16. **Falhas e consistência:** após crash, timeout, save/load, restore, fork, mod/build alterado, rede intermitente ou `UNCERTAIN`, reconciliar receipts/epochs antes de retry. `STALE` bloqueia, e revogação não é descartada por worker desatualizado.
17. **Prioridade de aviso de revogação:** fila DEC-056 prioriza correções de maior risco e processos prestes a executar efeito, sem prometer entrega instantânea ou furar limites legítimos; fallback é suspensão segura, não execução.
18. **Auditoria reversível em efeitos narrativos, não apagamento de fatos:** manter cadeia `ordem → revisão → envio → recebimento → reconhecimento → ação host` com tempos, fontes, ACL e motivos; retificações acrescentam fatos, sem apagar o que era conhecido antes.
19. **SPECS/POCs antes do motor:** estados, mensagens, fences, gates e interfaces são candidatos. Nenhuma capacidade de deter, libertar, remover wanted status, revogar script, mover guarda ou confiscar existe comprovadamente no BG2:EE/EEex multiplayer; exigir POCs isoladas host+2 clientes por build.
20. **Código determinístico primeiro:** aplicação/reconciliação, ordenação de revisões e risk gates via regras e algoritmos auditáveis; LLM local sob demanda para redação contextual, sem arbitrar vigência de mandado, competência, revogação ou coerção por conta própria.

## Exemplo hipotético

Autoridade X emite mandado versão 1; destinatário Y o recebe por mensageiro e o aceita nos limites locais. X revoga por evidência nova, produzindo revisão 2. Y ainda desconhece a revogação porque a notícia está em trânsito; em sua memória, acredita na versão 1. O validador de **segurança** da campanha conhece ou exige informação atual antes de permitir uma ação coercitiva HIGH. Assim, a tentativa mecânica fica bloqueada se a versão vigente foi revogada ou não é verificável, sem que Y passe a saber automaticamente da revisão 2. Após recebimento legítimo, sua crença pode ser corrigida, com registro temporal. Se houve dano antes da revogação, ele não desaparece automaticamente.

## Consequências

- **Benefícios:** continuidade entre regiões sem onisciência, correções rastreáveis, bloqueio de coerção obsoleta e auditoria.
- **Custos:** revisões por ordem, tombstones, estado epistêmico por destinatário, verificação de autoridade e reconciliador mais robusto.
- **Limite:** atores podem manter crenças obsoletas e ocorrer decisões ficcionais equivocadas; **efeitos mecânicos graves** exigem prova/autorizações da campanha, ou permanecem pendentes.

## Evidências e próximo tema

Esta é somente uma escolha humana de arquitetura. Documento 80 traz **64 testes candidatos T080-01 a T080-64 NÃO EXECUTADOS**. Não há POC BG2:EE/EEex/multiplayer. Questões abertas DEC-006/007/013/015/017/018 continuam abertas.

**DEC-081, em aberto:** reparação e revisão de danos após mandados injustos ou revogados: A) nenhuma reparação; B) rollback integral automático; **C (recomendada)** reparação contextual rastreável, proporcional, com nova avaliação, restituição quando tecnicamente comprovada e autorizada, sem apagar consequências históricas ou prometer rollback do motor.
