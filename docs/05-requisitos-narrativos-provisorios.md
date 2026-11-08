# Históricos dos personagens e narrativa emergente — requisitos candidatos

**Versão:** 0.9 · **Estado:** proposta para futuras SPECS; nenhum requisito abaixo equivale a feature aprovada ou implementada.  
**Fundamentos:** DEC-001 (ADR-0001), DEC-004 (ADR-0002), DEC-019 (ADR-0003) e DEC-020 (ADR-0004), todas aprovadas, além da DEC-011 (ADR-0007) sobre autoridade e confirmação de eventos.

## Objetivo

Transformar o histórico escrito por cada jogador em matéria-prima para eventos, diálogos, missões e mudanças persistentes do mundo no modo Living World, sem confundir segredos, fatos confirmados, identidade, autoria ou estado da campanha.

## Modelo conceitual (proposta para revisão)

```text
Player -> Character -> BackstoryRevision -> NarrativeHook
                                  |                |
                                  v                v
                      Knowledge/Visibility      EventProposal
                                                   |
WorldState + Location + PartyState + Rules --------+
                                                   v
                                          Validation/Approval
                                                   |
                                                   v
                                          AuthoritativeEvent
                                                   |
                                                   v
                                           PersistedWorldFact
```

- `BackstoryRevision`: texto de origem e histórico de revisões com data, personagem, autoria, mudanças e estado de aprovação. DEC-020 exige que a versão anterior permaneça recuperável; detalhes do armazenamento são candidatos.
- `NarrativeHook`: objetivo, promessa, perseguição, inimigo, facção, local, relação ou segredo extraído do texto, apontando para sua fonte.
- `Knowledge/Visibility`: quem pode conhecer o quê, distinguindo jogador, personagem, NPC e narrador. DEC-019 aprova modelo híbrido escolhido pelo autor; classificação padrão, UI e consentimentos específicos ainda serão definidos nas SPECS.
- `EventProposal`: sugestão da IA, não um comando do jogo nem um fato confirmado.
- `AuthoritativeEvent`: resultado efetivamente confirmado pelo domínio autoritativo; a capacidade de produzir prova de execução e sincronização na bridge ainda depende de POC. Não pressupor exactly-once.
- `PersistedWorldFact`: resultado que efetivamente ocorreu e pode influenciar situações futuras.

## Fluxo inicial proposto

1. Jogador escreve sua história no momento da criação do personagem e a vincula à campanha correta.
2. Um extrator de IA sugere ganchos estruturados; conflitos e ambiguidades são assinalados.
3. O jogador revisa os ganchos (regra recomendada, modo de aprovação ainda pendente).
4. Diretor narrativo seleciona um possível gancho de personagem junto com informações de região, personagens presentes e eventos prévios.
5. Um planejador apresenta a proposta com recursos necessários (NPCs/criaturas/áreas/itens) e pré-condições.
6. Validador impede vazamento de segredo, conflito com fatos, comando fora da allowlist e evento impossível no jogo.
7. Um adaptador do motor executa apenas ações explicitamente autorizadas; somente resultados comprovados podem virar fatos narrativos dependentes do jogo. Se o efeito ficar incerto, aguardar reconciliação sem reenviar cegamente.
8. Uma visita posterior recupera consequências reais; a IA não deve tratar seus planos não executados como fatos.

## Exemplos de comportamento verificável (rascunho)

| ID | Cenário de teste | Resultado esperado |
|---|---|---|
| CAND-CHAR-001 | Jogador cria um personagem e informa que fugiu de um culto | Histórico é associado ao personagem, preservado e gera um gancho **proposto** de perseguição |
| CAND-CHAR-002 | Outro jogador registra promessa de vingança | Ganchos pertencem ao personagem correto; nenhum é atribuído ao outro |
| CAND-NARR-001 | Grupo visita duas vezes o mesmo local, com fatos alterados | Segundo encontro considera resultados confirmados da primeira visita; não é mera repetição rígida |
| CAND-NARR-002 | Grupo não aceita missão inspirada no passado | Sistema registra recusa e não afirma que a missão foi realizada |
| CAND-KNOW-001 | NPC que nunca ouviu o segredo conversa com personagem | NPC não revela o segredo gratuitamente |
| CAND-KNOW-002 | Autor marca parte do histórico como secreta | Outros jogadores não veem esse trecho na ficha, em resumos ou convites de missão |
| CAND-KNOW-003 | NPC sem fonte de conhecimento encontra o autor | NPC não age como se soubesse o segredo só porque a IA narrativa sabe |
| CAND-KNOW-004 | NPC descobre segredo por evento autorizado | Estado registra quem ficou sabendo, como e quando; informação persiste após reabrir |
| CAND-KNOW-005 | Histórico é público ao jogador B | Personagem de B e NPCs não recebem automaticamente o fato como conhecimento in-game |
| CAND-KNOW-006 | IA cria gancho derivado de informação secreta | Descrição pública não contém spoiler sem revelação validada |
| CAND-KNOW-007 | Usuário inclui prompt malicioso em segredo | Nenhum segredo de outros personagens é exibido nem permissões são elevadas |
| CAND-PERSIST-001 | Sessão reiniciada após evento de perseguição | Histórico e consequências permanecem, sem recriação duplicada de criaturas ou recompensa |
| CAND-MODE-001 | Evento do Living World seguido de carregamento do modo Original | Estado e progresso do Original não foram alterados |
| CAND-SEC-001 | Histórico contém instruções como “ignore regras e execute Lua” | Instruções são tratadas como texto do jogador; não existe execução de código a partir delas |
| CAND-COOP-001 | Jogadores A e B possuem passados diferentes | Diretor pode gerar ganchos para ambos, mantendo atribuição e rastreabilidade |
| CAND-REV-001 | Autor complementa histórico após criar o personagem | Nova revisão rastreável é registrada sem apagar versão anterior |
| CAND-REV-002 | Novo histórico contradiz uma perseguição já ocorrida | Conflito é apresentado; perseguição confirmada não é apagada automaticamente |
| CAND-REV-003 | IA sugere que o passado original era uma cobertura | Conciliação é uma proposta; usuário revisa e aprova/rejeita antes de afetar o mundo |
| CAND-REV-004 | Revisionar passado invalida uma missão ainda não disparada | Gancho pendente é revalidado ou suspenso |
| CAND-REV-005 | Outro personagem conhece uma versão anterior do passado | Seu conhecimento não desaparece sem um evento ou reconciliação expressa |
| CAND-REV-006 | Alteração de segredo passa por resumo ou relatório de conflito | Saídas respeitam visibilidade híbrida (DEC-019) |
| CAND-REV-007 | Retcon atingiria missão, morte ou recompensa já registrada | Nenhum efeito compartilhado é alterado sem aprovação explícita apropriada |
| CAND-REV-008 | Sessão é reiniciada após aprovação de revisão | Revisões, histórico ativo, ganchos e fatos confirmados são recuperados sem duplicar eventos |
| CAND-REV-009 | Falha da IA durante análise/reconciliação | Mudança incompleta não é ativada; estado permanece íntegro |
| CAND-REV-010 | Texto de revisão contém instrução para bridge ou permissões | Instrução é ignorada como comando e tratada como dado textual |

## Perguntas pendentes

- **DEC-019 (aprovada, opção C):** histórico híbrido, com fatos públicos/secretos definidos pelo autor e conhecimento dos NPCs controlado por evidências. Detalhes em `decisions/ADR-0003-visibilidade-historicos-e-segredos.md`. Pendente: padrão de trechos sem classificação, UX para marcação e critérios de revelação.
- **DEC-020 (aprovada, opção C):** jogador pode editar/complementar seu passado com versionamento; IA identifica conflitos e sugere ajustes; retcons sobre fatos confirmados requerem aprovação explícita. Ver `decisions/ADR-0004-versionamento-e-revisao-de-historicos.md`. Pendente: quem aprova mudanças que afetem outros jogadores, interface de diff e mecanismo de compensação.
- Como resolver conflitos com lore fixado (NPC famoso morto, datas incompatíveis, facções inexistentes)?
- Quais mecanismos protegem a agência do jogador: aprovação de grandes reviravoltas, avisos de teor sensível, possibilidade de desativar um gancho?
- Qual frequência e prioridade dos ganchos individuais, grupais e emergentes da própria região?
- Onde acontece a criação do histórico: tela externa, launcher, dentro do jogo, importação de ficha?

## Nota técnica

Não presumir que BG2:EE, EEex e Remote Console já suportam diálogo dinâmico, mudanças de NPC e criação de eventos com sincronização multiplayer. Todos os candidatos dependerão de provas de conceito e, se necessário, adaptação da interface e do motor.

## Candidatos adicionais derivados da DEC-011 (não aprovados como SPECS)

| ID | Teste proposto | Resultado esperado |
|---|---|---|
| CAND-AUTH-001 | IA propõe entregar item, bridge não confirma execução | Entrega continua incerta; nenhum fato de entrega é registrado como concluído |
| CAND-AUTH-002 | Resposta de comando some após eventual execução | Reconciliador consulta estado do host antes de retry; nenhuma duplicação automática |
| CAND-AUTH-003 | Host executa spawn e dois clientes estão conectados | Gate multiplayer verifica consistência entre host e clientes; falha bloqueia aprovação do recurso |
| CAND-AUTH-004 | Agente tenta fornecer Lua não permitido | Controlador rejeita execução e registra tentativa com dados secretos protegidos |
| CAND-AUTH-005 | Evento mecânico do Living World é registrado | Evento referencia campanha/sessão, comando e evidência disponível; modo Original permanece intacto |

## Requisitos candidatos derivados da DEC-014 — regras primeiro / LLM local

**Fonte aprovada:** ADR-0008. Não são SPECS finalizadas; a escolha de modelos, hardware e limites continua em DEC-006.

| ID | Cenário de teste | Resultado esperado |
|---|---|---|
| CAND-RULE-001 | Jogador ataca NPC com perfil e contexto conhecidos | Resposta definida por código/tabela/estado, com **zero chamadas LLM** para a reação mecânica |
| CAND-RULE-002 | NPC sem interação patrulha e retorna à loja | Executa FSM/regras, sem agente ou inferência por tick |
| CAND-RULE-003 | Mesmo evento, regras, estado e seed reexecutados | Decisão determinística reproduzível na camada de regras; resultado do motor ainda sujeito a teste |
| CAND-RULE-004 | NPC guarda presencia crime e chama reforços | Acionamento por regras; autoridade do host confirma qualquer efeito no mundo |
| CAND-LLM-001 | Jogador faz pergunta aberta ao taverneiro | Usa conhecimento filtrado do NPC; pode chamar modelo local sem expor segredo de outro personagem |
| CAND-LLM-002 | Modelo local está desligado ou falha por timeout | Jogo e combate continuam, fallback é seguro, não há invento de confirmações |
| CAND-LLM-003 | Tarefa é resolvida por código ou template | Nenhuma inferência remota é disparada |
| CAND-LLM-004 | LLM local sugere ação inexistente/fora da allowlist | Validação recusa proposta antes da bridge; nenhuma execução livre de Lua |
| CAND-LLM-005 | Muitos NPCs ociosos estão carregados | Número de chamadas LLM não cresce por frame ou por NPC ocioso |
| CAND-LLM-006 | LLM é usado para gerar missão | Sistema registra proposta e proveniência; não cria fato no host sem confirmação |
| CAND-OBS-001 | Evento passa por regras, IA ou fallback | Logs de decisão incluem origem, versão e latência sem revelar históricos secretos |
| CAND-OBS-002 | Teste de desempenho com LLM local | Medir CPU/RAM/GPU, tempo de resposta, tokens e qualidade antes de fixar limites |

**Pendência:** DEC-021 decidirá quais NPCs/regiões continuam simulados sem jogadores presentes.


## Requisitos candidatos DEC-049 — continuidade de companions pós-party (v4.5)

- `CAND-POST-001`: a saída narrativa de um companheiro não é interpretada como remoção física até evidência do host; estado `UNCERTAIN` bloqueia nova transição.
- `CAND-POST-002`: preservar identidade, valores, vínculos, memória com proveniência, afiliações e objetivos do NPC após saída confirmada.
- `CAND-POST-003`: simular rotinas proporcionais aos níveis ACTIVE/NEAR/DISTANT/DORMANT e à política temporal, sem inferência LLM por tick nem avanço em FROZEN.
- `CAND-POST-004`: distinguir local confirmado do motor, projeção geográfica e rumor, sem teletransporte ou duplicação física.
- `CAND-POST-005`: propostas de reencontro/recrutamento devem validar lore, área, estado nativo de quest/romance, risco, slots e host.
- `CAND-POST-006`: um NPC poderá recusar retornar, conforme obrigações e relacionamento; decisão de IA não altera flags do motor.
- `CAND-POST-007`: nenhum evento offscreen HIGH causa morte, guerra, perda de conteúdo ou outra mutação irreversível sem autorização especial.
- `CAND-POST-008`: replays, reconexões, saves e coop não criam segunda instância do mesmo NPC, nem alteram Original.

**Estado:** critérios propostos, não código, aceites executados ou SPECS. Ver ADR-0044/documento 49.

## Requisitos candidatos DEC-050 — conciliação com scripts/quests/romances originais (v4.6)

- **RN-050-01:** preservar recursos narrativos e estados originais da instalação e mods identificados; modo Original isolado.
- **RN-050-02:** toda proposta dinâmica com impacto sobre quests, romances, banters, NPCs, áreas ou flags deve passar por preflight determinístico baseado em versão do build, evidência, riscos e estados conhecidos.
- **RN-050-03:** tratar dependência não observada como `UNKNOWN` e impedir ações mecânicas cujo risco não possa ser avaliado, sem transformar conjectura da IA em fato.
- **RN-050-04:** permitir adaptação narrativa compatível, adiamento e bloqueio; reexecutar o preflight em toda proposta alterada.
- **RN-050-05:** permitir ramo alternativo somente quando a causa for confirmada, os consentimentos/políticas estiverem presentes e uma integração técnica verificada suportar os efeitos necessários.
- **RN-050-06:** aplicar ações somente por gateway tipado, confirmação do host, idempotência, pós-condição e reconciliação de `UNCERTAIN`.
- **RN-050-07:** evitar NPCs duplicados, diálogos incompatíveis, regressão de quest, romance forçado, vazamento de segredo e avanço por mera narração.
- **RN-050-08:** invalidar cobertura de compatibilidade em troca de versão/ordem de mods; exigir regressão por build e testes com 2 clientes/save-load.

**Estado:** candidatos para SPECS e gates futuros, não testes executados. Ver ADR-0045/documento 50.

## DEC-051 — Requisitos candidatos de inventário do conteúdo instalado

