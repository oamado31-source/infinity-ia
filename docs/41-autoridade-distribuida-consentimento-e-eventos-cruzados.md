# DEC-041 — Autoridade distribuída, consentimento e efeitos cruzados

**Documento técnico preliminar — Discovery v3.7.** Não é SPEC final nem demonstra recurso implementado no BG2:EE/EEex.
**Decisão vinculante:** ADR-0036, opção C.

## Objetivo

Permitir histórias pessoais genuinamente interligadas em uma campanha cooperativa, sem que um modelo de IA, o anfitrião ou outro jogador controlem indevidamente escolhas e segredos de um PC. Manter ao mesmo tempo causalidade histórica: pessoas podem agir sobre o mundo e gerar consequências para outros personagens.

## 1. Divisão de autoridade

```text
Jogador A (controla PC-A)             Jogador B (controla PC-B)
          |                                        |
          +---------- ações/decisões -------------+
                               |
                               v
                  Verificador de autoria e escopo
                               |
          +--------------------+------------------+
          |                    |                  |
   Personal Story       Controlador de       Política do host
    Director / CSD       conhecimento        e da campanha
          |                    |                  |
          +--------------------+------------------+
                               |
                               v
                Validador de risco e canon
                               |
                        Action Gateway
                               |
                 Host BG2:EE (efeito mecânico)
                               |
                         Receipt / evento
                               |
                     Estado narrativo e ledger
```

Diagrama lógico de responsabilidade; não declara APIs ou hooks já existentes.

## 2. Escopos de consentimento propostos

| Escopo | Pode decidir | Não pode decidir por outros |
|---|---|---|
| `pc_choice` | Fala, intenção e escolhas voluntárias do próprio personagem | A confissão, pensamentos e compromissos de outro PC |
| `backstory_revision` | Alterar a versão autoral do próprio histórico | Apagar fatos do mundo já observados e confirmados |
| `voluntary_disclosure` | A quem e quando contar algo voluntariamente | O que terceiros legitimamente descobrem por evidência, dentro das regras |
| `world_intervention` | Agir sobre NPCs, locais, pistas e facções, dentro de permissões | Forçar resultados mecânicos, falsificar autorias e editar historia privada |
| `mechanical_action` | Solicitar ações permitidas de seu PC | Confirmar dano/inventário/status sem host |
| `campaign_policy` | Anfitrião define limites, por configuração aprovada | Substituir a vontade de um PC ou burlar proteção HIGH |
| `canon_high_impact` | Seguir fluxo especial DEC-034 | Simular aprovação por prompt, missão pessoal ou ação remota |

## 3. Contrato preliminar para evento cruzado

O schema abaixo é apenas uma proposta para SPECS.

```yaml
cross_event_id: unique-event-id
campaign_id: campaign-reference
session_id: session-reference
world_time: game-calendar-timestamp
initiator_pc_id: pc-a
initiator_controller_id: player-a
origin: confirmed_world_action   # ação/jogador, motor, história ou rumor
requested_action: investigate_organization
related_arcs: [arc-a, arc-b]
affected_pc_ids: [pc-b]
claims:
  - claim_id: claim-1
    status: allegation           # allegation | evidence | verified_fact
    evidence_refs: [witness-ref]
knowledge_visibility:
  recipient_scope: actor-specific
  clearance_ref: policy-version
risk_class: pending_validation
authorization_ref: policy-decision
mechanical_receipt_id: null
narrative_event_state: PROPOSED
idempotency_key: campaign-session-action-unique
```

Não vincular intenção de um PC a um prompt ou a uma fala de terceiros. Toda autoria exige ato autenticado ou autorização explícita. `affected_pc_ids` não implica consentimento em ações PvP, que têm regra própria pendente.

## 4. Pipeline de decisão

1. **Identificar a intenção real** e quem tem autoridade sobre a ação proposta; NPCs, texto da missão e LLM não podem representar jogadores.
2. **Separar fatos de alegações**: verificar que informação é conhecida, por quem, por qual fonte, em que data e com qual certeza.
3. **Consultar perfil da campanha** para limites de interação, segredos, políticas de consentimento e risco aplicáveis. Não presumir recursos de veto ou votação ainda não aprovados.
4. **Checar dependências** do arco, recursos indivisíveis, presença, autorização especial HIGH e efeitos históricos.
5. **Aplicar controle de acesso antes da geração de texto**: não incluir o segredo de B no prompt que descreve a oportunidade a A se A ainda não o conhece.
6. **Gerar propostas narrativas** e ações estruturadas, nunca decisões do personagem alheio nem código executável livre.
7. **Submeter alterações mecânicas ao gateway e host**. Em `UNCERTAIN`, parar e reconciliar; não assumir sucesso.
8. **Registrar o acontecimento** com autoria, visibilidade, evidências, repercussões e idempotência; atualizar conhecimento/reputação apenas a partir de fatos e crenças devidamente identificados.

