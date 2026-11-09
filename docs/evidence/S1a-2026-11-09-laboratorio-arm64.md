# Evidência S1a — persistência, ramos no reload e memória de companheiros (single player, 2026-11-09)

**Gate:** S1 (etapa 1, ADR-0113), parte "a": persistência + memória de NPC. **Resultado:** APROVADO PARCIALMENTE **no laboratório ARM64/VM** (CR-2026-001). Diálogo (SPEC-004) e troca de área real ainda não exercitados. **Single player; não é evidência de multiplayer.**
**Executado por:** mantenedor (jogo) e Claude Code via SSH (probe, coleta, sessões, consultas ao banco).

## Componentes

| Item | Valor |
|---|---|
| Jogo / EEex | BG2:EE 2.7.3.0 x64 + EEex v1.3.1 Minimal, cópia `BG2EE-P1` (Windows 11 ARM64, VMware) |
| Probe | `tools/eeex-probe/M_INFAI.lua` (sha256 `16d60626a755…`) + `INFAIP2.menu`, campos `host.current_area_id`, `host.game_time`, `party.companion_ids` |
| `build_fingerprint` | `sha256:c05b2b97…` (igual ao P1/P2), inalterado do início ao fim |
| Banco | `~/.infinity-ai/campaigns/lab-s1.sqlite3` no Mac (fora do repo), schema `0001_initial` |
| Sessões | `tools/windows-lab/s1_record_session.py`, três execuções sobre o mesmo banco |

## Spike da leitura do grupo

`EEex_Sprite_GetInPortrait(i)` + `m_scriptName:get()` dentro de `pcall`: menu principal `n=0`; no mapa `[0 resref=*HARBASE script=None] [1 resref=*MOEN10 script=Imoen]`. O resref vem alterado (`*` no lugar da primeira letra) e varia por versão do CRE; o **script name** é a identidade estável do NPC (`npc:imoen`). O protagonista (`None`) é PC e fica fora da memória de NPC. 0 erros de Lua.

## O que foi gravado

| Tempo de jogo | Ramo | Evento | Observação |
|---|---|---|---|
| 40097 | `main` | `SessionStarted`, `AreaEntered(AR0602)`, `PartyChanged([imoen])` | save P2 carregado |
| 41230 | `main` | `PartyChanged([imoen, minsc])` | Minsc entra no grupo |
| 41373 | `main` | `PartyChanged([imoen, jaheira, minsc])` | Jaheira entra |
| 44982 / 45046 | `main` | `SessionStarted` (gravador reiniciado) e `SessionStarted` após reload | **sem ramo novo**: nada gravado depois do ponto do save |
| 48119 | `main` | `PartyChanged([imoen, jaheira])` | Minsc sai, **depois** do save `INFINITY-S1-DESCARTAVEL` |
| 45054 | `main` → `br-c465a22f8237` | `BranchForked` (pai) + `SessionStarted` (filho) | reload do save S1 sem salvar: ramo filho em `fork_game_time = 45054` |

Totais no backup final: 2 ramos, 11 eventos, 9 experiências de NPC, 0 revisões de crença (nenhuma regra de crença ligada ainda ao jogo).

## Linha do tempo por ramo

- `main` vê os 4 `PartyChanged`, inclusive a saída do Minsc (t=48119).
- `br-c465a22f8237` vê só os 3 primeiros: a saída do Minsc **não** faz parte da linha restaurada, e o grupo continua com os três. Nenhuma linha antiga foi alterada; `DELETE` no banco real foi recusado pelo trigger (`append-only: events`).

## Memória de NPC (recall com `purpose=npc_dialogue`, audiência `NARRATIVE_CONTEXT`)

| NPC | Ramo `main` | Ramo restaurado |
|---|---|---|
| `npc:imoen` | 5 memórias (entrada na área + 4 mudanças de grupo) | 4 (sem a saída do Minsc) |
| `npc:minsc` | 2 (a partir da própria entrada, t=41230) | 2 |
| `npc:jaheira` | 2 (entrada em t=41373 + saída do Minsc) | 1 |

Ninguém lembra do que aconteceu antes de entrar no grupo; a lembrança da saída do Minsc só existe no ramo em que ela aconteceu. Minsc, já fora do grupo, não ganhou memória do próprio evento de saída (não estava presente).

## Integridade e operação

- Backups: `lab-s1-…T000015…` (5 eventos) e `lab-s1-…T001933…` (11 eventos, 9 experiências), ambos com `verify_restore` ok (integrity_check, sha256, contagens, último `seq`).
- Cópia P1: desde a instalação do probe novo só mudaram `InfinityLoader.log` e os 2 arquivos do probe; sem `InfinityLoader_Crash`, sem `.dmp`, 0 erros de Lua.
- Cópia P0: idêntica à instalação Steam (2.324 arquivos, 0 diferenças); saves P0/P1/P2 intactos; save `INFINITY-S1-DESCARTAVEL` criado às 21:01:24 (local).
- O spike do grupo (`M_INFAIS.lua`, `INFAIPS.menu`) foi removido da cópia.

## Achados

1. **Reload sem mudança gravada depois do save não cria ramo** (observado às 00:04 UTC). É o comportamento projetado: só há divisão quando algum evento gravado ficou à frente do ponto restaurado.
2. **Script names chegam com caixa inconsistente** (`jaheira` em minúsculas, `Imoen`, `Minsc`); o adapter normaliza para minúsculas.
3. **A primeira sessão terminou no meio do roteiro** (limite de 15 min); a segunda reabriu o mesmo banco e continuou sem duplicar, como previsto.
4. **Troca de área não aconteceu** (a party ficou na AR0602 o tempo todo); coberta pelos testes do gravador, não por observação real.

## Limites

Linhagem do ramo é inferida do ramo ativo (o save carregado não é identificado). Sem criptografia em repouso, nada `HOST_ONLY`/`SECRET` vindo do jogo é gravado. Revisões de crença existem e estão testadas, mas nenhuma regra de jogo as dispara ainda.

## O que não foi publicado

O banco, os backups e as saídas das sessões ficam fora do repositório.
