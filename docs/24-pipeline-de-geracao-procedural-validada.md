# Pipeline de conteúdo procedural validado — DEC-010

**Discovery v2.2** · Documento técnico preliminar, **não é SPEC executável**.**Decisão aprovada:** DEC-010 opção C / ADR-0020.**Decisão seguinte aberta:** DEC-027 (limiares de aprovação/publicação de conteúdos gerados).

## Objetivo

Preservar mundo curado e acontecimentos históricos de Forgotten Realms e obter rejogabilidade por missões, rumores, diálogos, eventos e — após provas técnicas — novos locais/masmorras. A camada narrativa do Infinity AI não deve assumir capacidade de alterar arquivos `.ARE`, `.WED`, scripts ou saves em execução sem bridge comprovada.

## Classificação técnica por risco

| Classe | Exemplos | Alvo inicial | Bloqueios |
|---|---|---|---|
| `NARRATIVE` | rumor, fala, descrição, contexto de investigação | Geração local sob demanda e validação de conhecimento | DEC-007/016 UI; lore, segredos e qualidade |
| `STRUCTURED_QUEST` | objetivo, pistas, condições, relações, estados | Templates e planejamento estruturado validado | Integração de quest-state/flags ainda não comprovada |
| `WORLD_ENTITY` | NPC já compatível, variação de criaturas, itens e objetos existentes | Catálogo permitido + validação host | DEC-011; spawn/estado multiplayer; nenhum comando arbitrário |
| `ENCOUNTER` | seleção contextual de grupos de criaturas | Encounter Director, limites regionais | DEC-005-E; métrica e spawn pendentes |
| `STATIC_AREA_PACKAGE` | masmorra nova, novo mapa, recursos binários e scripts | **Pré-geração em build isolada** e validação antes da sessão | Formatos do motor, navegação, testes, compatibilidade EET |
| `LIVE_AREA_INJECTION` | nova área criada/importada durante sessão ativa | **Somente possibilidade futura** | POC explícita, sincronização, save/load e rollback |

A tabela **não autoriza automaticamente** nenhuma classe. A política de autorização será discutida na DEC-027.

## Fluxo de proposta, validação e confirmação

```text
Background / World Trigger / Player Backstory
       |
       v
Content Planner (rules/templates; local LLM if open-ended)
       |
       v
Structured Proposal + source provenance + requirements
       |
       v
Static Validators: canon, timeline, geography, secrets,
  factions, allowed resources, party ruleset, dependency versions
       |
       +-- invalid --> REJECTED + diagnostic + optional curated fallback
       v
VALIDATED proposal (NOT a game-state change)
       |
       v
Publication Policy [DEC-027 - pending] + Security Gate [DEC-012]
       |
       +-- needs review --> PENDING_APPROVAL
       v
Game Adapter / Host authority [DEC-011]
       |
       +-- no receipt --> UNCERTAIN / reconcile
       v
CONFIRMED execution --> append confirmed event --> snapshots
```

Para mapas novos, adicionar `asset build -> validation -> isolated test installation -> curated publication` antes de qualquer tentativa de uso. Não fazer download/redistribuição automática de assets proprietários.

## Estados candidatos

`DRAFT` → `VALIDATED` → `PENDING_APPROVAL` (caso aplicável) → `READY` → `APPLYING` → `CONFIRMED` ou `REJECTED` / `UNCERTAIN`.

- `VALIDATED`: passou por verificações preliminares; **não significa que o motor aceitou a mudança**.
- `CONFIRMED`: ação mecânica reconhecida pelo host ou publicação puramente narrativa validada, conforme contrato específico.
- `UNCERTAIN`: o comando pode ter sido aplicado; **não repetir sem reconciliação**.
- `PENDING_APPROVAL`: permitido/necessário dependerá de DEC-027.

## Contrato candidato — `GeneratedContentProposal`

```yaml
proposal_id: unique-and-idempotent
campaign_id: example-campaign
content_kind: STRUCTURED_QUEST
origin: local_llm_or_template
ruleset_version: adnd2e-baseline
world_revision: 123
world_time_dr: 1369
related_arc_ids: []
asset_manifest: []
prerequisites: []
knowledge_visibility: restricted
canon_source_refs: []
allowed_actions: []
seed: optional-for-deterministic-selection
validation_results: []
status: DRAFT
```

Todos os campos e valores são **hipóteses de schema**, não configurações ou software implementados.

## Validação do conteúdo novo

