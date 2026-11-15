# Plano de implementação — SPEC-009

1. **Taxonomia de sigilo:** classes do ADR-0131 aprovadas em 2026-11-15. Acrescentar o campo opcional ao schema do cânone por migração versionada. Item sem classe segue a regra atual.
2. **Decisão por item** (`dialogue/disclosure.py`, nome candidato):
   - a função pura recebe os itens elegíveis do NPC (a projeção da SPEC-008), a classe, a disposição, a confiança, a moral e a finalidade;
   - devolve `ALLOW_*`, `WITHHOLD` ou `UNKNOWN` com `reason_code`;
   - primeira versão com política neutra (confiança `NEUTRO` para todos).
3. **Pacote de evidências:**
   - o contexto do modelo passa a ser montado só com os itens liberados e a profundidade decidida;
   - o formato da resposta continua `speech`, `used_facts` e `unknown` (`dialogue/llm.py`);
   - o validador atual (`dialogue/validate.py`, `claims.py`) confere contra os IDs do pacote.
4. **Ausência tipada:** modelos determinísticos de fala para `NOT_KNOWN`, `NOT_DEFINED` e `WITHHELD`, usados quando não há item liberado ou quando a validação falha.
5. **Compatibilidade:**
   - testes que fixam o comportamento atual dos ADR-0125/0126 para itens sem classe;
   - depois, os casos novos (amistoso não revela confidência; `YIELD` não libera segredo de classe protegida).
6. **Confiança dinâmica** (fase 4b, depois do primeiro corte): estados qualitativos direcionais por evento, idempotentes, com revisão (ADR-0101).
7. **Validação:**
   - testes sintéticos dos critérios de aceite;
   - bateria de diálogo, com casos novos de recusa sem vazamento e de injeção;
   - laboratório na campanha `lab-s1f`, com Lehtinan (a arena como item de teste depois da curadoria) e Bernard.
