# CR-2026-017 — Pendências do teste real dos lotes A e A2

**Status:** APPROVED (mantenedor, 2026-11-15, "corrigir as pendências")  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-15

## Motivo e contexto

A evidência S1k (testes com Bernard em 2026-11-15) deixou quatro pendências. Este CR resolve três delas e registra a decisão sobre a quarta.

## DEC/ADR/SPEC/REQ afetados

- **ADR-0125 e ADR-0126:** "uma vez por pessoa por sessão" passa a distinguir as aberturas do jogo. O sentido da regra não muda.
- **SPEC-004 (validação):** um verificador novo, no estilo dos CR-2026-006 e CR-2026-008.
- **SPEC-008 (aquisição) e CR-2026-016:** a regra de menção passa a aceitar singular e plural.
- **REQ-REL-012:** o pin continua explícito; o serviço só avisa.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **A reação e a moral valem por abertura do jogo.**
   - **Problema:** o contador de sessão da caixa volta a 0 quando o jogo é reaberto, e o log é truncado, não recriado. Uma reação de uma abertura anterior do mesmo save era reaproveitada (ameaçador para sempre).
   - **Correção:** o serviço lê a hora de início do processo `Baldur.exe` pela mesma conexão do log (`SshLogSource.launch`) e passa esse valor a `reaction_for` e a `morale_for`.
   - **Registro:** o valor entra no evento (`launch`), na semente e na chave de idempotência.
   - **Compatibilidade:** eventos antigos, sem `launch`, continuam valendo só quando não há abertura conhecida, como nos testes sintéticos.
2. **Detalhe sem respaldo: metais.**
   - **Problema:** perguntado sobre as moedas, o modelo disse que a prata é comum e o ouro raro, contra o item que tinha.
   - **Correção:** um metal citado pelo NPC (ouro, prata, cobre, platina, electro, mithral, adamantina) precisa estar no que ele sabe ou no que o jogador disse. Senão a resposta é recusada com `UNBACKED_DETAIL:<metal>`, e a nova tentativa recebe uma dica em português.
3. **Singular e plural na menção.**
   - **Regra:** "moeda" nomeia "Moedas amnianas" e "Favela" nomeia "Favelas". Só para palavras com mais de 4 letras, para "sei" não nomear "Seis".
   - **Onde vale:** na recuperação pela pergunta (CR-2026-016), no aprendizado em conversa e na ausência tipada, que usam as mesmas funções (`title_words`, `spoken_words`).
4. **Aviso de pin defasado.** Quando o ramo atual está com uma revisão antiga do pacote (`REVISION_CHANGED`) ou sem pin, o serviço avisa uma vez por ramo, com o comando `pin_canon_pack.py`. O pin continua sendo um ato explícito.

## Decisão: o núcleo popular calculado não passa adiante por conversa

- **O caso:** o núcleo popular das cidades vizinhas (CR-2026-015) e o das viagens (CR-2026-012) são calculados quando a pessoa fala e nunca gravados. O aprendizado em conversa (INQUIRY) só repassa o que está gravado, então Bernard "não sabe" Murann para quem o ouve (`SPEAKER_DOES_NOT_KNOW`).
- **Decisão: manter.** Quem ouve não deve ganhar de segunda mão mais do que quem fala sabe. A gravação atual de conhecimento não tem profundidade: repassar o item daria a quem ouve a entrada inteira, inclusive as camadas INFORMED e STUDIED.
- **Revisão futura:** junto com a guarda de conhecimento por NPC com profundidade e estado epistêmico da SPEC-008 (`NpcKnowledgeHolding`).

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Abertura desconhecida:** se a leitura da abertura falhar (`launch` vazio), vale o comportamento de antes.
- **Falso positivo do verificador de metais:** "cobre" também é verbo ("ele cobre a mesa"). O verificador aceita o que está nas seções e na fala do jogador. Um falso positivo custa uma nova tentativa, nunca um fato.
- **Singular e plural:** pode fazer uma palavra comum casar com um título. O limite de 4 letras e a regra de títulos sem palavras comuns (lote A) contêm isso.
- **Privacidade:** nada do texto do jogador é gravado. O valor `launch` é só um horário de processo.

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** reverter cada item de forma independente. O `launch` é um parâmetro opcional com padrão vazio.
