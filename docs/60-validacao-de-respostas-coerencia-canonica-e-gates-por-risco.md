# DEC-060 — Validação em camadas de respostas e acontecimentos gerados

**Escolha aprovada:** C — validação híbrida, baseada em regras, fontes e risco; ADR-0055. **Estado:** desenho; nenhuma POC executada.

## Fluxo candidato

`task -> contexto permitido -> router -> saída proposta -> verificador estrutural -> ACL e conhecimento -> cronologia/cânone/ramo -> coerência de quest/build -> classificação de risco -> ACCEPT/REVISE/DEFER/REJECT/ESCALATE -> publicação ou gateway/host`.

A validação de privacidade acontece **antes do prompt e antes da publicação**. O verificador semântico nunca pode desautorizar regras de segurança. A saída aceita como *diálogo* não vira evento confirmado automaticamente. Um rumor deliberadamente falso pode ser publicado como rumor com atribuição/proveniência, não como verdade. Conteúdo canônico que depende de fontes ausentes fica desconhecido. Fatos de eventos da campanha precisam de receipt e ramo válidos.

## Matriz candidata de gates

| Classe | Verificações mínimas | Efeito permitido |
|---|---|---|
| Diálogo cotidiano | schema, ACL, conhecimento, proibições, revisão | Apenas fala, sem fato persistente implícito |
| Rumor/opinião | idem + autoria, grau de crença e propagação | Crença atribuída, não fato confirmado |
| Afirmação histórica | cronologia DR, fonte, local, personagem, branch | Publicação factual só com evidência suficiente |
| Missão gerada | dependências, inventário da build, quests, riscos e coerência | Proposta até validação/publicação autorizada |
| Mudança de relação/reputação | evento confirmado, causalidade, escopo e consentimentos | Atualização persistente validada |
| Alteração mecânica/irreversível | regras, alto risco, gateway, receipt host e aprovação específica | Nunca ação direta por LLM |

## Contrato conceitual

- Entrada: `proposal_id`, `job_id`, `campaign_id`, `mode`, `branch_id`, `build_fingerprint`, `world_revision`, `permission_epoch`, `speaker_id`, `audience_scope`, `risk_class`, `claim_refs`, `provenance_refs`.
- Saída: `verdict` (`ACCEPT|REVISE|DEFER|REJECT|ESCALATE`), `reasons`, `required_evidence`, `policy_version`, `review_trace_id`, `safe_publication_scope`.
- Invariantes: sem contexto de outro ramo, sem promoção de rumor a fato, sem autoridade mecânica por texto, sem liberação por timeout ou por aprovação isolada de segundo modelo.

## Cenários de teste candidatos (24; ainda não executados)

1. Diálogo simples compatível com a época; 2. NPC revela segredo sem acesso; 3. Referência a evento futuro; 4. Personagem com homônimo/alias; 5. Rumor falso explicitamente atribuído; 6. Rumor falso tratado como fato; 7. Contradição com receipt do host; 8. Contradição com estado narrativo; 9. Quest inexistente na build; 10. Script de romance em conflito; 11. Fato canônico com fonte insuficiente; 12. Divergência legítima autorizada; 13. Divergência não autorizada; 14. Saída com schema inválido; 15. Prompt injection em conteúdo recuperado; 16. Pedido de comando mecânico direto; 17. Saída stale após rewind; 18. Saída de worker revogado; 19. Verificador indisponível; 20. Timeout de revisão; 21. Segundo LLM aprova informação falsa; 22. Alto risco sem aprovação; 23. Logs sem segredos; 24. Diálogo de baixo risco sem revisor LLM e com validações determinísticas.

## Critérios pendentes

Precisamos medir taxas de erros factuais, vazamentos, falso bloqueio, custo/latência e regressões por cenário, em builds e ramos controlados. Nenhuma porcentagem de acerto ou garantia de precisão está aprovada. DEC-015 define aceitação global; DEC-061 discutirá resolução de conflitos de fontes e curadoria.

## Adendo de armazenamento e busca por período (DEC-060/C; v5.6.1)

- **Pré-condição de recuperação:** derivar `calendar_year_DR`, intervalo/data (quando disponível), `campaign_id`, `branch_id`, `world_revision`, `speaker_id`, `audience_scope`, `permission_epoch` do estado confirmado, nunca de uma sugestão não validada do LLM.
- **Corpus fisicamente particionado:** partir de `knowledge/periods/<ano>-DR/`; para 1369, ler `1369-DR/chronology`, `events`, `organizations`, `guilds`, `characters`, `regions` conforme a tarefa. Não juntar textos de todos os anos em um banco narrativo único ou num índice sem isolamento temporal.
- **Consulta histórica controlada:** referências a anos anteriores passam por seleção de partições explicitamente delimitada, validação `valid_from/valid_to`, fontes, contexto, ramo, ACL e momento de difusão. Nunca antecipar fatos de anos futuros como consumados; conhecimento de profecia/rumor futuro exige status distinto e prova.
- **Overlay da campanha:** fatos divergentes e memória dos jogadores continuam separados do catálogo imutável, particionados por campanha/ramo/época e com receipts/checkpoints. O roteador não divulga diretamente o corpus inteiro a um worker ou NPC.
- **Falhas:** partição anual não existente, incompleta, manifest inválido ou fato sem data adequada => `DEFER`/`REVISE`, ou fala neutra validada de baixo risco, conforme o caso. Nunca preencher com conteúdo do ano adjacente por conveniência.
- **Escopo de implementação:** estrutura documental criada em `knowledge/`; ainda vazia de fatos históricos. Formato/engine de busca/índices/caches e custos de varredura dependem de SPECS, testes e curadoria. Ver documento 60a.

