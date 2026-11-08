# Base técnica originalmente proposta para DEC-096 — Matriz cronológica condicional de eventos e repercussões no Living World

> **Atualização v9.2 (2026-11-07): DEC-096/C APROVADA COMO ARQUITETURA.** Este documento conserva o esboço técnico proposto na v9.1 e não é o contrato consolidado. Referências normativas atuais: `docs/decisions/ADR-0091-matriz-cronologica-condicional-declarativa-com-avaliacao-deterministica.md` e `docs/96-matriz-cronologica-condicional-arquitetura-aprovada-e-contratos-do-motor.md`. **Nenhuma POC BG2:EE/EEex executada.**

## 1. Ideia central

Substituir uma planilha monolítica de `IF/ELSE` por três camadas: **(a) catálogo de fatos históricos/lore curados por ano DR**, **(b) matriz declarativa de regras condicionais e impactos**, **(c) avaliador determinístico e ledger causal da campanha**. A LLM local serve para linguagem, diálogos e sugestões após filtros e gates; não data eventos, não escolhe verdade histórica, não decide efeitos mecânicos.

**Diferenciar:** evento factual (`CanonEvent`), hipótese de efeito projetável (`ImpactRule`), evento real de campanha (`ConfirmedCampaignEvent`), efeito aplicado (`AppliedImpact`) e informação recebida por um NPC (`KnowledgeAcquisition`). A presença de um evento no KPack não o coloca automaticamente em cada taverna, nem o torna conhecido de toda Faerûn.

## 2. Proposta de colunas (visão humana exportável CSV/planilha)

| Coluna | Tipo | Por quê |
|---|---|---|
| `event_id`, `title`, `source_refs` | ID + texto + refs | rastreabilidade da cronologia e proveniência das fontes (DEC-061/062) |
| `canon_status`, `source_confidence`, `version` | enum / revisão | fato curado, disputado, inferência ou evento sintético; só curado/permitido alcança runtime |
| `year_dr_start`, `year_dr_end` | int / intervalo | recortar cronologia física DEC-060 |
| `month_start`, `month_end`, `day`, `date_precision` | opcional / enum | ano ≠ mês conhecido; preservar precisão e intervalos sem fabricar datas |
| `phase` | enum | pré-evento, ocorrência, pós-evento, duração; efeitos distintos |
| `scope_level` | enum | global, regional ou local descreve o fenômeno, não conhecimento instantâneo |
| `region_ids`, `location_ids`, `location_tags` | listas | geografia factual vs categorias taverna/palácio/templo/estrada/mapa; mapas dependem de build/adapter |
| `direct_impacts`, `indirect_impacts` | listas por IDs | reação imediata ≠ propagação posterior/rumores |
| `activation_conditions` | AST DSL allowlisted | equivalente seguro a IF/ELSE, sem executar código textual arbitrário |
| `prerequisites`, `mutual_exclusions`, `branch_policy` | IDs + regras | dependências, spoilers e canon alternativo nas campanhas DEC-024–026 |
| `effect_bounds`, `risk_class`, `required_gates` | regras tipadas | limites para economia, patrulhas, encontros e efeitos irreversíveis |
| `propagation_policy` | grafo / velocidades candidatas | escopo e delays por canais DEC-029/074, sem telepatia global |
| `priority`, `conflict_policy`, `idempotency_scope` | enums / IDs | efeitos concorrentes/contraditórios e anti-duplicação |
| `knowledge_pack_hash`, `build_capabilities` | hashes / listas | pack fixado e adaptadores realmente verificados DEC-063/051 |

**Normalização recomendada:** evento (1 registro), fontes (N), fases/intervalos (N), regras de impacto (N), escopos geográficos (N), pré-requisitos (N), estados por campanha/ramo (N). A planilha é **visão/editing UI**; o runtime não usa 80 colunas gigantes com JSON misturado sem validação.

## 3. Tempo DR: nunca inventar mês

- Calendar **Harptos**: usar ID de mês canônico (`1..12` mapeado por dicionário estático de Hammer a Nightal), dias `1..30`, feriados intercalares representados separadamente; não converter arbitrariamente para calendário gregoriano.
- Precisões `EXACT_DAY`, `MONTH`, `YEAR_ONLY`, `INTERVAL`, `DISPUTED`, `UNKNOWN`. `YEAR_ONLY` permite saber que um evento pertence àquele ano, **não autoriza ativar no mês 1**; `DISPUTED`/`UNKNOWN` ficam pendentes de curadoria ou confirmação no overlay. Intervalos com fim desconhecido não causam efeitos perpétuos.
- Campanha que começa depois de evento histórico: aplicar somente **baseline histórico/legado explicitamente curado** ou estado confirmado no ramo, **nunca reexecutar** combate, guerra, morte ou pagamento como ocorrência nova.
- Ano futuro em diretório separado não pode vazar para o filtro atual nem para a LLM do NPC, salvo política de premonição excepcional explicitamente autorizada (não presumida).
- Campanhas `FROZEN/PARTIAL/REALTIME` DEC-022: transições não ocorrem ao avançar relógio de máquina; só conforme relógio do mundo autorizado, catch-up bounded e revisões/checkpoints.

