# DEC-061 — Governança de fontes, contradições e curadoria do cânone por período

**Discovery v5.7 · DEC-061 opção C aprovada · ADR-0056 · desenho candidato para SPECS, não implementado.**

## 1. Propósito e fronteiras

Registrar, comparar e consultar afirmações de fontes de Forgotten Realms preservando **quem afirmou o quê, em qual obra e contexto, para qual ano e região de Faerûn**, com possibilidade de interpretações conflitantes. Uma resposta elegante de IA não é prova de verdade. A decisão **não** substitui a DEC-060/C: a base continua fisicamente dividida por ano DR, e a história de cada campanha continua em overlays separados.

**Não confundir:**

| Objeto | Significado | Pode virar fato do mundo diretamente? |
|---|---|---|
| `Source` | Referência identificável de uma obra/material, edição/versão e localização | Não |
| `Claim` | Alegação vinculada a uma fonte e contexto | Não |
| `ConflictSet` | Alegações potencialmente incompatíveis sobre uma mesma entidade/atributo/época | Não |
| `CuratedResolution` | Interpretação homologada, com justificativa, escopo, revisão e alternativas | Somente após filtros de período, ACL, política DEC-060 e contexto da campanha |
| `Rumor/Belief` | Informação atribuída à perspectiva/experiência de um agente | Não como fato; pode ser relatada como crença autorizada |
| `CampaignEvent` | Ocorrência confirmada na campanha/host/log narrativo | Sim, apenas no ramo e escopos corretos, respeitando autoridade e confirmação |

## 2. Armazenamento: um diretório físico por ano, sem corpus monolítico

```text
knowledge/
  periods/
    1369-DR/
      chronology/        # somente registros pertinentes a 1369 DR
      events/
      organizations/
      guilds/
      characters/
      regions/
      README.md           # manifesto de cobertura, sem implicar fatos importados
    1370-DR/
      README.md           # outra partição física, independente
    _TEMPLATE-PERIOD.md
  campaigns/             # overlays separados por campanha/ramo/ano/revisão
```

- Preservar **fronteira física anual**, inclusive se futuramente houver índice vetorial: índice global pode conter **apenas referências de roteamento/metadata autorizados**; conteúdo e embeddings pesquisáveis não ultrapassam silenciosamente fronteiras anuais ou ACL.
- Ao consultar 1369 DR, selecionar primeiro `1369-DR`. Abrir explicitamente partições antecedentes somente com `as_of` e `validity` coerentes; uma referência anterior pode estar ainda válida, mas isso precisa ser comprovado.
- Um conteúdo **publicado depois** da época representada pode descrever legitimamente o passado: distinguir **ano editorial** de **ano DR do acontecimento**. Ser posterior na publicação não significa que o acontecimento ocorra no futuro; tampouco legitima aceitar um retcon sem análise.
- `coverage=EMPTY/PARTIAL/CURATED` e `UNKNOWN` nunca autorizam completar lacunas com um ano vizinho ou uma alucinação.
- Criar *referências lógicas* a uma entidade que atravessa anos sem copiar todo o corpus para cada ano; integridade do vínculo e vigência serão verificadas por SPECS/POCs.
- Sem fatos reais de lore importados nesta versão. Todos os exemplos são fictícios e ilustrativos.

## 3. Metadados candidatos de uma alegação

| Campo | Função |
|---|---|
| `claim_id`, `entity_id`, `predicate` | Identificação estável e atributo consultado |
| `source_id`, `source_location` | Referência à obra/material e à passagem verificável |
| `source_type`, `edition`, `source_version`, `published_at` | Contexto editorial real; valor desconhecido fica marcado |
| `asserted_value_summary` | Resumo factual original e mínimo, sem reproduzir trechos extensos |
| `world_year_DR`, `valid_from`, `valid_to`, `time_precision` | Pertinência temporal e precisão do relato |
| `region`, `perspective`, `epistemic_status` | Local, quem afirma e se é testemunho, rumor, proposição, fato etc. |
| `claim_status`, `conflict_set_id` | Estado de curadoria, concorrência ou contestação |
| `curation_revision`, `reviewer_id`, `decision_reason` | Auditoria e fundamentação quando houver resolução |
| `license_scope`, `read_scope` | Uso autorizado e restrições de leitura/distribuição |

