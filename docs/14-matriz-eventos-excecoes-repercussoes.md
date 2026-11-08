# Matriz de eventos históricos, exceções e repercussões no Living World

**Discovery v1.3 — levantamento inicial.** Datas DR e versões históricas devem ser auditadas por fontes primárias antes de gerar efeitos obrigatórios. Os efeitos abaixo são **regras de design propostas**, não afirmações de que o canon determina exatamente cada rumor/missão/efeito.

## Matriz inicial de cross-check histórico (12 eventos)

| ID | Data DR | Evento/lore de referência | Áreas afetadas e diferença vs jogos | Repercussões propostas por regras/código | Qualidade inicial da fonte |
|---|---|---|---|---|---|
| FR-1281-01 | 1281, ano | Crise em Icewind Dale ligada a Belhifet (IWD1) | Kuldahar, Easthaven e arredores; **passado distante** da data-base 1372 | Memória histórica, ruínas/reconstruções, livros, famílias e vestígios | Média: jogo + compêndios comunitários |
| FR-1312-01 | 1312, ano | Legion of the Chimera e defesa de Targos (IWD2) | Targos/Dez Cidades e locais explorados; 60 anos antes de 1372 | Memória da guerra, linhagens, mudanças de instituições; não recriar inimigos vivos automaticamente | Média: guia do jogo/comunidade |
| FR-1368-01 | 1368, ano | Crise do ferro e acontecimentos de BG1 | Costa da Espada; 4 anos antes de 1372 | Mudança em comércio e facções, depoimentos, rumores históricos | Alta sobre contexto do jogo; canon do resultado varia |
| FR-1368-02 | 1368–1369, intervalo | Siege of Dragonspear | Corredor da Costa da Espada; saga intermediária | Memória militar, sobreviventes, notícias locais | Média: cronologias de fãs; intervalo exige fonte primária |
| FR-1369-01 | 1369, ano | Enredo Shadows of Amn / crise envolvendo Irenicus | Athkatla, Suldanessellar; estado local em 1372 depende de desfecho | Rumores, reconhecimento de personagens, rotas/alianças | Alta para época-base do BG2; final exato não fixo |
| FR-1369-02 | 1369/1370, disputado | Throne of Bhaal e desdobramentos do Bhaalspawn | Tethyr/Amn e personagens da saga | Registrar como `SOURCE_CONFLICT`; consequências dependem da versão escolhida | Disputada — **sem ativação de dia/mês** |
| FR-1371-01 | 1371, ano | Morte de Azoun IV, de Tanalasta e regência de Alusair | **Cormyr**; autoridades do jogo/lore antigo deixam de estar atualizadas | Atualizar cargos, rumores de luto, tensões e ganchos de sucessão | Alta em referências de lore com citações; checar romances |
| FR-1372-01 | **30 Tarsakh 1372**, data secundária | Início da Wailing Death em Neverwinter | Cidade passa por pré-peste → epidemia → consequências | Mudança de serviços e população, rumores, patrulhas, missões relacionadas, disponibilidade de mercados por política | Média-alta em cronologia anotada; confirmar primária |
| FR-1372-02 | 1372, ano | Retorno de Bane (Midwinter em fontes secundárias) | Cultos, facções religiosas e magias/conflitos | Mudanças de diálogos e associações de cultistas | Média-alta em compêndios secundários |
| FR-1372-03 | 1372, ano | Retorno da Cidade de Shade a Faerûn | Anauroch, rotas de notícias e política regional | Rumores e missões de coleta de informação; evitar impacto global imediato | Média; confirmar fontes de cenário |
| FR-1372-04 | **28 Eleasias 1372–28 Ches 1373**, fontes secundárias | Silêncio de Lolth | Underdark e cultos drow, inclusive contextos de HotU | Religião/magia onde mecânica permitir, instabilidade de clérigos e rachas de facção | Média-alta; confirmar data na obra |
| FR-1373-01 | 1373, ano | Rage of Dragons | Regiões afetadas conforme fonte; não evento universal em toda área | Contadores de ameaça, encontros especiais e rumores com limites de região e tempo | Média; evento geral bem documentado |

## Matriz de exceções temporais prioritárias

