# ADR-0043 — Protocolo contextual de desacordo, lealdade, limites e ruptura dos companheiros NPCs

- **Decisão de produto:** DEC-048 — reações a desacordo e possível desligamento de companheiros NPCs no Living World.
- **Escolha:** **B — sistema contextual e gradual de lealdade, limites e ruptura**, com exceções proporcionais para atos excepcionalmente graves.
- **Estado:** **APROVADA** pelo idealizador em 2026-11-06.
- **Versão:** Infinity AI Discovery **v4.4**.
- **Fase:** SDD/Discovery; esta é uma diretriz arquitetural, **não** uma SPEC final, código funcional, demonstração de EEex nem garantia de controle mecânico em multiplayer.
- **Dependências:** DEC-003/004/008/009/011/012/014/019/020/021/022/027/028/029/030/034/035–038/039–043/045/046/047 e AD&D 2e/BG2:EE.
- **Modelo técnico:** `docs/48-protocolo-de-desacordo-lealdade-recusa-e-ruptura-npc.md`.

## Contexto

A DEC-047 aprovou o controle tático humano de companheiros recrutados e a autonomia **narrativa** desses NPCs. A DEC-048 define como suas convicções e relações geram reações coerentes: de dúvidas e pedidos de esclarecimento a advertências, condições de permanência, possível recusa e eventual saída da party. A decisão não pode substituir a personalidade canônica por uma pontuação genérica de aprovação, confundir reputação pública com lealdade individual, nem dar ao LLM acesso livre a scripts ou comandos mecânicos.

## Decisão vinculante

1. **Princípio contextual:** decisões e reações derivam de fatos do mundo confirmados ou crenças recebidas com proveniência, valores e objetivos do NPC, vínculos, momento, severidade, frequência, alternativas e circunstâncias justificadas. O NPC não presume que conhece intenções privadas dos PCs. Rumores são crenças atribuídas, não prova automática.
2. **Progressão geralmente gradual:** discordâncias leves podem gerar desconforto, conversa ou pedidos de esclarecimento; recorrência ou gravidade podem resultar em advertências, condições de permanência, distanciamento, negociação e proposta de ruptura. O estado de uma relação **não é necessariamente linear**: explicações, reparação, novas evidências e histórico alteram a avaliação.
3. **Exceção de gravidade:** atos comprovadamente excepcionais, incompatíveis com um limite central do NPC, podem motivar **ruptura imediata** sem sequência obrigatória de avisos. A exceção exige critérios versionados, evidência contextual e revisão de risco; não é liberdade aleatória da IA. A saída **física** ainda depende de viabilidade e recibo do motor.
4. **Múltiplas dimensões:** confiança, respeito, lealdade, temor, afinidade, conflito moral, obrigações e interesses podem evoluir independentemente; reputação social e alinhamento do personagem são conceitos diferentes, já tratados por DEC-030/035/036. Não reduzir o comportamento inteiro a um escalar universal.
5. **Autonomia sem arbitrariedade:** o NPC pode argumentar, recusar apoio *narrativamente*, procurar alternativas e avaliar permanência; **não** ganha autoridade para reescrever decisões dos PCs, inventar crimes, ocultar inventários ou decidir por um jogador ausente. Diálogos do LLM são propostas, não gatilhos finais de efeitos.
6. **Negociação e agência:** oferecer aos jogadores oportunidades plausíveis de escutar, esclarecer, persuadir, reparar danos ou aceitar a saída. Carisma, persuasão, magia ou reputação não garantem adesão do NPC e não revogam automaticamente seus limites pessoais. Negociações podem falhar, ser adiadas ou criar compromissos verificáveis.
7. **Continuidade do cânone:** políticas dos companheiros clássicos começam dos dados e comportamentos originais do BG2:EE por época, fontes e build; inventariar scripts, diálogos, banters, romances, triggers e saídas existentes. **Não duplicar** nem sobrescrever indiscriminadamente conteúdo nativo. Alterações legítimas de trajetória exigem causalidade, cronologia e proteção do cânone.
8. **Camadas de consequência:** `NPC_DISSENT` / `NPC_REFUSAL_INTENT` / `DEPARTURE_PROPOSAL` são estados e propostas narrativos. `ORDER_BLOCKED` / `PARTY_MEMBER_REMOVED` / `ITEM_TRANSFERRED` são efeitos mecânicos que **somente** existem mediante ação tipada autorizada, compatibilidade comprovada e **recebimento do host**. Sem hook validado, protesto **não é** veto efetivo.
9. **Saída em condição segura:** avaliar combate, transições de área, inventário, localização, diálogos/quest flags, personagens obrigatórios, scripts nativos, compatibilidade coop e regras de campanha antes de solicitar a remoção. Se a ação não puder ser executada, manter estado narrativo pendente e adotar fallback seguro, nunca falsificar a saída nem editar saves cegamente.
10. **Prevenção de duplicações:** cada acontecimento/aviso/proposta e recibo possuem IDs e versões; save/load, reconexão, catch-up e múltiplos clientes não podem executar a mesma saída duas vezes. Estado `UNCERTAIN` deve ser reconciliado antes de repetir uma ação, nunca por retry cego.
11. **Frequência e custo:** avaliação de condições por regras determinísticas e eventos significativos, com cadência apropriada aos estados ACTIVE/NEAR/DISTANT/DORMANT e relógio da campanha; IA local somente sob demanda para diálogo aberto. Evitar processamento por tick/por NPC.
12. **Proteções transversais:** fatos, crenças e segredos são filtrados antes de modelos (DEC-028/029); respeitar host/gateway, PvP, morte, autorizações HIGH, agência dos PCs e isolamento absoluto do modo Original. Não prometer recusa preventiva nem saída segura antes de POC BG2:EE/EEex multiplayer.