**Importante:** o esquema acima é **candidato**, não formato implementado. Dados não verificados permanecem `UNKNOWN` e não recebem valor inventado.

## 4. Estados e resolução contextual

Estados de trabalho propostos:

- `UNREVIEWED`: foi identificada uma alegação, mas ainda não verificada.
- `SOURCED`: a referência foi localizada e o resumo corresponde à fonte, sem significar preferência canônica.
- `CONFLICTED`: mais de uma alegação pertinente é potencialmente incompatível.
- `UNRESOLVED`: análise não permitiu conclusão contextual segura.
- `CONTEXTUALLY_RESOLVED`: há justificativa documentada para escopo delimitado, mantendo alternativas.
- `SUPERSEDED_IN_SCOPE`: determinada variante não é escolhida **nesse escopo**; não é apagada do catálogo.

Esses estados não são uma enumeração final de API. A resolução deverá distinguir pelo menos:

1. **Diferença temporal verdadeira:** duas lideranças em datas distintas, mesmo no mesmo ano; precisar da granularidade disponível.
2. **Diferença geográfica ou institucional:** entidades/filiais distintas ou homônimos; identificar antes de comparar.
3. **Perspectiva versus fato:** relato de um personagem, propaganda, rumor ou narrativa não confiável não é uma verdade objetiva.
4. **Edição/revisão editorial:** possível retcon ou mudança de regras/setting; anotar sem aplicar hierarquia universal mecânica.
5. **Contradição factual irresolvida:** conservar ambas as fontes e marcar `UNRESOLVED` até nova evidência ou decisão curatorial explicitamente autorizada.
6. **Divergência da campanha:** evento dos jogadores depois de start alterou o mundo naquele ramo; não é erro da fonte nem correção do cânone.

Um LLM pode **identificar candidatos a conflito**, sugerir análise e apresentar referências que já foram autorizadas; não pode alterar status para `CONTEXTUALLY_RESOLVED` nem gravar fato canônico por sua própria saída. Curadoria requer política de revisão identificável e trilha auditável.

## 5. Exemplo sintético (NÃO é lore de Forgotten Realms)

Um grupo fictício denominado `Guilda Exemplo` tem dois relatos distintos **dentro do ano 1369 DR**:

- `C1369-01`: fonte `SRC-ALFA`, liderança por uma pessoa no primeiro semestre; `time_precision=semester`.
- `C1369-02`: fonte `SRC-BETA`, liderança por outra pessoa no segundo semestre; `time_precision=semester`.

**Resultado correto:** não presumir contradição se há evidência de sucessão. Se as fontes alegarem simultaneidade excludente e não houver evidência suficiente, registrar `UNRESOLVED`; o NPC não deverá declarar certeza. Se uma campanha trocar a liderança por ação confirmada do grupo, registrar a mudança no **overlay daquela campanha** sem alterar `C1369-01/02`.

## 6. Caminho de consulta e validação (conceitual)

```text
Estado confirmado (ano DR, data, região, ramo, speaker, ACL)
   -> roteador de partição física do ano vigente (DEC-060)
   -> categorias de contexto, com referências anteriores só se autorizadas
   -> alegações com proveniência/versão/vigência e conflitos associados
   -> seleção de resolução contextual, quando existente e vigente
   -> filtro de conhecimento legítimo do NPC + rumor/crença
   -> montagem mínima de contexto para host/modelo LAN autorizado
   -> DEC-060 (validação de saída, risco, canon/quest/build)
   -> fala permitida OU REVISE/DEFER/ESCALATE
   -> efeito persistente apenas com confirmação de origem/host/gateway
```

**Princípios de falha segura:** ausência de fonte, conflito irresolvido, data insuficiente, `permission_epoch` desatualizado, ramo errado, partição ausente, worker revogado ou verificador indisponível **não** produzem uma resposta factual assertiva por default. Para diálogos de baixo risco, falas neutras previamente validadas podem ser empregadas sem inventar fatos.

