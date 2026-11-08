# Evidência P2 — bridge read-only allowlisted no laboratório Windows 11 ARM64 (2026-11-08)

**Gate:** P2 (ADR-0108, `docs/architecture/testing.md`: "dados allowlisted, UNKNOWN, nenhuma escrita"; ADR-0095: probe read-only provado por build). **Resultado:** APROVADO **no laboratório ARM64/VM** do CR-2026-001 (ainda PROPOSED), com a ressalva da troca de área (abaixo). Não vale para Windows x86-64 nativo nem para multiplayer (P4).
**Pré-requisitos:** P0 e P1 no mesmo laboratório (`P0-…`, `P1-2026-11-08-laboratorio-arm64.md`).
**Executado por:** Claude Code via SSH (instalação do probe, coleta, sessão do bridge) e mantenedor (passos de jogo).

## Arquitetura testada

```
BG2:EE 2.7.3.0 + EEex v1.3.1 (cópia BG2EE-P1)
  └─ override/M_INFAI.lua + INFAIP2.menu  (probe: lê 2 campos, imprime "INFAI-P2 {json}")
       └─ console ─► InfinityLoader LogFile=InfinityLoader.log   (canal de mão única)
            └─ SSH (leitura) ─► EEexLogAdapter ─► ReadOnlyBridge ─► envelopes JSONL
```

Nenhum caminho leva dados do Infinity AI para dentro do jogo. O Lua do jogo com EEex não abre `io`/`os`.

## Componentes

| Item | Valor |
|---|---|
| Probe | `tools/eeex-probe/M_INFAI.lua` (sha256 `c3fa92b41196…`), `INFAIP2.menu` (`43208e5251cd…`), schema `infinity-ai.eeex-probe.v1` |
| Adapter | `src/infinity_ai/bridge/eeex_log.py`, `ADAPTER_VERSION = eeex-log-0.1+probe-v1` |
| Allowlist | `host.current_area_id` e `host.game_time`, visibilidade `PARTY`, finalidade `narrative_context` |
| Configuração | `InfinityLoader.ini`: `LogFile=InfinityLoader.log` (original guardado como `InfinityLoader.ini.pre-p2`) |
| `build_fingerprint` (pinado e ao vivo) | `sha256:c05b2b973695b622de21a4ada502e862f1ec079c09f53c184cfe7dc2de10d94e` (igual ao P1) |
| `modpack_hash` (pinado e ao vivo) | `sha256:a7ce74c9f9611abcb103eafb9ca256884d2c11bb9f85f74aa9540b19f226c2dc` (P1 + 2 arquivos do probe) |

## Spike do canal (antes do código)

- `print` chega ao log em linha própria com o prefixo `INFO: LPRINT: `; `EEex_Print` chega sem quebra de linha (cola na linha seguinte). O probe usa `print`.
- `EEex_Area_GetVisible()` + `m_resref:get()` e `m_worldTime.m_gameTime` leem sem erro.
- **No menu principal o motor informa `m_gameTime = 0` sem partida carregada.** O probe publica `null` para o tempo quando não há área visível; sem isso, o zero viraria uma observação falsa (REQ-BRIDGE-005).

## Sessão (2026-11-08, 20:17:47–20:27:54 UTC; 251 registros)

| Momento (UTC) | Situação no jogo | Resultado no bridge |
|---|---|---|
| 20:17–20:20 | jogo fechado | `connect` falha fechado (`ADAPTER_UNAVAILABLE`, log parado há >10 s); leituras `BLOCKED_CAPABILITY` |
| 20:20:45 | menu principal | `connect` ok, época 0; área e tempo `UNKNOWN`/`NOT_OBSERVED` |
| 20:20:45 | — (sessão aberta) | escrita `BLOCKED_CAPABILITY`/`WRITE_FORBIDDEN`; `creature.inventory` `FIELD_NOT_ALLOWLISTED`; finalidade errada `DENIED`/`ACL_PURPOSE`; audiência inválida `MALFORMED_REQUEST` — **nenhuma delas leu o log** (verificado nos testes de integração) |
| 20:21:26–20:23:41 | save P1 carregado, no mapa | área `AR0602` e tempo `OBSERVED` (35/34 leituras), tempo avançando |
| 20:23:35 (17:23:35 local) | save `INFINITY-P2-DESCARTAVEL` gravado | — |
| 20:23:45 | reload do save P2 | `BLOCKED_CAPABILITY`/`EPOCH_MISMATCH`, sessão fechada |
| 20:23:51 | — | reconexão com época 1 (operador no papel do host); `OBSERVED`; tempo volta ao valor do save |
| 20:24:50 → fim | jogo fechado | leituras `UNKNOWN`/`ADAPTER_UNAVAILABLE` (nunca valor inventado) |

## Integridade

- Arquivos da cópia P1 alterados desde a instalação do probe: só `InfinityLoader.log` e os 2 arquivos do probe. `build_fingerprint` e `modpack_hash` iguais no início e no fim da sessão.
- Sem `InfinityLoader_Crash`, sem `.dmp`, 0 erros de Lua no log; 50 linhas `INFAI-P2` em ~4 min de jogo (~120 bytes cada).
- O log é **recriado a cada abertura do jogo** (nenhuma linha do spike sobreviveu).
- Cópia P0 continua idêntica à instalação Steam (2.324 arquivos, 0 diferenças); saves P0 e P1 intocados.

## Ressalvas e achados

1. **Troca de área não comprovada no laboratório:** a área ficou `AR0602` durante toda a sessão (os portões internos dessa área não trocam de resref). A detecção de mudança está coberta pelos testes do probe em Lua 5.2 simulado (`tests/test_eeex_probe.py`), não por observação real.
2. **`m_gameTime` não é monotônico:** recuou 1 tick ao pausar (20:23:06→20:23:12), comportamento já comentado pelo EEex (`B3TimeStep.lua`), e volta ao valor do save após um load. Consumidores não podem tratar o tempo como relógio crescente.
3. **Rótulo de evidência corrigido após a sessão:** nessa gravação, envelopes de recusa saíram com `evidence: SYNTHETIC` porque o bridge usava esse padrão quando não há leitura. Corrigido (`ReadOnlyBridge(..., evidence=Evidence.LAB_OBSERVED)` no script de laboratório, teste novo); as leituras reais já saíam `LAB_OBSERVED`. Os status e reasons não mudam.
4. **Log não autenticado:** qualquer mod que imprima `INFAI-P2` pode forjar observações; o parser só aceita o schema e os 2 campos com formato válido, mas isso não autentica a origem. Aceitável no laboratório; P4 exige canal autenticado.
5. **Época é local à execução:** `session_seq` recomeça em 0 a cada abertura do jogo; o pin de época continua sendo confirmação do host (aqui, do operador).

## Verificação automatizada

`python -m unittest discover -s tests` → 72 testes (8 do probe em Lua 5.2 com `lupa`; pulados quando ausente). Testes estáticos do probe: só funções allowlisted do EEex/Infinity, nenhuma atribuição a estado do motor, leituras protegidas por `pcall`; três mutações proibidas inseridas manualmente foram detectadas.

## O que não foi publicado

Log bruto, manifestos e o JSONL da sessão ficam fora do repositório. Nenhum save, arquivo do jogo, usuário ou caminho pessoal no repositório.
