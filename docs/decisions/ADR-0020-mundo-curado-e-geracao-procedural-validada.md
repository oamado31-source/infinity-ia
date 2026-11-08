# ADR-0020 — Mundo curado com geração procedural validada

- **Decisão:** DEC-010 — estratégia de criação e expansão de conteúdos.
- **Status:** **APROVADA — opção C**.
- **Data:** 2026-11-06.
- **Autoridade:** escolha expressa do idealizador nesta conversa.
- **Relacionamentos:** DEC-003 / ADR-0006 (integração incremental); DEC-004 / ADR-0002 (históricos); DEC-008 / ADR-0011 (persistência e cronologia); DEC-009 / ADR-0012 (cânone); DEC-011 / ADR-0007 (host/bridge); DEC-014 / ADR-0008 (código primeiro); DEC-021/022 (atividade/tempo); DEC-023 (1369 DR); DEC-024/025/026 (arcos); DEC-005-E / ADR-0019 (encontros); DEC-012/017 (segurança e direitos, pendentes).

## Contexto e problema

O Living World aproveita mapas, NPCs, história e regras do Baldur's Gate II: Enhanced Edition com expansão gradual por EET, Icewind Dale e NWNForBG. O objetivo é aumentar a variedade e a rejogabilidade sem comprometer estabilidade, coerência histórica e multiplayer. Geração de diálogo e missões tem riscos técnicos diferentes dos de criar/instalar recursos binários de áreas, scripts ou criaturas no motor.

## Alternativas consideradas

- **A — Somente conteúdo curado antecipadamente:** máxima previsibilidade; diversidade limitada.
- **B — Geração livre durante execução:** alta liberdade, mas risco elevado de scripts inconsistentes, dados inválidos, crashes, conflito de saves e dessincronização.
- **C — Mundo curado + geração procedural validada:** preserva os cenários existentes e cria novos conteúdos a partir de dados, modelos e componentes compatíveis, conforme gates graduais.

## Decisão aprovada — opção C

1. **Mundo curado como referência:** mapas, centros urbanos, personagens importantes, facções, datas e marcos canônicos existentes são preservados como base. Diferenças cronológicas são tratadas pelas matrizes aprovadas, com histórico e proveniência verificáveis.
2. **Geração procedural em camadas:** usar prioritariamente variações seguras de conteúdo sobre áreas existentes: objetivos de missões, pistas, rumores, diálogos e eventos narrativos, NPCs/objetos/encounters já permitidos pelo inventário de recursos. Conteúdos físicos complexos (novas áreas, tilesets, geometrias, scripts) seguem fluxo de geração **antecipada, validação e empacotamento/testes**, não injeção livre em runtime.
3. **Criatividade não é autoridade:** IA local pode propor roteiros, histórias de NPCs, descrições e alternativas. Regras determinísticas, schemas e curadoria verificam integridade, plausibilidade, cânone, histórico individual e limites de facções/biomas. IA não emite comandos Lua não filtrados, grava recursos do motor arbitrariamente, nem declara efeitos mecânicos realizados.
4. **Bridge/host como gate:** novas entidades, encontros, itens, flags, missões e recompensas que dependam de alterações mecânicas exigem capacidade suportada, permissão e confirmação do host. Estado incerto deve permanecer `UNCERTAIN` e ser reconciliado sem repetição cega, conforme ADR-0007.
5. **Versionamento e persistência:** cada pacote/instância de conteúdo deve ter identificadores únicos, origem, versão e pré-condições, associações a campanha/época/mods; estados confirmados e relações narrativas são registrados em eventos/snapshots, com seeds, idempotência, checkpoints e rollback quando aplicável.
6. **Mundos diferentes, saves isolados:** o conteúdo gerado no Living World não altera a campanha Original ou outras campanhas; não editar scripts/saves de uma instalação real sem autorização e provas de compatibilidade.
7. **Integração incremental:** validar primeiro propostas narrativas e eventos leves, depois uso de recursos já presentes, depois fluxos de pacote/área previamente compilados, e **somente se suportado por POCs** estudar geração/injeção de áreas durante a partida.
8. **Direitos e proveniência:** os recursos visuais e scripts de jogos/mods podem depender de licenças e permissão; o projeto privado não é autorização automática para redistribuição. O sistema não deve incorporar pacotes de assets proprietários nos artefatos de Discovery.
9. **Custo e execução:** criação procedural deve respeitar os níveis ACTIVE/NEAR/DISTANT/DORMANT, budgets e condições da DEC-014, sem LLM por tick, entidade ou evento trivial.