## 7. Gestão da curadoria e publicação

- **Entrada:** fonte identificada, escopo legal verificado, alegações com referência/edição/ano; registro inicial `UNREVIEWED` até revisão.
- **Triagem:** checar duplicações de fontes, identidade de entidade, incerteza e precisão temporal; associação ao diretório correto.
- **Comparação:** examinar candidatos sobre mesma entidade/atributo e janela temporal; reconhecer mudança legítima ou disputa.
- **Decisão:** curator autorizado registra `reviewer`, justificativa, alternativas, referência, regra/versão, escopo e timestamp de revisão.
- **Publicação:** criar revisão imutável ou versionada da partição, e somente então disponibilizar a consulta; nunca sobrescrever silenciosamente fatos anteriores.
- **Retificação:** manter histórico de decisões, invalidar cache e testar efeito sobre contextos/diálogos; não reescrever automaticamente campanhas em andamento.
- **Escopo externo:** importação de obras e automação do pipeline ficam para DEC-062; licenças não são inferidas do uso privado.

## 8. Segurança, autorização e auditoria

- Um `source_ref` pode apontar para arquivo local legítimo; **não** autoriza redistribuir livros, diálogos, ilustrações nem assets no pacote Discovery.
- Texto recuperado é dado, não instrução do sistema; neutralizar prompt injection em referências e anotações.
- Curador vê referências conforme acesso; NPC vê somente informações aprendidas por vias legítimas (DEC-028/029).
- Logs registram IDs de alegações/conflitos/resoluções e revisões, não segredos de personagens nem textos proprietários extensos.
- `resolution_revision`, `partition_revision`, `campaign_id`, `branch_id`, `world_revision`, `build_fingerprint` e `permission_epoch` devem acompanhar decisões em que forem pertinentes.
- Alterações pós-checkpoint ou migração não substituem o save/receipt do host. Nenhuma API mecânica foi demonstrada.

## 9. Testes candidatos de aceitação (não executados)

1. `T061-01`: duas fontes divergentes de 1369 DR permanecem como duas alegações ligadas ao conflito.
2. `T061-02`: não produzir alegação conciliadora inventada.
3. `T061-03`: mudanças em meses diferentes do mesmo ano não geram contradição falsa.
4. `T061-04`: fonte de 1370 não aparece em conversa de 1369 como evento consumado.
5. `T061-05`: registro histórico de 1368 ainda vigente pode ser buscado por abertura explícita.
6. `T061-06`: ausência de precisão temporal vira indeterminação, não data fabricada.
7. `T061-07`: fonte editorial recente sobre evento antigo é classificada por ano DR do evento, sem assumir superioridade automática.
8. `T061-08`: retcon suspeito é marcado como variante, sem substituição silenciosa.
9. `T061-09`: rumor de NPC pode ser citado como rumor, não como fato.
10. `T061-10`: texto propagandístico não é aceito como verdade única.
11. `T061-11`: homônimos e filiais de guilda não viram um conflito artificial.
12. `T061-12`: duas contradições reais mantêm estado `UNRESOLVED`.
13. `T061-13`: alto impacto com conflito irresolvido é bloqueado/escalado.
14. `T061-14`: narrativa de baixo risco pode recorrer a texto neutro validado.
15. `T061-15`: LLM sugere revisão, mas não consegue homologá-la.
16. `T061-16`: decisão curada tem reviewer, justificativa, escopo e revisão.
17. `T061-17`: revisão curada conserva versões rejeitadas em determinado escopo.
18. `T061-18`: curadoria de 1369 não muta a partição física de 1370.
19. `T061-19`: nova revisão invalida cache relevante sem liberar segredos.
20. `T061-20`: NPC sem acesso ao fato não o menciona, mesmo com resolução curada.
21. `T061-21`: dois NPCs podem manter crenças distintas sem reescrever fatos.
22. `T061-22`: overlay de campanha substitui contexto do ramo sem alterar o corpus canônico.
23. `T061-23`: ramo B não recebe divergências exclusivas do ramo A.
24. `T061-24`: retorno stale de worker LAN/LLM é rejeitado.
25. `T061-25`: tentativa de busca em índice all-years é rejeitada antes do prompt.
26. `T061-26`: log de revisão não expõe segredo nem trecho protegido extenso.
27. `T061-27`: queda/indisponibilidade de fonte retorna `UNKNOWN/DEFER`, não inventa fato.
28. `T061-28`: simulação BG2:EE/EEex/multiplayer não é declarada testada sem POC real.

