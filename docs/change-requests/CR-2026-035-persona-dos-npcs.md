# CR-2026-035 — A persona dos NPCs

**Estado:** APROVADA (mantenedor, 2026-11-25: "Aprovar como proposta", D1 a D4 na opção recomendada).

**Origem:** a frente 2 pedida pelo mantenedor em 2026-11-24: cada NPC do jogo com "pelo menos um prompt para a IA seguir", além das regras de reputação, moral, reação e histórico. O teste da ADR-0147 no jogo (evidência S2i) mostrou três casos:
- **Lehtinan** tem SAB 6 no jogo. O nível rudimentar (ADR-0117) o fazia dizer "não entendo isso".
- **Hendak** tem a mesma SAB 6.
- **Salvanas** disse que não conhece os Ladrões das Sombras. A entrada estava como só de referência (`CANON_REFERENCE`) desde o primeiro lote, de 2026-11-09, e nenhum NPC a recebia.

**Relaciona-se com:** ADR-0117, ADR-0125, ADR-0147 (D2, correção de INT e SAB), CR-2026-033 (`speech`) e a etapa 3 (curadoria da Coroa).

## Mudança

1. **A persona curada (D1):**
   - a curadoria ganha o campo opcional `persona`, um texto de até 240 caracteres: temperamento, o que a pessoa quer e como trata estranhos;
   - **não nomeia ninguém:** uma letra maiúscula só abre uma frase. Uma curadoria com `persona` inválida não carrega;
   - ela entra no prompt logo depois do jeito de falar: "Seu jeito de ser: … Deixe isso aparecer no tom e nas escolhas da resposta; é só jeito: não é fato para contar, não muda o que você sabe e vale menos que a sua reação ao jogador nesta conversa.";
   - não entra no vocabulário nem nos fatos, e o validador continua igual;
   - **o `speech` diz como a pessoa fala; a `persona`, quem ela é.**
2. **INT e SAB corrigidos (D2),** pelo campo `mind` da ADR-0147, onde o número padrão do jogo contradiz o personagem:

   | NPC | Jogo (INT / SAB) | Curadoria |
   |---|---|---|
   | Lehtinan | 9 / 6 | 13 / 12 |
   | Hendak | 9 / 6 | 11 / 13 |
   | Madame Nin | 9 / 9 | 13 / 13 |
   | Bernard | 9 / 9 | 10 / 11 |
   | Yarin | 9 / 9 | 12 / 12 |

   Nenhum deles passa de 14: continuam no Ollama e só sobem ao Claude com reação amistosa. Nenhum fica mais no nível rudimentar.
3. **Os Ladrões das Sombras conhecidos em Athkatla (D3):**
   - `org:shadow-thieves` passa a conhecimento regional comum de Athkatla;
   - o título leva o nome em inglês, como as outras organizações: "Ladrões das Sombras (Shadow Thieves)";
   - **as camadas:**
     - **popular:** a guilda de ladrões, espiões e assassinos que domina o crime em Athkatla;
     - **informada:** age pela Costa da Espada e nasceu em Águas Profundas, de onde foi expulsa;
     - **estudada:** o acordo com os mercadores de Amn, de teor desconhecido;
   - as fontes continuam as mesmas: o manual do BG2 (pp. 27–28) e *Lands of Intrigue* (Livro Três, p. 17);
   - os testes que usavam essa entrada como exemplo de "só referência" passam a usar `event:tethyrian-exiles-return`.
4. **O primeiro lote (D4):** as 27 curadorias com persona. São 24 da Coroa de Cobre (os dois guardas com a mesma persona) e 3 da quest do diário (Gregor, Kalessia e Tamoko).
   - Os companheiros (Imoen, Jaheira e Minsc) ficam sem persona: o grupo futuro do mantenedor será outro.
   - **Duas personas foram ajustadas para não nomear ninguém:**
     - Gladiador: "respeita o líder dos escravos acima de todos";
     - Kalessia: "despreza esta terra e o seu povo; quer a guerra que a célula prepara".
   - Unger e Zaviera ficam para conferir no jogo.

## Rollback

Tirar o campo `persona` (e `mind`) das curadorias e a linha do prompt; devolver `org:shadow-thieves` a `CANON_REFERENCE`.

## Verificação

- **`tests/test_persona.py`:**
  - a persona é curta e não nomeia ninguém;
  - vai ao prompt, e não aparece sem ela;
  - as 27 curadorias carregam com persona;
  - uma persona inválida derruba a curadoria;
  - Lehtinan sai do nível rudimentar.
- Testes de conhecimento comum: os Ladrões das Sombras entram no que se sabe em Athkatla.
- **Bateria:** caso novo `salvanas-ladroes-das-sombras`.
- No jogo: evidência própria.
