# Delegação granular, ACL de controle e consentimento de titular — DEC-046

**Infinity AI Discovery v4.2 — desenho técnico candidato, ainda não é SPEC nem implementação.**  
**Aprovado:** DEC-046, opção **C**; referência: `decisions/ADR-0041-delegacao-temporaria-por-categorias-e-consentimento-do-titular.md`.  
**Anterior:** DEC-045 / ADR-0040, Character Arbitration e múltiplos PCs por pessoa.  
**Próxima:** DEC-047 — autonomia narrativa dos companions NPC versus controle tático dos jogadores.

## 1. Problema a resolver

A atribuição de um slot de BG2:EE concede controle mecânico dentro do que o motor oferece, **não** uma procuração irrestrita do jogador dono do PC. Uma campanha Living World precisa distinguir, para cada ação, a identidade do personagem, o titular da história, o controlador temporário, o tipo de efeito, a gravidade, as permissões e o resultado confirmado. As políticas devem funcionar sem LLM e não dependem de inferir consentimento a partir de silêncio ou desconexão.

A implementação deve partir da capacidade nativa **documentada** (Character Arbitration, Player Permissions), sendo que o manual não demonstra hooks para **permissão granular por PC e evento**. A aplicação externa de políticas é uma intenção; por ora a única resposta honesta para restrições não interceptáveis é adotar pausa, não delegar a sessão naquele momento ou um acordo humano com riscos explícitos.

## 2. Autoridade: ordem de autorização

1. Identificar `campaign_id`, modo Living World, `pc_id`, `player_owner_id`, `session_controller_id` e `engine_slot_id`.
2. Confirmar atribuição `assignment_epoch` vigente; se a versão/estado for incerta, não gerar nova mutação e reconciliar.
3. Ler **política de campanha versionada** e a **delegação explícita do titular**, válida para controlador, sessão, prazo e categoria.
4. Classificar ação por categoria, recursos afetados, risco LOW/MEDIUM/HIGH, irreversibilidade e cruzamento com PvP, morte, canon e conhecimento.
5. Aplicar interseção de limites: campanha ∩ titular ∩ risco/consentimento ∩ regra mecânica/estado do motor; **deny prevalece**. Mesmo uma autorização de categoria não substitui autorização histórica especial ou consentimento PvP.
6. Se ação for mediável pelo gateway, construir proposta tipada e aguardar confirmação mecânica. A autorização narrativa não constitui confirmação de efeito.
7. Se a ação ocorrer diretamente na UI do motor e não existir hook comprovado, **não alegar que foi bloqueada**. Registrar risco, orientar ponto seguro, pausa ou retirar delegação se a política não puder ser cumprida.
8. Registrar proposta, controlador, titular, deliberação, receipts e consequências sem vazar segredos. Eventos incertos não devem ser repetidos cegamente.

## 3. Esboço de contrato de delegação (não implementado)

```yaml
delegation_grant:
  grant_id: UUID
  campaign_id: CAMPAIGN-ID
  pc_id: PC-ID
  player_owner_id: OWNER-ID
  allowed_controller_ids: [PLAYER-ID]
  allowed_categories:
    movement: true
    tactical_combat: true
    routine_consumables: false
    item_transfers: false
    routine_dialogue: false
    collective_quests: false
    personal_arc_decisions: false
    oaths_alignment_pacts: false
    private_backstory_disclosure: false
    pvp_actions: false
    irreversible_canonical_events: false
  conditions:
    max_spend: TO_BE_SPECIFIED
    item_rarity_policy: TO_BE_SPECIFIED
    pvp_policy_ref: POLICY-ID
    mortal_risk_acknowledged: true
  issued_at: TIMESTAMP
  expires_at: TIMESTAMP
  grant_version: INTEGER
  revoked_at: null
  owner_auth_proof_ref: PROOF-ID
assignment:
  engine_slot_id: SLOT-ID
  session_controller_id: PLAYER-ID
  assignment_epoch: INTEGER
  engine_receipt_ref: RECEIPT-IF-AVAILABLE
```

