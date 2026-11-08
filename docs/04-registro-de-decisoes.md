# Registro de decisões — Infinity AI

**Versão:** 6.4  
**Data:** 2026-11-06  
**Regra:** usar IDs `DEC-NNN` para perguntas de descoberta; `ADR-NNNN` para decisões técnicas aprovadas. Não renumerar IDs existentes apenas para seguir ordem de discussão.

| ID | Tema | Resultado | Estado | Evidência |
|---|---|---|---|---|
| DEC-001 | Modelo inicial/futuro de multiplayer | **Opção C:** cooperativo privado primeiro, preparar arquitetura para futuro mundo persistente compartilhado | **Aprovada** | Escolha expressa pelo idealizador nesta conversa, 2026-11-05 |
| DEC-002 | Plataforma de execução e testes iniciais | **Opção A:** Windows nativo; IA e serviços desacoplados; validação de versões ainda pendente | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-003 | Sequência da integração de jogos/mods | **Opção A:** BG2:EE mínimo → EEex/bridge → validação multiplayer → EET → IWD/NWN em builds progressivas e reprodutíveis | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-004 | Relação entre campanhas clássicas, Living World e origem dos personagens | **Opção C:** modos separados; cada jogador cria um histórico persistente que orienta os eventos da IA para o grupo | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-05 |
| DEC-008 | Persistência e cronologia de Forgotten Realms | **Opção C + adendo:** estados/snapshots + eventos; lore cronológico com proveniência e impactos no mundo, sem presumir resultado mecânico | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-011 | Autoridade sobre estado mecânico/narrativo | **Opção A:** host confirma efeitos do jogo, Infinity AI mantém narrativa persistente; IA propõe, bridge valida e reconcilia ações incertas | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-014 | Organização de IA e regras | **Opção C com adendos:** diretor central + especialistas sob demanda; executar por código sempre que suficiente; LLM local preferencial, remoto condicionado à futura DEC-006 | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-019 | Política de visibilidade do histórico e segredos | **Opção C:** visibilidade híbrida sob escolha do autor; conhecimento de NPC depende de evidência narrativa | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-05 |
| DEC-020 | Revisões de passado e ganchos | **Opção C:** histórico editável/versionado; IA identifica conflitos e sugere conciliação; mundo confirmado preservado até retcon explicitamente aprovado | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-021 | Autonomia temporal de NPCs e regiões | **Opção C:** simulação por níveis ACTIVE/NEAR/DISTANT/DORMANT, com lotes limitados e regras primeiro | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-022 | Política do relógio do Living World | **Opção C:** tempo híbrido configurável, sem servidor contínuo obrigatório; catch-up limitado e proteção contra eventos irreversíveis na ausência | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-023 | Escolha de época padrão e configurable | **Opção C:** anos por campanha; 1369 DR default para testes com foco em minimizar adaptação do BG2:EE/EET, hipótese sujeita a inventário | **Aprovada** | Solicitação expressa do idealizador em 2026-11-06 e matriz comparativa |
| DEC-024 | Arcos originais no Living World | **Opção C com adendo:** legado histórico para conteúdos passados; arcos contemporâneos paralelos com PCs próprios podendo encontrar e ajudar personagens clássicos, sem scripts de campanha executados indiscriminadamente | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-025 | Progressão dos arcos paralelos | **Opção C:** calendário/condições e janelas opcionais; avanço mesmo sem o grupo; marcos críticos protegidos e divergências após confirmação | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-026 | Intervenção nos arcos clássicos | **Opção C:** N1 diálogo; N2 apoio; N3 mudanças causais com persistência e aprovação de marcos críticos | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |
| DEC-030 | Reputação multidimensional e contextual | **Opção B:** observadores NPC/facção/região, alvos individuais/coletivos, conhecimento legitimado; reputação BG2:EE preservada | **Aprovada** | Escolha expressa pelo idealizador, 2026-11-06 |

## Rastreabilidade

- `DEC-011` → [`ADR-0007-autoridade-dividida-e-consistencia-do-estado.md`](decisions/ADR-0007-autoridade-dividida-e-consistencia-do-estado.md) → [`08-modelo-de-autoridade-e-consistencia.md`](08-modelo-de-autoridade-e-consistencia.md) → futuras SPECS de autorização, observação, reconciliação, consistência multiplayer e persistência.

- `DEC-002` → [`ADR-0005-ambiente-windows-nativo.md`](decisions/ADR-0005-ambiente-windows-nativo.md) → [`06-ambiente-e-matriz-de-compatibilidade-proposta.md`](06-ambiente-e-matriz-de-compatibilidade-proposta.md) → futuras SPECS de ambiente, instalação e gates de compatibilidade.
- `DEC-003` → [`ADR-0006-integracao-progressiva-de-conteudos.md`](decisions/ADR-0006-integracao-progressiva-de-conteudos.md) → [`07-plano-de-integracao-progressiva.md`](07-plano-de-integracao-progressiva.md) → futuras SPECS de baseline, bridge, multiplayer e build de mods.
- `DEC-001` → [`ADR-0001-modelo-de-multiplayer.md`](decisions/ADR-0001-modelo-de-multiplayer.md) → SPECS de sessão, estado do mundo, isolamento, sincronização e persistência (**ainda não redigidas**).
- `DEC-004` → [`ADR-0002-modos-de-jogo-e-historicos-de-personagem.md`](decisions/ADR-0002-modos-de-jogo-e-historicos-de-personagem.md) → [`05-requisitos-narrativos-provisorios.md`](05-requisitos-narrativos-provisorios.md) → futuras SPECS de modos, perfis, ganchos e diretor narrativo.
- `DEC-019` → [`ADR-0003-visibilidade-historicos-e-segredos.md`](decisions/ADR-0003-visibilidade-historicos-e-segredos.md) → futuras SPECS de ACL, informações por destinatário, conhecimento, revelações e auditoria.
- Nenhuma arquitetura de servidor compartilhado foi aprovada ou tecnicamente validada por esta decisão.
- O projeto permanece na fase de **Discovery**; nenhum código ou teste de motor foi executado nesta atualização.

- `DEC-020` → [`ADR-0004-versionamento-e-revisao-de-historicos.md`](decisions/ADR-0004-versionamento-e-revisao-de-historicos.md) → [`05-requisitos-narrativos-provisorios.md`](05-requisitos-narrativos-provisorios.md) → futuras SPECS de revisões, reconciliação, migração de ganchos, autoridade de eventos e auditoria.

**Próxima decisão da fase de discovery:** DEC-009 — política de canon, eventos históricos obrigatórios e desvios da campanha.

- `DEC-014` → [`ADR-0008-orquestracao-hibrida-regras-primeiro-e-llm-local.md`](decisions/ADR-0008-orquestracao-hibrida-regras-primeiro-e-llm-local.md) → [`09-arquitetura-hibrida-regras-e-ia.md`](09-arquitetura-hibrida-regras-e-ia.md) → futuras SPECS de roteamento determinístico, inferência local, validação e fallback.

- `DEC-021` → [`ADR-0009-simulacao-do-mundo-por-niveis-de-atividade.md`](decisions/ADR-0009-simulacao-do-mundo-por-niveis-de-atividade.md) → [`10-simulacao-por-niveis-de-atividade.md`](10-simulacao-por-niveis-de-atividade.md) → SPECS futuras de classificação de regiões, simulação por lotes, reidratação e orçamento de simulação.

- `DEC-022` → [`ADR-0010-tempo-hibrido-e-configuravel.md`](decisions/ADR-0010-tempo-hibrido-e-configuravel.md) → [`11-relogio-hibrido-e-catchup.md`](11-relogio-hibrido-e-catchup.md) → futuras SPECS do relógio, conversão de tempo, checkpoints, catch-up e recuperação.

- `DEC-008` → [`ADR-0011-persistencia-hibrida-e-cronologia-forgotten-realms.md`](decisions/ADR-0011-persistencia-hibrida-e-cronologia-forgotten-realms.md) → [`12-persistencia-hibrida-e-cronologia-forgotten-realms.md`](12-persistencia-hibrida-e-cronologia-forgotten-realms.md) → futuras SPECS de catálogo, tempo DR, regras de ativação, propagação de conhecimento, evento persistente e reconciliação de estados.

- `DEC-009` → [`ADR-0012-politica-de-canon-e-matriz-cronologica.md`](decisions/ADR-0012-politica-de-canon-e-matriz-cronologica.md) → [`13-matriz-cronologica-jogos-expansoes.md`](13-matriz-cronologica-jogos-expansoes.md), [`14-matriz-eventos-excecoes-repercussoes.md`](14-matriz-eventos-excecoes-repercussoes.md), [`15-politica-fontes-canon-curadoria.md`](15-politica-fontes-canon-curadoria.md). Opção C aprovada com adendo de cruzamento histórico. **DEC-023 permanece em aberto.**


- `DEC-023` → [`ADR-0013-epoca-padrao-minimo-impacto.md`](decisions/ADR-0013-epoca-padrao-minimo-impacto.md) → [`16-avaliacao-do-ano-base-por-minimo-impacto.md`](16-avaliacao-do-ano-base-por-minimo-impacto.md); atualiza a matriz 13. **Próxima DEC-024 ainda não aprovada.**

- `DEC-024` → [`ADR-0014-campanhas-paralelas-e-legado-historico.md`](decisions/ADR-0014-campanhas-paralelas-e-legado-historico.md) → [`17-legado-historico-e-campanhas-paralelas.md`](17-legado-historico-e-campanhas-paralelas.md) → futuras SPECS de arcos, encontros opcionais, legado e adaptação de scripts.
- `DEC-025` → [`ADR-0015-progressao-hibrida-arcos-paralelos.md`](decisions/ADR-0015-progressao-hibrida-arcos-paralelos.md) → [`18-progressao-hibrida-arcos-paralelos.md`](18-progressao-hibrida-arcos-paralelos.md) → SPECS de agenda determinística, janelas opcionais, eventos críticos, reconciliação e idempotência.
- `DEC-026` → [`ADR-0016-niveis-de-intervencao-em-arcos-classicos.md`](decisions/ADR-0016-niveis-de-intervencao-em-arcos-classicos.md) → [`19-intervencoes-causais-em-arcos-classicos.md`](19-intervencoes-causais-em-arcos-classicos.md).
- **Próxima decisão pendente: DEC-005** — regras de combate e balanceamento de encontros.


## Pesquisa em andamento — DEC-005 (2026-11-06)

Não é uma ADR aprovada. Avaliação preliminar de AD&D 2e, D&D 3e/5e e combate por turnos; GemRB-TBC como referência experimental, com ressalvas sobre ausência de multiplayer. Consultar `20-estudo-de-viabilidade-regras-e-combate-por-turnos.md`.

## DEC-005-T — Preferência B aprovada (2026-11-06)

- **ADR:** [`ADR-0017-combate-opcional-turnos-com-gate-tecnico.md`](decisions/ADR-0017-combate-opcional-turnos-com-gate-tecnico.md).
- **Decisão:** manter combate clássico RTwP; oferecer turnos individuais opcionais se viáveis.
- **Auditoria:** [`21-auditoria-tecnica-gemrb-tbc-e-gates.md`](21-auditoria-tecnica-gemrb-tbc-e-gates.md) — GemRB-TBC demonstra implementação em motor próprio, mas não possui multiplayer upstream nem suporte direto a EEex/EET.
- **Status:** preferência de design aprovada; implementação condicionada a POCs; DEC-005-R/E abertas.


## DEC-005-R — Escolha B aprovada em 2026-11-06

- **Decisão:** AD&D 2e como núcleo mecânico da implementação BG2:EE; modernizações modulares, opt-in, versionadas e reversíveis apenas quando os testes comprovarem.
- **Status:** aprovada como arquitetura, não como instalação de módulos já concluída.
- **Limites:** sem conversão total para 3e/5e; DEC-005-T mantém gate técnico para turnos; DEC-005-E aberta sobre balanceamento e encontros.
- **Evidência de decisão:** escolha expressa pelo idealizador nesta conversa.
- **Arquivos:** `decisions/ADR-0018-nucleo-adnd-2e-com-modernizacoes-modulares.md` e `22-politica-de-regras-modulares-e-gates.md`.
- **Próxima decisão:** DEC-005-E.

## DEC-005-E — Opção B aprovada em 2026-11-06

- **Decisão:** diretor determinístico de encontros com limites de dificuldade e identidade por região, adaptação contextual ao grupo e preservação de ameaças reais.
- **Sem promessa de vitória:** negociação, fuga, reconhecimento de perigo e preparação são possibilidades quando plausíveis.
- **Regras:** AD&D 2e do BG2:EE (DEC-005-R), sem converter automaticamente CR de outras edições.
- **Governança:** contexto histórico e facções, propostas de spawn/loot, host confirma efeitos; idempotência e gates multiplayer.
- **Status:** arquitetura aprovada, ainda sem SPEC, parâmetros numéricos ou prova técnica de integração.
- **Arquivos:** `decisions/ADR-0019-diretor-adaptativo-encontros-com-limites-regionais.md` e `23-diretor-adaptativo-de-encontros-regionais.md`.
- **Próxima:** DEC-010 — criação/curadoria de conteúdo.


