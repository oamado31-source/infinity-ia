# Distribuição de personagens a jogadores, ausências e devolução de controle — DEC-045

**Infinity AI Discovery v4.1 — arquitetura candidata, ainda sem implementação/SPEC.**  
**Aprovação:** DEC-045, modelo BG3 de redistribuição de PCs ausentes, sustentado por `ADR-0040`.  
**Próxima decisão:** DEC-046 — escopo das ações delegáveis ao controlador temporário.

## 1. Resultado da pesquisa: BG2:EE já possui uma base nativa

O [manual oficial *Baldur’s Gate II: Enhanced Edition — Amn Survival Guide*](https://cdn.steamstatic.com/steam/apps/257350/manuals/BGIIEE_-_Amn_Survival_Guide.pdf) documenta, nas páginas impressas 58–63:

- **Multiplayer:** uma sessão pode conter múltiplos participantes, e um participante pode controlar **um ou mais personagens**.
- **Character Arbitration (p. 59):** o líder da sessão **atribui slots de personagens aos jogadores**, com a possibilidade de escolher qualquer participante presente para cada slot.
- **Player Permissions (p. 60):** permissões nativas por jogador incluem modificar personagens, gastar ouro, transição de área, iniciar diálogos, ver fichas, pausar e gerir permissões.
- **Protagonista (p. 60):** o personagem do primeiro slot é protagonista e sua morte desencadeia *game-over* no modelo nativo.
- **Durante o jogo (pp. 61–62):** Character Arbitration e Player Permissions podem ser acessadas, e o anfitrião controla a reatribuição de personagens; as mudanças específicas em sessão devem ser testadas.
- **Party:** restrições de área e recursos compartilhados são nativas. A documentação não prova isolamento granular de escolhas, segredos ou inventário do PC ausente.

O [guia de coop de Baldur's Gate 3](https://www.shacknews.com/article/136509/co-op-baldurs-gate-3) descreve a redistribuição de personagens pelo menu de sessão quando um participante está ausente. É **referência de experiência de usuário**, não API ou código reutilizável.

**Conclusão técnica honesta:** controle de vários PCs por um mesmo jogador **é um recurso documentado do BG2:EE**, mas a integração automatizada, os limites de permissão e o comportamento na build real **ainda precisam de POC**.

## 2. Escopos de identidade e controle

| Identidade/escopo | Atribuição | Persistência |
|---|---|---|
| `player_owner_id` | Jogador titular do PC e histórico autoral | Estável, não muda porque a pessoa saiu da sessão |
| `pc_id` | Ficha/identidade e história do personagem | Estável por campanha, sobrevive a troca de controlador |
| `session_controller_id` | Participante presente que emite comandos no momento | Pode mudar por ausência e retorno |
| `engine_slot_id` | Slot/índice de controle na party do BG2:EE | Referência mecânica, não identidade narrativa |
| `assignment_epoch` | Versão monotônica da atribuição | Usada para detectar ações tardias e evitar duplo controle |
| `policy_version` | Política aprovada da campanha/participantes | Auditável e imutável para eventos passados |

**Invariante:** `A controla PC-1 e PC-2` não implica `A é titular de PC-2` nem `PC-1 conhece os segredos de PC-2`.

## 3. Processo lógico de redistribuição

```text
[Jogador B ausente ou desconectado]
             |
             v
[Host observa estado de B e do PC-B no jogo]
             |
             v
[Regras da campanha e delegação preexistente verificadas]
             |
      +------+------+
      |             |
[Autorizável]   [Inseguro ou ambíguo]
      |             |
      v             v
[Anfitrião usa     [Pausa / fallback / intervenção
Character          humana; sem assumir consentimento]
Arbitration]
      |
      v
[PC-B atribuído ao jogador A presente]
      |
      v
[Game engine confirma estado observável]
      |
      v
[Ledger registra controlador, intervalo e versão]
      |
      v
[Jogador B retorna e reassume slot por mediação do host]
      |
      v
[Resumo de fatos confirmados, sem quebrar ACL]
```

O processo acima descreve um **alvo de arquitetura**. A interface nativa de atribuição é documentada, mas o Infinity AI ainda **não executa** leitura nem controle automático da Character Arbitration. Quais ações pedem aprovação do titular permanecem em DEC-046.

## 4. Comandos mecânicos versus escolhas pessoais

| Tipo de ação | Tratamento DEC-045 | A definir pela DEC-046 / SPECS |
|---|---|---|
| Deslocamento, seleção, formação, ataques comuns | PC atribuído ao jogador presente; resultado depende do motor | Cotas de risco, consentimento prévio e limites por situação |
| Consumíveis, magia rara, gasto de ouro compartilhado | Não implicam transferência de propriedade | Limites de itens/recursos, confirmação e auditoria |
| Conversas com NPC e alternativas de diálogo | Não atribuir automaticamente a vontade ou a crença do ausente | Autorização do substituto para escolhas com impacto pessoal |
| Histórico secreto, missão pessoal e juramentos | Permanecem ligados ao titular e às ACLs | Quais atos podem prosseguir sem o titular presente |
| PvP, coerção, abandono do grupo, morte permanente | Não são implicitamente liberados | Requerem DEC-042/043 e escopo específico da substituição |
| Inventário pessoal, equipamentos insubstituíveis | O comando não configura propriedade do substituto | Restrições nativas, regras externas e riscos de interceptação |
| Ressurreição, transformação de alinhamento, mudança de classe | Consequências apenas por fatos/regras/host confirmados | Gatilhos mecânicos e autorizações de decisões críticas |

**Atenção:** o BG2:EE pode permitir certas ações sem checar a política externa. A segurança não está provada até teste de interceptação; se indisponível, informar a limitação e usar acordo humano/pausa, sem alegar bloqueio seguro.

## 5. Eventos externos e ledger candidato

```yaml
control_assignment_event:
  campaign_id: "lw-example"
  pc_id: "pc-mage"
  engine_slot_id: 2
  owner_player_id: "player-b"
  previous_controller_id: "player-b"
  new_controller_id: "player-a"
  cause: "owner_absent"
  authorization: "campaign_policy_and_preexisting_delegation"
  assignment_epoch: 15
  host_status: "CONFIRMED_OR_NEEDS_RECONCILIATION"
  effective_from_event_id: "evt-..."
  policy_version: "pending"
  timestamp: "pending"
```

Este YAML é **exemplo conceitual, não contrato definitivo**. O status é ilustrativo e não substitui os estados reais `CONFIRMED / REJECTED / UNCERTAIN` da futura bridge.

Ação de um personagem: `actor_pc_id`, `session_controller_id_at_action`, `owner_player_id`, `assignment_epoch`, `action_scope`, `engine_receipt_id`, `world_time`, `causal_event_ids`. O registro preserva a autoria real do comando humano sem imputar ao titular ausente intenção que não escolheu.

## 6. Segurança, memória e direitos

1. Separar ACL por **personagem que sabe** e por **jogador autenticado que pode ver**. Acesso técnico à ficha não libera uma memória narrativa secreta externa.
2. O controlador temporário pode conhecer informações por meio legítimo durante o controle. Registrar a origem dessa aquisição; não transmitir automaticamente os segredos à memória do seu próprio PC.
3. Não inventar consentimentos de jogadores ausentes, seja por silêncio, timer, texto em chat ou LLM.
4. Evitar confundir a nova atribuição com transferência permanente de ficha, autoria ou itens, inclusive após save/load.
5. A morte é possível se o motor e a campanha permitirem, não existe imunidade garantida por ausência.
6. Atribuições em conexão instável, mudança simultânea e ações tardias exigem epoch/versão e reconciliação.
7. O modo Original não recebe regras Living World, nem relatórios de segredos, nem política de delegação.

## 7. POCs de compatibilidade prioritárias

- **POC-CTRL-01:** BG2:EE limpo, host + dois clientes, atribuir dois slots ao jogador A e um a B, confirmar controle de ambos com comandos simples.
- **POC-CTRL-02:** em pausa/ponto seguro, retirar B, atribuir PC-B a A pela Character Arbitration e retomar; registrar o procedimento real.
- **POC-CTRL-03:** retorno B, reassociar o mesmo PC-B, comparar atributos, inventário, efeitos de status e XP.
- **POC-CTRL-04:** save e load após redistribuição, comparar PC IDs, slots e controle; evitar duplicação.
- **POC-CTRL-05:** queda abrupta de B durante combate, medir se controles e pausa ficam disponíveis; não pressupor troca instantânea.
- **POC-CTRL-06:** testar personagem no slot 1 e morte do protagonista; nenhum workaround afirmado sem evidência.
- **POC-CTRL-07:** testar permissões nativas para diálogo, ouro, ficha e modificação de personagem em A/B.
- **POC-CTRL-08:** diferença entre ownership narrativo e controles da interface; detectar exposição de segredos privados.
- **POC-CTRL-09:** ações e inventário antes/depois da troca, verificar sincronização entre clientes.
- **POC-CTRL-10:** tentar reatribuir slot enquanto antigo dono ainda está conectado; evitar disputa e conflitos de consentimento.
- **POC-CTRL-11:** testar reconexão B durante luta e transição de áreas, com estado `UNCERTAIN`.
- **POC-CTRL-12:** reatribuição de PC antes de ação cara/irreversível; provar eventual bloqueio ou assumir que não existe.
- **POC-CTRL-13:** atribuição de companion NPC versus PC criado e diferenças reais de comportamento.
- **POC-CTRL-14:** isolamento entre Original/Living World e entre campanhas.
- **POC-CTRL-15:** interface EEex/bridge, se houver, somente após baseline sem mods.
- **POC-CTRL-16:** verificar latência e segurança de acesso à tela de arbitragem com dois clientes.
- **POC-CTRL-17:** conferir atribuições nos snapshots/logs após queda de rede do host.
- **POC-CTRL-18:** ação iniciada por A quando PC-B já foi devolvido a B; rejeitar eventos tardios na camada externa.
- **POC-CTRL-19:** atribuir todos os slots a um participante e verificar limites de party e comandos no BG2:EE.
- **POC-CTRL-20:** testar sem qualquer LLM e sem rede externa de IA, garantindo fluxo manual básico.

## 8. Aceitação e bloqueios

**Aceitação arquitetural:** o projeto deve representar vários PCs por controlador, delegação temporária e retomada do controle pelo titular sem trocar a identidade do PC nem sua história, e sem fazer a IA representar automaticamente o ausente.

**Bloqueios técnicos:** interface/versão real, EEex, hooks, alteração em combate, restrição de acesso a segredos, protagonista/game-over, estados inconsistentes e persistência do mecanismo. Sem SPEC/POC, não anunciar automação nem controles preventivos garantidos.

## 9. Próxima decisão

**DEC-046 — escopo da delegação temporária**: o controlador provisório terá autoridade completa de personagem; somente movimentos/combate; ou permissões granulares por categoria, configuradas antes pelo titular e pela política da campanha? A recomendação para discussão é a terceira opção, sem prejulgar a aprovação do usuário.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Contribuição de um PC delegadamente controlado fica ligada ao PC; distinguir controlador de titular. Não supor que o titular autorizou todo ato fora do escopo.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Controlar temporariamente PC de terceiro não muda sua identidade factual nem concede automaticamente acesso ao segredo de sua persona. Dados de dono e controlador permanecem separados.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

PC ausente não é considerado culpado apenas por integrar grupo, e controlador temporário não assume identidade do titular; DEC-078 necessita evento e autoria comprovados.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Mandados contra PC delegado DEC-079 não revelam segredos de titular e não transfere autoria fictícia ao controlador. Respeitar consentimento e identidade estável.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

PC delegado não admite culpa, compromisso ou testemunho por mera atuação do controlador além de permissões vigentes.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Controlador delegado não herda acesso ao depoimento selado do titular e não decide por padrão revelar informações pessoais.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Personagem ausente/delegado não aceita fuga, escolta ou testemunho sem permissão do titular; controlador temporário não recebe segredo operacional automaticamente.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Controlador temporário só conhece campos de plano necessários e permitidos; dono ausente não concede autorização automática para divulgar refúgio.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Controlador temporário não assume consentimento do titular para criar documentos ou mentiras em seu nome; fontes e aliases mantêm owner distinto de controller.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Delegação temporária não concede controle sobre mudança secreta de lealdade/compromisso do PC salvo permissão explícita de escopo adequado.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Controlador temporário de PC não assume o papel de informante, nem gasta recursos/assina contrato além do escopo delegável.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Jogador temporariamente controlador de PC não recebe automaticamente segredos que a fonte revelou ao titular nem pode assinar avaliações em seu nome.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

PC ausente ou delegado pode ter dados em dossiê, mas ninguém assume automaticamente sua autorização ou decisão de compartilhar um segredo pessoal.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Delegado só aceita operação dentro de escopo; não movimenta/gasta recursos do dono por decisão do LLM.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Delegação temporária tem escopo e prazo, validados em cada revisão; retirada do titular bloqueia novas ações fora das permissões remanescentes.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Delegação de PC não é licença para transferi-lo entre operações nem comprometer recursos pessoais; validar titular, controlador, escopo, revisão e janela.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

PC temporariamente delegado não permite que scheduler libere seu equipamento, cancele suas decisões ou execute movimentos sem escopo autorizado.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-096/C — Discovery v9.2

Regras históricas DEC-096/C não ampliam scope de delegação de PC; todo gate mantém consentimento e epoch/owner.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Personagem ausente não deve aparecer como duplicata nem adquirir compromissos mecânicos pela materialização local; respeitar delegação aprovada.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Delegação entre PCs não concede licença permanente de inventário ou de quest.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Controle temporário de personagem não permite ler seu histórico romântico/quests privados fora das permissões delegadas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** DEC-101 interpretation is read-only, version-pinned and independent of gateway/host execution. A confirmed semantic milestone does not authorize actions or prove a command receipt; mod upgrades, checkpoint restore, revised mapping, epoch mismatch or contradictory states cause fail-closed reconciliation. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **ausência de PC**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para personagem ausente não participa automaticamente de transmissão, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para ausência de PC impede confissão ou compromisso implícito, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Ausência de PC não delega assinatura de termo. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

PC ausente não delega assinatura ou aceite implícito de aditamentos. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
