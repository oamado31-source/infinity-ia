# Evidência S1o — lote G (o Norte e Águas Profundas) no jogo (single player, 2026-11-17)

**Gate:** etapa 4 do plano de conhecimento (testes reais), CR-2026-025 e CR-2026-026.
**Resultado:** **APROVADO no laboratório ARM64/VM**, depois da CR-2026-026. O mantenedor aprovou os testes ("Testes Ok").
- Drizzt, Khelben e Alustriel, conhecidos em toda Faerûn, responderam de primeira ou depois de uma recusa do verificador.
- O teste achou duas incoerências com nomes de lugares distantes. A CR-2026-026 corrigiu as duas, e as mesmas perguntas passaram no jogo, sem recusa.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin`).

## Preparação

- **Pacote:** 130 entradas, revisão `sha256:f4710be636e7`.
- **Pin:** ao carregar o save, o ramo `br-4ee98a56c1a2` recebeu sozinho a revisão pinada no ramo `br-5d5079369ceb` (CR-2026-020), sem `AVISO`. A CR-2026-026 não muda o pacote nem o pin.
- **Caixa e manifesto:** sem mudança (`s1j-manifest-2026-11-15e-pinned.json`).

## Turnos

O log não guarda as falas (ADR-0107). As perguntas abaixo foram relatadas pelo mantenedor.

### Lote G com a CR-2026-025

| Falante | Reação | Entradas | Resultado |
|---|---|---|---|
| Lorde Jierdan (3 turnos) | ameaçador | — | Retém tudo (`ABSENCE:WITHHELD`), Drizzt e Khelben incluídos; regra de reação (ADR-0125) |
| Bernard | indiferente | `char:drizzt` | OK de primeira |
| Bernard | indiferente | `char:khelben` | OK depois de uma recusa `THIRD_PARTY:TRAIT` |
| Bernard | indiferente | `char:alustriel` | OK de primeira |
| Salvanas | indiferente | — | `ABSENCE:NOT_KNOWN` ("não sei"); veja a incoerência 1 |
| Salvanas, "Mas sobre Waterdeep você sabe algo? E sobre Khelben?" | indiferente | `char:khelben` | OK de primeira |

### Primeira versão da CR-2026-026

| Falante | Entradas | Resultado |
|---|---|---|
| Salvanas, "O que sabe sobre Silvery Moon e sobre Alustriel?" | — | Reserva: `THIRD_PARTY:STRANGER` e depois `THIRD_PARTY:ROLE`; veja a incoerência 2 |
| Salvanas | `char:khelben` | OK depois de uma recusa `THIRD_PARTY:TRAIT` |

### Versão final da CR-2026-026

| Falante | Entradas | Resultado |
|---|---|---|
| Salvanas | `char:selune`, `char:alustriel` | OK de primeira |
| Salvanas | — | OK de primeira |
| Salvanas | — | OK de primeira |
| Salvanas | `char:khelben` | OK de primeira |

Salvanas e Bernard tinham 106 assuntos no prompt; Jierdan, 105.

## Incoerências achadas e corrigidas (CR-2026-026)

1. **Águas Profundas.** Salvanas mora em Athkatla e não tem as entradas do Norte, que não é vizinho de Amn. Ele dizia "não sei" sobre a cidade, mas sabia que Khelben é "o arquimago de Águas Profundas".
   - **Correção:** a pergunta pelo nome inteiro de uma entrada não tida traz as entradas tidas cuja camada popular cita esse nome.
2. **Silvery Moon.** O nome em inglês e em duas palavras não ligava Alustriel a Lua Prateada. O verificador recusou as tentativas que faziam essa ligação, e a resposta caiu na reserva.
   - **Correção:** as palavras seguidas valem também juntas, os nomes de um título são o mesmo lugar, e uma linha tirada do título diz isso no prompt. O "não sei" automático só vale quando a pergunta é toda sobre o que a pessoa não sabe.

## Pendências anotadas

- **Enfeite de lugar distante.** Na bateria, perguntado sobre Waterdeep, o modelo às vezes descreve a cidade com o que não sabe ("o lugar mais rico da Costa da Espada"). O verificador recusa (`THIRD_PARTY:TRAIT`), e em 2 de 8 rodadas a resposta caiu na reserva. É o lado seguro.
- **"cidade" e Dez Cidades.** Para quem tem a entrada de Dez Cidades (Ten-Towns), a palavra "cidade" nomeia essa entrada (CR-2026-016). Isso só reordena o prompt e não muda a resposta.