## DEC-010 — Registro de decisão (2026-11-06)

- **Escolha aprovada:** C, arquitetura híbrida: preservar mundo curado e expandir com geração procedural validada.
- **Graduação técnica:** conteúdo estruturado sobre mapas existentes primeiro; áreas/masmorras novas preferencialmente pré-geradas e validadas em ambiente isolado. Geração de mapas durante sessão ativa condicionada a POCs de compatibilidade e multiplayer.
- **Autoridade:** IA gera apenas propostas, com regras/validações de lore, período, conhecimento, mecânicas, recursos disponíveis e segurança; alteração mecânica precisa de confirmação do host.
- **Restrições:** modo Original separado, assets e mods sujeitos a licenças, respeitar progressão canônica e eventos persistidos.
- **Pendência:** a política de aprovação/publicação de conteúdo gerado será decidida na DEC-027, sem automatizar intervenções arriscadas neste momento.
- **Artefatos:** `decisions/ADR-0020-mundo-curado-e-geracao-procedural-validada.md` e `24-pipeline-de-geracao-procedural-validada.md`.


## DEC-027 — Publicação por nível de risco (2026-11-06)

- **Escolha:** opção C, expressa pelo idealizador do Infinity AI.
- **Publicação:** LOW automático somente após validação; MEDIUM sob gates de regras e confirmação do host para efeitos; HIGH com autorização especial e bloqueio padrão na ausência de política explícita.
- **Proteções:** classificação por impacto acumulado; sem Lua livre/execução de texto bruto do LLM; segredos protegidos, canon por campanha, auditoria e reconciliação de ações incertas.
- **Pendência:** autoridade/fluxo de consentimento para eventos críticos, autorização de comandos, allowlist de Lua, isolamentos e backups ainda não especificados.
- **Artefatos:** `decisions/ADR-0021-autonomia-de-publicacao-por-niveis-de-risco.md`; `25-politica-de-publicacao-e-autorizacao-por-risco.md`.
- **Próxima:** DEC-012 (segurança da bridge e permissões de execução).

> **Estado corrente v2.3 (histórico):** DEC-012 era a discussão seguinte; foi aprovada posteriormente na v2.4. Referências antigas a próximas decisões integram o histórico de descoberta.


## DEC-012 — Opção B aprovada em 2026-11-06 (Discovery v2.4)

- **Escolha:** gateway seguro com allowlist de ações tipadas e autorização determinística, sem Lua/shell arbitrário do LLM.
- **Impacto:** autorização de proposta separada de confirmação mecânica do host; isolamentos por campanha/sessão/modo; validação de riscos DEC-027; idempotência e conciliação de resultados incertos.
- **Limites:** política de HIGH ainda não define papéis/consentimento, capacidades reais não testadas, nem canal/versões da bridge definidos.
- **Documentação:** `decisions/ADR-0022-gateway-seguro-de-acoes-autorizadas.md`, `26-gateway-de-acoes-seguras-e-contratos.md`.
- **Próxima decisão:** DEC-028 — política de recuperação/contexto e autorização de leitura antes do LLM.

## DEC-028 — Opção B aprovada em 2026-11-06 (Discovery v2.5)

- **Decisão:** memória compartilhada com acesso seletivo e controlado **antes do LLM**, com proveniência, escopo por campanha, tempo e destinatário; conhecimento de NPCs baseado em fontes legitimadas, rumores distintos de fatos.
- **Dependências:** DEC-019 (segredos definidos pelo jogador), DEC-020 (retcons), DEC-008 (eventos + snapshots), DEC-012 (gateway de mutações), DEC-014 (regras primeiro), DEC-027 (risco de publicação).
- **Aprovado:** arquitetura e princípios de segurança, **não** schemas, banco, ACL implementada, interface no BG2:EE ou compatibilidade multiplayer.
- **Artefatos:** `decisions/ADR-0023-acesso-seletivo-a-memoria-e-conhecimento-por-agente.md` e `27-politica-de-conhecimento-e-recuperacao-seletiva.md`.
- **Próxima:** DEC-029 — política de propagação social de notícias e rumores, com temporalidade e confiabilidade.


## DEC-029 — Propagação de notícias, rumores e segredos (2026-11-06)

- **Status:** **aprovada — opção B** (redes sociais/geográficas e regras determinísticas).
- **Fundamento:** relações entre NPCs/facções, contatos, deslocamentos, tempo autorizado, confiança, intenção e canais de comunicação; sem difusão universal de fatos privados ou dependência de LLM contínuo.
- **Controle:** aquisição de crenças requer proveniência/canal elegível e políticas DEC-019/028; rumores falsos não reescrevem canon; evento mecânico exige confirmação do host; consequências de alto risco preservam bloqueio DEC-027.
- **Integração:** persistência e recuperação em lotes idempotentes alinhados a DEC-008/021/022; testes BG2:EE/EEex e sincronização multiplayer pendentes.
- **Artefatos:** `decisions/ADR-0024-propagacao-deterministica-de-noticias-e-rumores.md` e `28-propagacao-de-noticias-rumores-e-grafo-social.md`.
- **Próxima:** DEC-030 — reputação e percepção conforme conhecimento individual, social e regional.


## DEC-030 — Reputação contextual (2026-11-06)

- **Aprovação:** opção B. Visões diferentes de indivíduos, grupos, facções e regiões; dimensões de fama, confiança, temor, hostilidade e respeito ainda sem escala/fórmula.
- **Causa e conhecimento:** percepção não é estado canônico; eventos testemunhados e relatos/boatos legitimamente recebidos podem alterá-la, com proveniência e diferenças por observador.
- **Compatibilidade:** preservar reputação mecânica do BG2:EE; camada narrativa separada, sem efeitos no jogo sem SPEC, gateway e confirmação do host.
- **Proteções:** dados secretos, personas e limites de atribuição; idempotência, isolamento de campanhas e distinção de opinião individual vs facção.
- **Artefatos:** `decisions/ADR-0025-reputacao-contextual-multidimensional.md` e `29-reputacao-contextual-percepcoes-e-faccoes.md`.
- **Próxima:** DEC-031 — facções, objetivos, alianças e autonomia por regras.


## DEC-031 — Facções autônomas e cânone expandido (2026-11-06)

- **Decisão:** opção B com adendo — facções/governos/guildas/organizações evoluem por regras, objetivos e recursos, sem agente LLM permanente. Preservar organizações dos jogos clássicos e ampliar a base de conhecimento a **todas as organizações existentes no cânone FR**, mediante curadoria progressiva de fontes, épocas e geografia.
- **Separação:** catalogação não é ativação física no motor; facções não presentes nos jogos podem ter relevância narrativa/histórica sem área ou NPC instalado. Não prometer catálogo completo já existente.
- **Gates:** cânone e divergências por campanha, desconhecidos temporais explícitos, risco HIGH default-deny, segredo/rumor/reputação por observador e host para efeitos mecânicos.
- **Documentos:** ADR-0026 e modelo técnico 30.
- **Próxima decisão:** DEC-032 — nível de detalhe de recursos, diplomacia, territórios e conflitos.


## DEC-032 — Simulação estratégica hierárquica (2026-11-06)

- **Status:** aprovada, **opção B** — modelar economia, política, logística, diplomacia e poder militar segundo relevância e níveis de atividade; usar cálculo agregado para regiões distantes.
- **Adendo de pesquisa:** benchmarking técnico de Rome/Total War, Bannerlord, Crusader Kings III, X4 e Stellaris, priorizando documentação oficial; jogos são **referências de design**, não motores integrados/licenciados automaticamente.
- **Compromissos:** código/regras primeiro, LLM apenas sob demanda; cronologia FR e divergências controladas; eventos HIGH exigem política especial; efeitos mecânicos requerem Action Gateway/host; processamento em lotes idempotentes.
- **Limite:** modelos numéricos, calendários estratégicos, resolução de guerras, impacto em lojas/áreas do BG2:EE e multiplayer seguem hipóteses até SPECS/POCs.
- **Artefatos:** ADR-0027, estudo comparativo 31, desenho 32.
- **Próxima:** DEC-033 — escopo de conflitos militares e resolução macro/tática.


## DEC-033 — Conflitos estratégicos e encontros locais (2026-11-06)

- **Aprovada opção B:** cálculo militar agregado distante; atividades locais opcionais quando jogadores estão próximos, condicionadas a recursos reais e integração segura.
- **Proteções:** efeitos mecânicos no BG2:EE apenas após confirmação do host; acontecimentos `HIGH` bloqueados; impacto proporcional, isolamento da resolução estratégica versus encontro ativo, checkpoint e idempotência.
- **Arquivos:** `decisions/ADR-0028-resolucao-hibrida-de-conflitos-e-intervencoes-locais.md`; `33-ponte-entre-conflitos-estrategicos-e-combates-locais.md`.
- **Pendente:** DEC-034 sobre política especial para consequências irreversíveis; execução de POCs com BG2:EE/EEex e multiplayer.


## DEC-034 — Proteção especial do cânone (2026-11-06)

- **Aprovação:** opção C, autonomia controlada com políticas delimitadas para mudanças limitadas e reversíveis, mas bloqueio padrão de acontecimentos históricos centrais/irreversíveis sem consentimento especial explícito.
- **Agência:** jogadores podem tomar rumos diferentes — investigação, defesa ou participação em conspiração — produzindo consequências causais autorizadas.
- **Limites:** preflight e escopo de consentimento pendentes de SPEC; se host já confirmou resultado inesperado, não inventar rollback; conciliar antes de oficializar divergência histórica.
- **Artefatos:** ADR-0029, modelo 34.

## DEC-035 — Alinhamento mutável (2026-11-06)

- **Adendo aprovado e numerado separadamente:** personagens podem mudar alinhamento pela trajetória de escolhas e ações confirmadas, em ambos os eixos ético e moral.
- **Reputação DEC-030 ≠ alinhamento:** crenças/rumores externos não redefinem moral interna; mudanças mecânicas no BG2:EE dependem de validação específica, sobretudo classes/kits.
- **Artefatos:** ADR-0030, modelo 35.
- **Próxima decisão:** DEC-036, método de avaliação contextual de ações e transições de alinhamento.


## DEC-036 — Avaliação contextual e gradual do alinhamento (2026-11-06)

- **Escolha expressa:** opção B — avaliação híbrida contextual e gradual.
- **Aprovação:** regras testáveis/versionadas são autoridade do julgamento de tendência; LLM local pode propor interpretação de situação ambígua, sem arbitrar sozinho ou executar mudanças mecânicas.
- **Condições:** fatos confirmados, causalidade e autoria individual; o conhecimento do personagem e qualquer coerção comprovada são considerados, sem inferir intenções desconhecidas. Rumores e reputação social não viram alinhamento automaticamente.
- **Segurança:** mudanças graduais, idempotentes, revisáveis, preservando modo Original, saves e segredos. Consequências na classe/kit/itens/magias e atributo BG2:EE **não** foram autorizadas automaticamente.
- **Parâmetros ainda em SPEC:** pesos, limiares, taxas, escalas, taxonomia final, contestação, quando convidar o anfitrião a revisar e efeitos mecânicos.
- **Arquivos:** `decisions/ADR-0031-avaliacao-contextual-hibrida-e-gradual-do-alinhamento.md`, `36-avaliacao-contextual-gradual-e-auditoria-do-alinhamento.md`.
- **Próxima decisão:** DEC-037 — consequências mecânicas, avisos e proteções de mudança de alinhamento.


## DEC-037 — Consequências progressivas e validadas do alinhamento (2026-11-06, v3.3)

- **Aprovação expressa:** opção B. Tendência, transição confirmada e efeito mecânico são fases separadas; perfil/versionamento da campanha vincula as regras de aplicação.
- **Classes, kits, magias e itens:** impacto analisado por regra real e build instalada. Nenhuma alteração de atributo, perda de poderes ou transformação de classe é autorizada antes de SPEC, POC e gateway/host.
- **Direitos e consequências:** avisos proporcionais, sem anulação de consequências deliberadas; redenção e recuperação ficam para DEC-038.
- **Consistência:** Original intocado, responsabilidade individual, eventos confirmados e sem rumor como fato, saves/multiplayer idempotentes, retenção de provas e reconciliação de `UNCERTAIN`.
- **Documentação:** `decisions/ADR-0032-consequencias-progressivas-e-validadas-do-alinhamento.md`; `37-consequencias-mecanicas-progressivas-do-alinhamento.md`.
- **Próxima:** DEC-038 — redenção, juramentos, patronos e caminhos de recuperação.


