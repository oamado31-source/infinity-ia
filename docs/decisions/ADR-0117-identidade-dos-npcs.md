# ADR-0117 — Identidade dos NPCs: quem são, o que fazem, onde vivem e por onde passaram

**Estado:** APROVADA (decisões explícitas do mantenedor, 2026-11-10).
**Origem:** teste S1e. Bernard, perguntado na caixa do jogo, disse ser "apenas um viajante": o prompt de um habitante não dizia quem ele é, e a Coroa de Cobre aparecia como "um lugar que você não sabe nomear".
**Relaciona-se com:** ADR-0115 (personalidade, PROPOSTA) e SPEC-006, que ganha a camada P0 "identidade"; ADR-0116 (caixa no jogo e habitantes); ADR-0059 (conhecimento legítimo); REQ-CANON-004 (dados do jogo fora do repositório).
**Gate:** etapa 1 (single player, ADR-0113); testes sintéticos não comprovam a fala no jogo.

## Contexto

A personalidade (SPEC-006) diz **como** o NPC fala, mas não **quem** ele é. Sem identidade, o modelo inventa ofício, origem e passado. O mantenedor quer que cada NPC saiba o que sabe sobre si mesmo (nome, ofício, onde vive, de onde veio, por onde passou) e responda só a partir disso, combinando identidade e personalidade.

## Alternativas consideradas

- **A — Deixar o modelo improvisar a partir do nome:** é a causa do problema; rejeitada.
- **B — Resumir as falas nativas do jogo:** mais rico, mas o resumo pode errar e o texto do jogo não pode entrar no repositório; fica para depois.
- **C — Dados do jogo + curadoria para NPCs oficiais, geração fechada para genéricos:** **selecionada.**

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-10.

1. **Precedência:** curadoria do mantenedor > dados do jogo > geração. Cada campo guarda a proveniência (`CURATED`, `GAME_DATA`, `GENERATED`).
2. **Dados do jogo (locais, fora do repositório):**
   - nome;
   - área onde o jogo coloca a criatura, e a região do pacote que a contém;
   - raça, gênero, classe e alinhamento da ficha (CRE);
   - o papel indicado pelo nome no jogo ("Guarda…", "Cliente…").
   O nome das áreas internas vem da curadoria provisória de nomes de lugar (texto nosso).
3. **Curadoria** (`knowledge/npcs/<npc>.pt_BR.json`, schema `infinity-ai.npc-identity-curation.v1`):
   - campos: ofício, origem e lugares do pacote, anos no lugar e até alguns fatos sobre si (texto nosso, ≤ 200 caracteres cada), com fonte;
   - **só vale com conferência** (`checked_by`, `checked_at`), e regiões fora do pacote invalidam o arquivo.
4. **Geração para genéricos** (`src/infinity_ai/personality/identity.py`):
   - determinística, com a semente da SPEC-006;
   - ofício de um vocabulário fechado por papel;
   - origem numa região do pacote, com peso maior para a própria região e as ancestrais;
   - tempo no lugar entre 1 e 40 anos, ou "nasceu aqui";
   - no máximo 2 regiões do pacote por onde passou.
   **Nunca** nomeia pessoas, família nem acontecimentos.
5. **Persistência** igual à da personalidade:
   - `CANONICAL` (criatura com script name) não recebe histórico gerado;
   - `CANDIDATE` recebe identidade temporária, estável por instância na cena e não gravada;
   - `VERIFIED` grava a identidade uma vez, no mesmo `NpcPersonalityAssigned`, e a reutiliza.
6. **Uso no diálogo:**
   - a identidade vira fatos `F` "SOBRE VOCÊ" (ids `identity:<npc>:<n>`) e entra na apresentação ("Você é Bernard, taverneiro da Coroa de Cobre, e está na Coroa de Cobre");
   - regra 8: sobre si mesmo, o NPC só afirma o que está nos fatos e desconversa sobre o resto;
   - a regra 3 passa a proibir acrescentar características, idades, números, aparência ou opiniões alheias;
   - nomes de lugar fora dos fatos continuam barrados pelo validador.
7. **O que o NPC sabe por quem é** (decisão do mantenedor, 2026-11-10): o NPC conhece o que é público na **terra natal** da identidade (região e sub-regiões, como `ORIGIN`) e **onde vive** (região e ancestrais, como `RESIDENCE`).
   - **Elegibilidade:** a mesma dos outros canais (`COMMON_REGIONAL`, gate `CANON_OK`, pin `MATCH`).
   - **Cálculo:** é feito na hora da fala e não é gravado, porque a identidade gerada pode ser temporária.
   - **INQUIRY:** o que ele contar a partir disso ensina os ouvintes, como qualquer outra entrada nomeada na fala.
   - **Motivo:** Bernard, que veio de Tethyr, deixa de inventar ("sol forte, vida movimentada") e passa a contar o que é público lá.
