# Probe EEex read-only (SPEC-001, gate P2)

Publica no console do jogo, uma linha por evento, somente os campos da allowlist:

```
INFAI-P2 {"schema":"infinity-ai.eeex-probe.v1","seq":12,"session_seq":1,"clock_ms":246121,"fields":{"host.current_area_id":"AR0602","host.game_time":40709}}
```

- Lê `EEex_Area_GetVisible()` → `m_resref` e `m_worldTime.m_gameTime`, dentro de `pcall`. Sem área visível, os dois campos saem `null` (no menu o motor informa tempo 0, que não é observação).
- Publica ao mudar a área ou a sessão, e a cada 5 s (checagem no máximo 1×/s), por um menu oculto cujo `enabled` chama `INFAI_P2_Tick()` (mesmo padrão dos módulos do EEex).
- `session_seq` sobe a cada destroy de sessão (load, volta ao menu): vira o `host_epoch` do bridge.
- Não lê comandos, não grava arquivos (o Lua do jogo com EEex não tem `io`/`os`), não altera estado do motor. `tests/test_eeex_probe.py` verifica isso estaticamente e, com `lupa`, em Lua 5.2 com objetos do motor somente leitura.

## Instalação no laboratório

1. Jogo fechado. Copie `M_INFAI.lua` e `INFAIP2.menu` para `override\` da cópia com EEex (nunca na cópia P0).
2. Em `InfinityLoader.ini` da mesma cópia, `LogFile=InfinityLoader.log` (o loader espelha o console nesse arquivo; ele é recriado a cada abertura).
3. Abra pelo `InfinityLoader.exe`. As linhas aparecem no log com o prefixo `INFO: LPRINT: `.
4. Leitura: `src/infinity_ai/bridge/eeex_log.py` (`EEexLogAdapter`); sessão de laboratório: `tools/windows-lab/p2_lab_session.py`.

Para remover: apague os dois arquivos do `override\` e volte `LogFile=` ao valor vazio.

**Limite conhecido:** o log não é autenticado; qualquer mod pode imprimir `INFAI-P2`. Serve ao laboratório, não ao multiplayer.