## 10. Dependências e próximo passo

- Integração real, testes de busca, seleção de base, protocolos de curadoria, métricas e licença por obra precisam de SPECS e POCs.
- **DEC-006/013/015/018 seguem abertas.** DEC-060/C e o adendo físico anual permanecem obrigatórios.
- **DEC-062 — ainda aberta:** política de ingestão de fontes e atualização curada das partições anuais, incluindo revisão humana, versionamento e validação de permissões de uso.

## Integração DEC-062 — ingestão respeita proveniência e conflitos

O pipeline híbrido (ADR-0057 e doc. 62) deve identificar/registrar `Source`, `Claim`, `ConflictSet` e `CuratedResolution` conforme esta DEC-061. IA auxilia triagem/classificação, **não** consolida fontes conflitantes nem homologa curadoria automaticamente. Fontes com dados de edição, região, data ou direitos incertos ficam em revisão; publicação apenas na partição física anual correta da DEC-060, com manifestos e auditoria. Conflitos existentes não são sobrescritos por nova fonte; alternativas ficam disponíveis para revisão. A DEC-063 tratará a vinculação das revisões de lore às campanhas em andamento; a importação não promove retcon mecânico.

## Integração DEC-063/C — fontes e conflitos atravessam revisões sem perda (v5.9)

*Knowledge Packs* versionados apontam para revisões anuais publicadas, conservando `Source`, `Claim`, `ConflictSet`, decisões curatoriais, evidências e intervalos DR. O diff identifica quando uma nova resolução mudaria informação usada pela campanha ou contradiz história confirmada. O anfitrião não pode receber retcon invisível; a migração exige revisão contextual DEC-061, staging/publicação DEC-062 e pin DEC-063. Uma revisão temporal não transforma automaticamente crenças individuais de NPCs.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Proveniência DEC-061/C continua independente das crenças DEC-064/C. Uma resolução curada de conflito em 1369 DR não apaga rumor antigo ou episódio NPC; NPC só reavalia crença quando legitimamente recebe evidência. `UNRESOLVED` não se converte em fato por aceitação psicológica. Partições físicas anuais DEC-060 e versões de fontes são preservadas.


### Síntese de memória subjetiva e proveniência — DEC-065/C (Discovery v6.1)

