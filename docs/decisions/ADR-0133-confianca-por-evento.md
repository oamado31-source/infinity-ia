# ADR-0133 — Confiança por evento (fase 4b da SPEC-009)

**Estado:** APROVADA (mantenedor, 2026-11-17: "Aprovar como proposta", decisões D1 a D4 como propostas).

**Origem:** a ADR-0131 definiu os estados de confiança, `DESCONFIADO`, `NEUTRO`, `CONFIANTE` e `ÍNTIMO`. O primeiro corte usava todos `NEUTRO`. Por isso, nada `CONFIDENTIAL` saía, como o segredo dos escravos da arena (etapa 3), e ninguém ficava desconfiado.

**Relaciona-se com:**
- SPEC-009 (REQ-DISC-002 e REQ-DISC-003; tarefa "Confiança qualitativa e direcional por evento");
- ADR-0131 (divulgação por item, refinada aqui sem edição);
- ADR-0125 (reação) e ADR-0126 (moral);
- ADR-0124 (turnos de conversa);
- ADR-0101 (revisão, idempotência, sem decaimento automático);
- ADR-0095 e ADR-0096 (marcos de quest, fase seguinte).

**Gate:** etapa 1, single player. Nada é escrito no estado do jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-17.

1. **A confiança é um registro próprio, por evento.**
   - Cada mudança é um evento `NpcTrustRevised` com o NPC, o alvo, o estado, a regra e a causa (os ids dos eventos que a justificam).
   - A chave de idempotência é a regra mais a causa.
   - O estado atual sai dos eventos do ramo pela função pura `trust_of`.
   - O texto do jogador nunca cria nem muda confiança (ADR-0131, item 6).
2. **O alvo é o grupo do jogador** (`party`) no single player. A confiança por personagem fica para o multiplayer.
3. **Regras da primeira versão,** a partir do que a campanha já registra (`personality/trust.py`):
   - **`DESCONFIADO`:** uma intimidação ou uma traição (teste de moral da ADR-0126, qualquer resultado), ou uma reação hostil (ADR-0125). A decisão D3 incluiu a reação hostil. O estado fica até uma regra de volta, que não existe na primeira versão.
   - **`CONFIANTE`:** reação amistosa ou indiferente em pelo menos três sessões de jogo diferentes e pelo menos seis turnos de conversa no total, sem nada hostil antes (D1).
   - **O suborno** não move a confiança: dinheiro compra cessão (`YIELD`), não confiança.
   - **`ÍNTIMO`:** sem regra automática. Fica para os marcos de quest curados (D4).
4. **Domínio (D2):** o `CONFIANTE` que vem da convivência libera só os itens `CONFIDENTIAL` sobre o próprio NPC (`subject_id` igual ao dele). Segredos da casa ou de terceiros, como os escravos da arena, pedem um marco curado.
5. **Sem decaimento automático** (ADR-0101, item 13).
6. **A pergunta sobre um item retido, por título:**
   - A ausência tipada (ADR-0131) responde `WITHHELD` quando a pergunta cita, de algum título retido, uma palavra que nada do que a pessoa pode dizer tem.
   - Antes bastava qualquer palavra de qualquer título retido aparecer no que ela diz para desistir. "Tem uma arena aqui na Coroa de Cobre?" não era recusada, e o modelo, sem o item, dizia que não havia arena.
7. **A memória da conversa não cita o que está retido** (laboratório, S1u).
   - A linha "Vocês falaram sobre: …" (ADR-0124) sai sem os títulos que a pessoa retém no turno.
   - Quem contou da arena antes e agora desconfia do grupo não recebe o título no prompt.
8. **Fora desta decisão:** a confiança entre NPCs, a reputação por comunidade (ADR-0025), o rumor (ADR-0024) e os marcos de quest (fatia seguinte, ADR-0095 e ADR-0096, com o mesmo evento).

## Consequências

- **O serviço** revisa a confiança a cada turno, depois de registrar a reação e a moral, e escreve no log `confianca=NÍVEL/REGRA`.
- **Quem foi intimidado ou traído** retém o que é `PROFESSIONAL` e responde com a linha neutra: "Não vou falar disso."
- **Quem convive bem com o grupo** passa a poder contar as próprias confidências. Ainda não há segredos assim no pacote; a curadoria pode criá-los.

## Verificação

- **`tests/test_trust.py`:**
  - as regras;
  - a idempotência e a leitura;
  - o domínio D2: a convivência abre o segredo próprio e não o da casa; a desconfiança fecha o que é `PROFESSIONAL`;
  - a memória da conversa sem o assunto retido.
- **`tests/test_absence.py`:** o título retido conta sozinho.
- **`tests/test_morale.py`:** a intimidação no imperativo informal ("Fala logo ou vai se arrepender!").
- **No jogo (S1u):** Unger intimidado fica desconfiado e responde à pergunta sobre a arena com a linha neutra.
- **Bateria:** `desconfiado-retem-a-arena`. Salvanas desconfiado responde "Não vou falar disso." (3/3).