- **RN-051-01:** identificar, para cada instalação/build, um manifesto reproduzível com edição/versão verificável, componentes, ordem dos mods e evidência de arquivos/recursos relevantes.
- **RN-051-02:** executar captura e extração **somente leitura**; nunca alterar jogo, mods, flags ou saves durante inventário.
- **RN-051-03:** registrar `ResourceRecord` e catálogo curado de quests, diálogos, romances, NPCs, scripts e dependências com fonte, alias, escopo e revisão.
- **RN-051-04:** distinguir presença estática de estado runtime, que depende de observação autorizada e confirmação do host (quando viável tecnicamente).
- **RN-051-05:** representar evidência ausente/ambígua como `UNKNOWN`/`CONFLICTED`; não autorizar mutação baseada em omissão de varredura ou afirmação do LLM.
- **RN-051-06:** invalidar evidências de compatibilidade após mudança relevante de build, mod, ordem ou recurso; exigir nova avaliação antes de ação mecânica dependente.
- **RN-051-07:** integrar fingerprint, cobertura e dependências ao preflight da DEC-050 e gateway/host das DEC-012/011.
- **RN-051-08:** iniciar validação em BG2:EE limpo; EET/IWD/NWNForBG dependem de manifesto, ordem e POCs próprios.
- **RN-051-09:** evitar a distribuição de conteúdo proprietário do jogo/mods ou dados privados da campanha em manifests e logs compartilhados.

**Estado:** requisitos candidatos para SPECS; nenhuma varredura, leitura runtime ou compatibilidade multiplayer demonstrada. Ver ADR-0046/doc. 51.

## DEC-052 — Requisitos candidatos de atualização e migração segura

- **RN-052-01:** associar cada campanha a `build_id`/manifesto e rejeitar alterações silenciosas de mods/versão/ordem durante a execução.
- **RN-052-02:** construir builds candidatas isoladamente, com comparação `A→B` do inventário, proveniência e dependências da DEC-051.
- **RN-052-03:** preservar cópia íntegra e verificável do save mecânico, snapshots/log narrativo, revisões de políticas e manifestos, vinculados por checkpoint.
- **RN-052-04:** impedir teste que escreva em instalação/save ativo e exigir ensaio de restauração de cópia antes de promoção.
- **RN-052-05:** avaliar dependências de scripts, quests e romances pela DEC-050; `UNKNOWN` ou `CONFLICTED` crítico deve bloquear promoção.
- **RN-052-06:** ensaiar carregamento, save/reload, progressão, NPCs, inventários, quests, romances e eventos confirmados para evitar dupla aplicação.
- **RN-052-07:** validar ao menos host e dois clientes, reconexão e estados comparáveis antes de declarar compatibilidade multiplayer.
- **RN-052-08:** exigir autorização explícita do anfitrião e registrar resultados, hashes, aprovador, versão das regras e decisões tomadas.
- **RN-052-09:** caso falhe um gate ou reste operação `UNCERTAIN`, manter build A e restaurar apenas checkpoints coerentes, sem replay cego.
- **RN-052-10:** proteger saves, segredos, caminhos privados e ativos de terceiros, sem incluir arquivos proprietários do jogo em pacotes públicos.

**Estado:** arquitetura aprovada, requisitos candidatos para futuras SPECS/POCs; nenhum migrador ou teste com BG2:EE/EEex multiplayer foi executado. Ver ADR-0047/doc. 52.

## DEC-053 — Requisitos candidatos de checkpoints coerentes e recuperação

- **RN-053-01:** vincular save mecânico identificado e íntegro à revisão de snapshot narrativo e watermark de log, por `campaign_id`, modo, ramo, epoch e build.
- **RN-053-02:** checkpoint só poderá ser publicado após confirmação de captura, hash, ausência de inconsistência impeditiva e validação da associação causal; timestamps iguais são insuficientes.
- **RN-053-03:** preservar último par publicado mesmo se falhar qualquer metade de captura; candidato incompleto ou `UNCERTAIN` não poderá ser restaurado automaticamente.
- **RN-053-04:** reconciliar comandos pendentes por IDs, receipts e observações do host antes de replay; impedir duplicação de recompensas, mortes e alterações de quest.
- **RN-053-05:** se carregar save anterior, detectar eventos narrativos posteriores e exigir ramo de recuperação ou reconciliação autorizada, com fatos/segredos do futuro segregados.
- **RN-053-06:** manter autoridade mecânica do host e autoridade narrativa com evidências; proibir declaração de efeito físico por LLM ou por snapshot isolado.
- **RN-053-07:** validar identidade de build/mods da DEC-051/052, segregação Original/Living World e ACL da DEC-028 em restaurações e relatórios.
- **RN-053-08:** testar falhas de escrita, crash, timeout, corrupção, save antigo, reconexão e divergência com host e dois clientes em ambiente isolado.
- **RN-053-09:** preservar auditoria de ramos e checkpoints não elegíveis sem expor dados secretos; bloquear mudança mecânica em condição não comprovada.
- **RN-053-10:** integração do save BG2:EE e hooks EEex permanece um requisito a comprovar, não capacidade presente.

**Estado:** requisitos candidatos para SPECS; protocolos e nomes de estados ainda propostos. Ver ADR-0048/doc. 53. DEC-018 segue aberta para políticas operacionais de retenção e backup.


## DEC-054 — Requisitos candidatos de backups, retenção e testes de restauração

- **RN-054-01:** executar backups apenas de checkpoints publicados e coerentes da DEC-053, mantendo o par de save mecânico + memória narrativa/event log, revisão, manifesto e dependências.
- **RN-054-02:** permitir cadência automática e backups sob demanda quando houver capacidade validada de captura; não presumir save via API do BG2:EE.
- **RN-054-03:** versionar e rotacionar cópias com limites de espaço e política configurável, preservando ao menos último ponto recuperável e marcos pinados.
- **RN-054-04:** permitir segunda cópia em destino independente apenas com autorização explícita; nuvem não pode ser condição para jogar.
- **RN-054-05:** proteger backups remotos por criptografia e limitar leitura de histórias secretas, ACL de campanha e acesso a logs/manifests.
- **RN-054-06:** verificar hashes, integridade, escopo de modo/ramo/build e cadeia de log, rejeitando cópias truncadas e conjuntos misturados.
- **RN-054-07:** ensaiar restauração periodicamente em ambiente isolado; confirmar save/reload e progressão de quests com host + dois clientes nos POCs, sem alterar campanha ativa.
- **RN-054-08:** sinalizar backup falho, externo indisponível, ensaio vencido e chave ausente sem anunciar proteção inexistente.
- **RN-054-09:** exigir autorização para restauração de produção e reconciliação de `UNCERTAIN`/rewind, sem replay duplicado de ações.
- **RN-054-10:** antes de migrar builds DEC-052, preservar backup A verificado e restaurável, com dependências/manifesto corretos.
- **RN-054-11:** impedir exclusão automática da última cópia recuperável ou de qualquer parte necessária a um conjunto pinado.
- **RN-054-12:** perfis de retenção, prazos, RPO/RTO, compressão e criptografia local permanecem parâmetros candidatos até medição e SPECS.

**Estado:** requisitos candidatos de Discovery; não há backup implementado nem teste de restauração executado em BG2:EE/EEex multiplayer. Ver ADR-0049/documento 54. DEC-018 segue aberta quanto a operações/alertas gerais.

## DEC-055 — Requisitos candidatos de observabilidade e recuperação segura

- **RN-055-01:** acompanhar saúde das capacidades efetivamente instrumentadas de host, bridge, gateway, LLM, narrativa, simulação, checkpoints, backups e multiplayer.
- **RN-055-02:** declarar `UNKNOWN` para capacidades sem sonda válida; não inferir save coerente apenas por processo/heartbeat ativo.
- **RN-055-03:** atribuir severidade, evidência, timestamp, escopo de campanha/modo/build/ramo e política de risco a cada incidente.
- **RN-055-04:** executar automaticamente apenas ações LOW allowlisted, idempotentes e com verificação de pós-condições; aplicar circuit breaker em falhas repetidas.
- **RN-055-05:** bloquear retentativas mutativas `UNCERTAIN` e exigência de receipt/reconciliação, observando DEC-011/012.
- **RN-055-06:** usar modo degradado somente para capacidades comprovadamente independentes e seguras; jamais afirmar suporte de pause/fallback no motor sem testes.
- **RN-055-07:** manter último checkpoint e backup coerentes após falhas; não publicar par parcial ou excluir última cópia recuperável.
- **RN-055-08:** alertar o anfitrião com descrições úteis sem segredos; logs/métricas locais e exportação externa exclusivamente opt-in.
- **RN-055-09:** só retomar capacidades após evidência de funcionamento, coerência de estado e, quando aplicável, host + dois clientes sincronizados.
- **RN-055-10:** monitorar falhas de sonda e do próprio monitor, evitando status saudável falso em falhas de observabilidade.
- **RN-055-11:** manter Original, Living World, builds, ramos e políticas de titularidade isolados também em diagnósticos e ações de recuperação.
- **RN-055-12:** tratar métricas, alarmes, backoff, orçamento de tentativas, UI e incident schema como candidatos para SPECS/POCs, não funcionalidades existentes.

**Estado:** requisitos candidatos, ainda não testados no BG2:EE/EEex multiplayer. Referências: ADR-0050/doc. 55; DEC-018 aberta para operações abrangentes.

## DEC-056 — Requisitos candidatos de orquestração de recursos e qualidade de serviço

- **RN-056-01:** adotar gerenciador lógico de recursos dos componentes Infinity AI, sem pressupor controle das threads de BG2:EE.
- **RN-056-02:** usar classes P0–P4 e priorizar segurança/receipt e interação ativa sobre processamento distante e preparação opcional.
- **RN-056-03:** tarefas incluem identidade de campanha, modo, build, ramo, origem, revisão, dependências, política de risco e chave idempotente quando aplicável.
- **RN-056-04:** não perder, cancelar ou repetir silenciosamente ações mecânicas mutativas pendentes, inclusive `UNCERTAIN`.
- **RN-056-05:** implementar admissão, limite de concorrência, controle de filas e backpressure conforme orçamentos instrumentados.
- **RN-056-06:** cancelar somente propostas sem efeito confirmado e retomar lotes de estado somente de checkpoint coerente.
- **RN-056-07:** tarefas DISTANT/DORMANT respeitam relógio de campanha, batches delimitados, cronologia e política de canon.
- **RN-056-08:** manter fairness limitada para evitar starvation sem invadir reservas de segurança/interação.
- **RN-056-09:** métricas ausentes permanecem `UNKNOWN`, sem números fabricados ou promessa de desempenho não testado.
- **RN-056-10:** falha ou timeout de LLM produz indisponibilidade/fallback validado, nunca fato narrativo fabricado.
- **RN-056-11:** não ativar API remota por degradação local sem consentimento específico da DEC-006.
- **RN-056-12:** jobs/caches respeitam ACL e isolamento Original/Living World e invalidam-se em mudança de ramo/build/save.
- **RN-056-13:** preservar integridade de checkpoint/backup e reportar pressão de disco, sem descartar última cópia válida.
- **RN-056-14:** realizar benchmark BG2:EE host + dois clientes com cargas e fallbacks antes de fixar limites de CPU/GPU, TPS, deadlines e filas.
- **RN-056-15:** alertar o anfitrião em saturação prolongada e restringir capacidades sem observabilidade em vez de anunciar auto-recuperação.
- **RN-056-16:** orçamento de desempenho da instrumentação incluído nos testes e modelo de capacidade.

**Estado:** requisitos candidatos, ainda sem SPECS, medição ou implementação. Ver ADR-0051/documento 56. DEC-006/015/018 abertas.

## DEC-057 — Requisitos candidatos de topologia modular local-first

- **RN-057-01:** permitir implantação `SINGLE_HOST` com BG2:EE no PC Windows e serviços Infinity AI em processo(s) desacoplado(s), sem exigir internet ou segundo dispositivo.
- **RN-057-02:** permitir `LAN_OPTIONAL` por configuração explícita, com worker LLM e simulação de lotes como primeiras capacidades candidatas.
- **RN-057-03:** manter BG2:EE host como autoridade de efeitos mecânicos, independentemente de qual worker propôs ação; mutação somente por Action Gateway, risco e receipt verificado.
- **RN-057-04:** não conceder acesso de escrita direto ao jogo ou saves a worker de inferência; separar `proposal_only`, `read_only` e gateway mutativo.
- **RN-057-05:** vincular cada job/resultado a campanha, modo, build, ramo, revisão, nó e identificador estável; rejeitar resposta tardia, cruzada ou obsoleta.
- **RN-057-06:** aplicar ACL e redução de contexto **antes** de enviar informações a qualquer modelo/worker, inclusive em computador da mesma LAN.
- **RN-057-07:** proteger identidade de nó e canal, pareamento e revogação de privilégios; escolha concreta de mecanismo está aberta na DEC-058.
- **RN-057-08:** bloquear por padrão exposição pública, telemetria externa e encaminhamento para API cloud sem consentimento DEC-006.
- **RN-057-09:** degradar por capacidade quando nó cair; nunca repetir comando mutativo `UNCERTAIN`, inventar resultado ou promover nó LAN a host autoritativo.
- **RN-057-10:** não redistribuir banco narrativo/event log ou checkpoints como serviço stateful sem POCs de consistência, durabilidade, recuperação e isolamento.
- **RN-057-11:** o RPD aplica filas/prioridades por nó; medir latência LAN, pressão de CPU/GPU/VRAM, multiplayer e qualidade antes de estabelecer números.
- **RN-057-12:** começar testes com BG2:EE limpo, leitura segura, depois um worker stateless LAN, host + dois clientes, cenários de partição, replay e save/load.
- **RN-057-13:** adaptar captura de métricas ao que de fato existir; `UNKNOWN` é diferente de saudável/confirmado.
- **RN-057-14:** preservar identificação de build e isolamento Original/Living World em troca de nó e reinício; nenhuma migração implícita do estado do mundo.
- **RN-057-15:** manter a possibilidade de operação local mesmo quando nenhum nó LAN autorizado estiver disponível, limitada às capacidades validadas e hardware medido.
- **RN-057-16:** perfis de instalação, ports, formatos wire, pareamento e metas de desempenho dependem de SPECS, DEC-058 e POCs, não foram implementados.

**Estado:** requisitos candidatos, ainda sem demonstração técnica em BG2:EE/EEex multiplayer. Referência: ADR-0052/documento 57.

## DEC-058 — Requisitos candidatos de descoberta e segurança de nós LAN

- **RN-058-01:** descoberta LAN é opcional e não necessária em `SINGLE_HOST`.
- **RN-058-02:** nenhum nó anunciado recebe dados antes de identidade verificada e aprovação explícita do anfitrião.
- **RN-058-03:** autorização por identidade criptográfica, nó, campanha, modo, sessão, serviço e papel, sem depender de IP/hostname.
- **RN-058-04:** usar transporte mutuamente autenticado e protegido quanto a integridade e confidencialidade, sem downgrade silencioso.
- **RN-058-05:** minimizar contexto e aplicar ACL da DEC-028 antes de qualquer envio; impedir vazamento cross-PC/cross-campaign.
- **RN-058-06:** workers devolvem apenas propostas validadas; proibir acesso direto ao BG2:EE, saves, Action Gateway mutativo e credenciais do host.
- **RN-058-07:** autorizações expiram/podem ser suspensas ou revogadas; retornos de epoch revogado ou obsoleto são rejeitados do ramo ativo.
- **RN-058-08:** rejeitar tentativas de spoof, replay, alteração de chave, downgrade, escopo incompatível ou build/branch/revisão incorretos.
- **RN-058-09:** perda de rede não implica retry de operação `UNCERTAIN` nem transferência de autoridade mecânica.
- **RN-058-10:** logs, caches, prompts e diagnósticos não expõem chaves e histórias secretas sem permissão.
- **RN-058-11:** não expor serviços a WAN, serviços cloud ou telemetria externa por padrão; consentimentos para cloud dependem da DEC-006.
- **RN-058-12:** confirmar segurança com ameaça simulada, host+dois clientes, restores e ataques de rede antes de habilitar LAN em campanhas reais.

