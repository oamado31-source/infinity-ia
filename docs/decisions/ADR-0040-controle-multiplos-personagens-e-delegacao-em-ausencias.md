# ADR-0040 — Controle de múltiplos personagens por jogador e redistribuição temporária em ausências

- **Decisão:** DEC-045 — política de ausência, desconexão e retorno em multiplayer Living World.
- **Status:** **APROVADA — proposta do usuário: modelo de atribuição de personagens semelhante a Baldur’s Gate 3**; substitui as alternativas A/B/C apresentadas anteriormente para DEC-045.
- **Aprovação:** 2026-11-06, escolha expressa do idealizador do Infinity AI.
- **Fase:** Discovery / SDD; **não** é uma SPEC nem implementação testada.
- **Versão:** Infinity AI Discovery v4.1.
- **Dependências:** DEC-001/003/004/011/012/019/020/022/028/040/041/042/043/044; ADR-0035–0039 e documento `45-multiplos-personagens-por-jogador-e-delegacao-em-ausencias.md`.

## Contexto e motivação

No Living World, o grupo pode continuar a aventura mesmo quando um jogador estiver ausente. A proposta do usuário adota o mecanismo conhecido de Baldur's Gate 3: os PCs do participante ausente permanecem no grupo e podem ser **atribuídos a outro jogador humano presente**, que passa a controlar temporariamente mais de um personagem. A IA não precisa ocupar o lugar do jogador ausente para operar seus personagens.

**Verificação documental relevante:** o manual oficial de **Baldur's Gate II: Enhanced Edition**, *Amn Survival Guide*, seção Multiplayer / Character Arbitration (pp. 58–63), já documenta que o líder pode atribuir slots a participantes e que um participante pode controlar um ou mais personagens; define também permissões, primeiro slot do protagonista e game-over na morte do protagonista. Assim, há **suporte documentado para redistribuição manual de controle**, mas não se comprovou nesta fase uma operação programática via EEex, redistribuição automática sem abrir a tela, reconexão sem interrupção, consentimento técnico granular ou proteção efetiva contra decisões/ações indevidas. A confirmação depende de POC com host e dois clientes na build fixada.

