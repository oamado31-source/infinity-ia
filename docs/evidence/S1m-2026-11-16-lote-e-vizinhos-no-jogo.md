# Evidência S1m — lote E, reinos vizinhos e nomes já ditos, no jogo (single player, 2026-11-16)

**Gate:** etapa 4 do plano de conhecimento (testes reais), CR-2026-021 e CR-2026-022.
**Resultado:** **APROVADO no laboratório ARM64/VM.** Bernard (de Tethyr, morador de Athkatla) respondeu sobre:
- a terra natal: a rainha Zaranda e Darromar;
- o reino vizinho: Calimshan;
- a Costa da Espada, vizinha de Amn: a Fortaleza da Vela;
- as terras distantes: Halruaa e Lantan;
- o Império Shoon.

O teste revelou duas falhas, que foram corrigidas e confirmadas no jogo.
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin`).

## Preparação

- **Pacote:** 108 entradas. As revisões foram `sha256:8869ae60cbdd` e, depois do novo título de Zaranda, `sha256:45d8fcfa6127`.
- **Vizinhos** (`realm_neighbors`): Amn–Tethyr, Amn–Costa da Espada, Tethyr–Calimshan e Amn–Calimshan.
- **Caixa e manifesto:** sem mudança (`s1j-manifest-2026-11-15e-pinned.json`).

## Turnos (Bernard, reação amistosa, 89 assuntos)

| Pergunta | Entradas usadas | Resultado |
|---|---|---|
| A rainha Zaranda | `char:zaranda` | OK de primeira |
| Darromar (seguimento) | nenhuma | **FALLBACK**: `UNKNOWN_NAMES:Zaranda` duas vezes |
| Calimshan | `region:calimshan` (vizinho) | OK de primeira |
| Fortaleza da Vela | `place:candlekeep` (vizinho de Amn) | OK de primeira |
| Halruaa | `topic:far-lands-renown` | OK de primeira |
| Lantan | `topic:far-lands-renown` | OK de primeira |
| Império Shoon | `event:shoon-imperium`, `region:tethyr` | OK de primeira |

## Achados e correções

| Achado no jogo | Causa | Correção |
|---|---|---|
| "E Darromar?" caiu na fala de reserva | o verificador só aceitava nomes das entradas do prompt daquela pergunta, e "Zaranda", que o próprio Bernard tinha dito no turno anterior, não estava | CR-2026-022: os nomes que o NPC já disse na conversa contam como conhecidos |
| "Quem é a rainha de Tethyr?": "Tethyr não tem rainha há anos [...] não sei quem é" | a busca pela pergunta usa o título, que era só "Zaranda". A entrada dela não foi ao prompt, e o modelo inventou | o título passou a ser "Rainha Zaranda", que é como o jogo a chama |

## Confirmação

Depois das duas correções, na mesma conversa:
- "Quem é a rainha de Tethyr?" usou `char:zaranda` e `event:tethyr-reclamation-wars-end`, de primeira;
- "E Darromar?" usou `region:darromar` e `char:zaranda`, de primeira;
- o mantenedor confirmou as respostas na tela.

**Bateria:** 35/35, com quatro casos novos:
- `reino-vizinho-pela-pergunta` (CR-2026-021);
- `terra-distante-pela-pergunta` (tópico das terras distantes);
- `nome-ja-dito-na-conversa` (CR-2026-022);
- `rainha-sem-o-nome`, que falha 0/3 com o título antigo e passa 3/3 com o novo.
