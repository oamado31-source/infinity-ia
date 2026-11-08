# DEC-032 — Pesquisa comparativa de simulação estratégica em jogos

**Discovery v2.9 — estudo de referência, não SPEC nem verificação de código/engine completo.**  
**Objetivo:** identificar padrões publicamente documentados de economia, política, diplomacia e guerra para o Living World, respeitando as DEC-031/032.

## Escopo e método

Fontes revisadas em 2026-11-06: manuais oficiais, blogs de desenvolvedores, documentação oficial de modding, páginas oficiais e notas técnicas. Comparou-se **o comportamento descrito**; não se desmontou motores proprietários nem se verificou o desempenho em máquinas do usuário. Inspiração em mecânicas não equivale a direito de distribuir código/ativos de outros jogos.

## Matriz dos jogos e lições reaproveitáveis

| Jogo/família | Mecanismos confirmados nas fontes | Reaproveitar conceitualmente | Evitar no primeiro MVP | Aderência |
|---|---|---|---|---|
| Total War: ROME II e Rome: Total War / Rome Remastered | Estratégia por províncias e facções, recursos, exércitos, diplomacia, ordem pública, receitas e batalhas separadas; resolução automática é opção do jogo. | **Separação macro/tático; grafo político/regional; ordem pública; objetivos de facção; cálculo resumido de confrontos** | Novo motor de guerra 3D, microcontrole de unidades, interface de grand strategy | Muito alta |
| Mount & Blade II: Bannerlord | Aldeias produzem; camponeses transportam; oficinas transformam; caravanas arbitram preços; guerras/saques perturbam cadeias, prosperidade e rendimentos; exércitos consideram força/alimento | **Economia regional simples ligada a rotas, segurança, abastecimento e missões** | Simular individualmente todas as viagens/caravanas/cargas e preços de centenas de mercadorias | Muito alta |
| Crusader Kings III | Dinastias, líderes, vassalos, títulos, decisões, intrigas, personagens históricos com características, eventos e sucessão | **Líderes, legitimidade, lealdade, alianças, disputas internas, crises históricas** | Genealogia de cada pessoa, sucessão ilimitada durante períodos do cânone sem validação | Alta |
| X4: Foundations | Produção, consumo, comércio e expansão econômica/militar entre facções; mercado dinâmico | **Escassez, abastecimento e reação a perturbações** | Simulação integral de cadeia física de cada produto/objeto | Média (alta como inspiração; custo alto se copiado) |
| Stellaris 4.0 | Agrupa populações para reduzir cálculos e representa trabalho/produção de forma agregada | **Coortes/indicadores por região e processamento em lote** | Iterar cada morador/emprego/mercador no mesmo tick | Muito alta para desempenho |

## 1. Total War / Rome Remastered — macro e micro são subsistemas diferentes

- A documentação oficial de **ROME II** separa campanha estratégica (recrutamento, construções, comércio, diplomacia, guerra) das batalhas táticas; guerras podem ser resolvidas manualmente ou por autoresolução. A interface de campanha mostra renda, impostos, ordem pública, alimento e relações internacionais.
- O repositório oficial de documentação para modders de **ROME REMASTERED** explicita componentes da IA diplomática: `manager` (objetivos), `analyser` (valor de propostas), `negotiator` (aceitar/recusar/contrapropor), `diplomat controller` (contato). A IA prioriza missões como comércio, aliança, neutralidade, guerra, passagem militar e proteção; confiança, reputação, postura e personalidade impactam decisões.
- Os documentos públicos detalham regras de **comércio terrestre e marítimo**, incluindo adjacência, recursos, estradas, bloqueios, guerra, epidemias e portos; outro guia distingue **rotas por região** e **movimentação local por células**.

**Padrão recomendado:** `FactionGoals + DiplomaticPlanner + RegionalGraph + StrategicEventResolver`, tudo por regras testáveis. A visualização detalhada existe apenas se um evento local efetivamente alcançar o BG2:EE.