## DEC-038 — Redenção e transformação narrativa (2026-11-06)

- **Escolha aprovada:** opção B — jornadas individuais e opcionais de redenção, reparação, juramentos, fé, facções e transformação, alimentadas pelo histórico e ações confirmadas.
- **Agência e consequências:** jogador pode rejeitar redenção, e cumprir quest não apaga culpa, danos, alinhamento ou reputação automaticamente; não há perdão universal garantido.
- **Condições mecânicas:** qualquer recuperação de poderes, mudança de classe/kit, patrono com efeito físico ou alteração de atributos exige regras específicas, SPEC, POC BG2:EE/EEex, Action Gateway, receipt do host e persistência idempotente.
- **Cânone/privacidade:** entidades históricas validadas por data/região, não divulgação de segredos sem proveniência e proteção de eventos HIGH.
- **Artefatos:** ADR-0033 e documento técnico 38.
- **Próxima:** DEC-039 — pipeline de geração e marcos de arcos pessoais de personagem.


## DEC-039 — Personal Story Director híbrido (2026-11-06)

- **Aprovação:** opção C — ganchos pessoais derivados de históricos versionados e ações confirmadas, templates validados, IA local sob demanda para variações, marcos e desfechos alternativos com evidências.
- **Agência:** escolha livre de aceitar, recusar, adiar ou alterar rumo; oportunidades individuais não devem monopolizar o multiplayer (detalhes DEC-040).
- **Proteções:** canon/data, segredos filtrados antes do LLM, validação de risco, gateway, autoridade do host para efeitos mecânicos, idempotência e isolamento Original/Living World.
- **Ressalvas:** não foi implementada a geração de quests nem validada a manipulação de recursos no BG2:EE/EEex.
- **Artefatos:** ADR-0034 e documento técnico 39.
- **Próxima decisão:** DEC-040 — equilíbrio e coordenação cooperativa dos arcos pessoais.


## DEC-040 — Diretor cooperativo com equilíbrio dinâmico (2026-11-06)

- **Escolha:** opção B, aprovada pelo idealizador.
- **Âmbito:** distribuição de oportunidades significativas, não por rotação rígida. Considerar relevância, presença, histórico de foco, disponibilidade e participação voluntária de personagens.
- **Agência:** titular decide aceitar/adiar/recusar e quanto revelar; papéis compartilhados opcionais e sem absorver histórias dos outros personagens.
- **Autoridade:** regras e eventos confirmados, filtragem de segredos, gateway/host, relógio, canon e proteção HIGH já aprovados.
- **Limites:** algoritmo quantitativo e suporte multiplayer ainda sujeitos a SPECS/POCs; não implementar teletransporte, separação de grupos ou UI sem validação.
- **Artefatos:** ADR-0035 e `docs/40-diretor-cooperativo-equilibrio-narrativo.md`.
- **Próxima:** DEC-041 — consentimento e autoridade em escolhas com efeitos cruzados ou coletivos.


## DEC-041 — Autoridade distribuída em arcos compartilhados (2026-11-06; Discovery v3.7)

- **Aprovação:** opção C — agência individual dos controladores de PCs; o anfitrião governa políticas globais e não escolhe falas, motivações ou compromissos dos personagens dos outros.
- **Intervenções legítimas:** acontecimentos confirmados de um jogador podem afetar outro, mas não criar fatos secretos, consentimentos ou ações passadas sem evidências.
- **Sigilo:** revelação voluntária cabe ao titular; investigação e descoberta por terceiros podem ocorrer quando houver origem legítima, em concordância com ACL e os limites da campanha. Rumores continuam crenças, não verdades automáticas.
- **Gates:** DEC-011/012/027/034/028; host confirma mecânica, HIGH exige aprovação especial, CSD/PSD não têm autoridade para decidir pelo jogador nem realizar retcons.
- **Fora do escopo:** DEC-042 ainda aberta para PvP, roubo, coerção e dano entre PCs.
- **Documentos:** ADR-0036 e `41-autoridade-distribuida-consentimento-e-eventos-cruzados.md`.


## DEC-042 — PvP configurável, consentimento por categoria (2026-11-06; Discovery v3.8)

- **Aprovação:** opção C, expressamente escolhida pelo idealizador.
- **Política:** campanha configura PvP por categoria (duelos, dano, furto, magia/coerção, prisão, efeitos irreversíveis), com limites e consentimento dos jogadores afetados. O anfitrião não concede autorização em nome de outros.
- **Conservação da agência:** decisões e falas de PCs pertencem a controladores humanos; jogadores desconectados não aceitam hostilidades novas por omissão.
- **Riscos e autoridade:** gateways e regras autorizam propostas; host confirma efeitos; resultados `UNCERTAIN` não são reaplicados sem reconciliação. Efeitos indiretos e *friendly fire* exigem POCs.
- **Limites:** morte permanente não é implicitamente autorizada. Perfis, UI, escopo de autorização e interceptação preventiva no motor ainda dependem de SPECS/POCs.
- **Arquivos:** ADR-0037 e documento técnico 42.
- **Próxima:** DEC-043 — morte e ressurreição dos PCs.

## DEC-043 — Mortalidade configurável, retorno e legado (2026-11-06; Discovery v3.9)

- **Escolha aprovada:** **opção C**, com políticas por campanha para morte, possibilidades de ressurreição, perda definitiva e manutenção de legado de PCs.
- **Sem atalho mecânico:** host BG2:EE confirma morte/retorno e efeitos sobre inventário; Infinity AI registra a consequência narrativa e não implementa regras alternativas por LLM. SPECS/POCs obrigatórias.
- **Persistência:** ações, relações, reputação e marcos confirmados permanecem e podem causar novas histórias; morte não torna públicas informações privadas automaticamente. Retorno não apaga história.
- **PvP:** categorias de DEC-042 são independentes; duelo ou dano consentido não equivalem a permadeath autorizado.
- **Segurança:** jogador ausente não é representado; consequências offscreen não matam PCs sem host; `UNCERTAIN` e save/load exigem conciliação, sem duplicações ou falsos retornos.
- **Limites técnicos:** protagonista, possível game-over, feitiços/recursos, engine/EEex, mods e multiplayer ainda não comprovados. Modo Original preservado.
- **Arquivos:** ADR-0038 e documento técnico 43.
- **Próxima:** DEC-044 — personagens substitutos, continuidade, bens e conhecimento herdados legitimamente.

## DEC-044 — Integração contextual, progressão equilibrada e herança legítima (2026-11-06; Discovery v4.0)

- **Escolha expressa:** **opção C**. Novo PC tem biografia, alinhamento, conhecimento, reputação e escolhas próprios, mesmo sob o mesmo controlador humano.
- **Ingresso contextual:** PSD/CSD propõem encontros coerentes e opcionais no mundo; inclusão física no BG2:EE é pendente de POC e confirmação do host.
- **Equilíbrio:** nível e recursos de entrada são políticas por campanha a especificar, com limites contra criação sucessiva de fichas/itens/XP; sem nível 1 forçado nem cópia de XP como herança.
- **Espólio:** doações, heranças, títulos, itens e obrigações só mudam de titularidade por regras, evidência, consentimento quando exigido e host receipt; reivindicação não cria item.
- **Conhecimento:** segredos e lembranças não migram de PC por identidade de jogador; NPCs podem reconhecer vínculos legítimos sem conhecer toda a vida do personagem anterior.
- **Legado:** fatos históricos confirmados permanecem, arcos pessoais podem originar novos ganchos, sem retcon ou autoria fictícia.
- **Riscos:** multiplayer/slots, protagonista/game-over, ressuscitação tardia, ficha/inventário e saves sem compatibilidade demonstrada; `UNCERTAIN` exige reconciliação.
- **Arquivos:** ADR-0039 e documento técnico 44.
- **Próxima:** DEC-045 — ausências, desconexão e retorno de um jogador/PC.

## DEC-045 — Atribuição temporária de personagens e controle compartilhado (2026-11-06; Discovery v4.1)

- **Aprovação:** proposta expressa do usuário, inspirada no sistema de coop de **BG3**. Jogador presente pode controlar vários PCs; PCs de ausentes são redistribuídos, não removidos ou controlados obrigatoriamente por IA.
- **Evidência:** manual oficial **BG2:EE** confirma *Character Arbitration*, atribuição de slots e controle de múltiplos PCs por participante (pp. 58–63). EEex/automação de reatribuição/midcombat não foram testados.
- **Agência:** titular do histórico e controlador da sessão são papéis distintos. O controlador não ganha automaticamente a autoria de segredos, decisões pessoais ou direitos de propriedade; limites específicos serão DEC-046.
- **Estado autoritativo:** host/Character Arbitration, eventos auditados, reconciliados, versionados, sem dupla posse/controle de slot ou duplicação de fichas. Mecânica não confirma intenção narrativa.
- **Regresso:** ao reconectar, o titular recupera o controle do mesmo PC por atribuição legítima; efeitos confirmados não são revertidos por padrão.
- **Risco:** combate pode ser letal e não existe proteção técnica provada por simples ausência; aplicar DEC-042/043 e regras do motor.
- **Arquivos:** ADR-0040 e documento técnico 45; **próxima:** DEC-046 — limites da delegação.

## DEC-046 — Permissões granulares de controle substituto (2026-11-06; Discovery v4.2)

- **Escolha:** opção **C**. O titular configura antecipadamente **categorias independentes de delegação** do PC para um controlador presente (DEC-045). Atribuição do slot não transfere agência, histórico, segredos ou consentimento ilimitado.
- **Categorias:** movimentação, combate, recursos/itens, diálogos comuns, missões coletivas, compromissos pessoais, juramentos/pactos, sigilo, PvP e fatos HIGH; limites da campanha prevalecem.
- **Autorização:** escopo por PC/controlador/campanha, tempo, política e epoch; revogação e retorno prospectivos, com auditoria e reconciliação.
- **Gates:** a atribuição manual nativa do BG2:EE é documentada; interceptar/impedir **cada tipo** de comando não foi comprovado. Sem veto real, fallback seguro (pausa/não delegação) e transparência.
- **Integrações:** DEC-019/020/027/028/034/041/042/043, Action Gateway e host, sem IA interpretando o ausente.
- **Arquivos:** ADR-0041 e documento 46; **próxima: DEC-047 — autonomia dos companheiros NPC versus controle tático**.


## DEC-047 — Controle tático com autonomia narrativa dos companheiros NPCs (2026-11-06; Discovery v4.3)

- **Escolha aprovada:** **C**. Companheiros NPC recrutáveis são comandáveis taticamente pelos humanos nos limites da engine, porém mantêm vontade narrativa, valores, relações, lembranças e objetivos individuais.
- **Não equiparar NPC a PC:** titularidade/consentimento DEC-041/045/046 protege personagens de jogadores; um NPC conserva identidade própria e não passa a ser "interpretado integralmente" por quem move seu slot.
- **Reações causais:** NPC pode aprovar, protestar, negociar, gerar missões, questionar alinhamento moral, impor limites e considerar saída do grupo, mas consequências físicas só após integração permitida, execução tipada e host receipt.
- **Confidencialidade:** conhecimento legítimo, rumor com proveniência, cronologia e memória seletiva antes da IA; personagens canônicos e scripts originais devem ser auditados.
- **Viabilidade:** bloqueio de ordens, saída e recrutamento programáticos, reações sincronizadas em multiplayer e compatibilidade EEex/EET/IWD/NWNForBG permanecem sem POC; não prometer autonomia mecânica executável.
- **Documentação:** ADR-0042 e documento técnico 47; **próxima DEC-048**, gradação de desaprovação e ruptura dos companheiros.


## DEC-048 — Desacordo contextual, lealdade, negociação e ruptura de NPCs (2026-11-06; Discovery v4.4)

- **Opção aprovada:** **B**. Companheiros NPCs reagem a fatos conhecidos, princípios pessoais, vínculos, gravidade e contexto por regras auditáveis; IA local apenas auxilia na conversa.
- **Escalada adaptativa:** preocupação, advertência, negociação, recusa narrativa e intenção de abandono são possibilidades, não etapas obrigatórias de uma barra única. Atos críticos comprovados podem justificar ruptura imediata, sem dispensar gates técnicos.
- **Agência:** permitir explicação, correção de boato, compromisso e reparação, mas sem forçar perdão ou produzir alterações de relação apenas por discurso. Proteger agência e segredos dos PCs.
- **Mecânica:** saída/recusa física da party não foi comprovada; apenas gateway tipado + recibo do host pode confirmar efeito, inclusive em multiplayer/save/load.
- **Cânone e compatibilidade:** inventariar scripts, diálogos, romances, recrutamentos e condições de despedida originais; preservar Original.
- **Documentos:** ADR-0043 e documento técnico 48. **Próxima:** DEC-049, vida pós-party e reencontro de companheiros NPCs.