**Testes adicionais candidatos T060-25 a T060-36:** (25) pergunta de 1369 consulta partição 1369; (26) fonte exclusiva de 1370 não é tratada como conhecida em 1369; (27) evento de 1368 ainda vigente é encontrado por referência histórica permitida; (28) NPC não sabe informação do arquivo mesmo presente na pasta; (29) segredo do PC não entra no catálogo canônico; (30) mesmas identidades em dois ramos não misturam resultados; (31) falta pasta do ano não ativa fallback indiscriminado; (32) manifesto/data corrompidos falham fechados; (33) cache invalidado por mudança de ano/revisão; (34) tentativa de indexação global sem isolamento temporal é rejeitada; (35) worker LAN recebe apenas trechos ACL-filtrados; (36) mudança legítima de organização entre anos usa a versão vigente e proveniência.

## Extensão DEC-061 — evidência e conflitos (Discovery v5.7)

A etapa `cronologia/cânone/ramo` da DEC-060 deve distinguir `Source/Claim/ConflictSet/CuratedResolution/Rumor/CampaignEvent` (proposta no doc. 61). Uma fonte bibliográfica sem curadoria não vira verdade; duas fontes conflitantes no mesmo diretório anual não são conciliadas automaticamente pelo modelo. Para `UNRESOLVED`, a política de risco decide `REVISE/DEFER/ESCALATE` ou fala neutra previamente validada; opiniões e rumores atribuídos só se houver acesso legítimo do NPC. O filtro por ano DR ocorre **antes** de inferência; 1370 DR não se torna fato presente em 1369 DR.

**Testes candidatos adicionais T060-37 a T060-41:** (37) fontes divergentes dentro de 1369 geram conflito, não novo fato; (38) mudança legítima de liderança dentro de 1369 não é falsa contradição; (39) rumor não vira verdade objetiva; (40) revisão curada invalida cache com versionamento; (41) fonte temporal futura não contamina a resposta presente. Ver ADR-0056/doc. 61.

## Integração DEC-062 — somente conhecimento publicado e curado

Os validadores DEC-060 também se aplicam **antes da promoção** de alegações importadas: fonte/rights gate, ano DR, ACL, `Claim` com localização, `ConflictSet`, risco e revisão. A saída da IA em estágio `CANDIDATE` ou conteúdo de vault privado **não** tem status de fato; políticas LOW necessitam allowlist versionada e testes, enquanto novos fatos canônicos iniciam com revisão humana. Falha/UNKNOWN não libera publicação. Depois de publicada no diretório anual correto, uma resposta de NPC ainda precisa dos gates de conhecimento e da história do ramo. DEC-061 mantém proveniência/contradições; nenhum fato futuro é recuperado como passado. Ver ADR-0057/doc. 62.

## Integração DEC-063/C — validação consulta revisão fixa (v5.9)

O validador de respostas usa o *knowledge pack* vinculado à campanha/ramo/ano, não o catálogo sempre mais novo. Novas publicações só entram após atualização seletiva DEC-063 verificada. Saídas com `source_pack != active_pack` são rejeitadas ou geradas novamente; afirmações conflitantes preservam incerteza DEC-061. A troca não modifica diálogo passado nem dá onisciência a NPCs.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

DEC-064/C distingue diálogo subjetivo do NPC de asserção de fato canônico. Crença falsa pode produzir fala plausível se enquadrada como rumor/opinião e com episódio legitimamente recebido. Validar fonte, ano DR, ACL, pack, continuidade histórica e consequência; não mudar automaticamente crenças porque uma fonte curada as contradiz. Alto risco e UNCERTAIN bloqueados/escalados.

### Integração DEC-066/C — validar falas sobre reconhecimento (v6.2)

Diálogo que pressupõe reencontro, dívida, romance, trauma, segredo ou compromisso exige identidade `VERIFIED`, conhecimento legítimo DEC-064, memória válida DEC-065, pack/ano DEC-060/063 e ACL. Em ambiguidade, rejeitar afirmação pessoal sem evidência, permitindo resposta neutra quando seguro. Cânone anual não prova que a instância no motor é a mesma pessoa.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