## Razões da escolha

- **Versus A (gatilhos fixos):** permite contexto, histórico, explicação, correção de fatos e limites individuais sem simples `desaprovação >= X` universal.
- **Versus C (IA autônoma):** reduz inconsistência, violações do cânone, latência e mutações mecânicas não auditáveis.
- **Vantagem da B:** mantém consequências duradouras, aceitando que atos extremos justifiquem ruptura rápida, mas torna cada transição explicável e reproduzível.

## Invariantes

- `FACT != BELIEF != RUMOR`; um NPC só reage a visão legitimamente obtida.
- `RELATIONSHIP ≠ ALIGNMENT ≠ REPUTATION`; sobreposição de sinais não implica equivalência.
- `PROTEST != MECHANICAL_VETO`; `INTENTION_TO_LEAVE != CONFIRMED_PARTY_EXIT`.
- `NO_ENGINE_RECEIPT => NO_CONFIRMED_MECHANICAL_MUTATION`.
- `OWNER(PC) != TACTICAL_CONTROLLER(NPC) != NARRATIVE_IDENTITY(NPC)`.
- `CRITICAL_EVENT` pode abreviar avisos, **não** os gates técnicos nem de risco.
- Estado anterior confirmado jamais será apagado por negociação ou eventual retorno posterior.

## Não decidido nesta ADR

- Valores numéricos, pesos, limiares, tabelas de afinidade, duração, interfaces, gêneros de fala, fórmulas de persuasão ou lista completa de reações por NPC.
- Operações específicas de EEex/Lua, ganchos de comandos, scripts de party, saídas de combate e testes concluídos: continuam em aberto.
- **DEC-049:** destino dos companheiros depois de deixarem a party e condições de reencontro/recrutamento futuro.

## Provas/gates posteriores

1. Inventário de NPCs nativos e mods e dos fluxos originais de desentendimento, romances, abandono e flags por build.
2. Observação read-only: logs de eventos, conhecimento, reações e estados, sem efeito na engine.
3. Diálogos em modo seguro e testes de causas, exceções, repetição, sigilo e multiplayer.
4. Integração isolada do gateway/host para saída/recrutamento **somente se** a build suportar, com rollback/recuperação testada ou fallback documental.
5. Regressões em saves, reconexão, 2 clientes, protagonistas e mods EET/IWD/NWNForBG, mantendo Original separado.

**Nenhuma funcionalidade de abandono/recusa foi implementada por esta decisão.**