| Entidade/objeto de revisão | Origem da possível incompatibilidade | Risco para campanha 1372 DR | Resolução recomendada |
|---|---|---|---|
| Azoun IV de Cormyr | Vivo antes de 1371; morto em 1371 | **Crítico** — NPC incorretamente vivo ou ocupando cargo | Registro histórico de morte; NPC não ativo, salvo divergência confirmada; retratos/estátuas possíveis |
| Alusair e Azoun V | Regência posterior à morte de Azoun IV | **Crítico** — governança incorreta | Modelos específicos de facções, autoridades e guardas a partir de 1371 |
| Neverwinter antes/durante Wailing Death | 1372; mudança drástica em curto período | **Crítico** — comércio e vida urbana indiferentes à epidemia | Região com estados históricos por janela; efeitos só na janela validada |
| NPC humano de IWD1 | Origem em 1281, campanha em 1372 | **Alto** — 91 anos sem envelhecimento | Revisão por raça/idade/paradeiro/morte; não preservar automaticamente como NPC vivo |
| NPC de IWD2 | Origem em 1312 | **Alto** — 60 anos de salto | Idade, espécie, sobrevivência, mudança de carreira e família |
| Kuldahar, Targos e outras localidades | Mudanças entre 1281, 1312 e 1372 | **Alto** — cidade congelada no tempo | Manter geometria plausível, atualizar sinais de reconstrução, comerciantes/guardas/população |
| NPCs e antagonistas de BG1/BG2 | Campanhas com escolhas e mortes | **Alto** — duplicação de morto/companheiro ou vilão | Estado de lore escolhido e árvore de ramificação por campanha; nunca supor todos os NPCs vivos |
| Bhaalspawn/quest flags | A trama original presume protagonista específico | **Crítico** — missões autorreferentes indevidas | Living World trata eventos como história, sem assumir que PC atual seja Gorion's Ward |
| NWN original vs SoU/HotU | Campanhas/protagonistas diferentes | **Alto** — falsa continuidade pessoal | Construir linhas narrativas separadas e referenciadas; integrar apenas conteúdo com adaptação comprovada |
| Drow clerics durante Silêncio de Lolth | Janela 1372–1373 | **Alto** — habilidades e diálogos anacrônicos | Regras temporais por facção; qualquer efeito de magia depende de confirmação mecânica |
| Títulos de governo e organizações | Guerras, sucessões, dissoluções | **Médio-alto** | `office_assignment(valid_from, valid_to)` e mudanças por evento |
| Edifícios destruídos/recuperados | Importação visual de décadas anteriores | **Médio-alto** | Variante de região/decoração, ou lore explicativa, nunca ignorar anacronismo identificado |

## Exemplo de repercussão rastreável: morte de Azoun IV (1371)

1. Catálogo recebe evento verificado com `year=1371` e `date_precision=YEAR_ONLY` (sem fabricar dia/mês).
2. Campanha em 1372, sem `CANON_BRANCH` que impeça o resultado, tem a autoridade de Cormyr atualizada pelo motor de regras.
3. NPC com acesso plausível à notícia aprende o fato via `KnowledgeFact`; não é transmitido instantaneamente a todo NPC de Faerûn.
4. Diretor de mundo propõe rumores, disputa política ou escolta/segurança, conforme tabelas/estado da região; gerador narrativo local pode escrever diálogo, mas não decide a troca de governo.
5. Ao reencontrar Suzail, jogadores veem alterações autorizadas em guardas, representantes ou diálogos **se a integração do jogo suportar esses recursos**.
6. Alteração por jogadores no passado (p.ex. salvar Azoun IV) exige evento causal confirmado e criação de um ramo alternativo, com impacto em eventos dependentes e auditoria.

## Exemplo: linha do tempo Neverwinter — 1372

- **Antes do início da epidemia:** NPCs podem mencionar preocupações e rumores plausíveis, mas não narrar mortos de um evento futuro como fato consumado.
- **Durante a epidemia:** serviços/relações/missões e risco de viagem dependem do estado confirmado do cenário e das ações do grupo; não assumir que toda execução do módulo original ocorreu.
- **Após desfecho:** a cidade recebe estado pós-evento condicionado a evidências, data, resultado do módulo e canon escolhido; não presumir desfecho específico quando o jogo permite escolhas.

## Gates de validação (Discovery, ainda não testes executados)

- `GATE-CHRON-01`: evento de fonte sem data exata preserva `YEAR_ONLY`, sem criar dia fictício.
- `GATE-CHRON-02`: 1372 em Cormyr não apresenta Azoun IV como rei vivo sem ramo autorizado.
- `GATE-CHRON-03`: calendário avançando para 1372 não reaplica mudanças 1371 duas vezes.
- `GATE-CHRON-04`: NPCs de IWD1 e IWD2 passam pelo registro de longevidade/identidade antes do spawn.
- `GATE-CHRON-05`: divergência do grupo suspende repercussões oficiais incompatíveis, com motivos legíveis.
- `GATE-CHRON-06`: data de módulo premium NWN não verificada impede repercussão histórica rígida.
- `GATE-CHRON-07`: Open World e Original não compartilham consequências sem ação explícita.
- `GATE-CHRON-08`: informação passada por rumores é filtrada por tempo, geografia e conhecimento do NPC.