DEC-067 não autoriza biografias inventadas ou transformação de diálogo genérico em fato; validar relevância, conhecimento e origem antes de consolidar eventos pessoais.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: validação de história de viagem compara tempo/região, KB anual, crenças NPC e estados da jornada; resposta não pode inventar viagem concluída/teleporte.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 integra incidentes de viagem aos gates de resposta DEC-060: verificar fonte anual, existência factual, conhecimento NPC, consequência por risco e nenhuma afirmação de combate offscreen confirmado.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

O validador DEC-060 aplica ano DR, conhecimento ACL e risco a qualquer fala/cena DEC-071. Citar evento proposto como já ocorrido é erro; incidente pertence ao overlay e nunca é escrito nos diretórios canônicos.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Validador DEC-060 rejeita composição DEC-072 anacrônica, secreta ou fora do catálogo, consulta diretório canônico do ano DR correto e não interpreta texto LLM como presença de asset.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Validar declarações de autoria e contribuição sem confundir uma fala de NPC com evento confirmado; manter conhecimento físico por ano DR e overlays separados.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Validação de fala deve recusar informação sobre identidade verdadeira que o observador não poderia saber. Suspeita em diálogo deve ser rotulada como suspeita e não verdade factual.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Frases de autoridade DEC-078 devem indicar alegação versus fato e respeitar ano DR. Não inventar lei aplicável por fluência de LLM; regras exigem evidência curada.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Validador DEC-060 impede que LLM invente tratado, extradição universal, autoridade ou captura; qualquer afirmação de competência DEC-079 exige fonte de ano DR e revisão.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Resposta de NPC DEC-080 pode refletir crença de mandado desatualizada sem afirmar validade autoritativa; crítica HIGH usa safety gate distinto e nenhuma ordem fora do ano DR.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Validar alegação de dano e reparação DEC-081 contra fatos/ano DR/ACL; ausência de recibo não autoriza frase “item devolvido” ou “preso libertado”.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Validador separa alegação, prova e conclusão, impede criação de competência histórica e efeitos HIGH por texto LLM, respeita ano DR.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Checagens de saída impedem identidade protegida fora da audiência; rumor e testemunho não são prova factual e nenhum LLM decreta divulgação.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Validar ameaças e medidas contra narrativa inventada: rumor não confirma ataque, plano não prova sucesso, LLM não cria proteção mecânica, falha HIGH é fechada.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Validador recusa vazamento de plano privado em diálogo de NPC que só recebeu rumor e recusa transformar hipótese adversária em fato.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Validador exige que mensagem falsa seja alegação in-world, impede promoção a fato e filtra segredos da proteção; risco HIGH impede consequências punitivas sem gate.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Validação deve bloquear afirmações de traição como fato sem evidência verificada; distinguir suspeita, rumor, compromisso e recibo do host.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Validador de fala bloqueia aceite/assinatura inventados, criação de recursos e informação secreta sem proveniência, separando proposta LLM de acordo autorizado.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Validador de saída recusa conclusões categóricas sem fontes acessíveis, referências de prova inventadas e falsa independência A→C de rumor.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Checar respostas geradas contra claims/citations e ACL da view. Resumos não podem reforçar alegações INCONCLUSIVE, omitir contradições essenciais ou vazar origem protegida.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Validação de resposta rejeita afirmações de operação executada, NPC presente ou reunião confirmada se apenas houver proposta/relato.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Validação de novas falas/planos DEC-092 exige origem do trigger, escopo epistemológico, risco e revisão; LLM não transforma rumor em fato nem inventa recibo.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Validar propostas que aleguem duplicar NPC/item ou tirar PC de operação sem consentimento; nenhuma narrativa substitui prova de presença/ação pela engine.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Validadores recusam narrativa de liberação de NPC/item ou conclusão de quest sem receipt; tempo de lease não é mudança confirmada no mundo.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-096 proposta: evento fonte disputada/YEAR_ONLY não pode produzir afirmação exata de mês nem comando automático; avaliação temporal/geográfica determinística e fallback sem LLM.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C preserva `knowledge/periods/<ANO>-DR/` como fonte física do lore; índice de regras compilado separado; dados futuros não disponíveis por default.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Catálogo original por ano DEC-060 fica imutável; DEC-097/C guarda composição em overlays/snapshots de campanha.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

DEC-098 materializa exclusivamente overlays por campanha/branch e jamais grava fatos mecânicos em `knowledge/periods/<ANO>-DR/`.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Validação canônica/risco não substitui autorização de campo nem teste da capability EEex/bridge.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Canon por ano DR não é alterado pelo mero recebimento de uma observação técnica.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Catalogues by exact build/modpack/quest/script fingerprint, curated proof of semantic milestone and valid transition; an observed flag or stage is never an authorized quest write or host receipt. On patch or restore, invalidate semantic cache and avoid generic stage inference. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **partição física por ano DR**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para validador de resposta não promove boato ou errata a fato mecânico, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para validação de saídas evita inventar reputação mecânica, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
