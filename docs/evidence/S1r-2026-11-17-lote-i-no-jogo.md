# Evidência S1r — lote I (o Leste e as terras distantes) no jogo (single player, 2026-11-17)

**Gate:** etapa 4 do plano de conhecimento (testes reais), CR-2026-029.
**Resultado:** **APROVADO no laboratório ARM64/VM** (mantenedor: "Testes feitos, tudo OK para abrir o PR"). Salvanas, morador de Athkatla, respondeu sobre a Simbul, o Leste e Lolth de primeira, sem nenhuma recusa.
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin`).

## Preparação

- **Pacote:** 160 entradas, revisão `sha256:fea4d45fac5b`, pinada à mão no ramo `br-c10e8c5d3d47`. A revisão inclui `talk_only_regions` (CR-2026-029).
- **Serviço:** reiniciado com o lote I (`vendedores: 19`, ADR-0132).
- **Caixa e manifesto:** sem mudança (`s1j-manifest-2026-11-15e-pinned.json`).

## Turnos

Salvanas, reação amistosa, com 112 assuntos no prompt (109 antes do lote I). O log não guarda as falas (ADR-0107); a avaliação das respostas é a do mantenedor no jogo.

| Turno | Entradas usadas | Resultado |
|---|---|---|
| 1 | `char:simbul` | OK de primeira |
| 2 | `org:red-wizards`, `topic:east-renown`, `topic:far-lands-renown` | OK de primeira: o tópico novo do Leste chegou a quem mora em Athkatla |
| 3 | `char:lolth` | OK de primeira |

## Ajuste feito antes do teste

- **Umbreterna dava "não sei":** antes do teste, "O que é Umbreterna?" dava "não sei" para todo NPC da superfície.
- **Mudança em Lolth:** o resumo e a camada popular de Lolth passaram a dizer "dos drows de Umbreterna (Underdark), o mundo debaixo da terra". Lolth é conhecida em toda Faerûn, então a pergunta chega pela menção (CR-2026-026).
- **Bateria:** o caso `umbreterna-pela-lolth` cobre isso.

## Pendência anotada

O modelo às vezes inventa de quem ouviu algo ("um comerciante que veio do norte"). A regra 7 do prompt proíbe isso, mas nenhum verificador pega.
