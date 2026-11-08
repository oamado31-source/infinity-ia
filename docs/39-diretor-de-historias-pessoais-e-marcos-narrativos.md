# Personal Story Director — geração híbrida e acompanhamento de arcos pessoais

**Discovery v3.5** · **DEC-039 opção C aprovada** · **Arquitetura candidata, não SPEC implementada**

## Objetivo

Transformar históricos versionados, fatos confirmados, vínculos, reputações, escolhas éticas e acontecimentos do cenário em histórias individuais coerentes, com ganchos, marcos, alternativas, consequências e condições verificáveis. As histórias convivem com a campanha cooperativa e com os arcos clássicos sem substituir os protagonistas canônicos.

## Fronteiras de responsabilidade

| Sistema | Responsabilidade | Não pode |
|---|---|---|
| Personal Story Director | Selecionar oportunidades, manter arcos/etapas, propor progressão e verificar dependências | Inventar estado mecânico ou reescrever fatos confirmados |
| Rules/Template Registry | Estruturas narrativas, regras de elegibilidade, impacto/raridade e condições de marcos | Tratar template como canon automaticamente |
| Lore/Chronology Guard | Validar data inicial da campanha, entidade, região, timeline e ramificações | Declarar fatos de outros anos sem adaptação |
| Knowledge Guard | Filtrar fatos por protagonista, NPC, jogador e finalidade antes do LLM | Copiar backstories secretas para prompts públicos |
| Local LLM | Propor texto, estrutura de missão e alternativas a partir de contexto permitido | Executar comandos, recompensas, decidir canonicidade ou concluir marco |
| World Memory/Event Log | Reconstituir contexto, eventos confirmados e projeções, manter versões | Mesclar estados de campanhas diferentes |
| Risk/Action Gateway | Validar tipo de ação, permissões, impacto e duplicação | Executar Lua livre de um modelo |
| BG2:EE host/bridge | Executar mecânica permitida, emitir confirmação | Garantir capacidade não testada em EEex/multiplayer |

## Estados candidatos por arco

`IDEA` → `PROPOSED` → `VALIDATED` → `OFFERED` → `ACTIVE` → `RESOLVED`

Desvios: `DEFERRED`, `DECLINED`, `SUSPENDED`, `BLOCKED_BY_CANON`, `BLOCKED_BY_RESOURCE`, `AWAITING_AUTHORIZATION`, `AWAITING_HOST_RECEIPT`, `NEEDS_RECONCILIATION`, `CANCELLED_WITH_REASON`.

- `RESOLVED` requer evidência verificável de resolução narrativa e, quando aplicável, confirmação mecânica; não pode ser atribuído exclusivamente por texto gerado.
- `DEFERRED`/`DECLINED` registram agência e não geram automaticamente punição moral ou perda de oportunidades gerais.
- `SUSPENDED` representa dependência indisponível, data incompatível ou interrupção legítima, permitindo retomada sem retcon.
- A semântica final dos estados deve ser definida nas SPECS, principalmente alternativas e conflitos entre propostas simultâneas.

## Dados candidatos

```yaml
arc_id: arc-id
campaign_id: campaign-id
mode: living_world
subject_character_id: character-instance-id
participant_character_ids: []
origin:
  backstory_revision_id: rev-123
  confirmed_event_ids: []
  world_fact_refs: []
  trusted_canon_sources: []
privacy:
  sharing_policy: restricted
  authorized_recipients: [subject_character_id]
  knowledge_provenance_refs: []
outline:
  narrative_premise: null
  player_defined_goal: null
  adaptable_paths: []
state: PROPOSED
milestones: []
prerequisites: []
optional_participation: true
window:
  earliest_world_time: null
  latest_world_time: null
  irreversible_when_unattended: false
risk: not_classified
rule_profile_version: pinned-by-campaign
event_version: 0
mechanical_receipt_ids: []
```

Campos, formato e valores são ilustrativos. Em particular, o campo `sharing_policy` exige contratos concretos de ACL; o exemplo não concede acesso automático a outro jogador.

## Pipeline de conteúdo candidato

