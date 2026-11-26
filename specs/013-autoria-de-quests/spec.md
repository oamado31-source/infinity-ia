# SPEC-013 — Autoria de quests: as regras, o verificador e o agente

**Status:** APROVADA (mantenedor, 2026-11-25: "Aprovar como proposta", D1 a D4 na opção recomendada).
**Rastreabilidade:** SPEC-011 (quests narrativas); ADR-0134 (marcos); ADR-0136 (gateway, portão P3); ADR-0137 (fichas); ADR-0138 (presença); ADR-0139 (relógio e chegada); ADR-0140 (contagem e derrota); ADR-0141 (fichas e inventário); ADR-0142 (combate); ADR-0143 (nascer juntos); ADR-0144 (chamado e saída); ADR-0145 (chegada preparada); ADR-0146 (área nossa e passagens); CR-2026-030, CR-2026-032, CR-2026-033, CR-2026-035; ADR-0147 (camadas das falas); ADR-0148 (quem entra pela porta e a recompensa); ADR-0095 (spoilers).

## Objetivo

Reunir num lugar só tudo o que uma quest do Infinity pode ter, com os limites de cada parte. Assim uma quest nova pode ser escrita, verificada e levada ao laboratório por um agente que segue estas regras, sempre com a aprovação do mantenedor.

**Invariantes (de SPEC-011 e das ADRs acima):**
- o código decide oferta, aceite, passos, derrota, chegada e entrega; o modelo só dá voz ao fato curado do turno;
- a quest nunca toca a quest original do jogo nem lê variáveis dele;
- o que escreve no jogo passa pelo gateway: só criaturas nossas, áreas nossas e operações de modelo fixo, com recibo;
- os textos da quest são do projeto. Dados do jogo e fichas de criatura nunca vão ao repositório (CR-2026-030, REQ-CANON-004).

## 1. A anatomia de uma quest

Arquivo `knowledge/quests/<quest_id>.pt_BR.json`, esquema `infinity-ai.narrative-quest.v1`.

| Campo | O que é | Regras |
|---|---|---|
| `quest_id` | identificador | minúsculas, números e hífen, até 48 |
| `title` | nome da quest | até 80 caracteres |
| `curation` | conferência | `status: CHECKED`, `checked_by`, `checked_at`: sem isso a quest não carrega |
| `milestone` | marco do fim | sempre `quest:<quest_id>:RESOLVED` (ADR-0134) |
| `area` | área principal | opcional; a quest pode passar por várias áreas |
| `giver` | quem dá a quest | ver §2 |
| `call` | chamado de quem dá | opcional; ver §2 |
| `steps` | os passos | pelo menos um; ver §3 |
| `turn_in` | a entrega | ver §4 |
| `presence` | criaturas nossas | opcional; ver §5 |
| `passages` | passagens | opcional; ver §6 |

## 2. Quem dá a quest

- **`giver.npc_id`:** uma pessoa com curadoria conferida (`knowledge/npcs`). **Não pode ter passo de conversa:** a entrega volta a ela.
- **Quem dá pode ser uma pessoa nossa (ADR-0148):** `npc:infai_<nome>`, com uma presença `from: "START"` de mesmo nome na área dela, para estar no mundo antes da oferta. Com `x`, `y` (a porta) e `walk_to` (o balcão), ela entra pela porta e anda até o ponto. O verificador avisa (`GIVER_PRESENCE`) se faltar a presença.
- **`offer_cues`:** palavras que fazem a pessoa oferecer a quest. `*` marca começo de palavra (`ajud*`).
- **`offer_fact`:** o que ela conta ao oferecer, até 400 caracteres. Deve **terminar perguntando** se o grupo aceita (lição de Garoll).
  - o pedido ao grupo vem como desejo ("você quer que o grupo …") ou no fecho "Pergunte se o grupo aceita …", **nunca como ordem** ("Peça que o grupo …"): no laboratório, Doran repetiu a ordem palavra por palavra. O verificador avisa (`FACT_ORDER`).
- **`accept_cues`:** as formas de aceitar.
  - Precisam ser **amplas:** "aceito", "pode deixar", "vamos ajudar", "podemos ir", "sim", "claro"…
  - A lista curta foi o maior problema no diário; o verificador avisa abaixo de 4 formas.
  - Só valem depois da oferta.
- **`waiting_fact`:** o que ela diz enquanto o grupo não voltou.
- **`accept_journal`:** a linha de diário do aceite, até 200 caracteres.
- **`call` (ADR-0144):**
  - `{script_name, area, strref, every}`: uma legenda sobre a cabeça de quem dá, com uma frase **que já existe no jogo** (`strref` do `dialog.tlk`);
  - de uma pessoa do jogo, ou de uma criatura nossa que seja presença da mesma quest (ADR-0148);
  - repetida a cada `every` (300 a 108000; 4500 é uma hora de jogo);
  - só exibe texto e nunca usa voz.

## 3. Os passos

Cada passo tem `step_id`, `journal` (até 200 caracteres) e, opcionalmente, `after`: os passos que vêm antes. **`after` só cita passos anteriores na lista**, então a ordem nunca dá volta.

