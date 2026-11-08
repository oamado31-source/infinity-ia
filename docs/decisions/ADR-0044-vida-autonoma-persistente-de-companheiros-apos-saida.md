# ADR-0044 — Vida autônoma persistente de companheiros NPC após a saída da party

- **Decisão:** DEC-049 — destino dos companheiros NPC que abandonaram o grupo.
- **Escolha expressa:** **B — NPC continua vivendo autonomamente no mundo**, de modo persistente, com atividades proporcionais à relevância e possibilidade de reencontros e recrutamento futuro.
- **Estado:** **APROVADA** pelo idealizador em 2026-11-06.
- **Versão:** Infinity AI Discovery **v4.5**.
- **Fase:** SDD/Discovery; arquitetura aprovada, não SPEC, código ou funcionalidade comprovada em BG2:EE/EEex multiplayer.
- **Dependências:** DEC-003/004/008/009/010/011/012/014/021/022/023/024/025/027/028/029/030/031/032/034/039/040/041/043/047/048.
- **Desenho:** `docs/49-vida-autonoma-reencontros-e-recrutamento-de-companheiros-npc.md`.

## Contexto

A DEC-047 preserva o controle tático de NPCs recrutados, com autonomia narrativa; a DEC-048 permite desacordo, negociação e ruptura. A DEC-049 determina que, **após saída realmente confirmada**, o companheiro não seja eliminado da realidade do Living World nem se torne uma unidade individual simulada em tempo real em qualquer distância. Deve ter continuidade de trajetória, limitações de recursos, vínculos e possibilidades de reencontro ou eventual retorno ao grupo, integrados à cronologia e ao ecossistema das facções.

## Decisão vinculante

1. **Persistência de identidade:** cada NPC mantém identidade estável, origem, personalidade, histórico confirmado, relações, conhecimento permitido, motivações, compromissos, posição/área conhecida e afiliações válidas. Sair da party não destrói registros, nem transfere automaticamente inventário, propriedades, segredos, poderes ou conhecimento.
2. **Saída comprovada como pré-condição:** `DEPARTURE_PROPOSAL` / `INTENT_TO_LEAVE` ≠ `PARTY_MEMBER_REMOVED`. Somente após recibo/observação autoritativa do host, verificada a compatibilidade, o NPC ingressa no regime pós-party. Se houver `UNCERTAIN`, reter transição pendente, sem spawn ou exclusão duplicados.
3. **Vida autônoma por objetivos e recursos:** simular agendas e possibilidades coerentes (viagens, trabalho, relações, compromissos, encontros, participação em facções e histórias próprias), segundo regras determinísticas e estado do mundo. Propostas não são automaticamente fatos históricos.
4. **Escala hierárquica:** aplicar `ACTIVE`, `NEAR`, `DISTANT` e `DORMANT` (DEC-021), com atividade e custos proporcionais à proximidade/relevância. NPC distante pode ser representado por resumo de trajetória, agenda, estado e checkpoints; **sem LLM por tick** e sem manter entidade física continuamente ativa.
5. **Tempo autorizado:** avanço e catch-up conforme relógio configurado (DEC-022), com limites de processamento, seeds e versões de regras para reconstrução auditável. Períodos de congelamento não permitem deslocamento/evolução silenciosos.
6. **Cânone e roteiro original:** companheiros canônicos devem respeitar período, contexto, arcos, relações, scripts/quest flags, banters, romances e eventos dos jogos e mods presentes. Divergências só com causalidade confirmada e política de eventos críticos (DEC-009/034); **não presumir que um NPC canon deixa de existir ou muda de alinhamento por hipótese de IA**.
7. **Viabilidade geográfica:** jornadas requerem rotas e tempo plausíveis, limites regionais e recursos. Simular intenção de viajar não confirma presença em área; sem transição/mapa/hook testado, usar projeção narrativa pendente ou resumo, sem alegar teleportação física.
8. **Reencontro contextual:** surgirá somente em locais, datas e circunstâncias compatíveis; deve haver validação do recurso/área/personagem e controle de duplicação. Rumores sobre destino não equivalem a localização confirmada. Efeitos mecânicos dependem de gateway e recibo do host.
9. **Recrutamento não automático:** eventual convite pode ser considerado conforme vontade do NPC, história da ruptura, deveres atuais, obrigações, classe/alinhamento, party slots e condições do jogo. O jogador não tem direito automático ao retorno; uma promessa textual de retorno não prova `PARTY_MEMBER_JOINED`.
10. **Relações e percepção persistentes:** NPC lembra relações efetivamente construídas, mas não é onisciente. Fontes de conhecimento e rumor são controladas por DEC-028/029/030; mudanças de facção não concedem conhecimento implícito de segredos de PCs.
11. **Conflitos e perigo:** decisões de morte, captura, mudança histórica, guerra, retirada permanente de conteúdo ou outras consequências irreversíveis continuam sob classificação de risco e aprovação especial; evolução offscreen não deve criar fatos mecânicos que o host não confirmou.
12. **Reconciliação e isolamento:** snapshot + event log com `npc_id`, `campaign_id`, revisões, fonte e estado autoritativo. Evitar NPC em dois lugares ou simultaneamente recrutado e viajando. Saves, reconexão e Original vs Living World isolados.
13. **IA sob demanda:** regras escolhem elegibilidade e consequências, LLM local apenas ajuda a redigir diálogos e conteúdo aberto filtrado; não cria comandos livres, não controla diretamente o motor e não reescreve o passado.