**Cuidado:** Rome Remastered **não oferece seu motor como biblioteca acoplável ao Infinity Engine**. Documentação de modding revela comportamentos e dados, mas não autoriza copiar o jogo ou presumir licença de código.

## 2. Bannerlord — economia conectada a segurança e campanha

- Blogs técnicos de TaleWorlds relatam fluxo **aldeias → cidades/oficinas → caravanas → consumo e prosperidade**; ataques a aldeias/caravanas e interdição de passagens prejudicam a economia de um rival.
- A TaleWorlds também descreve evolução do modelo de consumo urbano por orçamento de categorias e oferta/demanda; não basta inventar preços aleatórios.
- Fontes de desenvolvimento citam que a capacidade de sustentar guerra depende da economia e que desorganização de tropas, alimento e renda pesa nas decisões de lordes; relatos posteriores de atualização abordam decisões de guerra/paz e suprimentos.

**Padrão recomendado:** indicadores agregados como `regional_supply`, `route_security`, `prosperity`, `faction_treasury_proxy`, `military_readiness`. Bloqueio de uma estrada pode reduzir fornecimento, afetar preços indicativos e justificar escoltas ou patrulhas. **Não** exigir transporte de cada pão ou espada em um NPC por viagem.

## 3. Crusader Kings III — liderança e política pessoal

A página oficial descreve facções/dinastias, territórios, títulos, vassalos, personagens com traços, intrigas, espionagem, mercenários e eventos dinâmicos. Uma escolha de líder pode mudar alianças, estabilidade e objetivos de um grupo.

**Padrão recomendado:** representar `leader_id`, `loyalty`, `legitimacy`, `relationships`, `succession_constraints` nas organizações para que situações diplomáticas existam sem gerar todo evento individual. O canônico prevalece até uma divergência histórica legitimada por DEC-009; não matar/eleger personagens estabelecidos simplesmente por rolagem oculta distante.

## 4. X4: Foundations — cadeias e oferta/demanda

A desenvolvedora Egosoft descreve uma economia interligada e facções que expandem instalações conforme condições comerciais e ameaças. O próprio jogo apresenta simulação física rica, mas o Infinity AI não precisa copiar seu escopo.

**Padrão recomendado:** no MVP, **poucas categorias agregadas** de mercadorias, índices de escassez e rotas comerciais; as categorias e escalas ainda dependem de uma SPEC e de fontes do cânone. Em lugares próximos, expandir apenas as categorias que efetivamente afetam narrativa e quests. Loja do BG2:EE não muda seus preços até existir contrato mecânico compatível e autorizado.

## 5. Stellaris 4.0 — o precedente de otimização mais relevante

A Paradox descreve na atualização 4.0 a substituição de cálculos individualizados de populações por grupos, permitindo reduzir o trabalho quando crescem as economias. É prova de um *princípio de design*: **agregar entidades, evitar loops por indivíduo, computar mudanças por projeção e periodicamente**.

**Padrão recomendado:** para região distante, simular, por exemplo, `capacidade_de_producao`, `demanda`, `disponibilidade_de_recursos`, `forca_defensiva`, `tensao_politica` e **não** cada habitante. Ao chegar, materializar NPCs/aventuras consistentes com os agregados, jamais dizer que existiam como entidades do jogo sem validação.

## Matriz de custo/benefício específica do Infinity AI (avaliação qualitativa)

| Módulo conceitual | Benefício narrativo | Custo estimado | Fase candidata |
|---|---|---|---|
| Grafo de cidades/regiões e rotas documentadas | Essencial para comércio, rumores e viagens | Médio | MVP de simulação externa |
| Ledger de relações/objetivos de facções | Conflitos, diplomacia, consequências | Médio | MVP de simulação externa |
| Indicadores de suprimento, riqueza e segurança regional | Quests e contexto convincente | Médio | MVP limitado |
| Missões diplomáticas por objetivo e valor esperado | Fações parecem agir segundo interesses | Médio | Após modelos mínimos de facção |
| Política/autoridade local, estabilidade, liderança | Crises locais mais coerentes | Médio/alto | Expansão seletiva |
| Exércitos em unidades agregadas e logística | Guerras com consequências e gargalos | Alto | POC isolada, não marco histórico automático |
| Cadeias econômicas completas de mercadorias | Alto realismo econômico, porém marginal para RPG | Muito alto | Fora do MVP |
| Batalhas táticas massivas, cercos reais e tomada de cidades no motor | Alto espetáculo, risco muito alto | Muito alto | Fora do MVP; estudo futuro |

