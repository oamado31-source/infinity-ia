# ADR-0121 — Afirmações sobre outras pessoas: opinião passa, fato inventado não

**Estado:** APROVADA (decisões explícitas do mantenedor, 2026-11-10).
**Origem:** laboratório S1f.
**Problema:** o validador só conferia nomes desconhecidos e afirmações do NPC sobre si mesmo. Passaram, como se fossem fato, coisas sobre outras pessoas que não estavam no conhecimento de quem falava:
- "O taverneiro é Lehtinan" (Lehtinan é o dono);
- "Lehtinan? Cara duro, mas bem-humorado";
- "governam há décadas", vindo de quem não tinha a camada de estudo;
- "governa quem tem dinheiro".

**Relaciona-se com:** SPEC-004 (validação da fala), ADR-0117 (regra 3 e matriz Sabedoria/Inteligência), ADR-0119 (conhecimento restrito) e ADR-0120 (validador de origem). Não altera esses ADRs: acrescenta uma regra ao validador.
**Gate:** etapa 1, single player. Os testes sintéticos não comprovam a fala no jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-10.

1. **Opinião passa, fato não.** A reação ou o juízo do próprio NPC passam ("Cruel!", "acho que ele é duro", "não confio nele"). O que é dito como fato sobre outra pessoa ou grupo precisa estar no que o NPC sabe sobre ela.
   - **Marcas de opinião:** "acho", "pra mim", "na minha opinião", "não confio", "não gosto", "parece", "dizem que".
2. **Regras locais, sem segunda chamada ao modelo.** Padrões em português, conferidos contra os itens de FATOS, CONHECIMENTO GERAL e CONHECIMENTO RESTRITO que citam aquele nome, com uma tabela curta de sinônimos escrita por nós (dono ≈ proprietário; taverneiro ≈ gerente, administra, cuida, coordena; dinheiro ≈ riqueza, ouro…). A recusa vai para o log com o motivo:
   - `THIRD_PARTY:ROLE`: papel ou parentesco atribuído a um nome ("o taverneiro é Lehtinan");
   - `THIRD_PARTY:TRAIT`: traço afirmado sobre um nome ("Lehtinan é muito rico", "Lehtinan? Cara duro");
   - `THIRD_PARTY:NUMBER`:
     - número ou duração sobre um nome ("há décadas"), conferido contra o texto já filtrado pela camada de Sabedoria/Inteligência;
     - em primeira pessoa ("vivo aqui há 20 anos"), conferido contra os FATOS;
     - "há muito tempo" passa;
   - `THIRD_PARTY:GENERAL`: regra geral ("governa quem tem dinheiro"), que passa só quando algo que a pessoa sabe a sustenta. "A riqueza vale mais que tudo", de Amn, sustenta essa frase.
3. **Prompt:** a regra 3 passa a dizer que a opinião própria pode aparecer, dita como opinião, e que papel, traço, número, tempo ou regra geral sobre outra pessoa só valem se estiverem nas seções.
4. **Sem efeito no jogo:** a regra só aceita ou recusa falas; não altera dados, diálogos nem save.

## Consequências

- **Código:** `src/infinity_ai/dialogue/claims.py` (`third_party_claim`), chamado por `validate_reply`.
- **Testes:** `tests/test_third_party.py`, com os casos reais do S1f e as respostas já aprovadas, que continuam passando.

## Riscos e limites

- **Pronomes:** "ele é o dono" não é conferido, porque o validador não sabe de quem se fala.
- **Paráfrases:** frases fora dos padrões passam. A regra estreita a invenção, mas não prova a verdade.
- **Sinônimos:** a tabela é curta e pode recusar uma paráfrase correta com palavra nova. Nesse caso, o modelo tenta de novo e, se errar outra vez, entra a fala de reserva.