## Razões e trade-offs

- **Versus A:** permanência apenas no script local original limita o propósito de Living World e a consequência duradoura das rupturas.
- **Versus C:** detalhamento individual integral de todo ex-companheiro, a cada tick e distância, conflita com escalabilidade e custo; não é necessário para efeitos percebidos pelos jogadores.
- **B preserva:** trajetórias próprias persistentes e verificáveis, encontros plausíveis e progressão coerente, com processamento escalonado e compatibilidade gradual.

## Invariantes

- `DEPARTURE_INTENT != CONFIRMED_DEPARTURE`.
- `OFFSCREEN_PROJECTION != ENGINE_POSITION`.
- `RUMORED_LOCATION != CONFIRMED_LOCATION`.
- `REUNION_PROPOSAL != ENGINE_SPAWN` e `RECRUITMENT_OFFER != PARTY_MEMBER_JOINED`.
- `EVENT_UNCERTAIN => RECONCILE_BEFORE_RETRY`.
- `CANON_NPC_BASELINE + CONFIRMED_CAMPAIGN_DELTA`, não retcon silencioso.
- `ORIGINAL_MODE_STATE` isolado de `LIVING_WORLD_STATE`.
- Nenhum ato `HIGH` autoautorizado por agenda offscreen.

## Não decidido aqui

- Fórmulas, cadências, número de NPCs, subsistemas de viagem, preço, rota, tabelas de risco e quotas de LLM.
- Interfaces de busca/rumores, garantias de reencontro, direitos do NPC sobre equipamentos, condições finas de re-recrutamento, técnicas reais de spawn/removal, integração com scripts de banters/romances e multiplayer.
- **DEC-050:** política de conciliação entre scripts/quests/romances canônicos do motor e eventos dinâmicos do Infinity AI para companheiros.

## Gates técnicos e provas exigidas

1. Inventariar scripts nativos e mods de companheiros após dismissal, localização, re-recrutamento e possíveis alterações de `GLOBAL`/party-state.
2. POC read-only com saída/reentrada manual em BG2:EE e testes de 2 clientes, save/load e protagonist/game-over.
3. Persistência e lotes determinísticos em simulação externa (sem efeitos de engine), incluindo cronologia, memória e idempotência.
4. Reencontro em área e (re)recrutamento somente após demonstração de hooks, conteúdo existente e confirmação do host; fallback seguro onde não for possível.
5. Regressão em EET, IWD e NWNForBG após baseline puro, preservando modo Original e saves.

**Não há qualquer implementação funcional de autonomia pós-party, spawn ou re-recrutamento nesta aprovação.**

## Resolução posterior da pendência DEC-050 (Discovery v4.6)

A opção C da DEC-050 foi aprovada no ADR-0045. O NPC com vida externa tem suas propostas de viagem, reaparição e recrutamento conciliadas com scripts, quests, romances e demais compromissos nativos comprovados por build; propostas incompatíveis são adaptadas, adiadas ou bloqueadas. A reserva anterior neste ADR registra o estado da v4.5, não uma pendência atual. Implementação e observabilidade continuam dependentes de SPECS e POCs.