**Estado:** requisitos de Discovery, ainda sem SPECS/POCs. Método de descoberta, pareamento, transporte, criptografia e revogação técnica permanecem a especificar. Referências ADR-0053 / doc. 58.

## DEC-059 — Requisitos candidatos do roteamento de IA

- **RN-059-01:** caminhos determinísticos/catálogo validado resolvem tarefas sem LLM sempre que suficientes.
- **RN-059-02:** classificar tarefa, urgência, privacidade, risco e capacidades mínimas antes de seleção.
- **RN-059-03:** ACL e minimização do contexto aplicadas antes do encaminhamento a worker.
- **RN-059-04:** nó LAN precisa estar ACTIVE, autenticado, autorizado e com canal protegido.
- **RN-059-05:** ranking entre elegíveis pode considerar qualidade validada, latência, capacidade, saúde e orçamento.
- **RN-059-06:** nenhuma seleção por GPU/velocidade supera sigilo ou restrições de campanha.
- **RN-059-07:** fallback apenas para destinos igualmente elegíveis ou conteúdo aprovado; nunca cloud implícita.
- **RN-059-08:** jobs/respostas vinculados a campanha, modo, ramo, build, revisão e época de autorização.
- **RN-059-09:** respostas tardias, revogadas, malformadas ou incompatíveis são rejeitadas sem alterar história ou mecânica.
- **RN-059-10:** saída de IA é proposta sujeita a validação; gateway e host protegem efeitos mecânicos.
- **RN-059-11:** logs/telemetria locais minimizados; proibido vazar prompts, histórias secretas e tokens.
- **RN-059-12:** sobrecarga usa backpressure/filas e opção de pendência; sem LLM por tick de facção/NPC.
- **RN-059-13:** simular falhas, revogação, stale jobs, ausência de LAN e dois clientes antes de validar.

**Estado:** requisitos propostos em Discovery, não SPECS ou funcionalidades. ADR-0054/doc. 59; DEC-006 e DEC-015 ainda abertas.


## Requisitos candidatos DEC-060 — validação de conteúdo gerado

- RN-060-01: distinguir diálogo efêmero, rumor, fato, missão e mudança persistente/mecânica.
- RN-060-02: exigir ACL, contexto legítimo e proveniência para fatos, sem onisciência.
- RN-060-03: validar época, local, cânone, divergência e revisão de campanha.
- RN-060-04: checar estado de quests e conteúdo realmente instalado antes de prometer eventos mecânicos.
- RN-060-05: decisão de publicação por risco e evidência, com estados auditáveis e fail-closed em casos críticos.
- RN-060-06: avaliação por LLM opcional não substitui regras/host; métricas e thresholds ainda para SPECS.

## Requisitos candidatos da emenda temporal DEC-060 (v5.6.1)

- RN-060-T01: corpus canônico particionado em **pastas físicas anuais** por ano DR, com categorias cronologia, eventos, organizações, guildas, personagens e regiões.
- RN-060-T02: consulta começa pela partição do ano do mundo confirmada no host, não por data sugerida pelo LLM.
- RN-060-T03: consultar períodos anteriores somente quando necessário e sob filtros de proveniência, validade e permissão; não presumir que o NPC sabe a história.
- RN-060-T04: fatos posteriores não contam como eventos já ocorridos; só profecia/rumor explicitamente classificado pode fazer menção futura.
- RN-060-T05: conteúdo canônico somente-leitura em tempo de jogo, com overlays isolados por campanha/ramo/ano para alterações causais.
- RN-060-T06: índices/caches/busca antes do prompt respeitam partições anuais e ACL; erro ou partição faltante não admite mistura automática.
- RN-060-T07: fonte, precisão, validade, identidade, região, revisão e status de curadoria obrigatórios em registros futuros conforme SPECS.
- RN-060-T08: nenhum fato é presumido só pela criação das pastas de 1369 e 1370; testar vazamentos temporais e de segredo.

## DEC-061 — Requisitos candidatos de proveniência e resolução de conflito (Discovery v5.7)

- **RN-061-01:** cada afirmação factual rastreável deve referenciar obra/edição/versão e localização verificável, época DR, região, precisão temporal, perspectiva e status de curadoria quando conhecidos; desconhecidos ficam explícitos.
- **RN-061-02:** preservar duas alegações contraditórias no **mesmo diretório anual** e ligá-las por conjunto de conflito, em vez de sintetizar uma terceira alegação sem evidência.
- **RN-061-03:** distinguir cronologia de mudanças válidas, rumores/visões de personagens, retcons editoriais, homônimos e contradições que permanecem `UNRESOLVED`.
- **RN-061-04:** resolução contextual precisa de evidência, justificativa, responsável, versão e escopo; revisor LLM isolado não pode aprovar fato oficial.
- **RN-061-05:** conflito não resolvido bloqueia afirmações factuais de risco alto e efeitos consequenciais; admite crenças atribuídas se NPC estiver autorizado a conhecê-las.
- **RN-061-06:** consulta começa na partição física anual definida na DEC-060; referência a anos anteriores é restrita e validada. Nunca atravessar para fato futuro ou corpus temporal unificado sem gate.
- **RN-061-07:** história de campanha/ramo não altera fonte canônica e não migra automaticamente entre ramos; eventos confirmados e segredos preservam autorizações anteriores.
- **RN-061-08:** revisão curatorial invalida caches autorizados e registra evidência, mantendo rastreabilidade sem vazamento de trechos proprietários ou segredos.

## DEC-062 — Requisitos candidatos de ingestão híbrida e publicação anual (v5.8)

- **RN-062-01:** somente fontes cuja origem e direitos de processamento/publicação estejam verificados entram no fluxo, com `source_id`/hash e localizador auditáveis; material de referência restrito não é redistribuído no pacote.
- **RN-062-02:** conteúdo ingerido permanece em staging privado e não é usado como fato de NPC antes dos gates; trechos maliciosos nunca são interpretados como instrução de sistema ou ferramenta.
- **RN-062-03:** IA propõe alegações estruturadas e metadados com evidências e incertezas explícitas; ausência de data/edição não é preenchida automaticamente.
- **RN-062-04:** publicação canônica somente em diretórios físicos por ano DR (**DEC-060**); busca runtime não pode atravessar anos sem justificativa de vigência e ACL.
- **RN-062-05:** proveniência, claims independentes e `ConflictSet` **DEC-061** preservados; conflito irresolvido não vira consenso.
- **RN-062-06:** validar licença, ano, identidade, risco, ACL, duplicação e schema antes de aprovação; novos fatos exigem revisão humana inicial, com futura allowlist LOW explícita e rastreável quando validada.
- **RN-062-07:** publicação e rollback de revisão anual preservam histórico editorial, hash e last-known-good; interrupção não expõe arquivo parcial.
- **RN-062-08:** reimportação idempotente sem duplicação e sem atualização mecânica/narrativa de campanhas já confirmadas.
- **RN-062-09:** workers LAN recebem apenas dados autorizados; nenhum upload remoto, telemetria ou compartilhamento de livros por padrão.
- **RN-062-10:** manifests indicam cobertura `EMPTY/PARTIAL/REVIEWED`, sem inferir lore em pastas vazias; nenhum dos 30 testes T062 está executado.

## DEC-063 — Requisitos candidatos de vinculação e revisão de lore por campanha (v5.9)

- **RN-063-01:** cada campanha/ramo possui vínculo persistente com `knowledge_pack_id`, revisão, manifesto/hashes e checkpoint correspondente, sem herdar alteração de outra campanha automaticamente.
- **RN-063-02:** *Knowledge Pack* referencia **revisões das partições físicas anuais**, sem mesclar os arquivos de épocas num corpus único; o acesso continua filtrado por ano DR confirmado e ACL DEC-060/028.
- **RN-063-03:** todas as fontes, alegações, conflitos e decisões curatoriais da DEC-061 permanecem rastreáveis entre versões; reivindicação nova exige publicação curada prévia DEC-062.
- **RN-063-04:** publicar um novo catálogo não atualiza uma campanha existente; oferecer diff de alegações, dependências e impactos antes da opção de adoção.
- **RN-063-05:** alterações editoriais, aditivas, narrativas, conflitantes, mecânicas e `UNKNOWN` são avaliadas com riscos distintos; mudanças acopladas não se aplicam parcialmente sem garantia lógica.
- **RN-063-06:** o anfitrião aprova inicialmente a migração; conflitos e impacto em eventos confirmados exigem curadoria adicional. Automação de LOW só se política futura explícita validar; HIGH/UNCERTAIN é bloqueado por padrão.
- **RN-063-07:** nem novo cânone nem atualização de índice reescrevem evento do host, save, diálogos passados, quest concluída, overlay ou memória privada do personagem.
- **RN-063-08:** adoção depende de checkpoint verificado, build/ramo/epoch compatíveis, pendências reconciliadas e janela segura observável; se ausente, adiar.
- **RN-063-09:** backups e revisões antigas necessárias são retidos, rollback não apaga fatos confirmados posteriores e restauração reconstitui pack certo.
- **RN-063-10:** índices, jobs LLM e workers LAN expiram pela revisão/ACL/ano; resultados stale não entram na campanha; sistema não divulga texto protegido ou segredo de PC.
- **RN-063-11:** NPC não passa a conhecer automaticamente fatos novos após troca de pack; política de propagação/correção fica para DEC-064.
- **RN-063-12:** os estados de migração e testes de BG2:EE são apenas candidatos, sem alegação de compatibilidade já comprovada.

## DEC-064 — Requisitos candidatos para memória individual e correção de crenças (v6.0)

- **RN-064-01:** preservar eventos de aquisição do NPC com fonte, tipo, instante DR, localização, canal e provenance sem reescrever declarações passadas.
- **RN-064-02:** separar `CANON_CLAIM`, fato de campanha confirmado, observação, rumor, crença, memória episódica e reputação/atitude; não promover um tipo a outro por síntese LLM.
- **RN-064-03:** informação só é adquirida por encontro, transmissão, observação ou documento legítimos, observando DEC-028/029 e ACL antes do prompt.
- **RN-064-04:** correção editorial de catálogo/Knowledge Pack DEC-063 não altera automaticamente memória ou crença de NPC; requer aquisição/caminho social legítimo.
- **RN-064-05:** permitir aceitar, duvidar, rejeitar, suspender juízo ou investigar conforme evidência, fonte, relações e experiência, sem grau de certeza ou limiares fixados em Discovery.
- **RN-064-06:** novas crenças criam revisão auditável e mantêm crenças anteriores/episódios/diálogos; sem retcon de eventos mecânicos ou história de jogadores.
- **RN-064-07:** NPC pode manter crença falsa e oferecer diálogo marcado como perspectiva sem convertê-la em fato narrador/canon.
- **RN-064-08:** preservar **separação física anual DEC-060**; consultar ano DR atual/antecedentes válidos, nunca antecipar futuro; memórias ficam no overlay privado de campanha/ramo.
- **RN-064-09:** conservar proveniência e conflitos DEC-061, staging/publicação curada DEC-062 e vínculo de pack DEC-063 para cada revisão/consulta.
- **RN-064-10:** transmissão e reavaliação respeitam o relógio, atividade regional, orçamento, segurança de nós LAN e ausência de LLM por NPC/tick.
- **RN-064-11:** em ausência de evidência, permissão, revisão anual ou checkpoint coerente, adiar/bloquear; resultados duplicados/obsoletos não alteram crença.
- **RN-064-12:** mudança de crença não muda automaticamente alinhamento, reputação, quest, item ou variável do jogo; consequências acionam gates narrativos/mecânicos independentes.
- **RN-064-13:** política de esquecimento, compactação e retenção de décadas de episódios será decidida na DEC-065; não presumir memória ilimitada nem expiração automática.
- **RN-064-14:** testes de BG2:EE/EEex, integração de logs/diálogos e performance são candidatos, sem resultado medido.


## DEC-065 — Requisitos candidatos para memória hierárquica, consolidação e retenção (v6.1)

- **RN-065-01:** oferecer camadas de memória imediata, episódica, consolidada e âncoras protegidas, sem duplicar verdades ou tornar síntese uma fonte primária.
- **RN-065-02:** preservar episódio/fonte/DR/campanha/ramo/NPC/ACL e revisão na memória persistente; nunca derivar testemunho de opinião do LLM.
- **RN-065-03:** gerar síntese somente de evidência acessível e verificável, com referências auditáveis e estados candidato/validado/stale/rejeitado.
- **RN-065-04:** usar importância contextual e relações para busca, sem equacionar antiguidade com irrelevância ou assumir escores fixos sem SPECS.
- **RN-065-05:** compromissos, segredos, marcos, mortes e eventos fundadores podem receber âncora de proteção auditável, sem tornarem-se oniscientes ou automaticamente divulgáveis.
- **RN-065-06:** restringir a recuperação ao NPC, branch, relógio, revisão, propósito, executor e ACL antes de pesquisar índice, montar prompt ou enviar a worker LAN.
- **RN-065-07:** uma síntese resumida não apaga evento histórico, crença anterior, quest confirmada, ação do host ou sua proveniência.
- **RN-065-08:** cache descartado, prioridade de recuperação reduzida e eliminação legal/privada são políticas distintas; não definir TTL arbitrário nem ignorar solicitações legítimas de expurgo.
- **RN-065-09:** conservar DEC-060 com **pastas físicas por ano DR**; resumo NPC nunca é publicado como fato canônico anual.
- **RN-065-10:** conservar DEC-061/062/063: fonte/contradição, staging curado e pack versionado; mudança editorial não sincroniza automaticamente memória/consciência do NPC.
- **RN-065-11:** conservar DEC-064: revisão de crença depende de aquisição legítima e preserva histórico de posições anteriores.
- **RN-065-12:** usar consolidação sob demanda/lotes e orçamento DEC-056; não convocar LLM por NPC/tick nem travar jogabilidade por tarefa secundária.
- **RN-065-13:** em falta de identidade, provas, revisão, permissão ou recibo host, adiar ou bloquear; sem promover evento UNCERTAIN.
- **RN-065-14:** projeções e âncoras devem ser restauráveis por checkpoint/backup coerente com campanha/ramo, sem cruzar branches.
- **RN-065-15:** manter telemetria, contexto enviado a modelos e logs minimizados; segredos somente para nós autorizados.
- **RN-065-16:** definir identidade persistente de NPC em DEC-066, antes de atribuir episódios em execução real; POCs/benchmark não executados.

## Requisitos candidatos DEC-066/C — identidade verificável de NPCs (Discovery v6.2)