**Atenção:** o bloco é um exemplo de **esquema candidato**, não tokens/IDs reais, API confirmada ou defaults obrigatórios. `max_spend` e itens equipados podem exigir subcategorias; políticas granulares só serão anunciadas como efetivas quando provadas.

## 4. Matriz de tipos de ação e limites

| Ação | Delegação por categoria | Risco adicional |
|---|---|---|
| Deslocar, selecionar, explorar | `movement` | Transição de área pode ativar cutscene irreversível |
| Combate ordinário, magias e habilidades | `tactical_combat` | Morte real sob DEC-043; recursos escassos tratados separadamente |
| Poções, pergaminhos, charges | `routine_consumables` | Raridade, inventário e gasto permanente |
| Vender, doar, trocar item único | `item_transfers` específica | Propriedade/legitimidade, receipt do host |
| Comércio com ouro compartilhado | Limites separados | Saldo e controle per player nativos podem diferir |
| Iniciar diálogo comum | `routine_dialogue` | Alguns diálogos produzem escolhas HIGH sem aviso |
| Decisão sobre missão coletiva | `collective_quests` | Não suprime veto pessoal do titular sobre seus compromissos |
| Aceitar pacto, alterar religião, jurar fidelidade | `oaths_alignment_pacts` + requisitos | Default deny; escolhas íntimas e consequências AD&D 2e |
| Revelar passado secreto ou editar histórico | Não decorrente de slot | ACL DEC-019/020/028 e proveniência |
| Atacar outro PC ou aceitar duelo | `pvp_actions` mais opt-in separado | Consentimento DEC-042/043, efeitos indiretos |
| Sacrifício deliberado, morte permanente | Política HIGH, não herdar do combate | Regras DEC-027/034/043 |
| Destruição de cidade/alteração canônica | Política histórica extraordinária | DEC-009/034, controle de evento irreversível |

**Mudança de alinhamento:** ações efetivamente confirmadas com contexto poderão continuar impactando o PC delegado segundo DEC-035/036. A delegação não elimina consequências; tampouco concede ao substituto a intenção íntima não comprovada do titular ou autorização para forçar uma transição moral.

## 5. Estados, duração e retorno

Estados candidatos: `DRAFT_GRANT` → `ACTIVE_GRANT` → `REVOKED`/`EXPIRED`; atribuição `OWNER_CONTROL` → `DELEGATED_CONTROL` → `RETURN_PENDING` → `OWNER_CONTROL`; falhas `UNCERTAIN` até reconciliação.

- Atribuição sem grant válido não implica autorização narrativa.
- Conceder permissão deve exigir autenticação do titular antes da ausência, escopo claro e registro de versão. A política poderá ser restrita ou revogada depois.
- Retorno do titular invalida capacidades/epochs anteriores após confirmação de reassociação; transações iniciadas antes e finalizadas depois precisam de classificação e reconciliação.
- Não mudar o proprietário da história, nem duplicar itens/fichas, nem reprocessar side effects no retorno.
- Revogação é prospectiva. Fatos do motor já confirmados mantêm sua trilha, inclusive ocorrências que violem uma política narrativa; violação exige tratamento explícito, não reescrita silenciosa.
- Uma sessão com ausência abrupta durante combate deve usar fallback real; nenhuma promessa de congelamento automático do PC, imunidade ou proteção total sem suporte medido.

## 6. Conhecimento, segredo e experiência de usuário

Separar quem **controla fisicamente** o slot, quem **é titular** do histórico, quem **tem legitimamente conhecimento** no mundo e quem **pode consultar** uma memória privada externa. As camadas não são equivalentes.

A UI candidata poderá indicar as categorias autorizadas, limites e titular, sem revelar conteúdo privado. Em vez de mostrar segredos ao substituto, os diretores narrativos podem **adiar gatilhos de arcos privados** quando exigirem decisão do titular. Não presumir que cutscenes e diálogos canônicos de BG2:EE sejam interceptáveis.

