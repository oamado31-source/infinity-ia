# Mapa de decisões — backlog de discovery

**Versão:** 11.0. Este mapa inclui decisões aprovadas e temas ainda em aberto; os estados válidos são os de cada linha. DEC-005-R e DEC-005-E estão aprovadas; DEC-005-T é um objetivo aprovado cuja implementação está bloqueada por testes. O histórico individual como gerador de eventos faz parte da DEC-004.


## Atualização vinculante — questionário aprovado, 2026-11-07

DEC-006, 007, 013, 015, 016, 017, 018 e 111 aprovadas **como política de implementação** no lote Q01–Q28, com ADR-0106 a ADR-0111. Estados legados 'abertos' nas notas cronológicas abaixo são históricos. A Q07/Q20 acrescenta voz bidirecional push-to-talk, STT e TTS opcionais. Github será público com PRs externos, mas **não foi criado** no serviço e a estratégia repo independente/fork permanece **PROPOSTA**. Integração BG2EE/EEex multiplayer segue não executada.

**Estados permitidos:** Aberta | Proposta | Aprovada | Bloqueada por teste | Substituída.

| ID | Domínio | Decisão a tomar | Dependências / impacto | Estado |
|---|---|---|---|---|
| DEC-001 | Produto | **Opção C escolhida: coop privado primeiro, mantendo evolução possível para mundo compartilhado** | Autoridade do estado, isolamento de campanhas, migração de persistência | **Aprovada** |
| DEC-002 | Infraestrutura | **Opção A: Windows nativo para execução e testes iniciais, com IA desacoplada** | EEex, instalação, desempenho e portabilidade | **Aprovada** |
| DEC-003 | Plataforma | **Opção A: validar BG2:EE mínimo + EEex/bridge + multiplayer antes de EET/IWD/NWN, em builds reproduzíveis** | Ordem de mods, baselines, regressão | **Aprovada** |
| DEC-004 | Jogabilidade e narrativa | **Opção C: modo Original + Living World separados, com história individual dos personagens alimentando eventos por IA** | Isolamento de saves, origens, eventos personalizados | **Aprovada** |
| DEC-005 | Regras e combate | **Regras e encontros aprovados:** R = AD&D 2e com módulos; E = diretor regional adaptativo; T = turnos opcionais como objetivo, ainda bloqueados por teste | Multiplayer, EEex, GemRB-TBC, EET e compatibilidade temporal | **Aprovada como arquitetura; implementação T bloqueada por teste** |
| DEC-005-T | Modalidade de combate | **Opção B escolhida: modo clássico preservado e turnos individuais opcionais, se viáveis** | ADR-0017, auditoria 21, POCs G1–G4 | **Aprovada como objetivo; bloqueada por teste para implementação** |
| DEC-005-R | Edição das regras | **Opção B aprovada: AD&D 2e do BG2:EE como núcleo, com modernizações opcionais, versionadas e isoladas (ADR-0018)** | Compatibilidade mecânica, módulos, saves e multiplayer | **Aprovada; módulos específicos pendentes de SPECS** |
| DEC-005-E | Encontros | **Opção B aprovada: diretor adaptativo por regras, respeitando ecologia, faixas de risco e ameaças próprias da região (ADR-0019)** | DEC-005-R, DEC-011, DEC-014, DEC-009/023 e estado regional | **Aprovada; métricas e listas para SPECS** |
| DEC-006 | IA | Runtime local-first, remote só com opt-in/contexto filtrado/teto de custo (Q06=B; ADR-0106) | Infraestrutura, privacidade, performance | **Aprovada como política; benchmark pendente** |
| DEC-007 | Diálogos | Overlay/janela externa; texto sempre; voz push-to-talk bidirecional STT/TTS opcional, sem UI nativa presumida (Q07/20=B; ADR-0107) | EEex, sincronização, UX | **Aprovada como política; implementação pendente** |
| DEC-008 | Mundo e cronologia | **Opção C + adendo: estado/snapshots e log de eventos; cronologia oficial de Forgotten Realms alimenta repercussões por data, local e conhecimento** | DEC-009, DEC-011, DEC-014, DEC-019, DEC-021/022, DEC-018 | **Aprovada** |
| DEC-009 | Canon/cronologia | **Opção C: canon principal com divergências causais controladas, matriz entre períodos BG/IWD/NWN e repercussões da cronologia** | DEC-008, DEC-011, DEC-022; revisão de fontes/expansões | **Aprovada** |
| DEC-010 | Conteúdo | **Opção C: mundo curado + geração procedural validada; novos mapas/masmorras preferencialmente pré-gerados e testados; geração ao vivo condicionada a POCs (ADR-0020)** | DEC-003/008/009/011/014/017, recursos, mods, persistência e segurança | **Aprovada como arquitetura; geração dinâmica de áreas não comprovada** |
| DEC-027 | Conteúdo / governança | **Opção C: autonomia por níveis de risco (LOW narrativo automático validado; MEDIUM com regras e receipts mecânicos do host; HIGH com autorização especial e bloqueio por padrão sem política)** — ADR-0021 | DEC-010/011/012/014/019/021/022/024/025/026, persistência e segurança | **Aprovada; gateway DEC-012 aprovado, detalhes de HIGH ainda em SPECS** |
| DEC-011 | Multiplayer e arquitetura | **Opção A: autoridade dividida — host confirma estado mecânico; Infinity AI confirma fatos narrativos após evidências; IA propõe e bridge valida/reconcilia** | Segurança, consistência, eventos, anti-duplicação | **Aprovada** |
| DEC-012 | Segurança | **Opção B: Action Gateway com allowlist de operações tipadas, política default-deny, escopo por sessão/campanha, autorização por risco e receipts do host (ADR-0022)** | Segurança Lua/EEex, idempotência, isolamento, logs e POCs multiplayer | **Aprovada; implementação condicionada a SPECS/POCs** |
| DEC-028 | Conhecimento/segredos | **Opção B: memória compartilhada com ACL de leitura e recuperação/contexto filtrado antes do LLM, por destinatário, finalidade, proveniência e tempo (ADR-0023)** | DEC-019/020, DEC-008/009/014/012/027, caches, prompts e logs | **Aprovada; implementação sujeita a SPECS/POCs** |
| DEC-029 | Conhecimento/comunicação | **Opção B: difusão por relações NPC/facção, rotas e tempo do mundo, com regras determinísticas, crenças/proveniência e controle de segredos (ADR-0024)** | DEC-028/019/008/009/014/021/022/027; cronologia e persistência | **Aprovada; algoritmos e parâmetros para SPECS** |
| DEC-030 | Reputação/percepção | **Opção B: fama, confiança, temor, hostilidade e respeito contextualizados por NPC, facção e região; verdade ≠ crença; preservar reputação BG2:EE (ADR-0025)** | DEC-029/028/008/009/014/027, direitos de leitura, eventos, saves e gateway | **Aprovada; métricas para SPECS** |
| DEC-031 | Facções e geopolítica | **Opção B + adendo: autonomia por objetivos/recursos e regras, incluindo as facções dos jogos e expansão do catálogo para todas as organizações do cânone FR, condicionadas à época/região/curadoria (ADR-0026)** | DEC-008/009/014/021/022/028/029/030/027/012/011; catálogo completo ainda não inventariado | **Aprovada; cobertura progressiva e simulação testável por SPECS** |
| DEC-032 | Facções/economia/conflitos | **Opção B: simulação hierárquica adaptativa por relevância; economia, política e forças agregadas, com detalhe local e benchmark de jogos de estratégia (ADR-0027)** | DEC-031/021/022/027/012/011; tempo, cânone, gateway e validação técnica | **Aprovada; fórmulas e integração dependem de SPECS/POCs** |
| DEC-033 | Conflitos militares / integração | **Opção B: simulação estratégica distante + encontros locais opcionais, com efeitos confirmados e proporcionais (ADR-0028)** | DEC-032/021/022/005-E/009/027/012/011; integração BG2:EE a comprovar | **Aprovada — POCs pendentes** |
| DEC-034 | Eventos históricos irreversíveis | **Opção C: autonomia controlada para efeitos limitados, proteção especial de fatos centrais do cânone, HIGH crítico default-deny salvo autorização expressa e delimitada (ADR-0029)** | DEC-009/027/011/012/033; detalhes de consentimento/UI e interceptação para SPECS | **Aprovada; políticas granulares/POCs pendentes** |
| DEC-035 | Evolução de personagens | **Adendo aprovado: alinhamento mutável nos dois eixos (Lawful–Chaotic; Good–Evil) por ações contextualizadas e confirmadas; distinto da reputação social (ADR-0030)** | DEC-005-R/011/012/030/034; mudança mecânica depende de POCs | **Aprovada como princípio; fórmula e classe pendentes** |
| DEC-036 | Avaliação do alinhamento | **Opção B aprovada: avaliação híbrida, contextual e gradual, com regras versionadas e auditáveis; IA local propõe interpretações, mas não decide/aplica efeitos mecânicos (ADR-0031)** | DEC-035/030/028/005-R/014/011/012; contexto, autoria e revisão | **Aprovada; critérios quantitativos e arbitragem para SPECS** |
| DEC-037 | Consequências mecânicas do alinhamento | **Opção B aprovada: consequências progressivas, com transições confirmadas, perfil de campanha, aviso e efeitos mecânicos somente após SPEC/POC + gateway + receipt do host (ADR-0032)** | DEC-035/036/005-R/011/012/030; BG2:EE/EEex, classes/kits, saves e multiplayer | **Aprovada; implementação mecânica bloqueada por testes** |
| DEC-038 | Redenção, juramentos e recuperação de poderes | **Opção B: jornadas personalizadas e opcionais de redenção/transformação, com agência e efeitos mecânicos apenas após regras/SPEC/POC/host (ADR-0033)** | DEC-004/010/035/036/037/005-R/011/012/028/030/034, cronologia, classe e multiplayer | **Aprovada; mecânicas condicionadas a testes** |
| DEC-039 | Arcos pessoais e missões de personagem | **Opção C: Personal Story Director híbrido, marcos verificáveis, contexto versionado, escolhas e desfechos alternativos (ADR-0034)** | DEC-004/008/009/010/011/012/014/020/025/027/028/030/034/035-038, canon, sigilo e save | **Aprovada; SPECS e POCs pendentes** |
| DEC-040 | Coordenação cooperativa dos arcos pessoais | **Opção B: Cooperative Story Director prioriza oportunidades significativas, integra histórias individuais/coletivas por escolha, sem rotação rígida e com segredos protegidos (ADR-0035)** | DEC-004/008/014/019/020/021/022/025/028/029/030/039; multiplayer, agência e ritmo | **Aprovada — SPECS/POCs pendentes** |
| DEC-041 | Consentimento e autoridade em decisões narrativas coletivas | **Opção C: autoridade distribuída, com agência do controlador de cada PC, consequências externas verificadas, segredos com proveniência e host administrando políticas (ADR-0036)** | DEC-004/019/020/028/034/039/040; gateway, multiplayer, autorização de risco | **Aprovada; SPECS/POCs pendentes** |
| DEC-042 | PvP e ações hostis entre PCs | **Opção C aprovada: PvP configurável por campanha, com permissões por categoria, limites e consentimento dos jogadores afetados (ADR-0037)** | DEC-001/011/012/028/034/041; proteção de ausentes, efeitos indiretos, save e multiplayer | **Aprovada como política; implementação condicionada a SPECS/POCs** |
| DEC-043 | Morte, ressurreição e permanência dos PCs | **Opção C aprovada: mortalidade e ressurreição configuráveis por campanha, com legado histórico persistente e morte definitiva condicionada à política e evidência mecânica (ADR-0038)** | DEC-005-R/008/011/012/028/029/030/034–042; regras reais, consentimento PvP, saves, game-over e multiplayer | **Aprovada como arquitetura; SPECS/POCs pendentes** |
| DEC-044 | Sucessão de personagens e continuidade do grupo | **Opção C aprovada: entrada contextual com identidade nova, progressão inicial equilibrada por campanha e herança comprovadamente legítima (ADR-0039)** | DEC-004/008/011/012/019/020/028/030/039/040/041/042/043; party multiplayer, itens, XP, slots e saves | **Aprovada como arquitetura; SPECS/POCs pendentes** |
| DEC-045 | Ausências, desconexão e retomada da sessão | **Aprovada: modelo BG3 — PCs de jogador ausente podem ser atribuídos a outro jogador presente, que controla vários personagens, mantendo identidade e titularidade separadas (ADR-0040)** | DEC-001/003/011/012/040/041/042/043/044; Character Arbitration BG2:EE documentada; POC de 2 clientes e save/load pendente | **Aprovada — integração automatizada bloqueada por teste** |
| DEC-046 | Limites da delegação de controle | **Opção C aprovada: o titular autoriza previamente categorias específicas de controle temporário, com validade/revogação, limites por risco, PvP/cânone e conhecimento; não herda autorização apenas por atribuir slot (ADR-0041)** | DEC-019/020/027/028/034/041/042/043/045; owner/controller, motor, gateway, POCs | **Aprovada como política — veto granular condicionado a testes** |
| DEC-047 | Autonomia narrativa dos companions NPC recrutáveis | **Opção C: controle tático dos companheiros pelos jogadores, com identidade, memória, relações e autonomia narrativa contextual dos NPCs; alterações mecânicas apenas via gateway/host (ADR-0042)** | DEC-004/009/011/014/028/030/039–041/046; conteúdo canônico BG2:EE, scripts, multiplayer | **Aprovada — integração dependente de SPECS/POCs** |
| DEC-048 | Desacordos, limites e ruptura de companions NPCs | **Opção B: avaliação contextual e gradual, com negociação e possibilidade de saída; ato excepcionalmente grave pode justificar ruptura imediata (ADR-0043)** | DEC-011/012/014/027/028/030/034/047; scripts nativos, host, multiplayer e POCs | **Aprovada — implementação condicionada a SPECS/POCs** |
| DEC-049 | Vida de NPCs após saída da party | **Opção B aprovada: vida autônoma persistente, agenda/simulação hierárquica, reencontros contextuais e re-recrutamento condicionado a regras/host (ADR-0044)** | DEC-021/022/030/031/047/048/008/009/011/012; scripts, cronologia, persistência e multiplayer | **Aprovada — mecânica condicionada a SPECS/POCs** |
| DEC-050 | Conflitos entre conteúdo nativo e eventos dinâmicos de NPCs | **Opção C: conciliação híbrida com scripts/quests/romances protegidos, propostas adaptadas, adiadas ou bloqueadas; divergências causais sob revisão e gateway (ADR-0045)** | DEC-009/024/025/034/047/048/049; versão de mods, observação de flags, host, SPECS/POCs | **Aprovada; implementação bloqueada por testes** |
| DEC-051 | Inventário e proveniência do conteúdo instalado | **Opção C: inventário automatizado somente leitura, curadoria/versionamento por build/mod e confiança explícita; runtime não inferido de arquivos estáticos (ADR-0046)** | DEC-003/011/012/050; versões, ordem, cobertura, reconciliação, segurança | **Aprovada — SPECS/POCs pendentes** |
| DEC-052 | Evolução de builds e migração de campanhas persistentes | **Opção C: build pinada por campanha e migração controlada entre instalações isoladas, com backups, gates, aprovação do host/anfitrião e restauração de estado coerente (ADR-0047)** | DEC-003/008/011/012/013/015/018/050/051; saves, scripts, multiplayer, rollback, licenças | **Aprovada — migração real condicionada a SPECS/POCs** |
| DEC-053 | Coordenação de checkpoints de save mecânico e estado narrativo externo | **Opção C: checkpoints vinculados e publicados somente após verificação de save + snapshot/event log; restauração de par coerente, idempotência, ramificação de rewind e reconciliação de `UNCERTAIN` (ADR-0048)** | DEC-008/011/012/018/022/052; integridade, recuperação, segredos, save/load e multiplayer | **Aprovada — integração com motor depende de SPECS/POCs** |
| DEC-054 | Backup, retenção e recuperação operacional | **Opção C: backups automáticos de checkpoints certificados, rotação e retenção versionadas, cópia independente opcional e ensaios periódicos de restauração (ADR-0049)** | DEC-018/053/052/028; redundância consentida, criptografia e restauração não destrutiva | **Aprovada — política; implementação condicionada a SPECS/POCs** |
| DEC-055 | Observabilidade e resposta a incidentes | **Opção C: World Health Monitor local-first; falhas por capacidade, fallback verificado, alertas privados, recuperação LOW allowlisted e bloqueio de `UNCERTAIN`/HIGH (ADR-0050)** | DEC-011/012/014/018/028/053/054; segurança, gateway, IA local, multiplayer, backups | **Aprovada — monitoramento efetivo depende de SPECS/POCs** |
| DEC-056 | Desempenho e qualidade de serviço | **Opção C: Resource & Performance Director com admissão, prioridades P0–P4, filas, backpressure e budgets adaptativos; jogo e integridade prevalecem (ADR-0051)** | DEC-014/021/032/055/006/011/015; CPU, GPU, RAM, I/O, filas e latência | **Aprovada — benchmarks e implementação pendentes** |
| DEC-057 | Implantação e topologia da IA local | **Opção C: serviços modulares local-first, sidecars no host Windows e execução LAN opcional de workers; nenhuma transferência de autoridade do BG2:EE (ADR-0052)** | DEC-002/003/006/011/012/014/028/053/055/056; identidade, ACL, rede e desempenho | **Aprovada — SPECS/POCs de implantação pendentes** |
| DEC-058 | Segurança de nós e comunicação LAN | **Opção C: descoberta assistida, pareamento explicitamente aprovado, identidade verificável, canal protegido, mínimo privilégio e revogação (ADR-0053)** | DEC-012/028/041/053/055/057; privacidade, sessão, antirreplay e contenção | **Aprovada — protocolos/implementação sujeitos a SPECS/POCs** |
| DEC-059 | Roteamento de tarefas e modelos locais | **Opção C: AI Model Router por tarefa, sensibilidade, autorização e capacidade aferida; ranking por recursos/latência entre elegíveis; fallback seguro sem nuvem implícita (ADR-0054)** | DEC-006/011/012/014/028/053/055/056/057/058; jobs rev-bound e ACL | **Aprovada — SPECS/POCs pendentes** |
| DEC-060 | Confiabilidade de conteúdo gerado por modelos e isolamento temporal | **Opção C + adendo: validação híbrida por risco/evidência e corpus canônico fisicamente separado por ano DR, com busca primária por ano e história anterior somente sob critérios de vigência e ACL (ADR-0055)** | DEC-008/009/012/014/015/022/028/029/050/059; conhecimento de NPC, diretórios anuais e overlays isolados | **Aprovada — emendada na v5.6.1; implementação pendente** |
| DEC-061 | Governança de fontes e conflitos no mesmo período | **Opção C aprovada: preservar alegações com proveniência, classificar diferenças por data/região/perspectiva/retcon, manter conflitos não resolvidos e exigir resolução curada contextual e auditável (ADR-0056); sem desfazer diretórios físicos anuais DEC-060** | DEC-008/009/015/028/029/060; ano, fonte, ACL e ramo | **Aprovada — não implementada** |
| DEC-062 | Curadoria/ingestão de novas fontes | **Opção C aprovada: pipeline híbrido com fontes autorizadas, staging separado, extração IA como proposta, validação/curadoria e promoção versionada somente por ano DR; novos fatos requerem revisão humana inicial e casos LOW podem seguir allowlist curada futura (ADR-0057)** | DEC-060/061/015/017/028/051/056/059; direitos, ano, evidência, auditoria | **Aprovada — não implementada** |
| DEC-063 | Vinculação de revisões do cânone a campanhas ativas | **Opção C aprovada: Knowledge Packs são manifestos por revisões de diretórios anuais, pinados por campanha/ramo; atualizações seletivas por diff/impacto, checkpoint, aprovação do host e recuperação controlada (ADR-0058)** | DEC-008/009/011/028/029/052/053/054/060/061/062; source/branch/clock/build/ACL | **Aprovada — SPECS/POCs pendentes** |
| DEC-064 | Crenças individuais e memória episódica dos NPCs | **Opção C aprovada: preservar experiências, adquirir informação por canais legítimos e revisar crenças por evidência/contexto sem reescrever memória, cânone ou história confirmada (ADR-0059)** | DEC-028/029/030/060/061/062/063; rumor, ACL, provenance, memória, branch | **Aprovada — SPECS/POCs pendentes** |
| DEC-065 | Memória hierárquica, consolidação e recuperação contextual | **Opção C aprovada:** memória imediata, episódica, consolidada e âncoras críticas; resumos derivados com fontes, recuperação por relevância/ACL/branch e nenhuma exclusão automática de eventos por tempo (ADR-0060) | DEC-021/022/028/029/053/054/056/060–064; memória, retenção, privacidade e desempenho | **Aprovada — SPECS/POCs pendentes** |
| DEC-066 | Identidade persistente de NPCs através de saves, áreas e builds | **Opção C aprovada:** identidade lógica por campanha/ramo + observação runtime separada; correspondência comprovada, ambiguidade e revisões incompatíveis bloqueiam memória privada (ADR-0061) | DEC-011/012/028/049/050/051/052/053/060–065; provas, branch, build e ACL | **Aprovada — SPECS/POCs pendentes** |
| DEC-067 | Individualização progressiva de NPCs | **Opção C aprovada:** priorizar únicos/companheiros; genéricos agregados/efêmeros podem ser promovidos por acontecimentos relevantes, identidade verificada DEC-066, autorização por risco e quotas (ADR-0062) | DEC-021/022/049/056/060–066; custos, clones, dupla contagem e privacidade | **Aprovada — SPECS/POCs pendentes** |
| DEC-068 | Vida persistente de NPCs fora de cena | **Opção C aprovada:** atividade ACTIVE/NEAR/DISTANT/DORMANT, hibernação sem apagar memória, catch-up delimitado e retomada reconciliada (ADR-0063) | DEC-021/022/049/053/056/060–067; identidade, clock, host, filas e privacidade | **Aprovada — SPECS/POCs pendentes** |
| DEC-069 | Viagens e continuidade espacial de NPCs entre regiões | **Opção C aprovada:** itinerários por etapas, grafo geográfico temporal curado, restrições e tempo verificáveis, presença narrativa separada da observação mecânica do host (ADR-0064) | DEC-021/022/049/050/056/060–068; rotas, scripts, KPack, identidade e host | **Aprovada — SPECS/POCs de movimento e multiplayer pendentes** |
| DEC-070 | Encontros e incidentes durante viagens de NPCs fora de cena | **Opção C aprovada:** propostas de incidente com evidências, LOW somente allowlisted/idempotente narrativo, MEDIUM por gate e HIGH fail-closed; resultados mecânicos só com host receipt (ADR-0065) | DEC-005-E/011/012/021/022/027/034/050/056/060–069; risco, consentimento, itinerário, privacidade e host | **Aprovada — SPECS/POCs pendentes** |
| DEC-071 | Transição de incidentes de rota para encontros em cena | **Opção C aprovada:** handoff seletivo por compatibilidade/risco/host, reserva durável que impede resolução dupla offscreen/local e receipt mecânico obrigatório (ADR-0066) | DEC-005-E/011/012/027/033/050/051/053/060–070; build, área, identidade, ledger, multiplayer | **Aprovada — SPECS/POCs pendentes** |
| DEC-072 | Catálogo e composição segura de encontros jogáveis | **Opção C aprovada:** templates/componentes/adapters curados por build, provenance/licenças/capabilities verificadas, preparação offline e expansão controlada; nenhum runtime codegen/spawn presumido (ADR-0067) | DEC-003/005-E/010/011/012/015/017/023/024/050/051/070/071; build/mods/rights/multiplayer | **Aprovada — SPECS/POCs pendentes** |
| DEC-073 | Ciclo de vida, limpeza e persistência pós-encontro | **Opção C aprovada:** ownership verificado por instância, persistência seletiva de consequências confirmadas, limpeza somente de temporários comprovados por adapter/host receipt; `UNCERTAIN` bloqueia remoção (ADR-0068) | DEC-011/012/027/050/051/052/053/054/060–072; ownership, risco, save/load, multiplayer | **Aprovada — SPECS/POCs pendentes** |
| DEC-074 | Repercussão causal dos encontros no Living World | **Opção C aprovada:** evento confirmado → testemunhos/notícias → crenças → efeitos proporcionais em relações, reputação, facções e economia; tempos, ACL, risco e ledger idempotente (ADR-0069) | DEC-011/027/028/029/030/032/033/053/060–073; causa, canais, host e SPECS/POCs | **Aprovada — SPECS/POCs pendentes** |
| DEC-075 | Crédito e responsabilidade por feitos em cooperativo | **Opção C aprovada:** atribuição causal contextual por evidências, autoria individual/coletiva, papéis de suporte, relatos e percepção social; sem confundir reconhecimento com verdade, nem efeitos mecânicos sem host (ADR-0070) | DEC-011/027/029/030/041/045/046/060–074; ACL, idempotência, identidade e recibos | **Aprovada — não implementada; SPECS/POCs pendentes** |
| DEC-076 | Identidade factual privada, pseudônimos e reconhecimento contextual | **Opção C aprovada:** persona pública separada de ator privado; suspeitas e ligações factuais só por evidência; divulgação por audiência autorizada, ACL, consentimento e canal, sem presumir disfarce mecânico (ADR-0071) | DEC-019/028/029/030/041/045/046/060–075; segredos, reputação, engine, coop e evidências | **Aprovada — não implementada; SPECS/POCs pendentes** |
| DEC-077 | Investigação e contestação de identidades secretas | **Opção C aprovada:** ledger de pistas com proveniência, contradições e independência de fontes; suspeita não vira fato; vínculo privado e divulgação têm gates distintos (ADR-0072) | DEC-019/028/029/041/060–076; segredos, investigação, direitos do PC, risco e evidências | **Aprovada — não implementada; SPECS/POCs pendentes** |
| DEC-078 | Acusações e decisões por autoridades ou facções | **Opção C aprovada:** procedimentos por jurisdição/ano/autoridade curados, alegação ≠ fato ≠ decisão oficial ≠ efeito mecânico; contestação contextual, risco, autorizações e receipt do host (ADR-0073) | DEC-011/012/027/030/031/034/041/042/060–077; fontes, privacidade, gateway, multiplayer | **Aprovada — SPECS/POCs pendentes; não implementada** |
| DEC-079 | Reconhecimento de mandados e conflitos de jurisdição entre regiões | **Opção C aprovada:** pedidos transmitidos por canais/tempo verificáveis, autoridade e competência por ano DR, avaliação/aceite/recusa/contestação no destinatário, gates de risco e host para qualquer efeito mecânico (ADR-0074) | DEC-011/012/022/027/029/030/031/034/041/060–078; rotas, sigilo, KPack, casos, autoridade e host | **Aprovada — não implementada; SPECS/POCs pendentes** |
| DEC-080 | Revogações e mandados desatualizados | **Opção C aprovada:** ordem versionada, transmissão causal de correções, estado autoritativo distinto de crença local, verificação de vigência e fail-closed de coerção incerta; sem rollback automático (ADR-0075) | DEC-011/012/022/027/029/053/060–079; autenticidade, revisão, consentimento, risco, host e idempotência | **Aprovada — SPECS/POCs pendentes** |
| DEC-081 | Reparação e revisão de danos jurídicos indevidos | **Opção C aprovada:** prova de dano/nexo, autoridade por região/ano, pedido de restituição/reabilitação contextual, consentimento, dedup e host receipt para efeitos mecânicos; sem rollback universal (ADR-0076) | DEC-011/012/027/034/041/050/053/054/060–080; direitos, causalidade, competência e idempotência | **Aprovada — não implementada; SPECS/POCs pendentes** |
| DEC-082 | Fiscalização e responsabilização de agentes/instituições | **Opção C aprovada:** investigação contextual com provas e competência por ano/região; distinguir agente, superior e prática institucional; contestação, gates de risco e host para efeitos mecânicos (ADR-0077) | DEC-011/012/027/029–034/041/060–081; acusações, cadeia de comando, consentimento e idempotência | **Aprovada como arquitetura — SPECS/POCs pendentes** |
| DEC-083 | Proteção de denunciantes, testemunhas e fontes | **Opção C aprovada:** identidade factual selada, depoimento e provas separados; ACL contextual por finalidade/audiência, consentimento, risco, proveniência, revelação idempotente e sem invulnerabilidade presumida (ADR-0078) | DEC-019/027/028/029/041/045/046/060–082; competência, testemunhas, sigilo e host | **Aprovada como arquitetura — SPECS/POCs pendentes** |
| DEC-084 | Proteção ativa de fontes sob ameaça | **Opção C aprovada:** avaliar ameaças por provas e risco; propor discrição, abrigo, ajuda, escolta ou realocação somente com consentimento, meios e tempo, sem invulnerabilidade, teleporte ou efeito mecânico presumido (ADR-0079) | DEC-011/012/019/022/027/028/034/041/056/066/068–083; capacidade host, incidentes, proteção e ACL | **Aprovada — não implementada; SPECS/POCs pendentes** |
| DEC-085 | Sigilo operacional e descoberta contextual de planos de proteção | **Opção C aprovada:** acesso compartmentalizado, vazamento/descoberta parcial por evidência, canal, horário e ACL; replanejamento autorizado, sem onisciência, ataques automáticos ou engine presumida (ADR-0080) | DEC-019/027/028/029/041/053/056/057–060/063–084; privacidade, adversários, recursos e causação | **Aprovada — arquitetura, não implementada; SPECS/POCs pendentes** |
| DEC-086 | Engano defensivo, desinformação e iscas de contraespionagem | **Opção C aprovada:** operações de isca com autoria, consentimento, recursos e proveniência; claim plantado distinto de fato confirmado, propagação causal, crença falível e gates de risco (ADR-0081) | DEC-011/012/019/022/027/028/041/042/061/064/074/076–085; segurança, segredo, reputação e motor | **Aprovada somente como arquitetura; SPECS/POCs pendentes** |
| DEC-087 | Agentes duplos, fontes comprometidas e conflitos de lealdade | **Opção C aprovada:** múltiplos vínculos contextuais; mudanças por eventos, valores e provas, agência PC e autonomia NPC; crença/suspeita diferente de compromisso/ato factual; gates e host (ADR-0082) | DEC-019/027/028/041/042/047/048/061/064–086; confiança, privacidade, canonicidade, recursos | **Aprovada como arquitetura — SPECS/POCs pendentes** |
| DEC-088 | Recrutamento e gestão de informantes voluntários | **Opção C aprovada:** contatos, propostas, contrapropostas, consentimento, acordo contextual versionado, custos reservados, segredos, entregas verificadas separadas de promessas, recusa/saída e gates; ADR-0083 | DEC-011/012/019/027/028/032/041/045–049/060–087; recursos, privacidade, NPC e coop | **Aprovada como arquitetura; SPECS/POCs pendentes** |
| DEC-089 | Credibilidade, veracidade e contradições dos informes recebidos | **Opção C aprovada:** avaliação por origem, acesso epistêmico, famílias de evidências independentes, contradição, perfis por contexto, ACL, revisão e risco; ADR-0084 | DEC-019/028/061/064/074/077/083–088; informes ≠ fato, evidência e consentimento | **Aprovada como arquitetura; não implementada; SPECS/POCs pendentes** |
| DEC-090 | Dossiês de inteligência e compartilhamento seletivo | **Opção C aprovada:** compilar alegações verificáveis com incerteza e proveniência; revisões imutáveis, views sanitizadas por destinatário, ACL por campo, consentimento, transmissão/recibos e correções causais (ADR-0085) | DEC-019/028/029/041/061/064/074/076/077/083–089; privacidade, jurisdição, RPG multiplayer e difusão | **Aprovada como arquitetura; não implementada; SPECS/POCs pendentes** |
| DEC-091 | Planejamento operacional contextual com inteligência incerta | **Opção C aprovada:** planos tipados derivados de alegações/contradições com validação de fonte, recursos, tempo, consentimento e risco; planejamento ≠ autorização ≠ reserva ≠ execução/receipt, com Action Gateway e host (ADR-0086) | DEC-011/012/019/022/027/028/034/041/053/060–090; confiabilidade, ACL, agência, recursos e multiplayer | **Aprovada como arquitetura; não implementada; SPECS/POCs pendentes** |
| DEC-092 | Monitoramento e replanejamento de operações em andamento | **Opção C aprovada:** eventos confirmados, diff de impacto, pausa lógica, aborto seguro e nova revisão/reautorização material; sem pressupor pausa de engine ou rollback (ADR-0087) | DEC-011/012/022/027/041/053/056/068–074/089–091; autorização, privacidade, recursos e host receipts | **Aprovada como arquitetura; não implementada; SPECS/POCs pendentes** |
| DEC-093 | Coordenação de operações simultâneas e contenção de recursos | **Opção C aprovada:** scheduler determinístico com operações independentes paralelas, reservas por recurso/tempo, CAS/fencing, detecção de conflitos, fairness, agência PC e receipt host; sem presumir transação com BG2:EE (ADR-0088) | DEC-011/012/027/041/051/053/056/068–074/091/092; concorrência, agência e recursos | **Aprovada como arquitetura; não implementada; SPECS/POCs pendentes** |
| DEC-094 | Resolução segura de deadlocks, starvation e reservas órfãs | **Opção C aprovada:** ciclos versionados, fairness, provas de revogabilidade, CAS/fencing, quarentena de in-flight, consentimento e conciliação com host (ADR-0089) | DEC-011/012/027/041/053/056/071/091–093; wait-for graph e efeitos in-flight | **Aprovada como arquitetura; não implementada; SPECS/POCs pendentes** |
| DEC-095 | Compensação segura de operações parcialmente concluídas | **Opção C aprovada:** Sagas versionadas com passos confirmados, compensações como novos atos, recursos/consentimento, idempotência, estados incertos e receipts host; nenhum rollback global (ADR-0090) | DEC-011/012/027/041/050–054/060–063/081/091–094; efeitos parciais, Saga e reconciliação | **Aprovada como arquitetura; NÃO implementada; POCs pendentes** |
| DEC-096 | Matriz cronológica condicional de eventos e repercussões por ano/mês DR, geografia e tipo de local | **Opção C aprovada:** catálogo canônico particionado por ano DR + rulesets declarativos versionados + avaliação determinística de tempo/fase/local/branch + propostas/ledger causal, pai confirmado para indiretos, gates e LLM só para texto (ADR-0091, tech 96) | DEC-008/009/021–026/028–034/060–063/068–074/091–095; fonte, precisão, regiões, engine/host | **Aprovada como arquitetura; NÃO implementada; POCs pendentes** |
| DEC-097 | Composição de efeitos históricos simultâneos em regiões e estabelecimentos | **Opção C aprovada:** composição por métrica/domínio tipado, famílias de stacking e precedência; caps, duração/decaimento, idempotência, trilha causal; host-confirmed separa projeção de aplicação (ADR-0092, técnico 97) | DEC-022/027/056/060–063/074/093–096; economia, risco, cronologia e recibos do host | **Aprovada como arquitetura; NÃO implementada; POCs pendentes** |
| DEC-098 | Materialização incremental de repercussões em regiões e locais | **Opção C aprovada:** snapshot regional host-confirmed, diff por identidade/ownership, observação suficiente, gates e recibos, offscreen/catch-up limitado e idempotência (ADR-0093, doc 98) | DEC-021/022/053/056/060–074/091–097; save/load, mod/quest e host+2 clientes | **Aprovada como arquitetura; NÃO implementada; POCs pendentes** |
| DEC-099 | Ownership e compatibilidade de scripts originais, quests e mods | **Opção C aprovada:** ownership por instância e campo; fonte, custódia, consentimento, capacidade por build/modpack, precedência estreita e reconciliação; UNKNOWN/quest/mod/PC preservado por padrão | ADR-0094; doc. 99; DEC-050/051/052/066/073/096–098 | **APROVADA — arquitetura (2026-11-07)** |
| DEC-100 | Observação segura de quests, scripts e estados internos do BG2:EE/EEex | **Opção C aprovada:** probes read-only e allowlisted por build/modpack/adapter, ACL por finalidade/audiência, cobertura explícita, minimização, proteção de spoilers e separação estado técnico/conhecimento narrativo | ADR-0095, doc. 100; DEC-011/012/028/050/051/052/055/059/083/090/098/099 | **APROVADA — arquitetura (2026-11-07)** |
| DEC-101 | Mapeamento semântico curado de estados técnicos de quests | **Opção C aprovada:** catálogo curado e pinado por build/modpack/script, predicados tipados, transições causais verificáveis, marcos exclusivos, `UNKNOWN`/`AMBIGUOUS`, divulgação mínima segregada de leitura | ADR-0096, doc. 101; DEC-050/051/052/099/100, ACL e spoilers | **APROVADA — arquitetura (2026-11-07); POCs pendentes** |
| DEC-102 | Reconciliação de marcos de quests do host versus overlay persistente | **Opção C aprovada:** evidências semânticas verificadas DEC-100/101, epochs, snapshots, receipts e lineage; propor apenas revisão de projeções derivadas por CAS/autorização; nunca reescrever host/fatos/segredos | ADR-0097, doc. 102; DEC-011/012/050/053/060–063/098–101 | **APROVADA — arquitetura (2026-11-07), POCs pendentes** |
| DEC-103 | Admissão e propagação causal de marcos de quests reconciliados | **Opção C aprovada:** prova DEC-100/101, reconciliação committed DEC-102, ledger/outbox idempotente, matriz temporal/espacial e ruleset pinado, ACL/privacidade; propostas separadas de receipts mecânicos e de entregas de notícias (ADR-0098, doc. 103) | DEC-011/012/028/029/050/074/090/096–102; host authority, conhecimento contextual | **APROVADA — arquitetura (2026-11-07), POCs pendentes** |
| DEC-104 | Retificação causal e contenção de repercussões de quests | **Opção C aprovada:** grafo causal, prova curada committed, contenção de despachos futuros, revisão CAS, reconciliação de `DISPATCHED/UNCERTAIN`, compensação via Saga DEC-095 e correção de notícia sem apagar fatos host-confirmed ou conhecimento de NPCs (ADR-0099/doc. 104) | DEC-011/012/028/029/053/064/074/083/090/095–103 | **APROVADA — arquitetura (2026-11-07), POCs pendentes** |
| DEC-105 | Correção causal de rumores e revisão gradual das crenças | **Opção C APROVADA:** retificação committed como nova comunicação, canais e tempo DR, ACL por destinatário, recibos independentes de entrega/percepção, memória preservada, crenças falíveis, revisão versionada sem aceitar automaticamente (ADR-0100, doc. 105) | DEC-028/029/030/064/065/076/083–090/095/103/104; host/campaign/branch | **APROVADA — arquitetura (2026-11-07), POCs pendentes** |
| DEC-106 | Reabilitação reputacional proporcional após acusações comprovadamente incorretas | **Opção C APROVADA:** reputação contextual por público/relação/região, retificação committed, exposição e percepção reais, danos comprovados versus alegados, oportunidades voluntárias de esclarecimento/reengajamento, reparações separadas DEC-081/095, consentimento e host gates (ADR-0101; doc. 106) | DEC-030/064–065/075/077–083/089/095/104/105; ACL, prova e autonomia | **APROVADA — arquitetura (2026-11-07), POCs pendentes** |
| DEC-107 | Direito de resposta e mediação reputacional voluntária | **Opção C APROVADA:** contraditório facultativo, aviso/entrega/percepção/réplica separados, provas curadas e contestáveis, mandato de partes e facilitador imparcial, ACL e consentimento por termo; sem culpa, retratação, perdão ou efeitos mecânicos automáticos (ADR-0102; doc.107) | DEC-030/041–046/064–065/075–090/095/104–106 | **APROVADA — arquitetura (2026-11-07), POCs pendentes** |
| DEC-108 | Cumprimento verificável de acordos e fiscalização não coercitiva | **Opção C APROVADA:** termos committed, prazos DR, claims distintos de host receipts, prestações parciais, saldos não comprovados, contraditório e renegociação com novo aceite; sem inadimplência, sanção, reputação ou transferência automática (ADR-0103; doc.108) | DEC-011/012/022/030/041–046/053/077–082/091–095/099/104–107 | **APROVADA — arquitetura (2026-11-07), POCs pendentes** |
| DEC-109 | Grafo de obrigações condicionais e acordos multipartes | **Opção C APROVADA:** DAG versionado, condições `CONFIRMED_COMPLETE/AT_LEAST` e `ALL/ANY/AT_LEAST(k)` somente curadas, provas host-confirmed, resource fencing, DR, idempotência, autorização por termo e bloqueio de ciclos; condição satisfeita **não** despacha operação (ADR-0104; doc.109) | DEC-011/012/022/041–046/053/077–083/091–095/099/107/108 | **APROVADA — arquitetura (2026-11-07), POCs pendentes** |
| DEC-110 | Garantias e custódia condicional de recursos (*escrow*) | **DEC-110/C APROVADA:** custódia mecânica só após transferência host-confirmed por capability validada e consentimento do titular; liberação condicionada elegível para revisão, nunca automática; sem capability apenas narrativa rotulada | DEC-011/012/041–046/053/081/093–095/099/107–109; ADR-0105; doc 110 | **APROVADA — arquitetura; POCs pendentes** |
| DEC-111 | Governança de SPECS e desenvolvimento | Constitution e SPECs numeradas, change requests, revisão por PR e rastreabilidade (Q12=B; ADR-0111) | DEC-013/015/018 e SDD docs/01; questionário 111; handoff 112 | **Aprovada como política SDD** |
| DEC-013 | Compatibilidade | Build/hash/modlist fixos, BG2:EE limpo → EEex → bridge; expansões após POC (Q02/21=B; ADR-0108) | EET, IWD-EET, NWNForBG, EEex | **Aprovada como política; POCs pendentes** |
| DEC-014 | IA/NPCs | **Opção C com adendos: orquestrador central + especialistas sob demanda; código/regras primeiro, LLM local preferencial; sem modelo dedicado por NPC** | DEC-011, DEC-006, DEC-008, DEC-012 | **Aprovada** |
| DEC-015 | Testes | Gates P0–P4, evidências e rollback, host+2 clientes, save/load (Q03/05/11/28; ADR-0108) | Aceitação por feature | **Aprovada como política; POCs pendentes** |
| DEC-016 | UX | UX externa até UI nativa segura; voice PTT/STT/TTS opt-in, fallback texto e ACL (Q07/20/26; ADR-0107) | Diálogos, multiplayer | **Aprovada como política; POCs pendentes** |
| DEC-017 | Conteúdo | Instalação legítima local, sem redistribuir assets; manifesto/licenças; recorte BG2:EE (Q14/16; ADR-0109) | Licenças, distribuição de mods | **Aprovada como política; inventário pendente** |
| DEC-018 | Operação | SQLite + eventos append-only + snapshots/epochs, logs redigidos, LAN autenticada e replay (Q08/10/15/24/25/26; ADR-0110) | Estado persistente e integridade | **Aprovada como política; implementação pendente** |
| DEC-019 | Narrativa/personagens | **Opção C: históricos híbridos; autor controla o que é público ou secreto, NPCs têm conhecimento próprio justificado** | Política de acesso, prompts e memória, vazamento de informações | **Aprovada** |
| DEC-020 | Narrativa/personagens | **Opção C: histórico versionado e editável; IA sinaliza conflitos e sugere ajustes; fatos confirmados preservados até aprovação explícita** | Versionamento, canon, persistência e autoria | **Aprovada** |
| DEC-021 | Simulação/NPCs | **Opção C: simulação por níveis ACTIVE, NEAR, DISTANT e DORMANT, código primeiro, catch-up limitado e sem inferência contínua** | DEC-014, DEC-011, DEC-008, DEC-009; relógio DEC-022 (aprovada) | **Aprovada** |
| DEC-022 | Tempo/campanha | **Opção C: tempo híbrido configurável FROZEN/PARTIAL/REALTIME, catch-up delimitado na retomada e proteção de eventos irreversíveis** | DEC-021, DEC-011, DEC-008, DEC-009 | **Aprovada** |
| DEC-023 | Cronologia / calendário | **Opção C aprovada: época configurável; 1369 DR é referência dos primeiros testes por menor impacto estimado no BG2:EE/EET, 1370 concorrente, sujeito a inventário de recursos** | DEC-009, DEC-003, ADR-0013, matriz 16 | **Aprovada** |
| DEC-024 | Conteúdo e cronologia | **Opção C com adendo: legado histórico para campanhas anteriores + arcos contemporâneos paralelos opcionais; PCs podem encontrar/ajudar NPCs clássicos sem assumir protagonistas originais** | Isolamento de flags/scripts, DEC-009, DEC-023, DEC-011, eventos confirmados | **Aprovada** |
| DEC-025 | Simulação narrativa | **Opção C: progressão por calendário e condições, janelas opcionais, proteção de marcos críticos e divergências rastreáveis** | DEC-021/022, DEC-024, DEC-009, DEC-011 | **Aprovada** |
| DEC-026 | Participação do grupo | **Opção C: N1 interação, N2 apoio e N3 intervenções causais com consequências reais; marcos críticos protegidos** | DEC-025/009/024/011; política detalhada de aprovação ainda aberta | **Aprovada** |