## Fronteiras de capacidade — não confundir desejo e implementação

| Tipo de conteúdo | Estratégia candidata | Estado de viabilidade |
|---|---|---|
| Rumores, descrições e conversas | Geração narrativa local sob demanda + filtros de conhecimento/cânone | Objetivo arquitetural; integração na UI/diálogos não comprovada |
| Missões estruturadas / etapas / pistas | Templates + estruturas procedurais + validação causal e de estados | Objetivo arquitetural; host/bridge ainda não validado |
| Composição de encontros | Diretor determinístico regional (ADR-0019) | Política aprovada; integração/spawn ainda não comprovados |
| NPCs, objetos e recursos já instalados | Seleção/ativação condicionada a allowlist e confirmação mecânica | Dependente de testes em BG2:EE e multiplayer |
| Masmorras e mapas inteiramente novos | Geração antecipada e validação offline do pacote + instalação compatível | POC requerida, sem presumir geração automática de recursos BG2:EE |
| Injeção dinâmica de novas áreas/scripts em jogo ativo | **Não prometida nesta decisão** | Hipótese futura sob prova técnica própria |

## Pipeline lógico aprovado (contratos a detalhar em SPECS)

`Intenção narrativa / gatilho do mundo` → `Planejador estruturado` → `Validações de lore, tempo, conhecimento, versão e risco` → `Proposta versionada` → `Gate de segurança e compatibilidade` → `Host aplica quando autorizado e suportado` → `Confirmação ou reconciliação` → `Persistência/eventos confirmados`.

- Geração de mapa/pacote passa adicionalmente por construção isolada, inspeção e testes antes de qualquer instalação.
- Entrega de texto para o jogador pode ter circuito separado de escrita mecânica; ainda assim deve observar segredos, segurança, origem da informação e compatibilidade da interface.

## Requisitos candidatos e critérios de aceitação

1. Conteúdo gerado não invalida fatos históricos já confirmados, conhecimento dos NPCs, cronologia da campanha nem perfis de regras; divergências exigem cadeia causal e autorização aplicável.
2. Missão gerada apresenta pré-requisitos, etapas, condições de sucesso/fracasso, proveniência, dependências e estratégia de retomada; o formato final depende da SPEC.
3. Propostas com recursos desconhecidos/ausentes ou scripts não allowlisted são rejeitadas antes de tentar alterar o jogo.
4. Eventos mecânicos só são consolidados após receipt do host; reenvio de proposta não duplica NPC, item, spawn nem recompensa.
5. Mesmo seed e versões geram a mesma **proposta procedural determinística** onde se usa RNG; texto livre de LLM pode variar, mas não altera unilateralmente resultados mecânicos.
6. A instalação Original não recebe conteúdos do Living World, e duas campanhas não compartilham estado secreto ou eventos.
7. Saves restauram referências e versões de missões em andamento; ausência de pacotes obriga migração validada ou bloqueio claro, jamais substituição silenciosa.
8. Conteúdo antecipadamente criado passa por validação de áreas, entradas/saídas, navegação, encontros, diálogos, saves e multiplayer em build isolada.
9. Rejeições de conteúdo e falhas geram diagnóstico rastreável, com fallback curado quando possível.
10. Custos de IA, densidade e repetição são limitados; eventos distantes não induzem simulação mecânica sem host.

## Consequências

**Prós:** alta reutilização dos recursos originais, expansão controlada, diversidade sem LLM constante, maior explicabilidade e integração mais progressiva.

**Contras:** requer curadoria/validação, templates e pipeline de build para áreas; geração altamente dinâmica em runtime pode continuar inviável no motor; teste combinatório de mods e eventos será significativo.

## Questões deliberadamente abertas

- **DEC-027 — política de publicação de conteúdo procedural (próxima):** quais classes de mudança são autorizadas automaticamente e quais dependem de validação/aprovação de anfitrião? A aprovação da arquitetura híbrida **não define esse limiar**.
- **DEC-012/017:** allowlists, sandbox, controles e licenças/uso dos recursos.
- Contratos e formatos reais para missões, dados, assets, migrations e UX.
- Disponibilidade de ferramentas/hook para compilar/importar novas áreas em BG2:EE e sincronizá-las entre clientes.
- Quantidade, critérios de qualidade, frequência, persistência e nível de criatividade permitidos para a geração procedural.

**Aprovação de arquitetura não equivale a feature implementada.** Sem POC e integração em BG2:EE, o sistema permanece um desenho a especificar.