## DEC-049 — Vida pós-party dos companions NPCs (2026-11-06)

- **Escolha:** opção B — autonomia persistente com simulação hierárquica, não simulação individual contínua.
- **Escopo:** histórico, vínculos, memória, objetivos, recursos, agendas, possíveis reencontros e re-recrutamento contextual, preservados após saída comprovada pelo host.
- **Fronteiras:** continuidade narrativa fora da party não confirma deslocamento físico no motor; reconciliação de posição, tempo, flags e disponibilidade é obrigatória. Possíveis encontros e retorno dependem de POC e host.
- **Proteções:** dados e segredos filtrados, canon e scripts originais preservados, HIGH default-deny, sem NPC duplicado, replay idempotente, Original isolado.
- **Artefatos:** ADR-0044 e `49-vida-autonoma-reencontros-e-recrutamento-de-companheiros-npc.md`.
- **Próximo debate:** DEC-050 — conciliação de scripts/quests/romances originais com propostas narrativas dinâmicas.

## DEC-050 — Conciliação de scripts originais e eventos dinâmicos (2026-11-06)

- **Escolhida opção C:** proteger roteiros, quests, banters e romances BG2:EE/mods existentes, mas aceitar extensões compatíveis e divergências causais aprovadas e tecnicamente viáveis.
- **Fluxo aprovado:** proposta narrativa identificada → inventário/observação confiável do build → checagem determinística de colisões e políticas → adaptar, adiar, bloquear ou escalar ramificação → gateway/host para qualquer mutação e pós-condição.
- **Princípio de integridade:** desconhecimento de flag não equivale a ausência de dependência; `UNCERTAIN` e alterações de build bloqueiam mutações até reconciliação/novas provas.
- **Escopo:** ADR-0045 e documento técnico 50; arquitetura Discovery, sem implementação e sem promessa de hooks de EEex ou suporte a EET/IWD/NWNForBG.
- **Próximo debate:** DEC-051 — inventário versionado e curadoria dos conteúdos instalados.

## DEC-051 — Inventário híbrido de conteúdo instalado (2026-11-06)

- **Escolha expressa:** C — varredura automatizada somente leitura + catálogo curado e versionado por instalação, edição e componentes/ordem de mods.
- **Governança:** registrar fingerprints, cobertura e origem de cada recurso; separar `OBSERVED` estático de estado runtime validado. Dependências `UNKNOWN`/`CONFLICTED` bloqueiam efeitos mecânicos até evidências suficientes.
- **Compatibilidade:** uma build não autoriza outra; alteração de recursos/mods invalida aprovações e demanda novos gates. BG2:EE limpo primeiro e expansão progressiva.
- **Integração:** DEC-050 reconciliador, DEC-011 host, DEC-012 Action Gateway, DEC-003 builds reproduzíveis e DEC-009 cronologia.
- **Artefatos:** `decisions/ADR-0046-inventario-hibrido-curado-e-versionado-do-conteudo-instalado.md` e `51-inventario-hibrido-de-conteudo-por-build-e-proveniencia.md`.
- **Próximo debate:** DEC-052 — atualizações de instalação/mods versus migração segura de campanha.

## DEC-052 — Builds fixas e migração controlada (2026-11-06)

- **Escolha expressa:** opção **C**, aprovada. A campanha conserva fingerprint de instalação/build e ordem de mods; atualização é candidata isolada, jamais aplicada automaticamente sobre o baseline ou saves ativos.
- **Migração:** inventariar e comparar conteúdo/IDs/flags pertinentes; criar e testar backup coerente, ensaiar em cópias, revalidar quests, romances, personagens, save/load, host e dois clientes.
- **Gate:** bloquear incompatibilidade, cobertura crítica desconhecida, ação incerta não reconciliada ou falha de recuperação. Aprovação do anfitrião só após evidência de testes; após promoção, preservar log auditável e revalidar direitos/permissões de build.
- **Rollback:** restaurar conjunto íntegro previamente preservado da instalação/saves/dados narrativos, não garantir rollback atômico de duas aplicações.
- **Arquivos:** ADR-0047 e documento técnico 52 (20 testes candidatos), Discovery v4.8.
- **Próximo debate:** DEC-053 — coordenar checkpoints/restauração entre estado do host BG2:EE e estado narrativo externo, tema relacionado à DEC-018 ainda aberta.

## DEC-053 — Checkpoints coordenados e recuperação segura (2026-11-06)

- **Escolha expressa:** opção C. Vincular checkpoint verificável do save do host BG2:EE a uma revisão de snapshot e watermark do event log da camada narrativa. Publicar apenas par íntegro e causalmente compatível, por campanha/modo/build/ramo.
- **Falhas:** candidato incompleto não é recuperável; `UNCERTAIN` deve ser reconciliado com recibos/evidência antes de retry. Save anterior com registro narrativo posterior exige separação de ramo e preservação de auditoria, não reescrita automática.
- **Autoridade e segurança:** host confirma mecânica; Infinity AI preserva fatos narrativos com proveniência; ninguém presume commit atômico, save por API ou alterações de flags por LLM. Proteger segredos e isolamento Original/Living World.
- **Gates:** captura, interrupção entre metades, hash/identity, rewind, idempotência, restore em cópias, host e dois clientes.
- **Artefatos:** ADR-0048 e documento técnico 53 (24 testes candidatos), Discovery v4.9.
- **Próxima:** DEC-054 — retenção, backup operacional e recuperação testada, integrada à DEC-018 ainda aberta.


## DEC-054 — Backups versionados e testes de recuperação (2026-11-06)

- **Escolha:** opção C aprovada. Automatizar cópias **somente de pares coordenados publicados pela DEC-053**, mantendo índice, hashes, revisões, cadeias de logs e identidade de build/campanha.
- **Retenção e proteção:** versões rotativas com parâmetros para SPEC; respeitar pins de marcos e pré-migração, dependências incrementais e proibição de excluir a última cópia recuperável.
- **Redundância:** cópia independente opcional por escolha explícita do anfitrião; sem nuvem exigida nem upload não autorizado. Destinos remotos cifrados, chaves sob custódia segura e privilégios mínimos.
- **Ensaios:** testar em cópia isolada, incluindo save/load e progressão real com host + dois clientes nos POCs; checksum não certifica jogabilidade. Falhas devem ser visíveis e a restauração em produção exige autorização.
- **Artefatos:** ADR-0049 e documento técnico 54 (28 casos candidatos), Discovery v5.0.
- **Próxima:** DEC-055 — observabilidade e resposta a incidentes. DEC-018 permanece aberta para operação geral, logs e alertas.

## DEC-055 — World Health Monitor e recuperação por níveis de risco (2026-11-06)

- **Opção C aprovada:** observar componentes e capacidades instrumentáveis sem confundir disponibilidade de processo com integridade de campanha.
- **Fail-closed e degradação:** serviços stateless/read-only podem receber retries limitados previamente autorizados; efeitos mecânicos `UNCERTAIN`, divergências save/log, dados corrompidos ou falhas de ACL suspendem operações afetadas até conciliação e autorização adequada.
- **Conservação de estado:** nenhum restart assume sucesso; gateway requer action_id/receipt e idempotência; checkpoint/backup permanecem nos pares íntegros publicados das DEC-053/054.
- **Privacidade:** observabilidade local por padrão, alertas minimizados por ACL e sem telemetria externa implícita.
- **Artefatos:** ADR-0050 e documento 55 (28 casos candidatos), Discovery v5.1, ainda sem execução de testes no BG2:EE.
- **DEC-018:** ainda aberta para especificações operacionais completas; **DEC-056** será a próxima sobre políticas de desempenho e priorização.

## DEC-056 — Gerenciador adaptativo de desempenho (2026-11-06)

- **Escolha expressa:** opção C, aprovada. Orquestrar apenas o trabalho sob controle do Infinity AI com classes P0–P4, budgets observados, filas de prioridade, controle de admissão, backpressure e fairness delimitada.
- **Proteção:** fluidez do BG2:EE e consistência host/multiplayer primeiro; receipts do gateway, ações `UNCERTAIN`, ACL, salvamento e proteção de risco jamais descartados por sobrecarga. Fallback LLM não inventa fatos; carga distante é adiável, sem avanço temporal arbitrário ou duplicação.
- **Medição:** CPU/RAM/GPU/VRAM/I/O, throughput e latência só quando observáveis; sem prometer prioridades OS, FPS ou timeouts antes de benchmark com host e dois clientes. Sonda não demonstrada=`UNKNOWN`.
- **Artefatos:** ADR-0051 e documento técnico 56 (28 casos candidatos), Infinity AI Discovery v5.2, nenhum teste ou código executado.
- **Próxima decisão:** DEC-057 — topologia de execução (host/sidecar/nó LAN); DEC-006 (modelos/hardware), 015 e 018 seguem abertas.

## DEC-057 — Topologia modular local-first, execução distribuída opcional (2026-11-06; Discovery v5.3)

- **Escolha expressa:** opção **C**. Serviços Infinity AI desacoplados, executáveis no mesmo PC Windows anfitrião ou, por configuração explícita, com inferência/simulação em nós adicionais da LAN.
- **Sem alteração de autoridade:** BG2:EE host continua único responsável pelo efeito mecânico; worker retorna propostas com identidade de campanha/build/ramo/revisão e sem escrita direta no motor. Gateway e receipts não são opcionais.
- **Segurança e dados:** ACL minimizada antes de qualquer envio, escopo por sessão/nó, isolamento Original/Living World; LAN não confere confiança automática. Pareamento/autenticação/transporte são **DEC-058**, próxima.
- **Falhas:** desconexão de worker não dispara replay de mutações `UNCERTAIN`; estados críticos continuam com host + persistência/backup verificados; modo degradado somente se testado.
- **Limites:** nenhum protocolo, infraestrutura, hardware mínimo, desempenho, distribuição de DB ou sincronização de EEex multiplayer validado. DEC-006/013/015/018 continuam abertas.
- **Artefatos:** `decisions/ADR-0052-topologia-modular-local-first-e-execucao-distribuida-opcional.md` e `57-topologia-local-first-servicos-desacoplados-e-nos-lan.md` (24 testes candidatos).

## DEC-058 — Descoberta assistida, pareamento autorizado e canais protegidos (2026-11-06; Discovery v5.4)

- **Escolha expressa:** opção C — o anfitrião confirma cada nó LAN e suas capacidades; descoberta não autoriza conexão nem envio de dados privados.
- **Identidade e proteção:** vínculo criptograficamente verificável, transporte autenticado/confidencial/íntegro e escopos por nó/campanha/serviço; protocolos, bibliotecas e métodos de verificação ficam para SPECS/POCs.
- **Privacidade:** ACL e minimização antes do envio a workers. Logs, prompts, caches e credenciais protegidos; nenhum worker recebe saves ou privilégio de gateway por default.
- **Revogação e falhas:** bloqueio de jobs/resultados após revogação, status e épocas de autorização, antirreplay, fail-closed para spoofing e partição. Não afirmar que segredo previamente entregue tenha sido apagado.
- **Limite de autoridade:** nenhum nó LAN confirma ações BG2:EE ou resolve `UNCERTAIN` automaticamente; gateway/host permanecem autoritativos.
- **Artefatos:** `decisions/ADR-0053-descoberta-assistida-pareamento-autorizado-e-canais-protegidos-lan.md` e `58-descoberta-pareamento-identidade-e-seguranca-lan.md` (26 testes candidatos).
- **Próxima:** DEC-059 sobre roteamento/fallback seguro de inferências e jobs entre nós; DEC-006/013/015/018 abertas. **Nenhuma implementação ou teste concluído.**

## DEC-059 — Roteamento de modelos conforme tarefa, privacidade e recursos

- **Escolha do idealizador em 2026-11-06:** opção **C**; **aprovada** em Discovery, ADR-0054.
- **Decisão:** primeiro caminhos determinísticos; se IA for necessária, classificar tarefa/sensibilidade e aplicar ACL antes do prompt; selecionar apenas worker `ACTIVE` e autorizado, com capacidades aferidas. Recursos e latência só classificam elegíveis.
- **Fallback:** recurso equivalente autorizado, conteúdo aprovado ou pendência. Proibido presumir autorização de IA externa, reenviar segredo a nó não autorizado ou executar comandos de modelo.
- **Autoridade:** `job_id`, ramo/build/revisão/epoch, saída como proposta; host confirma mecânica e não se repete `UNCERTAIN`.
- **Artefatos:** `decisions/ADR-0054-roteamento-de-modelos-por-tarefa-privacidade-recursos-e-fallback.md`; `59-roteador-de-modelos-politicas-de-privacidade-qualidade-e-fallback.md` (24 testes candidatos).
- **Próxima:** DEC-060 — política de qualidade/validação de saídas de modelos. DEC-006/013/015/018 seguem abertas. **Nenhum teste executado.**


