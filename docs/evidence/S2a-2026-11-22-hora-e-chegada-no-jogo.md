# Evidência S2a — ADR-0139: hora do dia e chegada a um lugar (2026-11-22)

**Gate:** etapa 1, single player, save descartável; ADR-0139, sobre a presença da ADR-0138.
**Resultado:** **APROVADO no laboratório ARM64/VM.** A quest de teste andou por chegada a lugares, sem conversa. A visão de Tamoko apareceu só à noite e sumiu de dia, com o jogo confirmando. O relógio foi calibrado contra o do próprio jogo. Os sete pontos passaram.

A série S1 terminou na S1z; esta é a primeira da série S2.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, Capítulo 2, uma linha só de saves desde NOITE-INICIO) e Claude Code (serviço com `--quest-presence` e `--local-quests`).

## Preparação

**Quest de teste só local:** `~/.infinity-ai/quests/local/teste-noite.pt_BR.json`, fora do repositório (D4).
- Bernard oferece ("vulto") e o grupo aceita ("vou vigiar").
- Passos:
  1. chegar às Favelas (AR0400);
  2. chegar à Coroa (AR0406) à noite, depois do primeiro passo;
  3. falar com a visão, depois do segundo passo.
- Presença: `IATAMOKO` na AR0406, `when: NIGHT`.

## Calibração do relógio (ponto 1)

| Tempo de jogo | Relógio do jogo | Hora com 300 por hora | Hora com 4500 por hora |
|---|---|---|---|
| 497541 | 14h | 2h | **14h** |
| 538089 | dia 5, 23h | — | **23h**, dia 5 |
| 577690 | dia 6, 8h | — | **8h**, dia 6 |

- O tempo do probe conta ticks do motor, 15 por segundo de jogo: uma hora tem 4500 e um dia 108000. A suposição antiga (300 por hora) estava errada e foi corrigida em `quests/clock.py`.
- Dia = tempo ÷ 108000 + 1, conferido nas leituras 2 e 3. Na primeira, o mantenedor leu "dia 4", e a fórmula dá 5. A hora bateu nas três.
- **Pendência fora da ADR:** `dialogue/recall.py` (`DAY = 7200`) e o limite de residência (7200) supõem um dia que na verdade é cerca de 1h36 de jogo.

## Os sete pontos

| # | Ponto | Resultado |
|---|---|---|
| 1 | Calibração | as três leituras acima |
| 2 | De dia, quest aceita | aceita às 15h (`ACEITA(0)`); nenhum pedido; ela não apareceu |
| 3 | À noite, ela aparece | ao entrar na Coroa às 23h: `ENTER IATAMOKO … hora 23`, `HOST_CONFIRMED`; ela apareceu |
| 4 | Ao amanhecer | fora da Coroa, ela ficou no mapa; na entrada às 8h: `LEAVE INFAI_TAMOKO … hora 8`, `HOST_CONFIRMED`; ela sumiu em cerca de 10 s (probe a cada 5 s, diretor a cada 2 s, contagem do módulo em 3 s); o ramo ficou sem criatura nossa |
| 5 | Chegar antes de aceitar | saída às Favelas e volta antes de aceitar: só `AreaEntered`, nenhum passo |
| 6 | Chegar depois de aceitar | `chegada: teste-noite:ir-as-favelas em AR0400 (hora 15)`, uma vez; o diário foi mostrado uma vez, na resposta de um morador das Favelas (`NarrativeQuestJournalShown`) |
| 7 | Ordem (`after`) e noite | às 15h, na Coroa, sem as Favelas: nenhum passo; às 23h, depois das Favelas: `chegada: teste-noite:voltar-a-noite em AR0406 (hora 23)` |

## Limites

- Como na ADR-0138, um save posterior de outra linha não abre ramo novo. A contagem antes de criar entra com a peça G, e este teste correu numa linha só de saves.
- O diário de uma chegada vai na próxima resposta de um morador. Um companheiro na caixa ainda não o mostra.

## Verificação do ramo

- Suíte OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64.