**Custo relativo sem horas estimadas ou prova empírica.**

## Referências verificadas (primárias preferenciais)

1. Creative Assembly / Total War — ROME II manual de campanha: https://r2encv2.totalwar.com/en/manual/single-player/0015a_enc_page_campaign_play_interface/index.html
2. Creative Assembly — ROME II objetivos e modos de batalha: https://r2encv2.totalwar.com/en/manual/single-player/0013_enc_page_campaign_play_objectives/index.html
3. Feral Interactive — documentação oficial Rome Remastered: https://github.com/FeralInteractive/romeremastered
4. Feral Interactive — como a IA conduz diplomacia: https://github.com/FeralInteractive/romeremastered/blob/main/documentation/feature_guides/AI_Diplomacy.md
5. Feral Interactive — fórmulas de batalha/campanha e comércio: https://github.com/FeralInteractive/romeremastered/blob/main/documentation/feature_guides/Battle_and_Campaign_Formulae.md
6. Feral Interactive — regiões e pathfinding estratégico: https://github.com/FeralInteractive/romeremastered/blob/main/documentation/feature_guides/Campaign_Map_Pathfinding.md
7. TaleWorlds — passagem do tempo e economia (blog): https://www.taleworlds.com/en/Games/Bannerlord/Blog/14
8. TaleWorlds — consumo, preços e oferta/demanda (blog): https://www.taleworlds.com/en/Games/Bannerlord/Blog/107
9. TaleWorlds — a economia como base de guerras (entrevista dev): https://www.taleworlds.com/en/Games/Bannerlord/Blog/68
10. TaleWorlds — ajustes de diplomacia, caravanas e exércitos (versões recentes): https://www.taleworlds.com/en/News/587
11. Paradox Interactive — página oficial CK3: https://www.paradoxinteractive.com/games/crusader-kings-iii/about
12. Egosoft — página oficial X4 (português): https://www.x4foundations.com/games/x4/info_br.php
13. Paradox Interactive — descrição da otimização de grupos populacionais em Stellaris 4.0: https://www.paradoxinteractive.com/games/stellaris/news/stellaris-update-4-0

## Conclusão para DEC-032

A combinação com melhor relação entre valor para um RPG e custo esperado é **Rome (macro/tático e diplomacia), Bannerlord (efeitos econômicos de rotas/segurança) e Stellaris (agregação para desempenho)**. CK3 acrescenta a dimensão política pessoal; X4 é referência de causalidade comercial, mas não seu nível completo de detalhe. **Não recomendamos trocar o BG2:EE de motor, integrar motores proprietários ou implementar guerra/economia completas no MVP.**

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Planos faccionais podem considerar fontes/informações efetivamente obtidas, não promessas de agentes ou segredos do ledger host.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Planos faccionais revisados respeitam autoridade/recursos e políticas políticas; não presumir que uma facção possa realocar todos membros livremente.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C pode propor mudanças políticas regionais decorrentes do histórico, mas mudanças de facção/cargos requerem prova, escopo, gates e branch; canon imutável.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Modificadores de guerra/mercado DEC-097/C não permitem recursos ou capacidade faccional inexistente.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Facções só podem agir sobre marcos de quests que conheçam por vias autorizadas, não branches antecipados.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para informação diplomática não pode ser conhecida por facções sem canal, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para efeitos diplomáticos dependem de canais e prova, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-109/C — Obrigações condicionais multipartes

Facções negociam dentro de recursos e mandatos provados. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