## Roteiro de entrevistas proposto

1. Visão e experiência de jogo: DEC-001, DEC-004, DEC-019 e DEC-020 (**aprovadas**).
2. Ambiente técnico e versões: DEC-002 e DEC-003 (**aprovadas**), DEC-013 (em aberto).
3. Regras e simulação do mundo: **DEC-005-E (aprovada)**; **DEC-010 (aprovada); DEC-027 (aprovada)**, DEC-008, DEC-009, DEC-014 (**aprovada**), DEC-020 (**aprovada**) e DEC-021 (**aprovada**); DEC-022 (**aprovada**).
4. Agentes IA e interface: DEC-006 (**restrita pela diretriz local-first já aprovada**), DEC-007, DEC-016.
5. Conteúdo, geração e expansão: DEC-010 (**aprovada**), DEC-027 (**aprovada**), DEC-012 (**aprovada**), DEC-028 (**aprovada**), DEC-029 (**aprovada**), DEC-030 (**aprovada**), DEC-031 (**aprovada; catálogo canônico expandido**), DEC-032 (**aprovada**), DEC-033 (**aprovada**), DEC-034 (**aprovada**), DEC-035 (**aprovada**), DEC-036 (**aprovada**), DEC-037 (**próxima**), DEC-017.
6. Segurança, multiplayer e recuperação: DEC-011 (**aprovada**), DEC-012 (**aprovada**), DEC-018 e DEC-028 (**aprovada**), DEC-029 (**aprovada**) e DEC-030 (**aprovada**), DEC-031 (**aprovada; catálogo canônico expandido**), DEC-032 (**aprovada**), DEC-033 (**aprovada**), DEC-034 (**aprovada**), DEC-035 (**aprovada**), DEC-036 (**aprovada**), DEC-037 (**próxima**).
7. Testes, milestones e consolidação: DEC-015.

Em cada decisão, registrar: contexto, opções, escolha, justificativa, riscos, data, impacto nas SPECS.

## DEC-001 — Registro

- **Escolha:** C, comunicada pelo idealizador em 2026-11-05.
- **Motivo:** reduzir escopo inicial sem descartar o conceito de mundo online persistente.
- **Consequência:** provas de conceito do multiplayer cooperativo são requisito do MVP; mundo compartilhado simultâneo é objetivo futuro sujeito a avaliação do motor/servidor.
- **Artefato:** `decisions/ADR-0001-modelo-de-multiplayer.md`.

## DEC-002 — Registro

- **Escolha:** A, comunicada pelo idealizador em 2026-11-06.
- **Âmbito:** Windows nativo como ambiente prioritário de execução do BG2:EE, EEex e testes de bridge. A IA é desacoplada; não se fixaram versões de jogo, SO, mods nem hardware.
- **Consequência:** validar primeiro a integração real nesse SO, com instalação isolada, rollback e gate multiplayer de dois clientes.
- **Artefatos:** `decisions/ADR-0005-ambiente-windows-nativo.md` e `06-ambiente-e-matriz-de-compatibilidade-proposta.md`.

## DEC-004 — Registro

- **Escolha:** C, comunicada pelo idealizador em 2026-11-05, com adendo obrigatório sobre históricos dos personagens.
- **Modos:** Original e Living World; saves e estados separados.
- **Adendo:** cada jogador cria uma história de personagem persistente que motiva acontecimentos, missões, encontros e interações da IA para aquele grupo.
- **Limites:** IA respeita conhecimento dos NPCs, fatos confirmados, identidade e agência de jogadores; decisões detalhadas sobre segredos e revisões ainda pendentes.
- **Artefatos:** `decisions/ADR-0002-modos-de-jogo-e-historicos-de-personagem.md` e `05-requisitos-narrativos-provisorios.md`.

## DEC-019 — Registro

- **Escolha:** C (híbrido), comunicada pelo idealizador em 2026-11-05.
- **Escopo aprovado:** cada jogador controla quais partes de seu passado ficam públicas ou secretas; IA com acesso narrativo não transfere conhecimento automaticamente a NPCs ou personagens de outros jogadores.
- **Risco tratado:** vazamento e metaconhecimento; conhecimento adquirido no jogo exige justificativa e atualização persistente.
- **Artefato:** `decisions/ADR-0003-visibilidade-historicos-e-segredos.md`.
- **DEC-020 — aprovada (opção C):** histórico versionado/editável, análise de conflitos e reconciliação explícita; fatos confirmados são preservados por padrão. Detalhes em `decisions/ADR-0004-versionamento-e-revisao-de-historicos.md`.

## DEC-020 — Registro

- **Escolha:** C, comunicada pelo idealizador em 2026-11-06.
- **Escopo aprovado:** histórico editável/versionado; conflitos com eventos, memória e lore devem ser identificados antes da ativação; IA sugere reconciliação, sem executar retcons automaticamente.
- **Garantia:** eventos e consequências confirmados no mundo continuam válidos até alteração explicitamente autorizada. O tipo de aprovação para impacto em outros jogadores segue pendente.
- **Artefato:** `decisions/ADR-0004-versionamento-e-revisao-de-historicos.md`.
- **DEC-011:** aprovada (opção A), autoridade dividida e reconciliação. **DEC-014:** aprovada (opção C com adendos); DEC-021 foi aprovada depois; próxima discussão daquele registro: DEC-022 (já aprovada).