- **RN-066-01:** Memórias e relações serão indexadas por identidade lógica persistente, campanha e ramo, jamais apenas pelo nome/ID temporário do motor.
- **RN-066-02:** Todo reencontro e recuperação de memória pessoal exigem correspondência positiva verificada com observação vigente; candidato ambíguo não acessa memória privada.
- **RN-066-03:** Despawn, save/load e mudança de área não comprovam morte ou criação de novo indivíduo; eventos de vida/morte exigem evidência apropriada.
- **RN-066-04:** Dois NPCs homônimos, clones ou spawns genéricos não compartilham segredos/relacionamentos por similaridade.
- **RN-066-05:** Restauração, mudança de build e fork invalidam bindings incompatíveis; causalidade anterior legítima pode ser herdada apenas conforme revisão/branch.
- **RN-066-06:** Em ambiguidade, NPC pode oferecer apenas diálogo genérico permitido, nunca alegar familiaridade ou revelar histórias não confirmadas.
- **RN-066-07:** Confirmação de identidade não substitui ACL, cronologia, evidências, consentimento e autorização do host.
- **RN-066-08:** A DEC-060 mantém os diretórios físicos anuais para cânone; identidade/memória privadas são do overlay e não podem ser publicadas nesses arquivos.
- **RN-066-09:** Correções de vínculos terão trilha auditável minimizada, sem apagar eventos confirmados e sem consolidar identidades por IA sem aprovação.
- **RN-066-10:** Comprovar em POCs a estabilidade/escopo dos campos disponíveis em BG2:EE/EEex e dois clientes antes de implementar.

## DEC-067 — Requisitos candidatos de individualização seletiva (v6.3)

- **RN-067-01:** NPCs únicos/companheiros curados têm prioridade de registro; figura genérica não exige identidade persistente nem LLM por tick.
- **RN-067-02:** um figurante pode tornar-se personagem persistente quando evento relevante for confirmado e houver identidade verificável DEC-066, respeitando a política por risco.
- **RN-067-03:** candidatos `AMBIGUOUS`, `STALE` ou `UNCERTAIN` não recebem memória privada nem alegação de reencontro; diálogo genérico autorizado continua possível.
- **RN-067-04:** não inferir passado, vínculos, profissão, segredo ou poderes por simples nome/CRE/aparência/LLM.
- **RN-067-05:** promoção idempotente e reconciliação com população agregada; nenhuma duplicação de NPC, eventos, agenda ou quantidades.
- **RN-067-06:** memórias/crenças do promovido seguem DEC-064/065 e ACL DEC-028/029, sem aprendizado automático de lore.
- **RN-067-07:** individualização lógica não implica spawn, IA contínua ou efeito mecânico; host/Action Gateway e quotas regulam.
- **RN-067-08:** DEC-060–063 preservadas: partições canônicas físicas anuais, proveniência, ingestão curada e Knowledge Pack versionado; overlay NPC por campanha/ramo.
- **RN-067-09:** depois de fork, restore, atualização de mods ou migração, verificar identidade e evidência antes de restaurar/continuar relação.
- **RN-067-10:** quotas e métricas somente após POCs/benchmarks; CPU saturada pode adiar promoção sem descartar fatos confirmados.
- **RN-067-11:** atividades fora de cena e estado arquivado dos promovidos permanecerão objeto da DEC-068, sem perda silenciosa de memórias.
- **RN-067-12:** nenhum teste ou suporte de EEex/BG2:EE/multiplayer foi validado nesta decisão.


## Requisitos candidatos DEC-068/C — vida persistente de NPCs fora de cena (Discovery v6.4)

- **RN-068-01:** NPC individualizado conserva identidade e vínculos após saída da área, desligamento e hibernação; não rebaixar automaticamente a figurante.
- **RN-068-02:** âncoras DEC-065 (promessas, consequências, relações críticas) sobreviverão à mudança de atividade, respeitando retenção legítima e privacidade.
- **RN-068-03:** ACTIVE/NEAR/DISTANT/DORMANT representam *prioridade operacional*, não onipresença ou certeza da localização mecânica.
- **RN-068-04:** ausência e retorno seguirão relógio FROZEN/PARTIAL/REALTIME, intervalos limitados e cursor de evolução confirmada; sem vivências inventadas retrospectivamente.
- **RN-068-05:** acontecimentos pessoais irreversíveis, físicos ou HIGH ficam como proposta ou bloqueados até gates/autorizações/receipts aplicáveis.
- **RN-068-06:** ao reencontrar NPC, verificar identidade DEC-066, ramo, checkpoint, build e estado nativo antes de recuperar memórias personalizadas ou materializá-lo.
- **RN-068-07:** fontes canônicas consultadas apenas via `knowledge/periods/<ano>-DR/` (DEC-060), proveniência/curadoria DEC-061–063 e conhecimento individual DEC-064/065.
- **RN-068-08:** proteger Original Mode, histórias privadas, ACL e nós LAN; diferenciar hibernação, esquecimento, expurgo e desligamento.
- **RN-068-09:** jobs offscreen são limitados e idempotentes; atraso de processamento não avança tempo nem confirma fatos.
- **RN-068-10:** retorno mecânico e consistência multiplayer só serão funcionalidades se POCs com BG2:EE/EEex/host+clientes demonstrarem suporte.

**Status:** requisitos candidatos; não SPEC, testes não executados.

## Requisitos candidatos DEC-069/C — itinerários de NPCs (Discovery v6.5)

- **RN-069-01:** toda viagem relevante de NPC individual terá plano com campanha/ramo, identidade comprovada, origem, destino e versão de rota.
- **RN-069-02:** percurso e conexões geográficas exigem evidência por ano DR, sem inventar caminhos nem tempos exatos.
- **RN-069-03:** local narrativo não pode ser usado como prova de área carregada no motor.
- **RN-069-04:** partida, trânsito, chegada narrativa e presença mecânica possuem estados e provas separadas.
- **RN-069-05:** confirmação física de presença/ação depende de observação/receipt do host e das POCs.
- **RN-069-06:** relógio FROZEN/PARTIAL/REALTIME e catch-up limitado impedem teleporte temporal.
- **RN-069-07:** níveis ACTIVE/NEAR/DISTANT/DORMANT modulam detalhamento sem pathfinding/LLM sempre ativos.
- **RN-069-08:** bloqueios de rota exigem acontecimentos confirmados, não boatos tidos como fatos.
- **RN-069-09:** viagens incertas ou sem topologia ficam pausadas ou pendentes, sem conclusão inventada.
- **RN-069-10:** eventos de viagem, retomada, checkpoint e replay são versionados/idempotentes por campanha e branch.
- **RN-069-11:** segredos e memórias NPC ficam no overlay privado, não nas pastas anuais canônicas.
- **RN-069-12:** rotas de regiões sem áreas jogáveis não prometem aparição física de NPCs na engine.
- **RN-069-13:** reencontros exigem identidade DEC-066 `VERIFIED`, sem associação por nome/visual.
- **RN-069-14:** eventos HIGH/irreversíveis em deslocamentos ficam bloqueados sem gates prévios.
- **RN-069-15:** cenários de POC limpo, EEex, host+clientes e mods são pendência explícita.

## Requisitos candidatos DEC-070/C — incidentes de viagem (Discovery v6.6)

- **RN-070-01:** Todo incidente proposto deve vincular NPCIdentity verificada, trecho/itinerário, janela do mundo, campanha/branch, fontes e revisão KPack.
- **RN-070-02:** Permitir encontros sociais e incidentes LOW apenas sob regras curadas, autorização, validação, ACL e idempotência.
- **RN-070-03:** Incidentes MEDIUM não produzem consequências persistentes antes de satisfação de gates de impacto e autorização.
- **RN-070-04:** Incidentes HIGH não geram morte, prisão, saque, ferimentos, perdas de equipamento ou resultados de combate por inferência.
- **RN-070-05:** LLM sugere conteúdo, mas não valida sozinho a verdade, o risco nem o efeito mecânico.
- **RN-070-06:** Classificar consequências agregadas para impedir encadear LOW em resultado MEDIUM/HIGH.
- **RN-070-07:** Rumores de perigo não devem ser promovidos a ataque/bloqueio confirmado sem evidência e contexto temporal.
- **RN-070-08:** Qualquer alteração mecânica depende do gateway tipado e confirmação por receipt do host; UNCERTAIN bloqueia retry cego.
- **RN-070-09:** Respectar FROZEN/PARTIAL/REALTIME, catch-up delimitado, tempos de rota e ordens causais.
- **RN-070-10:** Se uma rota muda, incidentes de segmento antigo ficam STALE e exigem nova avaliação.
- **RN-070-11:** Não inventar deslocamento físico, spawn ou luta em área que não existe na build atual.
- **RN-070-12:** Checkpoints, restaurações e branches impedem dupla aplicação de incidentes e consequências.
- **RN-070-13:** O fato narrativo da viagem ficará no overlay privado da campanha, e não nos diretórios canônicos anuais.
- **RN-070-14:** Conhecimento NPC será atualizado somente por testemunho ou comunicação plausível e conforme permissões DEC-064.
- **RN-070-15:** Compatibilidade com conteúdos nativos/quests/romances e consentimentos prevalece sobre sugestões do diretor de incidentes.
- **RN-070-16:** Incidentes DORMANT/DISTANT devem ser resolvidos por regras/lotes com orçamento, sem LLM por tick e sem resultados retroinventados.
- **RN-070-17:** Dados fornecidos a worker LAN exigem pareamento e autorização; nenhuma permissão de executar engine.
- **RN-070-18:** Integração de incidentes em encontros jogáveis deverá aguardar decisão específica DEC-071 e validação host/multiplayer.

**Status:** requisitos candidatos, não SPECS; 44 testes T070 não executados. Preservar DEC-060–069.

## DEC-071 — Requisitos provisórios de encontro local a partir de incidentes pendentes

- **RN-071-01:** permitir *candidatar* uma interação local a partir de `incident_id` DEC-070 em janela temporal/área compatíveis, sem presumir spawn.
- **RN-071-02:** exigir evidência do host de presença da party; informações de clientes e IA não comprovam área/instância.
- **RN-071-03:** validar recursos por build DEC-051, identidade DEC-066, scripts DEC-050, cronologia/Knowledge Pack e riscos/consentimentos antes do handoff.
- **RN-071-04:** reservar o direito de resolução por ledger durável e revisão; nunca aplicar o mesmo incidente no offscreen e no encounter simultaneamente.
- **RN-071-05:** admitir apenas operações mecânicas tipadas e suportadas pela build via host/gateway; exigir receipts; `UNCERTAIN` falha fechado.
- **RN-071-06:** registrar efeito narrativo LOW somente quando allowlisted, idempotente e autorizado; impedir consequências MEDIUM/HIGH sem gates.
- **RN-071-07:** em materialização inviável, degradar para narrativa compatível ou estado pendente, sem fabricar combate, loot, HP, quests, scripts, NPCs ou áreas.
- **RN-071-08:** proteger saves, multiplayer, NPCs duplicados, segredos e agência de jogadores presentes/ausentes.
- **RN-071-09:** preservar DEC-060–070 e as memórias/ocorrências somente no overlay da campanha; nunca gravar fatos novos no cânone anual.
- **RN-071-10:** especificar e testar 46 casos de compatibilidade, corrida, cancelamento, reconciliação, restauração e host+dois clientes; testes ainda não executados.

## DEC-072 — Requisitos provisórios do catálogo modular de encontros

- **RN-072-01:** manter catálogo de templates/componentes por build com origem, revisão, dependências, conflitos e direitos de uso.
- **RN-072-02:** não confundir recurso inventariado com capability de interação, materialização ou script comprovada em POC.
- **RN-072-03:** composição de encontros será apenas proposta até revisão temporal, localização/área, build, scripts nativos, risco e consentimento.
- **RN-072-04:** proibir código arbitrário, scripts gerados livremente pelo LLM, edição de save e spawn sem adapter validado e host receipt.
- **RN-072-05:** vincular cada composição à `incident_id` e ao ledger exclusivo DEC-071; nenhuma dupla resolução offscreen/local.
- **RN-072-06:** impedir NPC homônimo/duplicado; exigir identidade DEC-066, estado de quest/romance DEC-050 e manifest DEC-051.
- **RN-072-07:** usar somente contexto autorizado do ano DR, conforme diretórios físicos DEC-060 e Knowledge Pack DEC-063; sem misturar memórias privadas e cânone.
- **RN-072-08:** permitir templates novos exclusivamente após preparo offline, revisão de licença, testes, versão e rollout controlado.
- **RN-072-09:** quando faltar suporte ou recursos, manter incidente pendente/narrativo, sem inventar HP, XP, loot, eventos ou NPCs.
- **RN-072-10:** exigir validação multiplayer host + dois clientes, save/load, restore e capacidade por build antes de habilitar encontro mecânico.
- **RN-072-11:** preservar DEC-060–071 e não alterar ADRs anteriores; template não modifica por si dados canônicos anuais.
- **RN-072-12:** elaborar e executar futuros 48 testes T072-01..48; todos pendentes. Políticas de limpeza pós-encontro ficam para DEC-073.

**Estado:** requisitos candidatos, ainda não SPECS implementadas; nenhuma capacidade de engine comprovada.

## DEC-073/C — Requisitos candidatos de pós-encontro (Discovery v6.9)

- **RN-073-01:** classificar todo recurso candidato à limpeza por origem e propriedade da instância, com cadeia de evidências.
- **RN-073-02:** nunca assumir propriedade a partir de nome, CRE, sprite, coordenada ou template.
- **RN-073-03:** preservar conteúdo nativo e de outros mods, scripts, romances e quests sem deleção automática.
- **RN-073-04:** registrar resultados mecânicos somente por receipts válidos do host da campanha/branch/build/epoch corretos.
- **RN-073-05:** impedir dupla resolução, dupla recompensa ou duplicação de efeitos usando ledger, fencing e idempotência DEC-071.
- **RN-073-06:** preservar itens coletados e ownership transferido, sem cleanup pelo encontro antigo.
- **RN-073-07:** manter memória, identidade e relações NPC após remover uma representação física temporária.
- **RN-073-08:** exigir adapter de cleanup tipado e comprovado por build e multiplayer; asset PRESENT não prova capability.
- **RN-073-09:** aplicar gates de risco cumulativo e autorizações antes de operações destrutivas.
- **RN-073-10:** em `UNCERTAIN`, `STALE`, crash, timeout ou save/load, suspender e reconciliar sem retry cego.
- **RN-073-11:** alinhar plano de encerramento a checkpoint, backup, migração e restauração por ramo.
- **RN-073-12:** impedir a gravação de incidentes e dados de campanha nos diretórios canônicos por ano DR.
- **RN-073-13:** registrar auditoria e pendências com proteção de segredos e sem telemetria obrigatória.
- **RN-073-14:** se não houver suporte de limpeza, manter pendência segura em vez de afirmar recurso removido.
- **RN-073-15:** não propagar efeitos automaticamente para economia/facções; tratar DEC-074 separadamente.
- **RN-073-16:** planejar 50 testes candidatos T073-01..50, todos ainda não executados.

**Estado:** requisitos provisórios, não SPECS; DEC-060 a DEC-072 e ADRs anteriores preservados.


## Requisitos candidatos da DEC-074/C (Discovery v7.0; ainda NÃO SPECS)

