# Modelo preliminar — Legado histórico e arcos paralelos do Living World

**Discovery v1.5 | Estado: desenho para futuras SPECS, sem implementação**  
**Fundamento:** DEC-024 / ADR-0014; DEC-004, DEC-008, DEC-009, DEC-011, DEC-014, DEC-019, DEC-021, DEC-022, DEC-023.

## Visão de experiência

O grupo cria heróis próprios, inicia em 1369 DR (padrão inicial de teste) e explora os cenários BG/IWD/NWN disponíveis. Eventos mais antigos criam passado, memória social e nostalgia; tramas contemporâneas prosseguem paralelamente. Encontrar ou ajudar personagens originais deve ser **opcional**, sem forçar participação na jornada do Bhaalspawn.

## Três camadas independentes

```text
L1 — História-base Forgotten Realms
  fatos com fonte, época, região, versão/canon e confiabilidade
        |
        v
L2 — Arcos originais dos jogos (legado ou paralelos)
  estado de arco + elenco próprio + dependências + ganchos + resultados possíveis
        |
        v
L3 — Living World desta campanha
  intervenções dos jogadores + eventos confirmados + IA narrativa sob demanda
        |
        v
Reconciliação de canon (DEC-009) + Controller/Host (DEC-011)
```

A cronologia oficial é uma fonte para o mundo, não um interruptor que ativa automaticamente *scripts originais*. O domínio narrativo não assume que componentes EET de uma história principal podem correr com o protagonista ausente.

## Matriz de estados de conteúdo por época (1369 DR como exemplo)

| Origem | Estado narrativo candidato | Possíveis experiências dos jogadores | Alerta obrigatório |
|---|---|---|---|
| IWD1 / HoW / ToL (~1281) | legado distante com verificação individual | ruínas, notícias antigas, ecos familiares, descendentes, inimigo sobrevivente se plausível | não importar automaticamente NPC humano vivo após 88 anos |
| IWD2 (1312) | legado histórico com verificação individual | facções sobreviventes, descendentes, efeitos regionais e possíveis inimigos remanescentes | não presumir população e facções invariáveis |
| BG1 / TotSC (1368) | passado recente, conforme linha histórica escolhida | relatos da Crise do Ferro, referências a heróis, consequências de ações | finais múltiplos e falas dependentes de fonte |
| Siege of Dragonspear (1368–1369) | `HISTORICAL_UNRESOLVED` ou `PARALLEL_ACTIVE`, por data exata | notícias, movimento militar, ganchos relacionados | não assumir conclusão em dia desconhecido |
| BG2: Shadows of Amn (início 1369) | `PARALLEL_ACTIVE` quando cronologia/estado permitir | cruzar com personagens importantes e ajudá-los opcionalmente | protagonistas não são PCs; scripts de capítulos não podem rodar indiscriminadamente |
| BG2: Throne of Bhaal (~1369–1370) | `SCHEDULED`/`HISTORICAL_UNRESOLVED` conforme fonte | consequências posteriores, eventual participação se datado | data e resultado disputados; não ativar por suposição |
| NWN original (1372) | `SCHEDULED` em 1369 | conhecer Neverwinter antes da Wailing Death | não ativar peste em 1369 |
| NWN SoU/HotU (~1372, importação não comprovada) | lore futuro, recurso `NOT_IMPORTED` até teste | rumores futuros apenas quando tempo chegar e conteúdo existir | não prometer áreas ou quests importadas |

## Experiências nostálgicas candidatas

- **Cameo:** encontrar figura famosa no local e época plausíveis, podendo conversar sem iniciar trama obrigatória.
- **Missão lateral de apoio:** fornecer medicamento, suprimentos, informações ou escolta ao personagem de campanha original, com impacto medido por evento confirmado.
- **Legado:** uma ação de BG1/IWD inspira rumor, monumento, desconfiança ou nova busca no ano atual.
- **Inimigo recorrente:** sobrevivente ressurgindo com justificativa; se morto, possível ressurreição **apenas** se mecânica e narrativa autorizarem, com trilha causal.
- **Conexão com backstory:** história própria do jogador cruza evento clássico, sem expropriar protagonista ou conhecimento secreto.

## Proposta de dados conceituais (não schema final)

```text
CanonicalEvent(id, date_interval, provenance, confidence, ...)
LegacyReference(id, canonical_event_id, asset_id, target_year, portrayal_policy, ...)
ParallelArc(id, source_story_id, campaign_id, start_window, end_window,
            canonical_protagonists[], state, current_stage, dependencies[], ...)
ArcBeat(id, arc_id, trigger, deadline_policy, world_effects[], ...)
OptionalInteraction(id, arc_id, npc_id, allowed_actions[], cooldown, ...)
ArcInfluence(id, actor_id, arc_id, world_event_id, consequence, verification, ...)
CampaignBranch(id, parent_canon_event_id, divergence_reason, event_receipt, ...)
```

