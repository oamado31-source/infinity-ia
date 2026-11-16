# Evidência S1l — lotes D e C2 no jogo e pin levado ao ramo novo (single player, 2026-11-16)

**Gate:** etapa 4 do plano de conhecimento (testes reais), CR-2026-020.
**Resultado:** **APROVADO no laboratório ARM64/VM.** Depois de carregar um save antigo, o ramo novo recebeu sozinho a revisão já pinada. Bernard respondeu com o conhecimento dos lotes C2 e A. O mantenedor avaliou: "respostas bem redigidas e com bom embasamento".
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac).

## Preparação

- **Pacote:** 92 entradas (main `93bb754`, PR #47), revisão `sha256:71d951f661d9`. Pin manual no ramo `br-8c55e05ecb4d`.
- **Serviço:** `dialogue_service.py --voice --carry-pin`, com a CR-2026-020 aplicada por cima da main.
- **Caixa e manifesto:** sem mudança (`s1j-manifest-2026-11-15e-pinned.json`).

## O problema que motivou a CR

Nos primeiros testes do dia, os saves carregados abriram os ramos `br-20184c5c981e` e `br-8c55e05ecb4d` com o pin anterior aos lotes D e C2. O serviço desligou o conhecimento do pacote nesses ramos e só avisou no log (`AVISO ... REVISION_CHANGED`). Por isso, as 17 perguntas a Bernard e a Unger foram respondidas sem a enciclopédia.

## Teste com a CR-2026-020

Ao carregar um save antigo, o serviço registrou:

`pin levado ao ramo br-95a903cb3971: revisao sha256:71d951f661d9... (92 entradas, t=488708), aprovada no pin ev-799df6ac904541cfae4c1e50b5ded730 do ramo br-8c55e05ecb4d`

Não saiu nenhum `AVISO`. Bernard (reação amistosa) tinha 73 assuntos no prompt, contra 30 no ramo sem pin.

| Turno | Entradas usadas | Resultado |
|---|---|---|
| 1 | `char:kelemvor` | OK de primeira |
| 2 | nenhuma | OK na 2ª tentativa (1ª recusada por `THIRD_PARTY:ROLE`) |
| 3 | `char:cyric`, `event:cyric-takes-banite-temples` | OK de primeira |
| 4 | `region:cloud-peaks` (Picos das Nuvens) | OK de primeira |
| 5 | `topic:tymora-pearls-in-amn`, `char:tymora` | OK de primeira |
| 6 | `topic:amnian-currency` | OK de primeira |
| 7 | nenhuma | ausência tipada `NOT_KNOWN` |
| 8 | nenhuma | OK na 2ª tentativa (1ª recusada por `THIRD_PARTY:ROLE`) |

O log não guarda as falas (ADR-0107). A avaliação das respostas é a do mantenedor no jogo.

## Pendências

- **Turnos 2 e 8:** a primeira tentativa atribuiu um papel a alguém sem base (`THIRD_PARTY:ROLE`), e o verificador a recusou. As duas terminaram bem; fica a observar.
- **Lote D:** só pode ser testado no jogo com um NPC nascido ou morador da Costa da Espada. Bernard é de Tethyr e mora em Athkatla.