## DEC-003 — Registro

- **Escolha:** opção A, comunicada pelo idealizador em 2026-11-06.
- **Âmbito:** começar por BG2:EE limpo em Windows; validar EEex e bridge, primeiro em leitura, depois ação controlada offline e sincronização de dois clientes; somente então passar a EET, Icewind Dale e NWNForBG.
- **Condição crítica:** etapas de testes são incrementais, mas a **montagem de cada combinação de mods deve respeitar a ordem documentada**. Quando necessário, reconstruir do zero a build de teste; não instalar componentes posteriores indevidamente depois de `EET_End`.
- **Regressão:** snapshots e manifestos de versões/ordem, saves descartáveis, teste de áreas/diálogos/combate/save-load e rollback.
- **Não comprovado:** compatibilidade da combinação completa, integração de IA e multiplayer dinâmico; continuam sujeitos a gates.
- **Artefatos:** `decisions/ADR-0006-integracao-progressiva-de-conteudos.md` e `07-plano-de-integracao-progressiva.md`.

## DEC-011 — Registro

- **Escolha:** A, comunicada pelo idealizador em 2026-11-06.
- **Autoridade mecânica:** host BG2:EE confirma resultados de combate, inventário, movimentação, NPCs e itens.
- **Autoridade narrativa:** Infinity AI mantém registros persistentes de histórico, memórias, fatos e consequências devidamente confirmadas.
- **IA e bridge:** agentes propõem ações; controlador valida permissões e operações allowlisted; efeitos com resultado incerto não são registrados como sucessos nem repetidos cegamente.
- **Limite técnico:** confirmação de execução e sincronização entre clientes ainda dependem das POCs com EEex/bridge; esta decisão não comprova sua disponibilidade.
- **Artefatos:** `decisions/ADR-0007-autoridade-dividida-e-consistencia-do-estado.md` e `08-modelo-de-autoridade-e-consistencia.md`.
- **DEC-014 aprovada:** orquestração com especialistas; código primeiro e LLM local preferencial. **DEC-021:** aprovada (opção C); próxima discussão daquele registro: DEC-008 — política de persistência (já aprovada).

## Atualização DEC-014

Topologia aprovada em `decisions/ADR-0008-orquestracao-hibrida-regras-primeiro-e-llm-local.md`. O desenho preliminar está em `09-arquitetura-hibrida-regras-e-ia.md`. **DEC-006 permanece aberta para seleção de runtime/modelos e política de API remota; DEC-021 foi aprovada; DEC-022 aprovada: relógio híbrido configurável (ADR-0010).**


## DEC-021 — Registro

- **Escolha:** opção C, comunicada pelo idealizador em 2026-11-06.
- **Âmbito aprovado:** regiões ativas simuladas com o motor + regras; próximas com agendas e eventos leves; distantes com evolução resumida e limitada em lotes; dormentes sem processamento contínuo, com catch-up sob demanda.
- **Restrições:** código primeiro, LLM local somente sob demanda (DEC-014); host continua autoridade mecânica (DEC-011); conhecimento e canon preservados (DEC-019, DEC-020); sem efeito mecânico declarado como realizado sem confirmação.
- **Não decidido:** relógio com jogo fechado, prazos, categorias de fatos irreversíveis e limiares/custos por região.
- **Artefatos:** `decisions/ADR-0009-simulacao-do-mundo-por-niveis-de-atividade.md` e `10-simulacao-por-niveis-de-atividade.md`.
- **Próxima discussão:** DEC-008 — política de persistência.


## DEC-022 — Registro

- **Escolha:** opção C, comunicada pelo idealizador em 2026-11-06.
- **Âmbito aprovado:** relógio híbrido do Living World, com políticas por campanha `FROZEN`, `PARTIAL` ou `REALTIME` administradas pelo anfitrião; durante jogo ativo, o calendário segue o host. Sem sessão, não há obrigatoriedade de simulação contínua.
- **Retomada:** calcular avanço admissível (catch-up) por lotes limitados e checkpoints, apenas uma vez por revisão; registrar eventos narrativos autorizados; efeitos mecânicos dependem de confirmação do host (DEC-011).
- **Proteções:** sem perda automática de missões essenciais ou acontecimentos irreversíveis importantes durante ausência, salvo futuras regras/autorizações específicas; preservar segredos, histórico e modo Original.
- **Não decidido:** política padrão, taxa e limite de avanço, tratamento de relógio do SO, sequência de autorização de eventos irreversíveis, detalhamento de persistência e comportamento em falhas.
- **Artefatos:** `decisions/ADR-0010-tempo-hibrido-e-configuravel.md` e `11-relogio-hibrido-e-catchup.md`.
- **Próxima discussão:** DEC-008 — política de persistência do estado/memória do mundo.

## DEC-008 — Registro (2026-11-06)

- **Escolha:** opção C, com adendo: persistência híbrida (estado/snapshots e log de eventos) e cronologia oficial de Forgotten Realms integrada como origem adicional de fatos e repercussões.
- **Consequência:** eventos históricos verificados podem afetar diálogos, missões, rumores, instabilidade regional, facções e mundo simulado de acordo com ano DR, região, causalidade e conhecimento.
- **Separação necessária:** eventos históricos catalogados, acontecimentos confirmados na campanha, propostas do diretor e projeções de consulta não são a mesma coisa.
- **Autoridade e segurança:** nenhuma sugestão ou entrada de lore implica efeito mecânico sem confirmação do host; manter isolamento de modos, campanhas e segredos.
- **Atualização posterior:** DEC-009 foi aprovada com canon principal, divergência causal e matriz histórica (ADR-0012). Persistem pendências de curadoria de fontes e de precedência para conflitos específicos.
- **Artefatos:** `decisions/ADR-0011-persistencia-hibrida-e-cronologia-forgotten-realms.md`, `12-persistencia-hibrida-e-cronologia-forgotten-realms.md`.
- **Discussão concluída posteriormente:** DEC-009 aprovada em ADR-0012.


## DEC-009 — Registro

- **Escolha:** opção C com adendo, comunicada pelo idealizador em 2026-11-06.
- **Âmbito:** cronologia oficial como linha histórica principal; eventos dos jogadores podem criar desvios causais confirmados, sem retcon silencioso.
- **Adendo:** construir matriz comparativa cobrindo BG1/BG2, SoD/ToB, IWD1/IWD2 e expansões HoW/ToL, NWN1 e expansões SoU/HotU, cruzando com acontecimentos documentados de Forgotten Realms.
- **Reutilização:** priorizar conservar mapas e conteúdos existentes; atualizar exceções temporais de NPCs, governos, facções, localidades, missões e história.
- **Ressalva:** IWD1 1281 DR e IWD2 1312 DR são décadas anteriores a BG/NWN; 1372 DR é **apenas hipótese de data inicial**. NWNForBG não garante adaptação de SoU/HotU.
- **Artefatos:** `decisions/ADR-0012-politica-de-canon-e-matriz-cronologica.md`, `13-matriz-cronologica-jogos-expansoes.md`, `14-matriz-eventos-excecoes-repercussoes.md`, `15-politica-fontes-canon-curadoria.md`.
- **Próxima discussão:** DEC-023 — época inicial padrão e parâmetros por campanha.


## DEC-023 — Registro (2026-11-06)

- **Escolha:** opção C com adendo do idealizador — data configurável por campanha, com ano-base dos primeiros testes selecionado conforme menor esforço de adaptação dos conteúdos existentes.
- **Resultado da matriz inicial:** **1369 DR** é a referência de testes, por coincidir com BG2:EE (`STARTYEAR 1369` e manual do jogo); BG1 a +1, NWN a −3, IWD1 a +88 e IWD2 a +57 anos. 1370 ficou como alternativa.
- **Limite epistemológico:** não foi feito inventário de áreas/NPCs/scripts das instalações; portanto o ótimo de custo é **estimativa argumentada para o núcleo prioritário BG/EET**, a validar.
- **Restrições:** modo Living World com scripts de campanhas originais isolados; canon e origem de cada recurso verificados; SoD/ToB sem data final fabricada; cronologia não substitui teste de compatibilidade/multiplayer.
- **Documentos:** `decisions/ADR-0013-epoca-padrao-minimo-impacto.md` e `16-avaliacao-do-ano-base-por-minimo-impacto.md` (e matriz 13 atualizada).
- **Próxima discussão:** **DEC-024** — snapshot narrativo inicial: estado de BG1/SoD/BG2/ToB e isolamento dos scripts no Living World.

## DEC-024 — Registro (2026-11-06)

- **Escolha:** opção C com adendo do idealizador: manter arcos originais contemporâneos ocorrendo em paralelo, com NPCs encontráveis e ajuda **opcional**.
- **Passado:** acontecimentos originais anteriores à data do Living World (BG1/IWD) são fontes de legado — rumores, relações, consequências, sobreviventes, ressurgimentos justificados.
- **Presente:** arcos BG2 em 1369 podem evoluir independentemente do grupo; participação não obrigatória e identidade do protagonista original separada dos PCs.
- **Restrições:** datas incertas não são inventadas; script original não é autoexecutável no Living World; qualquer nova cena requer adaptador, isolamento de flags e confirmação do host para efeitos mecânicos.
- **Artefatos:** `decisions/ADR-0014-campanhas-paralelas-e-legado-historico.md` e `17-legado-historico-e-campanhas-paralelas.md`.
- **Próxima decisão:** DEC-025 — política de avanço dos arcos paralelos sem participação dos jogadores.


## DEC-025 — Registro (2026-11-06)

- **Escolha:** opção C — progressão híbrida, com janelas de participação opcionais.
- **Sem participação:** arcos contemporâneos podem continuar por regras, condições e calendário do mundo autorizado, seguindo a linha-base da campanha quando não houver divergência ou bloqueio.
- **Interação:** jogadores podem ajudar, ignorar ou interferir nos marcos disponíveis; participação não é obrigatória e não transfere a eles o papel de protagonistas originais.
- **Proteção:** acontecimentos irreversíveis relevantes não são concluídos em ausência sem regras/autorização específicas; ficam pendentes; política de aprovação detalhada ainda não decidida.
- **Consistência:** código primeiro, LLM local opcional para falas; eventos mecânicos exigem recibo do host; eventos/replay usam idempotência e isolamento por campanha.
- **Artefatos:** `decisions/ADR-0015-progressao-hibrida-arcos-paralelos.md` e `18-progressao-hibrida-arcos-paralelos.md`.
- **Próxima discussão:** DEC-026 — profundidade das intervenções e tipos de participação em campanhas clássicas.


## DEC-026 — Registro (2026-11-06)

- **Escolha:** opção C, comunicada pelo idealizador em 2026-11-06.
- **Níveis:** `N1` encontros/diálogos e relações; `N2` missões e ajuda opcional; `N3` interferência causal relevante em resultados históricos.
- **Consequências reais:** divergências confirmadas são persistidas por campanha e podem repercutir em cronologia, relações, regiões e arcos dependentes (DEC-009/008).
- **Restrições:** o grupo não assume o protagonista original; efeitos mecânicos só após confirmação do host (DEC-011); marcos irreversíveis não são executados automaticamente sem política específica; segredos respeitam DEC-019.
- **Gates:** interação real e sincronização com EEex/bridge, scripts e multiplayer ainda precisam de prova de conceito.
- **Documentos:** `decisions/ADR-0016-niveis-de-intervencao-em-arcos-classicos.md` e `19-intervencoes-causais-em-arcos-classicos.md`.
- **Próxima decisão:** **DEC-005** — base de regras de combate e modelo para dimensionar encontros.


## DEC-005 — Nota de pesquisa e comparação (2026-11-06)

- **Estado:** em análise, nenhuma opção aprovada.
- **Questões levantadas:** menor complexidade entre portar regras NWN→AD&D ou BG→D&D; benefício de regras populares/modernas; mudança de RTwP para turnos individuais.
- **Descoberta:** GemRB-TBC implementa turnos sobre AD&D 2e, mas não entrega multiplayer nem EEex/EET pronto; GemRB upstream confirma ausência de multiplayer e BG2EE experimental.
- **Conclusão provisória:** preservar BG2:EE/AD&D 2e facilita reutilização imediata; avaliar combate por turnos separadamente da conversão das regras.
- **Estudo e POCs:** `20-estudo-de-viabilidade-regras-e-combate-por-turnos.md`.
- **Possível desdobramento (pendente de aprovação):** DEC-005-R (regras), DEC-005-T (turnos), DEC-005-E (encontros).

## DEC-005-T — Registro de escolha e auditoria

- **Escolha:** B, comunicada pelo idealizador em 2026-11-06 — preservar RTwP e buscar turnos individuais como modo opcional.
- **Condição:** objetivo aprovado, implementação NÃO confirmada; validar multiplayer e hooks antes de comprometer o motor.
- **GemRB-TBC:** implementação real em código-fonte, mas motor GemRB sem multiplayer; não instalável diretamente como mod de BG2:EE.
- **Artefatos:** `decisions/ADR-0017-combate-opcional-turnos-com-gate-tecnico.md` e `21-auditoria-tecnica-gemrb-tbc-e-gates.md`.
- **Registro histórico da etapa anterior:** DEC-005-R aprovada (opção B) em 2026-11-06; ADR-0018 e documento 22. **DEC-005-E foi aprovada posteriormente, nesta v2.1** (ADR-0019 e documento 23).


## DEC-005-R — Registro da escolha (2026-11-06)

- **Escolha:** B — núcleo AD&D 2e como implementado no BG2:EE, com modernizações modulares opcionais.
- **Objetivo:** preservar a compatibilidade com conteúdo da Infinity Engine, sem conversão integral para D&D 3e ou 5e neste marco.
- **Governança:** mudanças por módulo, de forma isolada, versionada, opcional e testada; separar UX, comportamento e mecânica; não habilitar regras novas em saves/campanhas silenciosamente.
- **Gates:** regressões do baseline, compatibilidade com mods e saves, sincronização host/clientes e autoridade mecânica do jogo; validação da bridge/EEex ainda não concluída.
- **Limites:** não foram escolhidos módulos individuais, nem CR/sistema de dificuldade. DEC-005-T continua condicional a POCs do combate por turnos.
- **Artefatos:** `decisions/ADR-0018-nucleo-adnd-2e-com-modernizacoes-modulares.md` e `22-politica-de-regras-modulares-e-gates.md`.
- **Próxima decisão na época deste registro:** DEC-005-E; **já aprovada na v2.1**. A decisão DEC-010 também foi aprovada na v2.2.

## DEC-005-E — Registro da escolha (2026-11-06)

- **Escolha:** B — diretor adaptativo com limites regionais.
- **Objetivo:** encontros variados para grupos diferentes sem escalonamento global nem garantia de vitória. Região, cânone/época, ecologia, facções e consequências confirmadas permanecem fontes primárias.
- **Mecânica:** regras/tabelas/seed rastreável; AD&D 2e como baseline; sem LLM para seleção de criaturas, combate ou loot.
- **Autoridade:** spawn e efeitos do encontro dependem de confirmação do host, idempotência e testes multiplayer.
- **Limites:** nenhuma fórmula de dificuldade, faixa numérica, lista de criaturas ou taxa de encontro já aprovada; turnos opcionais continuam bloqueados por POCs.
- **Artefatos:** `decisions/ADR-0019-diretor-adaptativo-encontros-com-limites-regionais.md` e `23-diretor-adaptativo-de-encontros-regionais.md`.
- **Próxima decisão:** DEC-010 — conteúdo criado previamente, geração em runtime ou sistema híbrido.


## DEC-010 — Registro da escolha (2026-11-06)

- **Escolha:** opção C — mundo curado com geração procedural validada e progressiva.
- **Alvo:** preservar mapas/cidades, NPCs importantes, canon e recursos dos jogos e mods existentes, ampliando a rejogabilidade com missões, rumores, histórias, encontros e locais novos quando viáveis.
- **Estratégia:** priorizar reuso de áreas e recursos conhecidos; propostas narrativas por templates/código e LLM local sob demanda; geração de mapas/masmorras via construção **antecipada e teste isolado**. Alterar mapa/scripts/áreas durante jogo em execução é **hipótese técnica não aprovada como capacidade comprovada**.
- **Validação:** lore, época, histórico/segredos, precondições, ecologia, manifesto/versionamento, segurança, permissões, multiplayer e save/load. Propostas não são resultados mecânicos: exigem host/bridge e receipt conforme DEC-011.
- **Limites:** licença dos recursos externos, isolamento entre Original e Living World, não habilitar scripts gerados pela IA sem allowlist/avaliação.
- **O que ainda não foi escolhido:** regras de publicação e autorização de cada classe de conteúdo (DEC-027), inventário e formatos reais dos assets, e qualquer instalação em BG2:EE.
- **Documentação:** `decisions/ADR-0020-mundo-curado-e-geracao-procedural-validada.md` e `24-pipeline-de-geracao-procedural-validada.md`.
- **Próxima decisão à época do registro:** DEC-027 — aprovada posteriormente na v2.3; próxima atual DEC-012.


## DEC-027 — Opção C aprovada em 2026-11-06

- **Escolha:** autonomia por níveis de risco para publicação do conteúdo do Living World.
- **LOW:** rumores, interações e conteúdo narrativo simples podem ser publicados automaticamente apenas após validação temporal, de conhecimento/segredos e do estado do mundo.
- **MEDIUM:** missões, encontros, itens/recompensas e alterações locais seguem controles estruturados; qualquer efeito mecânico precisa de confirmação independente do **host**, não apenas de uma declaração do LLM.
- **HIGH:** mortes permanentes históricas, alterações políticas/canônicas, destruições importantes e eventos irreversíveis ficam bloqueados sem política de autorização especial explícita. Política futura poderá requerer aprovação humana.
- **Defesa:** risco calculado deterministicamente pelos impactos e efeitos agregados; o LLM não autoautoriza, não reclassifica arbitrariamente e não injeta Lua livre na bridge. Estados `UNCERTAIN` exigem reconciliação antes de retry.
- **Limites:** critérios numéricos, escopo de autorização, papéis de aprovação e UI ainda não foram aprovados; publicação em jogo e multiplayer não foram testados.
- **Artefatos:** `decisions/ADR-0021-autonomia-de-publicacao-por-niveis-de-risco.md` e `25-politica-de-publicacao-e-autorizacao-por-risco.md`.
- **Próxima decisão:** DEC-012 — fronteira de segurança, permissões e allowlist de comandos da bridge.

> **Estado corrente no encerramento da v2.3:** DEC-027 aprovada (ADR-0021); DEC-012 aberta e selecionada para a próxima entrevista. Referências a “próxima decisão” em registros históricos descrevem a ordem daquela etapa, não o backlog atual.


## DEC-012 — Registro da escolha (2026-11-06)

- **Escolha:** opção **B — gateway seguro de ações autorizadas**, comunicada pelo idealizador.
- **Decisão:** agentes/LLMs só geram propostas tipadas de uma allowlist. Policy Engine determinístico valida limites, tempo, campanha, sessão, identidade, versão de recursos, pré-condições, escopo e risco agregado; default-deny para qualquer operação fora do contrato.
- **Execução:** apenas bridge confiável pode traduzir operações autorizadas para mecanismos realmente suportados pelo BG2:EE/EEex; jamais avaliar texto do LLM como Lua/código; o host confirma efeitos mecânicos.
- **Conexão com DEC-027:** `LOW` narrativa validada, `MEDIUM` com autorização por operação e recibo do host, `HIGH` **bloqueado** até existir política especial explícita; permissão de despachar não é prova de execução.
- **Segurança e resiliência:** menor privilégio, isolamento entre Original/Living World e campanhas, auditoria sem segredos, idempotência, `UNCERTAIN`/reconciliação; sem retries cegos de spawn/recompensa.
- **Gates:** leitura primeiro, mutação isolada, depois multiplayer com 2 clientes; viabilidade técnica e versões EEex/bridge não comprovadas.
- **Pendências:** schema e catálogo real de operações, autenticação, quotas, recuperação, UI/papéis de HIGH; decisão DEC-028 sobre autorização de leitura/contexto antes dos LLMs.
- **Artefatos:** `decisions/ADR-0022-gateway-seguro-de-acoes-autorizadas.md` e `26-gateway-de-acoes-seguras-e-contratos.md`.

> **Estado corrente v2.4:** DEC-012 aprovada (ADR-0022). A próxima discussão é **DEC-028**; referências anteriores ao status aberto da DEC-012 são históricas e não substituem este registro.

## DEC-028 — Registro da escolha (2026-11-06)

- **Escolha:** B — memória global estruturada e compartilhada, mas recuperação **autorizada antes** de montar o contexto do agente ou modelo, conforme origem, identidade, destinatário, finalidade e instante da campanha.
- **Separações obrigatórias:** visibilidade pública/privada do histórico do jogador (DEC-019), conhecimento legítimo dos personagens, privilégios do narrador/orquestrador e capacidade de executar mudanças mecânicas (DEC-012).
- **Sem onisciência por armazenamento:** estar na base não torna o fato conhecido por NPCs; fontes legitimadoras incluem testemunho, comunicação, descoberta e eventos validados. Distinguir rumores e suspeitas de fatos confirmados.
- **Proteções:** default deny, segregação por campanha/mode, controle de caches/embeddings/prompts/resumos/logs, prevenção de injeção, retcon condicionado à DEC-020. LLM não autoriza leitura por si mesmo.
- **Limites:** não foram escolhidos banco físico, formato final, regras de esquecimento/revogação ou política de difusão. Integração com BG2:EE/EEex e multiplayer não testada.
- **Artefatos:** `decisions/ADR-0023-acesso-seletivo-a-memoria-e-conhecimento-por-agente.md` e `27-politica-de-conhecimento-e-recuperacao-seletiva.md`.
- **Próxima discussão naquele momento:** DEC-029 — aprovada posteriormente na v2.6; veja ADR-0024.

> **Estado histórico v2.5:** DEC-028 aprovada (ADR-0023); DEC-029 ainda estava aberta nessa versão. A DEC-029 foi aprovada na v2.6.


## DEC-029 — Registro da escolha (2026-11-06)

- **Escolha:** opção **B**, comunicada expressamente pelo idealizador — notícias e rumores se propagam por redes sociais, facções, regiões, viagens, canais e passagem do tempo.
- **Mecanismo:** regras/FSM e agendas com seeds e checkpoints, sem modelo de IA rodando para cada conversa ou NPC inativo. LLM local poderá redigir versões narrativas sob demanda, jamais atribuir conhecimento sem proveniência.
- **Autorização:** emissor precisa conhecer a informação e ter canal/contexto de divulgação permitido; receptor adquire crença/relato somente depois da transferência elegível. Respeitar DEC-019/028, isolamento por campanha/mode e default-deny para segredos.
- **Verdade e crença:** eventos confirmados/canon, observações, rumores, exageros e mentiras são mantidos separadamente. Rumores podem divergir entre personagens, sem alterar o histórico real por repetição.
- **Simulação:** tempo autorizado por DEC-022, propagação `ACTIVE/NEAR/DISTANT/DORMANT` conforme DEC-021, lotes limitados e idempotência; sem anúncio automático de fatos futuros de Forgotten Realms.
- **Governança:** ações mecânicas ou consequências exigem gateway/host (DEC-012/011); eventos `HIGH` permanecem bloqueados sem política especial (DEC-027).
- **Limites:** não foram escolhidos algoritmos probabilísticos, tempos/distâncias/TTL, taxas de retransmissão, UI, banco físico ou política detalhada para segredos legitimamente descobertos; integração BG2:EE/EEex/multiplayer não executada.
- **Documentos:** `decisions/ADR-0024-propagacao-deterministica-de-noticias-e-rumores.md` e `28-propagacao-de-noticias-rumores-e-grafo-social.md`.
- **Próxima decisão:** **DEC-030** — reputação e percepção entre NPCs, facções e regiões, fundamentadas nas informações que efetivamente receberam.

> **Estado corrente v2.6:** DEC-029 aprovada; DEC-030 em aberto. As citações de etapas anteriores sobre “próxima discussão” permanecem como histórico.


## DEC-030 — Registro da escolha (2026-11-06)

- **Opção B aprovada:** reputação por observador (NPC, facção, região) e por alvo (jogador, grupo, identidade legitimamente conhecida), multidimensional e contextual.
- **Sem universalização:** reputação factual não é igual a rumor/crença. Compartilhamento segue DEC-028/029; reputações locais não se tornam globais por armazenamento; membros da mesma facção podem discordar.
- **Eixos candidatos:** fama/notoriedade, confiança, temor, hostilidade, respeito/prestígio. Sem fórmula, escala, pesos, decaimento ou influência mecânica aprovados.
- **Compatibilidade:** preservar reputação nativa de BG2:EE e modo Original. Camada externa narrativa, sem alterações automáticas em preços, combate, scripts ou alinhamento; efeitos mecânicos exigem SPEC, gateway DEC-012 e host DEC-011.
- **Persistência:** causa e proveniência (fato/alegação), contexto temporal, versão, idempotência e snapshots/log (DEC-008/022). Cálculo por código primeiro; LLM sob demanda só para verbalizar percepções autorizadas.
- **Segurança:** histórico secreto não muda reputação pública antes de descoberta legítima; identidade disfarçada não é ligada à real automaticamente; responsabilidade individual e coletiva não se confundem.
- **Artefatos:** `decisions/ADR-0025-reputacao-contextual-multidimensional.md` e `29-reputacao-contextual-percepcoes-e-faccoes.md`.
- **Status:** decisão arquitetural aprovada, implementação/POCs pendentes.
- **Próxima entrevista indicada na v2.7 (histórico):** **DEC-031** — aprovada na v2.8; a próxima atual é **DEC-032**.

