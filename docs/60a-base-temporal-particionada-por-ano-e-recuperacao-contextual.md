# Adendo DEC-060/C — Base de conhecimento particionada fisicamente por ano (DR)

**Discovery v5.6.1 · Decisão aprovada como emenda à ADR-0055 · não é SPEC nem software funcional.**

## Requisito central

O corpus curado de Forgotten Realms será mantido em **diretórios separados por período**, inicialmente por ano do calendário de Dale Reckoning (DR). Para diálogos situados em 1369 DR, a primeira fonte de busca será o diretório `1369-DR`. O armazenamento não deverá transformar todos os anos em um único corpus de fatos sem fronteiras temporais. Esta é uma exigência de **organização física**, além da filtragem lógica.

## Esboço real dos diretórios, ainda sem fatos importados

```text
knowledge/
  README.md
  periods/
    _TEMPLATE-PERIOD.md
    1369-DR/
      README.md                   # manifesto/cobertura do ano
      chronology/README.md       # marcos datados
      events/README.md           # acontecimentos/eventos
      organizations/README.md    # organizações por validade temporal
      guilds/README.md           # guildas e associações
      characters/README.md       # pessoas/identidades
      regions/README.md          # lugares, governos, relações
    1370-DR/
      README.md                   # exemplo vazio, isolado de 1369
  campaigns/
    README.md                     # overlay por campanha/ramo/ano; sem saves reais
```

Os arquivos `README.md` de categorias são **andaimes de curadoria**. Não afirmam que 1369 ou 1370 estejam inventariados, que um evento canônico ocorreu, nem definem tecnologia de armazenamento final.

## Algoritmo conceitual de recuperação — sem execução implementada

1. Obter **tempo DR confirmado**, campanha, ramo, região, falante, público e finalidade do pedido. Não derivar o ano exclusivamente de texto do NPC ou do modelo.
2. Selecionar **um diretório primário** `knowledge/periods/{world_year}-DR/` e suas categorias pertinentes, sem abrir automaticamente outros anos.
3. Consultar registros específicos com fontes/precisão temporal e validade **na data**. Uma fonte de `1369-DR` pode narrar evento anterior somente como referência histórica explícita, com proveniência de seu ano real.
4. Para uma pergunta sobre o passado, abrir **somente** as partições históricas necessárias e autorizadas; resolver continuidade temporal por `valid_from/valid_to` e versões. A sequência temporal não exige copiar cada evento antigo para a pasta de todos os anos subsequentes.
5. Consultar sobreposições (*overlays*) de eventos **confirmados nesta campanha e ramo**, por época e revisão. A história da campanha não altera os fatos curados do cânone.
6. Aplicar ACL de jogador/NPC, *learned_at*, propagação geográfica, segredo e status `rumor | fact | proposed` **antes** de montar o contexto enviado ao modelo, inclusive em nó LAN.
7. Submeter a saída à validação DEC-060: fonte, cronologia, coerência causal, confiança e gate de risco. Não liberar efeito mecânico sem gateway/receipt do host.

## Exemplos hipotéticos de consulta

- **NPC em 1369 DR pergunta sobre uma guilda ativa naquele ano:** consultar `1369-DR/guilds/`; se necessário, buscar referências a origem anterior e verificar se ela continuava vigente. O NPC ainda precisa ter adquirido esse conhecimento legitimamente.
- **Jogador pergunta sobre evento ocorrido em 1368 DR:** buscar explicitamente `1368-DR/events/` **se** esse diretório estiver curado e a consulta for autorizada; não transformar o evento em conhecimento automático de qualquer NPC.
- **Registro presente somente em 1370 DR:** não usá-lo como acontecimento passado ou condição vigente em 1369 DR. Uma profecia eventualmente conhecida é outro tipo de registro, com status e evidência próprios.
- **A campanha divergiu em 1369 DR:** prevalece o overlay confirmado daquela campanha/ramo para o estado atual, sem reescrever o catálogo canônico de 1369.