Quando A controla simultaneamente o próprio PC e o PC de B, uma descoberta que ambos testemunhem pode ser observável por ambos — mas a memória secreta anterior de B não passa automaticamente ao PC-A. Distinguir conhecimento adquirido pelo jogador humano e fatos internalizados na narrativa para cada personagem.

## 7. Gate de compatibilidade BG2:EE / EEex e multiplayer

**O que existe na documentação do motor:** um jogador pode controlar múltiplos personagens via atribuição de slots, com permissões nativas por jogador na sessão. [Fonte: manual BG2:EE, multiplayer pp. 58–63](https://cdn.steamstatic.com/steam/apps/257350/manuals/BGIIEE_-_Amn_Survival_Guide.pdf).

**O que ainda não existe como evidência:** veto granular de ações por `pc_id`; interceptar menu de diálogo, inventário, movimentação, feitiços e decisões pessoais antes de efeitos; rollback de ações não autorizadas; pausa segura no meio de combate; UI de revogação automática; hooks EEex interoperáveis em multiplayer. O motor pode produzir mudanças ainda que as regras externas as proíbam. Antes de integrar, provar cada hook ou degradar a feature honestamente.

Ordem de POC: instalação BG2:EE limpa → host + dois clientes e Character Arbitration → permissões nativas realmente oferecidas → UI sem automação → Action Gateway read-only e proposições inofensivas → hooks de veto se comprovados → EEex/mods em builds reprodutíveis → testes de save/load, desync e recuperação. Se o veto requerido não funcionar, **não habilitar delegação de alto risco como recurso seguro**.

## 8. Vinte testes candidatos (a detalhar nas SPECS)

1. **POC-DEL-01** — titular B autoriza movimento ao controlador A; confirmar atribuição e presença em sessão.
2. **POC-DEL-02** — A controla PC-A e PC-B simultaneamente, sem mesclar memórias, IDs ou históricos.
3. **POC-DEL-03** — ausência de grant pessoal não cria autorização narrativa apesar de Character Arbitration.
4. **POC-DEL-04** — concessão explícita de combate não autoriza venda de item único.
5. **POC-DEL-05** — permissão de diálogo comum não permite compromisso de arco pessoal.
6. **POC-DEL-06** — um diálogo iniciado automaticamente fora do gateway revela a capacidade real ou limitação de interceptação.
7. **POC-DEL-07** — mudanças normais em inventário, poções e ouro observadas no host são conciliadas sem criar item duplicado.
8. **POC-DEL-08** — item exclusivo e ouro compartilhado sujeitos a categorias/limites distintos.
9. **POC-DEL-09** — PvP hostil direto e indireto: verificar políticas e capacidade real de veto.
10. **POC-DEL-10** — combate delegado com morte: confirmar riscos reais sem imunidade ou rollback inventados.
11. **POC-DEL-11** — divergência histórica HIGH requer política especial apesar de delegação ampla.
12. **POC-DEL-12** — pacto/juramento e mudança de classe não ocorrem por autorização genérica de exploração.
13. **POC-DEL-13** — acesso ao histórico privado via LLM é filtrado antes de recuperar contexto.
14. **POC-DEL-14** — jogador A não transfere conhecimento privado de PC-B para PC-A.
15. **POC-DEL-15** — expiração/revogação elimina capacidades futuras e rejeita versões antigas.
16. **POC-DEL-16** — retorno de B após intervalo delegado mantém PC e estado confirmado, sem apagar eventos.
17. **POC-DEL-17** — perda de conexão durante combate identifica limites de pausa/reassociação efetivamente existentes.
18. **POC-DEL-18** — race entre retorno de B, comando tardio de A e mudança de assignment_epoch exige reconciliação.
19. **POC-DEL-19** — save/load e reinício do host preservam trilha de grants e eventos, sem repetir mutações.
20. **POC-DEL-20** — modo Original e outra campanha não recebem grants, contextos, segredos nem permissões Living World.

## 9. Critérios de aceitação da arquitetura

- O titular escolhe **antes** o escopo de delegação por categoria e pode revogar concessões prospectivamente.
- Controle mecânico não é autorização ilimitada de atos pessoais e não transfere direitos de edição/segredo.
- As regras PvP, mortalidade, fatos HIGH e cânone têm prioridade sobre permissões operacionais.
- Host/engine continuam autoritativos para efeitos mecânicos e o ledger narrativo preserva proveniência.
- Qualquer veto que dependa de hook do BG2:EE permanece bloqueado até POC; fallback explícito evita alegação de segurança não comprovada.
- O fluxo não requer IA controlando PC ausente nem modelo ativo por tick.

## 10. Próxima decisão

**DEC-047 — companions NPC canônicos e novos: autonomia narrativa versus controle tático.** O BG2:EE permite comando tático de membros da party, mas no Living World seus companheiros também teriam interesses, opiniões, relações e limites próprios. Devemos preservar o controle tradicional dos jogadores, automatizar a agência completa ou combinar **controle tático do grupo com uma camada de personalidade/reação contextual e consentimento narrativo**, respeitando o motor, a cronologia e a memória? Essa decisão é distinta da DEC-046, que protege PCs titulares de jogadores humanos.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

O ledger preserva titular e controlador e verifica categorias de ação autorizadas. Atribuição social não substitui consentimento do titular.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Divulgação de pseudônimo/identidade do titular exige autorização específica dentro da delegação e das políticas de segredo; nenhuma permissão implícita por acesso tático.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Defesa e aceitação de sanção DEC-078 são ações voluntárias do PC com autorização de seu titular/delegado conforme escopo, não inferidas por NPC/LLM.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Controlador delegado não pode aceitar compensação que modifica pertencimento/inventário do PC sem permissão explícita e receipt; titular e controlador permanecem distintos.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Delegação não confere direito de confessar, acusar ou revelar segredos do titular sem permissão específica; auditabilidade de controlador vs. personagem.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Divulgação, denúncia e acesso a testemunhos secretos exigem categorias de consentimento específicas; controle tático não autoriza testemunhar pelo PC.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Medidas de realocação, exposição de segredo e escolta são ações de escopo específico, não autorizadas pela mera delegação de combate.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Delegação tática não equivale a permissão para compartilhar informação operacional privada; verificar field-level ACL e consentimento por finalidade.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Participar de contraespionagem, divulgar rota, redigir documento falso ou implicar terceiros são permissões separadas; delegação tática não implica autorização informacional.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Gerenciar ações táticas delegadas não implica licença para conspirar, jurar fidelidade, mentir ou expor segredo em nome do PC titular.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Delegações requerem permissão granular para negociação, remuneração e divulgação. Sem permissão, protocolo registra proposta pendente, não aceitação.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Delegação não implica autorização de compartilhar relatório privado ou declarar novo fato; registrar viewer, purpose e rights na recuperação.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Compartilhar dossiê com detalhes do titular exige delegação explícita daquela finalidade e audiência; dar ordens táticas não concede poder de revelar fontes privadas.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Consentimento granular do titular prevalece em planos de escolta, espionagem ou operações de risco.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Reautorizações por alteração material devem consultar as permissões granulares vigentes e registrar aceite/recusa por titular; silêncio não significa consentimento.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Reatribuição de NPC ou PC delegado decorrente de conflito de reserva requer permissões específicas; urgência/fairness não sobrepõe proibições.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Permissão de controle delegado não implica permissão de renunciar a reservas, desistir de uma quest ou autorizar HIGH por starve/deadlock.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Delegação em co-op não confere ownership mecânico ilimitado ao orquestrador; reconciliar epoch, consentimento e receipts ao retorno do jogador.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Permissões delegadas são escopadas, revogáveis e não equivalem a ownership pleno da instância.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Delegação granular inclui negação de segredos e de flags de estado não autorizadas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **delegação PC**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para delegação não confere poder de rever crença do controlador do PC, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para delegação de PC não implica perdão ou consentimento, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Controle de personagem ausente não legitima pagamento ou confissão sem grant. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Controle delegável não equivale a autorização para pagamentos de terceiros. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Delegação de jogo e mandato de custódia são permissões separadas e versionadas; expiração/ausência bloqueiam transferência.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
