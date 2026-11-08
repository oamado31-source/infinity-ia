# ADR-0014 — Campanhas paralelas e legado histórico no Living World

- **Decisão:** DEC-024
- **Estado:** **APROVADA — opção C com adendo de acontecimentos originais em paralelo e participações opcionais**
- **Data da aprovação:** 2026-11-06
- **Fase:** Discovery; ainda não é SPEC técnica nem integração validada no BG2:EE/EET.
- **Contexto:** DEC-004/ADR-0002 (Original vs. Living World), DEC-008/ADR-0011 (histórico/eventos), DEC-009/ADR-0012 (canon + divergências), DEC-023/ADR-0013 (ano-base 1369 DR), DEC-011/ADR-0007 (autoridade), DEC-014/ADR-0008 (regras primeiro, LLM local).

## Problema e motivação

Em um Living World situado inicialmente em 1369 DR, histórias de jogos anteriores (BG1, IWD1/IWD2) devem existir como passado com repercussões. Aventuras contemporâneas (especialmente BG2 e, conforme data precisa, SoD/ToB) **podem continuar ocorrendo em paralelo**, com protagonistas e NPCs próprios. Os jogadores criam personagens originais e podem encontrar, dialogar com e ajudar personagens das campanhas clássicas, sem se tornarem obrigatoriamente os protagonistas dessas campanhas.

O objetivo é preservar a nostalgia e o valor dos cenários, encontros e personagens, evitando tratar NPCs históricos apenas como decoração ou transformar as missões centrais em obrigações para o grupo.

## Deliberação aprovada

1. **Duas experiências isoladas:** Original mantém campanhas e saves originais; Living World tem estado próprio. Nenhuma mudança de campanha Living World altera automaticamente o jogo Original.
2. **Histórias anteriores = legado histórico:** eventos de jogos anteriores à data da campanha compõem a história do mundo **quando sustentados pela cronologia e pelo estado canônico eleito para a campanha**. Efeitos observáveis podem incluir notícias, reputações, objetos, ruínas, sobreviventes, inimigos remanescentes, facções e tramas derivadas.
3. **Histórias contemporâneas = arcos paralelos opcionais:** narrativas originais que coincidirem com o calendário podem avançar paralelamente, independentemente da participação obrigatória do grupo. O jogador pode encontrar personagens e aceitar ajuda ou missões paralelas, ignorá-los ou seguir outras histórias.
4. **Protagonistas independentes:** o grupo do Living World **não é automaticamente Gorion's Ward nem herda flags, identidade, destinos, itens ou conquistas** da saga original. Protagonistas canônicos/históricos possuem identidade distinta, com resolução de ambiguidades de canon por curadoria; não se declara o destino de personagem incerto como fato.
5. **Intervenções têm consequência:** ações efetivamente confirmadas dos jogadores podem auxiliar, atrasar, alterar ou impedir um acontecimento; conflitos relevantes com a linha oficial abrem divergência causal auditável nos termos de DEC-009, sem sobrescrever histórico silenciosamente.
6. **Interações nostálgicas contextualizadas:** personagens, adversários e locais antigos podem ser lembrados em conversas, gerar rumor, missão ou retorno plausível. Sobrevivência, retorno ou ressurreição **não são fatos automáticos**; precisam de fonte/estado narrativo ou evento novo justificado e registrado. Distinguir `SURVIVOR`, `RETURNED`, `RESURRECTED`, `LEGACY_REFERENCE`.
7. **Respeito a datas e conhecimento:** nada que ocorra depois do ponto atual do calendário é tratado como fato consumado; se a fonte só indicar ano/intervalo, não forçar dia arbitrário. NPCs só comentam fatos que conheceram por uma via narrativa válida, conforme DEC-019.
8. **Scripts originais não rodam indiscriminadamente:** o EET reúne recursos e scripts para uma campanha centrada em seu protagonista original. O Living World requer **adaptadores ou reconstrução seletiva** dos arcos paralelos (flags isoladas, triggers e personagens); não pressupõe que a história de BG2 rode de forma autônoma em outro grupo pelo simples carregamento de seus mapas.
9. **Regra determinística primeiro:** calendário, progresso de arcos, elegibilidade de cameo, tabelas de rumores, cooldowns e condições de eventos são controlados por código; LLM local somente para composição de fala/novos ganchos quando necessário, com fatos/segredos filtrados. Nenhum LLM decide retroativamente a conclusão de missões sem evidência.
10. **Autoridade e multiplayer:** o host confirma alterações mecânicas; serviço narrativo registra eventos de campanha após recibos. A sincronização de personagens/eventos adicionais no multiplayer é hipótese que exige testes reais em EEex/bridge.
11. **Ano-base:** 1369 DR continua referência para o primeiro teste, com ano configurável por campanha (DEC-023). Dia/mês inicial ainda pendente. SoD/ToB e outros episódios de data controversa não são marcados como concluídos/ativos por presunção.

