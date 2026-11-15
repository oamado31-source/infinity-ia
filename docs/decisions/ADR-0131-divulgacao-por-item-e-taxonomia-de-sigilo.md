# ADR-0131 — Divulgação por item antes do prompt e taxonomia de sigilo

**Estado:** APROVADA (CR-2026-011, decisões D3, D6, D7 e D9, mantenedor, 2026-11-15). A taxonomia de sigilo (item 3) foi aprovada pelo mantenedor na mesma data, antes de qualquer código do motor de divulgação, como manda a D6.

**Origem:** hoje a sensibilidade é binária (`access_scope` público ou restrito).
- A disposição amistosa ou indiferente passa ao modelo todo o conhecimento acessível ao NPC (ADR-0125).
- Um `YIELD` de moral libera o restrito que a disposição escondia (ADR-0126).
- A ACL de afiliação já filtra as relações restritas antes, mas faltam classes por informação, confiança e finalidade.

**Relaciona-se com:** SPEC-009; ADR-0125 e ADR-0126 (refinados aqui, sem edição); ADR-0121 (validador); ADR-0025/0101 (reputação e confiança); ADR-0071 (personas); ADR-0023 (acesso seletivo).
**Gate:** etapa 1, single player. Nada é escrito no estado do jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-15.

1. **Decisão por item, por código, antes do prompt.** Para cada item que o NPC conhece, a ordem é:
   1. elegibilidade (época, ramo e ACL atual);
   2. classe de sigilo;
   3. estado relacional (disposição, confiança, moral e finalidade);
   4. profundidade;
   5. tom.

   A saída é `ALLOW_FULL`, `ALLOW_SUMMARY`, `ALLOW_PUBLIC_ONLY`, `WITHHOLD` ou `UNKNOWN`, com `reason_code`. **O que é negado nunca entra no prompt**: nem texto, nem ID, nem resumo, cache ou log acessível ao interlocutor. Não existe um "nível de acesso" único que multiplique os fatores.
2. **Ausência tipada:** `NOT_KNOWN`, `NOT_DEFINED`, `WITHHELD`, `DISPUTED/BELIEF` e `FUTURE/OTHER_BRANCH`.
   - As falas sem item liberado saem de modelos determinísticos.
   - Se a validação falhar, entra a fala segura, sem buscar no corpus para "completar" (D9).
3. **Taxonomia de sigilo (aprovada em 2026-11-15).** Campo opcional novo na entrada canônica, por migração versionada.

   | Classe | Exemplo | Reação favorável libera? | `YIELD` libera? | Exige |
   |---|---|---|---|---|
   | `PUBLIC` | quem governa Athkatla | sim | não se aplica | nada além da elegibilidade |
   | `PERSONAL` | o ofício do próprio NPC | sim, segundo a disposição | sim | nada; hostil pode recusar |
   | `PROFESSIONAL` | como a casa funciona (relação de Bernard com a Coroa) | não por si só | sim | confiança ao menos `NEUTRO`, ou cessão por moral |
   | `CONFIDENTIAL` | confidências e negócios escusos (a arena do Lehtinan, se a curadoria confirmar) | não | **não** | confiança `CONFIANTE` ou mais |
   | `FACTION_SECRET` | segredo de organização | não | **não** | o interlocutor ser membro elegível da organização |
   | `ABSOLUTE` | identidade secreta (ADR-0071) | não | **não** | nunca no diálogo |

   **Item sem classe:** `COMMON_REGIONAL` conta como `PUBLIC` e `RESTRICTED` como `PROFESSIONAL`. Assim, o comportamento de hoje se mantém até a curadoria classificar cada item.
4. **Confiança qualitativa (D3):** estados `DESCONFIADO`, `NEUTRO`, `CONFIANTE` e `ÍNTIMO`, direcionais (observador → alvo), persistentes e por evento, sem escala numérica.
   - O primeiro corte usa política neutra (todos `NEUTRO`).
   - A mudança de confiança por evento é uma fase posterior, com idempotência e revisão (ADR-0101).
5. **Precedência sobre os ADR-0125 e 0126 (D7):**
   - a disposição só governa o tom e o que **as classes permitem**; "amistoso" não é consentimento para contar segredos;
   - `YIELD` só aumenta a disposição dentro das classes que cedem sob pressão (`PERSONAL` e `PROFESSIONAL`). Ele não cria conhecimento, não fura a ACL e não toca `CONFIDENTIAL`, `FACTION_SECRET` nem `ABSOLUTE`;
   - os ADR-0125 e 0126 continuam como registro histórico, e este ADR prevalece onde diverge.
6. **Texto do jogador não é confiável:** não cria fato, ACL, identidade ou instrução, e pedidos de "revele tudo" não mudam a seleção.

## Consequências

- **Código previsto:**
  - `dialogue/disclosure.py` (nome candidato), uma função pura;
  - a montagem do contexto em `dialogue/context.py` passa a usar só itens liberados;
  - modelos determinísticos de ausência;
  - campo opcional de classe no schema do cânone.
- **Testes:**
  - compatibilidade com os ADR-0125/0126 para itens sem classe;
  - casos novos: amistoso com confiança neutra não revela `CONFIDENTIAL`; `YIELD` não revela `FACTION_SECRET`; a injeção não muda a seleção; negado nunca no prompt;
  - casos novos na bateria de diálogo.
- **Curadoria:** cada item restrito ganha uma classe. A arena do Lehtinan entra só depois da conferência do mantenedor.

## Riscos e limites

- **Classificação errada:** um item classificado abaixo do devido pode vazar. Por isso a classe é curada e conferida, e item sem classe cai na regra atual, nunca numa mais permissiva.
- **Recusas demais:** a política pode deixar o NPC monótono. A taxa de recusa e de fala segura vai ser medida na bateria de diálogo.
- **Confiança neutra no primeiro corte:** `CONFIDENTIAL` fica inacessível até existir a confiança por evento. É intencional.