## DEC-060 — Validação híbrida de respostas de IA (2026-11-06)

- **Aprovada: C**, ADR-0055, Discovery v5.6. Validação em camadas proporcional ao risco: schema, ACL, conhecimento legítimo, fontes e cronologia de Forgotten Realms, ramo/quest/build e autorização de efeitos.
- Segundo LLM pode auxiliar, mas não é autoridade; sem evidência, não promover alegação a fato. `ACCEPT/REVISE/DEFER/REJECT/ESCALATE`.
- Documento técnico `docs/60-validacao-de-respostas-coerencia-canonica-e-gates-por-risco.md`; DEC-061 próxima. DEC-006/013/015/018 abertas.

## Adendo à DEC-060/C — particionamento físico anual do lore (2026-11-06)

- **Aprovado a pedido do idealizador:** manter o conhecimento canônico em diretórios separados por ano DR, inicialmente com `1369-DR/{chronology,events,organizations,guilds,characters,regions}`. A consulta de NPC começa no diretório do **ano vigente confirmado**; consulta a anos anteriores é excepcional/explicita e temporalmente válida, anos futuros não viram fatos presentes.
- Conhecimento acessível a NPC depende também de ACL, difusão e proveniência; conteúdo próprio da campanha fica em overlay separado por campanha/ramo/ano. Nenhum diretório do cânone se torna memória global/verdade automática do NPC.
- **Registro:** emenda à ADR-0055 e documento 60, complemento técnico 60a e árvore inicial `knowledge/` (sem lore preenchido). Nenhuma DEC/ADR nova; **DEC-061 permanece aberta** para conflitos editoriais e fontes divergentes dentro do período.

## DEC-061 — Fontes concorrentes e curadoria contextual (2026-11-06)

- **Escolha expressa:** opção **C**, aprovada como arquitetura no **ADR-0056**; não implementar hierarquia editorial global nem publicar consenso produzido automaticamente por LLM.
- **Regra:** fatos de lore ainda são alegações com referência. Registrar obras/edições/versões, época DR, precisão, região e perspectiva; distinguir evolução histórica, rumor e retcon de contradição real. Versões conflitantes não são apagadas.
- **Curadoria:** resolução de alto impacto exige responsável, evidência, escopo e revisão. Conteúdo `UNRESOLVED` não vira fato assertivo; a validação de saída DEC-060/C e ACL DEC-028/029 permanecem.
- **Adendo DEC-060 mantido:** partições **fisicamente separadas por ano DR** e overlays por campanha/ramo; nenhuma consulta sem isolamento temporal ou troca da árvore anual por um corpus único.
- **Artefatos:** `decisions/ADR-0056-proveniencia-e-resolucao-contextual-de-conflitos-canonicos.md` e `61-governanca-de-fontes-conflitos-e-curadoria-por-periodo.md`. **DEC-062 próxima** (ingestão e revisão de fontes); DEC-006/013/015/018 abertas. Sem dados de lore importados nem implementação.

## DEC-062 — Pipeline híbrido de ingestão e publicação curada (2026-11-06)

- **Escolha aprovada:** opção **C**; ADR-0057 e doc. 62. IA assiste na extração, identificação de entidades, datas e conflitos; fontes candidatas ficam em staging privado e são verificadas por regras independentes antes de qualquer publicação.
- **Gates:** direitos de uso, arquivo de origem, checksum, escopo de licença, proveniência DEC-061, ano/validade DEC-060, ACL, duplicatas, contradicões e risco; novos fatos canônicos exigem inicialmente revisão humana. Possível automatização LOW só com allowlist expressa/versionada, testes e audit.
- **Invariantes:** cada publicação ocorre em diretório físico anual `knowledge/periods/<ano>-DR/...`; nenhuma base global substitui as partições; anos futuros, afirmações `UNKNOWN` ou conflitos não resolvidos não são convertidos em fatos por LLM.
- **Campanha:** importações não modificam overlays, saves ou fatos confirmados; pinning/migração de revisions fica para DEC-063.
- **Licença e estágio:** nenhuma obra/lore foi importada, direitos de obras não foram individualmente verificados, nenhuma POC executada. Material integral restrito não entra no ZIP.
- **Próxima:** DEC-063 (versões do knowledge pack por campanha). DEC-006/013/015/017/018 ainda abertas.

## DEC-063 — Vinculação versionada e atualização seletiva de Knowledge Packs (2026-11-06)

- **Escolha:** opção **C** aprovada; ADR-0058 e documento técnico 63.
- **Campanhas:** cada campanha/ramo tem *knowledge pack* versionado, manifesto de referências anuais e vínculo com checkpoint/época/build. Publicação de novo lore não troca automaticamente o pack da campanha.
- **Decisões preservadas:** DEC-060 — pastas físicas **por ano DR** e consultas temporais; DEC-061 — proveniência, versões e conflitos; DEC-062 — staging e publicação controlada antes de oferecer atualização.
- **Adoção:** diff por alegação/ano e impacto em eventos confirmados, quests, NPCs, história pessoal, overlays, ACL, risco e compatibilidade; seleção coerente; aprovação do anfitrião por padrão e revisão humana para conflitos/substância; HIGH/UNCERTAIN não autoaplicado.
- **Consistência:** gates DEC-052/053/054, retenção de last-known-good, promoção lógica e possibilidade condicionada de recuperação; não presumir hot-swap nem reescrever save/event log para acomodar nova fonte. Crenças NPC não mudam automaticamente.
- **Próxima:** DEC-064 (mudança de memória/conhecimento individual de NPC); DEC-006/013/015/017/018 seguem abertas. 32 testes candidatos, não executados; nenhuma POC BG2:EE/EEex/multiplayer.

## DEC-064 — Memória persistente e aprendizado contextual dos NPCs (2026-11-06; Discovery v6.0)

- **Escolha expressa:** **C**, ADR-0059 e doc. 64. Os NPCs mantêm episódios de aquisição de informação e crenças individuais versionadas; podem reconsiderar crenças ao receber evidências por canal legítimo, com proveniência, contexto, tempo e ACL.
- **Não equivalências:** novo cânone/pack ≠ conhecimento automático do NPC; rumor/relato ≠ fato histórico; memória de ouvir algo ≠ concordar com aquilo; correção de crença ≠ edição retroativa de diálogo/evento confirmado.
- **DEC-060–063 intocadas:** pastas **fisicamente separadas por ano DR**; fontes/conflitos preservados com curadoria; ingestão validada; Knowledge Packs pinados por campanha e sem migração automática. Memórias NPC são projeções da campanha/ramo, não arquivos canônicos anuais.
- **Gates:** DEC-028/029 para acesso/difusão; DEC-030/035–037 para reputação/alinhamento; DEC-011/012 e host para efeitos mecânicos; DEC-060 para validar a saída. Jobs stale/UNCERTAIN não se confirmam.
- **Próxima DEC-065:** política de retenção/consolidação/esquecimento de memória; 30 testes candidatos não executados; SPECS/POCs ainda necessárias.


## DEC-065 — Memória hierárquica, consolidação contextual e âncoras críticas (2026-11-06; Discovery v6.1)

- **Opção C escolhida:** ADR-0060 e documento técnico 65. Quatro níveis lógicos: memória imediata, episódios rastreáveis, sínteses consolidadas e âncoras críticas de acontecimentos/relacionamentos/compromissos.
- **Consolidação:** resumos são derivados reconstruíveis com vínculos a episódios/versões/ACL, não novos fatos; reduzir recuperação não significa apagar fontes. Não se aprova expiração temporal cega nem retenção ilimitada de dados privados.
- **DEC-060–064 integralmente mantidas:** diretórios canônicos **fisicamente segregados por ano DR**, fontes/alegações curadas, publicação controlada, manifesto de Knowledge Pack por campanha, aprendizado individual por evidência legítima. Episódios e sínteses NPC ficam no overlay privado por campanha/ramo.
- **Segurança:** recuperar apenas o que NPC e solicitante podem conhecer, obedecer ACL/tempo, checkpoints, autoridade do host e políticas de exclusão/privacidade. Proteção de memória crítica não dá licença para divulgar segredos.
- **Evidência:** escolha expressa do idealizador, 32 testes candidatos não executados, sem benchmarks/POC. **Próxima DEC-066:** reconhecimento de identidade NPC entre saves/áreas/builds. DEC-006/007/013/015/017/018 abertas.

## DEC-066 — Identidade persistente e correspondência verificada (2026-11-06; Discovery v6.2)

- **Escolha expressa:** **C**; ADR-0061 e documento 66. Separar identidade narrativa `NPCIdentity` por campanha/ramo de observações efêmeras do motor; exigir evidência positiva antes de ligar memórias/segredos a instância runtime.
- **Fail-closed:** nomes iguais, IDs reciclados, clones, duplicatas, snapshots incompatíveis, migração de build ou múltiplos candidatos não autorizam merge; `AMBIGUOUS`/`STALE` → sem memória pessoal, sujeito a reconciliação. LLM e worker LAN não certificam identidade.
- **DEC-060–065 integralmente preservadas:** cânone por diretório físico anual, proveniência e curadoria, ingestão controlada, Knowledge Packs por campanha, memória/adaptação de crenças e consolidação por NPC no overlay de campanha.
- **Limite:** desenho sem ID estável confirmado, sem POC de BG2:EE/EEex/multiplayer; 34 testes candidatos não executados. **Próxima DEC-067:** individualização persistente de NPCs únicos/genéricos.

## DEC-067 — Individualização híbrida e promoção progressiva (2026-11-06)

- **Escolha expressa:** opção **C**, ADR-0062 e doc. 67. NPCs únicos curados/companheiros são prioritários; NPCs genéricos começam agregados ou efêmeros e podem tornar-se persistentes após interação/acontecimento relevante **confirmado**, com evidência de identidade DEC-066 e política de risco.
- **Não usar LLM para certificar pessoa, passado ou engine:** homônimos, CREs, IDs reciclados e spawn duplicado bloqueiam vínculo automático; memórias, segredos, crenças e compromissos são projetados só após identificação verificada e ACL.
- **Orçamento e consistência:** promoção lógica idempotente, transição agregado/individual sem dupla contagem, sem spawn automático ou LLM/tick; prioridades DEC-021/022/056 e host/gateway DEC-011/012.
- **DEC-060–066 preservadas:** pastas canônicas por ano DR, proveniência, ingestão controlada, packs pinados, memória/credo por overlay e identidade comprovada. Nenhum ADR histórico modificado.
- **Evidência:** 36 testes candidatos não executados, POCs BG2:EE/EEex/multiplayer pendentes. **Próxima DEC-068:** hibernação/atividade de NPC persistente fora de cena.


## DEC-068 — Vida persistente e hibernação segura de NPCs (2026-11-06; Discovery v6.4)

- **Escolha expressa:** opção **C**; ADR-0063 e documento 68. NPC já individualizado conserva identidade, memórias, compromissos e histórico mesmo em `DISTANT/DORMANT`; hibernação operacional nunca apaga história ou implica perda automática de individualidade.
- **Regimes:** reutilizar DEC-021 `ACTIVE/NEAR/DISTANT/DORMANT`, DEC-022 `FROZEN/PARTIAL/REALTIME`, RPD DEC-056 para quotas e lotes, sem LLM por NPC/tick. `world_time` não avança porque trabalho está pendente.
- **Resolução de efeito:** offscreen produz propostas auditáveis; efeitos mecânicos exigem host/receipts e as autorizações de risco/roteiro nativo. `UNCERTAIN` e `STALE` impedem commit; retomar por checkpoint/branch/ACL/build/identidade verificada DEC-066 e individualização DEC-067.
- **Preservação:** DEC-060–067 e ADR-0055–0062 não modificados; cânone por diretórios anuais, overlays privados de campanha. São 36 testes candidatos não executados; SPECS e BG2:EE/EEex/multiplayer pendentes.
- **Próxima DEC-069:** trajetória/localização regional plausível de NPCs fora de cena, sem pressupor movimento físico contínuo no motor.

## DEC-069 — Itinerários hierárquicos de NPCs (2026-11-06; Discovery v6.5)