> Estado corrente v2.7: DEC-030 aprovada. Registros de versões anteriores que mencionam DEC-030 como “próxima” descrevem apenas a cronologia das entrevistas.


## DEC-031 — Registro aprovado (2026-11-06; v2.8)

- **Escolha:** opção B, com adendo expresso: facções autônomas por objetivos, recursos e regras determinísticas, sem LLM continuamente ativo para cada instituição.
- **Cobertura:** preservar facções dos jogos BG/IWD/NWN, mas ampliar o **catálogo** às demais organizações canônicas de Forgotten Realms. Objetivo de cobertura global do canon, **curadoria e indexação progressivas**; não prometer NPCs, mapas ou simulação integral de todas no MVP.
- **Tempo e lugar:** organizações têm identidade, fontes, períodos de atividade, localização, lideranças e mudanças históricas; 1369 DR é ano-base de testes, outras épocas configuráveis.
- **Limites:** uma entrada canônica pode influenciar o mundo sem que exista asset na instalação; efeitos mecânicos exigem gateway/host; guerras, golpes ou mortes históricas críticas seguem bloqueadas sem política HIGH; membros não são oniscientes.
- **Arquitetura:** catálogo canônico verificado + overlay específico da campanha, simulação por relevância, lotes e níveis de atividade; cronologia e divergências auditáveis.
- **Artefatos:** `decisions/ADR-0026-faccoes-autonomas-e-catalogo-canonico-expandido.md` e `30-simulacao-de-faccoes-e-catalogo-canonico.md`.
- **Próxima:** DEC-032 — granularidade e custo de simulação econômica, territorial e político-militar.


## DEC-032 — Registro da escolha e benchmark (2026-11-06)

- **Escolha:** B — simulação hierárquica adaptativa por relevância, com níveis ACTIVE/NEAR/DISTANT/DORMANT e tempo de campanha delimitado.
- **Adendo:** estudar mecanismos econômicos, políticos e militares de *Rome: Total War/ROME II/Remastered* e outros simuladores. Investigados também *Bannerlord*, *Crusader Kings III*, *X4: Foundations* e *Stellaris 4.0* mediante fontes oficiais/documentação de desenvolvedores.
- **Padrões:** mapa político e diplomacia com objetivos por regras (Rome), comércio e logística interdependentes (Bannerlord), liderança e intriga (CK3), escassez e cadeias produtivas como influência (X4), agregação de populações para escala (Stellaris).
- **Autoridades e limites:** sistemas estratégicos agregados externos não alteram o BG2:EE sem gateway e recibo do host; eventos históricos/irreversíveis HIGH permanecem bloqueados sem política especial. Nenhuma incorporação de motores, algoritmos proprietários ou modulação de preços real é presumida.
- **Documentos:** `decisions/ADR-0027-simulacao-hierarquica-adaptativa-politica-economica-e-militar.md`, `31-pesquisa-comparativa-simuladores-estrategicos.md`, `32-modelo-hierarquico-de-economia-politica-e-conflitos.md`.
- **Próxima discussão na v2.9:** DEC-033 — aprovada posteriormente na v3.0; ver ADR-0028.


## DEC-033 — Resolução híbrida de conflitos militares (2026-11-06, v3.0)

- **Escolha:** **opção B aprovada** — simulação militar agregada para conflitos distantes e, próximos dos jogadores, oportunidades de batalhas, escoltas, defesa ou negociação no BG2:EE, **sempre opcionais**.
- **Autoridade:** eventos abstratos estratégicos não são recibos mecânicos; alterações no motor exigem gateway, bridge e confirmação do host. Escaramuças locais só afetam proporcionalmente a parte relevante do conflito.
- **Garantias:** impedir resolução macro+micro duplicada da mesma subinstância; checkpoints, idempotência, provenance e isolamento de modo Original. Não requer combate por turnos (DEC-005-T ainda depende de POCs).
- **Limite crítico:** quedas canônicas de cidades, guerras de alto impacto e morte de líderes históricos continuam `HIGH` e bloqueadas até política de autorização especial em DEC-034, ainda aberta.
- **Artefatos:** `decisions/ADR-0028-resolucao-hibrida-de-conflitos-e-intervencoes-locais.md` e `33-ponte-entre-conflitos-estrategicos-e-combates-locais.md`.
- **Status:** arquitetura aprovada, **não executada** em BG2:EE/EEex/multiplayer; fórmulas e materiais concretos dependem de SPECS.
- **Próxima discussão:** DEC-034 — autorização de eventos irreversíveis de alto risco.


## DEC-034 — Autonomia controlada e proteção do cânone (2026-11-06, v3.1)

- **Aprovada — opção C:** eventos de impacto limitado/reversível podem seguir políticas de campanha preautorizadas; mortes históricas centrais, destruição de grandes cidades e outros fatos canônicos irreversíveis exigem autorização especial explícita, escopo verificável e registro causal.
- **Default-deny para HIGH crítico:** sem pré-política suficiente, bloquear/pender, inclusive eventos offscreen, sem deixar LLM ou facção decretarem o fato.
- **Jogadores têm agência:** investigar, proteger ou apoiar conspirações; não atribuir moralidade fixa a uma escolha sem contexto.
- **Pendente:** política detalhada de consentimento, UI, tratamento técnico de ações físicas já confirmadas pelo host; POCs com multiplayer.
- **Artefatos:** `decisions/ADR-0029-autonomia-controlada-protecao-especial-do-canon.md`; `34-politica-de-eventos-historicos-irreversiveis.md`.

## DEC-035 — Alinhamento mutável (adendo expresso à DEC-034; 2026-11-06, v3.1)

- **Aprovada:** personagem não mantém alinhamento congelado; poderá evoluir nos eixos Lawful/Neutral/Chaotic e Good/Neutral/Evil conforme histórico de ações efetivas e contextuais.
- **Separação obrigatória:** alinhamento interno/moral ≠ reputação social DEC-030; rumor falso não muda alinhamento, e ação sem testemunha pode alterar evolução ética mesmo sem mudar reputação.
- **Limites técnicos:** BG2:EE restringe classes/efeitos de alinhamento; consequências mecânicas dependem de SPEC, gateway, host, testes, compatibilidade de save e multiplayer.
- **Artefatos:** `decisions/ADR-0030-alinhamento-dinamico-por-acoes-confirmadas.md`; `35-alinhamento-dinamico-e-relacao-com-reputacao.md`.
- **Próxima discussão:** **DEC-036 — método de avaliação contextual e gradual do alinhamento**.


## DEC-036 — Avaliação contextual híbrida do alinhamento (2026-11-06, v3.2)

- **Opção B APROVADA.** Avaliação em dois eixos por regras versionadas, com contexto causal, padrão de ações e mudança gradual; LLM local pode sugerir interpretação de situações abertas, nunca arbitrar sozinho resultados ou aplicar estado mecânico.
- **Evidência:** somente fatos confirmados e autoria/participação individual fundamentada. Separar intenção conhecida de intenção inferida; coerção, legítima defesa, informação disponível e consequências não são equivalentes.
- **Incerteza:** casos insuficientes ficam pendentes/revisáveis; sem efeito mecânico automático. Nenhum peso, limiar, taxa, escala ou algoritmo numérico foi aprovado.
- **Independência:** alinhamento narrativo ≠ reputação social por NPC/facção ≠ atributo mecânico do BG2:EE. Modo Original e segredos permanecem protegidos.
- **ADR:** `decisions/ADR-0031-avaliacao-contextual-hibrida-e-gradual-do-alinhamento.md`.
- **Desenho técnico preliminar:** `36-avaliacao-contextual-gradual-e-auditoria-do-alinhamento.md`.
- **Próxima:** **DEC-037 — consequências mecânicas da evolução de alinhamento** (classes, kits, magias, equipamentos, avisos e gate BG2:EE/EEex).

> **Estado corrente v3.2:** DEC-036 aprovada; menções anteriores a DEC-036 como "próxima" registram a sequência histórica de Discovery, não seu estado atual.


## DEC-037 — Registro da escolha (2026-11-06; Discovery v3.3)

- **Escolha expressa:** **B — consequências progressivas e validadas** das mudanças de alinhamento.
- **Moral versus mecânica:** a tendência da DEC-036 não é o atributo do engine. Uma transição contextual confirmada exige avaliação de classe/kit/itens/magias e efeitos da instalação/modlist antes de qualquer escrita no BG2:EE.
- **Regras da campanha:** o jogador conhece as possibilidades gerais de consequência; versões do perfil de regra são preservadas, sem mudança retroativa silenciosa. Avisos devem ser proporcionais, sem vazamento de segredos.
- **Sem perdão automático:** a escolha B não equivale a permitir cancelar perdas legítimas; possíveis jornadas de redenção, juramentos ou troca de classe dependem da DEC-038 e de SPECS.
- **Autoridade e segurança:** LLM não escreve atributos; Action Gateway executa somente propostas tipadas e permitidas; host confirma efeitos; resultados `UNCERTAIN` exigem conciliação e não autorizam repetição cega.
- **Gates:** nenhuma alteração mecânica aprovada como funcionalidade executável; POCs BG2:EE/EEex por classe/kit, mods, multiplayer, save/load, modo Original e rollback.
- **Documentação:** `decisions/ADR-0032-consequencias-progressivas-e-validadas-do-alinhamento.md`; `37-consequencias-mecanicas-progressivas-do-alinhamento.md`.
- **Próxima decisão:** **DEC-038 — redenção, reconsagração de juramentos e recuperação de poderes ou mudanças de classe**.

> **Estado corrente v3.3:** DEC-037 aprovada; DEC-038 aberta. Referências anteriores a DEC-037 como “próxima” fazem parte do histórico de versões.


## DEC-038 — Redenção e transformação (2026-11-06; Discovery v3.4)

- **Escolha expressa:** **opção B aprovada** — jornadas pessoais de redenção, renovação de juramentos, reparação ou transformação, gerando aventuras personalizadas conforme histórico, ações e cenário de Forgotten Realms.
- **Agência:** a busca por redenção é voluntária; o personagem pode recusar, adiar ou manter a nova orientação. Não é necessário retornar ao alinhamento de origem; não existe recuperação gratuita de poderes nem perdão garantido de terceiros.
- **Não apagar consequências:** danos e acontecimentos confirmados persistem; conclusão de missão pessoal não reverte automaticamente alinhamento, reputação, promessas, relacionamentos ou responsabilidades.
- **Regras e classes:** recuperar poderes, trocar juramentos/patronos, kit ou classe depende de regras da campanha, SPEC, POC real BG2:EE/EEex, gateway e receipt do host. Nenhuma dessas conversões foi aprovada como recurso implementado.
- **Cânone/segredos:** deuses, ordens, facções e NPCs precisam corresponder ao período da campanha e ao conhecimento legitimamente disponível, sem vazamento de históricos secretos.
- **Arquivos:** `decisions/ADR-0033-jornadas-personalizadas-de-redencao-e-transformacao.md` e `38-jornadas-de-redencao-e-transformacao-pessoal.md`.
- **Próximo tema:** **DEC-039 — geração e acompanhamento de arcos pessoais/quests de personagem** (opções a escolher).

> **Estado corrente v3.4:** DEC-038 aprovada; DEC-039 aberta. Referências anteriores que chamem DEC-038 de “próxima” pertencem ao histórico das versões anteriores.


## DEC-039 — Diretor híbrido de histórias pessoais (2026-11-06; Discovery v3.5)

- **Escolha expressamente aprovada:** opção C, com **Personal Story Director** combinando templates narrativos validados, marcos e dependências estruturadas, geração local sob demanda e continuidade persistente por personagem/campanha.
- **Agência e progressão:** permitir aceitar, adiar, recusar e transformar arcos sem impor desfecho; só concluir marcos com evidências e efeitos mecânicos confirmados pelo host.
- **Conhecimento, sigilo e canon:** origem de cada gancho e versão do histórico rastreadas, contexto filtrado antes do LLM, cronologia e alterações irreversíveis sujeitas a validação/autorizações existentes.
- **Grupo:** arcos pessoais podem oferecer oportunidades cooperativas, sem tornar segredos públicos nem exigir participação; alocação do foco entre jogadores não foi escolhida nesta decisão.
- **Limite técnico:** não implica geração de mapas em runtime, scripts autônomos seguros, interface implementada ou suporte já testado com BG2:EE/EEex/multiplayer.
- **Documentos:** `decisions/ADR-0034-diretor-hibrido-de-historias-pessoais-e-marcos.md` e `39-diretor-de-historias-pessoais-e-marcos-narrativos.md`.
- **Próxima discussão:** **DEC-040 — protagonismo e coordenação de histórias pessoais na campanha cooperativa.**

> **Estado corrente v3.5:** DEC-039 aprovada; DEC-040 aberta. Trechos históricos que indiquem DEC-039 como aberta são registros de versões anteriores.


## DEC-040 — Equilíbrio narrativo dinâmico (2026-11-06; Discovery v3.6)

- **Escolha expressamente aprovada:** opção **B — diretor cooperativo de narrativas com equilíbrio dinâmico**; coordena oportunidades do PSD para personagens de diferentes jogadores, com foco narrativo distribuído ao longo da campanha.
- **Sem alternância rígida:** oportunidade significativa, momento narrativo, presença, elegibilidade por canon/recursos, participação recente e ritmo são considerados por regras; métricas e fórmulas ficam para SPECS.
- **Agência:** aceitar, recusar, adiar, manter privado ou convidar voluntários; não forçar missões individuais nem encerrar escolhas de personagens ausentes.
- **Segredos:** compartilhamento de missão não revela automaticamente backstory ou conhecimento privado. Contexto filtrado antes de convites, prompts, diálogos e logs.
- **Progressão e consequência:** marcos por evidência, autoria individual, gateway, recibos do host e persistência idempotente; DEC-022/027/034 continuam em vigor.
- **Limitações:** não há POC de interface, divisão de grupo, scheduler ou sincronização multiplayer BG2:EE/EEex. Sem estimativa de pesos/quotas aprovada.
- **Artefatos:** `decisions/ADR-0035-diretor-cooperativo-de-equilibrio-narrativo-dinamico.md` e `40-diretor-cooperativo-equilibrio-narrativo.md`.
- **Próxima:** **DEC-041 — consentimento e autoridade quando um arco pessoal interfere em outros jogadores, segredos ou eventos coletivos**.

> **Estado corrente v3.6:** DEC-040 aprovada. Referências anteriores a DEC-040 como “próxima” são históricas.


## DEC-041 — Autoridade distribuída e consequências cruzadas (2026-11-06; Discovery v3.7)

- **Escolha expressa:** **opção C aprovada** — cada jogador decide as ações, falas, intenções e revelações voluntárias do próprio PC; anfitrião administra políticas do mundo e gateway/host confirmam efeitos mecânicos.
- **Causalidade compartilhada:** ações legítimas e comprovadas de outro PC podem afetar fatos do mundo e as circunstâncias de um personagem sem exigir aprovação individual para cada consequência; isso **não autoriza controlar outro PC nem editar seu histórico**.
- **Segredos:** o titular escolhe o que contar voluntariamente; terceiros podem descobrir por vias legítimas dentro de políticas de conhecimento, histórico de evidências e limites definidos; boato/suspeita não vira fato confirmado.
- **Ausência:** nenhum diretor/LLM escolhe pelo jogador ausente; a simulação continua somente onde DEC-021/022/025 e o risco permitem, sem assumir autoria pessoal.
- **Restrições:** autorização histórica HIGH DEC-034, Action Gateway DEC-012, host DEC-011, fatos persistentes e isolamento Original/Living World continuam obrigatórios.
- **Fora do escopo:** ações diretamente prejudiciais entre PCs (PvP, furto, coerção, dano/morte) continuam **abertas na DEC-042**.
- **Artefatos:** `decisions/ADR-0036-autoridade-distribuida-agencia-e-consequencias-cruzadas.md` e `41-autoridade-distribuida-consentimento-e-eventos-cruzados.md`.
- **Próxima:** DEC-042 — política de interações hostis/PvP em campanha cooperativa.

> **Estado corrente v3.7:** DEC-041 aprovada. Referências históricas a DEC-041 como “próxima” correspondem ao Discovery anterior.


## DEC-042 — PvP configurável com limites e consentimento (2026-11-06; Discovery v3.8)

- **Escolha expressa:** **opção C aprovada** — políticas por campanha para duelos, roubo, magias hostis, dano, coerção e consequências irreversíveis, com limites e consentimento em categorias separadas.
- **Agência:** o anfitrião configura o mundo, mas não consente em nome do controlador de outro PC; IA/LLM não cria falas, confissões, autorizações nem decisões por jogador.
- **Default seguro proposto:** campanhas cooperativas sem dano mecânico hostil autorizado até opt-in. Perfis alternativos dependem de acordo e validação; as regras granulares de UX e revogação ficam para SPECS.
- **Morte permanente:** não é permitida implicitamente por duelos ou PvP genérico; depende de política especial e DEC-043, ainda aberta.
- **Mecânica e bypass:** gateway + host para efeitos confirmados, checagens de alvos/ações indiretas; nenhum hook de bloqueio preventivo é presumido em BG2:EE/EEex sem POC em dois clientes.
- **Persistência:** escopo, versão de política, autorizações e efeitos confirmados auditáveis, idempotentes e isolados do modo Original.
- **Documentos:** `decisions/ADR-0037-pvp-configuravel-com-limites-e-consentimento.md` e `42-politicas-de-pvp-consentimento-e-limites-mecanicos.md`.
- **Próxima:** **DEC-043 — morte, ressurreição e permanência de personagens de jogador**.

> **Estado corrente v3.8:** DEC-042 aprovada. Referências mais antigas à DEC-042 como “aberta/próxima” permanecem apenas como histórico de versões anteriores.

## DEC-043 — Mortalidade configurável e legado persistente (2026-11-06; Discovery v3.9)

- **Escolha expressa:** opção **C — morte/ressurreição por política de campanha, com histórico persistente do PC falecido**.
- **Motor primeiro:** morte, retorno e efeitos materiais exigem evidência do host; o LLM não gera ressurreição, game-over, cadáver, item ou sucessor por ficção.
- **Perfis:** regras clássicas são referência inicial, configurações mais permissivas/rigorosas dependem de opt-in conhecido, SPECS e compatibilidade comprovada. Não anunciar intervenção preventiva sem hook validado.
- **Legado:** eventos, relações e repercussões confirmadas permanecem após a morte; rumores, segredos e conhecimento mantêm proveniência, tempo e ACL.
- **PvP:** consentimento para duelo/ataque não equivale a consentimento para morte definitiva. Proteger jogadores ausentes e ações indiretas.
- **Consistência:** manter modo Original isolado, host/bridge autoritativos, ledger/snapshots idempotentes, reconciliação `UNCERTAIN`, suporte específico de ressurreição, saves e *game-over* ainda não verificados.
- **Documentos:** `decisions/ADR-0038-mortalidade-configuravel-ressurreicao-e-legado-persistente.md` e `43-mortalidade-ressurreicao-e-legado-de-personagens.md`.
- **Próxima:** **DEC-044 — sucessão, criação de novos personagens, integração à party e herança/conhecimento após a morte ou aposentadoria de um PC.**

> **Estado corrente v3.9:** DEC-043 aprovada; DEC-044 aberta. Menções anteriores a DEC-043 como "aberta/próxima" são partes do histórico do Discovery.

## DEC-044 — Sucessão contextual e herança legítima (2026-11-06; Discovery v4.0)

- **Escolha expressa:** opção **C — novo personagem com histórico próprio, ingresso contextual e progressão por política de equilíbrio da campanha**.
- **Identidades distintas:** continuidade de jogador não equivale a continuidade de PC; nada de transmissão automática de memória, alinhamento, fama, inimigos, status, quests ou bens.
- **Herança causal:** espólio, propriedade e conhecimento dependem de eventos/fontes legítimos, autorização dos titulares, regras de risco e recibos do host; sucessor não recebe itens ou experiência por ser controlado pela mesma conta.
- **Legado:** fatos e relações do PC antigo permanecem; diretores narrativos podem propor ganchos derivados sem retcon ou divulgação de segredos.
- **Motor e segurança:** criação/entrada no BG2:EE, controle por slots, protagonista, game-over, ressurreição tardia, saves/EEex/multiplayer e transações de itens **não estão testados**. Sem prometer hot-swap ou modificar save por LLM.
- **Documentos:** `decisions/ADR-0039-integracao-contextual-de-novos-personagens-e-heranca-legitima.md` e `44-entrada-de-personagens-sucessao-e-heranca-legitima.md`.
- **Próxima:** **DEC-045 — como proteger a agência e a segurança mecânica de um PC quando seu jogador está ausente ou desconectado?**

> **Estado corrente v4.0:** DEC-044 aprovada; DEC-045 aberta. Referências anteriores a DEC-044 como próxima/aberta são históricas.

## DEC-045 — Múltiplos PCs por jogador e redistribuição em ausências (2026-11-06; Discovery v4.1)

- **Escolha expressa:** atribuir temporariamente o PC de jogador ausente a outro jogador presente (um participante pode controlar vários PCs), como no modelo de BG3. Isto substitui as opções preliminares A/B/C da pergunta DEC-045.
- **Evidência forte:** BG2:EE possui **Character Arbitration**, descrita no manual oficial (pp. 58–63), capaz de atribuir slots a jogadores. Trata-se de função nativa documentada, **não** de integração por script já comprovada.
- **Separações:** PC e seu titular persistem. Controlador temporário não se torna dono da identidade/histórico, não herda conhecimento privado nem ganha autorização irrestrita para narrativas pessoais.
- **Continuidade:** a party pode prosseguir com controle humano e retornar o mesmo PC ao jogador titular, quando tecnicamente possível. IA não interpreta o ausente automaticamente.
- **Gates:** host confirma ações; anotar epoch e controlar `UNCERTAIN`, evitar duplo comando; salvamento, tela de arbitragem durante combate, protagonista/game-over e EEex exigem POCs.
- **Direitos:** ações táticas da sessão não autorizam automaticamente PvP, exploração de segredos, juramentos, escolhas pessoais nem alterações irreversíveis; amplitude dessas permissões é **DEC-046**.
- **Arquivos:** `decisions/ADR-0040-controle-multiplos-personagens-e-delegacao-em-ausencias.md` e `45-multiplos-personagens-por-jogador-e-delegacao-em-ausencias.md`.
- **Próxima:** DEC-046 — autoridade do controlador substituto por categoria.

> **Estado corrente v4.1:** DEC-045 aprovada. Menções anteriores a DEC-045 como aberta são históricas.

## DEC-046 — Delegação granular por categorias e consentimento do titular (2026-11-06; Discovery v4.2)

- **Escolha expressa:** **opção C** — o titular do PC define previamente a extensão de autoridade do controlador substituto por categoria, sob políticas de campanha.
- **Escopos:** movimento/exploração, combate, consumíveis, recursos/itens, diálogos, missões coletivas, arcos pessoais, juramentos/pactos, segredos, PvP e ações irreversíveis são categorias distintas; permissão operacional não implica decisão pessoal.
- **Padrão seguro:** sem consentimento prévio, não atribuir autoridade para atos pessoais ou HIGH; exigências extras de DEC-027/034/042/043 prevalecem sempre. Combate pode causar perdas reais; não prometer imunidade de personagem delegado.
- **Segurança:** `owner_id`, `controller_id`, `pc_id`, slot, epoch e grant versionados; retorno/revogação prospectiva, auditáveis; memória privada filtrada antes do modelo.
- **Fronteira de viabilidade:** Character Arbitration BG2:EE documentada, mas **não é prova de veto granular via hooks**. Se um ato proibido não puder ser interceptado, aplicar pausa/não delegação/fallback humano em vez de declarar bloqueio inexistente.
- **Arquivos:** `decisions/ADR-0041-delegacao-temporaria-por-categorias-e-consentimento-do-titular.md` e `46-delegacao-granular-permissoes-e-consentimento-do-titular.md`.
- **Próxima:** **DEC-047 — autonomia e personalidade narrativa de companions NPCs recrutáveis versus o controle tático do jogador**.

> **Estado corrente v4.2:** DEC-046 aprovada. Menções anteriores a DEC-046 como aberta/próxima são históricas.


## DEC-047 — Companheiros NPC: controle tático e autonomia narrativa (2026-11-06; Discovery v4.3)

