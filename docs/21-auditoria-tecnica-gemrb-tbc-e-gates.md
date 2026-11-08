# Auditoria técnica — GemRB-TBC no contexto do Infinity AI

**Discovery v1.9** | 2026-11-06 | **Investigação de código e documentação, não teste de execução**

## Pergunta / conclusão executiva

**A versão GemRB-TBC resolve o requisito de turnos individuais opcionais no RPG cooperativo baseado em BG2:EE + EET?**

- **Resolve como demonstração de código em GemRB**: há um gerenciador C++ de turnos integrado ao fork, interface de iniciativa, ações e movimento; a documentação prevê alternância de modo.
- **Não resolve como instalação direta no projeto**: GemRB é motor reimplementado e não o executável BG2:EE; multiplayer oficial GemRB ausente; extensões EEex e Lua da EE não se transferem automaticamente; EET foi desenvolvido para BG2:EE.
- **Pode reduzir pesquisa de algoritmo, mas não elimina portabilidade nem integração multiplayer**. Portanto, DEC-005-T aprova a *preferência B* condicionalmente; DEC-005-R e DEC-005-E continuam em análise.

## Comparação de capacidade

| Característica | Evidência | Adequação atual |
|---|---|---|
| Alternar RTwP / turnos individuais | README do fork, `ToggleTurnBased()` em gerenciador C++ | **Demonstrado no código; testar em execução** |
| Iniciativa e múltiplas fases de ataque | `InitiativeSlot`, `FirstRoundStart`, `MAX_ATTACK_LISTS=10`, `EndTurn` | **Implementação disponível, ainda sem teste próprio** |
| Ações e movimento | hook em Actor/Actions/Map/GameControl, README | **Requer regressão extensa** |
| Host coop multiplayer GemRB | Documentação oficial GemRB não suporta multiplayer | **Bloqueador** |
| EEex/Remote Console | Ferramentas voltadas ao BG2:EE; GemRB não implementa esses hooks | **Bloqueador para nossa bridge atual** |
| BG2:EE rodando no GemRB | Suporte upstream experimental | **Não é baseline confiável para o projeto** |
| EET e IWD-EET e NWNForBG | EET mira BG2:EE, sem matriz demonstrada no fork | **Desconhecido; testes necessários** |
| Save e restauração em meio aos turnos | Estado do gerenciador contém ponteiros de Actor e estruturas transitórias; diff inspecionado não confirma serialização completa | **Alto risco; verificar** |
| Criação de encontros por regras e IA | Pode ser arquitetada separadamente do combate | **Independente da escolha de motor** |

## Leitura de código — o que foi verificado

Verificação em repositório público `Dreamkins/gemrb-TBC`, branch padrão `TBC`, usando comparação `master...TBC` e leitura dos arquivos originais. No momento da consulta:

1. O fork possui **199 commits à frente do seu branch `master`**, sem commits atrás. Não atribuir todos exclusivamente ao turno.
2. Foram adicionados `gemrb/core/TurnBasedCombatManager.cpp` (**568 linhas**) e `gemrb/core/TurnBasedCombatManager.h` (**177 linhas**), além de dezenas de alterações ao núcleo — notadamente `Actor.cpp`, `GameScript/Actions.cpp`, `GameScript/GSUtils.cpp`, `Map.cpp`, `GUI/GameControl.cpp`, `Game.cpp` e `Interface.cpp`.
3. `InitiativeSlot` inclui ponteiro para `Actor`, ordem de iniciativa, deslocamento restante, disponibilidade das ações principal e livre, flags e temporização.
4. `FirstRoundStart()` ordena a iniciativa, atualiza fases para ataques múltiplos e interage com o tempo interno do jogo.
5. `EndTurn()` percorre fases, trata ações postergadas, ataques de oportunidade e progressão temporal por frações de round.
6. `UpdateTurnBased()` observa participantes ativos, mortes, inimigos, início/fim de combate, interrupções e atualizações de estado.
7. `ToggleTurnBased()` permite ligar/desligar a modalidade no fork. **Não prova transição segura durante todas as condições de combate.**
8. Na comparação de arquivos **não aparecem testes especificamente novos do modo TBC**. Não equivale à afirmação de que o projeto inteiro não possui testes.
9. O foco da inspeção foi diff e gerenciador. Não foram compilados binários, executadas batalhas, conferidas magias com instrumentação nem realizados ensaios multiplayer.

## Pergunta de arquitetura: reaproveitar C++ diretamente?

- **No próprio GemRB:** código C++ nativo integrado; potencialmente reutilizável após resolver suporte a dados e multiplayer.
- **No BG2:EE comercial:** sem acesso ao código do motor proprietário para simplesmente adicionar `TurnBasedCombatManager.cpp`; exige reimplementar o comportamento por hooks compatíveis do EEex, interceptação de ações/tempo e interface, com sincronismo pelo host. Código GPL-2.0+ do fork não se converte em permissão para modificar ou redistribuir o motor fechado.
- **Em motor novo 2D:** a lógica do manager pode servir de inspiração/parte de uma reimplementação licenciada, mas a arquitetura de multiplayer e de conteúdo teria de ser construída e mantida.

