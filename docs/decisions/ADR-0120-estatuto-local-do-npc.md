# ADR-0120 — Estatuto local do NPC: habitante, viajante e forasteiro

**Estado:** APROVADA (decisões explícitas do mantenedor, 2026-11-10).
**Origem:** laboratório S1f.
- **Lorde Jierdan:** o jogo o coloca na Coroa de Cobre, mas a ficha dele não é humanoide. O inventário não o conta como habitante, ele fica sem conhecimento comum e o modelo enrola: diz saber quem governa sem dizer quem, e diz "sou de aqui".
- **O Nobre:** afirmou "não sou de cá" sem base nos fatos.

**Relaciona-se com:** ADR-0114 (canais ORIGIN, RESIDENCE e INQUIRY), ADR-0116 (habitantes pelos dados do jogo), ADR-0117 (identidade e matriz de Sabedoria/Inteligência) e ADR-0119 (conhecimento relacional). Não altera esses ADRs: acrescenta uma camada.
**Gate:** etapa 1, single player. Os testes sintéticos não comprovam a fala no jogo.

## Contexto

Até aqui, todo NPC que o jogo coloca numa área de região do pacote era tratado como morador dela. Na prática, uma taverna mistura moradores, gente de passagem e estrangeiros, e cada um sabe coisas diferentes, às vezes opostas. O morador conhece o lugar. O estrangeiro não conhece o lugar, mas conhece a própria terra, que o morador não conhece.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-10.

1. **Três estatutos**, guardados na identidade (`standing`), com proveniência:

   | Estatuto | Lugar atual (a região onde está e as sub-regiões) | Terra natal |
   |---|---|---|
   | `HABITANTE` | o que a matriz de Sabedoria/Inteligência permite (como antes) | idem |
   | `VIAJANTE` (de passagem, do mesmo reino) | **só a camada POPULAR**, qualquer que seja a Sabedoria | o que a matriz permite |
   | `FORASTEIRO` (terra distante) | **nada**; só aprende perguntando (INQUIRY) | o que a matriz permite |

   - **Quem não é habitante:** a `RESIDENCE` que o jogo deu por colocação não conta. O que a pessoa ouviu por INQUIRY ou trouxe da terra natal vale inteiro.
2. **Precedência:** curadoria > geração > `HABITANTE` (colocado pelo jogo).
   - **Curadoria conferida `HABITANTE`:** vale mesmo para quem o filtro de humanoides do inventário deixou de fora, desde que o jogo o coloque na área.
   - **Valor inválido:** um `standing` fora dos três invalida o arquivo de curadoria.
3. **Genéricos por sorteio conforme o papel:**
   - **Semente:** a da SPEC-006, num fluxo próprio. Quem continua habitante mantém exatamente o ofício e a origem que já tinha.
   - **Chance de não ser habitante** (ajuste de design, não regra de AD&D): viajante pelo nome 100%, marinheiro 60%, cliente 30%, comerciante 30%, lutador 20%, gente do povo e camponês 5%. Guardas, trabalhadores, donos, nobres, mendigos e crianças: 0%.
   - **Entre os de fora:** 1/3 é forasteiro, se houver região do pacote fora do reino; os demais são viajantes.
   - **Origem coerente:**
     - viajante: uma região acima de onde está (Athkatla → Amn);
     - forasteiro: uma região fora da cadeia (Tethyr);
     - nenhum dos dois tem "anos aqui".
4. **Fala:**
   - **Fatos "SOBRE VOCÊ":**
     - habitante: "Você vive em Athkatla e está na Coroa de Cobre." (item 7);
     - viajante: "Você está de passagem por Athkatla e está agora na Coroa de Cobre." e "Você veio de Amn.";
     - forasteiro: "Você é de Tethyr, terra distante, e não conhece bem os costumes daqui."
   - **Apresentação no prompt:** a pessoa sabe se mora ali ou não.