- **Escolha expressa:** **opção C**. Recrutados permanecem taticamente comandáveis pelos jogadores; companheiros NPC mantêm personalidade, valores, memória, relações e objetivos próprios.
- **Separação de papéis:** companion NPC não é PC de jogador ausente. Conceder controle de uma unidade não torna um humano autor de sua identidade nem transforma autonomia narrativa em comando mecânico da IA.
- **Reações:** podem apoiar, discordar, protestar, propor aventuras e desenvolver lealdades/rivalidades; ruptura e saída da party são **possibilidades condicionadas a regras e provas técnicas**, não efeitos arbitrários já implementados.
- **Conhecimento:** reações apenas a acontecimentos legitimamente observados/relatados, com filtro de segredos e proveniência; fatos do cânone sujeitos a época, fontes e divergências confirmadas.
- **Orquestração:** regras determinísticas para eventos, condições e relações; LLM local sob demanda para falas abertas; sem inferência permanente por NPC.
- **Mecânica e compatibilidade:** qualquer recrutamento, saída, mudança de flags, inventário, posição ou comportamento do motor depende de Action Gateway + recibo do host. A compatibilidade com diálogos/scripts nativos, mods e coop não foi validada; fallback narrativo quando veto/saída não é possível.
- **Arquivos:** `decisions/ADR-0042-controle-tatico-com-autonomia-narrativa-dos-companheiros-npc.md` e `47-companheiros-npc-controle-tatico-e-autonomia-narrativa.md`.
- **Próxima:** **DEC-048 — protocolo de desacordo, avisos, negociação, recusa e desligamento de companions NPCs**.

> **Estado corrente v4.3:** DEC-047 aprovada; DEC-048 aberta. Referências anteriores a DEC-047 como próxima/aberta integram o histórico.


## DEC-048 — Lealdade contextual, negociação e ruptura dos companheiros NPCs (2026-11-06; Discovery v4.4)

- **Escolha expressa:** opção **B** — respostas dos companheiros são condicionadas a valores, limites, eventos, conhecimento legítimo, vínculo e gravidade; negociação e reparação podem ocorrer ao longo do tempo.
- **Ruptura proporcional:** desentendimento leve não gera saída automática. Ato excepcionalmente grave confirmado pode motivar ruptura imediata, sem obrigação artificial de vários avisos, **mas não dispensa** permissão, viabilidade, gateway e confirmação do host.
- **Estados distintos:** preocupação, aviso, negociação, intenção de recusa, proposta de saída e saída mecânica confirmada são conceitos separados. Protesto textual não é veto efetivo de comandos.
- **Fidelidade:** preservar características e roteiros canônicos de cada NPC, sem sobrepor scripts/banters/romances/quests ou divulgar segredos. IA local só redige falas filtradas sob demanda.
- **Segurança/consistência:** operações mecânicas dependem de POC BG2:EE/EEex multiplayer; checar combate e condições seguras, receipts, idempotência, `UNCERTAIN`, save/load e modos isolados.
- **Arquivos:** `decisions/ADR-0043-protocolo-contextual-de-desacordo-e-ruptura-dos-companheiros-npc.md` e `48-protocolo-de-desacordo-lealdade-recusa-e-ruptura-npc.md`.
- **Próxima:** **DEC-049 — o que acontece com o companheiro após sair do grupo, e como reencontro/recrutamento devem funcionar?**

> **Estado corrente v4.4:** DEC-048 aprovada; DEC-049 aberta. Menções anteriores a DEC-048 como próxima são históricas.


## DEC-049 — Vida autônoma de companheiros após a saída (2026-11-06; Discovery v4.5)

- **Escolha expressa:** opção **B** — companheiros NPC seguem vivendo no Living World após saída efetivamente confirmada do grupo, com identidade, memória, vínculos, objetivos e recursos persistentes.
- **Níveis:** atividades ACTIVE/NEAR detalhadas conforme relevância; DISTANT/DORMANT agregadas por checkpoints e relógio autorizado (DEC-021/022), sem IA por tick.
- **Cânone e segurança:** scripts/romances/quests e disponibilidade por época permanecem protegidos. Projeção de destino não é posição mecânica; spawn, retorno e re-recrutamento requerem compatibilidade, ação permitida e receipt do host.
- **Reencontro:** possível sob condições geográficas/temporais, histórico relacional e elegibilidade do NPC; retorno nunca obrigatório, nem duplica sua presença.
- **Restrições:** mortes e mudanças históricas HIGH não são autoexecutadas offscreen; rumores não são fatos; UNCERTAIN exige reconciliação, saves e Original são isolados.
- **Arquivos:** `decisions/ADR-0044-vida-autonoma-persistente-de-companheiros-apos-saida.md` e `49-vida-autonoma-reencontros-e-recrutamento-de-companheiros-npc.md`.
- **Próxima:** **DEC-050 — conciliação entre roteiros canônicos/nativos e eventos dinâmicos do Infinity AI para companions NPCs**.

> **Estado corrente v4.5:** 44 ADRs aprovadas; DEC-050 aberta. Referências a DEC-049 como aberta/próxima nas seções históricas não indicam seu estado atual.

## DEC-050 — Conciliação do conteúdo nativo com eventos dinâmicos (2026-11-06; Discovery v4.6)

- **Escolha:** **opção C aprovada** — preservar a baseline dos roteiros instalados, admitir propostas narrativas complementares compatíveis e divergências causais autorizadas/tecnicamente verificadas.
- **Regra de conflitos:** reconciliador determinístico identifica dependências/flags conhecidas, tempo DR, reservas de cenas, romances, quests, party e NPC; produz `ALLOW`, `ADAPT`, `DEFER`, `BLOCK` ou `DIVERGENCE_REVIEW`. Não tratar desconhecimento de flag como ausência de conflito.
- **Segurança:** IA não altera roteiros diretamente; eventos mecânicos dependem de Action Gateway, receipt do host, pós-condição, logs e reconciliação em `UNCERTAIN`.
- **Ressalva:** nenhuma leitura/escrita de estados do motor em BG2:EE/EEex multiplayer foi demonstrada nesta etapa. Conteúdo de mods exige inventário específico e testes independentes.
- **Arquivos:** `decisions/ADR-0045-conciliacao-hibrida-de-roteiros-nativos-e-eventos-dinamicos.md` e `50-conciliacao-de-scripts-quests-romances-e-eventos-dinamicos.md`.
- **Próxima:** **DEC-051 — estratégia de inventário versionado de scripts, flags, quests e romances nativos/mods**.

> **Estado corrente v4.6:** 45 ADRs aprovadas, DEC-051 aberta. Declarações antigas de DEC-050 como “próxima” são histórico.

## DEC-051 — Inventário híbrido curado por build (2026-11-06; Discovery v4.7)

- **Escolhida:** opção C — varredura de recursos instalada somente leitura + catálogos curados com proveniência, versão, escopo e cobertura explícita.
- **Separação crítica:** existência de arquivo é fato estático; flags, etapas de quests, romances ativos e estado de NPCs exigem evidência runtime/host. Desconhecido nunca significa inexistente.
- **Compatibilidade:** fingerprint de build, ordem de mods e fontes efetivas. Mudanças invalidam gates dependentes; a política não presume suporte a EET/IWD/NWNForBG.
- **Proteções:** IA não autoriza mutações, inventário não altera recursos; propostas passam pelo reconciliador DEC-050, gateway DEC-012 e host DEC-011.
- **Documentos:** `decisions/ADR-0046-inventario-hibrido-curado-e-versionado-do-conteudo-instalado.md` e `51-inventario-hibrido-de-conteudo-por-build-e-proveniencia.md`.
- **Próxima:** **DEC-052 — política de atualização de builds/mods e migração de campanhas/saves persistentes**.

> **Estado corrente v4.7:** 46 ADRs aprovados, DEC-052 aberta. Menções anteriores a DEC-051 como próxima são histórico.

## DEC-052 — Builds versionadas com migração controlada (2026-11-06; Discovery v4.8)

- **Escolha expressa:** opção C — preservar manifesto/build por campanha; novas versões de jogo/mods somente em ambiente isolado e sem migração automática de saves.
- **Segurança:** backup de componentes mecânicos e narrativos, checkpoint vinculado, diff por build/catálogo, dependências observáveis, ensaio de restauração e testes de progressão. `UNKNOWN` crítico, quest/romance incompatível ou estado `UNCERTAIN` impedem promoção.
- **Evidência/autoridade:** anfitrião aprova explicitamente promoção após resultados verificáveis; host BG2:EE confirma mecânica; serviço narrativo preserva fatos e pendências, sem declaração otimista de conclusão.
- **Resultado conservador:** se a migração falha, manter instalação anterior; restaurar **par coerente** de backups caso tenha ocorrido dano em etapa controlada.
- **Não presumir:** portabilidade universal de saves, migração a quente, rollback atômico, suporte a EET/IWD/NWNForBG ou execução de ferramentas de modding/migração nesta fase.
- **Documentos:** `decisions/ADR-0047-builds-versionadas-e-migracao-controlada-de-campanhas.md` e `52-migracao-controlada-de-builds-e-campanhas-persistentes.md`.
- **Próxima:** **DEC-053 — checkpoints coordenados e recuperação de campanhas entre save mecânico e estado narrativo**.

> **Estado corrente v4.8:** 47 ADRs aprovados, DEC-053 aberta; DEC-013/015/018 seguem abertas. Todas as notas históricas anteriores sobre DEC-052/051 como próximas refletem o estágio anterior.

## DEC-053 — Checkpoints coordenados entre save e memória (2026-11-06; Discovery v4.9)

- **Escolha:** opção C — checkpoint certificado como par de save BG2:EE/host + revisão do snapshot/event log do Infinity AI, com identidade, build, modo, ramo, clock, hash e watermark; somente publicar após verificação.
- **Autoridade:** host confirma a mecânica, log narrativo guarda fatos com evidências; nenhuma transação distribuída entre ambos foi demonstrada.
- **Crash, atraso e rewind:** manter último checkpoint íntegro, reconciliar `UNCERTAIN` sem retry cego, preservar auditoria e isolar ramo se save anterior for carregado com histórico posterior.
- **Segurança:** Original e Living World separados, conhecimento por ACL, recuperação com host + dois clientes nos gates futuros; checkpoint parcial permanece ineligível.
- **Documentos:** `decisions/ADR-0048-checkpoints-coordenados-e-reconciliacao-segura-de-campanhas.md` e `53-checkpoints-coordenados-recuperacao-e-consistencia-da-campanha.md` (24 testes candidatos).
- **Próxima:** DEC-054 — operacionalização de backups/retention/testes de restore, detalhando DEC-018 aberta.

> **Estado corrente v4.9:** 48 ADRs aprovados; DEC-054 aberta. DEC-013/015/018 permanecem abertas. Entradas anteriores com DEC-053 pendente são histórico.


## Atualização DEC-054 — Backup, redundância e restauração verificada (Discovery v5.0)

- **Opção C aprovada:** backups automáticos apenas de checkpoints elegíveis da DEC-053; política de rotação/retention configurável com proteção da última cópia recuperável, pins históricos/pré-migração e dependências de logs.
- **Redundância independente:** disco externo, NAS ou armazenamento remoto **somente por escolha explícita**, sem nuvem obrigatória; remoto criptografado, acesso limitado e risco de perda de chaves documentado.
- **Verificação:** hash/manifesto de cópia + **ensaio isolado de restauração**; continuar quests e sincronizar host + dois clientes requer POC e não pode ser inferido de checksum. Falha torna proteção degradada, nunca sucesso falso.
- **Escopo:** ADR-0049 e documento 54 (28 testes candidatos); não há backup/restauração funcional implementados. DEC-018 ainda aberta para observabilidade e resposta operacional.
- **Próxima:** DEC-055 — monitoramento, alertas e resposta segura a incidentes.

> **Estado corrente v5.0:** 49 ADRs aprovados, DEC-055 aberta; DEC-013/015/018 continuam abertas nas frentes de compatibilidade, gates e operação. Menções históricas à DEC-054 como próxima são etapas anteriores do Discovery.

## Atualização DEC-055 — Monitoramento contínuo e resposta segura (Discovery v5.1)

- **Escolha expressa:** opção C, ADR-0050. World Health Monitor local-first com sondas, estados explícitos de capacidade (`HEALTHY/DEGRADED/UNAVAILABLE/UNKNOWN/UNCERTAIN/RECOVERING/QUARANTINED`) e evidências; não confundir processo saudável com estado de save íntegro.
- **Modo degradado:** suspender só capacidades afetadas quando continuidade segura for demonstrada no build. LLM off não autoriza gerar narrativa falsa; bridge/DB/gateway incertos não autorizam mutações; checkpoint/backup falhos preservam último conjunto válido.
- **Risco e autoridade:** recuperação LOW somente allowlisted/reversível/idempotente; HIGH e UNCERTAIN exigem contenção, reconciliação e, quando aplicável, decisão do anfitrião e receipt do host. Sem auto-rollback/replay ou telemetria externa implícita.
- **Documentos:** `decisions/ADR-0050-monitoramento-continuo-e-recuperacao-segura-por-risco.md` e `55-observabilidade-health-monitor-e-resposta-segura-a-incidentes.md` (28 testes candidatos).
- **Próxima:** DEC-056 — orçamento adaptativo de desempenho e prioridades para simulação/LLM/bridge sem comprometer jogo e estado.

> **Estado corrente v5.1:** 50 ADRs aprovados; DEC-056 aberta. DEC-018 permanece aberta como guarda-chuva operacional, e DEC-013/015/006 continuam requerendo especificação e evidência. As menções antigas a DEC-055 como próxima refletem histórico.

## Atualização DEC-056 — Resource & Performance Director (Discovery v5.2)

- **Opção C aprovada:** prioridades conceituais P0–P4, admissão de tarefas, backpressure, cancelamento somente de trabalho comprovadamente descartável, cotas adaptativas e instrumentação com estado `UNKNOWN` quando ausente.
- **Integridade não preemptível por conveniência:** host continua autoridade mecânica; gateway/receipts, ACL, checkpoints e incidentes `UNCERTAIN` não são descartados por pressão de FPS. Simulação DISTANT/DORMANT cede primeiro à interação, com fairness limitado e catch-up coerente.
- **Escopo das provas:** baseline BG2:EE Windows host+dois clientes, instrumentação de baixo overhead, saturação CPU/RAM/GPU/VRAM/I/O, carga LLM, filas/rewind/restore, build diferente e incidentes. Orçamentos quantitativos pendem de DEC-006/015 e SPECS.
- **Documentos:** `decisions/ADR-0051-gerenciamento-adaptativo-de-recursos-prioridades-e-filas.md` e `56-gerenciador-adaptativo-de-recursos-prioridades-e-filas.md` (28 testes candidatos).
- **Próxima:** DEC-057 — topologia local-first para serviços de IA/simulação em coop, separando colocação física da autoridade do host.

> **Estado corrente v5.2:** 51 ADRs aprovados; DEC-057 aberta. DEC-006/013/015/018 continuam abertas. Registros anteriores que mencionam DEC-056 aberta são históricos.

## Atualização DEC-057 — Execução modular local-first e nós LAN opcionais (Discovery v5.3)

- **Opção C:** sidecars/orquestração no PC Windows anfitrião como baseline e distribuição opcional de workers LLM/simulação em LAN explicitamente configurada; sem nuvem ou segunda máquina obrigatória.
- **Autoridade:** host BG2:EE mantém estado mecânico; retorno do worker é proposta validada, não efeito confirmado. Gateway e revisão/branch/build da campanha continuam obrigatórios. Serviços com estado requerem gates extras antes de relocação.
- **Segurança:** nós não herdam confiança só por pertencer à LAN; limites de ACL, isolamento Original/Living World, consentimento para envio de contexto e conexão protegida pendente da DEC-058.
- **Degradação:** queda de nó permite desabilitar capacidade ou fallback verificado; mutação `UNCERTAIN` não pode ser reexecutada por failover. Qualidade de serviço e budgets seguem DEC-056.
- **Artefatos:** ADR-0052 e documento técnico 57 (24 testes candidatos). Nenhuma POC de LAN, instrumento de rede ou medição de FPS executada.
- **Próxima:** **DEC-058 — pareamento, identidade, descoberta e proteção dos serviços na LAN**; DEC-006/013/015/018 permanecem abertas.

> **Estado corrente v5.3:** 52 ADRs aprovadas, DEC-057 aprovada, DEC-058 aberta. Passagens históricas com versão anterior não representam o estado vigente.

## Atualização DEC-058 — Pareamento assistido e segurança da LAN (Discovery v5.4)

- **Opção C aprovada:** host identifica worker por identidade verificável, verifica seu pareamento e concede permissão explícita por campanha e função. Descoberta automática não significa confiança.
- **Segurança:** canal autenticado e protegido, autorização de menor privilégio, ACL e minimização antes do despacho, rejeição de respostas stale/revogadas e contenção de incidente. Nenhuma confiança implícita em IP, hostname ou LAN.
- **Fronteiras:** worker envia proposta; host confirma efeitos mecânicos; revogar acesso não elimina informação já divulgada a um dispositivo comprometido. Não há serviço de segurança implantado.
- **Documentos:** `decisions/ADR-0053-descoberta-assistida-pareamento-autorizado-e-canais-protegidos-lan.md` e `58-descoberta-pareamento-identidade-e-seguranca-lan.md` (26 testes candidatos).
- **Próxima:** **DEC-059 — roteamento entre modelos/tarefas locais e nós LAN por sensibilidade, recursos, latência e fallback**. DEC-006/013/015/018 permanecem abertas para parâmetros, validação e implementação.

> **Estado corrente v5.4:** 53 ADRs aprovados; DEC-058 aprovada como arquitetura e DEC-059 aberta. Passagens que indiquem DEC-058 aberta são históricas.

## Atualização DEC-059 — Roteamento de modelos por tarefa, privacidade e recursos (v5.5)

- **DEC-059/C aprovada:** primeiro filtrar por contexto/privacidade/autorização, capacidades verificadas e revisão; depois selecionar modelo e worker por adequação, latência/recursos e budgets.
- **Default single-host:** não depende da LAN. Nós autorizados são trabalhadores não autoritativos; não permitem gateway mutativo, saves ou segredos fora do escopo.
- **Fallback:** somente entre recursos igualmente elegíveis; quando não há, usar material previamente aprovado ou aguardar. Sem chamada à nuvem por padrão.
- **Proteções:** no máximo propostas; outputs em schema válido não são automaticamente verdadeiros; branch/build/permission epoch e idempotência impedem reaplicar resultados antigos.
- **Documentos:** `decisions/ADR-0054-roteamento-de-modelos-por-tarefa-privacidade-recursos-e-fallback.md` e `59-roteador-de-modelos-politicas-de-privacidade-qualidade-e-fallback.md` (24 testes candidatos).
- **Próxima decisão:** **DEC-060 — validação de respostas geradas, coerência factual/narrativa e tratamento de riscos**. DEC-006/013/015/018 ainda abertas.

> **Estado corrente v5.5:** 54 ADRs aprovadas, DEC-059 concluída como desenho, DEC-060 aberta. As menções anteriores à DEC-059 como próxima são registros históricos.


## Atualização DEC-060 — Validação híbrida em camadas e proporcional ao risco (Discovery v5.6)

- **Opção C aprovada:** regras determinísticas, ACL, proveniência, conhecimento do NPC, cronologia, cânone, estado de build/quests e políticas de risco antes da publicação.
- **Não equivalências:** fala ≠ fato confirmado; rumor ≠ verdade; aprovação por segundo LLM ≠ evidência suficiente; resposta ≠ comando mecânico.
- **Estados:** `ACCEPT`, `REVISE`, `DEFER`, `REJECT`, `ESCALATE`; falta de evidência crítica ou falha do verificador bloqueia a operação afetada.
- **Artefatos:** ADR-0055 e documento 60 (24 testes candidatos). Sem implementação, métricas ou provas técnicas.
- **Próxima:** **DEC-061 — governança de fontes, evidências conflitantes e curadoria humana do conhecimento canônico**. DEC-006/013/015/018 seguem abertas.

> **Estado corrente v5.6:** 55 ADRs aprovados; DEC-060 concluída; DEC-061 aberta. Passagens anteriores são histórico.

## Adendo à DEC-060 — Partição física anual do lore (Discovery v5.6.1)

- **O idealizador aprovou explicitamente:** diretórios por ano DR, evitando reunir fatos de todos os períodos num corpus único. Para 1369 DR: `knowledge/periods/1369-DR/chronology`, `events`, `organizations`, `guilds`, `characters`, `regions`; 1370 DR em pasta distinta.
- **Resolução contextual:** o recuperador começa no diretório do ano confirmado da campanha e só abre anos anteriores quando há fundamento cronológico e autorização; o futuro não é tratado como consumado. O filtro temporal não substitui ACL/propagação do conhecimento do NPC.
- **Mundo persistente:** alterações dos jogadores são overlays por campanha/ramo/ano, não modificações no cânone curado; versões, fontes e validade impedem identidade/estado obsoletos.
- **Artefatos:** emenda ADR-0055, atualização doc. 60, novo doc. 60a, árvore documental `knowledge/` vazia de fatos, requisitos/riscos e referências cruzadas atualizados.
- **Próxima:** DEC-061 — como resolver conflitos de fonte e diferenças editoriais **dentro** de uma mesma partição anual, sem alucinar consenso.

> **Estado corrente v5.6.1:** **55 ADRs** aprovados (sem ADR novo nesta emenda); DEC-060/C aprovada e emendada; DEC-061 continua aberta. Nenhuma POC de recuperação nem conteúdo de lore implementados.

## DEC-061 — Proveniência, divergências e revisão contextual (2026-11-06; Discovery v5.7)

- **Escolha:** **C**, expressa pelo idealizador. Não há prioridade universal de fonte por edição ou data editorial; cada afirmação deve manter referência, escopo temporal, região/perspectiva e estado de curadoria.
- **Divergências:** distinguir mudanças legítimas no tempo, facções homônimas, rumores, narradores não confiáveis e retcons de contradições irredutíveis. Um LLM ajuda na comparação, mas não determina sozinho a verdade histórica.
- **Revisão:** resolução contextual exige evidência, autor/revisor, motivo, revisão e escopo; alternativas conflitantes são preservadas. Quando `UNRESOLVED`, usar fala prudente/`DEFER`/`ESCALATE` conforme o risco, nunca inventar consenso.
- **Requisito inalterado DEC-060/C:** bases canônicas em **diretórios físicos anuais** (`knowledge/periods/{ano}-DR/`); 1369 busca primeiro 1369, antecedentes explicitamente autorizados, futuro não promovido a fato e overlays por campanha/ramo sem reescrever cânone.
- **Documentos:** ADR-0056, doc. 61 (28 testes candidatos); 60/60a, conhecimento, riscos e requisitos sincronizados. Não há dados históricos curados nem testes de recuperação/engine executados.
- **Próxima decisão:** **DEC-062 — ingestão, revisão e publicação de fontes**, preservando licenciamento, partição anual e auditoria. DEC-006/013/015/018 continuam abertas.

> **Estado corrente v5.7:** 56 ADRs aprovados no Discovery, DEC-061/C aprovada; DEC-062 aberta. As menções anteriores a DEC-061 como futura são históricas.


## DEC-062 — Ingestão híbrida com publicação curada e anual (2026-11-06; Discovery v5.8)

- **Escolha:** opção **C**, comunicada pelo idealizador. Entrada permitida somente a partir de materiais legítimos com direitos/uso verificados; IA propõe entidades, datas e alegações, mas não estabelece fatos canônicos nem decisões de licença.
- **Pipeline:** registro de fonte → quarentena → extração e staging isolados → validação de licença, cronologia, esquema, ACL e proveniência → detecção de conflitos → revisão humana ou política LOW explicitamente autorizada → publicação por revisão anual com rollback editorial e auditoria.
- **DEC-060 mantida:** diretórios **fisicamente separados** `knowledge/periods/<ano>-DR/` e busca semântica restrita por ano; anos anteriores somente se vigência permitida, fatos futuros jamais convertidos em presente. Pastas atuais são andaimes sem lore importado.
- **DEC-061 mantida:** preservar `Source`, `Claim`, `ConflictSet` e resoluções auditáveis; não inventar consenso entre edições ou dentro de um ano.
- **Campanhas:** overlays/eventos confirmados não são reescritos por mudanças no catálogo. Versões aplicadas às campanhas serão tratadas na DEC-063.
- **Artefatos:** `decisions/ADR-0057-pipeline-hibrido-de-ingestao-validacao-e-publicacao-por-ano.md` e `62-pipeline-hibrido-de-ingestao-curadoria-e-publicacao-por-ano.md` (30 testes candidatos).
- **Pendências:** DEC-006/013/015/017/018 e SPECS/POCs. Não houve importação real, teste de engine, benchmark nem verificação de licenças de obras particulares.

> **Estado corrente v5.8:** 57 ADRs aprovados, DEC-062 aprovada, DEC-063 aberta. Menções históricas a DEC-062 aberta são registros do estágio anterior.


## DEC-063 — Knowledge Packs pinados e adoção seletiva (2026-11-06; Discovery v5.9)

