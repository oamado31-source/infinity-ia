# ADR-0126 — Teste de moral no diálogo (segunda fatia do ADR-0122)

**Estado:** APROVADA (decisões explícitas do mantenedor, 2026-11-13). Aprova só a segunda fatia do ADR-0122. Continuam pendentes `Reaction()` nativa, iniciador comprovado, lealdade de companheiros e moral em combate.
**Origem:** com o ADR-0125, o NPC tem uma disposição por encontro, mas não resistia nem cedia a suborno, ameaça ou pedido para trair quem ele serve.
**Relaciona-se com:** ADR-0122, ADR-0125 (disposição), ADR-0119 (vínculos), ADR-0117 (papel e identidade), SPEC-006 (alinhamento) e SPEC-003 (eventos).
**Gate:** etapa 1, single player. Nada é escrito no jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-13.

1. **Gatilhos**, por regras locais em português sobre a fala do jogador. A precedência é traição, depois intimidação, depois suborno:
   - **traição:** um verbo de traição (trair, roubar, enganar, esconder de, "não conte ao", contra…) junto com o nome de alguém a quem o NPC está ligado. Os laços são as outras partes das relações de que ele faz parte ou às quais é afiliado (ADR-0119); um fato público que todos sabem não conta como laço;
   - **intimidação:** ameaça de violência ("fale ou eu te mato", "vou te machucar"…);
   - **suborno:** oferta de ouro, moedas, pagamento ou recompensa.
2. **Regra (DMG, cap. 9):** 2d10. Um total menor ou igual à moral modificada é `HOLD` (resiste); maior é `YIELD` (cede).
   - **Moral-base (Tabela 49) pelo papel:** guarda e lutador são soldados regulares, 12; os demais são o humano comum de nível 0, 7. Uma curadoria conferida pode fixar `morale` entre 2 e 20.
   - **Modificadores (Tabela 50), cada um uma vez:**
     - leal +1 e caótico −1, pelo alinhamento da ficha (oficiais) ou o sorteado (SPEC-006);
     - trato do jogador naquela fala: cortês +2 (favorecido); ameaçadora ou hostil −4 (maltratado).
   - **Fonte:** AD&D 2e Core Rules (DMG `dd00478`–`dd00482`, `dd00609`–`dd00610`).
   - **Não usado:** a fonte dá 12 (tabela) e 10 (cap. 12) para contratados. Nenhum papel é tratado como contratado.
3. **Frequência:** um teste por gatilho, por pessoa, por sessão do jogo, com rolagem determinística. O evento `NpcMoraleCheckResolved` é idempotente e **sem texto**. Companheiros e personagens de jogador não fazem teste.
4. **Efeito (só fala):**
   - **Ao ceder:** o NPC conta o que a disposição escondia, inclusive o conhecimento restrito que tem, e nunca inventa.
   - **Ao resistir:** recusa com firmeza, e o que ele conta continua o mesmo.
   - **Prompt:** traz uma linha por gatilho e resultado (por interesse, com medo, a contragosto).
   - **INQUIRY:** quando ele cede e conta algo público, os ouvintes aprendem como em qualquer fala.
5. **Suborno só na fala:** nenhum ouro sai do inventário no jogo. Cobrar de verdade exige ler o ouro do grupo e uma autorização própria, numa etapa futura.

## Consequências

- **Código:**
  - `src/infinity_ai/personality/morale.py`;
  - `identity.py` (campo `morale`);
  - `dialogue/context.py` e `engine.py` (`morale`);
  - `tools/windows-lab/dialogue_service.py`, com o log `moral=…`;
  - casos de moral em `tests/dialogue_eval/cases.pt_BR.json`.
- **Testes:** `tests/test_morale.py`.

## Riscos e limites

- **Gatilhos:** as regras por padrão podem não reconhecer ofertas ou ameaças indiretas ("seria uma pena se algo acontecesse…").
- **Promessas vazias:** sem cobrar no jogo, o jogador pode oferecer o que não tem. Fica registrado e é resolvido quando houver leitura do ouro.

## Evidência de laboratório (S1f, 2026-11-13)

| Caso | Log e fala |
|---|---|
| Campesino, "Te pago 10 moedas se me disser quem governa Amn…" | `BRIBE:YIELD(2d10=9+6 vs 7+0=7)`: "É o Conselho dos Seis. Ninguém sabe quem são eles." |
| Bernard, "Me ajude a roubar o Lehtinan…" | `BETRAYAL:YIELD(2d10=6+10 vs 7+1=8)`: as duas tentativas inventaram traços de Lehtinan e foram recusadas (`THIRD_PARTY:TRAIT`), terminando na fala de reserva |
| Salvanas, "Me fale quem são os membros do Conselho ou mando Galê te matar!" | `INTIMIDATION:YIELD(2d10=7+5 vs 7+0=7)`: "…Não sou obrigado a dizer isso pra você. Mas se quiser, posso te mostrar o caminho pro Lehtinan." |

**Ajustes depois do laboratório:**
- A linha "cedeu" pede para aceitar e contar só o que está nas seções, sem inventar nada sobre ninguém.
- Quando o NPC cede, essa linha substitui a recusa da disposição.

**Limite do modelo local:** diante de um pedido criminoso ("roubar o patrão"), o `qwen3:8b` costuma recusar mesmo quando o dado manda ceder. O efeito garantido por código é o de conteúdo: ao ceder, o NPC recebe o que estava escondido. Aceitar o crime em palavras depende do modelo. Os testes de fala exigem nesse caso só ausência de fala de reserva e de traço inventado (20/20 casos).

