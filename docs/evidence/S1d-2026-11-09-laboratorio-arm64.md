# Evidência S1d — conhecimento comum regional de NPCs (single player, 2026-11-09)

**Gate:** S1 (etapa 1, ADR-0113), parte "d": ADR-0114 sobre SPEC-003/004/005. **Resultado:** mecânica (pin, gate, registro, ramo, diálogo) **APROVADA no laboratório ARM64/VM** (CR-2026-001). O canal testado, exposição de companheiros por tempo, foi **rejeitado pelo mantenedor** e substituído antes do merge. Single player.
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`) e Claude Code via SSH (serviço de diálogo no Mac).

## Preparação

- Pacote 1369 DR com 6 entradas reclassificadas `COMMON_REGIONAL`: `region:amn`, `region:athkatla`, `region:tethyr`, `org:council-of-six`, `org:cowled-wizards` e `event:tethyr-reclamation-wars-end`. As outras 4 continuam `CANON_REFERENCE`. A Copper Coronet (`AR0406`) foi ligada a Athkatla e Amn. Nova revisão `sha256:9ef2416a…`.
- Pin explícito (`tools/windows-lab/pin_canon_pack.py`) ancorado no tempo de jogo lido do probe. Antes do pin, o serviço registrou `REVISION_CHANGED` e não concedeu nada.
- Modo de depuração do jogo ligado temporariamente no `baldur.lua` da VM (com backup), para o teleporte. O atalho Ctrl+Espaço foi enviado à janela do jogo por uma tarefa agendada interativa, porque no Mac o atalho é capturado pelo sistema.

## Roteiro e resultado

| Passo | Observado |
|---|---|
| Jaheira, na masmorra (`AR0602`), perguntada "quem governa Amn?" | Duas tentativas do modelo barradas (`UNKNOWN_NAMES`: nomes inventados, depois "Amn" sem `unknown`); fala de reserva. **Nada inventado.** |
| Viagem pelo painel de depuração até `AR0406` | Entrada gravada. O observador leu dois tempos falsos durante a viagem (54606 e 55176) e, quando o tempo "voltou" a 45122, criou um ramo filho. O novo ramo não via o pin → `REVISION_CHANGED`, até novo pin explícito → `MATCH`. |
| Tempo em Athkatla | Um descanso não foi possível (sem quarto alugado); o tempo avançou com exploração e viagens. Tempo contado: 1581 + 5739 = 7320 ≥ 7200. Os 255 passados em `AR0335` (fora de Athkatla) ficaram fora. |
| Concessão (regra rejeitada, `REGIONAL_EXPOSURE`) | Imoen, Jaheira e Minsc receberam `org:council-of-six`, `region:athkatla`, `region:amn` e `org:cowled-wizards`. Tethyr e as entradas `CANON_REFERENCE` não foram concedidas. |
| Mesma pergunta depois | Jaheira: "O Conselho dos Seis…", acrescentando que não se deve perguntar quem são. Status `OK`, 1 fato `K` usado, sem alertas, sem dizer que viu. A ressalva vem do resumo (identidades secretas). |

## Decisão do mantenedor após o teste

Um membro do grupo não aprende sobre um lugar só por estar nele por horas ou dias, sem pesquisar nem conversar com os habitantes. A regra virou o ADR-0114:

- `ORIGIN`: antecedente curado, para qualquer NPC.
- `RESIDENCE`: tempo de permanência, só para NPCs de fora do grupo.
- `INQUIRY`: perguntar a quem sabe ou pesquisar, reservado para a próxima entrega.

Com a regra final, os companheiros deste teste não teriam aprendido nada (teste `test_days_in_athkatla_teach_companions_nothing`).

## Pendências

- Unidade de `game_time`: medir um descanso real numa estalagem (alugando o quarto).
- Observador: ignorar picos de tempo durante a troca de área, em vez de criar ramo.
- Validador: aceitar nomes vindos da pergunta do jogador também quando o NPC responde sem se declarar sem conhecimento.
- Canal `INQUIRY`: observar a conversa do jogo com um habitante e o tema perguntado.
- Reverter o `Debug Mode` no `baldur.lua` da VM com o jogo fechado.
- Os registros `REGIONAL_EXPOSURE` ficam no banco `lab-s1` como evidência; novas rodadas usam outra campanha.