## Metadados candidatos por entrada

`record_id`, `partition_year_DR`, `valid_from_DR`, `valid_to_DR`, `date_precision`, `category`, `entity_id`, `region_ids`, `source_refs`, `verification_status`, `variant_group_id`, `revision`, `visibility_scope`, `ingested_at`.

`partition_year_DR` informa **onde se encontra o registro**, enquanto `valid_from_DR/valid_to_DR` definem sua **vigência**; não presumir equivalência. `source_refs` aponta para bibliografia/trecho identificado e resumos próprios, não reproduções extensas. Nenhuma destas chaves é schema definitivamente aprovado.

## Índices e privacidade

- Índice opcional entre anos contém **rotas para partições**, IDs e metadados mínimos para seleção, sem materializar um corpus de respostas/prompt com conteúdos de todas as épocas.
- Busca vetorial, se aprovada, deve obedecer à fronteira anual **durante a recuperação**, e não apenas filtrar os resultados depois de já entregar trechos ao modelo.
- Caches isolados por campanha/ramo/ano e revisão, identidade/permissões/finalidade; rejeitar resultados `stale` e processos em workers revogados.
- A existência de um arquivo, título ou índice não deve vazar segredo; arquivos do cânone e histórias de personagens possuem políticas de acesso distintas.

## Riscos e verificações

**Riscos:** conhecimento de ano futuro; apagamento de fatos anteriores ainda vigentes; divergência de ramo misturada com cânone; personagem onisciente; dependências entre pastas quebradas; custos de leitura excessivos; importações com data imprecisa; conteúdo obsoleto em cache.

**Testes candidatos:** cenário 1369 isolado de 1370; evento anterior ainda vigente; declaração só datada por ano; ano inexistente; NPC não informado; evento futuro como profecia marcada; manifestação contraditória de duas fontes em 1369; mod de jogo de outra época; branch divergente; save anterior; LAN e revogação; cache stale; decisão HIGH; recuperação por fonte exata; catálogo vazio; busca global indevida. **Todos pendentes.**

## Decisões preservadas

- DEC-008/009: event sourcing, cânone base e divergências por causalidade.
- DEC-022/023: relógio configurável; ano 1369 DR é referência inicial de testes, **não ano fixo obrigatório**.
- DEC-028/029: conhecimento individual e rumores, sem onisciência.
- DEC-053/054: recuperação coordenada do estado narrativo/mecânico.
- DEC-058/059: acesso LAN e roteamento por permissões.
- **DEC-061 ainda aberta:** como resolver fontes contraditórias **dentro do mesmo ano**, decidir versões canônicas e registrar curadoria. A separação física por ano não soluciona sozinha esses conflitos.

## Integração da DEC-061/C — conflito dentro da mesma partição (Discovery v5.7)

**DEC-061 aprovada** no ADR-0056 e documento 61. A separação física anual permanece **obrigatória**; os diretórios `1369-DR` e `1370-DR` não são consolidados nem substituídos por um único corpus. Cada registro futuro na partição pode referenciar `source_id`, edição, precisão, perspectiva e `conflict_set_id`. A consulta anual deverá considerar status curatorial antes de apresentar alegação como fato.

Múltiplas fontes sobre o mesmo ano podem refletir sucessão dentro do ano, diferença de região/entidade, rumor, retcon ou contradição real. Manter versões concorrentes; sem decisão curada e válida no escopo, usar `UNRESOLVED` e falha segura. Quando existir resolução, guardar as fontes e alternativas com revisão, razão e responsável. Um worker LAN/LLM não tem autoridade para transformar incerteza em fato.

**DEC-062 continua aberta** para ingestão de fontes e fluxo de publicação. Nenhum conteúdo de lore foi preenchido nesta atualização.

## Integração DEC-062/C — ingestão escreve somente na partição anual aprovada

