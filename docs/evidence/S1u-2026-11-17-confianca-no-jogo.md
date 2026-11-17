# Evidência S1u — ADR-0133: confiança por evento no jogo (2026-11-17)

**Gate:** etapa 1, single player; ADR-0133 (fase 4b da SPEC-009), com a ADR-0126 (moral) e a ADR-0131 (divulgação).
**Resultado:** **APROVADO no laboratório ARM64/VM** (mantenedor: "De acordo").
- Uma intimidação deixou Unger `DESCONFIADO`, e ele passou a reter o que é `PROFESSIONAL`, como a arena.
- O teste achou dois defeitos, corrigidos no mesmo ramo, com testes.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin`).

## Preparação

- **Pacote:** 172 entradas, revisão `sha256:5bf7e32f2a3c`, sem mudança nesta fatia.
- **Instalação conferida:** `live matches pinned: True`.
- **Fichas:** 27 identidades curadas.
- **Serviço:** reiniciado duas vezes, uma por correção, sempre com cópia idêntica dos arquivos do ramo.

## Turnos

O log não guarda as falas (ADR-0107). As falas citadas vêm das capturas de tela do mantenedor.

| Hora (UTC) | Falante | Moral | Confiança | Retidos | Resultado |
|---|---|---|---|---|---|
| 21:18:09 | Bernard | — | `NEUTRO` | `rel:arena-slaves` (`TRUST_REQUIRED`) | OK. A arena (`PROFESSIONAL`) foi contada por quem trabalha na casa; o segredo dos escravos ficou fora do prompt |
| 21:19:51 | Unger, ameaçado | — | `NEUTRO` | — | **Defeito 1:** a ameaça não contou como intimidação. Resposta de reserva ("Disso eu não sei."), porque o modelo inventou uma origem duas vezes (`SELF_CLAIM:AWAY`) |
| 21:24:10 | Unger, a mesma ameaça | `INTIMIDATION:YIELD` (15 contra 3) | `DESCONFIADO/COERCION` | — | OK: cedeu sem contar nada do pacote |
| 21:24:37 | Unger, sobre a arena | — | `DESCONFIADO/COERCION` | a arena e a administração de Bernard | **Defeito 2:** ele falou da "Arena de Lehtinan" |
| 21:41:04 | Unger, sobre a arena | — | `DESCONFIADO/COERCION` | os mesmos | OK: a linha neutra pelo código (`ABSENCE:WITHHELD`) |

## Defeitos achados e corrigidos

1. **Imperativo informal.**
   - A intimidação (ADR-0126) só reconhecia "fale", "diga", "conte" e "responda", seguidos de "ou… te/vai".
   - "Fala logo ou vai se arrepender!" era só tom ameaçador, sem teste de moral nem mudança de confiança.
   - Correção: `personality/morale.py` aceita "fala", "diz", "conta", "responde" e "desembucha". Teste em `tests/test_morale.py`.
2. **A memória da conversa citava o assunto retido.**
   - Na etapa 3 (S1t), Unger tinha contado ao grupo sobre a arena. A linha de memória (ADR-0124) ainda dizia "Vocês falaram sobre: Arena de Lehtinan".
   - Com isso, o título retido chegava ao modelo. Como "arena" também aparecia no que ele podia dizer, a ausência tipada não respondia `WITHHELD`.
   - Correção: `dialogue/context.py` monta a memória depois da decisão por item e tira dela os títulos retidos (`recall.without_topics`). Se não sobra assunto, a linha sai inteira. Teste em `tests/test_trust.py`.

## Verificação do ramo

- Suíte: 524 testes OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 61/61, tempo médio 1.4 s, p90 1.8 s.

## O que não foi testado no jogo

- **`CONFIANTE` por convivência:** pede três sessões amistosas na mesma linha do tempo. O histórico de Bernard está espalhado por cerca de 15 ramos de saves recarregados, e o ramo atual não chega a três sessões, então `NEUTRO` está correto. A regra é coberta por `tests/test_trust.py`.

## Pendências anotadas

- **Origem de Unger:** a ficha não diz de onde ele vem, e o modelo tentou inventar duas vezes. O verificador barrou, e a fala de reserva saiu.
- **Desconfiado e cedido ao mesmo tempo:** depois de ceder à ameaça (`YIELD`), Unger segue desconfiado e retém a casa. A cessão vale para o turno; a desconfiança, para o ramo.
