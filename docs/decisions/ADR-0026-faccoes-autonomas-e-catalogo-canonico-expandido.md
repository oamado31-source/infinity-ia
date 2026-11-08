# ADR-0026 — Facções autônomas por regras e catálogo expandido de Forgotten Realms

- **ID:** DEC-031
- **Situação:** **APROVADA — opção B com adendo de abrangência canônica**
- **Data:** 2026-11-06
- **Domínio:** geopolítica, facções, alianças, organizações, influência e simulação social.
- **Contexto:** Infinity AI Living World, com motor-base BG2:EE e data-base de testes 1369 DR.
- **Relações:** DEC-008/009/023 (cronologia/canon), DEC-014/021/022 (código primeiro e simulação por nível), DEC-028/029/030 (conhecimento, rumores, reputação), DEC-010/027/012/011 (geração, risco, gateway e autoridade do host).

## Contexto

As facções clássicas presentes nos jogos BG, IWD e NWN são apenas uma parte das organizações documentadas no cenário de Forgotten Realms. Um mundo persistente capaz de repercutir sua história deve considerar outras guildas, organizações religiosas, ordens, casas, grupos políticos, organizações comerciais e redes de influência do **cânone**, não apenas as que possuam conteúdo implementado nos jogos.

Exigir um LLM contínuo para cada grupo seria caro, difícil de auditar e incoerente com a DEC-014. Criar todas as organizações, NPCs, locais e estruturas físicas simultaneamente também criaria custos altos e problemas de anacronismo.

## Decisão aprovada

1. **Opção B:** as facções evoluirão por objetivos, recursos, relações, interesses e condições do mundo, **prioritariamente via regras determinísticas**, em ciclos proporcionais aos níveis de atividade ACTIVE/NEAR/DISTANT/DORMANT. Não há um LLM persistentemente ativo para cada organização.
2. **Adendo obrigatório de cobertura:** manter as facções/guildas/grupos encontrados nas campanhas clássicas **e expandir a base de referência para todas as demais organizações reconhecidas no cânone de Forgotten Realms**, sem limitar o catálogo às presentes nos jogos originais.
3. A abrangência diz respeito ao **catálogo canônico pesquisável e progressivamente curado**. Não equivale a prometer que todas as organizações terão imediatamente NPCs, sedes, recursos de mapa, scripts ou simulação tática completa no protótipo.
4. **Temporalidade e localização obrigatórias:** existência, fundação, dissolução, cisões, líderes, alianças, presença regional e influência são avaliadas na data DR e na continuidade da campanha; instituições futuras não podem agir antes de existir, e extintas não operam sem evento de reativação fundamentado.
5. **Preservação de conteúdos clássicos:** facções já existentes nos jogos são reaproveitadas com identificadores, personagens, recursos e estado histórico coerentes; sua presença em um jogo não garante disponibilidade atemporal. As novas facções podem influenciar o contexto narrativo mesmo sem área visitável, sem gerar assets não instalados.
6. **Canon e divergências:** fatos oficiais verificados formam o baseline. Mudanças confirmadas pelos jogadores podem gerar linhas alternativas específicas por campanha (DEC-009), com rastreabilidade e sem reescrever a fonte canônica.
7. **Autonomia limitada pelo risco:** ações cotidianas e propostas de baixo/médio impacto podem ser geridas por regras, respeitando os gates da DEC-027. Golpes políticos, guerras, morte de liderança canônica, destruição permanente ou alteração maior de território/canon ficam em `HIGH` e **não são aprovados automaticamente nesta decisão**.
8. **Ações mecânicas:** qualquer mudança no jogo (spawn, hostilidade, inventário, preços, bloqueio de acesso etc.) precisa de uma feature/contrato suportado, autorização pelo Action Gateway DEC-012 e confirmação do host DEC-011. Simulação narrativa offscreen não se confunde com mutação mecânica confirmada.
9. **Conhecimento e reputação:** membros, liderança e facção não são oniscientes; informações chegam por canais permitidos (DEC-028/029) e percepções de indivíduos podem divergir das posições institucionais (DEC-030).
10. **Origem e licenciamento:** cada entrada canônica precisa de fonte verificável, precisão de datas e rastreabilidade; catálogos/enciclopédias da comunidade servem como índices a conferir contra fontes primárias quando possível. Não incorporar textos ou recursos proprietários indiscriminadamente à distribuição do software.