5. **Validador** (`SELF_CLAIM`), só para pessoas encontradas no jogo:
   - "não sou daqui" ou "estou de passagem" vindo de habitante;
   - "sou daqui" ou "moro aqui" vindo de viajante ou forasteiro;
   - "nasci aqui" sem o fato "nasceu e cresceu aqui";
   - "sou de X" ou "vim de X" quando X não está nos fatos da pessoa;
   - "trabalho aqui", "trabalho para o dono" ou "sou empregado da casa" sem afiliação curada `STAFF` do lugar (ADR-0119). Isso foi acrescentado depois que, no S1f, o Campesino aceitou a sugestão da pergunta e disse que trabalhava na taverna.
6. **Primeira curadoria:** Lorde Jierdan (`npc:firkra01`), `HABITANTE`, "nobre de Athkatla". Conferida pelo mantenedor em 2026-11-10. Nada sobre a verdadeira natureza dele entra nos fatos.
7. **Ajustes do laboratório S1f** (decisões do mantenedor, 2026-11-10).
   - **Onde vive não é onde está:**
     - **O problema:** o fato "Você vive na Coroa de Cobre" levava genéricos a dizer que moram ou trabalham na taverna.
     - **Habitante:** passa a ouvir "Você vive em Athkatla e está na Coroa de Cobre".
     - **Viajante e forasteiro:** "Você está de passagem por Athkatla e está agora na Coroa de Cobre".
     - **Vínculo com o lugar** (morar ou trabalhar ali) só vem de afiliação curada (ADR-0119).
   - **Nomes comuns do lugar:** onde a pessoa está, "taverna", "estalagem", "casa", "local" ou "lugar" valem pelo PLACE da área, "cidade" pela cidade e "reino", "país" ou "nação" pelo reino.
   - **O nome pode vir da pergunta:** uma resposta a "quem é o dono dessa taverna?" passa a ensinar a relação, desde que a própria fala traga conteúdo dela ("É Lehtinan."). Um "não sei" não ensina nada. Para acrescentar uma entrada que o modelo não declarou, o nome continua precisando estar na fala.
8. **Exemplos no prompt** (decisão do mantenedor após o S1f, 2026-11-10): as regras 2, 7 e 8 voltam a ter exemplos fora do mundo do jogo, porque sem eles alguns NPCs copiaram o texto da camada ou recitaram a lista de fatos ("Sou humano, vivo em Athkatla e estou aqui na Coroa de Cobre"). A regra 8 também pede para usar só o fato que responde à pergunta. Os nomes inventados dos exemplos, como "Vila Alta", seguem barrados pelo validador se forem copiados.
9. **Sem efeito no jogo:** o estatuto é dado narrativo; não altera ficha, diálogos nem save.

## Consequências

- **Código:**
  - `personality/identity.py`: `standing`, `AWAY_CHANCE` e `popular_only`;
  - `memory/common_knowledge.py`: `identity_knowledge` devolve o conhecimento completo e o só popular;
  - `MemoryStore.known_canon`/`recall_common`: novo filtro `exclude_basis`;
  - `dialogue/context.py`, `engine.py` e `validate.py`;
  - `tools/windows-lab/dialogue_service.py`: o log ganha `estatuto=`.
- **Testes:**
  - `tests/test_identity.py`: `StandingTests` e `OriginClaimTests`;
  - `tests/test_common_knowledge.py`: residência ignorada para quem é de passagem.

## Evidências, riscos e hipóteses não verificadas

- **Evidência:** S1f, teste do estatuto a registrar.
- **Risco — faixas:** as chances do sorteio são ajuste de design e podem precisar de calibração no jogo.
- **Risco — reinos:** com o pacote atual (Amn, Athkatla e Tethyr), "mesmo reino" é Amn e "terra distante" é Tethyr. Regiões novas no pacote mudam as origens possíveis.
- **Hipótese:** o validador de origem cobre as formas mais comuns ("sou de", "vim de", "não sou daqui"). Paráfrases podem escapar.