- **Escolha expressa:** opção **C**, ADR-0058, doc. 63. Cada campanha/ramo permanece vinculada a um manifesto de **referências imutáveis de revisões anuais**, e não a uma cópia misturada de lore. Catálogo pode mudar sem atualização automática de saves/campanhas.
- **DEC-060 preservada:** pastas físicas `knowledge/periods/<ano>-DR/`, busca restrita ao ano do relógio confirmado, antecedentes só por validade/ACL e nenhum futuro como fato já ocorrido. O manifesto não é corpus universal.
- **DEC-061 preservada:** fontes e alegações concorrentes com proveniência, conflitos não resolvidos e decisões curatoriais versionadas. DEC-062 preservada: novos fatos passam por staging, verificações de direitos/risco e publicação anual aprovada antes de poderem ser propostos às campanhas.
- **Migração:** diff de impacto em missões, personagens, eventos, overlays, ACL, memória e build; selecionar alterações compatíveis, comprovar checkpoint, verificar dependências e obter aprovação explícita do anfitrião (padrão inicial). HIGH/UNCERTAIN segue fail-closed. Fallback/rollback não pode apagar história confirmada.
- **Sem suporte comprovado:** mecanismo de hot-swap, checkpoints e integração de BG2:EE/EEex/multiplayer permanecem para SPECS/POCs; testes T063-01..32 propostos.
- **Próxima:** **DEC-064 — como crenças e memórias de NPCs evoluem após correção do conhecimento**, sem onisciência ou edição retroativa de conversas. DEC-006/013/015/017/018 continuam abertas.

> **Estado corrente v5.9:** **58 ADRs aprovados**, DEC-063/C aprovada; DEC-064 aberta. Menções históricas anteriores de DEC-063 aberta representam versões antigas.


## DEC-064 — Memória persistente e correção contextual de crenças (2026-11-06; Discovery v6.0)

- **Opção C aprovada:** ADR-0059/doc. 64. NPCs preservam testemunhos, observações, rumores e episódios de aprendizagem com proveniência, e atualizam crenças por experiências e evidências legítimas, não por sincronização automática do catálogo.
- **Episódio ≠ crença ≠ fato canônico:** é permitido crer num boato falso. A correção pode gerar dúvida, investigação, aceitação ou rejeição, preservando o histórico da crença e o diálogo passado; um LLM não decide a verdade nem fabrica a fonte.
- **DEC-060 preservada:** cada ano DR continua em diretório físico independente; recuperador seleciona primeiro o ano confirmado e só consulta antecedentes legítimos com vigência/ACL, nunca fatos de anos futuros como consumados. Memórias de NPC ficam no overlay de campanha/ramo, **não no diretório canônico anual**.
- **DEC-061/062/063 preservadas:** fontes e conflitos curados rastreáveis; ingestão em staging e publicação por ano; Knowledge Pack pinado por campanha/ramo não atualiza automaticamente as mentes após migração.
- **Gates narrativos e mecânicos:** DEC-028/029 restringem aquisição, DEC-060 valida saídas, gateway/host validam ações e DEC-030/035/036/037 regulam reputação/alinhamento. Sem onisciência, retcon de diálogos, LLM por NPC/tick ou atualização de save por suposição.
- **Pendências:** 30 testes candidatos, não executados. DEC-006/007/013/015/017/018 continuam abertas. **Próxima DEC-065** — retenção, consolidação e possível esquecimento de experiências NPC sem perda de eventos críticos.

> **Estado corrente v6.0:** **59 ADRs aprovados**, DEC-064/C aprovada como desenho, DEC-065 aberta. Menções anteriores a DEC-064 como futura são histórico.


## DEC-065 — Memória hierárquica, consolidação e proteção de âncoras (2026-11-06; Discovery v6.1)

- **Opção C aprovada:** ADR-0060/doc. 65. Memória imediata, episódios com evidência, sínteses semânticas reconstruíveis e âncoras críticas protegidas. Recuperar contexto relevante dentro de orçamento, sem enviar toda história ao LLM e sem expirar experiências apenas por idade.
- **Proveniência:** cada síntese aponta para episódios/fonte/revisão; não cria fato canônico, testemunho, confirmação mecânica ou crença sem evidência. Crenças continuam revisáveis pela DEC-064; rumores permanecem perspectiva subjetiva.
- **Separação física por ano DR DEC-060 preservada:** `knowledge/periods/<ano>-DR/` para cânone; memórias NPC permanecem em projeções da campanha/ramo. DEC-061/062/063 continuam exigindo proveniência, publicação curada e Knowledge Pack pinado por campanha.
- **Proteção e privacidade:** detalhes críticos, segredos, compromissos, mortes, relações e marcos são protegidos contra compactação inadvertida mas somente recuperados com ACL; proteção não elimina obrigações legítimas de expurgo/redação. Cache, retenção e descarte são operações distintas.
- **Segurança e execução:** host/gateway DEC-011/012, ACL DEC-028/029, checkpoint DEC-053/054, scheduler DEC-056, Model Router DEC-059 e validação DEC-060. Sem LLM em loop por NPC, sem síntese stale/UNCERTAIN.
- **Evidência:** 32 testes candidatos **não executados**; sem POCs de NPC/EEex, benchmarks, parâmetros numéricos ou APIs definitivas. DEC-006/007/013/015/017/018 abertas.
- **Próxima DEC-066:** identidade persistente e correspondência segura de NPCs entre saves, áreas, respawns e versões de build; não assumir IDs temporários estáveis.

> **Estado corrente v6.1:** **60 ADRs aprovados**, DEC-065/C aprovada como desenho e DEC-066 aberta. Menções anteriores de DEC-065 aberta são históricas.


## DEC-066 — Identidade lógica persistente e correspondência verificada (2026-11-06; Discovery v6.2)

- **Opção C escolhida:** ADR-0061 e documento técnico 66. Identidade lógica persistente por campanha/ramo distinta de instância/runtime/observação do BG2:EE; evidência positiva e compatível para vinculação. Nome, área, aparência, CRE/script ou ID isolados nunca comprovam correspondência.
- **Ambiguidade fail-closed:** `CANDIDATE` não tem autorização para revelar memória; `AMBIGUOUS`, `STALE`, ID reciclado, duplicata de spawn, fork ou migração incompatível impedem ligação automática. Fala genérica não personalizada poderá ser permitida sob ACL.
- **DEC-060–065 preservadas integralmente:** cânone **fisicamente particionado por ano DR**; proveniência/conflitos, staging de ingestão controlada, Knowledge Pack pinado por campanha; experiências, crenças e sínteses NPC no overlay da campanha/ramo, sem cópia para diretório anual. Revisões de identidade não reescrevem acontecimentos confirmados.
- **Consistência:** bridge/host, idempotência, checks/reconciliation, alinhamento de fingerprint da build, snapshots DEC-053/054 e autorização de segredos DEC-028. Nenhuma API EEex ou ID estável demonstrados; 34 testes candidatos não executados.
- **Próxima DEC-067:** política para persistência seletiva e promoção progressiva de NPCs genéricos vs únicos. DEC-006/007/013/015/017/018 continuam abertas.

> **Estado corrente v6.2:** 61 ADRs aprovados, DEC-066/C registrada como desenho e DEC-067 aberta. Histórico anterior que mencione DEC-066 aberta é registro cronológico.

## DEC-067 — Individualização híbrida e promoção progressiva (2026-11-06; Discovery v6.3)

- **Escolha expressa:** opção **C**, formalizada no ADR-0062 e no documento 67. NPCs únicos e companions têm prioridade; personagens genéricos começam como população agregada/instâncias efêmeras e podem ganhar identidade e memória persistentes por acontecimentos significativos confirmados.
- **Identidade não é relevância:** a promoção requer correspondência segura **DEC-066** e vínculo causal verificável; nomes, CREs, sprites e respawns iguais não são prova. `AMBIGUOUS`, `STALE` e `UNCERTAIN` não autorizam memória individual; possível diálogo genérico sem reconhecimento.
- **Custo e coerência:** transição agregado→indivíduo com revisão/idempotência, sem simulação ou spawn duplicado; não exigir LLM contínuo. Regiões DEC-021, relógio DEC-022 e RPD DEC-056 determinam a prioridade. Compromissos e efeitos mecânicos dependem de host/gateway, ACL, risco e checkpoints.
- **DEC-060–066 preservadas integralmente:** cânone fisicamente particionado por ano DR, proveniência e conflitos curados, staging de ingestão, packs versionados por campanha, memória/credo individual em overlay privado, consolidação auditável e prova de identidade. ADR-0055 a ADR-0061 imutáveis.
- **Testes:** 36 candidatos `T067-*` **não executados**; IDs estáveis, spawns e compatibilidade BG2:EE/EEex/multiplayer ainda sem POC.
- **Próxima:** **DEC-068 — como NPCs persistentes evoluem/hibernam fora de cena**, mantendo lembranças e consequências enquanto controlamos recursos. DEC-006/007/013/015/017/018 continuam abertas.

> **Estado corrente v6.3:** 62 ADRs aprovados, DEC-067/C registrada em Discovery, DEC-068 aberta. Menções históricas a DEC-067 aberta são registros de versões anteriores.


## DEC-068 — Vida persistente com atividade adaptativa e hibernação (2026-11-06; Discovery v6.4)

- **Escolha expressa:** opção **C**, formalizada no ADR-0063 e no documento 68. NPCs individualizados DEC-067 preservam identidade, memórias, crenças e compromissos mesmo fora de cena. `DORMANT` suspende execução, não equivale a esquecimento, morte ou desindividualização.
- **Atividade proporcional:** `ACTIVE/NEAR/DISTANT/DORMANT` são níveis de custo e detalhe DEC-021/056, não evidência de NPC mecanicamente presente em qualquer mapa. IA só sob demanda; processamento distante por regras e lotes, não simulação individual por tick.
- **Retomada segura:** relógio configurável `FROZEN/PARTIAL/REALTIME` DEC-022, catch-up delimitado, jobs duráveis/idempotentes, verificação de `NPCIdentity`, branch, build, KPack, ACL e checkpoint. `UNCERTAIN`, `STALE` ou ausência de receipt impede publicar efeitos mecânicos; nenhum evento HIGH ou irreversível é inferido no intervalo.
- **DEC-060–067 integralmente preservadas:** cânone **fisicamente particionado por ano DR**, fontes com proveniência, staging curado, packs fixados por campanha, memórias epistêmicas/episódicas privadas, identidade verificada e agregado→individual sem duplicação. ADR-0055–0062 idênticos à v6.3.
- **Limites:** 36 testes `T068-*` candidatos **NÃO EXECUTADOS**; não foi comprovado pathfinding, persistência de NPC genérico ou controle em multiplayer do BG2:EE/EEex. DEC-006/007/013/015/017/018 continuam abertas.
- **Próxima DEC-069:** deslocamento espacial entre regiões e conciliação de itinerário narrativo com presença mecânica confirmada.

> **Estado corrente v6.4:** 63 ADRs aprovados, DEC-068/C documentada como arquitetura, DEC-069 aberta. Menções anteriores a DEC-068 aberta são históricas e preservadas deliberadamente.

## DEC-069 — Itinerários hierárquicos e presença mecânica verificada (2026-11-06; Discovery v6.5)

- **Escolha expressa:** opção C, registrada em `ADR-0064` e documento 69. NPCs individuais têm rotas regionais propostas/validadas por segmentos, tempo e restrições curadas; nada exige pathfinding contínuo em regiões não carregadas.
- **Separação de evidências:** plano/partida narrativa, trânsito, chegada narrativa e observação mecânica são estados distintos; área do lore não significa área de BG2:EE, e `ARRIVED_NARRATIVE` não cria `ENGINE_PRESENT`. Motor e host confirmam efeitos físicos; workers LLM não.
- **Consistência:** grafo temporal com proveniência, Knowledge Pack fixado, branch/checkpoint, NPCIdentity `VERIFIED`, relógio DEC-022, estados ACTIVE/NEAR/DISTANT/DORMANT, idempotência e fail-closed para `STALE/UNCERTAIN`. Evitar teleporte, presença simultânea e biografias inventadas.
- **Preservação integral:** DEC-060–068 e ADR-0055–0063 permanecem inalterados; cânone fisicamente separado por ano DR, fontes curadas, memórias privadas por campanha/ramo.
- **Evidências:** 40 testes `T069-*` candidatos **não executados**, sem suporte BG2:EE/EEex/EET/multiplayer confirmado. DEC-006/007/013/015/017/018 continuam em aberto.
- **Próxima DEC-070:** políticas de encontros, imprevistos e riscos das viagens fora de cena, sem efeitos irreversíveis automáticos.

> **Estado corrente v6.5:** 64 ADRs aprovados, DEC-069/C documentada como arquitetura, DEC-070 aberta. Indicações anteriores de DEC-069 em aberto são histórico preservado.

## DEC-070 — Incidentes de viagem por risco e confirmação (2026-11-06; Discovery v6.6)

- **Escolha expressa:** opção **C**, formalizada no ADR-0065 e documento 70; incidentes ancorados a itinerário/segmento DEC-069, calendário, evidência e NPCIdentity.
- **LOW:** somente fatos narrativos seguros por regra curada allowlisted, permissão, idempotência e limites; **MEDIUM:** análise contextual e autorização aplicável; **HIGH:** bloqueio inicial até gates especiais, observação/receipt host para efeito mecânico. Impacto cumulativo pode elevar a categoria.
- **Comportamento proibido:** inferir ataque realizado por perigo regional; declarar mortes, ferimentos, saque, XP, reputação mecânica, quest, guerra ou combate de engine apenas por narração. UNKNOWN/UNCERTAIN permanece sem commit.
- **DEC-060–069 preservadas integralmente:** fontes em diretórios **fisicamente separados por ano DR**, proveniência/curadoria, staging, Knowledge Pack por campanha, memória/identidade NPC, hibernação e itinerários. ADR-0055 a ADR-0064 não alterados. Incidentes ficam em overlays privados da campanha/ramo.
- **Testes:** 44 candidatos T070-01..T070-44; nenhum executado, sem comprovação BG2:EE/EEex/multiplayer. DEC-006/007/013/015/017/018 permanecem abertas.
- **Próxima DEC-071 (em aberto):** transição controlada de incidente fora de cena para encontro jogável quando os jogadores se aproximam, com congelamento de resolução offscreen e host/gateway.

> **Estado corrente v6.6:** 65 ADRs aprovados, DEC-070/C registrada como arquitetura; DEC-071 aberta. Registros históricos anteriores de DEC-070 em aberto são preservados como histórico.

## DEC-071 — Transição controlada offscreen → encontro local (2026-11-06; Discovery v6.8)

- **Aprovada opção C:** incidente DEC-070 pode virar oferta jogável quando jogadores estiverem próximos e o host, a área, a build, NPCs, conteúdo e risco forem verificados. A verificação de presença não materializa automaticamente atores ou combate.
- **Exclusividade por incidente:** uma única resolução válida entre filas distante/local, com reserva persistida, revisão monotônica, idempotência, fencing e reconciliação. `UNCERTAIN` suspende ações e impede reenvio cego.
- **Autoridade e consentimento:** gateway DEC-012 e host DEC-011 controlam comandos e efeitos; clientes não confirmam mecânica. Risco DEC-027/070 e proteção de quests DEC-050 permanecem; nenhuma implantação assumida.
- **DEC-060–070 preservadas integralmente:** canônico fisicamente separado por ano DR, origens e Knowledge Packs controlados, memórias NPC e overlay por campanha/ramo. Os ADRs anteriores não mudaram.
- **Artefatos:** ADR-0066; documento técnico 71; **46 testes T071-* candidatos NÃO EXECUTADOS**. Próxima DEC-072 (aberta): catálogo/templates de encontros locais com compatibilidade verificada por build.

> **Estado corrente v6.7:** 66 ADRs aprovados, DEC-071/C documentada como arquitetura e DEC-072 em aberto. As referências históricas acima a DEC-071 em aberto são mantidas somente como histórico.

## DEC-072 — Catálogo modular de encontros validado por build (2026-11-06; Discovery v6.8)

- **Escolha expressa:** opção **C**, ADR-0067/documento 72. Templates, componentes e adapters são inventariados com proveniência, permissões, dependências, compatibilidade e capability específica comprovada por build; geração de recursos de engine livre em runtime não está autorizada.
- **Separação de responsabilidades:** DEC-071 reserva um incidente elegível contra dupla resolução; DEC-072 seleciona/compõe *proposta* de encontro, sem afirmar spawn ou efeito mecânico. Host/gateway permanecem autoridades para mudanças confirmadas.
- **Gates por build:** distinguir presença de arquivos de suporte real de integração; mod atualizado, área inexistente, quest/romance conflitante, NPC ambíguo, scripts sem POC ou falta de direitos bloqueiam utilização.
- **Expansão offline:** staging, análise de licença, validação estática, POCs isoladas, teste host+dois clientes e rollback antes de habilitar packs. Nenhuma capacidade EEex foi demonstrada e nenhuma obra importada.
- **DEC-060–071 preservadas:** cânone particionado fisicamente por ano DR, fontes curadas, packs versionados por campanha, memórias em overlays, identidade confirmada, itinerário, incidentes e ledger de handoff. ADR-0055..0066 não alterados.
- **Testes:** T072-01..48 são **candidatos NÃO EXECUTADOS**. **Próxima DEC-073:** ownership e limpeza seletiva/persistência pós-encontro. DEC-006/007/013/015/017/018 seguem abertas.

> **Estado corrente v6.8:** 67 ADRs, DEC-072/C aprovada como arquitetura e DEC-073 aberta. As menções anteriores a DEC-072 aberta representam o histórico de decisões.

## DEC-073 — Persistência seletiva e limpeza pós-encontro segura (2026-11-06; Discovery v6.9)

- **Escolha expressa:** opção **C**, ADR-0068 e documento técnico 73. Concluir um incidente/encounter não dá licença para apagar tudo nem para manter lixo indefinidamente. Separar por ownership **comprovado da instância**, origem native/mod/temp/transferida, receipt de host e eventos de campanha.
- **Confirmar antes de limpar:** capacidade por build/adapter testado (DEC-072), riscos e autorizações, checkpoint/backup, ledger único/lease DEC-071 e recibos mecânicos (DEC-011/012). Save/load, crash ou resultado `UNCERTAIN` suspende operações e impede retry destrutivo cego.
- **Proteção de consequências:** itens coletados, inventários, flags nativas, NPCs persistentes, memórias, quest e repercussões não são apagados por limpeza de uma representação temporária. Ausência de capability implica pendência observável, não sucesso fictício.
- **Preservação integral DEC-060–072:** diretórios históricos fisicamente separados por ano DR, fontes/proveniência curadas, Knowledge Packs e overlays de campanha, identidade/memória NPC, viagens, incidentes, handoff e catálogo de composição. ADR-0055..0067 iguais aos da v6.8.
- **Evidência:** 50 testes candidatos `T073-*`, todos **não executados**; nenhuma POC de limpeza, spawn, save ou multiplayer BG2:EE/EEex. DEC-006/007/013/015/017/018 abertas.
- **Próxima DEC-074:** propagação de consequências confirmadas a rumores, relações, reputação, facções e economia sem onisciência e sem dupla aplicação.

> **Estado corrente v6.9:** 68 ADRs aprovados; DEC-073/C documentada como arquitetura e DEC-074 em aberto. Referências a DEC-073 em aberto nas seções anteriores são históricas.


## DEC-074 — Propagação causal gradual das consequências (2026-11-06; Discovery v7.0)

- **Escolha expressa:** opção **C**, ADR-0069/documento 74. Encerramentos confirmados DEC-071/073 originam propostas de difusão via testemunhas, relatos, rotas e vínculos, sujeitos a hora/região/ACL e prova de conhecimento.
- **Distinções:** fato confirmado, alegação/rumor, crença individual e consequência social/econômica não se confundem. Uma notícia não é um ganho de reputação mecânica nem uma decisão de facção por si só.
- **Gates:** reputação DEC-030 contextual; economia/facções DEC-031–033 com causalidade e limites; DEC-027/034 HIGH bloqueados por padrão; host/gateway para qualquer efeito de engine; ledger por causa/alvo/regra evita efeitos duplicados.
- **DEC-060–073 preservadas:** diretórios históricos separados **fisicamente por ano DR**, proveniência e packs por campanha, memórias NPC, viagens e handoff/cleanup. ADR-0055..0068 idênticos à v6.9.
- **Testes:** `T074-01..T074-52` são candidatos **NÃO EXECUTADOS**, sem POCs BG2:EE/EEex/multiplayer. DEC-006/007/013/015/017/018 abertas.
- **Próxima DEC-075:** autoria, crédito e responsabilidade por ações cooperativas, diferenciando participação real da percepção pública e rumores.

> **Estado corrente v7.0:** 69 ADRs aprovados, DEC-074/C documentada apenas como arquitetura e DEC-075 aberta. Seções anteriores que citam DEC-074 em aberto são registros históricos.

## DEC-075 — Atribuição causal e reconhecimento em ações cooperativas (2026-11-06; Discovery v7.1)

- **Opção C aprovada:** autoria e contribuição confirmadas por evidências distintas de testemunhos, crenças e fama pública. Registrar suporte, cura, proteção, negociação e responsabilidade coletiva legítima, mas nunca inventar granularidade que o BG2:EE/EEex não tenha mostrado.
- **Contribuição ≠ reconhecimento:** testemunhas podem desconhecer autores reais ou atribuir crédito erroneamente como crença, sem reescrever evento confirmado. Sem prova individual, `UNKNOWN` ou `PENDING_EVIDENCE`, não punição ou score arbitrário.
- **Segurança cooperativa:** distinguir PC, titular e controlador temporário; ausentes não recebem culpa automaticamente. Respeitar DEC-041/042/045/046, ACL, segredos e consentimento. XP, itens, alinhamento e reputação mecânica exigem gateway/host/capability e gates de risco.
- **Ledger e integridade:** idempotência por evento/ator/tipo de atribuição/regra/branch, recibos e checkpoint; relatos múltiplos não multiplicam consequências. `UNCERTAIN` suspende, sem retry cego; retificações preservam histórico.
- **DEC-060–074 preservadas:** cânone em diretórios físicos independentes por ano DR, fontes curadas, Knowledge Pack pinado; fatos de jogo, testemunhos e crédito no overlay privado de campanha/ramo. ADR-0055 a ADR-0069 não alterados.
- **Artefatos:** ADR-0070 e documento técnico 75; **54 testes T075-* candidatos NÃO EXECUTADOS**. Sem POC BG2:EE/EEex/multiplayer; DEC-006/007/013/015/017/018 abertas.
- **Próxima DEC-076:** identidade verdadeira privada vs. identidade pública/pseudônimo/disfarce, com ligação ou revelação apenas por evidência contextual e autorização.

> **Estado corrente v7.1:** 70 ADRs aprovados; DEC-075/C registrada como arquitetura; DEC-076 aberta. Menções históricas acima a DEC-075 aberta não invalidam o estado corrente.

## DEC-076 — Identidade factual privada e personas públicas (2026-11-06; Discovery v7.2)

- **Escolha expressa C:** ADR-0071 e documento 76; um `FactualActorIdentity` privado pode portar múltiplas `Persona` públicas, enquanto NPCs/facções mantêm crenças individuais, não acesso direto ao segredo. Homonímia e múltiplos aliases não comprovam vínculos.
- **Vínculos e revelação:** separar `SUSPECTED`, `VERIFIED_PRIVATE`, `DISCLOSED_TO_SCOPE`, `DISPUTED` e `REVOKED`; evidência/proveniência/ACL/consentimento e cronologia determinam cada transição. Revelação a um NPC não equivale a revelação pública.
- **Consequências:** reputações por persona e comunidade não se fundem automaticamente; DEC-029/030/074/075 regulam relatos, mérito e efeitos. Nenhum LLM presume observabilidade de disfarce ou altera mecânica sem capability/host receipt.
- **Preservação integral:** DEC-060–075 e ADR-0055–0070 preservados byte a byte. Cânone em diretórios físicos anuais DEC-060, personas e segredos em overlay privado por campanha/ramo.
- **Teste:** 56 cenários T076-01..56 candidatos, **NÃO EXECUTADOS**. Próxima DEC-077: investigação gradual por pistas e contestação sem exposição indevida.

> **Estado corrente v7.2:** 71 ADRs aprovados; DEC-076/C documentada apenas como arquitetura; DEC-077 em aberto. Seções históricas podem referir DEC-076 como futura.

## DEC-077 — Investigação progressiva de identidades secretas (2026-11-06; Discovery v7.3)

- **Opção C aprovada:** registro de pistas e provas com fonte, ancestralidade, tempo e audiências autorizadas; contraditório e ausência de evidência resultam em estado inconclusivo, não na revelação do segredo.
- **Separações obrigatórias:** fato privado ≠ alegação, suspeita ou crença ≠ verificação privada ≠ divulgação. Mesmo um vínculo verificado internamente não é conhecimento universal; a LLM não atribui identidade por conta própria.
- **Gates:** revisões, consentimento e ACL de PCs (DEC-019/028/041/045/046); divulgação MEDIUM/HIGH conforme DEC-027/034; nenhum efeito mecânico sem gateway e confirmação host.
- **DEC-060–076 preservadas:** lore canônico físico por ano DR, fontes curadas, Knowledge Packs pinados; fatos de campanha e investigações em overlay por campanha/ramo; ADR-0055–0071 e todos demais ADRs anteriores byte a byte idênticos à v7.2.
- **Artefatos:** ADR-0072/documento técnico 77; **58 testes T077-01..58 candidatos NÃO EXECUTADOS**. Sem implementação BG2:EE/EEex/multiplayer.
- **Próxima DEC-078 (aberta):** política de acusações, decisões de autoridades e consequências regionais; A) sanções automáticas; B) efeitos narrativos apenas; **C) procedimento contextual, contraditório e controle de risco/autoridade**.