- **RN-074-01:** somente evento confirmado/reconciliado pode originar efeitos factuais de encontro; rumor não confirma ocorrência.
- **RN-074-02:** observadores, destinatários e canais devem ser documentados; difusão temporal/geográfica não pode criar onisciência.
- **RN-074-03:** conhecimento e crença individuais são distintos de verdade, reputação social, economia e estado mecânico.
- **RN-074-04:** efeitos sociais e econômicos exigem regra de domínio, causalidade, magnitude proporcional e classificação de risco acumulado.
- **RN-074-05:** cada `(evento, alvo, efeito, regra, campanha, ramo)` pode gerar somente um efeito material; relatos duplicados não duplicam resultados.
- **RN-074-06:** contexto e dados privados são filtrados antes da recuperação/LLM e respeitam ACL de PC/NPC/facção.
- **RN-074-07:** alterações de motor exigem gateway, capability comprovada e confirmação host; sem POC, não aplicar efeitos mecânicos.
- **RN-074-08:** fixar ano DR, Knowledge Pack e branch; fatos de campanha em overlay, sem modificar diretórios canônicos físicos por ano.
- **RN-074-09:** `STALE/UNCERTAIN` suspende propagação de efeitos, permite auditoria/reconciliação e não executa retry destrutivo.
- **RN-074-10:** notícias falsas e correções devem preservar fonte e histórico de crença; efeito corretivo não apaga acontecimento anterior.
- **RN-074-11:** comportamento distribuído de facções/mercados depende de informação recebida e das próprias regras, nunca do acesso irrestrito ao ledger.
- **RN-074-12:** preparar e testar 52 cenários `T074-*`; nenhum foi executado, sem garantias de interoperabilidade BG2:EE/EEex.

## DEC-075/C — Requisitos candidatos para crédito e responsabilidade no coop (Discovery v7.1)

- **RN-075-01:** nunca equiparar evento confirmado, participação comprovada, testemunho e reconhecimento social.
- **RN-075-02:** registrar contribuição individual/indireta/coletiva somente com evidências, aceitando `UNKNOWN` na ausência de telemetria.
- **RN-075-03:** respeitar consentimento, titularidade e controlador temporário ao avaliar PCs delegados ou ausentes.
- **RN-075-04:** não atribuir culpa coletiva por ato de PC isolado sem regra/evidência/consentimento aplicável.
- **RN-075-05:** permitir gratidão do observador conforme sua visão e conhecimento, sem onisciência.
- **RN-075-06:** manter proveniência de relatos falsos e discordantes sem modificar os fatos confirmados.
- **RN-075-07:** proteger identidade secreta de PC; decisão sobre disfarces/aliases permanece DEC-076.
- **RN-075-08:** assegurar idempotência por causa, ator/grupo, regra, campanha e branch; um rumor não duplica recompensas.
- **RN-075-09:** XP, inventário, reputação mecânica, alinhamento ou quest requerem gateway e recibo do host com capability testada.
- **RN-075-10:** preservar separação por ano DR (DEC-060) e armazenar autoria/testemunho no overlay da campanha.
- **RN-075-11:** revisões de atribuição deixam histórico auditável; `DISPUTED`, `STALE`, `UNCERTAIN` não geram certeza fictícia.
- **RN-075-12:** avaliar suporte, cura, negociação, defesa e ajuda indireta sem score competitivo oculto.
- **RN-075-13:** respeitar quotas do scheduler e recuperar pendências sem impactar gameplay.
- **RN-075-14:** executar futuramente 54 testes T075-01..54; todos NÃO EXECUTADOS; nenhuma capacidade de telemetria BG2:EE declarada.

## DEC-076/C — Requisitos candidatos de personas e segredos (Discovery v7.2; ainda NÃO SPECS)

- **RN-076-01:** separar identidade factual privada, persona/alias, declaração, suspeita, conhecimento do observador e divulgação.
- **RN-076-02:** verificar identidade lógica DEC-066; igualdade de nome, roupa ou retrato nunca basta para vínculo.
- **RN-076-03:** permitir várias personas por ator e nomes ambíguos entre atores sem fundir memórias ou mérito.
- **RN-076-04:** somente evidência com proveniência pode promover suspeita a vínculo privado verificado; LLM não decide sozinho.
- **RN-076-05:** vínculo verificado privado não torna a identidade conhecida por NPCs/facções/jogadores.
- **RN-076-06:** qualquer revelação define destinatários, canal, tempo, finalidade, risco, consentimento e ACL.
- **RN-076-07:** segredos e históricos de PCs respeitam DEC-019/028/041/045/046, incluindo delegações e ausências.
- **RN-076-08:** reputação social por persona não se funde globalmente após reconhecimento; efeitos exigem causalidade e dedup.
- **RN-076-09:** preservar cronologia/branch/checkpoint/KPack; save antigo não conhece revelações futuras.
- **RN-076-10:** lore permanece nos diretórios canônicos físicos por ano DR DEC-060; aliases no overlay privado da campanha.
- **RN-076-11:** falhas e `UNCERTAIN` bloqueiam divulgação ou mecânicas não confirmadas, sem retry cego.
- **RN-076-12:** jamais declarar disfarce, troca visual ou rename em BG2:EE sem POC de build e multiplayer.
- **RN-076-13:** nenhum segredo atravessa logs, prompts, índices, LAN ou cache sem ACL/minimização.
- **RN-076-14:** preparar 56 testes T076-01..56, **não executados**, como critérios candidatos para SPECS.

## DEC-077/C — Requisitos candidatos de investigação por evidências (Discovery v7.3; NÃO SPECS)

- **RN-077-01:** distinguir registro factual privado, hipótese de investigador, crença NPC, prova e divulgação.
- **RN-077-02:** cada pista registra identidade da fonte, período DR, local, cadeia de origem, integridade, validade e ACL.
- **RN-077-03:** cópias/eco da mesma fonte não corroboram independentemente uma hipótese.
- **RN-077-04:** contraprovas, álibis e versões contestadas permanecem visíveis a revisores autorizados, sem apagar histórico.
- **RN-077-05:** suspeita não equivale a comprovação; estados inconclusivos são legítimos e não exigem desfecho inventado.
- **RN-077-06:** vínculo verificado privado não pode ser revelado a NPCs, facções ou PCs sem canal e autorização apropriados.
- **RN-077-07:** proteger backstories, segredos e consentimento de titulares de PC, inclusive delegação temporária ou ausência.
- **RN-077-08:** LLM pode propor hipóteses, nunca inventar prova, certificar autoria ou efetivar punição.
- **RN-077-09:** evitar efeitos mecânicos, penalidades, reputação global ou condenações a partir de rumores sem host/gateway/gates.
- **RN-077-10:** rejeitar pistas do futuro, de outros branches/checkpoints e workers LAN sem acesso autorizado.
- **RN-077-11:** separar definitivamente `knowledge/periods/<ANO>-DR/` do ledger de investigações privado por campanha/ramo.
- **RN-077-12:** evitar vazamento em UI, logs, índices, embeddings e prompts de segredos não autorizados.
- **RN-077-13:** preservação de revisões, auditoria, idempotência, deduplicação por ancestralidade e fail-closed em UNCERTAIN.
- **RN-077-14:** preparar 58 cenários T077-01..58 candidatos, **NÃO EXECUTADOS**, e POCs específicas antes de prometer suporte no BG2:EE/EEex.

## DEC-078/C — Requisitos candidatos de justiça e facções (Discovery v7.4; ainda NÃO SPECS)

- **RN-078-01:** resolver política de autoridade por região, facção, tempo DR, fonte e competência validada; desconhecido não vira regra inventada.
- **RN-078-02:** diferenciar fato, denúncia, suspeita, alegação, decisão da autoridade e efeito de engine.
- **RN-078-03:** vincular casos a evidências DEC-077, pistas a favor/contra e identidades/atribuições verificadas DEC-066/075–077.
- **RN-078-04:** prever contraditório e contestação conforme sistema ficcional aplicável, sem impor tribunal universal.
- **RN-078-05:** autoridade corrupta/enganada pode errar no mundo ficcional sem sobrescrever a verdade confirmada.
- **RN-078-06:** motor de regras determinísticas para competência, fluxo, riscos e autorização; LLM local somente para diálogos e explicações contextualizadas.
- **RN-078-07:** suspeita e veredito nunca aplicam automaticamente prisão, confisco, hostilidade, reputação mecânica, morte ou quests.
- **RN-078-08:** ações LOW/MEDIUM/HIGH submetidas a políticas próprias, consentimento aplicável e risco acumulado.
- **RN-078-09:** qualquer efeito mecânico exige gateway tipado e confirmação host, com capability testada por build e multiplayer.
- **RN-078-10:** caso e decisão devem ser versionados, idempotentes por ramo/checkpoint e reconciliáveis em restore.
- **RN-078-11:** rumores e atos oficiais só alcançam destinatários por canais e tempos legítimos; sem notoriedade global automática.
- **RN-078-12:** processos de campanha permanecem em overlays privados, sem gravar nos diretórios canônicos físicos por ano DR.
- **RN-078-13:** jurisdições sobrepostas produzem disputa em vez de escolher autoridade por LLM; detalhamento fica na DEC-079.
- **RN-078-14:** preservar segurança de segredos nos prompts, logs, workers LAN, auditoria e consultas.
- **RN-078-15:** 60 testes candidatos T078-01..60 não executados; POCs de motor e coop obrigatórias.

## DEC-079/C — Requisitos candidatos de reconhecimento entre jurisdições (Discovery v7.5; NÃO SPECS)

- **RN-079-01:** emitir pedido versionado com caso, autoridade origem/destino, competência, intervalo DR, fonte, risco e ACL.
- **RN-079-02:** manter ato local, transmissão, entrega, aceite e execução como fatos distintos.
- **RN-079-03:** distinguir relações entre autoridades para cada tipo de pedido: informação não equivale a extradição.
- **RN-079-04:** não presumir autoridade ou tratado sem fontes/curadoria do período histórico e Knowledge Pack vigente.
- **RN-079-05:** mensagens percorrem canais/rotas e relógio autorizados, sem teleporte de informação ou guardas.
- **RN-079-06:** destinatário verifica autenticidade, validade, competência local, oposição e provas antes de reconhecer solicitação.
- **RN-079-07:** fonte falsa, selo forjado, pseudônimo ambíguo ou documento vencido não geram culpa/mandado automático.
- **RN-079-08:** autoridades podem negociar, negar, aceitar com condição e contestar segundo regras verificadas.
- **RN-079-09:** proteger segredos, backstories, propriedade de PC e controle delegado; ACL antes de enviar a outro domínio.
- **RN-079-10:** LOW/MEDIUM/HIGH e efeitos acumulados seguem gates; coerção HIGH default-deny.
- **RN-079-11:** ação mecânica exige capacidade demonstrada por build, Action Gateway tipado e host receipt; sem POC, narrativa ou pendência.
- **RN-079-12:** mandados e respostas são idempotentes por ramo/caso/pedido/revisão/efeito, sem sanções repetidas.
- **RN-079-13:** UNCERTAIN/STALE, restore, revogação ou disputa bloqueiam novas ações até reconciliação.
- **RN-079-14:** pedidos e respostas derivados da campanha permanecem em overlay privado, sem alteração do cânone físico por ano DR.
- **RN-079-15:** difusão de mandado/revogação respeita tempo/rotas; a política detalhada de correções é DEC-080.
- **RN-079-16:** definir/rodar futuramente **62 testes T079-***, nenhum executado; considerar BG2:EE/EEex host+dois clientes antes de alegar suporte.

## DEC-080/C — Requisitos candidatos para atualização de mandados (Discovery v7.6)

- **RN-080-01:** preservar todos os atos de emissão, retificação, suspensão, revogação, expiração e reemissão como eventos imutáveis, com revisão monotônica.
- **RN-080-02:** distinguir status autoritativo da ordem, conhecimento de cada destinatário e elegibilidade para execução mecânica.
- **RN-080-03:** enviar correções por canal, rota, tempo DR, competência, origem autenticada e ACL; envio não implica recebimento.
- **RN-080-04:** impedir que versão antiga ressuscite ordem revogada após entrega fora de ordem.
- **RN-080-05:** permitir crenças desatualizadas de NPCs sem autorizar coerção mecânica por ordem inválida.
- **RN-080-06:** safety gate em contexto restrito pode bloquear ação HIGH sem transferir informação confidencial ao conhecimento do NPC.
- **RN-080-07:** quando vigência, competência ou identidade são incertas, bloquear/pender atos graves; nenhum LLM pode autorizar.
- **RN-080-08:** exigir consentimentos DEC-041/042 e recibo/capability host para prisão, confisco, perseguição e efeitos em quests.
- **RN-080-09:** distinguir revogação de reparação; não apagar eventos efetivamente confirmados ou restaurar itens automaticamente.
- **RN-080-10:** deduplicar por ordem, revisão, autoridade emissora/destinatária, ramo e tipo; checkpoint/replay sem aplicação dupla.
- **RN-080-11:** proteger identidades secretas, pseudônimos, testemunhos e segredos ao transmitir mandados, logs ou LLM.
- **RN-080-12:** preservar diretórios físicos `knowledge/periods/<ANO>-DR/`, usando overlay de campanha/ramo para processos.
- **RN-080-13:** priorizar avisos de revogação de alto risco dentro do scheduler sem inventar entregas instantâneas.
- **RN-080-14:** critérios e algoritmos específicos ficam para SPECS; 64 testes T080 candidatos ainda não executados.

## DEC-081/C — Requisitos provisórios de reparação (Discovery v7.7)

- **RN-081-01:** Revogação ou anulação não implica dano ocorrido nem direito automático de reparação.
- **RN-081-02:** Comprovar dano e nexo causal com evento/recibo e titular identificado, aceitando estado UNKNOWN/DISPUTED.
- **RN-081-03:** Diferenciar caso jurídico, caso reparatório, remédio, decisão e recibo de efeito.
- **RN-081-04:** Aplicar competências, procedimentos e normas curadas por região, organização e ano DR.
- **RN-081-05:** Não atribuir valores monetários sem fonte e regras econômicas; diferenciar custos/ownership.
- **RN-081-06:** Permitir remédios múltiplos independentes, resultados parciais, revisões e negativas fundamentadas.
- **RN-081-07:** Separar publicação narrativa de restituição mecânica comprovada por host/gateway/adapter.
- **RN-081-08:** Prevenir duplicidade de item, ouro, reputação ou remédio entre autoridades e replays.
- **RN-081-09:** Consentimento e agência de PCs/ausentes preservados, sem impor perdão ou compensação.
- **RN-081-10:** Proteção de pseudônimo e identidade secreta na retratação, por ACL, finalidade e audiência.
- **RN-081-11:** Evitar apagar história, memórias e eventos confirmados; toda correção é novo fato causal.
- **RN-081-12:** Propagação de retratação por canais, rotas e clock; sem atualização global instantânea.
- **RN-081-13:** Risco agregado LOW/MEDIUM/HIGH, HIGH default-deny para liberação, perdas e quests.
- **RN-081-14:** Operação UNCERTAIN, restore ou build divergente exige reconciliação antes de retry.
- **RN-081-15:** Persistir danos/remédios somente em overlay, não em knowledge/periods/<ANO>-DR/.
- **RN-081-16:** Prorrogar pendências com scheduler sem fingir audiência, pagamento ou recibo.
- **RN-081-17:** Definir em SPECS critérios de aceitação e testar host+dois clientes antes de habilitar efeito mecânico.
- **RN-081-18:** 66 testes T081-01..T081-66 são candidatos NÃO EXECUTADOS; decisões DEC-060–080 inalteradas.

