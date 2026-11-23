# Evidência S2b — ADR-0140: contagem no jogo (2026-11-22)

**Gate:** etapa 1, single player, save descartável; ADR-0140, sobre a presença da ADR-0138.
**Resultado:** **APROVADO no laboratório ARM64/VM.** O diretor contou antes de confiar no ramo, criou as cópias que faltavam e recriou a criatura que tinha caído. Viu a derrota dos camponeses quando a contagem dos vivos chegou a zero. Os sete pontos passaram, depois de uma correção no módulo: o jogo também conta os corpos.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, Coroa de Cobre, Capítulo 2, uma linha só de saves desde CONTAGEM-INICIO) e Claude Code (módulo `M_INFAIA.lua` com `COUNT`, serviço com `--quest-presence` e `--local-quests`).

## Preparação

- **Módulo novo instalado com o jogo fechado.** O manifesto foi fixado de novo, duas vezes: a primeira com `COUNT`, a segunda com a contagem só dos vivos. A build continua a mesma; mudaram só `m_infaia.lua` e a lista de variáveis que o serviço grava (`infaiqst.lua`).
- **Quest de teste só local:** `~/.infinity-ai/quests/local/teste-contagem.pt_BR.json`.
  - Bernard oferece e o grupo aceita.
  - Presenças: a visão de Tamoko (`IATAMOKO`) e dois camponeses de teste (`IAP3TEST`, `copies: 2`).
  - Passo de derrota dos camponeses e entrega a Bernard.

## Os sete pontos

| # | Ponto | Resultado |
|---|---|---|
| 1 | Aceitar cria, contando antes | Tamoko: `COUNT 0` (`VERIFY`) e depois `SPAWN` (de 0 para 1). Camponeses: `COUNT 1` (o save já tinha o camponês do teste do P3) e só **uma** criação (de 1 para 2). Todos `HOST_CONFIRMED` |
| 2 | Sair e voltar | na volta, só `COUNT INFAI_TAMOKO 1`; nada criado |
| 3 | Registro errado corrigido | Tamoko apagada pelo console (`Ctrl+Y`); na volta, `COUNT 0` e recriação (de 0 para 1) |
| 4 | Derrota | camponeses apagados pelo console. Primeira tentativa: a contagem seguiu em 2, porque o seletor do jogo devolve os corpos (ver abaixo). Depois da correção, com o save CONTAGEM-CORPOS: `DEFEAT_WATCH` contou 0 vivos, e o passo foi feito (`DEFEAT`, `DEFEATED`) |
| 5 | Depois da derrota | saída e volta: nenhum camponês recriado. Uma contagem de Tamoko no meio da troca de área foi recusada (`WRONG_AREA`), sem suspender |
| 6 | Entrega | Bernard resolveu a quest (`RESOLVIDA`), com as duas linhas do diário; o diretor removeu Tamoko (`LEAVE`, `HOST_CONFIRMED`), cuja presença ia até a quest resolvida |
| 7 | Área errada | `lab_action.py count` em AR0300 com o grupo em AR0406: `REFUSED`, `WRONG_AREA`; na área certa, `DONE 0` |

## O que apareceu no caminho

1. **O jogo conta os corpos.** O seletor da área (`EEex_Area_GetAllOfTypeStringInRange`) devolve também as criaturas mortas. A ADR-0136 dizia o contrário, mas isso vinha do teste do `DPMALE`, quando a busca ainda estava quebrada.
   - Correção: o módulo tira da conta quem tem o estado de morte do jogo (bit 0x800), a mesma checagem da caixa, em `COUNT`, `SPAWN` e `DESPAWN`.
   - Teste do módulo com um corpo simulado; ADR-0140, item 1.
   - Tamoko, apagada do mesmo jeito, tinha dado 0 desde o começo, provavelmente porque o corpo dela some.
2. **Ordem das linhas do diário.** A linha do passo feito sem conversa (a derrota) saiu depois da linha da entrega. Corrigido: o que aconteceu antes desta resposta vem primeiro.
3. **Uma contagem a mais na volta.** Uma contagem saiu um instante antes de o jogo registrar a entrada, e o diretor contou de novo. Isso não criou nada.
4. **Custo da vigia.** Com a derrota pendente, uma contagem a cada cerca de 9 segundos, com dois eventos cada. Dá para espaçar depois, se pesar.

## Verificação do ramo

- Suíte OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64.
