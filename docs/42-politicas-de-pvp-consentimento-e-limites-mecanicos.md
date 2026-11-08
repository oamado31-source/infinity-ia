# Políticas de PvP, consentimento e limites mecânicos — DEC-042

**Discovery v3.8 — desenho técnico candidato, não SPEC final**  
**Decisão vinculante:** DEC-042 / ADR-0037 (opção C aprovada).  
**Status:** nenhum comando foi implementado, bloqueado ou validado no BG2:EE.

## Objetivo

Permitir que campanhas cooperativas privadas definam **por categoria** quais interações hostis entre PCs são legítimas, sob quais condições de consentimento e com que consequências, sem afetar autonomia individual, confidencialidade dos históricos e autoridade do host.

## Separações obrigatórias

1. **Escolha do jogador / agência:** o controle da vontade e da fala do PC é do jogador correspondente.
2. **Consentimento extrajogo (OOC):** controle técnico e social de limites dos participantes. Não descreve a vontade fictícia do PC.
3. **Política de campanha:** define quais categorias existem e quais requisitos precisam ser satisfeitos para cada uma.
4. **Permissão da ação:** validação específica de tipo, alvo, origem, contexto, duração e risco, distinta da configuração genérica.
5. **Resultado mecânico:** execução e confirmação pelo host, não pelo LLM nem pelo ledger de consentimentos.
6. **Consequência narrativa:** só após confirmação pertinente, com rastreabilidade, reputação/alinhamento conforme critérios próprios.

## Fluxo lógico candidato

```text
Player/Host action intent
      |
      v
PvP Action Classifier [rules; provenance; indirect effects]
      |
      v
Campaign Policy + Participant Consent Scope + risk gate
      |                            | allowed               \ rejected/uncertain
      v                        v
Typed Action Gateway          Block / quarantine / reconcile
      |
      v
BG2:EE host / EEex bridge [only if POC confirms support]
      |
      +--> CONFIRMED --> persist event once, update quest/reputation/alignment with provenance
      +--> UNCERTAIN --> reconcile; no blind replay
      +--> REJECTED  --> no persistent mechanical success
```

**Alerta de inviabilidade:** o motor comercial pode executar um comando de teclado/ordem de combate sem consultar o gateway. O diagrama é uma arquitetura pretendida e **não comprova a existência de hooks bloqueantes**. Antes de prometer PvP seguro, é obrigatório inspecionar interceptação de ataques, efeitos em área, comandos dos clientes, inventário, invocações, scripts e comportamentos da IA original.

## Contratos candidatos de dados

```yaml
campaign_pvp_policy:
  campaign_id: campaign-example
  version: pending
  baseline: coop_safe
  categories:
    duels: opt_in
    attacks: blocked
    theft: blocked
    hostile_magic: blocked
    imprisonment: blocked
    permanent_death: special_authorization
  owner_authority: host_configures_not_consents_for_others
  change_protocol: requires_notice_and_safe_boundary

pvp_consent_scope:
  consent_id: opaque
  campaign_id: campaign-example
  giving_player_id: player-B
  actor_ids: [PC-A, PC-B]
  scope: duel-only
  expires_at: session_or_event_bound
  risk_caps: [no_permanent_death, no_item_loss]
  revoked_at: null

pvp_action_proposal:
  action_id: unique
  session_id: session-example
  actor_pc_id: PC-A
  initiator_player_id: player-A
  target_pc_ids: [PC-B]
  action_category: attack
  indirect_origins: []
  expected_risk: medium
  policy_version: pending
  consent_refs: []
  state: PROPOSED
```

Os valores são **ilustrativos**, não configurações definitivas nem schema aprovado. Evitar coletar ou revelar informações de conta de usuários sem necessidade.

## Classes de interações e política candidata