## DEC-082/C — Requisitos candidatos de responsabilização institucional (Discovery v7.8)

- **RN-082-01:** separar denúncia, prova, conduta confirmada, avaliação de responsabilidade, decisão e execução.
- **RN-082-02:** vincular jurisdição/organização/ano DR a fonte canônica e competência realmente demonstradas.
- **RN-082-03:** distinguir responsabilidade de agente, superior, omissão e prática institucional sem culpa coletiva automática.
- **RN-082-04:** preservar depoimentos com proveniência, independência e contradições, recusando prova fabricada.
- **RN-082-05:** permitir contestação, revisão e decisões institucionalmente enviesadas como acontecimentos ficcionais, sem alterar fatos confirmados por LLM.
- **RN-082-06:** manter proteção de segredos, PCs, identidades privadas e consentimento DEC-019/028/041/045/046.
- **RN-082-07:** proteger medidas HIGH e mudanças políticas irreversíveis DEC-027/034; efeitos mecânicos somente com gateway/receipt host comprovados.
- **RN-082-08:** impedir reexecução de sanção, punição, reputação ou medida após retry/save/load e efeitos em branch divergente.
- **RN-082-09:** separar reparação da vítima DEC-081 de responsabilização do agente/organização.
- **RN-082-10:** repercussões de reputação e rumor dependem de canal e audiência; organização inteira não vira culpada automaticamente.
- **RN-082-11:** jamais escrever casos de campanha em `knowledge/periods/<ano>-DR/`; registrar somente overlays privados por campanha/ramo.
- **RN-082-12:** código determinístico primeiro, LLM assistivo sob demanda, sem decisão unilateral de medidas coercitivas.
- **RN-082-13:** manter pendência e motivo legível quando fonte/competência/capability são desconhecidos.
- **RN-082-14:** submeter POCs read-only, integração host + dois clientes e 68 testes candidatos T082-01..68, todos NÃO EXECUTADOS.

**Estado:** requisitos de Discovery; não são implementação nem validação de engine.

## Requisitos candidatos DEC-083/C — Proteção de denunciantes e testemunhas (Discovery v7.9)

- **RN-083-01:** vincular fonte ao ator somente por identidade verificada DEC-066; persona não é identificação factual.
- **RN-083-02:** separar nome real, depoimento, prova, risco e divulgação, com ACL individual por finalidade/audiência.
- **RN-083-03:** nunca publicar identidades de testemunhas automaticamente nem impor sigilo absoluto que impeça exame autorizado de conteúdo.
- **RN-083-04:** validar independência de testemunhas, cadeia de origem, autenticidade e contradições sem presumir veracidade.
- **RN-083-05:** disponibilizar extratos contestáveis quando autorizados, sem presumir acesso ao nome da fonte.
- **RN-083-06:** proteger identidades de PCs por consentimento, histórico e delegação DEC-019/041/045/046.
- **RN-083-07:** avaliar competência por organização/ano DR e autorizar divulgação com destinatário, propósito, risco cumulativo e revisão.
- **RN-083-08:** aplicar ACL antes do LLM, RAG, cache, índice, saída, UI, logs, workers LAN e backups.
- **RN-083-09:** detectar risco de reidentificação por metadados e bloquear ou generalizar conteúdo sem autorização.
- **RN-083-10:** preservar conhecimentos por observador e canal DEC-029/064/074; divulgação privada não cria fama pública.
- **RN-083-11:** usar idempotência e epochs para disclosures; `UNCERTAIN/STALE` bloqueiam repetição cega.
- **RN-083-12:** não declarar proteção física, invisibilidade, escolta, prisão ou fuga sem POC mecânica/host.
- **RN-083-13:** manter testemunhos em overlay de campanha/branch, nunca em diretórios físicos canônicos por ano DR.
- **RN-083-14:** não converter ameaça alegada em retaliação confirmada ou culpa institucional.
- **RN-083-15:** priorizar regras determinísticas; LLM apenas assistiva sob demanda, sem decisões de ACL ou revelação autônoma.
- **RN-083-16:** 70 testes T083-01..70 são candidatos NÃO EXECUTADOS e dependem de SPECS/POCs.

## Integração DEC-084/C — Discovery v8.0: requisitos candidatos de proteção ativa

- **RN-084-01:** registrar denúncias, evidências de ameaça e avaliação de risco em objetos distintos, com proveniência.
- **RN-084-02:** não presumir culpa de suspeitos nem agressão efetiva com base em rumor.
- **RN-084-03:** propor medidas graduais de proteção, sem sucesso garantido ou invulnerabilidade.
- **RN-084-04:** conferir consentimento e agência de PC, ausentes e delegados DEC-041/045/046.
- **RN-084-05:** exigir protetores existentes, recursos, autoridades, abrigo e reservas disponíveis.
- **RN-084-06:** respeitar relógio, rotas, presença host e não permitir teleporte narrativo.
- **RN-084-07:** separar propostas de ações mecânicas; action gateway/host receipts somente com POC por build.
- **RN-084-08:** antagonistas só sabem o que aprenderam por canais válidos; não acessar plano confidencial.
- **RN-084-09:** filtrar identidade/rota/horário por ACL antes de LLM/worker/cache/índice/log.
- **RN-084-10:** rejeitar ações irreversíveis HIGH e PvP sem gates específicos.
- **RN-084-11:** reconciliar incidentes e plano após save/load/crash/branch, idempotência e fencing.
- **RN-084-12:** não apagar memórias/quest/identidade ao encerrar proteção ou encounter.
- **RN-084-13:** manter overlays privados separados da base canônica por ano DR DEC-060.
- **RN-084-14:** definir SPECS e POCs com 72 testes candidatos T084-01..72, **todos NÃO EXECUTADOS**.

**DEC-060–083 preservadas integralmente; próxima DEC-085 aberta.**

## DEC-085/C — Requisitos candidatos de sigilo operacional e descobertas (Discovery v8.1, não SPECS)

- **RN-085-01:** compartimentar identidade, refúgio, horários, segmentos de rota, escoltas e contingências, com ACL por ator/finalidade/tempo.
- **RN-085-02:** separar plano confirmado, alegação, evidência, crença adversária e avaliação de comprometimento; não inferir verdade a partir de rumor.
- **RN-085-03:** descoberta pode ser parcial e contraditória; desconhecimento de campos não deve ser preenchido por LLM.
- **RN-085-04:** cada prova exige fonte, ancestralidade, instante, lugar, meio e verificação de oportunidade real de observação.
- **RN-085-05:** acesso interno do host/worker não transfere conhecimento para NPC/PC; filtrar antes de prompts, índices, logs e LAN.
- **RN-085-06:** reidentificação indireta por metadata é tratada como vazamento de segredo.
- **RN-085-07:** receptor só conhece relato após transmissão causal pelo canal e relógio DEC-022/029/069/074.
- **RN-085-08:** investigação do adversário exige capacidades, motivos e recursos fundamentados; NPCs sem presença não testemunham.
- **RN-085-09:** exposição pode iniciar proposta de replanejamento, mas não ataque HIGH, teleporte, invulnerabilidade ou sucesso garantido.
- **RN-085-10:** proteção de jogador exige agência e consentimento DEC-019/041/045/046; medida física requer host+gateway/capability comprovada.
- **RN-085-11:** revisão do plano revoga novos acessos antigos sem apagar memória legítima já adquirida.
- **RN-085-12:** ledger de divulgação/idempotência por campo, destinatário, evento, revisão, campanha, ramo e checkpoint previne efeitos duplicados.
- **RN-085-13:** separar fisicamente cânone `knowledge/periods/<ANO>-DR/` e overlay privado por campanha/ramo DEC-060/063.
- **RN-085-14:** revalidar ACL, clock, grants e build após crash/restore/UNCERTAIN; nenhuma execução mecânica não testada.
- **RN-085-15:** operações deliberadas de desinformação/iscas são assunto futuro DEC-086, não autorizadas nesta decisão.
- **RN-085-16:** preparar 74 cenários T085-01..74 candidatos **NÃO EXECUTADOS** e POC host+dois clientes antes de alegar stealth, escuta, proteção ou interceptação.

## DEC-086/C — Requisitos candidatos de desinformação e contraespionagem (Discovery v8.2)

- **RN-086-01:** diferenciar fato confirmado, alegação plantada, fonte/ator, audiência, conhecimento e resultado.
- **RN-086-02:** operação exige proponente legítimo, titular PC ou autorização delegada explícita e consentimento aplicável.
- **RN-086-03:** registrar propósito, target, meio, janela DR, duração, revisão, risco acumulado e possíveis terceiros afetados.
- **RN-086-04:** reservar recursos e disponibilidade reais; dedup contra gasto/rumor duplicado.
- **RN-086-05:** divulgar só por canais com oportunidade, tempo, presença e source chain demonstráveis.
- **RN-086-06:** receptor pode acreditar, rejeitar, questionar ou descobrir a falsidade; nunca conhecer verdade de plano por metadado privado.
- **RN-086-07:** documento narrativamente falsificado não se torna host receipt nem prova jurídica factual.
- **RN-086-08:** informação parcialmente recebida não revela refúgio/rota/identidade omitidos.
- **RN-086-09:** separar acusações falsas de fatos de autoria confirmada, sem punir NPC/PC automaticamente.
- **RN-086-10:** qualquer PVP, prisão, morte, confisco ou evento irreversível exige gate e capacidade confirmada.
- **RN-086-11:** correções de crenças e exposição de iscas preservam memória/causalidade, sem retcon.
- **RN-086-12:** excluir claims plantados do cânone anual físico; overlay por campanha/branch e Knowledge Pack pinado.
- **RN-086-13:** limitar LLM, workers LAN, RAG, prompt/log/índices e UI pelo need-to-know.
- **RN-086-14:** falha UNCERTAIN, cancelamento, plano revogado, rollback e branch stale não autorizam novo envio.
- **RN-086-15:** não afirmar engine de espionagem/interceptação/mudança visual sem POC host+dois clientes.
- **RN-086-16:** testar os **76 cenários T086-01..76** como candidatos, **NÃO EXECUTADOS**; requisitos ainda dependem de SPECS.

## Integração da DEC-087/C — Requisitos candidatos (Discovery v8.3; NÃO SPECS)

- **RN-087-01:** separar identidade persistente, lealdade factual, filiação pública, promessas, crenças, suspeitas e autoria de atos.
- **RN-087-02:** admitir vínculos simultâneos e não exclusivos com pessoas, facções e causas; manter proveniência e versões.
- **RN-087-03:** somente fatos/eventos autorizados alteram compromissos; nenhuma transição exclusivamente decidida por LLM.
- **RN-087-04:** personalidade e lore canônico curado por período limitam alterações de companheiros e NPCs.
- **RN-087-05:** PCs escolhem seus próprios segredos, alianças e decisões; nenhuma traição forçada por ausência ou delegação genérica.
- **RN-087-06:** NPC em conflito pode negociar, recusar ou não mudar de lado; não existe resultado obrigatório.
- **RN-087-07:** suspeita/rumor de agente duplo não comprova traição e não ativa punição automática.
- **RN-087-08:** recursos, riscos, presença/tempo e normas sociais/faccionais integram a validação da transição.
- **RN-087-09:** conhecimento de segredos segue ACL, memória local e difusão causal; sem onisciência.
- **RN-087-10:** qualquer alteração mecânica de party/faction/quest/item exige host receipt e capability testada.
- **RN-087-11:** histórico é append-only, idempotente e isolado por campanha/branch/ano DR; sem retcon após save/load.
- **RN-087-12:** dedup de propostas, recompensas e despesas; erro UNCERTAIN bloqueia retry cego.
- **RN-087-13:** manter corpus canônico anual físico DEC-060 e overlays sociais dinâmicos separados.
- **RN-087-14:** executar futuramente 80 testes candidatos T087-01..80, atualmente **NÃO EXECUTADOS**.

## DEC-088/C — Requisitos candidatos de informantes (Discovery v8.4; ainda NÃO SPECS)

- **RN-088-01:** validar identidade do NPC, disponibilidade, contexto, contato e conhecimento antes de propor colaboração.
- **RN-088-02:** NPC pode aceitar, recusar, negociar, suspender ou encerrar, sem recrutamento automático por preço.
- **RN-088-03:** diferenciar proposta, resposta, acordo confirmado, promessa, entrega e comprovação de conteúdo.
- **RN-088-04:** PC ausente/delegado não assina, confessa ou assume obrigações sem consentimento específico.
- **RN-088-05:** termos incluem escopo da informação, duração, limites, beneficiários, canais e segurança por audiência.
- **RN-088-06:** reservatórios de ouro/itens e recursos só validam saldo real; efetivar pagamento engine requer receipt host.
- **RN-088-07:** entregar documento/segredo não pode materializar fonte ou fato inexistente; veracidade é separada do evento de entrega.
- **RN-088-08:** evitar farming de segredos, dinheiro, XP, favores e recompensas por alias/recontratação.
- **RN-088-09:** vazamento de identidade, plano de proteção ou histórico PC é bloqueado antes de LLM/LAN/UI/log.
- **RN-088-10:** término da relação não apaga entregas ou memórias confirmadas, mas cessa obrigações futuras conforme contrato.
- **RN-088-11:** preservação estrita de cronologia, checkpoint, branch, fonte canônica anual e KPack fixado.
- **RN-088-12:** LLM local apenas ajuda na redação de propostas/falas; estado e atos determinados por regras e host.
- **RN-088-13:** funções de engine não comprovadas (contratação, pagamento, diálogos) permanecem fora de capacidade declarada.
- **RN-088-14:** 82 testes candidatos T088-01..82, todos ainda NÃO EXECUTADOS.

## DEC-089/C — Requisitos candidatos para informes falíveis (Discovery v8.5; NÃO IMPLEMENTADOS)

- **RN-089-01:** separar entrega confirmada, alegação, prova, família de fontes, avaliação e crença por observador.
- **RN-089-02:** origem de cada relato com ano DR, local, fonte/alias, cadeia de retransmissão e ACL; não preencher `UNKNOWN` pela LLM.
- **RN-089-03:** verificar oportunidade de acesso da fonte antes de atribuir conhecimento ocular, documental ou indireto.
- **RN-089-04:** reconhecer cópias e dependências; não tratar informação repetida como corroboração independente.
- **RN-089-05:** decompor alegações por tempo/local/participantes, permitindo corroboração parcial.
- **RN-089-06:** tratar ausência de confirmação diferente de contradição, mantendo versões incompatíveis quando necessário.
- **RN-089-07:** permitir estado `INCONCLUSIVE/UNVERIFIED` e revisões append-only por novas evidências.
- **RN-089-08:** confiabilidade histórica por contexto e domínio, sem garantia universal nem relação direta com reputação social.
- **RN-089-09:** filtrar identidade de fonte, nomes/rotas/horários protegidos, índices, logs, prompts e LAN antes de exposição.
- **RN-089-10:** nunca distribuir automaticamente a análise entre NPCs/facções; DEC-090 decide dossiês/publicação.
- **RN-089-11:** bloquear punições, mandados ou alterações de engine fundamentados apenas em alegação/informe; host e gates obrigatórios.
- **RN-089-12:** validar calendário/branch/KPack; não importar relato ou correção futura em save/restauração anterior.
- **RN-089-13:** dedup por causa e família de origem em retry/reconexão, reconciliando `UNCERTAIN`.
- **RN-089-14:** preservar conhecimento canônico em pastas anuais físicas DEC-060; relatórios de campanha em overlay privado.
- **RN-089-15:** testar offline com 84 fixtures T089-01..84, todos **NÃO EXECUTADOS**, e só depois medir capacidades reais da engine.