> **Estado corrente v7.3:** 72 ADRs aprovados; DEC-077/C documentada apenas como arquitetura; DEC-078 aberta. Menções anteriores a DEC-077 em aberto representam histórico.

## DEC-078 — Procedimentos jurídicos/faccionais contextuais (2026-11-07; Discovery v7.4)

- **Opção C aprovada:** ADR-0073 e documento 78. Cada autoridade opera regras próprias curadas por região, facção e vigência DR; competência real/poder de facto podem divergir, sem códigos legais globais inventados.
- **Fato ≠ acusação ≠ decisão oficial ≠ efeito mecânico:** denúncias e testemunhos podem estar errados; autoridade pode ser injusta sem reescrever o evento confirmado. Contraditório segue a política da autoridade e dá lugar a contestação/rastreabilidade quando possível, sem pressupor direitos processuais universais.
- **Código primeiro:** regras determinísticas de competência, estados, provas, risco e autorização; LLM local somente para linguagem permitida, nunca arbitra culpa ou aciona engine. Sanções exigem gates DEC-027/034/041 e host/gateway DEC-011/012 com POC por build.
- **Integridade:** case/decision/effect ledgers versionados e idempotentes; `UNCERTAIN`, divergência de ramo/save, disputa de jurisdição e ausência de capacidade bloqueiam ações irreversíveis. NPCs não surgem por teleporte e notícias obedecem canais DEC-029/074.
- **DEC-060–077 preservadas integralmente:** arquivos canônicos fisicamente separados por ano DR, proveniência e packs por campanha, identidades/pistas e casos no overlay privado; ADRs anteriores idênticos à v7.3.
- **Evidência:** 60 testes `T078-01..60` candidatos NÃO EXECUTADOS; nenhuma POC comprovada. Próxima **DEC-079 em aberto**: cooperação e conflitos de autoridade/mandados entre regiões e facções.

> **Estado corrente v7.4:** 73 ADRs aprovados como arquitetura; DEC-078/C documentada e DEC-079 aberta. Menções históricas anteriores a DEC-078 aberta são etapas já superadas.

## DEC-079 — Cooperação e reconhecimento interjurisdicional (2026-11-07; Discovery v7.5)

- **Opção C aprovada:** ADR-0074/doc.79. Pedidos de informação, investigação, notificação, coerção e extradição são enviados por canais/tempos plausíveis; cada autoridade avalia competência, autenticidade, relação política e condições de seu território. Nenhum mandado tem validade universal automática.
- **Distinção causal:** decisão local, emissão, transmissão, recibo de entrega, reconhecimento e execução são eventos diferentes. Rumores, pseudônimos e pedidos forjados não geram prisão ou culpa mecânica; `UNCERTAIN/STALE/DISPUTED` bloqueiam coerção.
- **Gates:** DEC-027/034/041/042 risco/consentimento e DEC-011/012 host/gateway, recursos/áreas DEC-051/069/071/072; sem POC de captura, guardas teletransportados, confisco ou mudanças em quest/rep. Preferir código determinístico, LLM local só sob demanda filtrada.
- **DEC-060–078 preservadas integralmente:** cânone em diretórios físicos anuais por DR, proveniência, packs por campanha e overlays isolados; ADR-0055–0073 intactos. **62 testes T079-* candidatos NÃO EXECUTADOS.**
- **Próxima DEC-080:** revalidação, transmissão e contenção de pedidos que foram revogados, corrigidos ou tornaram-se obsoletos entre autoridades distantes.

> **Estado corrente v7.5:** 74 ADRs aprovados, DEC-079/C registrada e DEC-080 aberta. O histórico de DEC-079 em aberto em documentos anteriores permanece como referência temporal.

## DEC-080 — Revogações versionadas e validação segura de ordens (2026-11-07; Discovery v7.6)

- **Escolha expressa:** opção C, ADR-0075/doc. 80; emitir, retificar, suspender, expirar ou revogar são eventos distintos versionados por autoridade/caso. Mensagem em trânsito não é recebimento; recebimento não é reconhecimento nem execução.
- **Separação de estado e conhecimento:** a origem pode ter revogado enquanto o destinatário ainda crê na versão antiga; o gate de segurança impede atos coercitivos HIGH com prova de status revogado ou incerto **sem transmitir a informação privada para a mente do NPC**.
- **Anti-ressurreição de mandados:** revisões monotônicas, tombstones, idempotência, origem autenticada, reconciliação UNCERTAIN/STALE e prioridade de revogações, sem emissão de perseguição/captura mecânica presumida.
- **Sem apagar história:** danos reais anteriores não desaparecem; reparação específica ainda será discutida na DEC-081. Código determinístico e autoridade do host prevalecem sobre LLM.
- **DEC-060–079 preservadas:** base canônica fisicamente separada por ano DR, proveniência, staging/Knowledge Packs, memória e identidade, casos/mandados no overlay por campanha. Todos os ADRs prévios mantidos byte a byte.
- **Evidência:** 64 testes candidatos T080-01..64 **NÃO EXECUTADOS**, sem POCs de BG2:EE/EEex/multiplayer. DEC-006/007/013/015/017/018 continuam abertas.
- **Próxima DEC-081:** política de revisão e reparações contextualizadas por caso, sem rollback fictício.

> **Estado corrente v7.6:** 75 ADRs aprovados; DEC-080/C registrada como arquitetura e DEC-081 em aberto. Referências anteriores a DEC-080 como aberta permanecem no histórico.

## DEC-081 — Reparação contextual e proporcional de injustiças (2026-11-07; Discovery v7.7)

- **Opção C aprovada:** ADR-0076/documento 81. Revogação é evento distinto de dano comprovado, avaliação de causalidade e autorização/execução de remédio; pedidos podem ser parciais, contestados ou impossíveis.
- **Exemplos de remédios:** retratação, reabilitação social, pedido de desculpas, restituição de itens, compensação e revisão de quest/liberdade, cada qual com competência, proprietário, fonte, consentimento e gate de risco. Host confirma apenas efeitos realmente realizados.
- **Sem rewind:** ações ocorridas continuam no histórico, NPCs só conhecem correções por canais legítimos; dinheiro/itens não são recriados automaticamente. `UNCERTAIN`, restore ou build sem capability bloqueiam mutações.
- **Preservação DEC-060–080:** cânone em pastas fisicamente separadas por ano DR; Knowledge Packs versionados, memórias NPC, ledger de incidentes, mandados e revogações. ADR-0055–0075 byte a byte intactos; reparações no overlay privado do ramo.
- **Validação:** 66 testes T081 candidatos **NÃO EXECUTADOS** e sem provas BG2:EE/EEex/multiplayer. Questões abertas históricas DEC-006/007/013/015/017/018 mantidas.
- **Próxima DEC-082 aberta:** accountability de autoridades e instituições em ações injustas, sem punição automática e sem confundir autoridade ficcional com host do motor.

> **Estado corrente v7.7:** 76 ADRs aprovados como arquitetura, DEC-081/C registrada e DEC-082 aberta. Referências históricas a DEC-081 aberta permanecem como histórico, não como status atual.

## DEC-082 — Responsabilização contextual de agentes e instituições (2026-11-07; v7.8)

- **Escolha C:** ADR-0077 e documento 82. Distinguir alegação, prova, conclusão institucional, responsabilidade individual, responsabilidade de comando, omissão e padrão organizacional. Organograma ou cargo não comprovam culpa.
- **Competência e época:** poder de investigar/rever/decidir depende de fonte canônica regional e do ano DR. Sem fonte: `PENDING_POLICY`, sem fabricar lei moderna universal.
- **Gates e host:** decisão de autoridade pode ser injusta sem mudar a verdade factual; LLM não julga automaticamente. Sanção, demissão, mudança governamental, prisão e efeitos mecânicos só após gates pertinentes e receipts do host quando houver capacidade realmente demonstrada.
- **Separação:** reparação da vítima DEC-081 não comprova responsabilidade do agente. Divulgação de rumores e reputação DEC-029/030/074 é causal, localizada e não universal.
- **Integridade:** DEC-060–081 e ADR-0001..0076 mantidos byte a byte. Cânone em `knowledge/periods/<ano>-DR/` fisicamente separado, impactos em overlays privados de campanha/branch.
- **Testes:** 68 candidatos `T082-01..68` NÃO EXECUTADOS. Sem implementação BG2:EE/EEex/multiplayer. **Próxima DEC-083:** proteção de testemunhas e denunciantes. DEC-006/007/013/015/017/018 mantidas abertas.

> **Estado corrente v7.8:** 77 ADRs aprovados; DEC-082/C documentada como arquitetura; DEC-083 aberta. Menções antigas a DEC-082 em aberto são registros históricos.

## DEC-083 — Proteção contextual de denunciantes e testemunhas (2026-11-07; Discovery v7.9)

- **Opção C aprovada:** `ProtectedSourceIdentity` separada de `TestimonyRecord`, `EvidenceProvenance`, `RetaliationRiskAssessment` e `DisclosureRequest`. Depoimento pode ser examinado por extrato/versão filtrada sem divulgar fonte. Sigilo não comprova acusação.
- **ACL e consentimento:** finalidade, destinatário, competência e risco determinam divulgação; outros PCs, NPCs, autoridades e nós LAN não recebem nomes por padrão. Histórico/segredos de PC sob DEC-019/028/041/045/046.
- **Causalidade e segurança:** testemunha pode sofrer riscos narrativos, mas não se torna invulnerável; não criar captura, teleporte, escolta ou ocultação mecânica sem host/capability/POC. Relatos devem ter origem rastreável e independência DEC-061/077.
- **Dados:** identidades/depoimentos de campanha somente no overlay privado por ramo; cânone continua em diretórios físicos anuais `knowledge/periods/<ANO>-DR/` da DEC-060, com Knowledge Pack pinado DEC-063.
- **Idempotência:** disclosure por audiência e revisão; retificação/revogação afeta acessos futuros, sem apagar conhecimento histórico de NPCs nem reproduzir revelações `UNCERTAIN` às cegas.
- **Preservação integral DEC-060–082:** ADR-0001..ADR-0077 idênticos à versão 7.8. **70 testes T083-* candidatos NÃO EXECUTADOS**; nenhuma POC do motor realizada.
- **DEC-084 aberta:** respostas graduais a ameaças/retaliações e proteção ativa sem imunidade fictícia nem ações mecânicas não testadas.

> **Estado corrente v7.9:** 78 ADRs aprovados; DEC-083/C arquitetura apenas e DEC-084 em aberto. Menções mais antigas à DEC-083 em aberto são históricas.

## DEC-084 — Proteção contextual e gradual contra ameaças/retaliações (2026-11-07; Discovery v8.0)

- **Opção C aprovada:** ADR-0079 / doc 84; separar alegação de ameaça, prova, avaliação de risco, plano e resultado. Relatos não comprovam perseguidor, tampouco risco alto permite ataque automático.
- **Resposta:** discrição, procura de aliados/abrigo, escolta ou realocação como propostas com consentimento, NPCs/recursos disponíveis, itinerário DEC-069, tempo DEC-022 e autoridade regional. Nenhuma invulnerabilidade, teleporte, escolta criada sem prova ou vitória garantida.
- **Gates:** código primeiro; LLM local sob demanda redige narrativa sem autorizar estados/efeitos. Presença, combate, inventário, captura, morte e quests apenas após gateway DEC-012, host DEC-011, adapter/POC por build e receipts. HIGH default-deny, handoff único DEC-071 e cleanup seguro DEC-073.
- **Segurança:** proteger fonte, refúgio e itinerários por ACL, consentimento DEC-019/041/045/046 e filtragem pré-LLM/LAN; adversários não recebem automaticamente os planos. Save/load e branch stale bloqueiam duplicatas.
- **DEC-060–083 integralmente preservadas:** cânone fisicamente particionado por ano DR, Knowledge Packs curados e memória/estado de campanha em overlays separados; ADR-0001..0078 idênticos à v7.9.
- **Validação:** 72 testes `T084-*` candidatos **NÃO EXECUTADOS**, nenhum mecanismo BG2:EE/EEex multiplayer de escolta/abrigo/realocação demonstrado. DEC-006/007/013/015/017/018 seguem abertas.
- **DEC-085 em aberto:** proteção do sigilo operacional versus descoberta legítima por NPCs/facções sem onisciência.

> **Estado corrente v8.0:** 79 ADRs aprovados; DEC-084/C registrada apenas como arquitetura; DEC-085 aberta. Referências anteriores a DEC-084 como tema futuro são históricas.

## DEC-085 — Sigilo operacional, vazamento causal e replanejamento (2026-11-07; Discovery v8.1)

- **Escolha expressa C, ADR-0080/doc 85:** planos de refúgio, rotas, horários, escolta e identidade são campos privados distintos; observação adversária pode descobrir apenas um subconjunto por prova, canal, audiência, tempo e recursos. Rumor não se torna evidência factual nem acesso global ao plano.
- **ACL, identidade e crenças:** DEC-028/057–059/083 exige mínimo acesso por necessidade antes de LLM/LAN/log/cache/RAG; DEC-064/074/076/077 garantem fontes, suspeitas e crenças com proveniência, sem acesso ao ledger privado. Verificações de compromisso internas não concedem conhecimento ao NPC.
- **Proteção continua realista:** exposição gera possibilidade de replanejamento DEC-084, não ataque/teleporte/invisibilidade. Tempo, itinerários, disponibilidade, decisões de PC, riscos MEDIUM/HIGH, host e capabilities validadas são vinculantes. Segredos conhecidos legitimamente não são apagados por revisão.
- **Preservação DEC-060–084:** arquivos canônicos separados fisicamente por ano DR; fontes/curadoria e Knowledge Packs pinados; planos e pistas só em overlays privados da campanha/ramo. Os 79 ADRs anteriores permanecem intactos.
- **Evidência:** 74 testes T085-01..74 candidatos **NÃO EXECUTADOS**; sem integração de espionagem no BG2:EE/EEex/multiplayer.
- **Próxima DEC-086:** operações de engano/iscas; A sem engano deliberado, B LLM livre, C engano contextual versionado, fundamentado e limitado por risco. **Ainda aberta.**

> **Estado corrente v8.1:** 80 ADRs aprovados como arquitetura; DEC-085/C documentada, não implementada; DEC-086 em aberto. Referências anteriores a DEC-085 aberta são histórico.

## DEC-086 — Contraespionagem contextual, iscas e desinformação deliberada (2026-11-07; Discovery v8.2)

- **Opção C aprovada:** ADR-0081/documento 86. `DeceptionOperation` precisa de autoria/autorização, objetivos, limite de terceiros, recursos e fonte de comunicação; narrativa falsa (`PlantedClaim`) permanece distinta da verdade host-confirmed e de provas jurídicas legítimas.
- **Difusão e crenças:** mensageiros, observadores e facções só conhecem claims por canais e tempos verificáveis; podem acreditar, rejeitar ou desmentir, sem descobrir por isso o plano verdadeiro. Sem LLM produzindo evidência falsa como fato ou scripts de motor.
- **Gates:** consentimento/controle delegado DEC-019/041/045/046; riscos e terceiros DEC-027/034/042; POCs por build, ação host/gateway DEC-011/012; duplo envio e UNCERTAIN conservadores.
- **Preservação integral DEC-060–085:** 80 ADRs anteriores idênticos a v8.1, cânone anual fisicamente separado DEC-060, Knowledge Pack pinado DEC-063, claims de isca exclusivamente em overlays privados por campanha/branch.
- **Evidência:** **76 testes T086-01..76 candidatos NÃO EXECUTADOS**. Não há POC de interceptação, disfarce, documento falso ou isca mecânica BG2:EE/EEex/multiplayer.
- **Próxima DEC-087:** agentes duplos, fontes comprometidas e conflitos de lealdade. A proibir, B LLM livre, **C evidência e confiança contextual, autonomia/consentimento de PCs e NPCs, risco e gates**; em aberto.

> **Estado corrente v8.2:** 81 ADRs aprovados somente como arquitetura, DEC-086/C documentada e DEC-087 aberta. Seções anteriores com DEC-086 como futuro são histórico.

## DEC-087 — Lealdades dinâmicas, agentes duplos e conflitos de compromisso (2026-11-07; Discovery v8.3)

- **Opção C aprovada:** ADR-0082/documento 87; NPC pode ter vínculos múltiplos, eventualmente concorrentes, com pessoas, guildas e valores próprios. Avaliação de lealdade contextual por fatos, promessas com fonte, memória, recursos, personalidade e política de autonomia DEC-047/048.
- **Separação epistêmica:** filiação declarada, lealdade privada, rumor, suspeita, compromisso aceito e traição comprovada são diferentes. A LLM não inventa motivações, decisões de PCs nem eventos mecânicos. NPC/facção só descobre vínculos por informação legitimamente adquirida.
- **Gates:** PC agência DEC-019/041/042/045/046, NPC recusa/negociação DEC-047/048, proveniência/ACL DEC-060–065/076/077/083/085, risco DEC-027/034, host/gateway DEC-011/012 e build POC; sem traição obrigatória ou penalidades automáticas.
- **Preservação integral:** DEC-060–086 e ADR-0001..0081 idênticos à v8.2. Cânone físico anual DEC-060 intacto, compromissos e fontes apenas em overlay privado por campanha/ramo.
- **Evidência:** 80 testes T087-01..80 candidatos **NÃO EXECUTADOS**; sem capacidade demonstrada de mudança de facção, manipulação de party ou comportamento de agente duplo BG2:EE/EEex.
- **Próxima DEC-088:** recrutamento de informantes e termos/compensação; A compra instantânea, B LLM livre, **C negociação voluntária com contratos, recursos, confidencialidade e possibilidade real de recusa** — **em aberto**.

> **Estado corrente v8.3:** 82 ADRs aprovados como arquitetura; DEC-087/C documentada e DEC-088 em aberto. Menções anteriores a DEC-087 como futura são históricas.

## DEC-088 — Recrutamento voluntário de informantes e acordos contextuais (2026-11-07; Discovery v8.4)

- **Opção C aprovada:** contato válido e proposta não são contrato; NPC com vontade própria pode recusar, negociar, comprometer-se apenas nos termos validados, suspender ou encerrar. ADR-0083/documento técnico 88.
- **Contratos e recursos:** separar `RecruitmentProposal`, `NegotiationTurn`, `InformantAgreement`, `CommitmentTerm`, `ResourceReservation`, `InformationPromise`, `DeliveryEvidence` e `TerminationEvent`. Saldo/reserva/promessa ≠ pagamento com host receipt; acordos não geram XP nem documentos do nada.
- **Conhecimento, proteção e coop:** informação prometida não foi entregue; informe entregue não é necessariamente verdadeiro. PC/owner e delegado têm consentimento próprio. Segredos DEC-076/083–085 permanecem protegidos e não se tornam onisciência NPC ou LLM.
- **Cânone/cronologia:** DEC-060–087 preservadas, especialmente `knowledge/periods/<ANO>-DR/` físico, proveniência/KPack versionado e overlay de campanha; ledger temporal, checkpoint, branch, retry e idempotência.
- **Evidências:** **82 testes T088-01..82 candidatos NÃO EXECUTADOS**; nenhuma capacidade de recrutamento/pagamento BG2:EE/EEex/multiplayer demonstrada.
- **Próxima DEC-089 aberta:** verificação da credibilidade de informes entregues: A confiar, B LLM arbitrar, **C avaliar proveniência, corroboração, contradições, acesso epistêmico, ACL e risco**.

> **Estado corrente v8.4:** 83 ADRs; DEC-088/C aprovada somente como arquitetura, DEC-089 em aberto. Menções anteriores a DEC-088 como futura são históricas.

## DEC-089 — Verificação de informes e independência de evidências (2026-11-07; Discovery v8.5)

- **Opção C expressamente aprovada:** `DeliveredReport`, `SourceClaim`, `OriginLineage`, `EvidenceFamily`, `ClaimAssessment` e `ObserverBelief` separados; autoria de relato, entrega, credibilidade, verdade factual e conhecimento de NPC não são equivalentes.
- **Dependência das fontes:** múltiplos repasses da mesma origem não contam como provas independentes; pistas contraditórias preservam versões e escopos. Ausência de prova permanece inconclusiva, não falsidade provada.
- **Contexto:** acessar apenas fontes/observações legitimamente possíveis no ano DR e branch; perfil de confiabilidade tem histórico por domínio, não certificação universal. A LLM não determina truthfulness nem cria objetos/quest/receipts.
- **Governança:** relatório pode permanecer `UNVERIFIED/INCONCLUSIVE`, ser parcialmente corroborado ou contradito; avaliação por si não divulga segredo, não impõe sanção e não altera a engine. ACL DEC-028/083 e host DEC-011/012 obrigatórios.
- **Preservação de DEC-060–088:** 83 ADRs anteriores (ADR-0001..0083) byte a byte idênticos à versão v8.4. Conhecimento canônico segue diretórios físicos independentes `knowledge/periods/<ANO>-DR/`; informes e perfis no overlay por campanha/branch.
- **Artefatos:** ADR-0084/documento 89; **84 testes T089-01..84 candidatos NÃO EXECUTADOS**, nenhuma POC BG2:EE/EEex/host+2 clientes.
- **Próxima DEC-090 aberta:** publicação de dossiês e relatórios para audiências autorizadas: A bruto automático, B seleção livre da LLM, **C dossiês versionados com provas citadas, incerteza, ACL, redação contextual e difusão causal**.

> **Estado corrente v8.5:** 84 ADRs; DEC-089/C aprovada apenas em arquitetura; DEC-090 aberta. Menções históricas anteriores a DEC-089 como aberta são registros de versões precedentes.

## DEC-090 — Dossiês versionados e compartilhamento seletivo autorizado (2026-11-07; Discovery v8.6)

- **Opção C aprovada:** ADR-0085/documento 90. `Dossier` restrito, `DossierRevision` imutável, `DossierClaim` ligado a evidências DEC-089, `DisclosureView` por destinatário e finalidade, `ShareAuthorization`, `TransmissionEvent` e `RecipientReceipt` são domínios distintos.
- **Verdade versus circulação:** versão privada não implica publicidade. A view preserva incertezas, contradições e proveniência, com ACL por campo e mitigação de metadados reidentificadores. Autorização não implica envio, envio não implica entrega, entrega não implica crença.
- **Privacidade e cooperação:** fontes DEC-083, identidade DEC-076, refúgios DEC-084/085 e acordos DEC-088 protegidos; consentimentos DEC-019/041/045/046. LLM local só recebe payload filtrado e não decide destinatários.
- **Correção causal:** novas evidências criam revisões e avisos a públicos legítimos, sem amnésia de NPC ou retcon de entrega. Nenhum ato de UI/engine sem gateway/host receipt e capabilities validadas.
- **Preservação DEC-060–089:** 84 ADRs prévios idênticos a v8.5, cânone em partições físicas anuais `knowledge/periods/<ANO>-DR/`; dossiês e segredos apenas em overlays privados por campanha/branch.
- **Evidência:** **86 testes T090-01..86 candidatos NÃO EXECUTADOS**, sem POCs BG2:EE/EEex/host+2 clientes.
- **Próxima DEC-091 aberta:** planejar/agir com inteligência de qualidade variável: A ações automáticas, B agência LLM, **C planos fundamentados, risco, recursos, consentimento, temporalidade e gates do host**.

> **Estado corrente v8.6:** 85 ADRs aprovados somente como arquitetura; DEC-090/C documentada, DEC-091 em aberto. Menções anteriores à DEC-090 como futura são registros históricos.

## DEC-091 — Planejamento operacional por evidências, recursos e gates (2026-11-07; Discovery v8.7)

- **Opção C aprovada:** ADR-0086/documento 91. Planejar a partir de dossiês DEC-090 exige preservar veracidade/contradição DEC-089, `DisclosureView` e acl; dossiê ≠ fato, plano ≠ ato.
- **Separação dos estados:** proposta, validação determinística, autorização dos PCs/autoridades, reserva de recursos, despacho pelo Action Gateway, recibo host e consequência narrativa confirmada; transições com idempotência, risco, revisão de plano e checkpoint.
- **Limites:** LLM local propõe alternativas, não obriga jogadores nem executa HIGH, prisão, combate, confisco, quest ou movimentação sem consentimento, capabilities validadas e confirmação host. Incerteza pode recomendar investigação adicional, não fabricar eventos.
- **Coerência:** identidades/presença, itinerários DEC-068–071, recursos de NPC/facção DEC-031/032 e inventário DEC-051; nenhuma instância CRE surge de afirmação textual.
- **Preservação DEC-060–090:** 85 ADRs prévios idênticos à versão v8.6; base canônica em `knowledge/periods/<ANO>-DR/` fisicamente separada, planos/dossiês privados em overlay por campanha/branch.
- **Teste:** 88 casos T091-01..88 **NÃO EXECUTADOS**. Próxima DEC-092 aberta: monitoramento/pause/abort/replanejamento durante operação, A imutável, B LLM livre, **C eventos observáveis e reaprovação controlada**.

