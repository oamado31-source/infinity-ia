# Probe EEex read-only (SPEC-001, gate P2)

Publica no console do jogo, uma linha por evento, somente os campos da allowlist:

```
INFAI-P2 {"schema":"infinity-ai.eeex-probe.v1","seq":12,"session_seq":1,"clock_ms":246121,"fields":{"host.current_area_id":"AR0602","host.game_time":40709,"party.companion_ids":["Imoen","Minsc","jaheira"]}}
```

- Lê `EEex_Area_GetVisible()` → `m_resref`, `m_worldTime.m_gameTime` e, para os retratos 1–5, `EEex_Sprite_GetInPortrait(i)` → `m_scriptName` (o retrato 0 é o protagonista, um PC), tudo dentro de `pcall`. Sem área visível, os campos saem `null` (no menu o motor informa tempo 0, que não é observação). Falha na leitura do grupo → `null`, nunca lista vazia inventada.
- Publica ao mudar a área, o grupo ou a sessão, e a cada 5 s (checagem no máximo 1×/s), por um menu oculto cujo `enabled` chama `INFAI_P2_Tick()` (mesmo padrão dos módulos do EEex).
- `session_seq` sobe a cada destroy de sessão (load, volta ao menu): vira o `host_epoch` do bridge.
- Não lê comandos, não grava arquivos (o Lua do jogo com EEex não tem `io`/`os`), não altera estado do motor. `tests/test_eeex_probe.py` verifica isso estaticamente e, com `lupa`, em Lua 5.2 com objetos do motor somente leitura.

## Instalação no laboratório

1. Jogo fechado. Copie `M_INFAI.lua` e `INFAIP2.menu` para `override\` da cópia com EEex (nunca na cópia P0).
2. Em `InfinityLoader.ini` da mesma cópia, `LogFile=InfinityLoader.log` (o loader espelha o console nesse arquivo; ele é recriado a cada abertura).
3. Abra pelo `InfinityLoader.exe`. As linhas aparecem no log com o prefixo `INFO: LPRINT: `.
4. Leitura: `src/infinity_ai/bridge/eeex_log.py` (`EEexLogAdapter`); sessão de laboratório: `tools/windows-lab/p2_lab_session.py`.

Para remover: apague os dois arquivos do `override\` e volte `LogFile=` ao valor vazio.

**Limite conhecido:** o log não é autenticado; qualquer mod pode imprimir `INFAI-P2`. Serve ao laboratório, não ao multiplayer.

## Caixa de diálogo no jogo (ADR-0116, SPEC-004/006)

`M_INFAIT.lua` + `INFAITLK.menu`, instalados na mesma cópia que o probe:

- **Abrir:** **clique com o botão direito** numa criatura fora do grupo (ou **F9**, `INFAI_TALK_KEY_NAME`, com o cursor sobre ela; no Mac, Fn+F9) abre um painel com nome, histórico, campo de texto, Enviar/Sair e o botão reservado "aperte para falar". O clique direito é capturado embrulhando `EEex_Key_Hook_AfterEventsPoll`; só é consumido sobre uma criatura fora do grupo, na tela de mundo.
- **Pausa:** enquanto a caixa está aberta o jogo fica pausado, como no diálogo nativo (`EEex_GameState_TogglePause`); ao fechar, só desfaz a pausa que a própria caixa fez.
- **Pedido:** Enviar ou Enter publica `INFAI-TALK {json}` com o pedido, a área, o tempo, o falante (script name, CRE, nome, id da instância, se está morto), o texto e os ouvintes: companheiros ao alcance de 448 com linha de visão.
- **Resposta:** vem de `override\INFAIRSP.lua` (só `INFAI_TALK_Reply = {req_id, speech}`), relido com `Infinity_DoFile` a cada 500 ms, com timeout de 60 s.
- **Garantias:** não altera variáveis, diário, diálogos nem save. `tests/test_talk.py` verifica a allowlist de funções do motor e que o único arquivo lido é a resposta.

Cópia para a VM: `python tools/windows-lab/talk_poc.py --deploy` (depois, reabrir o jogo). O serviço `dialogue_service.py` responde aos pedidos; `talk_poc.py` sem argumentos só responde com eco, sem modelo.


## Diagnóstico read-only de atributos sociais (ADR-0122, POC)

A caixa de diálogo também envia, no evento `INFAI-TALK`, observações opcionais do alvo:

- `chr_active`: `EEex_Sprite_GetActiveStats(sprite).m_nCHR`.
- `chr_base`: `sprite.m_baseStats.m_CHRBase`.
- `engine_morale_current`: `sprite.m_baseStats.m_morale` (estado atual do motor).
- `engine_morale_break_active`: `EEex_Sprite_GetActiveStats(sprite).m_nMoraleBreak`.
- `engine_morale_break_base`: `sprite.m_baseStats.m_moraleBreak`.

Também envia `selected_leader`, obtido por `EEex_Sprite_GetSelected()`, somente quando o líder selecionado corresponde a um dos retratos da party. O objeto contém script/name, id da instância, índice do retrato e Carisma-base/ativo. **É um candidato a iniciador, não prova de quem efetivamente iniciou o diálogo**; a semântica precisa ser validada na build pinada.

`m_morale` não pertence a `CDerivedStats`; é lido de `CCreatureFileHeader`. Não confundir a moral atual do motor com o valor-base de Morale do AD&D 2e. Morale Break é um limiar próprio do motor, não uma substituição automática para Morale AD&D.

Os valores são diagnósticos apenas: não alteram a seleção, não decidem Reaction Table 59 ou Morale Check e não são usados como modificadores pela DialogueEngine. Falhas de leitura resultam em `null`, sem valores presumidos. O serviço imprime os campos para comparação no laboratório.

### Roteiro de validação

1. Atualize a branch de POC, copie os arquivos do probe com `python tools/windows-lab/talk_poc.py --deploy` e reabra o jogo pela cópia P1 pinada.
2. Com um save descartável, selecione cada personagem da party individualmente; abra a caixa sobre o mesmo NPC e envie uma pergunta curta.
3. Repita com grupos de personagens selecionados e registre `selected_leader`, retrato e Carisma. Compare com o personagem que o motor efetivamente usa para iniciar um diálogo nativo equivalente.
4. Compare Carisma-base/ativo e Morale Break-base/ativo do NPC; repita com um ator cujo Morale varie durante o jogo, se disponível.
5. Registre versão/build, modpack hash e saída do serviço. Se não for possível provar o iniciador, mantenha o campo desconhecido e não aplique modificador de Carisma.

O teste é read-only. Não salve por cima de saves de uso normal, não instale o probe na cópia P0 e não altere scripts, reputação, quests ou estado do jogo.