| Tipo | Campos | Quando se cumpre |
|---|---|---|
| **conversa** | `npc_id`, `cues`, `fact` (até 400), `area` opcional | o jogador fala com a pessoa sobre o assunto, com a quest aceita |
| **chegada** | `arrive: {area, night}` | o grupo entra na área (de noite, se `night`) |
| **derrota** | `defeated: {presence}` | a contagem da presença cai a zero (ADR-0140) |

- **Duas conversas com a mesma pessoa:** a segunda precisa ter a primeira em `after`, direto ou não, para só uma ficar aberta de cada vez (ADR-0144).
- **O fato de um passo:**
  - é escrito **como fala direta da pessoa**, e não como resumo: Gregor só passou a contar o esconderijo quando o fato virou fala;
  - nunca chega ao prompt antes de a quest ser aceita;
  - quando muda nesta fala, vem marcado "(agora)" e precisa aparecer na resposta (CR-2026-033).
- **Noite:** 21:00 às 05:59 de jogo (ADR-0139). Se uma presença só aparece à noite, a quest deve dizer isso ao jogador.

## 4. A entrega

- **`turn_in`:** `cues`, `fact` e `journal`. Acontece com quem deu a quest, com todos os passos feitos.
- **A recompensa (ADR-0148):** `turn_in.reward: {gold, xp}`, ouro de 0 a 10.000 e XP de 0 a 50.000, ao menos um. É paga uma vez, com a quest resolvida, pelas ações do próprio jogo; sem a confirmação do ouro, fica retida e nunca é reenviada. O `xp` é o total da equipe, repartido pelo próprio jogo entre os personagens, como numa quest do jogo. Itens ainda não existem como recompensa.
- **O marco** (`milestone`) muda a confiança de quem a curadoria disser, no campo `milestones` da curadoria (ADR-0134): por exemplo, Garoll fica `INTIMO`.

## 5. Presenças (criaturas nossas no mundo)

| Campo | Regra |
|---|---|
| `presence_id` | identificador, único na quest |
| `cre` | **só criatura nossa:** `IA` e até 6 letras ou números, instalada no laboratório (`build_templates.py`, com o jogo fechado) |
| `name` | nome de script `INFAI_…`, único |
| `area` | área do jogo ou área nossa |
| `from` / `until` | de `START` (desde o começo, antes da oferta; ADR-0148), de `ACCEPTED` ou de um passo, até `RESOLVED` ou um passo; pontos diferentes |
| `walk_to` | `{x, y}`: ao nascer em `x`, `y`, anda até esse ponto e fica (ADR-0148); só com `x`, `y` |
| `when` | `ANY` ou `NIGHT`; à noite, some ao amanhecer |
| `copies` | de 1 a 8, todas no mesmo pedido, confirmadas pela soma (ADR-0143) |
| `hostile_from` | a partir de quando ficam hostis (ADR-0142) |
| `leave` | `DESPAWN` (somem) ou `ESCAPE` (vão embora pela saída mais perto, ADR-0144) |
| `x`, `y`, `facing` | ponto e direção, opcionais |

- **Chegada preparada (ADR-0145):** quem deve estar no lugar já está lá quando o grupo chega, criado ao aceitar.
- **Ficha:**
  - a criatura nasce de uma ficha local (`~/.infinity-ai/sheets/<jogo>/<nome>.json`), com números consultados por entidade (TH.GL, livros de monstros), nunca copiados para o repositório;
  - corpo de base vivo do BG2;
  - `sounds: "silent"` tira as falas de clique herdadas (ADR-0146).
- **Recurso de outro jogo** (desenho, animação): só no override do laboratório, pela regra da CR-2026-032; projeto sem licença só com o OK do mantenedor por projeto.

## 6. Passagens e áreas nossas

- **Área nossa (ADR-0146):**
  - cópia de uma sala do jogo com o nome `IA` e quatro dígitos, sem nada do jogo agindo, instalada com o jogo fechado (`build_area.py`);
  - **antes de propor:** ver o minimapa (`MOS`) da sala e os pontos de surgimento da área. A AR0310 não era um porão, e a AR0318 tem surgimento de rufiões.
- **Passagem:**
  - `{passage_id, area, x, y, to, to_x, to_y, facing, after}`, **só de ou para uma área nossa**, aberta depois dos passos em `after`;
  - o líder parado 1 s a até 60 px do ponto, sem inimigo vivo na área;
  - o ponto exato vem de `lab_action.py where`.

## 7. As pessoas da quest

- Toda pessoa que fala na quest tem **curadoria conferida**:
  - identidade, ofício, origem, estatuto (`HABITANTE`, `VIAJANTE`, `FORASTEIRO`, `VISAO`);
  - fatos sobre si;
  - opcionais: `speech` (como fala), `persona` (quem é, CR-2026-035) e `mind` (INT e SAB corrigidos, ADR-0147).