> **Estado corrente v8.7:** 86 ADRs aprovados apenas como arquitetura; DEC-091/C documentada; DEC-092 em aberto. Menções históricas a DEC-091 em aberto permanecem como histórico.

## DEC-092 — Monitoramento e replanejamento seguro de operações (2026-11-07; Discovery v8.8)

- **Opção C expressamente aprovada:** ADR-0087/documento técnico 92. Monitorar eventos confirmados e mudanças relevantes do plano; validar diferenças de evidência, objetivo, tempo, risco, recursos, localização, participantes e ACL antes de novos despachos.
- **Pausa não equivale a pausa da engine:** `PAUSE_REQUESTED`/`PAUSED_ORCHESTRATION` suspendem **novos comandos do orquestrador**. Pausa/cancelamento de ações já aceitas no BG2:EE/EEex dependem de capability e testes host+dois clientes; não implementados.
- **Agência e risco:** saída de PC bloqueia atos futuros em seu nome, não apaga fatos ou força decisões de outros PCs. Alteração material cria `plan_revision` nova e requer autorizações/consentimentos renovados DEC-041/045/046, gates DEC-027/034 e host receipt DEC-011/012.
- **Reconciliação:** ações `DISPATCHED`/`UNCERTAIN` não são repetidas nem liberadas como recursos livres sem reconciliação de receipts/checkpoint; abortar não é rollback. Knowledge Pack pinado e ramo da campanha DEC-022/053/063.
- **Preservação DEC-060–091:** ADRs anteriores ADR-0001..0086 imutáveis; corpus canônico em diretórios físicos anuais `knowledge/periods/<ANO>-DR/`, monitoramento e planos somente no overlay privado por campanha/branch.
- **Evidência:** **90 testes candidatos T092-01..90 NÃO EXECUTADOS**, sem POC de pausa nativa, cancelamento, presença mecânica ou multiplayer. **DEC-093 aberta:** coordenação de operações simultâneas; A serial, B LLM livre, **C scheduler determinístico com fairness/risco, fencing, reautorização e receipts**.

> **Estado corrente v8.8:** 87 ADRs aprovados somente como arquitetura; DEC-092/C documentada; DEC-093 em aberto. Referências anteriores a DEC-092 aberta são histórico.

## DEC-093 — Operações concorrentes e arbitragem determinística (2026-11-07; Discovery v8.9)

- **Opção C expressamente aprovada:** várias operações independentes podem avançar em paralelo, com reserva lógica exclusiva/compatível por recurso, janela DR e identidade persistente. CAS/fencing interno, dedup, fairness e critérios auditáveis candidatos; ADR-0088/documento 93.
- **Fronteira com motor:** reserva/lease do middleware **não** prova posse física, gasto de item, movimentação NPC ou pausa BG2:EE. Efeitos somente com gateway/receipt host e build validada; `DISPATCHED/UNCERTAIN` impede liberação/reenvio cego.
- **Agência, ACL e tempo:** ninguém realoca PC ou usa recurso de terceiro sem autorização; filas P0–P4 DEC-056 não concedem prioridades narrativas; segredo, campanha/branch e KPack pinado mantidos.
- **Conflitos:** avaliação contextual de recurso, objetivo e tempo; operações independentes não ficam presas. Impasses detectados, mas política de resolução detalhada adiada para DEC-094.
- **Preservação:** DEC-060–092 e ADR-0001..0087 byte a byte idênticos à v8.8. Cânone continua fisicamente particionado por ano DR em `knowledge/periods/<ANO>-DR/`; scheduling e operações somente em overlay privado.
- **Testes:** **92 T093-01..92 candidatos NÃO EXECUTADOS**. Sem prova de lock atômico real, bridge, consumo, NPC físico ou host+dois clientes.
- **Próxima DEC-094 aberta:** deadlocks, starvation, expiração/abandonos de reservas; A cancelar todos, B LLM arbitrar, **C recuperação determinística, proporcional, com consentimento e reconciliação host**.

> **Estado corrente v8.9:** 88 ADRs aprovados somente em arquitetura; DEC-093/C registrada, DEC-094 em aberto. Menções históricas a DEC-093 em aberto representam versões anteriores.

## DEC-094 — Recuperação segura de impasses e starvation (2026-11-07; Discovery v9.0)

- **Opção C expressamente aprovada:** grafo de espera versionado por recurso/operação/época, classificação de deadlocks confirmados versus suspeitas, detecção de starvation por indicadores transparentes e recuperação determinística proporcional; ADR-0089/documento técnico 94.
- **Reservas:** expirar lease lógico não libera recurso físico; `HELD` não despachado e comprovadamente revogável é candidato a liberação lógica por CAS/fencing com autorizações; `DISPATCH_PENDING` ambíguo, `DISPATCHED`, `UNCERTAIN` e `CONSUMED_VERIFIED` exigem reconciliação/compensação separada e não geram rollback automático.
- **Fairness sem poder:** idade de fila e urgência podem guiar desempate, sem afetar consentimento, propriedade, PC, host ou risco HIGH; dependências independentes seguem progredindo; logs redigidos para segredos.
- **Preservação:** DEC-060–093 e ADR-0001..0088 byte a byte idênticos à v8.9. Cânone fisicamente separado por ano DR em `knowledge/periods/<ANO>-DR/` e dados de operações nos overlays privados.
- **Provas:** 94 testes T094-01..94 propostos, **NÃO EXECUTADOS**; sem POCs de locks/reconciliação/BG2:EE/EEex/multiplayer.
- **Próxima DEC-095:** como compensar efeitos parcialmente confirmados sem rollback global; A reset automático, B LLM livre, **C saga de compensações reversíveis aprovadas e host-confirmadas, preservando efeitos irreversíveis**.

> **Estado corrente v9.0:** 89 ADRs aprovados somente na arquitetura; DEC-094/C documentada; DEC-095 em aberto. Menções anteriores a DEC-094 aberta são históricas.

## DEC-095 — Compensação segura de operações parciais (2026-11-07; Discovery v9.1)

- **Escolha C expressa:** Saga versionada de passos, distinção entre efeitos confirmados/incertos e novos atos compensatórios autorizados; **nenhum rollback global** e nenhuma criação de ouro, NPC, tempo ou recibo por LLM. ADR-0090 + documento técnico 95, com 96 testes **NÃO EXECUTADOS**.
- Preserva integralmente as DEC-060–094 e os 89 ADRs anteriores byte a byte; cânone físico por ano DR e overlay por campanha/ramo isolados. Estado host `UNCERTAIN` exige reconciliação, não retry cego.
- **Sugestão adicional do idealizador:** a matriz de eventos de Forgotten Realms deveria seguir uma estrutura tipo IF/ELSE por cronologia oficial, mês, abrangência, tipos de local e efeitos diretos/indiretos. A proposta foi detalhada no **documento técnico 96**, com regras declarativas, ano/mês DR preciso, proveniência, locais afetáveis e ledger causal; JSON Schema + fixtures sintéticas + testes locais exemplificam o filtro determinístico.
- **Status da ideia:** DEC-096 **EM ABERTO** para validação da arquitetura A/B/C; nenhum evento real de Forgotten Realms foi publicado/ativado, nenhuma implementação com EEex/BG2:EE foi realizada.

> **Estado corrente v9.1:** 90 ADRs aprovados apenas na arquitetura; DEC-095/C registrada; DEC-096 em aberto. Entradas antigas que mencionam DEC-095 em aberto são históricos preservados.

## DEC-096 — Matriz cronológica condicional e regras declarativas (2026-11-07; Discovery v9.2)

- **Opção C expressamente APROVADA:** catálogo histórico de FR por ano DR fisicamente isolado, com proveniência curada DEC-060–063, ruleset de impactos versionado/compilável e motor determinístico que filtra por data precisa, fase, região, locais/tags, branch, pré-condições e dependências. ADR-0091 e documento técnico 96 aprovado; proposta original v9.1 continua anexada como histórico.
- **Camadas distintas:** `CanonEvent` ≠ `ImpactRule` ≠ `ImpactProposal` ≠ `AppliedImpact` ≠ `KnowledgeAcquisition`. Ano histórico sem mês não vira mês presumido; GLOBAL não vira NPC onisciente; LLM não determina verdade, evento nem efeitos mecânicos.
- **Efeito direto e indireto:** só emitir proposta e respeitar capacidades reais; gate e receipt host para mudança mecânica; indireto requer confirmação do pai e janela própria; idempotência/checkpoint/epochs/caps e divergência do ramo preservam a causalidade.
- **Integridade e estado:** DEC-060–095 e ADR-0001..0090 preservados byte a byte. 100 testes candidatos T096-001..100 **NÃO EXECUTADOS**. Código de referência/schemas sintéticos têm apenas validações unitárias; nenhum teste de BG2:EE/EEex/host+2 clientes, cronologia oficial importada ou economia real realizada.
- **Próxima DEC-097 (em aberto):** resolver sobreposições de eventos e efeitos em mesma região/tempo/mercado: A último vence, B LLM livre, **C agregação tipada determinística com prioridades e caps, expiração/decay, revisão e host receipts**.

> **Estado corrente v9.2:** 91 ADRs aprovados somente como arquitetura; DEC-096/C registrada e DEC-097 em aberto. Registros antigos de DEC-096 aberta são históricos preservados.

## DEC-097/C — Composição de efeitos concorrentes (Discovery v9.3)

**APROVADA 2026-11-07, alternativa C.** ADR-0092 e doc 97 consolidam políticas tipadas por métrica/unidade, aritmética de ponto fixo e operações `BASELINE_PLUS_BPS`/`ADD_ABSOLUTE`, caps, duração e fade de tempo do mundo, famílias causais, precedência e empate fail-closed. Ordem da matriz e de chegada de eventos **não altera resultado**. Projeções não são estado mecânico; efeitos confirmados precisam recibo host, gates, idempotência e trilha auditável. As 91 ADRs anteriores continuam **byte a byte idênticas**. T097-001..102 são candidatos **NÃO EXECUTADOS**. DEC-098 aberta para snapshots e materialização incremental na entrada/saída de regiões. Menções históricas a DEC-097 aberta permanecem válidas como histórico anterior, não como estado atual.

## DEC-098/C — Materialização incremental por região (Discovery v9.4)

**APROVADA em 2026-11-07, alternativa C.** ADR-0093 e documento técnico 98 formalizam snapshots somente a partir de recibos host-confirmed, observação por capacidade testada, planejamento de diffs por instância e identidade persistente, ownership de mods/quests/PCs, quotas por área e catch-up limitado segundo DEC-021/022/068. Reentrada e save/load não repetem spawn/efeitos; `DISPATCHED/UNCERTAIN` requer reconciliação, sem retry cego. A DEC-096 determina elegibilidade e a DEC-097 compõe estado alvo; DEC-098 **não transforma projeção em estado de jogo** sem gates, capacidade e receipt. 92 ADRs anteriores preservados byte a byte; DEC-060–097 intactas. **104 testes candidatos T098-* NÃO EXECUTADOS**. Código de referência puramente sintético sem bridge/multiplayer. **DEC-099 EM ABERTO** para política de ownership e prioridade entre overlays, scripts e mods.

> **Estado corrente v9.4:** 93 ADRs aprovados apenas como arquitetura; DEC-098/C registrada; DEC-099 em aberto. Menções anteriores a DEC-098 aberta são históricos de versões anteriores.


## DEC-099 — Registro aprovado (2026-11-07) · Discovery v9.5

**DEC-099/C APROVADA COMO ARQUITETURA.** A origem do template, a custódia da instância, o titular da instância e a autoridade sobre cada campo são conceitos distintos. O `OwnershipRecord` é ancorado em campanha, ramo, persistent ID, geração de engine instance, prova de titularidade, observação, build fingerprint e modpack hash. Instâncias de scripts/quests originais, terceiros, jogadores e ownership desconhecido ficam protegidas, inclusive após unload, save/load, restauração e migração de builds. Precedência apenas em ação/campo/instância e condições tipadas; ambiguidades e campos protegidos bloqueiam, nunca fallback LLM. A DEC-098 produz **propostas**, não ownership nem aplicação. Read-only não implica write.

- **Decisão:** `decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md`.
- **Contrato:** `99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md`.
- **Referências sintéticas:** `examples/chronology/ownership_reference.py`, `ownership_policy_v1.candidate.schema.json`, `ownership_v1.synthetic.json`, `test_ownership_reference.py`.
- **Estado de verificação:** ADRs anteriores preservados byte a byte; T099-001..120 **candidatos NÃO EXECUTADOS**; testes de código apenas sintéticos. Nenhuma integração real BG2:EE/EEex, hook de quests, handshake multiplayer ou build POC verificados.
- **Próxima decisão:** DEC-100 em aberto — contratos de observação read-only por build, allowlist, informação mínima e controle de spoilers para módulos de IA.

> **Estado corrente v9.5:** 94 ADRs arquiteturais; DEC-099/C aprovada; DEC-100 aberta. Registros históricos que dizem DEC-099 aberta refletem o estado anterior de suas versões, não o estado corrente.


## DEC-100 — Observação read-only de quests/scripts (2026-11-07) · Discovery v9.6

**DEC-100/C APROVADA COMO ARQUITETURA.** A leitura de estado técnico deve usar um probe testado e allowlisted na build/modpack/adapter, com finalidade, audiência, sessão/campanha/ramo, host/checkpoint epoch, cobertura e freshness. O gateway de observação devolve ao contexto narrativo **apenas uma projeção semântica mínima autorizada**, sem flags brutos, spoilers, future branches, logs ou scripts. Scans parciais e consultas ausentes não provam negação, e observação não é host receipt nem conhecimento de NPC. Informação protegida e incertezas falham fechadas; ownership de escrita DEC-099 permanece independente.

- **ADR:** `decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md`.
- **Contrato:** `100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md`.
- **Código e exemplos sintéticos:** `examples/chronology/quest_observer_reference.py`, `quest_observation_v1.candidate.schema.json`, `quest_observation_v1.synthetic.json` e `test_quest_observer_reference.py`.
- **Verificação:** 94 ADRs anteriores preservados byte a byte; **124 testes candidatos T100-001..124 NÃO EXECUTADOS**. Testes de Python são exclusivamente sintéticos, sem sondagens BG2:EE/EEex.
- **Em aberto:** DEC-101 — mapeamento semântico versionado e curado de estados de quests por build, incluindo ambiguidades e prova de transição.

> **Estado corrente v9.6:** 95 ADRs arquiteturais, DEC-100/C aprovada, DEC-101 aberta. Passagens anteriores que mencionam DEC-100 como aberta são registros históricos preservados.

## DEC-101/C — Catálogo semântico curado por build (2026-11-07) · Discovery v9.7

**DEC-101/C aprovada como arquitetura:** estados brutos de quests são observados somente via probes allowlisted DEC-100 e interpretados pelo catálogo versionado por build/modpack/script/quest, com predicados tipados, estágios exclusivos, transições comprováveis, ambiguidade explícita e nenhum palpite de LLM. A interpretação técnica não é divulgação, recebimento, conhecimento NPC ou recibo mecânico. `UNKNOWN/AMBIGUOUS/BLOCKED` não disparam efeitos. **ADR-0096**, doc. 101, **128 testes candidatos NÃO EXECUTADOS**. DEC-060–100 e ADR-0001..0095 mantidos. **DEC-102 aberta**: reconciliação entre progresso do host e overlay persistente.

> **Estado corrente v9.7:** 96 ADRs arquiteturais, DEC-101/C aprovada, DEC-102 em discussão. Menções históricas à DEC-101 em aberto registram somente o estado de versões anteriores.


## DEC-102/C — Reconciliação semântica sem sobrescrita de quests (2026-11-07) · Discovery v9.8

**DEC-102/C APROVADA COMO ARQUITETURA.** O host/quest original continua soberano para mecânica; o overlay preserva fatos e visões derivadas versionadas. O motor compara somente observações read-only com prova DEC-100, marcos curados DEC-101, checkpoints, epochs, branch lineage e receipts do gateway. `CONSISTENT` não escreve nada; avanço comprovado pode gerar `PROPOSE_DERIVED_VIEW_REBASE` sujeito a CAS/autoridade separada. Restore exige revisão do ramo; observação parcial ou despacho incerto permanecem `UNKNOWN/QUARANTINED`. Sem inferência da LLM, sem overwrite de quest, sem vazamento de spoilers nem conhecimento instantâneo de NPCs. **ADR-0097**, **doc. 102**, **132 testes T102-001..132 candidatos NÃO EXECUTADOS**. ADR-0001..0096 anteriores preservados byte a byte; DEC-060..101 inalteradas.

> **Estado corrente v9.8:** 97 ADRs arquiteturais; DEC-102/C aprovada; **DEC-103 EM ABERTO** para admissão causal de marcos reconciliados em sistemas narrativos. As referências mais antigas a DEC-102 aberta são histórico de suas versões, não o status corrente.


## DEC-103/C — Admissão contextual e difusão causal de milestones (2026-11-07) · Discovery v9.9

**APROVADA como arquitetura, alternativa C**. O gateway de admissão só recebe prova minimizada de marcos reconciliados DEC-100/101/102, não flags brutas. `CONSISTENT` exige prova verificável; `PROPOSE_DERIVED_VIEW_REBASE` pendente **não** entra na fila. Avaliação por regras curadas DEC-096/097 com escopo/tempo/branch, ACL e dedup de ocorrência, outbox CAS/fencing; propostas não equivalem a host receipts ou aquisição de conhecimento NPC. Mensagens só propagam após canal/delivery; cada efeito mecânico exige Action Gateway/host e ownership. **ADR-0098** e doc. 103; 136 testes candidatos **NÃO EXECUTADOS**. 97 ADRs anteriores preservados.

> **Estado corrente v9.9:** 98 ADRs aprovados como arquitetura; DEC-103/C registrada; **DEC-104 EM ABERTO** para retificação de consequências derivadas. Registros históricos da DEC-103 aberta são preservados como histórico.

## DEC-104/C — Retificação causal não destrutiva de repercussões (2026-11-07) · Discovery v10.0

**APROVADA como arquitetura, opção C.** ADR-0099 e doc. 104 registram prova curada e committed, grafo causal versionado, contenção de efeitos pendentes, quarentena de `DISPATCHED/UNCERTAIN`, revisão derivada CAS, Sagas de compensação autorizada DEC-095 e correções informacionais posteriores sem apagamento de conhecimento NPC. Fatos confirmados pelo host e branches anteriores são preservados. **98 ADRs anteriores idênticos byte a byte; DEC-060..103 vinculantes.** **140 testes T104-001..140 candidatos NÃO EXECUTADOS** no jogo. Os exemplos Python/JSON de `examples/chronology/rectification_*` são sintéticos. **DEC-105 EM ABERTO** para propagação seletiva de correções e evolução de crenças.

> **Estado corrente v10.0:** 99 ADRs aprovados apenas como arquitetura; DEC-104/C registrada, DEC-105 em aberto. Estados de decisões abertas em seções históricas descrevem versões anteriores.


## DEC-105/C — Correção informacional causal e crenças falíveis (2026-11-07) · Discovery v10.1

**APROVADA COMO ARQUITETURA, opção C.** ADR-0100 e doc. 105: `CommittedCorrection` de DEC-104 alimenta mensagem filtrada e roteada, mas recepção, percepção e revisão de crença exigem provas próprias. Histórico de rumor original não é apagado; fonte protegida e suas ACL precedem qualquer fan-out. Crenças podem divergir legitimamente; nenhum NPC, PC, host ou facção muda automaticamente por LLM. Multiplos ramos e epochs são isolados e mensagens `UNCERTAIN` não sofrem retry cego. **99 ADRs anteriores idênticos byte a byte; DEC-060..104 vinculantes.** **144 cenários T105-001..144 candidatos NÃO EXECUTADOS no jogo.** Exemplos Python/JSON exclusivamente sintéticos. **DEC-106 EM ABERTO** para reabilitação reputacional proporcional após uma retificação comprovada.

> **Estado corrente v10.1:** 100 ADRs aprovados apenas como arquitetura; DEC-105/C aprovada; DEC-106 em discussão. Seções históricas com DEC-105 aberta representam versões anteriores.

## DEC-106/C — Reabilitação reputacional proporcional (2026-11-07) · Discovery v10.2

**APROVADA COMO ARQUITETURA, opção C.** ADR-0101 / doc. 106 formalizam `CorrectionProof` committed independente, público da acusação distinto do alcance da correção, reputação por contexto e relações, classificação de danos alegados/contestados/comprovados, propostas de retratação, diálogo voluntário e reparação como novo procedimento, sem restauração global, coerção de NPC/PC ou alteração automática de mecânicas. **100 ADRs anteriores preservados byte a byte; DEC-060..105 vinculantes.** **148 testes T106-001..148 candidatos de integração NÃO EXECUTADOS em BG2:EE/EEex.** Exemplo Python/JSON apenas sintético. **DEC-107 EM ABERTO** para mediação e direito de resposta.

> **Estado corrente v10.2:** 101 ADRs aprovados como arquitetura; DEC-106/C registrada; DEC-107 em discussão. Menções históricas a DEC-106 aberta representam versões anteriores.

## DEC-107/C — Registro formal (Discovery v10.3; 2026-11-07)

**APROVADA COMO ARQUITETURA, opção C.** ADR-0102 e doc.107. Fases independentes: notificação, entrega, percepção, réplica, convite de mediação, aceites voluntários, sessão, minuta, aceite por termo e commit autenticado. Alegação, prova e parecer não são fatos automáticos; silêncio não é culpa; facilitador deve ser independente; PC/representante precisa ter mandato e consentimento específico. Sem confissão, retratação, perdão ou efeitos de host compulsórios. **101 ADRs anteriores e DEC-060..106 preservados. T107-001..152 candidatos NÃO EXECUTADOS no jogo.** Código/JSON apenas sintéticos. **DEC-108 EM ABERTO:** cumprimento e contestação de obrigações pactuadas.

> **Estado corrente v10.3:** 102 ADRs de arquitetura; DEC-107 aprovada, DEC-108 em aberto. Referências históricas a DEC-107 aberta descrevem versões anteriores.

## DEC-108/C — Registro formal (Discovery v10.4; 2026-11-07)

**APROVADA COMO ARQUITETURA, opção C.** ADR-0103 / doc.108. O monitoramento distingue acordo committed, obrigação versionada, claim, recibo do host, quantidades comprovadas, saldo sem prova, disputa e aditamento; vencimento DR não presume culpa. Recibos `DISPATCHED/UNCERTAIN` exigem reconciliação; nenhum ouro, item, reputação, sanção ou ato de PC é executado automaticamente. **102 ADRs anteriores e DEC-060..107 preservados. T108-001..160 candidatos NÃO EXECUTADOS no jogo.** Código/schema/testes de laboratório sintéticos. **DEC-109 EM ABERTO:** obrigações condicionais e dependências em acordos multipartes.

> **Estado corrente v10.4:** 103 ADRs aprovados como arquitetura; DEC-108/C registrada e DEC-109 em discussão. Entradas históricas sobre DEC-108 aberta descrevem versões anteriores.

## DEC-109/C — Registro formal (Discovery v10.5; 2026-11-07)

**APROVADA COMO ARQUITETURA, opção C.** ADR-0104 e doc.109. Acordos multipartes committed têm DAG por obrigação e revisão, dependências com condições tipadas, grupos combinadores explícitos, escopo DR/branch/host epochs e provas de cumprimento vinculadas a receipts da DEC-108. A entrega de seis de dez caixas não habilita uma dependência de entrega integral. A satisfação de condição permite apenas `READY_FOR_AUTHORIZED_PLANNING`, nunca execução ou dispensa unilateral. Ciclos, referências inválidas, recursos conflitantes, autorizações inexistentes e comandos `UNCERTAIN` bloqueiam a transição. **103 ADRs anteriores e DEC-060..108 preservados. T109-001..168 candidatos NÃO EXECUTADOS em BG2:EE/EEex.** Código/JSON apenas sintéticos. **DEC-110 EM ABERTO:** escrow/garantias condicionais entre as partes.

> **Estado corrente v10.5:** 104 ADRs aprovados apenas como arquitetura; DEC-109/C registrada; DEC-110 em discussão. Entradas históricas sobre DEC-109 aberta retratam versões anteriores.


## Integração DEC-110/C e transição SDD — Discovery v10.6

DEC-110/C aprovada no **ADR-0105** e contrato docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md. Custódia real requer recibo host-confirmed, ownership específico, consentimento, escrow balance, gates por build e reconciliação; nenhuma liberação automática. 176 cenários T110 candidatos não executados. Questionário único docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md (28 respostas) e plano docs/112-plano-de-transicao-discovery-specs-e-primeiro-ciclo-executavel.md são **propostas de coleta e priorização**, não decisões aprovadas por antecipação. DEC-111 permanece em aberto. DEC-060–109 imutáveis e 104 ADRs antigos preservados byte a byte.
