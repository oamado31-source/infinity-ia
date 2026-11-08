# Política de acontecimentos irreversíveis e proteção do cânone — DEC-034

**Estado:** desenho técnico candidato de Discovery v3.1, **não é SPEC implementada**.  
**Decisão aprovada:** opção C; ADR-0029.  
**Adendo:** alinhamento mutável dos jogadores aprovado separadamente em DEC-035/ADR-0030.

## Resultado arquitetural

A simulação de facções, eventos estratégicos e arcos paralelos deve poder gerar mudanças sem interromper constantemente o anfitrião, mas não pode aplicar mudanças históricas críticas a menos que estejam autorizadas. O **canon de Forgotten Realms é baseline**, sobreposto por divergências específicas e rastreáveis da campanha.

## Matriz preliminar de autorização

| Classe | Exemplos ilustrativos | Autoridade pretendida | Tratamento |
|---|---|---|---|
| LOW | notícia pública validada, rumor sem efeito físico | validação de conhecimento/lore | publicar automaticamente conforme DEC-027 |
| MEDIUM | missão, patrulha, disputa de influência limitada | regras + gateway; host para física | executar somente após gates, idempotência e receipt |
| HIGH limitado/reversível | controle temporário de posto secundário, negociação política local | pré-política configurada e escopo estreito | autorizar se evento e consequências respeitarem os limites |
| HIGH histórico/irreversível | morte permanente de personagem icônico, destruição de cidade, fim de reino | proteção especial de cânone; consentimento explícito válido | **bloqueado por padrão** sem política individual expressa |

A classificação não pode ser reduzida pelo LLM; observar o impacto acumulado, sucessores/efeitos causais, ano DR e o grau de confiança das fontes. Exemplos são candidatos, não classificação final automática.

## Proposta de fluxo

```text
World Event (curado | regras | LLM local via orquestrador)
  → Evidence + Canon Timeline + Event Dependencies
  → Risk / Irreversibility Classifier (determinístico)
  → Preflight (policy / subject / campaign / timeframe)
     ├─ LOW + valid → Publish narrative
     ├─ MEDIUM + valid → Action Gateway → Host receipt → Commit
     ├─ HIGH limited + explicit scoped policy → Validate → Execute/Commit
     └─ HIGH critical without consent → PENDING_APPROVAL / BLOCKED
  → Event Store + Snapshot + Audit + knowledge propagation
```

**Ação direta de jogador:** se o jogador tenta atacar uma figura histórica crítica, checar o que pode ser controlado antes da ação. Quando o motor realiza ação impossível de desfazer, não inventar que ela não aconteceu: registrar a confirmação do host, entrar em estado de conflito e encaminhar para reconciliação política/narrativa. Isso exige POC; o modelo de exceção não garante que seja possível interceptar a ação.

### Contrato candidato de política

```yaml
policy_id: campaign-critical-event-v1
campaign_id: C1
mode: LIVING_WORLD
risk: HIGH
scope:
  region_ids: []
  event_types: []
  entity_ids: []
  date_window_dr: null
authorization:
  principal: HOST
  approval_ref: null
  expiry: null
immutable_evidence:
  event_id: null
  authorized_at: null
  host_receipt: null
status: PENDING
```

YAML meramente ilustrativo; não aprova nomes de campos finais, métodos criptográficos, nem UI.

## Testes de aceitação candidatos

| ID | Cenário | Resultado esperado |
|---|---|---|
| CANON-H01 | Facção decide matar figura canônica em região distante | HIGH pendente sem autorização |
| CANON-H02 | Anfitrião libera disputa comercial de área delimitada | Não estende autorização a guerra/regicídio |
| CANON-H03 | Personagens protegem, investigam ou ajudam conspiradores | Caminhos opcionais; efeitos distintos e verificáveis |
| CANON-H04 | Evento MEDIUM repetido para produzir queda de reino | Escalonar para HIGH antes da consequência |
| CANON-H05 | Fechamento offline com evento HIGH previsto | Não aplicar sozinho no catch-up |
| CANON-H06 | Host confirma dano/morte não interceptada | Evidência mantida; histórico em conflito, sem rollback fictício |
| CANON-H07 | Save/load e clientes simultâneos | Autorização e resultado idempotentes, sem duplicação |
| CANON-H08 | Campanha alternativa preautoriza desvio delimitado | Divergência auditável e vinculada ao evento e à campanha |
| CANON-H09 | Narrador especula que governante morreu | Texto não promove morte sem confirmação e autorização |
| CANON-H10 | Modo Original | Nenhuma política injetada |
| CANON-H11 | Tentativa de autorização por NPC/cliente | Falha fechada (somente autoridade configurada) |
| CANON-H12 | Política expirada ou alterada | Não reaproveitar autorização anterior |

## Gates antes de SPECS e implementação

Definir escopo de autorização/campanhas alternativas, papéis, UI, TTL, política para intervenção direta sobre NPC canônico, descoberta dos hooks reais, desvio canônico causal, backups/replays e sincronização com o tempo e host.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

