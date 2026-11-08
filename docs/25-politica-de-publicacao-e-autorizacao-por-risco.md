# Política de publicação e autorização por risco — DEC-027

**Estado:** desenho técnico preliminar de Discovery v2.3 — **não é SPEC implementada**.  
**ADR aprovado:** `decisions/ADR-0021-autonomia-de-publicacao-por-niveis-de-risco.md`.  
**Próximo tema:** DEC-012, fronteira de execução de comandos e permissões.

## Objetivo operacional

Permitir que a cidade responda espontaneamente a rumores, interações e eventos menores sem solicitar aprovações a cada fala; submeter missões e efeitos mecânicos a gates determinísticos; impedir que mudanças irreversíveis e históricas ocorram sem política explícita de autorização.

## Classificador lógico por impacto

| Critério | LOW | MEDIUM | HIGH |
|---|---|---|---|
| Persistência | Narrativa localizada, reversível, sem mecânica | Estado de quest, encontro, consequência local controlada | Mudança global, política, canônica ou irreversível |
| Acesso | Conhecimento legítimo do NPC, filtros de segredo | Checagem de quest, recursos e origem | Conferência histórica, dependências e autorização especial |
| Host/bridge | Nenhum comando necessário para texto puramente narrativo | Receipts obrigatórios para itens, spawn e mecânica | Política especial **e** recibo mecânico se houver ação no motor |
| Ausência/catch-up | Pode atualizar narrativa após validação, se compatível | Não aplica efeitos mecânicos offscreen sem confirmação | Bloqueia efeitos críticos sem política especial |
| Falha | Não publicar ou usar fallback curado | `UNCERTAIN`, conciliar, não duplicar | Bloquear e não declarar efeito realizado |

A classificação final deve vir de regras, não do LLM. Ação combinada assume classificação máxima e pode ser elevada pela soma das consequências. A escala de impacto ainda terá calibração em SPECS.

## Separar três decisões técnicas

1. **Validação semântica e estrutural:** este conteúdo combina com 1369 DR (ou período escolhido), lore, histórico, permissões de conhecimento, inventário de recursos, IDs e estado confirmado?
2. **Autorização para publicar:** essa classe de efeito pode tornar-se visível ou efetiva na campanha sem autorização adicional? A política especial de `HIGH` existe e foi confirmada?
3. **Confirmação mecânica:** se uma mudança depende do BG2:EE, a bridge recebeu resposta comprovada do host? Sem recibo, o estado permanece indeterminado e exige reconciliação.

Publicar um diálogo não significa executar uma recompensa. Validar uma missão não significa ter alterado o inventário. Aprovar uma mudança histórica não produz, por si, uma ação mecânica confirmada.

## Entidades de controle candidatas (nomes não finais)

```yaml
proposal_id: "<stable-id>"
campaign_id: "<campaign-id>"
source_type: "template | rules | local_llm | curated"
content_type: "dialogue | rumor | quest | encounter | world_event"
world_time_dr: "<campaign-time>"
provenance_refs: []
knowledge_scope: []
resource_manifest_ref: "<validated-version>"
impact_scope: "npc | local | regional | global"
canonical_impact: false
irreversible: false
risk_class: "LOW | MEDIUM | HIGH"
policy_version: "<version>"
validation_status: "PROPOSED"
authorization_ref: null
host_receipt: null
idempotency_key: "<campaign-and-event-key>"
```

*Campos ilustrativos: não são API, schema final nem garantia de interfaces disponíveis.*

## Máquina de estados proposta

```text
PROPOSED → VALIDATED → CLASSIFIED
  ├─ LOW    → PUBLICATION_READY → PUBLISHED
  ├─ MEDIUM → AUTHORIZED_FOR_COMMAND → DISPATCHED → CONFIRMED → COMMITTED
  └─ HIGH   → AWAITING_SPECIAL_AUTH → (AUTHORIZED or BLOCKED)

DISPATCHED → UNCERTAIN → RECONCILED or CANCELLED
REJECTED/EXPIRED → no mechanical mutation
```

Uma proposta pode conter texto publicável e um efeito pendente. Não publicar uma frase como se a recompensa já tivesse sido entregue quando `host_receipt` não existe. Toda transição exigirá auditoria mínima por campanha.

## Contramedidas mínimas

- LLM sem privilégios de execução: objetos estruturados para validação; sem Lua livre ou shell arbitrário.
- Allowlist de ações e argumentos tipados: DEC-012 definirá níveis de permissão, sandbox e logs.
- Segredos e metaconhecimento nunca devem ser expostos pela publicação de conteúdo (DEC-019).
- Prevenir encadeamentos como “10 pequenas missões” que juntas alteram um governo ou matam um personagem histórico.
- Snapshot e log antes/depois quando o suporte real existir; backup para operações de risco elevado.
- Manter `UNCERTAIN` em falhas de comunicação; não executar retry sem consultar o host.
- Não inferir morte, perda de item, destruição ou recompensa apenas pela passagem do tempo ou pelo texto de um NPC.
- Nem a IA nem o jogador cliente podem forçar transições de estado que competem ao host.
- Política por campanha; nunca transportar autorizações entre modos Original/Living World.

## Cenários de teste candidatos

