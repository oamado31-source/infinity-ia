# ADR-0134 — Marcos de quest: leitura permitida e significado curado

**Estado:** APROVADA (mantenedor, 2026-11-17: "Aprovar como proposta", decisões D1 a D5 como propostas).

**Origem:** a ADR-0133 deixou `ÍNTIMO` e os segredos da casa ou de terceiros para os "marcos de quest curados". As ADR-0095 e ADR-0096 aprovaram a arquitetura (leitura só com lista permitida e significado curado por build), mas nada estava implementado: o serviço não lia nada do andamento das quests.

**Relaciona-se com:**
- ADR-0095 (observação somente leitura, com lista permitida e proteção contra spoilers);
- ADR-0096 (catálogo semântico curado por build);
- ADR-0133 (confiança por evento; esta decisão a refina sem edição);
- ADR-0132 (dados do jogo só em arquivo local, fora do repositório);
- ADR-0097 (reconciliação do mundo com a quest, fora desta fatia).

**Gate:** etapa 1, single player. Nada é escrito no estado do jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-17.

1. **Uma quest na primeira fatia (D1):** os escravos da arena da Coroa de Cobre (Hendak).
2. **Catálogo local, por build, fora do repositório** (`~/.infinity-ai/quests/catalog.json`, esquema `infinity-ai.quest-catalog.v1`):
   - cada `probe_id` opaco aponta para uma variável global do jogo (D3: só `GLOBAL` nesta fatia);
   - cada marco (`semantic_id`, como `quest:coronet-slaves:RESOLVED`) é uma regra com predicados `eq`, `in` ou `ge`, e um grupo exclusivo opcional;
   - tem a impressão da build, a revisão e o estado `CURATED`, `REVIEW_PENDING` ou `REVOKED`.
   - Os nomes das variáveis são dados do jogo e contam como spoiler (ADR-0095, item 6): não entram no repositório, nos prompts, nos logs nem nos eventos.
3. **A leitura é da caixa do jogo, só no envio da pergunta:**
   - o serviço grava em `override/INFAIQST.lua` a lista permitida (só os pares `probe_id` e nome do catálogo);
   - a caixa relê a lista a cada abertura e, ao enviar, procura cada nome na tabela de globais (`EEex_Variable_Find`, que não cria nada) e manda `probes: {probe_id: valor ou null}`;
   - `null` quer dizer que a variável não existe, nunca 0. Não há varredura, leitura contínua nem escrita.
4. **O avaliador é puro e determinístico** (`quests/milestones.py`):
   - falta de probe: `UNKNOWN`, nunca "falso";
   - dois marcos do mesmo grupo exclusivo ao mesmo tempo: `AMBIGUOUS`, nada é registrado;
   - build diferente: `BLOCKED_BUILD`; catálogo não curado: `BLOCKED_MAPPING`.
5. **Um marco `MAPPED` vira o evento `QuestMilestoneObserved`, uma vez por ramo,** com o `semantic_id`, a revisão e o digest do catálogo e os `probe_id` usados, sem valores. Save antigo recarregado abre outro ramo, que não vê o marco. Se a leitura voltar atrás no mesmo ramo, o marco fica; o log avisa (`marco_regrediu`).
6. **A confiança ganha a regra `MILESTONE`** (`personality/trust.py`):
   - a ficha do NPC diz o nível que cada marco dá (`milestones: [{"milestone": ..., "trust": ...}]`, com `INTIMO`, `CONFIANTE` ou `DESCONFIADO`);
   - a confiança vinda de marco não é `own_only`: abre também os segredos da casa ou de terceiros (ADR-0133, D2);
   - os eventos contam na ordem em que foram gravados, e o último decisivo vence. Um marco tira alguém de `DESCONFIADO` (D5); uma coerção depois dele volta a deixá-lo desconfiado.
7. **Efeitos curados (D2):**
   - Hendak: `quest:coronet-slaves:RESOLVED` → `INTIMO`;
   - a equipe da arena (Lehtinan, o tratador das feras, o anunciador, a recepcionista da arena e os três guardas): o mesmo marco → `DESCONFIADO`;
   - Bernard, a cafetina e a acompanhante, que são da taverna e da casa, não mudam.
8. **O significado é provado no jogo antes de valer (D4):** o catálogo começa `REVIEW_PENDING`. O mantenedor joga a quest no laboratório, o serviço (`--watch-probes`) mostra os valores no Mac a cada pergunta, e só depois da confirmação dos momentos o catálogo vira `CURATED`.
9. **Fora desta decisão:** o mundo mudar por causa da quest (Hendak dono da taverna, a arena fechada, as falas de Hendak como escravo), que é a ADR-0097; outras quests; as variáveis da área; o multiplayer.

## Consequências

- **O serviço** registra os marcos do ramo a cada pergunta e escreve `marcos=[…]` no log, só com os ids semânticos.
- **A caixa do jogo** passa a ler variáveis globais, só as da lista e sem escrever. O cabeçalho do módulo e os testes estáticos registram isso.
- **A lista é lida na abertura do jogo:** a primeira instalação do `INFAIQST.lua` pede reiniciar o jogo, e no laboratório (S1v) a caixa também não releu a lista reescrita com o jogo aberto. Trocar o catálogo pede reabrir o jogo.

## Verificação

- **`tests/test_milestones.py`:**
  - o catálogo (validação estrita);
  - o avaliador (`UNKNOWN`, `AMBIGUOUS`, as builds e o catálogo pendente);
  - o evento por ramo, sem valores, e a regressão que não desfaz;
  - a regra `MILESTONE`, a D5 e o segredo da casa aberto pelo marco;
  - as fichas.
- **`tests/test_talk.py`:**
  - a leitura dos probes no pedido;
  - o arquivo da lista, sem injeção;
  - a caixa rodando em Lua: lê só os nomes da lista, e ausente vira `null`;
  - nenhuma escrita de variável.
- **No jogo (S1v):** a caixa leu só a lista; a variável ausente veio `null` em todas as leituras; uma existente (o capítulo) veio com valor. A curadoria dos momentos da quest de Hendak (D4) segue pendente, e o catálogo fica `REVIEW_PENDING`.
