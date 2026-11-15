# ADR-0130 — Conhecimento individual como projeção e aprendizado em conversa

**Estado:** APROVADA (CR-2026-011, decisões D1, D2, D4, D5 e D8–D12, mantenedor, 2026-11-15).
**Origem:** o mantenedor quer que os diálogos ensinem o jogador sobre o mundo, sem NPC onisciente e com risco mínimo de alucinação. Quer também que o NPC aprenda o que lhe é contado de forma legítima.
**Relaciona-se com:** SPEC-008; ADR-0059 (aprendizado e revisão de crenças); ADR-0114 (conhecimento regional); ADR-0116 (`INQUIRY`); ADR-0117 (identidade e camadas); ADR-0119 (relações); ADR-0123/0124 (memória e lembranças); ADR-0107 item 6 (privacidade); ADR-0071 (personas).
**Gate:** etapa 1, single player. Nada é escrito no estado do jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-15.

1. **Uma fonte curada, projetada por NPC.**
   - O pacote canônico por ano DR continua sendo a única referência factual.
   - Cada NPC tem uma **projeção** do que sabe: referências às entradas, com canal de aquisição, evidência, momento de jogo, ramo, profundidade e estado epistêmico. Não há cópia do corpus por NPC.
   - O modelo de linguagem nunca recebe o corpus.
2. **Rumor e crença ficam no NPC, não no cânone.**
   - Os valores de `verification_status` continuam os de `canon_entry_v1`.
   - `RUMOR`, `HEARD`, `SUSPECTS` e crenças são estados epistêmicos da projeção.
   - Um relato nunca vira `CAMPAIGN_CANON` ou `SOURCE_CHECKED` por ter sido dito.
3. **Biografia:**
   - oficial, só com respaldo;
   - NPC gerado: fixada uma vez, persistida e versionada; só vira cânone de campanha depois de curadoria (D2).
4. **Canais de aquisição:**
   - **mantidos:** `ORIGIN`, `RESIDENCE` (só para quem está fora do grupo) e `INQUIRY` (companheiros), como hoje;
   - **na v1:** `DIRECT_DIALOGUE`, para o NPC com quem o jogador fala (D10);
   - **depois, por decisão própria:** `NPC_TO_NPC`;
   - **bloqueados até haver prova no host (D11):** `VERIFIED_OVERHEARING` e `NATIVE_DIALOGUE_CAPTURE`.
5. **Aprendizado só depois da fala publicada.**
   - **Fala do NPC:** só a validada e publicada ensina, e só o que foi **dito**, conferido como no `mentioned_in` atual. Um ID que só aparece em `used_facts`, um rascunho ou uma resposta recusada não ensinam.
   - **Fala do jogador:** ensina só por **casamento determinístico** com entradas curadas (nomes, aliases e predicado), **nunca por modelo de linguagem**. Casamento parcial ou ambíguo dá `NO_ACQUISITION` (D9).
   - **Evento novo:** só acrescentado (append-only) e idempotente por fala, ouvinte, entrada e ramo, com atribuição da fonte. Não vale fora do ramo nem da campanha.
6. **Privacidade (D12):**
   - **v1:** não persiste texto do jogador; só IDs de entradas casadas, ouvinte, atribuição, ramo, tempo e chave. Um relato não confirmado do jogador não é aprendido.
   - **v2:** guardar alegações atribuídas, tipadas e sem a frase. Exige nova decisão.
   - **Resumo em texto:** fora de escopo.
7. **Notoriedade só curada na v1 (D4, D5):** registros de persona e feitos públicos com fonte, sem rolagens. O nível do personagem não conta como fama. Conhecer o nome não é reconhecer a pessoa (ADR-0071).
8. **Primeira curadoria (D8):** Athkatla em 1369 DR e Coroa de Cobre.

## Consequências

- **Código previsto:**
  - resolvedor único da projeção (refatoração do que hoje vem de `memory/common_knowledge.py` e das relações por afiliação);
  - extensão de `share_knowledge` para o NPC abordado;
  - recordação com atribuição no contexto e no validador.
- **Ordem (CR-2026-011):** o aprendizado vem depois da divulgação por item (ADR-0131), porque precisa saber o que o NPC pode retransmitir.
- **Testes:** os critérios de aceite da SPEC-008, sem regressão na bateria de diálogo.

## Riscos e limites

- **Gargalo de curadoria:** o ganho depende do corpus curado. A meta da fase (por exemplo, 30 entradas e 10 relações de Athkatla) deixa o custo explícito.
- **Casamento determinístico limitado:** o jogador pode contar algo verdadeiro com palavras que o código não casa. O resultado é não aprender, o que é preferível a aprender errado.
- **Sem prova de escuta no host:** ouvintes incidentais e diálogos nativos ficam fora até haver capacidade observada no BG2:EE/EEex.