## Política mínima de escopo e ativação

Uma organização pode estar em **quatro níveis de materialização**, segundo a arquitetura candidata (nomes sujeitos à SPEC):

- `CATALOG_ONLY`: conhecida pelo catálogo do canon com período/território e proveniência; sem processos de simulação individualizados.
- `WORLD_RELEVANT`: influencia eventos, notícias, reputações e narrativas numa campanha quando temporalmente pertinente.
- `SIMULATED`: possui estado resumido de objetivos/recursos/relações, atualizado em checkpoints e sob orçamento.
- `IN_GAME_ACTIVE`: tem NPCs/recursos/ações disponíveis e validados no motor instalado, sujeitos ao host e à bridge.

Esses níveis são proposta de detalhamento técnico, **não uma nova escolha de produto**. Não assumir que uma facção é ativa só porque consta em uma lista.

## Contexto de dados candidato

`faction_id`, `canonical_name`, `aliases`, `source_ids`, `edition_continuity`, `founded_dr`, `dissolved_dr`, `status_interval`, `regions`, `leadership_history`, `parent_child_links`, `goals`, `resources`, `territory_influence`, `alliances`, `rivalries`, `membership_provenance`, `campaign_overlay`, `simulation_tier`, `canon_confidence`, `content_installation_id`, `risk_policy`.

Precisão de data, fontes conflitantes, organizações sem data de fundação e mudanças de nome exigem `UNKNOWN`/intervalos, **nunca datas fabricadas**. Nomes e aliases não podem fundir automaticamente organizações distintas. O modelo definitivo fica para SPECS.

## Consequências

**Benefícios:** Forgotten Realms mais abrangente que os jogos originais; conflitos e oportunidades persistentes coerentes com o canon; possibilidade de reutilizar recursos existentes e inserir influência indireta de organizações sem mapas; escala computacional compatível com simulação por lotes.

**Custos e riscos:** curadoria de um universo grande e nem sempre documentado de forma homogênea; fontes contraditórias; limites de capacidades e recursos de mods; combinatória de relações; risco de acontecimentos políticos irreversíveis; necessidade de proveniência e validação editorial.

## Critérios de aceitação candidatos

1. Uma facção canônica ausente dos jogos pode ser catalogada com fonte, período, região e estado, sem necessidade de instalar um mapa.
2. Uma facção não fundada em 1369 DR não age como organização já existente nessa data.
3. Uma facção extinta é preservada como fato histórico; seu retorno requer evento confirmado e autorizado.
4. Facções de jogos clássicos permanecem reconhecíveis e vinculadas a seus recursos originais, sem assumir compatibilidade de toda a pilha de mods.
5. Ação do jogador altera relações locais de uma facção sem reescrever o registro da fonte canônica.
6. Rivalidades, recrutamento e negociações seguem regras verificáveis e orçamentos de simulação, sem invocação LLM por tick.
7. Ao reabrir um save, eventos faccionais não são duplicados; clientes não aplicam decisões contraditórias.
8. Membro de facção não acessa automaticamente todos os segredos da instituição ou do narrador.
9. Eventos de risco `HIGH` permanecem pendentes sem autorização especial; efeitos mecânicos exigem recibo do host.
10. Catálogo incremental e mudanças de nomenclatura não apagam registros históricos nem confundem duas organizações.

## Pendências

- Inventário **exaustivo** das organizações canônicas, com revisão de fontes e cronologia: **não realizado nesta fase**; a decisão estabelece a meta de cobertura, não afirma tê-la concluído.
- Fórmulas, pesos, budgets, periodicidade e recursos virtuais: próxima DEC-032 e SPECS posteriores.
- Políticas detalhadas de poderes político/militar/econômico, resolução de conflitos, diplomacia e territórios.
- Consulta efetiva de assets instalados e suporte a comandos faccionais em BG2:EE/EET/IWD/NWNForBG.
- Testes de multiplayer, salvamento, cronologia e sincronização: **não executados**.

## Próxima decisão

**DEC-032 — Granularidade e custo da simulação de recursos, economia, território e conflitos entre facções.**