- **Aprovação expressa C:** ADR-0064/documento 69. Viagens como planos/trechos geográficos com procedência, janelas temporais e restrições de mundo; detalhe ACTIVE/NEAR/DISTANT/DORMANT. Sem LLM/tick e sem simulação física contínua.
- **Presença:** `ARRIVED_NARRATIVE` é distinta de `ENGINE_OBSERVED`, exigindo prova de host, identidade verificada e build compatível; não teleportar nem assumir spawn disponível.
- **Segurança/tempo:** impedir roteamento por grafos incertos, dados futuros não autorizados, contagem duplicada, replay e ações mecânicas sem receipts; DEC-022 clock/catch-up, DEC-053 checkpoint, DEC-056 prioridades.
- **Preservação integral:** DEC-060–068 e ADR-0055–0063 não alterados; 40 testes candidatos não executados e integração BG2:EE/EEex/multiplayer não comprovada.
- **Próxima DEC-070:** perigos, incidentes e encontros durante jornadas offscreen por classe de risco.

## DEC-070 — Incidentes de viagem proporcionais ao risco (2026-11-06; Discovery v6.6)

- **Escolha expressa:** opção **C**, ADR-0065/doc.70. Viagens DEC-069 admitem propostas de encontros sociais, interrupções e perigos, fundadas em fontes/relógio/segmento/identidade.
- **Resolução:** LOW narrativo seguro com allowlist, validação, ACL, idempotência e quotas; MEDIUM sujeito a autorização contextual; HIGH bloqueado até gates e, para consequência mecânica, recibo do host. Sequências de LOW que produzam HIGH são classificadas pelo impacto cumulativo.
- **Nenhuma falsa execução:** boato de emboscada não equivale a ataque ocorrido; LLM não decide combate, HP, XP, inventário, morte, roteiro nativo ou canon. Incerteza e falha de host bloqueiam efeito e retry cego.
- **Continuidade:** DEC-060–069 e ADR-0055–0064 preservados; partições canônicas anuais físicas, overlays por campanha, proveniência, Knowledge Pack, memória/identidade, hibernação e itinerário.
- **Evidência:** 44 testes T070 candidatos **não executados**, POC BG2:EE/EEex/multiplayer pendente. **Próxima DEC-071:** handoff de incidente offscreen para encontro local, sem resolução dupla.

## DEC-071 — Handoff controlado entre incidente offscreen e encontro jogável (2026-11-06)

- **Escolha expressa:** opção **C**, ADR-0066 e documento técnico 71. Incidentes pendentes DEC-070 poderão oferecer encontro local **somente** após evidência de proximidade da party, compatibilidade por build/área/quest, identidades NPC verificadas, política de risco e autorização.
- **Prevenção de resolução dupla:** reserva exclusiva durável por `incident_id` e `resolution_epoch` suspende worker offscreen; CAS/fencing/idempotência/receipts de host asseguram um único resultado. Falha `UNCERTAIN` exige reconciliar, nunca executar novamente às cegas.
- **Separação de verdade:** oferta narrativa não equivale a spawn, batalha ou presença no motor. Sem capability realmente testada não haverá materialização; evento permanece narrativo ou pendente. Host decide mecânica DEC-011/012, respeitando scripts nativos DEC-050 e multiplayer.
- **Preservação expressa:** DEC-060–070 e ADR-0055–0065 continuam inalterados; cânone por pastas físicas anuais, sem gravação de eventos no corpus. **46 testes candidatos T071-01..46 não executados**; SPECS/POCs pendentes.
- **Próxima DEC-072:** catálogo seguro de modelos/templates de encontros por build (aberta).

## DEC-072 — Catálogo modular de encontros por build (2026-11-06; Discovery v6.8)

- **Escolha expressa:** opção C, ADR-0067/doc. 72. Catálogo modular curado de templates, áreas, atores, scripts e adapters com manifesto, hashes, proveniência/direitos, dependências e capacidades testadas por build.
- **Gates:** `PRESENT` ≠ capacidade executável; uso local exigirá POC de adapter e teste host+2 clientes para multiplayer, DEC-050/051, risco DEC-027/070, gateway/host DEC-011/012 e reserva DEC-071. Ausência de capability = narrativa/pendente.
- **Preparação offline:** expansão de conteúdo somente após validação estática, licença, conflitos, backup, rollback ensaiado e autorização. Sem geração arbitrária de recursos/scripts em runtime, spawn presumido ou distribuição não autorizada.
- **Preservação integral:** DEC-060–071 e ADR-0055–0066 inalterados; cânone em pastas anuais físicas, efeitos no overlay da campanha, ledger único de incidente.
- **Evidência:** 48 testes candidatos T072-01..48 **não executados**, sem POC BG2:EE/EEex/multiplayer. **Próxima DEC-073:** limpeza e persistência pós-encontro.

## DEC-073 — Pós-encontro por propriedade e persistência seletiva (2026-11-06; Discovery v6.9)

- **Opção C aprovada:** ADR-0068 e documento 73. Encerrar encontro com `EncounterClosurePlan` candidato; classificar componentes por proveniência e ownership da **instância**, preservar resultado e memória confirmados e limpar somente temporários permitidos por gates/receipts do host.
- **Proteções:** nenhum cleanup de atores/quests/mods nativos, NPCs individualizados ou loot já transferido. `UNCERTAIN`, `STALE` e divergência de checkpoint/build bloqueiam retry/destruição; DEC-071 continua garantindo resolução única do incidente.
- **Cânone:** DEC-060 diretórios anuais físicos e DEC-061–063 fontes/packs permanecem intactos; overlay de campanha separado. DEC-060–072 e ADRs prévios integralmente preservados.
- **Evidências:** 50 testes candidatos não executados e nenhuma capability BG2:EE/EEex/multiplayer validada. Próxima **DEC-074**, propagação causal de consequências confirmadas.


### DEC-074 — Repercussão causal, gradual e contextual (2026-11-06)

- **Aprovada opção C**; ADR-0069; documento 74. Evento confirmado DEC-071/073 pode gerar testemunhos e notícias pelo grafo DEC-029, nunca conhecimento universal. Crenças, reputação, facções e economia recebem propostas distintas e validadas conforme risco; nenhum efeito de engine sem host/adapter/POC.
- Deduplicação pelo `(evento, alvo, tipo de efeito, regra, campanha, ramo)`, ACL e checkpoints; correções não apagam recibos anteriores.
- DEC-060–073 e ADR-0055–0068 preservados integralmente; cânone físico por ano, overlays privados por campanha. 52 testes candidatos não executados.
- **DEC-075 aberta:** atribuição de crédito/responsabilidade em ações compartilhadas.

## DEC-075 — Atribuição factual e reconhecimento social (2026-11-06; Discovery v7.1)

- **Escolha expressa C:** ADR-0070 e doc 75. Ação confirmada, participação fundamentada, testemunhos, percepção social e efeito são registros distintos, com cronologia e proveniência.
- **Coop:** reconhecer papéis de dano, cura, proteção, negociação, suporte e coordenação **quando observáveis**; se o motor não fornecer prova fina, marcar `UNKNOWN`. O grupo pode receber reconhecimento coletivo legítimo, sem crédito uniforme automático nem culpa presumida de ausentes.
- **Controles:** identidade DEC-066, dono/controle delegado DEC-045/046, consentimento DEC-041/042, ACL DEC-028, propagação DEC-029/074; idempotência, risco, checkpoints e host/gateway impedem recompensas/efeitos fictícios.
- **Preservação:** DEC-060–074 e todos os ADRs anteriores byte a byte intactos; cânone em diretórios físicos por ano DR, autoria/reputação no overlay da campanha.
- **Evidência:** 54 testes candidatos não executados; DEC-076 aberta para personas, pseudônimos e anonimato; nenhuma integração de telemetria BG2:EE validada.

## DEC-076 — Identidade factual privada e personas contextuais (2026-11-06; Discovery v7.2)

- **Opção C aprovada:** ADR-0071/documento 76. Identidade factual comprovada permanece privada; um ator pode apresentar personas e pseudônimos diversos, sem conhecimento automático do vínculo por NPC/facção/jogador.
- **Provas e revelação:** identificação por nome ou aparência é insuficiente; evidências com proveniência e identidade DEC-066 sustentam ligações privadas; suspeita ≠ prova e prova interna ≠ divulgação. Audiência, finalidade, consentimento, risco, tempo, ACL e canais DEC-029/074 obrigatórios.
- **Efeitos:** não fundir reputações por alias, não reescrever fatos passados, nem alterar nomes/disfarces mecânicos por suposição. DEC-011/012 e capacidades testadas do host continuam exigidas.
- **Preservação:** DEC-060–075 e todos os ADRs prévios inalterados; cânone anual físico, personas e provas em overlay privado. **56 testes candidatos T076-* NÃO EXECUTADOS.** Próxima DEC-077: investigação por pistas e contestação contextual.

## DEC-077 — Investigações de identidade por evidências verificáveis (2026-11-06; Discovery v7.3)

- **Opção C aprovada.** ADR-0072 e documento técnico 77. Investigadores coletam pistas e testemunhos, controlam independência real das fontes, testam contradições, preservam álibis e registram hipóteses revisáveis.
- **Estados distintos:** suspeita/conhecimento do observador, vínculo factual privado e divulgação autorizada. Investigação inconclusiva permanece inconclusiva; LLM jamais arbitra sozinho a identidade.
- **Gates:** público e consentimento do titular, ACL de PC, risk gates e host/gateway para consequências mecânicas; `STALE/UNCERTAIN` bloqueia vazamento e mutações. Nenhuma prisão ou punição aprovada por esta decisão.
- **DEC-060–076 e ADRs anteriores preservados:** diretórios canônicos separados fisicamente por ano DR, overlays de investigação/segredos exclusivos da campanha. **58 testes candidatos T077-* NÃO EXECUTADOS.** Próxima DEC-078 aberta para consequências legais/faccionais.

## DEC-078 — Procedimentos locais, acusações e decisões de autoridades (2026-11-07; Discovery v7.4)

- **Aprovada opção C:** ADR-0073 e documento técnico 78. Jurisdições e facções possuem procedimentos contextuais próprios, fontes/tempo DR e contestação aplicável; alegação, evento factual, decisão oficial e efeito mecânico são camadas diferentes.
- **Regras/código primeiro:** sem LLM para decidir culpa, competência ou sanções; LLM local eventual para diálogos filtrados por ACL. HIGH e impactos mecânicos exigem autorização, consentimento aplicável, gateway tipado e receipt host.
- **Segurança:** identidade/participação DEC-066/075/076/077, privacidade DEC-019/028, risco DEC-027/034, checkpoint DEC-053/054 e dedup por ramo/caso/decisão/efeito.
- **Preservação DEC-060–077 e ADRs anteriores integralmente:** cânone anual físico e KPack; processos somente no overlay da campanha. **60 testes T078-* não executados**. Próxima DEC-079: competência e cooperação entre jurisdições.

## DEC-079 — Mandados e pedidos entre jurisdições (2026-11-07; Discovery v7.5)

- **Escolha expressa C:** ADR-0074/documento 79. Relações entre autoridades dirigidas e datadas; solicitações via canais com prova de entrega. O destinatário analisa competência própria e pode aceitar, condicionar, negociar, negar ou contestar.
- **Separação:** emissão ≠ recepção ≠ reconhecimento ≠ consequência mecânica; pedido local não tem validade global automática e guardas não se teleportam. Regras determinísticas e ACL primeiro, LLM local só para diálogos.
- **Proteção:** identidade/segredos DEC-066/075/076/077, coop DEC-041/042, risco DEC-027/034, host/gateway DEC-011/012, viagens/clock DEC-022/069, duplicação/restore/UNCERTAIN DEC-053/054.
- **Preservação:** DEC-060–078 e todos os ADRs anteriores idênticos. Knowledge Packs anuais e corpus físico não são modificados por mandados de campanha. **62 testes candidatos NÃO EXECUTADOS**, POCs pendentes.
- **Próxima DEC-080:** revogação, retificação e sincronização causal de pedidos distantes.

## DEC-080 — Suspensões, retificações e revogações por versão (2026-11-07; Discovery v7.6)

- **Escolha C aprovada:** ADR-0075/documento 80. Ordens passam por revisões rastreáveis e mensagens causais entre jurisdições, sem considerar que todos os destinatários saibam instantaneamente de revogação.
- **Segurança:** estado autoritativo da origem separado da crença local e do gate mecânico; ações coercitivas HIGH sobre PC ficam suspensas se a ordem foi revogada, não tem competência/validade confirmada ou host/adapter não foi validado. A consulta interna de safety não cria conhecimento de NPC.
- **Operação:** ordem tardia não ressuscita mandado; tombstones, dedup por ordem+revisão+destinatário, checkpoints, UNCERTAIN/STALE e autorização previnem execução duplicada; correções não apagam atos passados.
- **Preservação integral:** DEC-060–079 e ADRs anteriores; cânone por pastas físicas anuais DR, processos em overlay de ramo. 64 testes T080 candidatos **NÃO EXECUTADOS**.
- **Próxima DEC-081:** mecanismos de revisão e reparação contextual para danos de ordens indevidas.

## DEC-081 — Reparação contextual após injustiça (2026-11-07; Discovery v7.7)