## Classes de estado do arco (schema candidato; não aprovado como implementação)

- `HISTORICAL_CONFIRMED` — passado verificado e adotado no canon desta campanha.
- `HISTORICAL_UNRESOLVED` — passado parcialmente conhecido, controvertido ou sem desfecho selecionado.
- `SCHEDULED` — evento previsto para o futuro, ainda não ocorrido.
- `PARALLEL_ACTIVE` — arco contemporâneo que pode avançar com ou sem ajuda dos jogadores, segundo política temporal.
- `PAUSED_UNVERIFIED` — trama indisponível ou impossível de sincronizar tecnicamente; não fingir execução autônoma.
- `DIVERGED` — desfecho confirmado na campanha diverge do canon-base.
- `COMPLETED` — arco concluído e persistido na campanha.

## Guardrails de integração

- `canon_event_id` (linha histórica) **não** é `game_quest_flag` (flag do BG2/EET); usar mapeamento versionado de IDs; nunca ligar diretamente uma variável global do jogo a um fato histórico sem adaptador.
- Um mesmo NPC presente em áreas de BG1 e BG2 deve ter identidade única lógica e estado temporal, não dois duplicados por importação.
- Separar `NPC_APPEARANCE` de `NPC_CANON_STATE`; a existência do arquivo `.CRE` não atesta que a pessoa esteja viva naquele ano.
- Missões originais podem precisar de instâncias/duplicações isoladas de recursos, scripts próprios ou desabilitação seletiva de triggers de capítulo/protagonista. Não aprovar implementação antes de POC.
- Mudanças de questline com consequências irreversíveis exigem confirmação do domínio autoritativo e tratamento de conflito com outras pessoas jogadoras.

## Alternativas descartadas

- **A (manter todos os scripts originais integralmente em execução):** conflito alto com protagonista/flags, sequência de capítulos e fluxo multiplayer; não entrega mundo realmente autônomo.
- **B (tratar todas as campanhas como concluídas):** incorreto para 1369, elimina encontros opcionais com personagens contemporâneos e reduz a nostalgia dinâmica.
- **C sem adendo (mundo livre sem arcos clássicos ativos):** preserva cenários, mas não a experiência desejada de encontrar e auxiliar protagonistas originais.

## Critérios de aceitação candidatos

1. PC original de Living World encontra um NPC de BG2 sem ser confundido com Gorion's Ward nem receber quest principal obrigatória.
2. Personagem de campanha anterior é citado como legado apenas se a fonte/estado o sustentar e a notícia chegar ao NPC atual.
3. Uma missão paralela opcional é recusada sem bloquear viagem, progresso do grupo ou o andamento de outras aventuras.
4. Arc original contemporâneo tem estado distinto (`PARALLEL_ACTIVE` etc.) e progressão agendada por código, mesmo quando ninguém do grupo o segue.
5. Se jogadores interferirem e alterarem o desfecho, a divergência é registrada e eventos futuros incompatíveis ficam suspensos.
6. NPC morto em época anterior não reaparece automaticamente; reentrada por ressurreição exige evento plausível e rastreável.
7. Reabrir o mesmo save não reexecuta cameo, recompensa, morte, conversa histórica nem missão concluída.
8. Original e Living World possuem saves, flags, histórias e estados isolados.
9. Nenhum conteúdo sem importação comprovada (ex.: SoU/HotU em NWNForBG) é apresentado como acessível no jogo.
10. Falha de bridge/multiplayer não é mascarada por texto da IA declarando que a cena aconteceu.

## Questões ainda em aberto

- **DEC-025:** como simular o avanço dos arcos paralelos sem participação dos jogadores: eventos agendados, avanço condicionado à proximidade ou simulação híbrida com intervenção opcional? (Próxima discussão.)
- Qual é a data de início do calendário em 1369 (DEC-023 não determinou dia/mês)?
- Quais desfechos específicos de BG1/SoD/IWD devem ser importados como passados confirmados, e com que grau de confiança?
- Como mapear NPCs, ARE/CRE/DLG/BCS, flags e arcos entre EET e builds de mods (DEC-013)?
- Regras para protagonismo histórico, finais múltiplos e divergências de canon (DEC-009).
- Gating de progressão irreversível com anfitrião/jogadores (DEC-018 e futuras SPECS).

## Fontes e limitações

- EET, projeto e README: https://github.com/Gibberlings3/EET — reúne saga e suporta continuidade de NPCs/quests **em uma campanha tradicional**, não comprova história paralela autônoma.
- EET readme e notas de modding: https://github.com/Gibberlings3/EET/blob/master/EET/readme-EET.html e https://github.com/Gibberlings3/EET/blob/master/EET/docs/Modder%27s%20Notes.html — arquivos DLG/BCS, transições e ordem de mods.
- Referência temporal e classificação: `docs/13-*`, `docs/14-*`, `docs/15-*`, `docs/16-*`.

**Nenhum NPC, arco paralelo ou rotina foi criado/testado no jogo por esta decisão.**