1. **Observação por eventos:** consumir apenas mudanças relevantes do estado confirmado (histórico publicado, uma pista obtida, reputação alterada, passagem de tempo permitida, NPC presente ou rota disponível).
2. **Detecção de oportunidades:** regras priorizam ganchos plausíveis; sem LLM por tick.
3. **Construção do esqueleto:** selecionar template validado e preencher objetivos e dependências; LLM local pode sugerir variações sobre fatos permitidos.
4. **Validação cruzada:** canon (época, lugar, facção), conhecimento, existência de recurso, conflito com outras missões, política HIGH, balanceamento regional e limitações multiplayer.
5. **Oferta ao personagem:** apresentar oportunidades sem obrigar aceitação e sem quebrar o sigilo de seu passado perante outros participantes.
6. **Evolução em marcos:** objetivos têm precondições e evidências objetivas; caminhos alternativos podem atualizar etapas sem inventar sucessos.
7. **Fechamento transacional:** gateway e host confirmam efeitos mecânicos; World Memory registra evento e projeções, com idempotência e recuperação de `UNCERTAIN`.
8. **Reações:** reputação, alinhamento, notícias e facções processam somente efeitos confirmados e compatíveis com DEC-027/034.

## Exemplo completo: parente desaparecido

**Histórico:** um aventureiro sabe que seu pai desapareceu durante uma expedição. A pista de uma suposta organização secreta está marcada como **suspeita**, não fato.

- **Gancho:** um documento compatível com a época aponta uma expedição antiga. A pista pode ter sido obtida por contato autorizado ou encontrado pelos jogadores.
- **Investigação:** diferentes locais e NPCs podem corroborar ou contradizer a suspeita. A IA não determina previamente se o pai está vivo, morto ou transformado.
- **Escolhas:** negociar, investigar, confrontar ou adiar; o arco não força um combate nem obriga outros jogadores a revelar suas origens.
- **Consequências:** a história pode gerar novos aliados/inimigos e atualizar o conhecimento e a reputação local, mas somente após fatos confirmados. Uma ressurreição não será presumida pelo simples desejo da narrativa.
- **Persistência:** ao sair e reabrir o jogo, a versão da história, os fatos e o estado do arco continuam coerentes.

## Dependências e restrições

- **DEC-004/020:** históricos individuais e revisões não permitem apagar fatos testemunhados no jogo.
- **DEC-008/022:** estado+eventos e relógio híbrido; catch-up não executa arcos importantes irreversivelmente.
- **DEC-009/023/024/025/026:** ano-base 1369 DR apenas para primeiros testes, canon principal com divergências autorizadas, arcos clássicos independentes e intervenções opcionais.
- **DEC-010/005-E:** reuso de mapas e criaturas existentes; não gerar mapas ao vivo sem teste; encontros por regras regionais.
- **DEC-012/027/034:** comandos tipados e proteções de alto risco; nenhuma alteração mecânica por texto livre de LLM.
- **DEC-028/029/030:** filtro de conhecimento antes de contexto; rumores diferentes de fatos; efeitos sociais e percepção contextual.
- **DEC-035–038:** mudanças morais, redenção e poderes não ocorrem sem política, autorização e host; jornadas especiais são um subtipo de arco pessoal.
- **DEC-014/021:** orquestração híbrida, código primeiro, por tiers de atividade.

## Plano de testes candidatos

| ID | Caso | Resultado esperado |
|---|---|---|
| PSD-01 | Criar gancho a partir de histórico versionado | Proposta referencia versão e não inventa fatos |
| PSD-02 | Investigar suspeita falsa de conspiração | Informação continua suspeita até verificação |
| PSD-03 | Gerar dois caminhos para o mesmo gancho | Alternativas verificáveis e não predeterminadas |
| PSD-04 | Recusar missão pessoal | Sem sanção ou bloqueio geral artificial |
| PSD-05 | Adiar por múltiplas sessões | Estado e oportunidade coerentes com calendário |
| PSD-06 | Personagem ausente na sessão | Não mover sua escolha pessoal sem autorização |
| PSD-07 | NPC canônico já falecido naquela campanha | Rejeitar dependência ou adaptar lore validamente |
| PSD-08 | Dois arcos exigem o mesmo recurso indivisível | Detectar conflito antes da ativação |
| PSD-09 | NPC não autorizado recebe segredo | Contexto bloqueado antes do LLM |
| PSD-10 | Jogo fechado por dias, modo FROZEN | Nenhum marco avança pelo relógio externo |
| PSD-11 | Reabrir save após recompensa | Recompensa não duplicada |
| PSD-12 | Host responde `UNCERTAIN` | Quest aguarda reconciliação, não declara sucesso |
| PSD-13 | Jogador muda histórico editável | Eventos confirmados não sofrem retcon automático |
| PSD-14 | LLM indisponível | Diretor mantém estados e regras determinísticas |
| PSD-15 | Conteúdo requer mudança histórica HIGH | Requer autorização conforme DEC-034 |
| PSD-16 | O arco compete com missão clássica paralela | Preserva canon/flags e evita ativação incoerente |
| PSD-17 | Dois clientes multiplayer reabrem sessão | Mesma etapa confirmada e sem duplicação |
| PSD-18 | Iniciar modo Original | Nenhum arco personalizado injeta conteúdo |
| PSD-19 | Jogador encontra uma recompensa já recebida | Sem reaplicação mecânica ou registro duplo |
| PSD-20 | Quest pessoal promove ação compartilhada | Convites e acessos respeitam consentimento e conhecimento |

