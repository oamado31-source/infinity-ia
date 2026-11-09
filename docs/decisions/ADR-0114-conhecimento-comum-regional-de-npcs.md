# ADR-0114 — Conhecimento comum regional de NPCs a partir do pacote canônico pinado

**Estado:** APROVADA (decisão explícita do mantenedor, 2026-11-09).
**Origem:** SPEC-005 deixou para "uma regra própria" o uso do pacote canônico pelos NPCs; teste de laboratório S1d (2026-11-09).
**Interpreta (sem editar):** ADR-0059, itens 1–4 e 12 (aquisição legítima, pacote não atualiza mentes, falha segura); ADR-0024 (sem difusão por compartilhar região); ADR-0058 (pacotes pinados por campanha).
**Gate:** etapa 1 (single player, ADR-0113). Os testes sintéticos não comprovam capability no BG2:EE.

## Contexto

O pacote de 1369 DR (`knowledge/periods/1369-DR/`) tem entradas conferidas e é pinado por campanha. Os NPCs ainda não o usavam. O ADR-0059 exige que um NPC só saiba algo por canal legítimo (item 2), que a atualização de pacote não atualize mentes (item 3) e que `CANON_CLAIM` não vire `CAMPAIGN_FACT` (item 1). O ADR-0024 proíbe a difusão instantânea "só por estar na mesma região".

Uma primeira versão desta regra dava a um companheiro o conhecimento comum de uma região depois de cerca de um dia de jogo no grupo dentro dela (`REGIONAL_EXPOSURE`). O teste de laboratório funcionou: Jaheira passou a responder sobre o Conselho dos Seis depois de um dia em Athkatla. O mantenedor, porém, **rejeitou a regra para membros do grupo**. Um companheiro não aprende sobre um lugar só por estar nele por horas ou dias, sem pesquisar nem conversar com os habitantes. Ele poderia saber do Conselho perguntando a alguém na taverna, mas não perguntando a outro membro do grupo que só "esteve lá".

## Alternativas consideradas

- **A — Exposição por tempo para todos os NPCs, inclusive companheiros:** implementada e testada no laboratório; **rejeitada para membros do grupo**. Presença não é aquisição.
- **B — Canais distintos por situação do NPC:** **selecionada.** Origem curada para qualquer NPC, residência por tempo só para NPCs de fora do grupo, investigação ativa para os membros do grupo.
- **C — Injetar o pacote inteiro no contexto do diálogo:** contraria o ADR-0059 (onisciência) e o ADR-0024; rejeitada.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-09.

1. **Elegibilidade.** Só podem ser adquiridas entradas com `access_scope = COMMON_REGIONAL` cujo gate dê `CANON_OK`, num ramo cujo pin do pacote dê `MATCH`. Entradas `CANON_REFERENCE` (por exemplo, organizações secretas) nunca são adquiridas por estes canais.
2. **Canal `ORIGIN` (qualquer NPC).** Um antecedente curado (`background_regions` na persona: região, fonte S0/S1 com localizador e conferência) dá as entradas da região e das sub-regiões. Sem fonte forte conferida, o antecedente é ignorado.
3. **Canal `RESIDENCE` (só NPCs de fora do grupo).** Um NPC que mora ou está numa região (estadia curada com evidência, por exemplo a área onde o jogo o coloca) aprende o que é comum ali depois de um limite de tempo de jogo. O limite padrão é 7200, um dia se 300 = 1 hora, unidade ainda não confirmada. O tempo só conta depois do pin vigente e **enquanto o NPC não está no grupo**. Dá a região e as regiões ancestrais: morar em Athkatla ensina o que é público em Amn, morar no interior de Amn não ensina o que é específico de Athkatla.
4. **Membros do grupo nunca aprendem por tempo de permanência.** Para um companheiro, só valem `ORIGIN` e o canal `INQUIRY`.
5. **Canal `INQUIRY` (reservado; próxima entrega).** Ato ativo observado de um membro do grupo: perguntar a um NPC que sabe (pelo canal `ORIGIN` ou `RESIDENCE`), ler uma fonte no jogo ou pesquisar. Perguntar a outro companheiro que só esteve no lugar não conta. Até a observação desse ato existir, nenhum companheiro sem origem curada sabe o conhecimento comum.
6. **Registro.** Cada aquisição é gravada uma vez (`npc_canon_knowledge`, append-only, chave idempotente por campanha/ramo/NPC/entrada/canal/revisão). O registro guarda o canal, a região, a revisão, o pin, o evento-gatilho e um **instantâneo** do título e do resumo. Corrigir o pacote depois não muda o que o NPC aprendeu; um novo pin não concede nada retroativamente.
7. **Linha do tempo.** A aquisição só é visível no ramo e na linha do tempo do evento-gatilho. Um fork anterior ao gatilho não sabe.
8. **Uso no diálogo.** O conhecimento adquirido entra no prompt como itens `K1..Kn` (máximo 12) numa seção "CONHECIMENTO GERAL", com a regra de contar com as próprias palavras sem dizer que viu ou participou. O validador aceita os ids `K` em `used_facts` e bloqueia ids crus na fala, como já faz com `F`. Sem aquisição, os nomes do pacote continuam desconhecidos e a fala cai no fallback.
9. **Sem LLM na regra.** Aquisição é determinística, por código; o LLM só formula a fala sobre o que já foi atribuído (ADR-0024 item 3).

## Consequências

- Hoje nenhum companheiro do BG2 recebe conhecimento comum. O manual (p. 31) liga Imoen a Candlekeep, Jaheira aos Harpistas e Minsc a Rashemen; nenhum é de Amn ou Tethyr. O canal `RESIDENCE` está implementado e testado, mas inativo no laboratório: ainda não há estadias curadas de NPCs de fora do grupo.
- O valor `INQUIRY` já existe no schema (`basis`) para evitar reconstruir a tabela; a regra ainda não o concede.
- O serviço de laboratório troca `--exposure-threshold` por `--residence-threshold`.
- Os 12 registros `REGIONAL_EXPOSURE` do banco de laboratório `lab-s1` são evidência do experimento rejeitado. A migração 0002 mudou antes do merge, então uma nova rodada usa uma campanha nova.

## Contratos e SPECs vinculadas

SPEC-003 (memória de NPC: `src/infinity_ai/memory/common_knowledge.py`, `MemoryStore.known_canon/record_canon_knowledge/recall_common`, migração `0002_npc_canon_knowledge.sql`); SPEC-004 (contexto e validação do diálogo); SPEC-005 (pin, gate e `access_scope`).

## Evidências, riscos e hipóteses não verificadas

- Evidência: `docs/evidence/S1d-2026-11-09-laboratorio-arm64.md` (single player).
- Não verificado: a unidade de `game_time` (o descanso não pôde ser medido no laboratório). O limite fica configurável até a conferência.
- Risco: resumos enciclopédicos podem soar "livrescos" na fala; aceito nesta etapa.
- Fora de escopo: rumores, notícias novas e conhecimento por organização (Harpistas), que seguem o ADR-0024 (propagação por rede).