- O que a pessoa **não** deve contar fica fora dos fatos dela. O segredo da quest só aparece no fato do passo, na hora certa.
- **Camada da fala (ADR-0147):** INT ou SAB a partir de 15, ou reação amistosa, faz a pessoa falar pelo Claude; reação negativa, nunca.

## 8. Coerência com o mundo

- O ano é 1369 DR. Fatos de Faerûn coerentes com o pacote de cânone; nomes de lugares e organizações com o nome do jogo e o inglês, como no pacote.
- **Nada do enredo do BG2** (Irenicus, o Ravager, Saradush) nem spoiler (ADR-0095).
- Personagens de outros jogos entram como **pessoas novas** com ficha e curadoria próprias (Tamoko, Gregor, Kalessia), nunca alterando um NPC do jogo.
- Um nome no fato que o mundo não conhece (fora do pacote e das pessoas) gera aviso do verificador: ou entra no pacote, ou é explicado no próprio fato.

## 9. O verificador

`tools/quest-author/check_quest.py <arquivo>` (`quests/authoring.py`) lista cada problema pelo nome:
- **Erro, bloqueia:**
  - formato (campo e motivo);
  - `after` para frente;
  - conversas não encadeadas da mesma pessoa;
  - quem dá a quest com passo de conversa;
  - pessoa sem curadoria;
  - área fora da build;
  - criatura nossa não instalada;
  - passagem entre duas áreas do jogo;
  - derrota de presença inexistente;
  - chamado inválido.
- **Aviso, não bloqueia:**
  - palavra-chave comum demais;
  - menos de 4 formas de aceite;
  - nome que o mundo não conhece;
  - área nossa (confirmar a instalação);
  - presença só de noite sem a quest dizer que é de noite;
  - `until` antes de `from` na lista.
- **Concordância com o carregador:** o verificador nunca é mais rígido que o carregador. Se o carregador recusar algo que o verificador não nomeou, aparece o erro `FORMAT`.
- **No serviço:** o log diz por que cada quest não carregou (`quest recusada: <arquivo>: <motivos>`).

## 10. O teste no jogo (roteiro)

1. Quem dá a quest: o chamado aparece; a oferta, perguntando se o grupo aceita; o aceite com palavras comuns; a linha de diário.
2. Cada passo, na ordem: conversa (o fato dito, "(agora)"), chegada (de noite, se for o caso), derrota (contagem).
3. Presenças: já no lugar ao chegar; o número certo; hostis no ponto certo; saem como manda `leave`.
4. Passagens: só abrem depois do passo; vão e voltam.
5. Entrega e marco: a confiança muda.
6. Save antigo recarregado: a quest volta ao ponto daquele save.

## 11. O agente de quests (D1: skill do Claude Code)

`skills/quest-authoring/skill.md`:
1. **Entrevista:** quem dá a quest; o objetivo (achar, recuperar, derrotar, levar); onde; quem são os envolvidos (do jogo, de outro jogo ou novos); o tom; como termina.
2. **Proposta** em `~/Downloads`, com as decisões para o mantenedor.
3. **Montagem** depois da aprovação: quest, curadorias, fichas; o verificador sem erros; casos de bateria para as falas da quest.
4. **Laboratório:** a quest fica nas **quests locais** (`~/.infinity-ai/quests/local`, fora do repositório) até o mantenedor aprová-la no jogo (D2). Modelos com o jogo fechado, pin refixado, serviço com `--local-quests` e `--quest-presence`.
5. **Repositório:** depois do teste aprovado, a quest vai para `knowledge/quests`, com evidência; commit, push e PR só com o OK do mantenedor.

**Fora desta SPEC:** o agente dentro do jogo (o jogador pede uma quest pela caixa e o Claude monta pela API). Precisa de ADR própria.

## Requisitos EARS

- **REQ-QAUTH-001:** quando um arquivo de quest for verificado, o sistema deve listar cada erro e cada aviso com código, lugar e motivo.
- **REQ-QAUTH-002:** o verificador nunca deve aceitar uma quest que o carregador recusa, nem recusar uma que ele aceita.
- **REQ-QAUTH-003:** quando o serviço não carregar uma quest, deve registrar no log o arquivo e os motivos.
- **REQ-QAUTH-004:** com o inventário local presente, o verificador deve recusar pessoa sem curadoria, área fora da build e criatura nossa não instalada.
- **REQ-QAUTH-005:** uma quest feita pelo agente só deve ir para `knowledge/quests` depois do teste aprovado pelo mantenedor no jogo.

## Critérios de aceite

- `tests/test_quest_authoring.py`: as duas quests de hoje passam; cada erro da lista é nomeado e o carregador também recusa; o verificador nunca é mais rígido que o carregador; o inventário local bloqueia o que não existe; o serviço informa as quests recusadas.
- Fase 3: uma quest nova feita pelo agente, do começo ao fim, com evidência no jogo.

## UNKNOWN

- Como o jogador vai pedir uma quest dentro do jogo, e quanto o agente pode decidir sem o mantenedor (ADR futura).
- Objetivo de item (entregar ou recuperar um item do jogo) ainda não existe como passo; hoje um item só vem no inventário de uma criatura nossa (ADR-0141).