**A separação física anual desta decisão é preservada integralmente.** O importador híbrido DEC-062/C coloca candidatos em staging privado, não nos diretórios de lore. Um publisher autorizado e auditado escolhe `knowledge/periods/<ano>-DR/<categoria>/` apenas depois de validar data/validade, proveniência DEC-061, direitos, conflitos e risco. Fonte sem ano → revisão, **não** publicação em ano sugerido pelo modelo. Histórico antecedente pode ser vinculado apenas sob continuidade documentada; fatos futuros não vazam. Os diretórios de 1369/1370 ainda não contêm fatos de lore importados. Nenhum índice único pode conceder leitura irrestrita. Doc. 62 e ADR-0057 definem a política; SPEC/POC pendentes.

## Integração DEC-063/C — versionamento não une diretórios de anos DR (v5.9)

**Reafirmação explícita do adendo DEC-060:** cada revisão canônica está vinculada a um **diretório físico do ano DR**. O *Knowledge Pack* de uma campanha é um **manifesto de referências a revisões anuais**, nunca repositório único com lore de todas as épocas. Uma consulta em 1369 DR resolve a revisão publicada de `1369-DR` fixada no pack e aplica vigência/ACL quando busca histórico anterior; dados de 1370 não são fatos consumados. Adoção de revisão nova é controlada DEC-063 e não modifica overlays do ramo; pastas existentes ainda não contêm lore real.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

**Manter DEC-060 sem alterações:** o lore canônico permanece em **diretórios físicos separados por ano DR**. A DEC-064/C não cria um banco global de lore nem armazena crenças subjetivas nessas pastas; elas ficam em overlays privados de campanha/ramo/NPC. Consultas primárias seguem relógio e revisão anual pinada DEC-063, antecedentes só com vigência/ACL, nunca futuro como ocorrido. Conhecimento subjetivo requer evidência recebida.


### Memórias de NPC não criam corpus canônico global — DEC-065/C (Discovery v6.1)

Sínteses e âncoras pessoais pertencem ao overlay da campanha/ramo, com IDs de NPC, fonte e permissões. Nunca gravar episódio pessoal como fato em `knowledge/periods/<ano>-DR/` nem combinar lore de vários anos sem vigência/ACL. O cache de uma síntese não remove nem substitui as pastas **fisicamente separadas por ano** da DEC-060.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Individualização DEC-067 escreve somente no overlay de campanha/ramo, jamais nos diretórios canônicos anuais. Lore por ano DR continua fisicamente segregado DEC-060.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Eventos de NPC fora de cena DEC-068 são armazenados no overlay privado da campanha/ramo, jamais dentro da partição anual de lore. Consulta sobre ano DR atual respeita diretório físico; catch-up não autoriza acessar futuro como passado.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: grafo geográfico temporal referencia `knowledge/periods/<ano>-DR/`, preservando partição física, vigência e revisão; planos de NPC no overlay, não misturados com lore.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

Incidentes de viagem DEC-070 consultam `knowledge/periods/<ano>-DR/` de modo temporalmente autorizado e persistem em overlay privado, sem fundir diretórios de eras ou registrar combate ficcional como cânone.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

DEC-071 não muda a partição física `knowledge/periods/<ano>-DR/`: fato canônico segue no diretório anual e incidentes de campanha, handoffs, NPCs e receipts ficam exclusivamente no overlay do ramo.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

DEC-072 não consolida os diretórios `knowledge/periods/<ano>-DR/`; o catálogo de templates é operacional, separado do cânone físico anual e das memórias por campanha.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Limpeza local não tem permissão para editar `knowledge/periods/<ano>-DR/`; overlay privado da campanha mantém efeitos confirmados.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

DEC-074 preserva diretórios canônicos separados por ano DR. Rumores e impactos do jogo pertencem ao overlay privado por campanha/ramo/tempo, não a knowledge/periods/ em nenhum ano. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Crédito cooperativo e testemunhos são dados de campanha/ramo e não devem ser gravados em knowledge/periods/<ANO>-DR/; nunca misturar corpus canônico e participação.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Separação anual física continua integral; identidades, personas e segredos dinâmicos são overlay de campanha, jamais indexados como lore público do ano DR. Links têm validade temporal e não consultam futuro.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