8. **Sabedoria e Inteligência definem a profundidade, não a quantidade** (decisões do mantenedor, 2026-11-10).
   - **O que não muda:** todo assunto que a pessoa sabe continua disponível.
   - **Sabedoria** (ficha CRE; 10 quando desconhecida): define até que nível ela entende cada assunto e como fala.
   - **Inteligência:** destrava o conhecimento estudado.
   - **Níveis de cada entrada** (`knowledge_layers`):
     - `POPULAR`: o que todo mundo sabe;
     - `INFORMED`: exige atenção, vivência ou ofício;
     - `STUDIED`: história, causas, política; exige estudo.
     São os fatos do resumo conferido, reescritos em camadas, **nunca fatos novos**. Sem camadas, a primeira frase do resumo é o núcleo popular e o resto é informado.

   | Camada (WIS) | Níveis | Fala e raciocínio |
   |---|---|---|
   | 1 rudimentar (≤ 6) | POPULAR, só a primeira frase | muito simples e curta; repete o que ouviu; "não entendo disso" |
   | 2 comum (7–10) | POPULAR | curta e concreta; liga à própria vida; admite que não sabe |
   | 3 atento (11–14) | + INFORMED | clara, com detalhe prático ou conselho; diz até onde sabe |
   | 4 perspicaz (15–17) | + STUDIED parcial, se INT ≥ 10 | elaborada; causas e consequências; separa o que sabe do que supõe |
   | 5 sábio (≥ 18) | + STUDIED completo, se INT ≥ 12 | profunda; quadro geral; pode devolver a pergunta; não especula |

   - **Inteligência sozinha:** INT ≥ 14 dá STUDIED parcial, e INT ≥ 17 dá completo em qualquer camada. Um estudioso de Sabedoria média conhece a história; um sábio iletrado entende as pessoas, mas não os livros.
   - **Conhecimento aprendido antes das camadas:** o registro guarda o resumo conferido. Se o pacote pinado tem o mesmo resumo, as camadas dele são usadas, porque reescrevem os mesmos fatos.
   - **Fonte do INQUIRY:** o que a pessoa repassa continua sendo só o que a fala nomeia.
   - **Faixas:** são ajuste de design, não regra de AD&D.
9. **Ajustes do teste de laboratório** (decisão do mantenedor, 2026-11-10):
   - **INQUIRY só com conteúdo:** uma entrada só conta como ouvida se a fala a nomeia **e** transmite parte do que a pessoa sabe dela (ao menos uma palavra de conteúdo, contando a pergunta do jogador como contexto). "Sou de Athkatla" não ensina Athkatla. Recusa: `NOT_CONVEYED`.
   - **Com as próprias palavras:** a regra 7 pede que o NPC diga a ideia do seu jeito, sem copiar o texto do fato.
   - **Sobre si:** a regra 8 ganha exemplo de desconversa, e o validador recusa afirmações de posse, cargo ou parentesco que não estejam nos fatos (`SELF_CLAIM`, como "a cidade me pertence").
   - **Alinhamento dos oficiais:** personagens oficiais (com script name, sem sorteio pela SPEC-006) usam o **alinhamento da ficha do jogo** como orientação de fala; nada é sorteado e nada muda no jogo.
10. **Sem efeito no jogo:** a identidade é dado narrativo; não altera ficha, alinhamento mecânico, diálogos nem save.

## Consequências

- Primeira curadoria: Bernard ("taverneiro da Coroa de Cobre"), **PROPOSED**, até a conferência do mantenedor.
- Testes: `tests/test_identity.py` (papéis, gerador, precedência, curadoria, persistência e diálogo) e ajustes em `tests/test_common_knowledge.py` e `tests/test_gamedata.py`.
- A SPEC-006 deixa de dizer que o gerador "não inventa biografia". Agora ele gera um histórico **mínimo e fechado**, por esta decisão.

## Evidências, riscos e hipóteses não verificadas

- Evidência de laboratório: S1f (a registrar).
- Risco: identidade gerada pode contradizer falas nativas do jogo para NPCs sem curadoria; mitigado pela precedência da curadoria e por `CANONICAL` sem geração.
- Risco: o modelo ainda pode acrescentar detalhes que o validador não detecta (só nomes são checados); mitigado pelas regras 3 e 8 e pelo teste no laboratório.