Fontes: [manual oficial BG2:EE, PDF](https://cdn.steamstatic.com/steam/apps/257350/manuals/BGIIEE_-_Amn_Survival_Guide.pdf) e [guia de atribuição de personagens em BG3](https://www.shacknews.com/article/136509/co-op-baldurs-gate-3). Estas referências fundamentam as características do mecanismo, não garantem integração por código entre motores distintos.

## Decisão vinculante

1. **Modelo muitos-para-um:** uma pessoa conectada pode exercer o controle mecânico de **mais de um PC** dentro dos slots e limites reais da party BG2:EE, seja inicialmente, seja após redistribuição.
2. **Ausência ≠ retirada:** quando o jogador titular desconecta ou não participa da sessão, o PC não é removido, aposentado, morto, duplicado nem transformado em NPC automaticamente. Pode continuar presente e ser atribuído a outro participante presente.
3. **Atribuição por sessão:** o anfitrião/líder administra as atribuições na tela de **Character Arbitration**, ou por integração futura **somente se testada**. A regra de campanha determina quem pode ser designado como substituto. Não confundir atribuição de slot com transferência permanente de identidade ou propriedade do PC.
4. **Controle humano substituto:** o jogador presente designado emite comandos de exploração, combate e operações efetivamente permitidas pelas regras; **a IA não assume controle automático** do personagem ausente e não inventa ações ou falas dele.
5. **Titularidade distinta do controle da sessão:** manter IDs de `PLAYER_OWNER`, `SESSION_CONTROLLER`, `PC` e `ENGINE_SLOT` separadamente. A conta controladora temporária não herda o histórico autoral, segredos fora da percepção de seu próprio PC, consentimentos, nem o direito de editar o personagem alheio.
6. **Agência e autorização:** a DEC-041 continua válida para escolhas/intenções pessoais e DEC-042 para PvP. **A amplitude de poderes do substituto** (decisões pessoais, falas, missões privadas, gastos irreversíveis, inventário individual, risco de morte, diálogos e compromissos) requer política explícita e será detalhada pela **DEC-046**. Controlar a ficha no motor **não constitui, por si, consentimento ilimitado** do jogador ausente.
7. **Segurança e riscos reais:** se o personagem substituído combater, poderá sofrer consequências mecânicas inclusive graves sob a política DEC-043. Não prometer invulnerabilidade ou rollback seletivo sem capacidade validada. Se uma operação de alto risco estiver fora da permissão definida, o sistema deve negar sua automação ou recomendar pausa/ponto seguro; uma proteção preventiva só poderá ser anunciada após POC dos hooks.
8. **Persistência e autoria:** ações mecânicas confirmadas são atribuídas ao **PC que agiu**, registrando também o controlador efetivo da sessão e seu intervalo de atribuição; memória e alinhamento de cada PC não se misturam. A narrativa não atribui automaticamente intenção privada do titular ausente ao substituto.
9. **Retorno:** quando o titular se reconectar, o host/líder poderá **devolver o controle** do mesmo PC, conciliando estado mecânico, versão da campanha, atribuição e acontecimentos ocorridos durante a ausência. O retorno não cria uma ficha nova nem restaura indevidamente um estado anterior.
10. **Resolução de conflitos de controle:** um slot não pode ter dois controladores simultâneos. Atribuições e devoluções precisam ter versão/epoch, recibo do host quando existir integração, e estado de reconciliação `UNCERTAIN` para falhas, não replay cego.
11. **Protagonista e regras nativas:** o primeiro slot é protagonista segundo manual; a redistribuição **não altera o protagonista**, não contorna *game-over*, limites de seis personagens, regras de diálogo ou as permissões efetivas do motor.
12. **Disponibilidade diferente de confirmação:** BG2:EE documenta a função manual de atribuir slots; **não** há prova de controles programáticos em tempo real, interceptação PvP, UI de consentimento granular ou segurança de transferência no meio de combate com mods e EEex. Estas alegações ficam proibidas até testes.
13. **Isolamento:** estas políticas são do Living World, não reescrevem as regras nem os saves do modo Original. Campanhas distintas não compartilham permissões, ownership nem memória.

## Invariantes

- `PC_ID != PLAYER_ID != SESSION_CONTROLLER_ID != ENGINE_SLOT_ID`.
- `REASSIGN_CONTROL != TRANSFER_OWNERSHIP != INHERIT_KNOWLEDGE`.
- `ABSENT_PLAYER != DEAD_CHARACTER != RETIRED_CHARACTER`.
- `CONTROL_COMMAND_CONFIRMED != PERSONAL_INTENT_AUTHORIZED`.
- O motor pode aceitar um comando mesmo se uma política externa o vetar; isso é um risco técnico, não uma garantia de bloqueio.
- A entrega de controle deve ser reversível no registro de **atribuição**, mas acontecimentos já confirmados durante a ausência não podem ser apagados silenciosamente.

## Limites e verificação

- **Documentado:** um participante pode controlar mais de um personagem e o líder pode reatribuir slots por Character Arbitration (manual BG2:EE, pp. 58–63).
- **Não provado localmente:** comportamento exato da instalação/versão do projeto; troca no meio de combate; reconexão automática; retorno do controlador original sem reabrir menus; persistência após load; restrição de escolhas por personagem, capacidade de filtragem de segredos e EEex/bridge.
- **POCs necessárias:** host + dois clientes; ausência planejada; queda abrupta durante combate; reassociação de slot; retorno; protagonista; inventário; diálogo; saves/load; limites de permissões nativas; transações duplicadas; divergência entre clients.

## Consequências e próximas decisões

- **Benefício:** continuidade cooperativa com a equipe existente, aproveitando um recurso **documentado** do próprio motor, sem depender do LLM para controlar o PC ausente.
- **Custo:** a redistribuição mecânica é distinta da autorização narrativa e da segurança em situações críticas. O mecanismo nativo por si só não resolve escopo e consentimento.
- **DEC-046 (ABERTA):** qual é o alcance da autoridade concedida ao controlador temporário de um PC de jogador ausente? Opções candidatas: controle pleno, só tático/operacional, ou política granular por categoria e autorização antecipada do titular.

**Nenhum software foi escrito; este ADR confirma apenas uma direção arquitetural e referências documentais.**