## Critérios de POC priorizados

**G0 — baseline e reversibilidade**: BG2:EE limpo, build/versão documentados, save de teste, backup. Não modificar a instalação original.

**G1 — turnos solo do fork**: usar dados de jogo compatíveis com GemRB-TBC; verificar ataque, movimento, 2 ataques/round, magia de duração, interrupção, AoO, alternância e save/load. Reproduzir log/testemunho.

**G2 — portabilidade de dados**: testar em instalações separadas BG2 clássico, BG2:EE e EET, observando o que é carregado e o que falha. Não incorporar IWD/NWNForBG prematuramente.

**G3 — hooks EEex**: listar callbacks para timing, scripts de NPC, spawn, pausa, seleção, animações, resultados de ataque, ações bloqueáveis e UI; criar experimento **não destrutivo** de gate de ação.

**G4 — multiplayer BG2:EE**: dois clientes; host autoriza iniciativa, ação e finalização de turno; cliente rejeita comandos fora da vez; loss/reconnect; efeitos e saves verificados antes de confirmar.

**G5 — decisão de arquitetura**: se G3/G4 não forem suficientes, o modo de turnos continua condicionado e o RTwP mantém a funcionalidade principal. Solicitar decisão explícita antes de pivotar para GemRB como engine.

## Falhas específicas a procurar

- Congelamento ou aceleração indevida de efeitos de duração; `Haste`, `Slow`, dano periódico, conjuração com casting time, efeitos de área.
- Duplicação ou perda de ações; múltiplos ataques/round; NPC neutro entrando no combate; combate prolongado em outra área.
- Turnos independentes em diferentes clientes (desync), temporizador avançando no cliente sem autorização do host.
- AoO que interrompe outro turno e não devolve o controle; passos de movimento que atravessam aliados/inimigos indevidamente.
- Duplicação após save/load ou recovery; modo alternado em meio a animações; rollback de saves do Living World.
- Mod de conteúdo com triggers baseados em tempo real que não são disparados ao mudar o relógio.

## Resultado final da investigação documental

- **Viabilidade conceitual da modalidade de turnos:** alta (implementação GemRB-TBC observável em código).
- **Viabilidade de instalar o fork como solução imediata dentro do atual BG2:EE multiplayer:** **não**.
- **Viabilidade de implementar modalidade equivalente via EEex no BG2:EE:** **indeterminada** (faltam POCs de hooks, temporização e sincronização).
- **Viabilidade de mover todo o Infinity AI para GemRB-TBC mantendo o escopo aprovado:** **baixa no estado atual**, por ausência de multiplayer e lacunas de compatibilidade.

Não foram testadas instalações reais. Critérios acima são **gates propostos**, não testes executados.

## Fontes

- Fork código: https://github.com/Dreamkins/gemrb-TBC
- `TurnBasedCombatManager.cpp`: https://github.com/Dreamkins/gemrb-TBC/blob/TBC/gemrb/core/TurnBasedCombatManager.cpp
- `TurnBasedCombatManager.h`: https://github.com/Dreamkins/gemrb-TBC/blob/TBC/gemrb/core/TurnBasedCombatManager.h
- Upstream: https://gemrb.org/Features.html ; https://gemrb.org/Modding.html ; https://gemrb.org/Install
- EEex: https://github.com/Bubb13/EEex
- EET: https://gibberlings3.github.io/Documentation/readmes/readme-EET.html

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

As provas técnicas de DEC-067 devem testar se BG2:EE/EEex oferecem observações confiáveis de NPCs genéricos, sem assumir IDs ou suporte a spawn persistente; host+dois clientes e builds reproduzíveis.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Como requisito de POC DEC-068, testar se observações/ações offscreen que dependem de engine podem ser confirmadas no host e reconciliadas após saves/loads. Nenhuma capacidade de pathfinding persistente, spawn de NPC genérico ou sync multiplayer foi demonstrada; se falhar, manter apenas camada narrativa limitada.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

O sequenciamento de eventos e reentrância deve distinguir revisão de plano, operações in-flight e host receipts antes de declarar estado terminal.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-097/C — Discovery v9.3

Composição DEC-097/C depende de testes host+clientes, epoch, recibos e mapeamento real de métricas; sem POC não altera preços/patrulhas.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Simulação por níveis não é materialização física. Reentrada exige diff por snapshots e ownership DEC-098, com caps e host receipts.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Estados ACTIVE/NEAR/DISTANT/DORMANT não promovem observações técnicas ausentes a fatos de quest.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **simulação por relevância**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para persistência em domínios ativos, próximos e distantes, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Avanço do mundo em FROZEN/PARTIAL/REALTIME não pode ser inferido de relógio civil. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Relógio parcial/frozen impede adiantar prazos por cronômetro civil. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