Regras de identidade: o avatar do jogador **não** pode assumir por acidente a identidade de protagonistas clássicos. `game_quest_flag` e `lore_arc_state` são objetos separados, com conversor versionado e testes.

## Fluxo de evento candidato

1. A data e local tornam um arco elegível segundo regras determinísticas.
2. O serviço confirma disponibilidade do mod/área/NPC e compatibilidade com o save atual.
3. O diretor ativa estado narrativo `PARALLEL_ACTIVE` (sem declarar efeitos mecânicos).
4. Um NPC ou rumor pode apresentar um gancho contextual e opcional ao grupo; se precisar de diálogo livre, um LLM local monta a fala usando fatos/segredos filtrados.
5. Se o grupo interferir, o controlador autoriza ações e o host confirma resultados mecânicos.
6. O evento confirmado altera o arco e as projeções narrativas; conflitos com canon seguem a política de divergências DEC-009.
7. O avanço sem jogadores presentes usará a futura política DEC-025, mantendo DEC-021/022 sobre tempo e atividade.

## Riscos de implementação

- **Principal:** enredos BG foram desenhados para PC protagonista e capítulos sequenciais. Um mundo paralelo requer *adaptação de quests*, *eventos próprios* ou *instâncias isoladas*, não basta permitir viagem de EET.
- Duplicação/teletransporte de NPC entre áreas históricas e contemporâneas; o catálogo precisa de identidade global por personagem.
- Instalação de mods altera resrefs e flags; mapeamento estável depende de versões/manifests.
- Encontro com NPC canônico sem conhecimento suficiente pode revelar futuro da campanha ou segredos de PC.
- Avanço automático indiscriminado pode matar personagem favorito ou fechar arco antes de os jogadores poderem participar.
- Compatibilidade de spawn/diálogo/multiplayer com EEex/bridge ainda não demonstrada; `PAUSED_UNVERIFIED` quando necessário.

## Critérios de aceite candidatos (para SPECS posteriores)

| ID | Dado/ação | Saída verificável |
|---|---|---|
| CAND-ARC-001 | Um PC Living World encontra personagem clássico | personagem reconhecido como outra identidade; nenhuma quest principal forçada |
| CAND-ARC-002 | PC ignora gancho | continua explorando sem quebrar missão clássica ou mundo |
| CAND-ARC-003 | Evento anterior comprovado | pode gerar rumor/objeto/consequência dentro da data e conhecimento permitidos |
| CAND-ARC-004 | Data de SoD/ToB não confirmada | arco permanece pendente de curadoria; não marca sucesso/fim automaticamente |
| CAND-ARC-005 | Grupo ajuda protagonista original | alteração mecânica confirmada pelo host e efeito narrativo rastreável |
| CAND-ARC-006 | Grupo interfere de modo incompatível com canon | cria `CampaignBranch`; futuros eventos conflitantes ficam suspensos até conciliação |
| CAND-ARC-007 | NPC foi morto no passado | reaparecimento bloqueado salvo evento comprovado/justificativa de retorno |
| CAND-ARC-008 | Grupo recarrega save | não duplica cena, recompensa nem conhecimento |
| CAND-ARC-009 | Conteúdo não importado | nenhum NPC/quest/área falsamente anunciado como acessível |
| CAND-ARC-010 | Multiplayer com 2 clientes | ambos visualizam o mesmo estado autoritativo (a testar após POCs) |

## Próxima decisão

**DEC-025 — Política de avanço de arcos paralelos sem participação do grupo**. Deve ser coerente com tempo híbrido da DEC-022: agendamento por data, progresso por proximidade ou mistura dos dois com eventos críticos protegidos.

## Evidências consultadas

- EET: https://github.com/Gibberlings3/EET
- EET readme atual: https://github.com/Gibberlings3/EET/blob/master/EET/readme-EET.html
- Notas para modders: https://github.com/Gibberlings3/EET/blob/master/EET/docs/Modder%27s%20Notes.html
- Matrizes de data e compatibilidade: `docs/13-*` até `docs/16-*`.

## Integração DEC-091/C — Discovery v8.7

Arcos canônicos paralelos não podem ser acelerados por planos do diretor não confirmados; marcos críticos têm gating DEC-034.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Políticas de execução devem preservar idempotência por action_id, plan_revision, host_session e checkpoint ao cancelar/retomar.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Matriz condicional proposta DEC-096 distingue legado de acontecimento passado de progressão atual: não reexecutar campanhas antigas e não assumir protagonistas BG/IWD/NWN; ramificações exigem overlay de divergências.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Campanhas paralelas e legado não compartilham observações privadas de quests entre ramos ou modos Original/Living World.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para história pública e pessoal de NPCs não se reescreve retroativamente, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para identidade e histórico persistente de NPCs, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.