## Fontes indiciais a conferir em livros/jogos

- História de Cormyr: https://forgottenrealms.fandom.com/wiki/History_of_Cormyr_(timeline)
- Wailing Death e 1372: https://forgottenrealms.fandom.com/wiki/1372_DR
- Silêncio de Lolth: https://forgottenrealms.fandom.com/wiki/Silence_of_Lolth
- Rage of Dragons: https://forgottenrealms.fandom.com/wiki/1373_DR
- Eventos NWN por campanha: https://nwn.fandom.com/wiki/Original_campaign
- IWD2: https://forgottenrealms.fandom.com/wiki/Icewind_Dale_II

**Atenção:** na fase Discovery, essas são afirmações preliminares baseadas em índices e fontes secundárias (salvo quando manual/documentação original estiver identificada). Não tratar como extração definitiva da cronologia oficial.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: itinerário registrado não confirma combate, morte, bloqueio, romance ou outra repercussão irreversível. Eventos HIGH exigem gates históricos/mecânicos e autorizações; DEC-070 tratará imprevistos.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Vazamento parcial verificado pode disparar proposta de revisão de proteção, mas não ataque automático, mudança global de reputação ou evento histórico irreversível.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Narrativas de agente duplo e tensão só se tornam acontecimentos confirmados após pré-condições, fonte, tempo e riscos. Uma proposta da IA não é evento consumado.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Orquestrador não mantém agente por informante; negociação on-demand com regras determinísticas e filtros de papéis para preservar performance.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Consequências dependem de fatos e causas confirmados: informe não observado não cria evento histórico, encontro ou reação de facção. Contradição pode sustentar investigação sem concluir.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Difusão de dossiê, recibo, retificação e vazamento são eventos distintos com causalidade, ACL e risco; não produzir repercussões globais por arquivar relatório.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Consequências de um plano só entram no event log depois de fatos confirmados; não inferir incidente histórico de proposta baseada em rumor.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Avaliações determinísticas de risco e recursos devem preceder narrativas produzidas pela LLM, com opção de continuar, pausar, cancelar ou propor revisão autorizada.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

A proposta DEC-096 do idealizador converte esta tabela de **pesquisa sujeita a curadoria** em duas camadas: CanonEvent versionado separado de ImpactRule declarativo, com DR/precisão/mês, abrangência, locais afetáveis e efeitos diretos/indiretos. Proibir aplicar as entradas indiciais desta matriz no BG2:EE sem validação de fontes, branch, adapter, autorização e receipts.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

As 12 linhas históricas preliminares DEC-014 não viram automaticamente registros executáveis: precisam fonte, precisão DR, geografia, Knowledge Pack e curadoria da DEC-096/C. Campos de planejamento podem ser exportados para planilha, mas regras ficam em DSL allowlisted e overlay causal.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

As linhas de eventos originais requerem curadoria de family, metric, units, caps e tempo para DEC-097/C; nunca permitir stacking irrestrito.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Repercussões históricas em regiões não conferem permissão para remover ou alterar componentes de quests/mods.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

LLM local recebe apenas SafeQuestProjection mínima, não valores brutos de quest flags, mod scripts ou future branches.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

Rebase de quest DEC-102 não dispara automaticamente evento ou repercussão; admissão causal será DEC-103. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** marcos confirmados de quests originais são **origens candidatas** de regras históricas/regionais, não fatos canônicos escritos em `knowledge/periods/<ANO>-DR/`. A admissão exige prova reconciliada DEC-100/101/102, clock DR e branch adequados; a matriz DEC-096 filtra local, fase e precondições e DEC-097 compõe impactos. Escopo global não dá conhecimento universal. Evento proposto, evento host-confirmed e rumor entregue são distintos; nenhum efeito mecânico sem Action Gateway/receipt. Ver doc. 103. **POCs reais pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para regras de evento não produzem entrega nem mudança de crença automática, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para regras de evento devem gerar proposta, não reparação automática, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Representar pedido, aviso, entrega, percepção, direito de resposta, consentimento, sessão, minuta, aceite por termo e commit como fases diferentes; checks de tempo DR, branch/epochs e idempotência. Ações DISPATCHED/UNCERTAIN reconciliam sem retry cego. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

LLM pode redigir aviso, mas não julgar inadimplência ou pagar recursos. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

A LLM não altera predicado, limiar, compromisso nem recepção de comprovante. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
