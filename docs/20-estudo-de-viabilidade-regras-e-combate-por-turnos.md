# Estudo técnico — DEC-005: edição de D&D, motor e combate por turnos

**Infinity AI | Discovery v1.8 | 2026-11-06 | Estado: PESQUISA / NÃO APROVADO**

## Perguntas da investigação

1. Qual opção exige menos modificação: converter NWN (motor 3D, D&D 3e) para AD&D 2e, ou BG2:EE (2D, AD&D 2e) para D&D 3e/5e?
2. Quais vantagens das regras modernas são realmente importantes para jogadores do Living World?
3. Quanto custa converter combate RTwP de BG2:EE em turnos individuais com multiplayer?

## Fatos técnicos verificados

- BG2:EE usa regras adaptadas de AD&D 2e, gráficos isométricos e combate em tempo real com pausa; existe multiplayer oficial. Fonte: https://www.baldursgateii.com/index.html
- NWN original utiliza D&D 3e com decisões em tempo real e rounds do sistema; seu motor e seus recursos não são intercambiáveis automaticamente com a Infinity Engine. Referência: https://gamefaqs.gamespot.com/pc/188666-neverwinter-nights/faqs/51550
- IWD2 utilizou D&D 3e na Infinity Engine modificada; designers relataram mudanças extensas em bônus, itens, magias, talentos, perícias e interfaces. Fontes: https://www.gamebanshee.com/interviews/28279-icewind-daleicewind-dale-ii-interview-v15-28279/page-2.html e https://www.gamebanshee.com/interviews/28277-icewind-daleicewind-dale-ii-interview/all-pages.html
- BG3 utiliza D&D 5e e turnos. Fonte: https://baldursgate3.game/about
- GemRB-TBC é fork experimental de GemRB com modo de turnos individuais, iniciativa, deslocamento, ações e ataques de oportunidade preservando regras AD&D 2e: https://github.com/Dreamkins/gemrb-TBC e https://www.moddb.com/mods/gemrb-tbc
- GemRB não possui multiplayer, BG2:EE permanece com suporte experimental e mods Lua/EEex não funcionam no GemRB como no executável original. Fonte: https://gemrb.org/Features.html
- BG2:EE oferece pausa automática, inclusive no fim de round, mas isso NÃO equivale a iniciativa global/turnos exclusivos nem a um modo completo de BG3. Fontes: https://manualzz.com/doc/34390354/bioware-baldur-s-gate-ii-enhanced-edition-video-game-user... e https://baldursgate.fandom.com/wiki/Baldur.lua
- EEex permite ampliar mecânicas hardcoded de BG2:EE, mas a existência do extender não comprova um modo turn-based pronto, especialmente no multiplayer. Fonte: https://github.com/Bubb13/EEex

## Matriz de complexidade relativa (hipóteses de engenharia; sem medição)

| Estratégia | Edição | Combate | Complexidade relativa | Adequação a BG2:EE/EET/multiplayer |
|---|---|---|---|---|
| 1. BG2:EE sem conversão | AD&D 2e | RTwP | Baixa | Melhor preservação inicial |
| 2. BG2:EE com diretor adaptativo, sem modificar núcleo | AD&D 2e | RTwP | Baixa–média | Boa; validar bridge e host |
| 3. BG2:EE com melhorias de regras isoladas | 2e com adaptações pontuais | RTwP | Média | Viável sob teste de compatibilidade |
| 4. BG2:EE com pausa automática reforçada | 2e | Pseudo-turnos | Baixa–média | UX mais tática; não são turnos reais |
| 5. BG2:EE com turnos verdadeiros | 2e | Turnos reais | Alta/muito alta | Temporizadores, IA, magia e sincronização exigem mudanças |
| 6. BG2:EE inteiramente convertido | D&D 3e | RTwP ou turnos | Muito alta | IWD2 comprova possibilidade, não portabilidade do código |
| 7. BG2:EE inteiramente convertido | D&D 5e | Turnos | Muito alta | Quase reimplementação do sistema completo |
| 8. NWN 3e convertido a AD&D 2e | AD&D 2e | RTwP/turnos | Muito alta | Além de regras, exige adaptar arte/conteúdo 2D a 3D |
| 9. GemRB-TBC | AD&D 2e | Turnos reais | Média para protótipo isolado; alta/muito alta para meta multiplayer+mods | Sem multiplayer e sem equivalência EEex/EET comprovada |
| 10. IWD2 como motor | D&D 3e | RTwP | Baixa para regras IWD2, alta para mundo EET | Não pode assumir que módulos EET rodem no executável IWD2 |

## Distinção essencial de escopo