| ID | Estímulo | Oráculo de validação |
|---|---|---|
| PUB-01 | NPC comenta evento legítimo conhecido | `LOW` publica somente texto validado |
| PUB-02 | NPC tenta revelar segredo alheio | Rejeitado por proveniência do conhecimento |
| PUB-03 | Quest com item que não existe na build | Rejeitada antes da publicação/execução |
| PUB-04 | IA propõe entregar recompensa | `MEDIUM`, efeito só confirmado por host |
| PUB-05 | Timeout após spawn | `UNCERTAIN`, sem segundo spawn cego |
| PUB-06 | IA propõe morte de governante canônico | `HIGH`, bloqueado sem política especial |
| PUB-07 | Dez ações `LOW` encadeadas para provocar alteração canônica | Elevar a `HIGH` por impacto agregado |
| PUB-08 | Tentativa de reclassificar `HIGH` como `LOW` no texto | Classificador por impacto mantém `HIGH` |
| PUB-09 | Retomar após semanas offline | Não promover silenciosamente eventos críticos |
| PUB-10 | Reabrir o save após aprovação pendente | Não liberar ação sem ref de autorização válida |
| PUB-11 | 2 clientes discordam de um evento | Gate multiplayer interrompe promoção de estado |
| PUB-12 | Novo mapa procedural já aprovado como narrativa | Ainda requer build isolada e POC de área/recursos |
| PUB-13 | Comando de Lua fora da allowlist | Rejeitar sem alcançar o processo do jogo |
| PUB-14 | LLM local inoperante | Conteúdo curado/fallback, sem aprovação presumida |

## Gates para passagem a SPECS

- Definir autorização especial, autoridade de aprovação e expiração (DEC-012 ou SPEC posterior).
- Demonstrar que a bridge consegue observar e confirmar efeitos mecânicos no host.
- Demonstrar integridade e sincronização multiplayer com pelo menos dois clientes.
- Definir quais mudanças narrativas têm superfície real no BG2:EE e quais serão apenas memória externa até existir interface validada.
- Definir logs sem exposição de histórico secreto; políticas de backup, save e recuperação.
- Validar que riscos combinados, progresso de quests e consequências históricas não bypassam os gates.

**Situação atual:** desenho de requisitos e regras; nenhuma implementação, jogo executado, POC multiplayer ou validação de UI neste passo.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: travel events LOW/normal não criam efeitos mecânicos por si; riscos MEDIUM/HIGH, especialmente morte, saque, encontros e mudança de estado de quest, requerem política e autorização. DEC-070 aberta.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 aplica LOW/MEDIUM/HIGH aos incidentes de viagem e classifica impacto cumulativo; somente LOW allowlisted/idempotente pode registrar relato narrativo seguro. HIGH e resultados mecânicos bloqueiam sem autorização e receipt do host.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

A DEC-071 mantém LOW/MEDIUM/HIGH da DEC-027/070. Oferta local sem mecânica não consente automaticamente combate/loot/captura/permadeath; mudanças HIGH permanecem bloqueadas até autorização especial, precondições válidas e receipt host. Somar efeitos para determinar risco agregado.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Revogação pendente/ordem obsoleta DEC-080 bloqueia ações coercitivas HIGH por padrão. LOWs acumulados que resultem em perseguição ou punição HIGH não podem contornar a política.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Divulgação de identidade é publicação sensível, mesmo sem efeito mecânico: avaliar audiência, finalidade, risco acumulado, consentimento e autorização; HIGH fail-closed.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Realocação forçada, conflito/PvP, ataque HIGH e exposição de fonte são operações de risco e precisam de autorização; diversas LOW somadas podem exigir HIGH.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Revelação de segredo operacional é ação informacional independente e sujeita a risco/consentimento; descoberta parcial não autoriza coerção HIGH.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Acumulação de dissimulações LOW que implique dano HIGH requer gate próprio. Engano defensivo não autoriza acusação falsa grave, hostilidade ou PVP mecânico automaticamente.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

A ruptura com facção, traição e revelação de agente duplo podem ser HIGH quando irreversíveis; classificar risco acumulado e bloquear sem autoridade/consentimento.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Antes de ação MEDIUM/HIGH por inteligência recebida, verificar autoridade, proveniência, acesso e risco. Falta de corroboração não equivale a aprovação de consequência.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Publicação de dossier view é ato autorizado por audiência/campo/finalidade, distinto de composição. Exposição de PC/fonte/abrigo e impactos HIGH falham fechados sem autorização.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Risk gate DEC-027 aplicado ao plano e ao conjunto de etapas; HIGH default-deny, inclusive se dividido artificialmente em LOW.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Arcos narrativos continuam avançando por condições/calendário autorizados; replanejar operação pessoal não executa automaticamente arco central.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-094/C (Discovery v9.0)

Deadlock ou espera longa não reclassifica nem autoriza ação HIGH; liberação de recurso de jogador, aborto material e efeitos nativos exigem política de autorização e gates.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

DEC-095: compensar pagamento/contrato usa novo gate/autorizações. DEC-096 proposta: impacto histórico HIGH/irreversível nunca passa a ser permitido apenas por constar de tabela temporal.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Cronologia DEC-096/C explicita fonte, data, janela de aplicação, versões disputadas e baseline; nunca aproximar datas nem converter evento do futuro em rumor atual.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Gates de risco não substituem ownership; HIGH e campo protegido exigem bloquear mesmo quando plano narrativo é convincente.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Arcos clássicos não avançam nem revelam desfechos por inferência de flags futuros.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Uma projeção corrigida DEC-102 não libera automaticamente ações de risco, disseminação ou alterações de scripts. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para risco de vazamento HIGH e gates de autorização por finalidade, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para políticas de risco e consentimento, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Custódia e liberação de bens são HIGH quando afetam ownership ou bens de PC; nenhum consentimento pode ser inferido de contrato genérico.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