## 4. Espaço e abrangência

- `GLOBAL` significa escala **do evento histórico**, não efeitos mecânicos automáticos em todos os mapas. Cada regra associa regiões/locais/`location_tags` explícitos; ausências de geocoding ou mapa `UNKNOWN` implicam nenhum efeito mecânico.
- `REGIONAL`: conjunto de `region_ids`; `LOCAL`: `location_ids` com optional `location_tags`; `GLOBAL` pode fornecer contexto macro, mas efeitos locais requerem mapa de repercussão validado.
- Tipos candidatos: `tavern`, `palace`, `dungeon`, `forest`, `road`, `temple`, `market`, `port`, `gate`, `settlement`, `wilderness`; taxonomia controlada, IDs físicos verificados por build.
- Um tumulto pode afetar `market` e `road` apenas em um distrito; um aumento de patrulhas em `road` pode gerar evento indireto de menor banditismo **só após mudança confirmada e delay**.
- Presença de jogadores/NPCs e zonas ACTIVE/NEAR/DISTANT/DORMANT da DEC-021/068 determinam materialização, não o simples tipo de lugar.

## 5. Condições IF/ELSE como DSL declarativa (nunca código arbitrário)

Exemplo de AST **candidato**:

```json
{"all":[
  {"field":"campaign.world_phase","op":"EQ","value":"ACTIVE"},
  {"field":"region.flags.alert","op":"EQ","value":true},
  {"field":"campaign.flags.branch_divergence","op":"EQ","value":false}
]}
```

- `all/any/not` possuem profundidade máxima e campos allowlisted. `EQ`, `IN`, `GTE`, `LTE` tipados; **sem Python eval, SQL livre, JS ou prompt de LLM como predicado**.
- Compilar antecipadamente índices `year_dr/interval`, `region_id`, `location_tag` e dependências; só depois calcular predicados. Não varrer todas as linhas a cada frame ou diálogo.
- Saída do avaliador é `ImpactProposal`, **não** a aplicação de efeito. Os efeitos exigem gates/host quando mecânicos, evidence/branch para narrativa e dedup com `event_id+rule_id+scope+epoch`.
- Conflitos: por domínio/modificador, acumular apenas quando política explícita; usar caps/decay e precedência versionada; jamais somar infinitamente bônus ou penalidades.

## 6. Separação entre efeito direto e indireto

| Fase | Exemplo SINTÉTICO (não evento canônico FR) | Resultado permitido |
|---|---|---|
| Evento factual | 'Alerta no Porto-Exemplo', confirmado no ramo | trigger potencial na região e tempo certos |
| Direto | intensificação de patrulhas nas estradas | **proposta** de modificador limitado; nunca criar patrulha sem adapter/gate |
| Indireto | menor ocorrência de roubos após mudança material confirmada | dependência do efeito direto e janela, com cap e evidências |
| Informação | rumores chegam a tavernas por mensageiros | difusão causal por viagem/canal; NPC recebe apenas se evidenciado |
| Exceção | grupo neutraliza a causa na campanha | regra passa a INACTIVE/DIVERGED; não apagar fatos anteriores |

Eventos canônicos não são scripts de combate: **guerra histórica não dispara soldados/spawns do nada**. Efeito HIGH/irreversível permanece aguardando autorização DEC-027/034 e confirmação do host DEC-011/012.

## 7. Fluxo determinístico proposto

```text
1. carregar KPack pinado (DEC-063), catálogo temporal do ano DR e branch autorizado;
2. buscar eventos por ano/janela e não revelar registros futuros/privados;
3. intersectar `region_id`, `location_id`, `location_tag` e status da fase;
4. checar fonte, precisão temporal, contradições e condições IF/ELSE tipadas;
5. avaliar pré-requisitos e exclusões (arcos, divergências, facções, flags);
6. identificar impacto direto permitido e sua classe de risco;
7. emitir proposta deduplicada, com explicação auditável de *por que disparou*;
8. materializar efeitos via política, Action Gateway e recibo do host, se válido;
9. registrar `AppliedImpact`; só então avaliar impactos indiretos e difusão;
10. em save/restore, reindexar e reconciliar receipts; nunca repetir efeito por reload.
```

**Escalabilidade:** offline compilar catálogo em índices por ano e região; runtime avalia apenas as regras candidatas quando há transição de tempo, mudança de estado, entrada em área ou evento de campanha. Caches de leitura podem ser invalidáveis por `KPack hash`, `branch epoch`, `region-state revision` e `rule revision`. Não é loop de IA a cada tick.

## 8. Estrutura física recomendada