## Pendências (não decididas)

- Política de **equilíbrio de protagonismo, prioridade, cadência e coordenação de missões de jogadores** (DEC-040).
- Estruturas de templates, critérios quantitativos, esquema de versionamento, taxonomia de premissas, avaliações de qualidade narrativa e política de duplicação semântica.
- Recursos reais de UI e mecanismos de missões de BG2:EE/EEex; compatibilidade multiplayer; tempo/latência da IA local.
- Relação entre participação individual e coletiva quando segredos estão envolvidos; divulgação deve ser acordada pela política de conhecimento, não presumida.
- Capacidade de alterar NPC, área, triggers ou inventário em runtime — sujeita às POCs do motor, sem implementação garantida.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Mudança de crença NPC pode gerar candidato a missão, reconciliação, pedido de desculpas ou conflito pessoal, após evidência adquirida legitimamente e verificação DEC-064/C. Nenhum retcon de diálogo, segredos de PC ou arco já confirmado. Diretórios anuais canônicos DEC-060 e overlays de campanha permanecem distintos; consequências dependem de validação narrativa e mecânica.


### Âncoras de relacionamentos e promessas NPC — DEC-065/C (Discovery v6.1)

Arcos pessoais podem propor âncoras de promessas e marcos confirmados, vinculadas a episódios reais. Não declarar que um NPC testemunhou ou prometeu algo apenas porque um resumo narrativo o sugere. Proteção de memória não altera consentimento, recompensa, quests ou scripts do host. Revisões/segredos DEC-060–064 e privacidade continuam obrigatórias.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Um figurante pode ser promovido pela DEC-067 por marcos de história confirmados, mas diretor de narrativa não comprova identidade, não inventa biografia e não impõe missão ao grupo.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Contribuição e responsabilidade individual podem apoiar marcos pessoais quando validadas; a ausência de prova fica UNKNOWN e não é preenchida por dramaturgia da IA.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Arcos de espionagem, identidade oculta e descoberta só usam pistas com proveniência; informação do histórico secreto do jogador nunca vira conhecimento do NPC por proximidade, e revelação obedece consentimento e gates.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Histórias de denúncia, má-fé e fiscalização podem gerar oportunidades sem confissão ou participação de PC não consentida; fatos e suspeitas separados.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

NPC pode buscar proteção ou hesitar em denunciar, mas PC não terá confissão, testemunho ou decisão de exposição fabricada por PSD.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Ameaça e proteção podem alimentar história pessoal sem obrigar PCs a fugir/testemunhar e sem revelar segredo de background ou criar morte irreversível.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

História pessoal oculta e localização de fonte só entram em diálogos ou pistas se PC consentiu e observador obteve evidência legítima.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Operação de engano envolvendo segredo de histórico pessoal de PC exige autorização específica; IA não escreve traição, mentira ou confissão como escolha do jogador.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Conflitos entre objetivos de NPCs podem gerar propostas de diálogo/missão, mas não obrigar PC a trair seu grupo nem alterar retroativamente seu passado.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Ofertas e relações informais de PC podem render missões de investigação, mas a IA não assina por jogador nem força confissões ou compromissos.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Diretor de histórias pessoais só usa relatos acessíveis pelo ator no período; segredos de PCs não são revelados por rumor ou por parecer do host.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Segredos de histórias pessoais de PCs devem ser filtrados por autorização e destinatário. Dossiê de investigação não atribui passado inventado ou confissão ao titular.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Diretor de arcos pessoais pode sugerir planos, mas não escolher missões/objetivos no lugar de PC ou vazar segredos de histórico.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

O PSD só pode propor replanejamento de histórias pessoais após evento verificável; consentimento e autonomia do jogador não migram para outro arco.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Regras históricas DEC-096 candidatas podem filtrar oportunidades por época/region/venue; histórias privadas não se tornam NPC knowledge automaticamente.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Narrativas pessoais não podem substituir scripts/diálogos/romances sem capability e ownership comprovados.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Personal Story Director recebe somente marcos de quest liberados ao escopo e à audiência, sem spoilers.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **reputação**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para diretor narrativo recebe apenas contexto autorizado do destinatário, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para diretores narrativos com mínima view autorizada, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