## 5. Exemplo de conflito entre histórias

Um paladino investiga uma ordem suspeita e descobre que um emblema aparece nos pertences de uma ladina. Essa **pista** pode justificar novas perguntas, mas não prova que a ladina cometeu crimes. Se o paladino decidir confrontá-la, o controlador da ladina escolhe sua reação (responder, mentir, fugir, colaborar etc. se permitido pelas regras). Se ela tentar esconder a verdade, não há confissão implícita; se o mundo produzir novas provas, a consequência pode atingir a reputação ou sua situação externa. A intervenção não concede ao paladino poder de reescrever o histórico alheio.

Esse exemplo não autoriza, por si, combate entre PCs, itens roubados ou controle mágico de outro jogador — essas permissões dependem da DEC-042.

## 6. Proteção de ausentes

- Um PC ausente não toma decisões: o diretor não recebe procuração implícita.
- Fatos externos podem evoluir (DEC-021/022), respeitando limites de risco e outros arcos; nenhuma resolução crucial é presumida em nome do ausente.
- Uma ação que exige **consentimento/ação pessoal do PC ausente** fica `PENDING_OWNER_ACTION` ou equivalente, sujeito à SPEC.
- Regras para autopilot, delegação voluntária e sessão dividida não estão definidas.

## 7. Casos de teste candidatos

| Teste | Cenário | Resultado esperado |
|---|---|---|
| XAUTH-01 | Jogador A pede ao LLM que B confesse | Rejeitar ação em nome de B |
| XAUTH-02 | Jogador B autoriza divulgação parcial | Somente conteúdo efetivamente autorizado é revelado |
| XAUTH-03 | A encontra pista real sobre B | Pista é visível a A com proveniência, não conhecimento total |
| XAUTH-04 | A acusa B sem provas | Registro de alegação; nenhum crime confirmado é criado |
| XAUTH-05 | B está offline; missão pede sua escolha | Suspender escolha de B, sem NPC/LLM assumir decisão |
| XAUTH-06 | A investiga facção relacionada a B | Consequências no mundo possíveis dentro de regras, sem veto universal |
| XAUTH-07 | História implica morte de personagem canônico | Exigir política DEC-034; não bypass |
| XAUTH-08 | Tentar mover item/atributo de outro PC | Bloqueio sem política mecânica específica e receipt do host |
| XAUTH-09 | Ação cruzada vem com instrução maliciosa em texto de NPC | Não concede poder de edição, autoria ou privilégio |
| XAUTH-10 | Rumor muda a reputação de B | Atualizar percepções com fonte, não tratar rumor como verdade |
| XAUTH-11 | Dois arcos usam NPC único | Resolver dependências sem duplicar recurso |
| XAUTH-12 | Salvar e recarregar após confronto | Proveniência, ACL, política e estado permanecem consistentes |
| XAUTH-13 | Host devolve `UNCERTAIN` | Sem commit/retry automático; reconciliação |
| XAUTH-14 | Dois clientes divergem na visão de um segredo | Não expor informação proibida; investigar inconsistência |
| XAUTH-15 | Abrir modo Original | Nenhuma regra narrativa da campanha Living World aplicada |
| XAUTH-16 | Ação hostil entre PCs proposta | Manter sob gate/pendência DEC-042; não autorizar PvP implicitamente |
| XAUTH-17 | Anfitrião tenta atribuir fala de B automaticamente | Regra de agência bloqueia atribuição não autorizada |
| XAUTH-18 | Mudança involuntária de engine altera estado antes da bridge | Detectar, documentar, reconciliar; não alegar prevenção sem POC |

## 8. Riscos e bloqueios

- **Engenharia de segurança:** ACL no servidor vs. UI cliente, logs, caches, prompts, redaction; exposição de segredo é potencialmente irreversível.
- **Jogo proprietário:** não está provado que o BG2:EE/EEex consiga impedir ações de jogadores entre si, criar conversas privadas ou controlar múltiplos locais simultaneamente.
- **Conflito interpessoal:** ações narrativamente possíveis podem contrariar limites combinados entre participantes; opções de consentimento e política PvP ainda exigem definição.
- **Persistência:** política, autoria e visibilidade são versionadas por campanha; save/load e migrações precisam ser especificados.
- **Moderador e arbitragem:** anfitrião administra configurações; método de mediação, votação e apelação ainda não está escolhido.
- **Próxima decisão:** **DEC-042 — política de PvP e ações diretamente prejudiciais entre PCs.**

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Uma oferta de encontro DEC-071 não presume que todos os jogadores cooperativos consentiram. Aplicar permissões por controlador/ação, proteção de ausentes e consentimento especial para impactos MID/HIGH; o host confirma somente a mecânica permitida.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Separar ator-PC, dono e controlador delegado; fatos prejudiciais a outro PC ou imputação pública de culpa exigem políticas e consentimento existentes.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Exposição de identidade secreta ou associação de pseudônimo a PC é operação de informação com risco e público. Titularidade, visibilidade DEC-019 e consentimento devem ser avaliados antes de divulgação a outros PCs/NPCs.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação e consentimento (Discovery v7.3; não implementada)