| Classe | Exemplos | Controle proposto | Gate adicional |
|---|---|---|---|
| `ROLEPLAY_DISPUTE` | discussão, discordância, rivalidade | permitido dentro da agência individual | DEC-041, conhecimento DEC-028 |
| `DUEL` | confronto voluntário delimitado | consentimento explícito dos atingidos + política da campanha | host e engine hook |
| `HOSTILE_DAMAGE` | golpe, magia, efeito de área | consentimento/escopo por política | comportamento indireto, friendly fire |
| `THEFT` | furto e transferência coerciva de item | escopo específico; ação mecânica host-confirmada | idempotência e inventário |
| `MIND_CONTROL` | charme, medo, paralisia, dominação de PC | escopo específico; **não** inferir escolhas do controlado | magia/status/salvaguardas |
| `RESTRAINT` | prisão e impedimento persistente de ação | consentimento e duração sob política | salvamentos e desconexões |
| `PERMADEATH` | remoção definitiva de PC/ressurreição impossível | política HIGH/especial e confirmação expressa | DEC-043 ainda aberta |

**Ambiguidade a resolver em SPECS:** *friendly fire* acidental, invisibilidade do atacante, consentimento por ato versus por campanha, combat logging, limites de retirada e efeitos adversos que o motor execute antes de o gateway interceptá-los.

## Perfil de segurança e modos de compatibilidade

- `coop_safe`: recomendação inicial quando não houver configuração inequívoca; sem mutações hostis entre PCs até opt-in, mesmo com conflito social narrativo.
- `duels_consensual`: habilita apenas duelos com limites delimitados, se houver suporte técnico.
- `custom_pvp`: categorias avançadas e escopos testados, sem facilitar bypass de consentimento.
- `unverified_engine`: se não for possível aplicar um controle com confiabilidade, a UI não pode afirmar que o aplica; a funcionalidade deve ser desabilitada ou identificada como indisponível até resolvida.

## Direitos, eventos e persistência

- O consentimento **não altera** o backstory autoral; ações confirmadas podem alterar estado do mundo e reputação/alinhamento conforme suas políticas.
- O host configura a política e confirma mecânica; não é representante de consentimento de outro jogador.
- `campaign_id`, `session_id`, `action_id`, `policy_version` e `receipt_id` separados; reconciliação após desconexão e save antigo.
- NPC, magias de área, armadilhas, projéteis indiretos e efeitos de scripts devem preservar o mesmo controle de risco quando ligados à intenção hostil contra outro PC, se tecnicamente aplicável.
- Logs e notificações de consentimento exigem visibilidade restrita por destinatário; vazamento de segredos pessoais continua proibido.
- O modo Original e outras campanhas não compartilham regras PvP, eventos ou concessões de consentimento.

## POCs e testes candidatos

| Teste | Arranjo e evento | Critério de aprovação |
|---|---|---|
| PVP-01 | 2 clientes, PvP desativado, ordem de ataque | Prevenção antes do dano **se suportada**; caso contrário, detectar lacuna e não anunciar controle seguro |
| PVP-02 | Duelo consensual entre A/B | Só ações permitidas entre A/B; C não é afetado por bypass |
| PVP-03 | Jogador A desconecta durante duelo | Revalidação e política de pausa/revogação, sem ação em nome do ausente |
| PVP-04 | Roubo proibido com duelo liberado | Item não muda de dono por operação do gateway; avaliar motores que ignoram bloqueio |
| PVP-05 | Magia de área atinge PC não consentinte | Identificar dano colateral e impedir escape das restrições se tecnicamente viável |
| PVP-06 | Invocação ou armadilha utilizada para atacar PC | Aplicar política ao efeito indireto com proveniência rastreável |
| PVP-07 | Controle mental contra PC | Nenhum input/fala voluntária é produzido pelo LLM em nome do alvo |
| PVP-08 | Host tenta consentir em nome de cliente | Recusa sem evidência de aprovação do próprio titular |
| PVP-09 | Alteração de política durante combate | Não ampliar permissão silenciosamente |
| PVP-10 | Save/load após troca de versão | Compatibilidade ou bloqueio explícito; sem consentimento indevido |
| PVP-11 | Receipt `UNCERTAIN` + retry | Sem golpe, perda de item ou efeito repetido |
| PVP-12 | Pacote com texto malicioso induz permissão | Gateway ignora instrução textual não confiável |
| PVP-13 | PvP no Living World; modo Original | Original não recebe a política nem efeitos do Living World |
| PVP-14 | Duelo com condição de fim sem morte | Verificar término e segurança, sem prometer 'não letal' antes de POC |
| PVP-15 | Conduta hostil e mudança de reputação/alinhamento | Avaliar autoria e fatos confirmados; nenhum ajuste automático por etiqueta de PvP |
| PVP-16 | Tentativa de morte permanente em duelo ordinário | Bloqueio até DEC-043 e política especial validada |
| PVP-17 | Ação de NPC usada como intermediário intencional | Verificar escopo, responsabilidade e risco, evitando bypass |
| PVP-18 | Política host/clientes divergente | Diagnóstico e impedimento de execução inconsistente |