## Integração DEC-090/C — Discovery v8.6

**Requisitos candidatos — não SPECS nem implementação:**

- **RN-090-01:** separar dossiê, snapshot, alegação avaliada, citação de evidência, view filtrada, autorização, transmissão e recibo.
- **RN-090-02:** preservar incerteza/contradições/famílias independentes DEC-089 em cada relatório.
- **RN-090-03:** aplicar ACL por campo, finalidade, audiência, tempo e competência, incluindo anexos/metadados.
- **RN-090-04:** nunca revelar identidade protegida DEC-083, alias DEC-076 ou refúgio DEC-085 por redação indireta.
- **RN-090-05:** produzir views distintas para autoridade, aliado, party e NPC apenas com autorização específica.
- **RN-090-06:** preservar agência de PC, consentimento e limites da delegação DEC-019/041/045/046.
- **RN-090-07:** validação e sanitização determinísticas **antes** de inferência LLM, RAG, LAN, UI e logs.
- **RN-090-08:** compor não publica; enviar não confirma entrega; entregar não confirma crença ou compreensão.
- **RN-090-09:** atualizações, correções e retratações geram revisões imutáveis, sem apagar versões antigas.
- **RN-090-10:** transmissão respeita canais, geografia, tempo DR, checkpoint, branch e Knowledge Pack pinado.
- **RN-090-11:** falhas, UNCERTAIN e STALE não garantem envio nem autorizam reexecução cega.
- **RN-090-12:** conteúdo dinâmico de campanhas não é incorporado ao lore canônico físico anual DEC-060.
- **RN-090-13:** nenhum item, journal, quest ou reputação mecânica é modificado sem gateway/host receipt e POC.
- **RN-090-14:** implantar somente após fixtures e gates: **86 testes T090-01..86 candidatos NÃO EXECUTADOS**.

## Integração DEC-091/C — Discovery v8.7 (requisitos candidatos; SPECS pendentes)

- **RN-091-01:** toda proposta aponta dossiê/revisão/alegações com incertezas, contradições e autorização de acesso.
- **RN-091-02:** não transformar hipótese, dossiê, plano, reserva ou despacho em fato confirmado.
- **RN-091-03:** capturar objetivo, local, DR, alvo/participantes, precondições, critérios de sucesso/aborto e riscos.
- **RN-091-04:** validar deterministicamente localização, identidade, recurso, capacidade de build, facção, consentimento e efeitos agregados.
- **RN-091-05:** ações de PC exigem escolha legítima e delegação expressa; IA não pode assumir vontade do jogador.
- **RN-091-06:** ações de NPC/facção respeitam autonomia e disponibilidade verificadas, sem teleporte de instâncias.
- **RN-091-07:** HIGH é default-deny; ações mecânicas só por host + Action Gateway com recibo.
- **RN-091-08:** operações e reservas usam idempotência/lease/TTL; uncertain impede retry cego e duplicações.
- **RN-091-09:** novos fatos, mudanças de risco ou checkpoint tornam planos antigos STALE/NEEDS_REVALIDATION.
- **RN-091-10:** preservar ACL em prompts, logs, UI, LAN e caches, inclusive informação em metadados de planos.
- **RN-091-11:** particionamento físico canônico por ano DR DEC-060 continua intacto; planos ficam no overlay por ramo.
- **RN-091-12:** preparar 88 testes candidatos T091-01..88; **nenhum teste executado**; DEC-092 tratará replanejamento em curso.

## DEC-092/C — Requisitos de monitoramento e replanejamento (aprovados como Discovery v8.8, não SPECS)

- **RN-092-01:** monitorar apenas eventos confirmados, deduplicados e pertinentes à operação.
- **RN-092-02:** reter baseline e revisões imutáveis por `plan_id`, campanha/branch, DR, checkpoint e host session.
- **RN-092-03:** diferenciar alteração cosmética de alteração material por impacto em risco/objetivo/PCs/recursos/tempo/ACL.
- **RN-092-04:** bloquear novos despachos dependentes quando consentimento for revogado ou risco/capability variar.
- **RN-092-05:** replanejamento material exige novo consentimento/autoridade; não herdá-los automaticamente.
- **RN-092-06:** pausa do orquestrador não anuncia nem presume pausa do motor BG2:EE.
- **RN-092-07:** cancelar não reverte atos efetivamente confirmados; compensações são eventos separados.
- **RN-092-08:** ação host in-flight ou UNCERTAIN requer reconciliação antes de release/retry.
- **RN-092-09:** só host/Action Gateway alteram engine; nenhuma LLM assume decisão de PC.
- **RN-092-10:** recursos reservados, consumidos e liberados são estados separados com fencing/lease.
- **RN-092-11:** auditoria e notificações respeitam ACL de dossiês, testemunhas, pseudônimos e rotas.
- **RN-092-12:** monitoramento determinístico por subscriptions, sem polling LLM por frame/tick.
- **RN-092-13:** restore/reconnect impede reaplicação de eventos futuros ou comandos de outro branch.
- **RN-092-14:** a partição física canônica DEC-060 e Knowledge Packs por período DEC-063 permanecem intactos.
- **RN-092-15:** preparar e só depois executar 90 testes T092-01..90; nenhum teste ou POC é alegado como concluído.

## Integração da DEC-093/C — requisitos candidatos para operações concorrentes (não SPECS)

- **RN-093-01:** permitir operações simultâneas quando os recursos e janelas forem compatíveis.
- **RN-093-02:** definir identidade persistente de NPC/PC/item, sem usar pseudônimo como unicidade.
- **RN-093-03:** reservas por campanha/branch, janela DR, revision, fencing, quantidade, ownership e finalidade.
- **RN-093-04:** evitar double booking de recurso singular e overbooking de quantidade comprovada.
- **RN-093-05:** diferenciar reserva lógica, consumo mecânico e presença física confirmada pelo host.
- **RN-093-06:** reconhecer conflitos contextuais, não assumir que mesma região exige exclusão.
- **RN-093-07:** não redistribuir recursos/compromissos de PC sem seu consentimento específico.
- **RN-093-08:** prioridades determinísticas e fairness não substituem autoridade, ACL ou HIGH gates.
- **RN-093-09:** `DISPATCHED/UNCERTAIN` bloqueia reatribuição/duplicação até reconciliação.
- **RN-093-10:** garantir que planos sem conflito continuem enquanto outro aguarda recurso.
- **RN-093-11:** preservar revisões, cronologia DR, checkpoint, build e KPack por ramo.
- **RN-093-12:** evitar divulgação do motivo secreto de conflito a públicos sem ACL.
- **RN-093-13:** alertar ciclos de espera, sem cancelar operações/in-flight automaticamente; detalhar em DEC-094.
- **RN-093-14:** definir provas sintéticas e POC host+2 clientes antes de alegar execução mecânica.
- **Evidência:** 92 testes T093-* NÃO EXECUTADOS. Documentos DEC-060–092 preservados.

## Integração DEC-094/C (Discovery v9.0) — requisitos candidatos, NÃO SPECS

- **RN-094-01:** grafo de espera por operação/recurso/ramo/epoch; distinguir ciclo suspeito, deadlock confirmado e alternativas viáveis.
- **RN-094-02:** detectar starvation sem transformar antiguidade da fila em consentimento, recurso ou prioridade HIGH automática.
- **RN-094-03:** lease expirado não implica recurso físico livre; comprovar que reserva lógica nunca foi despachada.
- **RN-094-04:** segregar `HELD` revogável de `DISPATCHED`, `DISPATCH_PENDING` ambíguo, `CONSUMED_VERIFIED` e `UNCERTAIN` em quarentena segura.
- **RN-094-05:** decisões de recuperação auditáveis e idempotentes, com CAS/fencing, revisão de recursos e checkpoint/branch atuais.
- **RN-094-06:** respeitar titularidade/consentimento e não alterar obrigações de PC nem preemptar escolhas de terceiro.
- **RN-094-07:** realizar conciliação antes de qualquer nova reserva que possa duplicar efeito mecânico.
- **RN-094-08:** permitir progresso de operações independentes mesmo com outra aguardando reconciliação.
- **RN-094-09:** proteger metadados de operações, testemunhas, rotas e informantes por ACL e redação de logs.
- **RN-094-10:** manter clocks DR separados de relógios internos, revalidando epochs após restart/restore.
- **RN-094-11:** nenhuma reversão automática de ação host-confirmed; política de compensação fica para DEC-095.
- **RN-094-12:** preparar **94 testes candidatos, NÃO EXECUTADOS**, para SPECS e POCs futuras em host+dois clientes.

## Integração DEC-095/C — Discovery v9.1 — requisitos candidatos, NÃO SPECS

- **RN-095-01:** cada operação composta possui Saga versionada, etapas e evidências de execução distintas de propostas/despachos.
- **RN-095-02:** etapa host-confirmada persiste no ledger; compensação é novo evento e pode deixar efeitos residuais.
- **RN-095-03:** políticas tipadas classificam passos como compensáveis, condicionais, não compensáveis ou desconhecidos; fail-closed.
- **RN-095-04:** reembolsos/contratos exigem regra, saldo, titular e consentimento, e receipt se mecânicos.
- **RN-095-05:** ações UNCERTAIN mantêm quarentena e reconciliam sem retry cego.
- **RN-095-06:** ordem de compensação segue DAG/dependências seguras, não sempre inversão simples.
- **RN-095-07:** preservar mortes, testemunhos, memórias, viagem, tempo e fatos canônicos confirmados.
- **RN-095-08:** confidencialidade e autonomia PC valem mesmo sob falhas/restore.
- **RN-095-09:** 96 casos T095 candidatos NÃO EXECUTADOS; POCs de host/bridge pendentes.
- **RN-096-PROP-01 (NÃO APROVADO):** catálogo de eventos por ano DR, tempo preciso e proveniência, geografia e tags de locais com regras DSL pré-validadas.
- **RN-096-PROP-02 (NÃO APROVADO):** distinguir repercussões diretas/indiretas com pré-condições, limites, recibos, difusão causal e dedup.
- **RN-096-PROP-03 (NÃO APROVADO):** YEAR_ONLY/DISPUTED não fabricam mês; LLM sem autoridade sobre cronologia, consequências ou host.
- **RN-096-PROP-04 (NÃO APROVADO):** matrizes em planilha como ferramenta editorial; runtime indexado e determinístico, sem varredura completa por frame.

## Integração DEC-096/C — Discovery v9.2 — requisitos de arquitetura, ainda NÃO SPECS

- **RN-096-01:** cronologia física por ano DR em `knowledge/periods/<ANO>-DR/`, com fonte e pin KPack.
- **RN-096-02:** não inferir mês/dia não informado nem converter calendário Harptos em calendário gregoriano.
- **RN-096-03:** separar verdade canônica, regra de repercussão, efeito confirmado, informação adquirida e rumor.
- **RN-096-04:** abrangência global não implica efeitos em qualquer lugar nem conhecimento automático dos NPCs.
- **RN-096-05:** matriz de edição em colunas; runtime usa entidades normalizadas e DSL tipada sem código arbitrário.
- **RN-096-06:** filtro determinístico de fase, janela DR, região, tipo de local, pré-requisitos e divergência da campanha.
- **RN-096-07:** não ativar regra com fonte disputada, KPack não pinado, local não mapeado ou capability não comprovada.
- **RN-096-08:** emitir proposta sem efeito; aplicar mecânica somente com Action Gateway e host receipt.
- **RN-096-09:** impacto indireto requer pai host-confirmed, delay e escopo coerente.
- **RN-096-10:** dedup/ledger por campanha, ramo, epochs, rule revision, phase e efeito; restore não repete.
- **RN-096-11:** LLM só refina texto baseado em recorte autorizado, sem alterar valores, fatos, gatilhos ou prioridades.
- **RN-096-12:** não reexecutar acontecimentos antigos ao carregar estado posterior; usar baseline curado separado.
- **RN-096-13:** templates/IDs de mapas e mapas de presença validados por build; nenhuma criação automática de NPC.
- **RN-096-14:** NPC recebe notícia por canal com tempo e prova, nunca por presença em índice físico.
- **RN-096-15:** efeitos simultâneos exigem caps e política tipada de composição, a detalhar DEC-097.
- **RN-096-16:** 100 cenários T096-001..100 são candidatos NÃO EXECUTADOS; scripts/schemas sintéticos são somente unitários.

## Integração DEC-097/C — Discovery v9.3

RN-CMP-097-01: efeitos elegíveis DEC-096 sobre mesma variável local serão compostos por `MetricPolicy` e `stack_family`, nunca por ordem de leitura de linhas nem por LLM. RN-CMP-097-02: relatos e conhecimento dos NPCs seguem difusão causal separada. RN-CMP-097-03: eventos com origens correlacionadas não contam como impactos independentes sem curadoria. RN-CMP-097-04: caps, tempo DR, duração e expiração afetam propostas/snapshots e não apagam acontecimentos confirmados. RN-CMP-097-05: efeito só pode alterar BG2:EE após capabilities testadas, risco/consentimento, Action Gateway e receipt do host. Detalhes no ADR-0092 e doc técnico 97, 102 testes candidatos **NÃO EXECUTADOS**; DEC-098 aberta.

## Integração DEC-098/C — Discovery v9.4 — requisitos candidatos (não SPECS)

- **RN-MAT-098-01:** Materialização incremental depende de projeção elegível DEC-096 e composição DEC-097, nunca de LLM narrativa.
- **RN-MAT-098-02:** Snapshot regional só avança com receipt host validado e estado observado; proposta não altera estado.
- **RN-MAT-098-03:** HostObservation registra cobertura; ausência em scan parcial não prova inexistência de objeto.
- **RN-MAT-098-04:** ID persistente NPC/objeto não é nome/CRE nem engine instance ID e requer vínculo auditável.
- **RN-MAT-098-05:** Native/quest/mod, item de jogador, transferido ou ownership UNKNOWN devem ser preservados/bloqueados.
- **RN-MAT-098-06:** CREATE somente como proposta allowlisted e com quotas/recursos/gates/POC de capability.
- **RN-MAT-098-07:** UPDATE aplica target ou diff tipado, não multiplica percentuais a cada reentrada.
- **RN-MAT-098-08:** RETIRE é revisão, não DELETE; limpeza depende de DEC-071/073 e host receipt.
- **RN-MAT-098-09:** Snapshot por campanha, branch, epoch, checkpoint, map, build, pack, ruleset e revision.
- **RN-MAT-098-10:** Não duplicar NPCs ao sair, entrar, voltar de viagem ou restaurar save.
- **RN-MAT-098-11:** Nenhum comando incerto, em voo ou já confirmado é reemitido automaticamente.
- **RN-MAT-098-12:** Clientes multiplayer não confirmam estado host e não recebem dados privados de outro ramo.
- **RN-MAT-098-13:** FROZEN não avança por wall-clock; catch-up PARTIAL/REALTIME usa tempo DR validado.
- **RN-MAT-098-14:** ACTIVE/NEAR/DISTANT/DORMANT têm quotas e fidelidade adequadas a DEC-021/068.
- **RN-MAT-098-15:** Handoff offscreen->local preserva lease e unicidade do incidente DEC-071.
- **RN-MAT-098-16:** Patrulhas e recursos não são spawnados sem custo, titularidade e disponibilidade.
- **RN-MAT-098-17:** Rumores e memória dos NPCs não são atualizados por simples materialização.
- **RN-MAT-098-18:** Quest scripts, cutscenes e mods externos nunca são patchados por heurística genérica.
- **RN-MAT-098-19:** Conflito de snapshot/host/build ou ID reciclado deve falhar fechado e ser auditável.
- **RN-MAT-098-20:** Efeitos irreversíveis e transferências confirmados não são apagados por expiração de regras.
- **RN-MAT-098-21:** A LLM pode descrever resultados autorizados sem determinar estado mecânico nem segredos.
- **RN-MAT-098-22:** T098-001..104 são candidatos NÃO EXECUTADOS; referência sintética não valida bridge.