- **Escolha C aprovada:** ADR-0076 e documento 81. Distinguir ordem revogada, dano confirmado, nexo causal, autoridade competente, remédio autorizado, narrativa e mudança de engine com receipt.
- **Reparações contextualizadas:** indenização, devolução, pedido de desculpas e reabilitação são propostas por jurisdição/ano e tipo de dano, com consentimento/ownership; não há rollback automático, perdão imposto, item duplicado nem onisciência de NPC.
- **Gates:** LOW/ MEDIUM/HIGH e magnitude acumulada; HIGH fail-closed. Quest/liberdade/itens/ouro dependem do host, adapter testado por build, idempotência e checkpoint, com UNCERTAIN sem retry.
- **Preservação:** DEC-060–080 e 75 ADRs anteriores intactos; corpus físico por ano, overlay separado de casos/efeitos. **66 testes T081 não executados**. Próxima DEC-082: responsabilização institucional.

## DEC-082 — Responsabilização contextual por abuso de autoridade (2026-11-07; Discovery v7.8)

- **Opção C aprovada:** investigação de agentes, cadeia de comando, omissões e padrões institucionais, com evidências independentes, competência da autoridade, contraditório narrativo contextual e risco cumulativo. ADR-0077/doc.82.
- Reparação DEC-081, revogação DEC-080 e punição são processos separados. Rumores não provam culpa e não alteram automaticamente reputação da instituição inteira.
- Host/gateway DEC-011/012 para efeitos mecânicos; mudanças canônicas protegidas DEC-034. LLM propõe diálogos, não condenações, reformas, demissões ou golpes.
- DEC-060–081 e ADRs anteriores integralmente preservados; conhecimentos históricos em diretórios físicos por ano DR e consequências em overlays privados. **68 testes candidatos não executados**; DEC-083 aberta.

## DEC-083 — Proteção proporcional de testemunhas e fontes (2026-11-07; Discovery v7.9)

- **Opção C aprovada:** ADR-0078/doc 83; separar identidade selada, depoimento, proveniência, risco e evento de divulgação. ACL e consentimento por audiência/finalidade; publicidade e sigilo absoluto rejeitados como defaults.
- **Investigação legítima:** extratos filtrados e contradições podem ser considerados sem expor testemunha; confidencialidade não confirma veracidade. Medidas HIGH ou contra PCs não são automáticas; host/Action Gateway para qualquer efeito de engine.
- **Proteção:** não inventar escolta, invulnerabilidade, prisão ou teleporte; avaliação de ameaça não prova ataque. Sigilo de PC, persona, memória NPC e competência de autoridade mantidos.
- **Integridade:** disclosures versionados/idempotentes, branch/checkpoint/ano DR, ACL antes do LLM/LAN/índice/UI/log; cânone físico por ano preservado. DEC-060–082 e 77 ADRs anteriores intactos.
- **Status:** 70 testes T083-01..70 candidatos NÃO EXECUTADOS; DEC-084 em aberto para resposta a ameaças e proteção ativa.

## Integração DEC-084/C — Discovery v8.0: proteção ativa contextual e gradual

- **Escolha expressa C:** ADR-0079/documento 84. Ameaças com proveniência e risco não são agressões confirmadas; respostas candidatas incluem comunicação segura, discrição, abrigo, proteção de aliados, escolta e mudança de localização conforme consentimento.
- **Capacidade:** disponibilidade de NPCs, rotas, recursos, tempo e autoridade regional precisam ser verificadas. Sem teleporte, invulnerabilidade ou captura mecânica por narração; gate host/action gateway e risco HIGH default-deny.
- **Privacidade:** fontes e planos de proteção sob ACL DEC-083; adversários sem metaconhecimento. Ações offscreen/local não se duplicam; restore/UNCERTAIN exige reconciliação.
- **Preservação:** DEC-060–083 e ADRs antigos imutáveis; cânone em partições físicas por ano DR e estado do caso no overlay de campanha. 72 testes candidatos NÃO EXECUTADOS. Próxima DEC-085: sigilo operacional e descoberta causal de planos.

## DEC-085/C — Sigilo operacional e descoberta legítima de planos (2026-11-07; v8.1)

- **Opção C aprovada:** ADR-0080 e documento técnico 85; segredo por campo/segmento, audiência/propósito, descoberta parcial e gradual somente com fonte, presença, tempo e canal verificados. Acesso do backend não implica crença de NPC.
- **Ameaça e proteção:** vazamento inferido não implica plano todo comprometido, nem emboscada, perseguição ou teleporte. Replanejamento DEC-084 requer recursos/consentimento/risco, confirmação mecânica somente pelo host/Action Gateway.
- **Integridade:** diferencia plano factual, pista alegada, evidência, crença, comprometimento e evento de divulgação, com ledger idempotente, reconciliando checkpoint/branch e grants. Não propagar dados privados ao LLM, LAN, caches/logs ou diretórios canônicos anuais.
- **DEC-060–084 preservadas integralmente, ADRs anteriores intactos.** 74 testes candidatos NÃO EXECUTADOS. DEC-086 sobre engano defensivo permanece **aberta**.

## DEC-086/C — Contraespionagem, iscas e desinformação autorizada (Discovery v8.2)

**Opção C expressamente aprovada em 2026-11-07; ADR-0081; documento técnico 86.** Operações narrativas de engano precisam de autoria, consentimento, objetivos, recursos, canais/tempo, limitações a terceiros e risco. `PlantedClaim` é alegação deliberadamente falsa, sem virar `WorldFact`, prova de crime, host receipt ou fato canônico. NPCs só recebem informação por meios causais válidos e podem desconfiar/contestar; sem revelação do plano verdadeiro. MECÂNICA somente via host/gateway após POC. **76 testes candidatos NÃO EXECUTADOS**. DEC-060–085 e ADR-0001..0080 preservados integralmente. Próxima DEC-087: agentes duplos e lealdades conflitantes.

## Integração da DEC-087/C — Registro aprovado (Discovery v8.3)

- **Escolha expressa C (2026-11-07):** ADR-0082 e documento técnico 87; NPCs podem manter compromissos e lealdades múltiplos, com tensões e mudanças fundamentadas, sem traições automáticas ou motivações fabricadas pela LLM.
- **Eixos distintos:** `LoyaltyBond`, `Commitment`, `ConflictAssessment`, `ObserverBelief`, `LoyaltyTransition`; filiação não comprova culpa e suspeita não é fato. PCs nunca perdem autoria de suas escolhas, companheiros mantêm autonomia.
- **Mecânica:** qualquer saída de party, hostilidade ou alteração de facção/quest/inventário requer build POC, host receipt e gates DEC-011/012/027/034/041/047/048/050.
- **Preservação:** DEC-060–086 e ADRs anteriores idênticos; cânone físico por ano DR e vínculos privados por campanha/ramo. **80 testes T087-01..80 NÃO EXECUTADOS.** Próxima DEC-088 em aberto.

## DEC-088 — Recrutamento voluntário e negociação de informantes (2026-11-07; Discovery v8.4)

- **Opção C aprovada**: contato/verificação de elegibilidade, oferta, contraproposta, recusa, aceite, acordo com escopo e prazo, reservas de recursos, informe prometido, informe entregue e rescisão separados em ledger. ADR-0083 / documento 88.
- NPC respeita valores, obrigações, autonomia e limites canônicos DEC-047/048/087; PC escolhe compromissos por titular ou delegação específica DEC-041/045/046. Não comprar lealdade automaticamente nem determinar decisão pela LLM.
- Ouro/itens somente com saldo, reserva, gateway, confirmação host e idempotência; confidencialidade e proveniência não conferem automaticamente conhecimento ou veracidade.
- DEC-060–087 e ADR-0001..0082 preservados; cânone em diretórios físicos por ano DR, acordos no overlay privado. **82 testes candidatos T088-01..82 NÃO EXECUTADOS**. Próxima DEC-089: avaliação da qualidade dos informes.

## DEC-089/C — Verificação de informes e corroboração independente (Discovery v8.5, 2026-11-07)

- **Decisão aprovada:** relatórios recebidos de fontes informais/recrutadas devem passar por análise de origem, capacidade de conhecimento da fonte, cadeia de retransmissão, corroboração independente, contradições e risco. Fonte recrutada não é fonte infalível.
- **Autoridade:** entrega ≠ conteúdo verdadeiro; A e C dependentes não valem como duas provas; LLM apenas auxilia, não confirma fatos, aplica punições ou publica segredo. Parecer inconclusivo é permitido.
- **Segurança:** ACL e consentimento DEC-019/028/041/083; fatos/rumores armazenados no overlay por campanha/branch, com relógio DR e checkpoints; cânone anual DEC-060 fisicamente intacto.
- **Artefatos:** ADR-0084, documento 89 e **84 testes T089-01..84 candidatos NÃO EXECUTADOS**. Todas DEC-060–088/ADRs anteriores preservados. Próxima DEC-090: dossiês e compartilhamento seletivo de inteligência.

## Integração DEC-090/C — Discovery v8.6

**Decisão:** DEC-090/C, **aprovada em 2026-11-07**. Dossiês de inteligência versionados preservam alegações, evidências independentes e contraditórias DEC-089, com views filtradas por audiência/finalidade e transmissão por canal e tempo plausíveis. Um dossiê compilado não equivale a documento entregue; nenhum NPC recebe conhecimento global automaticamente. ADR-0085/documento 90; 86 testes candidatos **NÃO EXECUTADOS**. DEC-060–089 e todos ADRs prévios integralmente preservados. **DEC-091 aberta:** ações operacionais baseadas em inteligência incerta.

## Integração DEC-091/C — Discovery v8.7

- **Escolha expressa:** opção C em 2026-11-07; ADR-0086/documento 91. Planejar com dossiês incertos é permitido mediante evidências, recursos, presença, cronologia e risco, mas **planejamento não é execução**.
- **Autoridade:** aprovação individual de PCs, limites da autonomia NPC/faccional, gateway e confirmação mecânica do host. Falta de prova ou capability produz BLOCKED/PENDING, não resultado fictício.
- **Preservação:** DEC-060–090 e 85 ADRs anteriores intocados; cânone físico anual e overlay privado segregados. **88 testes T091-* candidatos NÃO EXECUTADOS**.
- **Próxima DEC-092:** monitoramento e replanejamento em execução, opções A fixo/B LLM livre/C orientado a eventos/gates (aberta).

## DEC-092/C — Monitoramento por eventos e replanejamento controlado (2026-11-07; Discovery v8.8)

- Opção C aprovada, ADR-0087/documento 92: receber fatos confirmados; diferenciar alerta, pausa lógica, abortar, nova revisão de plano, reautorização, despacho e receipt host.
- Mudanças materiais de risco, participantes, objetivos, destino, recursos, horário ou ACL invalidam validações/consentimentos anteriores no escopo afetado. Retirada de consentimento de PC impede novos atos em seu nome.
- `PAUSED_ORCHESTRATION` **não** comprova pausa de engine; cancelamento não desfaz atos confirmados e `UNCERTAIN` exige reconciliação em vez de retry cego.
- Planos/dossiês continuam em overlay privado por campanha/branch e o cânone físico anual DEC-060 permanece intacto. DEC-060–091 e 86 ADRs anteriores preservados. 90 testes T092-* **NÃO EXECUTADOS**.
- Próxima DEC-093: coordenação determinística de várias operações concorrentes com objetivos e recursos conflitantes.

## Integração da DEC-093/C — operações simultâneas (2026-11-07; Discovery v8.9)

- Opção **C aprovada**, ADR-0088/documento técnico 93. Scheduler determinístico para planos concorrentes, conflitos por identidade, recurso, tempo/posição, compatibilidade e recursos exclusivos; reservas lógicas com fencing e fairness.
- Autorização de PC e de host não é substituída por urgência, fila P0–P4 ou saída LLM. Receipts e `UNCERTAIN` bloqueiam duplicidade e liberação prematura.
- DEC-060–092 e ADRs anteriores preservados; 92 testes T093-* candidatos não executados. Próxima DEC-094 aberta para resolução segura de deadlocks/starvation.

## Integração DEC-094/C (Discovery v9.0) — decisão aprovada

**DEC-094, opção C, aprovada em 2026-11-07**: recuperação determinística de ciclos reais no grafo de espera, risco de starvation e reservas órfãs, com autorização, fairness, fencing, quarentena de efeitos incertos e reconciliação com host. ADR-0089 e documento técnico 94. `UNCERTAIN` e lease expirado não autorizam liberação física. DEC-060–093 e ADRs antigos preservados. **94 testes candidatos não executados.** DEC-095 aberta: compensações explícitas e seguras de operações parcialmente concluídas.

## Integração DEC-095/C — Discovery v9.1