```text
knowledge/periods/1369-DR/                 # cânone isolado por ano: não reescrever
  events/                                   # arquivos curados/versões de fonte
knowledge/periods/1370-DR/
knowledge/packs/<pack-id>/manifest.json      # manifest versionado/pinado (candidato)
world-rules/chronology/impact-rules/         # DSL compilável, não cânone
world-rules/chronology/locations/            # taxonomia e vínculos verificáveis
campaigns/<campaign>/<branch>/ledger/        # fatos, efeitos, receipts e memória
examples/chronology/                         # fixtures sintéticas, NÃO publicar como cânone
```

Os diretórios além de `knowledge/periods/...` são **proposta de organização**, não prova de implementação nem substituição da partição física DEC-060. A estrutura real da campanha deve respeitar o layout de `knowledge/campaigns` existente e a escolha futura de backend.

## 9. Exemplo de tabela amigável (somente cenários sintéticos)

| Evento (teste) | DR | Mês | Abrangência | Local | Direto | Indireto |
|---|---|---|---|---|---|---|
| Alerta no Porto-Exemplo | 1369 | 7 | Regional | Estrada e portão da Região-Exemplo | Propor patrulhas +1 (cap) | Após confirmação, propor risco de saque -1 |
| Rumor na Taverna-Exemplo | 1369 | não informado | Local | Taverna | Nenhum efeito automático: aguardar precisão/entrega por canal | Possível conversa, apenas após aquisição causal |

Os nomes são **ficcionais para teste**. A matriz original `docs/14-matriz-eventos-excecoes-repercussoes.md` tem eventos reais **ainda sujeitos a verificação de fontes**, que não devem ser convertidos automaticamente para regras acionáveis.

## 10. Critérios de aceite originais da proposta v9.1

1. Ano futuro ou mês conhecido diferente = **0 propostas**, sem spoiler de NPC.
2. Ano conhecido mas mês desconhecido = **não inventar mês nem ativar efeito por default**.
3. Eventos disputados = **pendentes de curadoria**, não eventos executáveis.
4. Região/tipo de local não afetado = **0 propostas**.
5. A mesma regra após reload = **0 novas aplicações** sem evento/epoch legítima.
6. `GLOBAL` não significa conhecimento global, nem spawn global.
7. Efeito indireto só após pré-condição e confirmação do efeito pai.
8. Divergência confirmada do grupo suspende efeitos oficiais incompatíveis.
9. WorldState não pode contradizer recibos host nem criar itens/combate sem gate.
10. LLM indisponível: avaliador e filtros continuam operacionais.
11. Performance: custo proporcional a eventos candidatos por área/período, não todo lore.
12. ACL: personagens só recebem informações que realmente aprenderam.
13. Calendário DR tem meses e feriados próprios, sem aproximação gregoriana.
14. Regras/catálogo versionados e fixados por campanha (KPack + ruleset revision).
15. Efeitos agregados com caps e policy anti-feedback infinito.
16. Capabilities verificadas por build antes de materializar efeitos no jogo.
17. `DORMANT` não simula cada evento minuto a minuto; catch-up limitado e auditável.
18. Importação de 1368 DR para campanha 1369 oferece legado, não reexecuta 1368.
19. Restauro de save velho mantém overlay coerente, sem vazamento de futuro.
20. Locais não mapeados ao build permanecem `UNKNOWN`, sem atuação mecânica.

**Entregáveis unitários (sem game integration):** JSON Schema, fixtures sintéticas, avaliador determinístico de referência e testes unitários em `examples/chronology/`. Eles exercitam somente filtros e emissão de propostas, não fazem deploy de regras ou eventos canônicos em FR.

## 11. Alternativas da deliberação DEC-096 — histórico da proposta

- **A:** planilha/IF-ELSE fixos e manuais para cada acontecimento.
- **B:** LLM consulta lore e decide livremente quando/onde aplicar repercussões.
- **C recomendada:** **catálogo cronológico por ano DR + regras declarativas determinísticas + índices temporais/espaciais e ledger causal; efeitos mecânicos apenas com gates e host; LLM apenas como refinador textual autorizado.**

**Estado atualizado em v9.2:** **DEC-096/C APROVADA COMO ARQUITETURA**, com ADR-0091 e documento técnico 96 consolidado. O texto acima representa o estágio de proposta da v9.1; a próxima deliberação é DEC-097. Nenhuma implementação de motor ou teste integrado foi comprovado.

## Integração DEC-097/C — Discovery v9.3

A ideia original da matriz recebeu complemento DEC-097/C para múltiplos impactos na mesma variável sem último efeito vencer; histórico preservado.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Ruleset histórico calcula candidatos apenas, não assume propriedade da área/entidades.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Rulesets históricos usam critérios narrativos curados, não future branches extraídos de scripts.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Semantic quest milestones are curated technical metadata, separate from FR historical canon partitioned by year DR and private campaign overlays. UNKNOWN, AMBIGUOUS or stale milestones cannot trigger chronology, historical effect or materialization; lore packs do not authorize interpreting runtime flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Prazos DR e matriz histórica são escopos distintos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Matriz histórica e calendário DR não devem disparar pagamento contratual. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