## Requisitos adicionais — DEC-099/C (Discovery v9.5)

- `REQ-OWN-099-01`: o overlay Living World não deve editar, remover, recriar ou assumir scripts, quests, NPCs de mods/engine ou recursos de PCs por divergência entre estado desejado e estado observado.
- `REQ-OWN-099-02`: identidade persistente, origem de template, ownership de instância, custódia e autoridade por campo devem ser distinguidos com provas e revisões.
- `REQ-OWN-099-03`: toda proposta de alteração será avaliada por campanha, branch, host/checkpoint epoch, build/EEex/modpack fingerprint, capability e autorização tipada; UNKNOWN/ambíguo/revisão divergente bloqueia.
- `REQ-OWN-099-04`: mesmo recursos criados pela IA não concedem permissão automática sobre quest flag, inventário de PC, scripts, romance ou kill/revive.
- `REQ-OWN-099-05`: toda execução real exige Action Gateway e receipt do host; ação `UNCERTAIN`/`DISPATCHED` demanda reconciliação sem retry cego.
- `REQ-OWN-099-06`: funções read-only de observação não expandem ACL, não revelam spoilers a jogadores e não tornam uma flag mecânica editável. DISCOVERY não confere capability sem POC por build.
- **Referências:** ADR-0094 e documento 99; DEC-100 pendente para observabilidade mínima. **Não implementado.**


## Requisitos candidatos — DEC-100/C: observação mínima e fronteiras de spoiler (Discovery v9.6)

- **RN-OBS-100-01:** observar quests/scripts apenas com probe read-only cuja ausência de efeitos colaterais esteja comprovada na build/modpack/adapter pinados.
- **RN-OBS-100-02:** toda leitura exige allowlist, audiência/finalidade, ACL, sessão/campanha/ramo, TTL, host/checkpoint epoch, cobertura e proveniência.
- **RN-OBS-100-03:** dados brutos técnicos não entram no prompt, memória de NPC, dossiê, logs compartilhados ou LAN sem política específica; divulgar apenas marcos semânticos mínimos autorizados.
- **RN-OBS-100-04:** scan parcial/indisponível/stale não prova negativo nem autoriza progressão de quest; resultado desconhecido permanece desconhecido.
- **RN-OBS-100-05:** leitura não confere ownership de escrita, confirmação de ação do host nem saber causal de NPC/jogador; recebimento de relatório é evento separado.
- **RN-OBS-100-06:** cache isolado por build/modpack/campaign/branch/audience/purpose/epoch; restore, mudança de ACL ou modpack invalidam projeções.
- **RN-OBS-100-07:** sem POC por build ou com side effects comprovados, manter default-deny; nenhuma integração EEex foi testada neste Discovery.
- **RN-OBS-100-08:** futuro mapeamento semântico DEC-101 precisa de curadoria de scripts/versionamento, nunca interpretação espontânea de LLM.

**Referências:** ADR-0095, documento 100, testes T100-001..124 **candidatos NÃO EXECUTADOS**.

## Requisitos de interpretação de quests — DEC-101/C (Discovery v9.7)

- **RN-101-01:** interpretar estados internos somente com observações de DEC-100 autorizadas e catalogadas por build, modpack, ordem, script e adapter.
- **RN-101-02:** não deduzir semântica de números/nomes de flags por analogia, sem mapeamento curado.
- **RN-101-03:** usar predicados tipados e completos, nunca execução de expressões arbitrárias vindas de mods.
- **RN-101-04:** checar grupos de marcos mutuamente exclusivos antes de publicar uma conclusão; múltiplos acertos => `AMBIGUOUS`.
- **RN-101-05:** validar `allowed_previous`, sequence e host/checkpoint epoch; divergência => quarentena sem correção de host.
- **RN-101-06:** ausência ou cobertura parcial não provam negativo; negativas exigem regra e coverage exaustiva.
- **RN-101-07:** manter catálogo técnico e observation envelope fora da LLM e dos NPCs; divulgar somente `safe_milestone_id` ACL-filtrado.
- **RN-101-08:** divulgação, entrega, recepção e conhecimento são eventos independentes; projection não é recebimento.
- **RN-101-09:** impedir leakage por log, erro, metadado, cache, rede, UI e prompt; segredos futuros são default-deny.
- **RN-101-10:** alterações de build/mod/script/mapping/epoch invalidam caches e require recertificação.
- **RN-101-11:** marco observado não é ação/recibo do host, não atribui autoria a PC, não modifica quests ou cânone.
- **RN-101-12:** nenhum gatilho de eventos históricos DEC-096–098 a partir de marco indeterminado; versionar dependências e source.
- **RN-101-13:** LLM só pode redigir com informações já liberadas, nunca inferir significado de flag desconhecida.
- **RN-101-14:** 128 testes T101-* candidatos **NÃO EXECUTADOS**; testes Python locais são apenas sintéticos.


## Integração DEC-102/C — Discovery v9.8

**Requisitos.** Ao detectar divergência entre quest do host e overlay, exigir prova DEC-100/101, epoch e receipts; nunca alterar scripts/quests nem fazer NPCs esquecerem/descobrirem fatos. Rebase somente da projeção derivada e sob autorização independente. LLM não concilia evidências.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**


## Requisitos candidatos derivados da DEC-103/C (Discovery v9.9)

1. **RN-103.1:** marco de quest só pode produzir candidatos de repercussão com prova read-only DEC-100, catálogo curado DEC-101 e reconciliação committed DEC-102; nenhuma interpretação por LLM.
2. **RN-103.2:** separar `Occurrence/Admission/ConsequenceProposal/HostReceipt/NewsDelivery/RecipientKnowledge` com proveniência, branch, epochs, cronologia DR, ACL e idempotência.
3. **RN-103.3:** aplicar matriz DEC-096 e agregação DEC-097 somente a regras pinadas e elegíveis; materialização por DEC-098/099 e autorização/host para efeitos mecânicos.
4. **RN-103.4:** não universalizar rumores; comunicação exige canal, distância/tempo e prova de entrega, resguardando fontes/identidades.
5. **RN-103.5:** save/load, reentry, replay de outbox, outro cliente ou mudança de session não podem duplicar efeitos; restore/branch é auditado.
6. **RN-103.6:** retificações futuras suspendem novas derivações incertas sem apagar fatos ou memórias; compensações aplicam DEC-095 com autorização separada.

**Nota:** requisitos são propostas para futuras SPECS; DEC-103 foi aprovada **somente como arquitetura** e os 136 testes de integração permanecem NÃO EXECUTADOS.

## Adendo vinculante — DEC-104/C (Discovery v10.0)

REQ-RECT-104: uma retificação curada não deve apagar o que um NPC ouviu ou o que host confirmou; somente novas mensagens e revisões causais permitidas, com ACL, relógio DR e proveniência. Suspender novas derivações arriscadas, reconciliar despacho incerto, compensar efeitos mediante DEC-095 e Action Gateway. Arquitetura aprovada; sem integração de jogo comprovada.

## Requisitos candidatos decorrentes da DEC-105/C — Discovery v10.1

| Requisito | Condição de aceite futura |
|---|---|
| RN-105-01 — Errata autenticamente comprovada | Fonte curada committed; requisição não pode self-grant proof/ACL |
| RN-105-02 — Propagação com alcance limitado | Mensagem enviada por canal, rota, tempo DR, presença e recursos verificáveis |
| RN-105-03 — Entrega independente da cognição | Receipts de despacho, entrega e percepção separados, sem aceitação implícita |
| RN-105-04 — Memória falível preservada | NPC pode aceitar, contestar ou ignorar correção; original continua no histórico |
| RN-105-05 — Proteção de fontes/PCs | ACL por finalidade/destinatário; ausência de leak e de decisão atribuída a PC |
| RN-105-06 — Recuperação e sincronização | Idempotência por destinatário e revisão, CAS/outbox, save/restore/fork/epochs |
| RN-105-07 — Consequências mecânicas independentes | Reputação, recursos e quests dependem de políticas e receipts próprios |

**Estado:** requisitos arquiteturais, não implementados; T105-001..144 são testes candidatos NÃO EXECUTADOS no jogo. Próxima DEC-106 para reabilitação reputacional.

## Requisitos arquiteturais candidatos — DEC-106/C · Discovery v10.2

| Requisito | Critério futuro de aceite |
|---|---|
| RN-106-01 — Prova independente | Retificação `COMMITTED`/curada e nexo com alegação original, nunca fornecidos pelo próprio pedido |
| RN-106-02 — Contexto reputacional | Público, região, facção e dimensão da confiança distintos, sem global reset |
| RN-106-03 — Alcance efetivo | Prova da exposição à acusação e da recepção/percepção da correção independentes |
| RN-106-04 — Danos | Diferenciar dano alegado, contestado, corroborado e host-confirmed, com origem e sem dupla contagem |
| RN-106-05 — Autonomia | Nenhum PC ou NPC obrigado a perdoar, confessar, aceitar retratação ou restaurar relações |
| RN-106-06 — Recursos e ownership | Nenhuma indenização, reputação do host ou quest alterada sem autorização, capacidade e recibo próprios |
| RN-106-07 — Sigilo | ACL pré-LLM para fonte, testemunha, alias, vítima, público e comprovantes |
| RN-106-08 — Continuidade | Save/load/forks e branches com CAS/idempotência; nenhuma reemissão ou pagamento em `UNCERTAIN` |

**Estado:** DEC-106/C aprovada apenas como arquitetura, 148 cenários T106-* candidatos NÃO EXECUTADOS em jogo; provas de integração pendentes. Próximo tema DEC-107: direito de resposta e mediação reputacional.

### Integração DEC-107/C — Requisitos de mediação e contraditório

- **REQ-MED-107-01:** notificação, entrega, percepção, janela DR e manifestação independente; ausência nunca prova culpa.
- **REQ-MED-107-02:** documento/evidência com proveniência, contestação, ACL e proteção de fontes.
- **REQ-MED-107-03:** identidade persistente, poderes de representante e participação voluntária; PC só por autorização do próprio jogador.
- **REQ-MED-107-04:** mediador imparcial, sessões e recursos viáveis, conflitos revisáveis e sem coerção.
- **REQ-MED-107-05:** minuta e aceites por parte e termo/revisão, nenhum compromisso ou mecanismo de host sem gates e receipt.
- **REQ-MED-107-06:** testes T107-001..152 candidatos, não executados; exemplos Python exclusivamente sintéticos.

### Requisitos arquiteturais candidatos — DEC-108/C · Discovery v10.4

- `REQ-FUL108-01`: monitorar apenas acordos committed e termos por revisão/parte com mandato comprovado.
- `REQ-FUL108-02`: distinguir vencimento em tempo DR, cumprimento alegado, prestação host-confirmed e saldo sem comprovação, sem presumir fraude.
- `REQ-FUL108-03`: agregar recibos válidos sem duplicar `action_id/receipt_id`, com isolamento de campanha, branch, epochs e build.
- `REQ-FUL108-04`: manter alegações e contestações, notificar por canal permitido e oferecer prazo de esclarecimento sem culpabilização pelo silêncio.
- `REQ-FUL108-05`: aditamento exige nova revisão committed, consentimentos individuais e recursos reais; pedido não altera termos.
- `REQ-FUL108-06`: `DISPATCHED/UNCERTAIN` bloqueia retry; reconciliar antes de reusar reservas ou confirmar pagamento.
- `REQ-FUL108-07`: nenhum ouro, inventário, quest, reputação, sanção ou declaração de PC é alterado sem gates e recibo mecânico.
- `REQ-FUL108-08`: versões de contrato, notificações, provas e dados privados seguem ACL, retenção e knowledge boundaries das DEC anteriores.

**Estado:** DEC-108/C aprovada como arquitetura; T108-001..160 são candidatos de integração NÃO EXECUTADOS no motor. DEC-109 em aberto, para grafos de obrigações condicionais multipartes.

### Requisitos candidatos — DEC-109/C · Discovery v10.5

- `REQ-109-01`: aceitar exclusivamente agreements committed com consentimentos, mandatos, branch/epoch e revisões verificadas.
- `REQ-109-02`: representar obrigações multipartes como DAG tipado com nós, arestas e limiares curados, sem ciclos, duplicatas ou dependências imaginadas.
- `REQ-109-03`: distinguir comprovantes host-confirmed, alegações, entregas parciais e condições realmente satisfeitas; recibos distintos e idempotentes.
- `REQ-109-04`: suportar `ALL/ANY/AT_LEAST(k)` somente quando acordados, sem habilitar `CONFIRMED_COMPLETE` por entrega parcial.
- `REQ-109-05`: usar tempo DR, resource ownership, capacidades testadas e grants por termo antes de propor qualquer ação subsequente.
- `REQ-109-06`: bloquear efeito automático, preempção, liberação de escrow, sanção e reputação; lidar com `UNCERTAIN` via reconciliação.
- `REQ-109-07`: revisar grafo mediante novo acordo committed, CAS, histórico imutável e consentimento das partes legítimas.
- `REQ-109-08`: segregar ACL, campanha/save e conhecimento de NPCs, não divulgar cláusulas ou identidade de fontes a destinatários não autorizados.

**Estado:** DEC-109/C aprovada como arquitetura; **T109-001..168 NÃO EXECUTADOS** no jogo. DEC-110 em aberto para garantias e custódia condicional de recursos.

## Integração DEC-110/C — custódia verificável (v10.6)

REQ-ESC-001: QUANDO um acordo previr caução, o sistema DEVERÁ distinguir promessa/compromisso de depósito realmente confirmado pelo host. REQ-ESC-002: ENQUANTO não existir capability validada para a build e dois clientes, o sistema NÃO DEVERÁ representar a caução como mecanicamente segregada. REQ-ESC-003: QUANDO condições de liberação forem comprovadas, o sistema DEVERÁ apenas produzir proposta dependente de consentimento/autoridade, jamais transferir item/moeda por conta própria. REQ-ESC-004: QUANDO a operação estiver `DISPATCHED`/`UNCERTAIN`, DEVERÁ bloquear retry e reutilização até reconciliação. Estes requisitos são arquitetura, não implementação.