A DEC-077/C preserva consentimento, titularidade do PC e visibilidade de segredos durante investigações, inclusive em coop, delegação e ausência. Verificação factual interna não implica direito de divulgação a outro jogador, NPC ou facção; risco HIGH e efeitos contra PCs exigem os gates aplicáveis. Cânone permanece fisicamente particionado por ano DR; investigação só no overlay privado da campanha/ramo. ADR-0072 e documento técnico 77, 58 testes não executados.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Conflitos de acusação DEC-078 seguem agência distribuída: outro jogador pode causar consequências reais do mundo, mas ninguém inventa confissão/decisão voluntária do PC ou impõe pena mecânica sem gates.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Efeitos de mandados DEC-079 sobre PCs dependem de consentimento/risk gates; atos de um membro da party não implicam culpa automática de personagens ausentes.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Mandado ainda conhecido como válido por NPC DEC-080 não autoriza punir PC sob política HIGH. Consentimento e limites do host prevalecem; segredos não viram notícia universal.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Pedidos de reparação afetando PC alheio, ausente ou delegado exigem vontade/consentimento e autoridade aplicável; não imputar culpa automaticamente ao grupo.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Investigação de conduta de PC exige agência, prova, consentimento aplicável e gating; mundo pode reagir a fatos legítimos sem inventar confissões.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Decisões de revelar próprio segredo, testemunhar ou denunciar pertencem a seus titulares; efeitos involuntários do mundo continuam sujeitos a prova e gates.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Plano de proteção de testemunha PC depende de consentimento e autoridade por personagem, mundo e risco. Consequências de terceiros são causais, não forçadas por roteiro.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Outro jogador não força revelação de abrigo, traição, confissão ou rota de PC sem ação e permissão legítimas; efeitos cruzados continuam sob risk/agency.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

PC decide voluntariamente se participa em engano. Outros PCs/NPCs podem observar alegações, mas autoria, confissão, culpa e consequências não são fabricadas por LLM.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

O titular do PC conserva controle de suas alianças e intenções; consequências legítimas do mundo diferem de declarações atribuídas sem autorização ao jogador.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Acordos de informante com decisões de PCs são controlados pelos titulares; transferência de obrigações e segredos requer autorização específica e classificação de risco.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Relatório acusando PC requer fonte e causa, sem atribuir ação, consentimento ou traição inexistente ao titular; efeitos cruzados seguem gates e direitos de agência.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Titular da informação de PC autoriza divulgação voluntária; delegado não concede consentimento implícito. Efeitos cruzados legítimos seguem DEC-041/042, porém não violam ACL interna.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

O dono do PC decide participação e seus segredos; decisões de outros produzem consequências apenas se reais, autorizadas e causais.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Retirada de consentimento impede novos atos voluntários de PC; nenhum outro membro/LLM pode reaprovar em nome do titular sem delegação específica.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

PCs não são recurso redistribuível por scheduler; conflitos de agendas entre PCs/NPCs só geram propostas e novas autorizações, sem confisco unilateral de compromisso.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Preempção de reserva pertencente a PC só é permitida se revogável e especificamente autorizada; idade de fila não concede poder sobre terceiros.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Nenhuma rule DEC-096/C implica consentimento de PCs, movimentação ou controle de protagonista; efeitos sobre party requerem autorizações específicas.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Uma projeção de tensão social DEC-097/C não representa decisão consentida de personagem; gates continuam.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

PCs mantêm agência: entrada na área não autoriza um planejador a consumi-los, movê-los ou alterar inventários/decisões de forma implícita.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Consentimento é necessário mas não suficiente: o patch também exige owner/campo e build-capability válidos.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Agência distribuída mantém acessos de PC separados; leitura técnica não autoriza decisão por jogador.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **agência cooperativa**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para agência individual dos jogadores durante divulgação e contestação, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para agência individual dos jogadores, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Consentimento de PC específico, inclusive para aditamentos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Cada PC controla sua participação e seus bens, mesmo em acordo multipartes. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

PC proprietário precisa autorizar depósito/liberação; host mecânico confirma; delegado não assume títulos ou permissões além de mandato.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