A memória consolidada de NPC pode resumir que ele acredita numa alegação conflitante, com fonte e incerteza, sem fundir reivindicações incompatíveis ou substituir resolução curatorial. Claims do catálogo seguem por ano DR com proveniência DEC-061; síntese pessoal não se torna fonte oficial.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Identidade NPC promovida não resolve conflitos de fontes nem transforma suspeita de um figurante em fato curado; manter proveniência DEC-061.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: fontes divergentes sobre rotas e portos devem reter claims e revisão curada; não fundir trajetos contraditórios pela IA.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 não pode criar incidente objetivo de estrada a partir de fontes cronologicamente incompatíveis ou conflitantes não resolvidas; preservar proveniência e estado de incerteza.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Recontar um encontro DEC-071 não substitui fontes históricas; rumores ou falas NPC devem preservar proveniência e separar interpretação do evento confirmado. Cânone por ano permanece independente.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Conflitos de fonte DEC-061 não são resolvidos pela escolha de template DEC-072. Propostas de encontro usam fontes temporais e conflitos curados; dúvidas relevantes bloqueiam afirmações definitivas.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Proveniência DEC-061 cobre fatos históricos; DEC-074 acrescenta cadeia auditável de testemunhos/relatos, sem transformar alegações de NPCs em fontes de cânone. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Fonte canônica pode descrever alias histórico com proveniência, mas isso não autoriza conhecer o vínculo pessoal de um PC em campanha; fatos de campanha permanecem privados por branch.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Autoridade e norma usadas em DEC-078 exigem fonte/região/ano e curadoria; duas descrições históricas incompatíveis geram conflito curatorial, não código legal inventado.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Conflitos de fontes sobre relações políticas/jurídicas ficam explícitos em DEC-079; não decidir competência por consenso LLM nem por popularidade da fonte.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Competência de autoridade e regras DEC-080 derivam de fontes temporalmente curadas; documento de campanha não substitui lore canônico nem cria tratado histórico sem evidência.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Normas e competências de reparação por época precisam de fonte/curadoria; testemunhos de dano da campanha mantêm proveniência e não viram cânone público.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Fontes canônicas contraditórias sobre competência requerem curadoria; depoimentos de campanha com proveniência não viram cânone editorial automaticamente.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Proveniência DEC-061 aplica-se também a cadeia de evidência, mas testemunho de campanha não vira fonte de cânone; relatórios derivados não são independentes.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Provas narrativas de ameaça têm cadeia de origem e contraditório, mas não são automaticamente fatos de cânone ou culpa de instituição.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

A base canônica e os relatos de espionagem são domínios distintos; alegação de informante não substitui fonte curada nem confirmação de evento.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Pista deliberadamente fabricada não é fonte canônica, mesmo que imite documento histórico; marcar proveniência de falsificação e cadeia de cópia.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Lore com lealdades conflitantes é fonte curada, não licença para mudar NPC canônico arbitrariamente; proveniência e revisões permanecem rastreáveis.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Alegações apresentadas por informantes não se tornam fonte canônica por contrato; preservar origem, conflito, edição e status epistêmico.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Proveniência de livro/edição histórica não equivale à cadeia de origem de testemunho na campanha. Fonte anônima, cópia e testemunha indireta são rotuladas.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Citação da fonte canônica no dossiê preserva referência/edição/ano, não confere automaticamente a um NPC acesso a essa fonte nem resolve conflito editorial por IA.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Evidência oriunda de lore deve manter proveniência e não afirmar que evento de campanha ocorreu; avaliação operacional preserva contradições.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Notificações originadas em fontes em conflito mantêm provenance e estado contraditório; nova versão não reinterpreta fonte editorial como evento confirmado.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-094/C (Discovery v9.0)

Hipóteses de conflito operacional não transformam rumores em fatos canônicos; revisões de fontes não mudam autorização e recibos de reservas privadas.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Para proposta DEC-096, versionar CanonEvent por proveniência/status de fonte e data precision, sem misturar regra de impacto hipotética com afirmação de lore.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Cada CanonEvent DEC-096/C precisa source refs e data precision; contradições ficam DISPUTED, não se resolvem por LLM nem por primeiro registro carregado.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Famílias de origem DEC-097/C usam fontes e dependências reais para não somar dois impactos derivados da mesma causa como independentes.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Fonte curada e Proveniência DEC-061 continuam separadas de receipt host e instance ownership; citar cronologia não prova spawn.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Proveniência de texto canônico e proveniência de entidade mecânica são camadas separadas.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Proveniência de fonte e proveniência de flag técnica têm semânticas diferentes; nenhuma concede fato canônico.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Semantic quest milestones are curated technical metadata, separate from FR historical canon partitioned by year DR and private campaign overlays. UNKNOWN, AMBIGUOUS or stale milestones cannot trigger chronology, historical effect or materialization; lore packs do not authorize interpreting runtime flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Metadados de quest DEC-102 são técnicos por build, não fontes canônicas a migrar de ano. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **proveniência histórica**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para fontes conflitantes e famílias de origem no suporte de retificações, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para fontes de alegações e retificações independentes, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Provenance de documento e cadeia de custódia de provas. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Proveniência de cláusulas e receipts deve ser auditável. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
