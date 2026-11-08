# ADR-0041 — Delegação temporária por categorias, consentimento prévio e limites de autoridade

- **Decisão de produto:** DEC-046 — extensão da autoridade do jogador substituto sobre um personagem de jogador ausente.
- **Escolha:** **C — permissões configuráveis antecipadamente por categoria pelo titular**, dentro das políticas da campanha.
- **Estado:** **APROVADA**, pelo idealizador, em 2026-11-06.
- **Versão:** Infinity AI Discovery **v4.2**.
- **Fase:** SDD/Discovery — direção arquitetural, **não uma SPEC implementada ou uma garantia de interceptação de comandos BG2:EE**.
- **Dependências:** DEC-003, 004, 008, 011, 012, 014, 019, 020, 027, 028, 034–046; ADR-0040 e `docs/45-multiplos-personagens-por-jogador-e-delegacao-em-ausencias.md`.

## Contexto

A DEC-045 aprovou o modelo de **muitos personagens por controlador humano**. BG2:EE já documenta atribuição de slots por **Character Arbitration**, inclusive mais de um PC por participante. A atribuição mecânica de slot, entretanto, não resolve quem pode dialogar em nome do personagem ausente, gastar seus itens, expor seus segredos, aceitar pactos, desencadear PvP, sacrificar sua vida ou autorizar eventos de risco HIGH. A DEC-041 distingue autoridade do jogador e acontecimentos do mundo; a DEC-042 exige política para PvP; a DEC-043 define mortalidade; a DEC-028 protege segredos. O controle mecânico é distinto de autorização narrativa, consentimento do titular e da capacidade técnica de bloqueio.

## Decisão vinculante

1. **Autorização anterior à ausência:** cada titular configura, de modo autenticado, versionado e limitado à sua campanha/PC, quais categorias de ações poderão ser praticadas por um substituto ou por uma lista autorizada de substitutos. **Ausência, silêncio e mera reatribuição do slot nunca significam consentimento ilimitado.**
2. **Política de múltiplos níveis:** a ação só pode prosseguir se permitida por **política global da campanha**, **delegação vigente do titular**, políticas de **risco/PvP/morte/cânone**, condições do **estado mecânico**, e se o controlador efetivo estiver autorizado. O host administra atribuições e regras globais, mas não cria, unilateralmente, consentimento pessoal do titular onde ele é obrigatório.
3. **Categorias independentes e configuráveis:** (a) movimento/exploração; (b) combate e habilidades; (c) consumíveis rotineiros; (d) equipamentos, ouro, inventário e itens únicos; (e) diálogos corriqueiros; (f) decisões em missões coletivas; (g) missões, pactos, votos, religião, alinhamento e escolhas **pessoais**; (h) divulgação/uso de segredos; (i) PvP e coerção; (j) morte permanente, sacrifício, transferência de titularidade e alteração de fatos centrais do cânone. As categorias de elevado impacto **não podem herdar autorização de categorias operacionais**.
4. **Padrão seguro candidato:** em ausência de política explícita, nenhuma ação pessoal/privada/HIGH é delegada. Uma configuração preliminar de exploração/combate rotineiro pode ser oferecida, **desde que seja ativada pelo titular e os riscos de combate sejam informados**; a fórmula final e os defaults de interface serão especificados mais tarde.
5. **Combate não é invulnerabilidade:** um substituto autorizado a lutar poderá expor o PC aos riscos normais permitidos pela campanha, incluindo derrota ou morte. **Autorização para combate não equivale a consentimento para um sacrifício deliberado, PvP fatal ou alteração de política de mortalidade.** O motor pode produzir consequências não planejadas; não prometer restauração seletiva/rollback sem POC.
6. **Ações de alto impacto:** atos `HIGH`, alterações do cânone, morte permanente por PvP, mudanças profundas de classe/juramento e decisões históricas centrais seguem **as autorizações especiais respectivas**, ainda que o titular tenha marcado uma categoria genérica como permitida. Algumas decisões poderão ser **não delegáveis** pela política da campanha.
7. **Decisões pessoais:** a IA e o controlador substituto não inventam vontade, confissão, arrependimento, adesão, paixão, alinhamento ou concordância íntima do titular. Diálogo corriqueiro, se permitido, não autoriza promessas pessoais permanentes. Situações sem autorização deverão ser adiadas, encaminhadas a ponto seguro ou bloqueadas no escopo efetivamente controlável.
8. **Sigilo e conhecimento:** a atribuição de um PC não amplia por si só os privilégios de leitura sobre o histórico secreto do jogador. Filtragem ocorre **antes de recuperar contexto ou chamar LLM**. Informações legitimamente percebidas durante a sessão devem registrar sua proveniência, mas não migram automaticamente para a memória do outro PC que o substituto também controla.
9. **Escopo e prazo:** delegação limitada a `campaign_id`, `pc_id`, `owner_id`, `controller_id` ou lista autorizada, categorias, condições, versão de política, início/fim, `assignment_epoch` e revogação. Reatribuição, retorno do titular e vencimento devem invalidar capacidades antigas; após reconciliação, ações tardias não serão reaplicadas.
10. **Ações observadas no motor:** o gateway somente pode negar **ações que efetivamente mediar**. Uma ação manual permitida pela interface do BG2:EE pode ultrapassar o filtro externo. **Nenhuma política será apresentada como bloqueio mecânico garantido** antes de POC em host e clientes. Se uma ação necessária estiver fora das permissões e não puder ser tecnicamente impedida com segurança, a sessão deve adotar fallback transparente (não delegar naquele momento, pausa, esperar titular, acordo humano e registro) em vez de falsa proteção.
11. **Confirmação e auditoria:** separar `DELEGATION_GRANT`, `CHARACTER_ASSIGNMENT`, `ACTION_PROPOSAL`, `ENGINE_RECEIPT` e `NARRATIVE_EVENT`. Registrar quem controlou, o PC afetado, categoria, política, momento, prova do host e resultado `CONFIRMED`/`REJECTED`/`UNCERTAIN`; eventos incertos exigem reconciliação sem repetição cega.
12. **Mudança de política:** o titular pode revogar ou restringir permissões para o futuro; não apagar eventos anteriores já confirmados. Alterações de permissão durante ação irreversível precisam de transição segura e recibo, não de retroatividade presumida.
13. **Isolamento de modos e campanhas:** o modo Original, saves de outras campanhas e outros PCs não herdam delegações.