DEC-078 conserva knowledge/periods/<ANO>-DR/ fisicamente isolado. Caso judicial inventado no gameplay vive no overlay, e regras regionais precisam de ano DR e proveniência.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Jurisdicões e acordos canônicos DEC-079 podem ser consultados por diretório físico anual conforme vigência; pedidos ficcionais de campanha não entram no corpus knowledge/periods.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

DEC-080 preserva physically-partitioned knowledge/periods/<ANO>-DR; ordens/revogações são overlay de campanha e não fonte canônica publicada. Não consultar normas futuras como vigentes.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

DEC-081 não escreve processos, vítimas ou restituições em knowledge/periods/<ANO>-DR/; ler normas por contexto sem fundir eras, persistir em overlay separado.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Corpus canônico em pastas físicas anuais não recebe denúncia/investigação da campanha; buscar lei/competência por ano vigente.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Depoimentos/identidades dinâmicas não entram em knowledge/periods/<ANO>-DR/; ACL e prova no overlay. Lore futuro não é vazado a testemunha.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Ameaças e planos ficam no overlay privado por ramo, sem gravar no conhecimento anual fisicamente separado; busca não usa futuro DR como ocorrência.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Cânone `knowledge/periods/<ANO>-DR/` segue fisicamente segregado; lugares públicos podem integrar lore anual, mas esconderijos/canais/rotas de campanha nunca entram no índice canônico.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

A desinformação deliberada pertence ao overlay da campanha e não aos diretórios canônicos `knowledge/periods/<ANO>-DR/`. Busca por ano DR não faz NPC saber rumor futuro.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Manter fisicamente o cânone por ano DR; trajetórias de agentes duplos dinâmicos são fatos da campanha em overlay por branch, jamais conteúdo retroativo do lore anual.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Lore físico anual por ano DR é imutável pela contratação; conhecimento de fonte e acordos ficam em overlay por campanha/branch, sem consultar fatos futuros.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Fatos canônicos continuam particionados em `knowledge/periods/<ANO>-DR/`; informes do mundo jogado não são publicados nessas pastas. Consulta temporal somente ao período permitido.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Dossiês ficam no overlay da campanha, não nas partições físicas canônicas anuais; referências a lore respeitam ano DR e Knowledge Pack sem futuro retroativo.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Busca temporal mantém `knowledge/periods/<ANO>-DR/` física; plano só referencia conhecimento canônico admissível ao ano e overlay privado do ramo.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Partições físicas canônicas anuais permanecem separadas; operação pertence ao overlay privado e apenas consulta o ano DR e Knowledge Pack pinado.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

A DEC-093 não altera separação física de lore por ano DR. Reservas e janelas temporais de missão são overlay de campaign/branch e nunca antecipam fatos do futuro.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Cânone permanece fisicamente em knowledge/periods por ano DR; deadlocks, leases e starvation são dados de overlay privados, nunca lore canônico.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-096 (proposta): catálogo de eventos por ano DR no conhecimento físico DEC-060, sem uma tabela central que reintroduza todo o lore futuro no contexto; filtro por versão KPack/ano e overlay.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Dados de lore particionados por ano DR permanecem somente-leitura e não autorizam patch de estado de quest.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Períodos históricos particionados por ano DR são somente-leitura e independentes de estados de quest internos.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Catalogues by exact build/modpack/quest/script fingerprint, curated proof of semantic milestone and valid transition; an observed flag or stage is never an authorized quest write or host receipt. On patch or restore, invalidate semantic cache and avoid generic stage inference. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para particionamento por ano DR e cache por audiência/branch/epoch, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para particionamento físico de lore anual, ACL e branches, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Knowledge Pack temporal não altera datas pactuadas na campanha. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Packs canônicos isolados por ano DR não materializam automaticamente obrigações. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
