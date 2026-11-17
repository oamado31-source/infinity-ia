# Evidência S1n — lote F (organizações e vilões) no jogo (single player, 2026-11-17)

**Gate:** etapa 4 do plano de conhecimento (testes reais), CR-2026-023.
**Resultado:** **APROVADO no laboratório ARM64/VM.** Os resultados:
- todas as perguntas passaram de primeira, sem nenhuma recusa;
- a organização local (a Ordem do Coração Radiante) e os Magos Encapuzados continuaram no prompt;
- as organizações distantes subiram quando a pergunta as nomeou, inclusive pelo nome em inglês ("Red Wizards").

O mantenedor aprovou os testes ("Testes Ok").
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin`).

## Preparação

- **Pacote:** 118 entradas, revisão `sha256:5f880434d680`.
- **Pin:** ao carregar o save, o ramo `br-5d5079369ceb` recebeu sozinho a revisão já pinada (CR-2026-020), sem `AVISO`.
- **Caixa e manifesto:** sem mudança (`s1j-manifest-2026-11-15e-pinned.json`).

## Turnos

| Falante | Entradas usadas | Resultado |
|---|---|---|
| Salvanas | `org:order-of-the-radiant-heart` | OK de primeira |
| Salvanas | `org:cowled-wizards` | OK de primeira |
| Salvanas | `org:harpers`, `org:cowled-wizards` | OK de primeira |
| Salvanas | `org:zhentarim`, `region:faerun` | OK de primeira |
| Salvanas | `char:szass-tam` | OK de primeira |
| Salvanas | `org:red-wizards` | OK de primeira |
| Salvanas | `org:iron-throne`, `region:amn` | OK de primeira |
| Salvanas | `org:lords-alliance`, `event:coast-plague` | OK de primeira |
| Bernard | `org:lords-alliance`, `event:coast-plague` | OK de primeira |

Salvanas tinha 97 assuntos no prompt e Bernard, 99. O log não guarda as falas (ADR-0107); a avaliação das respostas é a do mantenedor no jogo.

## Pendência anotada

O caso `sem-staff-trabalho` da bateria é instável também em main. Numa rodada, "Trabalho na Coroa de Cobre, sim." passou sem recusa, o que é uma brecha no verificador de afirmações sobre si (`SELF_CLAIM:WORK`). Não é efeito do lote F.