## Matriz conceitual inicial (parâmetros exatos ficam para SPECS)

| Categoria | Permissão por titular | Salvaguarda adicional |
|---|---|---|
| Movimento, exploração, habilidades rotineiras | Opt-in por categoria | Slot atribuído e regras do motor |
| Combate regular | Opt-in explícito e aviso de risco | DEC-043, pausa/fallback quando necessário |
| Consumíveis e equipamentos comuns | Opt-in com limites candidatos | Inventário/host; custo e raridade |
| Itens únicos, ouro e transferências permanentes | Categoria própria, autorização reforçada | Action Gateway, trilha de transferência |
| Diálogos e missões coletivas | Opt-in limitado | Não decidir compromissos íntimos ou arcos pessoais |
| Pactos, fé, juramentos, evolução moral | Reserva do titular por padrão | Mesmo opt-in não supera regras de classe/risco |
| Segredos de histórico e edição autoral | Não decorre do controle de slot | ACL DEC-019/028 e autoria DEC-020 |
| PvP, coerção e morte deliberada | Política e consentimento específicos | DEC-042/043 e restrições técnicas validadas |
| Divergência central de cânone | Política especial além da delegação | DEC-034/HIGH, autorização histórica |

## Invariantes e incompatibilidades

- `CHARACTER_ASSIGNED != OWNER_CONSENTED_TO_EVERY_ACTION`.
- `CONTROLLER != OWNER`; autorização é temporária, versionada, revogável e específica por categoria.
- `ALLOW_BY_OWNER ∩ ALLOW_BY_CAMPAIGN ∩ ALLOW_BY_RISK ∩ ENGINE_CAPABILITY`; qualquer bloqueio prevalece.
- `NO_GRANT != GRANT_ALL`; `DIALOGUE_PERMISSION != PERSONAL_PACT_PERMISSION`.
- `CAN_READ_CHARACTER_SHEET != CAN_READ_PRIVATE_BACKSTORY`.
- `NARRATIVE_ALLOW != ENGINE_PREVENTION_PROVEN`.
- O mesmo ator humano pode controlar dois PCs, mas seus modelos de conhecimento permanecem separados.
- Nenhum save, saldo, morte ou escolha confirmada será desfeito silenciosamente por uma revogação posterior.

## Evidências e limitações

- **Suporte documental existente:** BG2:EE permite Character Arbitration e permissões multiplayer por jogador; ver [manual Amn Survival Guide, multiplayer, pp. 58–63](https://cdn.steamstatic.com/steam/apps/257350/manuals/BGIIEE_-_Amn_Survival_Guide.pdf).
- **Ainda não comprovado:** permissões por categoria e **por PC**, interceptação preventiva de cliques do usuário, bloqueio de diálogos críticos, segregação do inventário, hooks EEex, controle concorrente, reatribuição em meio ao combate, segurança em reconexão e sincronização com saves/mods.
- **Gates técnicos:** POC host + dois clientes, ações nativas versus gateway, permissão/revogação/época do slot, fallback durante conversa forçada e combate, PvP indireto, itens raros, memória secreta e auditoria save/load.

## Efeitos e próxima pergunta

A DEC-046 fecha o **escopo da delegação provisória** (DEC-045), sem decidir ainda a granularidade exata dos widgets, budgets, duração padrão ou forma de aplicar restrições no motor. Os contratos candidatos e 20 testes constam no documento técnico **46**.

**DEC-047 — ABERTA:** grau de autonomia dos **companheiros NPC recrutáveis**, especialmente os canônicos BG2:EE, que podem ser controlados taticamente por humanos mas possuem identidade, motivações, alianças, relações e escolhas narrativas próprias. Distinguir PC de outro jogador de companion NPC e decidir o equilíbrio entre controle tático e agência narrativa.

**Nenhum recurso foi implementado.**
