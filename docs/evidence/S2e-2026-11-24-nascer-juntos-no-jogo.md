# Evidência S2e — ADR-0143: nascer juntos (2026-11-24)

**Gate:** etapa 1, single player, save descartável; ADR-0143, sobre a ADR-0142 (S2d).
**Resultado:** **APROVADO no laboratório ARM64/VM.** As cópias nasceram juntas, cada pedido confirmado pelas duas contagens. A célula ficou hostil em ciclos seguidos, antes de qualquer vigia.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, Favelas AR0400, Capítulo 2, save COMBATE-INICIO, ramo novo) e Claude Code (serviço com `--quest-presence --local-quests`, `lab_action.py`).

## Preparação

- Módulo novo instalado com o jogo fechado; SHA-256 igual ao do ramo (`1b691e03…`). Manifesto refixado antes e depois do serviço.
- A mesma quest local `teste-combate` e as mesmas criaturas da S2d: carcereiros ×2 nascidos hostis; Kalessia e agentes ×2 neutros, com `hostile_from: intimidacao`.

## Os pontos

| # | Ponto | Resultado |
|---|---|---|
| 1 | Carcereiros juntos | um pedido com `count` 2: nossos de 0 para 2, total da área de 45 para 47, `HOST_CONFIRMED`; o mantenedor viu os dois surgirem juntos e lutou; derrota vigiada (2, 1, 0) e `DEFEATED` |
| 2 | Kalessia e agentes juntos | Kalessia: de 0 para 1, total de 45 para 46. Agentes, num pedido só: de 0 para 2, total de 54 para 56. Todos confirmados |
| 3 | Hostilidade antes da vigia | "Entregue o diário de Sarevok" cumpriu o passo. Kalessia ficou hostil às 03:39:07 (1/1); os agentes no ciclo seguinte, às 03:39:23 (2/2), antes de qualquer vigia (na S2d: 25 s, com uma vigia no meio). Luta feita, derrotas vistas, diário no inventário dela (mantenedor) |
| 4 | Três cópias pelo `lab_action.py` | `spawn --cre IAP3TEST --count 3`: nossos de 0 para 3, total de 52 para 55, `HOST_CONFIRMED`. `--count 9`: `BAD_COUNT`, recusado antes do jogo. Remoção: de 3 para 0, total de 55 para 52 |
| 5 | Falsa confirmação recusada | teste com motor simulado (`test_combat.py`): as nossas sobem e o total não sobe, então as presenças ficam retidas e nada é pedido de novo. A suíte passa |

## O que apareceu no caminho

1. **O total da área muda sozinho.** Caiu de 47 para 45 conforme os carcereiros morriam. Nesta área, os corpos deles saíram da busca do EEex, embora na ADR-0140 (camponeses na Coroa) os corpos continuassem nela; a causa não foi investigada. A contagem das nossas não muda, porque já exclui os mortos. Entre a criação de Kalessia e a dos agentes, o total subiu de 46 para 54, provavelmente com moradores das Favelas entrando na área.
   - Nas criações desta rodada, nada entrou nem saiu nos 3 s, e todas valeram.
   - Se acontecer numa área movimentada, a presença fica retida e o mantenedor a retoma (lado seguro da ADR-0143).
2. **Kalessia agora respondeu no papel** ("Não entrego."), mas ainda sem identidade curada. A curadoria dela com o diário fica para a quest real, como registrado na S2d.

## Verificação do ramo

- Suíte OK (628 testes), também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64 (a primeira rodada deu 63/64, variação do modelo; a mudança não toca o diálogo).