## Riscos não resolvidos

- Engine pode permitir comandos diretos de teclado/cliente, de forma que a validação **somente no gateway** seja insuficiente.
- O modo cooperativo pode pressupor *friendly fire* ou efeitos entre aliados; interceptação parcial não deve oferecer falsa segurança.
- Consentimento verbal por chat ou texto da IA não substitui permissão técnica sem autenticidade verificada.
- Bloquear dano após o host já aplicá-lo pode não ser reversível sem efeitos colaterais; preferência por prevenção, com reconciliação quando falhar.
- Se não houver POC positiva, a opção segura é **manter as regras atuais de BG2:EE e não anunciar a camada PvP como habilitada**, documentando limitações.
- A política de **morte, ressurreição e permanência dos PCs (DEC-043)** ainda não está decidida.

## Próxima discussão

**DEC-043:** como tratar morte, ressuscitação, retorno e consequências persistentes para personagens de jogadores, em um Living World com alinhamento dinâmico, histórias pessoais, coop e PvP configurável.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Atribuir responsabilidade por ação hostil entre PCs não pode contornar gates de PvP/consentimento nem culpabilizar automaticamente aliados ausentes.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Uso de denúncia DEC-078 para perseguir/aprisionar PC não deve contornar limites de PVP e consentimento; sistema de acusação narrativa não é autorização de agressão mecânica.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Acusação jurídica DEC-080 não contorna proteções para coercão, dano ou PVP; nenhuma captura/hostilidade mecânica sem gate/consentimento aplicável.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Reparação de danos entre PCs não autoriza confisco, coerção, punição de jogador ou efeitos PvP mecânicos sem política de consentimento e host.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Punição institucional contra outro PC não contorna políticas de PvP, risco, controle e ausência de autorização mecânica.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Denúncia ou exposição de segredo de PC não autoriza perseguição/PvP; riscos de dano e consentimento continuam sob políticas específicas.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Suposta retaliação não desencadeia PvP/coerção contra PC sem gates e consentimento, mesmo quando a narrativa a classifica como risco alto.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Vazamento de rota para hostilidade de PC não autoriza PvP/emboscada unilateral; consentimento e gates mecânicos independentes.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Operação com desinformação não contorna limites de PvP, não autoriza incriminação falsa de PC para impor sanção nem inicia emboscada mecânica sem gates.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Agente duplo em party não é gatilho automático de PvP ou roubo; danos graves requerem consentimento/políticas aplicáveis e recibos mecânicos comprovados.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Alegação de traição ou crime contra jogador não autoriza PVP, punição, coerção ou disputa mecânica sem evidência, consentimento e política pertinente.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-091/C — Discovery v8.7

Planos hostis entre PCs exigem consentimento específico e políticas PvP; planejamento não permite dano por delegação implícita.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Suspensão/aborto de plano HIGH não substitui gates de dano, PvP e coerção; perigo agregado exige avaliação antes de retomar.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-094/C (Discovery v9.0)

A recuperação de impasse não pode iniciar PVP ou impor dano por prioridade; qualquer conflito entre players segue os gates da DEC-042.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Acordos PVP não transferem automaticamente ownership de itens, scripts nem controle de personagens.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

PvP e consentimentos não podem ser inferidos de flags; observação não concede controle sobre PCs.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **consentimento**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Jogadores podem recusar acordo ou alteração sem confissão automática. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Agressão ou sanção entre PCs não é derivada automaticamente de descumprimento alegado. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Proibir retirada involuntária de inventário de outro PC e uso de escrow como atalho de PvP ou confisco.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