**Opção C aprovada em 2026-11-07.** Operações parcialmente concluídas usam Saga versionada: nenhum rollback global; cada compensação é um novo ato validado, autorizado, host-confirmed e auditável. Etapas irreversíveis persistem. ADR-0090, doc. 95 e 96 testes candidatos **NÃO EXECUTADOS**. DEC-060–094 preservadas; 89 ADRs byte a byte intocados. A proposta do idealizador de matriz temporal/espacial de eventos FR foi refinada no doc. 96 e em fixtures sintéticas; **DEC-096 permanece aberta**.

## Integração DEC-096/C — Discovery v9.2

**Opção C expressamente aprovada (2026-11-07).** Matriz cronológica condicional por ano DR, fonte e precisão temporal, região, local/tag, fase, DSL declarativa, dependências e efeitos diretos/indiretos condicionados a confirmações. Catálogo canônico segregado fisicamente DEC-060–063, regras editoriais versionadas e estado de campanha causal separados. Registros de lore não executam engine. ADR-0091 e doc. técnico 96; 100 testes candidatos **NÃO EXECUTADOS**. 90 ADRs anteriores byte a byte preservados; testes de código meramente sintéticos. DEC-097 aberta para composição de efeitos simultâneos.

## Integração DEC-097/C — Discovery v9.3

**Aprovada por escolha expressa do idealizador em 2026-11-07.** A alternativa C determina agregação causal, tipada e determinística por domínio, políticas de famílias/precedência, limites, duração/decay no relógio DR, idempotência e auditabilidade. **ADR-0092** e **doc 97**; **102 testes T097-* NÃO EXECUTADOS**. Não confundir simulação unitária com comprovação de sistema BG2:EE/EEex. Anteriores DEC-060–096 mantidas, 91 ADRs bytes idênticos. **DEC-098 aberta:** materialização incremental/snapshots locais.

## DEC-098/C — Registro formal de decisão (Discovery v9.4)

- **Data/alternativa:** 2026-11-07, opção **C** explicitamente aprovada.
- **ADR:** `ADR-0093-materializacao-incremental-de-repercussoes-regionais-snapshots-deltas-e-reconciliacao.md` (**APROVADA COMO ARQUITETURA**); doc técnico 98.
- **Escopo:** diferenças incrementais entre projeção DEC-096/097, último snapshot host-confirmed e observação local; identidade persistente distinta de engine instance, ownership e capability por build; proposta, risco, consentimento, dispatch, receipt e reconciliation separados. Catch-up offscreen bounded sem simular mortes ou encontros não confirmados.
- **Restrições:** histórico canônico segregado por ano DR, quests/mods/PCs protegidos, nenhum spawn/cleanup implícito, evitar duplicação pós-reentrada e após restore. `UNCERTAIN` não recebe retry cego.
- **Integridade:** 92 ADRs anteriores byte a byte idênticos ao v9.3. **104 testes de integração T098-* NÃO EXECUTADOS**; ensaios Python e JSON são exclusivamente sintéticos.
- **Próxima decisão:** DEC-099 EM ABERTO: conflitos de ownership e precedence entre scripts originais, quests, mods e overlay de world state.


## Registro atual — DEC-099/C (2026-11-07, Discovery v9.5)

| ID | Escolha | ADR | Contrato | Condição de implementação |
|---|---|---|---|---|
| **DEC-099** | **C — ownership granular por instância/campo, compatibilidade por build e respeito a quests/scripts/mods/PCs** | `decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md` | `99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md` | **APROVADA COMO ARQUITETURA**; preflight sintético apenas; hooks/multiplayer não testados |
| **DEC-100** | Em aberto — observabilidade read-only allowlisted de quests/scripts, ACL e spoilers | — | — | Nova discussão, não aprovada |

**Governança:** ADR-0001 a ADR-0093 anteriores inalterados byte a byte; DEC-060–DEC-098 mantidas. `UNKNOWN`, quest, script original, mod terceiro e PC permanecem protegidos. T099-001..120 **não executados**.


## Registro formal — DEC-100/C (2026-11-07; Discovery v9.6)

| ID | Opção | ADR | Documento técnico | Estado |
|---|---|---|---|---|
| **DEC-100** | **C — observação read-only com allowlist/capability por build, ACL, proteção contra spoilers e conhecimento narrativo segregado** | `decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md` | `100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md` | **APROVADA como arquitetura; POCs pendentes** |
| **DEC-101** | Em discussão — mapeamento semântico curado por build | — | — | **EM ABERTO** |

**Preservação:** DEC-060 a DEC-099 e 94 ADRs anteriores inalterados. Probes são somente-leitura se essa propriedade for **demonstrada na build**, não apenas declarada. T100-001..124 são **candidatos não executados**.

## Registro formal — DEC-101/C (2026-11-07; Discovery v9.7)

| ID | Alternativa | ADR | Contrato | Status |
|---|---|---|---|---|
| **DEC-101** | **C — catálogo semântico curado e versionado, provas por predicados, exclusividade, transições verificáveis e ACL separada** | `decisions/ADR-0096-mapeamento-semantico-curado-de-estados-de-quests-por-build.md` | `101-mapeamento-semantico-curado-quests-transicoes-ambiguidade-e-divulgacao.md` | **APROVADA como arquitetura; POCs pendentes** |
| **DEC-102** | Em discussão — divergências host vs overlay de quest | — | — | **EM ABERTO** |

**Invariantes:** nenhuma heurística genérica ou LLM interpreta flags desconhecidas; `UNKNOWN/AMBIGUOUS` bloqueia efeitos narrativos; no raw state vai para prompts. DEC-060–100 e 95 ADRs anteriores íntegros. Testes T101-001..128 candidatos **NÃO EXECUTADOS**.


## Integração DEC-102/C — Discovery v9.8

**Registro.** DEC-102/C expressamente aprovada em 2026-11-07. ADR-0097; contrato doc. 102. Alternativa A (overwrite host) e B (LLM livre) rejeitadas. Preservados os 96 ADRs anteriores e DEC-060..101. 132 T102 NÃO EXECUTADOS. DEC-103 aberta.


## Registro formal — DEC-103/C (2026-11-07; Discovery v9.9)

| ID | Alternativa | ADR | Contrato | Estado |
|---|---|---|---|---|
| **DEC-103** | **C — pipeline determinístico e idempotente de admissão de marcos reconciliados e propagação causal controlada** | `decisions/ADR-0098-admissao-e-propagacao-causal-de-marcos-de-quests-reconciliados.md` | `103-admissao-e-propagacao-causal-de-marcos-de-quests-reconciliados.md` | **APROVADA como arquitetura; POCs BG2:EE/EEex pendentes** |
| **DEC-104** | Em discussão — correção/retificação descendente de repercussões | — | — | **EM ABERTO** |

**Preservação:** DEC-060 a DEC-102 e ADR-0001..0097 não revogados; 97 ADRs anteriores byte a byte idênticos. Testes T103-001..T103-136 **NÃO EXECUTADOS**; os exemplos Python e JSON são sintéticos, não POCs no jogo.

## DEC-104 — Opção C aprovada (2026-11-07; Discovery v10.0)

ADR-0099. Retificar um marco não apaga consequences, receipts ou notícias já entregues. Grafo causal curado e versionado; conter futuro, reconciliar dispatch incerto, propor compensação Saga DEC-095 e revisão derivada CAS; manter NPCs falíveis, ACL e branch. T104-001..140 são candidatos NÃO EXECUTADOS. DEC-105 permanece em aberto para distribuição de erratas.

## Registro formal — DEC-105/C (2026-11-07; Discovery v10.1)

| ID | Alternativa | ADR | Contrato | Estado |
|---|---|---|---|---|
| **DEC-105** | **C — comunicação causal de retificações, evidência e entrega individual com memória falível** | `decisions/ADR-0100-propagacao-causal-de-retificacoes-e-atualizacao-falivel-de-crencas.md` | `105-propagacao-causal-de-correcoes-recebimento-crencas-e-revisoes.md` | **APROVADA COMO ARQUITETURA**, sem implementação no motor |
| **DEC-106** | Em discussão — reabilitação reputacional contextual e proporcional | — | — | **EM ABERTO** |

**Invariantes:** original, correção, envio, entrega, percepção e crença não são a mesma entidade; nunca self-grant, broadcast global, coerção de PC ou reescrita de fatos. **Preservação:** DEC-060..104 e 99 ADRs anteriores imutáveis byte a byte. **144 cenários T105 candidatos NÃO EXECUTADOS** em BG2:EE/EEex/multiplayer.

## Registro formal — DEC-106/C (2026-11-07; Discovery v10.2)

| ID | Alternativa | ADR | Contrato técnico | Estado |
|---|---|---|---|---|
| **DEC-106** | **C — reabilitação contextual, proporcional e voluntária, com danos provados e reparações específicas** | `decisions/ADR-0101-reabilitacao-reputacional-proporcional-e-restauracao-contextual-da-confianca.md` | `106-reabilitacao-reputacional-proporcional-confianca-danos-alcance-e-reparacoes.md` | **APROVADA COMO ARQUITETURA**; sem implementação no motor |
| **DEC-107** | Em discussão — direito de resposta, contestação e mediação reputacional | — | — | **EM ABERTO** |

**Preservação:** 100 ADRs anteriores intactos byte a byte, DEC-060..105 vinculantes. Prova, exposição, correção, percepção, crença, confiança, reputação e dano são registros distintos; reabilitação gera apenas proposta. **148 casos T106-001..148 são candidatos NÃO EXECUTADOS no jogo**; fixtures Python/JSON sintéticas não demonstram capacidades BG2:EE/EEex.

## Registro formal — DEC-107/C (2026-11-07; Discovery v10.3)

**Aprovada como arquitetura** a alternativa C: contraditório e direito de resposta voluntários, provas versionadas/contestáveis, representação legítima, ACL por audiência, consentimento independente, imparcialidade do facilitador e acordo por termos/revisão, sem veredito, retratação, perdão, reputação ou transferência de bens automática. ADR-0102 / doc.107. **101 ADRs anteriores preservados byte a byte, DEC-060..106 mantidas. T107-001..152 candidatos NÃO EXECUTADOS no BG2:EE/EEex.** Código/fixtures sintéticos. DEC-108 aberta: monitoramento e contestação de cumprimento de acordo.

## Registro formal — DEC-108/C (2026-11-07; Discovery v10.4)

| ID | Alternativa | ADR | Contrato | Estado |
|---|---|---|---|---|
| **DEC-108** | **C — acompanhamento determinístico de cumprimento, parcialidade, contestação e renegociação não coercitiva** | `decisions/ADR-0103-acompanhamento-causal-de-obrigacoes-acordadas-e-cumprimento-contestavel.md` | `108-cumprimento-de-acordos-obrigacoes-prazos-recibos-e-contestacao-causal.md` | **APROVADA COMO ARQUITETURA**; POCs não realizados |
| **DEC-109** | Em discussão — obrigações condicionais e encadeadas, envolvendo múltiplas partes | — | — | **EM ABERTO** |

Acordo committed ≠ obrigação realizada ≠ prestação alegada ≠ recibo host-confirmed ≠ quitação. O vencimento de prazo DR não implica culpa, multa, execução ou reputação. Descumprimento contestado exige contraditório e autoridade própria. **102 ADRs anteriores preservados byte a byte; DEC-060..107 vinculantes.** T108-001..160 são cenários **NÃO EXECUTADOS em BG2:EE/EEex**; avaliador e fixtures apenas sintéticos.

### DEC-109/C — Grafo determinístico de obrigações condicionais e acordos multipartes (2026-11-07)

**APROVADA COMO ARQUITETURA** — ADR-0104; `docs/109-obrigacoes-condicionais-acordos-multipartes-grafo-de-dependencias-e-gates.md`. Acordo committed com partes/mandatos, DAG de termos versionado, receipts autenticados, `ALL/ANY/AT_LEAST(k)` explícitos e estados `WAITING_DEPENDENCIES/READY_FOR_AUTHORIZED_PLANNING/BLOCKED_*/QUARANTINED`. Sem execução, culpa, sanção ou transferência automática por LLM. **103 ADRs anteriores preservados; T109-001..168 NÃO EXECUTADOS em BG2:EE/EEex.** DEC-110 em aberto para escrow/garantias.

## DEC-110/C — Garantias e custódia condicionada / Discovery v10.6

**APROVADA como arquitetura:** ADR-0105, contrato `docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md`. Garantia contratual não é depósito; recibo de transferência pelo host é a única prova de custódia mecânica; condições atendidas tornam liberação apenas elegível. 176 cenários candidatos não executados. DEC-111 (*baselines SPECS*) ainda aberta; questionário único em `docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md`. As decisões antigas DEC-006,007,013,015,016,017,018 permanecem abertas. Todos os 104 ADRs anteriores estão preservados byte a byte.