- **Edição das regras:** THAC0/CA, BAB, talentos, perícias, habilidades, saves, progressão, magias, economia das ações, CR. Um sistema moderno pode ser desejável, mas trocar edição altera grandes quantidades de dados.
- **Orquestração do combate:** ordem de iniciativa, alternância exclusiva, filas de comandos, movimento por turno, ataques extras, interrupções, duração de efeitos e sincronismo. Pode ser implementada em cima de 2e, sem conversão total.
- **Apresentação gráfica:** a estética isométrica clássica é independente da edição das regras. Usar conteúdos de NWNForBG não implica executar D&D 3e.

## Três níveis de intervenção para combate

**Nível 0 — RTwP original (baseline):** nenhum desenvolvimento de turno; o jogo funciona como referência de regressão.

**Nível 1 — Pausa automática e UX tática (teste barato):** testar auto-pause no início/fim de eventos, ao fim de round, fila de ordens do jogador, funcionamento da pausa no host/cooperativo. Não anunciar como verdadeiro turn-based.

**Nível 2 — Turnos individuais reais (POC experimental):** exige scheduler de iniciativas, autorização host de vez, comando de encerrar turno, bloqueio de ação fora da vez, gerenciamento de timers, consumos e animações; validar que todos clientes vejam a mesma ordem de combate. Reavaliar se EEex oferece hooks suficientes. O fork GemRB-TBC serve como referência de conceitos/código para motor aberto, não como plugin direto de BG2:EE.

## Bloqueadores e riscos para turnos verdadeiros no BG2:EE

1. **Duração de efeitos e rounds:** manter semântica de 6 segundos, cast time, haste/slow, regeneration, efeitos de área, poison/disease, summons e cooldowns.
2. **Interrupções:** ataques de oportunidade, contra-ataques e efeitos que reagem no turno de outro combatente exigem regras explícitas.
3. **Fila de ação e IA:** impedir que personagens sob scripts continuem executando ações quando não é a vez; não convocar LLM para ataques normais (DEC-014).
4. **Cenários vivos:** separação clara entre tempo de exploração e tempo de combate, inclusive NPcs neutros e chegada tardia de combatentes.
5. **Multiplayer e estado:** iniciativa e mudança de turno calculadas no host; jogadores não podem executar ações fora da vez; perda de conexão, duas ordens simultâneas e save/load sem divergência (DEC-001/011).
6. **Mods e conteúdo:** verificar scripts BG2, EET, IWD1/2 e NWNForBG que dependem de temporização em tempo real; não assumir compatibilidade.
7. **Edição das regras:** converter 2e→3e/5e além de mudar combates implica inventário de TODAS as classes, feats, saves, listas de magias, itens, efeitos, CRE e balanceamento; não é consequência automática da adoção de turnos.

## Plano de prova de conceito (antes de decidir implementação de turnos)

- **POC-R01:** BG2:EE limpo com opções de auto-pause em combate singleplayer; comparar logs de dano, round e cast.
- **POC-R02:** Repetir com dois clientes multiplayer no host, observar quais pausas são locais/sincronizadas, bloquear ações sem confirmação.
- **POC-R03:** EEex/bridge lê estado de combate/round com segurança, sem alterar jogo; identificar hooks disponíveis e versões.
- **POC-R04:** Protótipo isolado GemRB-TBC sem assumir multiplayer; observar iniciativa, movimento, efeitos e edge cases.
- **POC-R05:** Caso os hooks do BG2:EE permitam, experimentar gate de turno em área isolada e saves descartáveis; não aplicar a EET no primeiro teste.
- **POC-R06:** Testes de progressão com duas criaturas, spells de duração, Haste, múltiplos ataques, explosões, NPC neutro, desconexão e save/load.

## Recomendação de trabalho (ainda não aprovada)

Preservar **BG2:EE + AD&D 2e** como baseline da DEC-003; implantar **Encounter Director determinístico** (sem conversão de edição), e avaliar turnos como **feature separada opcional**, inicialmente via auto-pause e POC. Se a escolha de design for verdadeiro turn-based multiplayer obrigatório, reavaliar o motor antes de prometer a feature e comparar custo de implementar multiplayer em GemRB-TBC versus scheduler no BG2:EE.

A eventual preferência por D&D 5e fica como hipótese de experiência do jogador e requer pesquisa de regras, inventário e custo específico. O suporte à versão atual de D&D também deve ser explicitamente decidido (não considerar 3e e 5e equivalentes).

## Status de decisão

**DEC-005: EM ANÁLISE; nenhuma das opções A/B/C anteriores foi aprovada.** Sugerido desdobrar em **DEC-005-R** (edição das regras), **DEC-005-T** (combate RTwP / pausa reforçada / turnos reais) e **DEC-005-E** (encontros adaptativos e CR). Nada disso altera as ADRs aprovadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Mudanças de plano que afetem histórico pessoal ou segredos exigem consentimento e autorização específica; não criar retcon por cancelamento.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Alterações editoriais/versionadas preservam fronteira entre fatos observados do motor e interpretações narrativas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**