NPC dormente não morre, casa ou altera desfecho histórico crítico por preenchimento narrativo do tempo ausente. Eventos HIGH DEC-034 continuam protegidos e exigem autorização especial e pré-condições; ausência de host impede confirmação. Ver ADR-0063.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: itinerário não pode alterar sozinho marcos históricos, resultado de guerra, morte canônica ou NPC importante; esses fatos mantêm gates HIGH e controle causal.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: morte, destruição de organização/cidade, batalha decisiva e evento protegido HIGH não são consumados automaticamente ao simular incidente offscreen; aplicar controle especial DEC-034.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Nenhum encontro local DEC-071 contorna política HIGH de eventos históricos DEC-034, mesmo com party presente. Só efeito mecânico confirmado e autorização especial podem alterar marcos protegidos; a base canônica anual permanece intacta.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Composição modular DEC-072 jamais contorna gates DEC-034 para alterar marcos canônicos; cenas envolvendo figuras/eventos protegidos exigem autorização apropriada e evidência temporal.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Limpeza/desaparecimento com impacto irreversível ou canônico segue gates HIGH; resultado físico incerto não é fato histórico.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Punição judicial/faccional DEC-078 que modifique marco histórico, pessoa canônica ou resultado irreversível continua HIGH bloqueado por padrão DEC-034, mesmo com veredito ficcional.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Decisão local ou pedido interjurisdicional DEC-079 não autoriza execução, exílio, guerra, eliminação de facção ou evento canônico HIGH sem política e consentimentos especiais.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Revogação não apaga dano histórico; reparação/sanção HIGH exige proteção DEC-034 e autorização explícita, sem rollback narrativo/mecânico arbitrário.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

DEC-081 não desfaz morte, história canônica, guerra ou ruptura irreversível por comando narrativo; HIGH default-deny e autorização especial, com limites explícitos.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Exoneração relevante, golpe, mudança de soberania e desfechos canônicos irreversíveis exigem gate HIGH e autorização da DEC-034, mesmo sob denúncia confirmada.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Vazamento de identidade e retaliação grave podem produzir consequências irreversíveis; gate HIGH não pode ser contornado por redação narrativa.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Morte, captura, fuga impossível, exposição de segredo crítico e alteração histórica são HIGH; o plano narrativo não os executa autonomamente.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Descoberta de esconderijo não justifica evento histórico irrevogável; planos de proteção e conspirações ficam no overlay e sob autorização histórica.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Alegação deliberadamente falsa não dispara mudança histórica irreversível. Quaisquer impactos excepcionais ficam bloqueados até política e autorização de risco apropriadas.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Deserção que altere fatos irreversíveis de personagens canônicos, controle de facções ou história principal depende da política de evento protegido DEC-034 e curadoria.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Acordos com NPCs canônicos não permitem reinventar motivações, violar segredos de enredo ou criar eventos canônicos irreversíveis sem autorização.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Informes sobre eventos históricos críticos não anulam a proteção de canon/high-risk DEC-034. LLM não confirma divergência de história central.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Divulgar dossiê não confirma eventos ou mudanças irreversíveis do cânone. Gates e autorização de impacto alto continuam exigidos.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Ações que alterem marcos irreversíveis do cânone são HIGH e não derivam de dossiês/LLM sem aprovação expressa.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Desfecho canônico irreversível não é autorizado por replanejamento LOW; mudanças materiais HIGH exigem autorização explícita e permanecem bloqueadas por padrão.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-094/C (Discovery v9.0)

Recuperar recurso narrativo nunca revoga morte, guerra, ascensão política ou outro evento confirmado irreversível; mudanças requerem gates próprios e continuidade histórica.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Matriz condicional DEC-096 proposta não força morte/ascensão/derrota apenas por calendário; cronologia é contexto/versionamento e marcos críticos seguem gate de divergência/prova e autorização.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C só emite propostas sobre eventos históricos de fato curados e ramo compatível; impacto irreversível requer autoridade específica e confirmação host. Desfechos canônicos divergentes ficam pendentes.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Nenhum clamp DEC-097/C retrocede morte, sucessão ou guerra; acontecimentos críticos permanecem protegidos.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

A materialização não pode reverter ou forçar eventos históricos irreversíveis; divergências de canon e decisões N3 continuam sob gates DEC-034.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Acontecimentos irreversíveis e flags de quest confirmados pelo host não são apagados por novas projeções.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Eventos históricos irreversíveis não podem ser disparados pela observação de estado oculto nem pela interpretação da LLM.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

Reconciliador DEC-102 não reverte fatos irreversíveis; restauração exige novo ramo e revisão explícita. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para eventos irreversíveis e conhecimento dos NPCs são entidades separadas, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para fatos irreversíveis não são revertidos por mudança de opinião, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-109/C — Obrigações condicionais multipartes

Efeito irreversível do cânone não é negociável por cláusula arbitrária. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
