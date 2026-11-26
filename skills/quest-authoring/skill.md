# Skill — Autoria de quests (agente de quests, SPEC-013)

Transformar a ideia do mantenedor numa quest do Infinity, testada no laboratório. Antes de tudo, ler `specs/013-autoria-de-quests/spec.md` (as regras) e a quest de referência `knowledge/quests/sarevok-diary.pt_BR.json`. Responder sempre em português do Brasil.

## Regras de conduta

- **Nada sem aprovação.** A ordem é: entrevista → proposta → aprovação → montagem → laboratório → teste do mantenedor → repositório. Commit, push e PR só com o OK explícito de cada vez; o mantenedor faz o merge.
- **Dados do jogo e fichas ficam fora do repositório** (CR-2026-030). Números de fontes externas: consultar por entidade, guardar só localmente, nunca copiar texto.
- **Recurso de outro jogo:** só no override do laboratório, pela CR-2026-032. Downloads só com permissão, dizendo nome, origem e tamanho.
- **Nunca** tocar a quest original do jogo, ler variáveis dele, nem pôr enredo do BG2 ou spoiler.
- **Se a ideia pedir algo que o sistema ainda não faz** (por exemplo, um item do jogo como objetivo), dizer na proposta e propor uma ADR ou CR antes de montar.

## 1. Entrevista (curta, uma rodada)

Perguntar só o que a ideia não disser:
1. **Quem dá a quest:** um NPC do jogo (qual, onde) ou uma pessoa nova?
2. **O objetivo:** achar alguém ou algo, recuperar, derrotar, levar uma mensagem, investigar.
3. **Onde:** as áreas. Uma área nova precisa de sala do jogo para copiar; ver o minimapa antes.
4. **Os envolvidos:** pessoas do jogo, de outros jogos (ficha de onde) ou criadas; quem luta.
5. **O tom:** mistério, terror, humor, drama.
6. **O fim:** o que muda (confiança, marco) e quem agradece.

## 2. Proposta (`~/Downloads/INFINITY_AI_Quest_<nome>_proposta.md`)

No formato da proposta do diário de Sarevok:
- **o roteiro passo a passo**, em linguagem do jogador;
- **as pessoas**, com curadoria (fatos, jeito de falar, persona, INT e SAB) e ficha;
- **as áreas e os pontos**; o que precisa de código novo (ADR ou CR);
- **as decisões para o mantenedor** (`- [ ]`, a recomendada primeiro);
- **o teste no jogo**, pelo roteiro da §10 da SPEC.

## 3. Montagem (depois de "Aprovar como proposta")

1. **O arquivo da quest em `~/.infinity-ai/quests/local/<quest_id>.pt_BR.json`** (fora do repositório, D2):
   - fatos como **fala direta**, terminando a oferta com a pergunta do aceite ("Pergunte se o grupo aceita …"); o pedido ao grupo como desejo ("você quer que o grupo …"), nunca como ordem ("Peça que o grupo …"), que a pessoa repete; o que a própria pessoa diz ou faz, como ordem ("Agradeça …, entregue …, diga …"): na entrega de Doran a ordem foi seguida e a descrição ("você agradece …") foi ignorada;
   - aceite amplo;
   - `after` encadeando as conversas da mesma pessoa.
2. **Curadorias novas** em `knowledge/npcs/` e **fichas locais** em `~/.infinity-ai/sheets/`.
3. **`tools/quest-author/check_quest.py <arquivo>` sem nenhum erro.** Ler os avisos e resolver os que fizerem sentido.
4. **Casos de bateria** para as falas da quest (`tests/dialogue_eval/cases.pt_BR.json`): a oferta, um passo e a entrega. Rodar `run_eval.py`.
5. Suíte, `pyflakes`, `check_historical_adrs` e `check_public_files`.

## 4. Laboratório

1. **Com o jogo fechado:**
   - `build_templates.py --from-sheet …` para cada criatura nova;
   - `build_area.py` para área nova;
   - `talk_poc.py --deploy` se o módulo mudou.
2. **Refixar o manifesto e o pin do pacote**, se algo do pacote mudou.
3. **Serviço** com `--local-quests ~/.infinity-ai/quests/local --quest-presence --claude`. Conferir no início do log que a quest não aparece em `quest local recusada`.
4. **Passar ao mantenedor o roteiro do teste** e acompanhar pelo log. Ajustar fala, palavras-chave ou fatos pelo que ele vir.

## 5. Repositório

Com o teste aprovado:
1. mover a quest para `knowledge/quests/`, com `curation.status: CHECKED`, `checked_by: mantenedor` e a data;
2. escrever a evidência (`docs/evidence/S2…`) e, se houver código novo, a ADR ou CR;
3. abrir o PR só com o OK. Depois do merge: sincronizar o laboratório, apagar o branch e atualizar a memória.