- **História e canon:** não contradizer o estado adotado da campanha nem antecipar acontecimentos de anos futuros; divergências registradas têm precedência apenas naquela campanha.
- **Causalidade:** vínculos com históricos, escolhas e acontecimentos confirmados; não transformar hipóteses de NPC em fatos.
- **Conhecimento:** segredos dos jogadores somente chegam a NPCs que tenham fontes justificadas.
- **Mundo:** não trazer facções, monstros ou autoridades a regiões/épocas incoerentes sem justificativa.
- **Compatibilidade:** engines, modpacks, assets e dependências identificados e instalados na build compatível.
- **Segurança:** rejeitar scripts e comandos fora de allowlist; sem alteração direta do motor por saída bruta de LLM.
- **Persistência:** ids estáveis, event log, checkpoints, consistência de save e proteção contra duplicação.
- **Multiplayer:** host confirma ações; clientes observam mesmo estado autorizado.
- **Performance:** número máximo de elementos, budget de latência/LLM e atualização por nível de atividade.

## Provas de conceito e testes candidatos

| Caso | Cenário | Esperado |
|---|---|---|
| PROC-01 | Gerar 20 missões estruturadas offline a partir de templates | Passam schema; duplicatas/conflitos identificados; sem modificar BG2:EE |
| PROC-02 | Proposta refere-se a NPC morto em campanha | Rejeitada ou aponta para desvio histórico autorizado e verificável |
| PROC-03 | Criar rumor sobre histórico secreto de jogador | Não publicar conhecimento não adquirido pelo NPC |
| PROC-04 | Quest necessita item/CRE inexistente na build | Rejeitar antes de execução; apresentar diagnóstico |
| PROC-05 | Simular duas entregas da mesma recompensa | Receipt idempotente; sem duplicação |
| PROC-06 | Gerar e testar novo pacote de área offline | Entradas/saídas, recursos e scripts validados antes da instalação |
| PROC-07 | Tentar injetar área em sessão sem suporte | Bloqueio seguro e conteúdo não publicado |
| PROC-08 | Save/reload com missão procedimental em andamento | Retomar o mesmo conteúdo/versão e progresso, sem recálculo destrutivo |
| PROC-09 | Dois clientes com manifestos de conteúdo diferentes | Impedir dessincronia e executar gate/mensagem de incompatibilidade |
| PROC-10 | LLM indisponível | Conteúdo curado ou template válido continua disponível quando aplicável |
| PROC-11 | Reload após timeout no spawn | Estado `UNCERTAIN`, reconciliação e sem spawn duplicado |
| PROC-12 | Mudança de ano-base entre campanhas | Fatos e recursos adequados a cada cronologia; nenhuma contaminação entre saves |

Os cenários acima precisam ser derivados em testes reais apenas após a aprovação de SPECS. Nenhum foi executado agora.

## Pendências de planejamento

1. DEC-027: autoativação versus revisão do anfitrião e níveis de risco de publicação.
2. DEC-012/013/017: permissões, perfis de mods/instalação e direitos de uso.
3. DEC-007/016: integração de diálogos, UI, avisos de oportunidade e acessibilidade.
4. Catálogo real de recursos por build BG2:EE/EET/IWD/NWNForBG e limites de importação de áreas.
5. Formatos finais de contrato/eventos, migração de saves e compatibilidade multiplayer.
6. POC de criação de uma missão sobre **área existente** antes de considerar geração de mapas novos.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 exige classificação de risco/impacto agregado, proveniência temporal, ACL e validação antes de usar conteúdo procedural como incidente de viagem. Saída LLM não é evento objetivo consumado.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

A DEC-071 não autoriza geração de áreas, assets, scripts ou spawn dinâmicos. A composição por templates/adapter pré-testados será discutida na DEC-072; até POCs compatíveis, fallback para narrativa/pending e nenhum arquivo de engine gerado durante a sessão.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Templates compostos não concedem propriedade universal: cadeia de custódia da instância e validação do plano pós-encontro obrigatórias.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.

## Integração DEC-084/C — Discovery v8.0

Planos de proteção não autorizam geração runtime de cenas/guardas/scripts sem manifesto e POC; componentes do catálogo DEC-072 permanecem gated.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Gerador não inventa informantes, interceptações, espionagem ou localização secreta para um adversário; templates de situações futuras exigem gates e fonte observável.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Propostas de pistas falsas e iscas passam por templates curados, limites de recursos, risco e autoria; não gerar scripts, flags ou provas de crime não validados.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração DEC-091/C — Discovery v8.7

Plano operacional não é licença para gerar área ou script procedural; stage e testes de conteúdo permanecem obrigatórios.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Notificações de missão e cenas devem respeitar propriedade de eventos e estágio; abortar uma intenção não apaga consequências de cenas já confirmadas.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Regras temporais propostas DEC-096 não dão à LLM poderes de gerar script da engine ou recriar evento canônico; somente propostas seguras e efeitos parametrizados/curados.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Fases de arcos DEC-024 e regras históricas DEC-096 não forçam jogadores a protagonista nem resultados irreversíveis; divergências confirmadas condicionam a elegibilidade das repercussões.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Geração procedural apenas propõe objetos novos em namespace e capacidade permitidos; nunca adota por nome/CRE instância nativa/mod.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Eventos originais paralelos verificam os marcos da quest com probes limitados; sem leitura indiscriminada de globals.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**
