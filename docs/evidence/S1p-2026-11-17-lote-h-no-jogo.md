# Evidência S1p — lote H (Terras Centrais e Mar Interior) no jogo (single player, 2026-11-17)

**Gate:** etapa 4 do plano de conhecimento (testes reais), CR-2026-027.
**Resultado:** **APROVADO no laboratório ARM64/VM**, com uma pendência do verificador anotada abaixo. Os resultados:
- Elminster e o Rei Azoun IV, no nível de Faerûn, responderam de primeira;
- as perguntas com palavras comuns ("quanto vale", "pelo mar") foram ao modelo, sem o "não sei" automático (CR-2026-027).

O mantenedor seguiu para o PR depois do teste ("Sim, nessa ordem").
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin`).

## Preparação

- **Pacote:** 147 entradas, revisão `sha256:dd158cc00b9d`, pinada à mão no ramo `br-4ee98a56c1a2`.
- **Pin levado:** ao carregar o save, o ramo novo `br-c10e8c5d3d47` recebeu a mesma revisão sozinho (CR-2026-020), sem `AVISO`.
- **Caixa e manifesto:** sem mudança (`s1j-manifest-2026-11-15e-pinned.json`).

## Turnos

Bernard, reação amistosa, com 109 assuntos no prompt (106 antes do lote H). O log não guarda as falas (ADR-0107); as perguntas 3 e 4 e as respostas vêm da captura de tela do mantenedor.

| Pergunta | Entradas | Resultado |
|---|---|---|
| Sobre Elminster | `char:elminster` | OK de primeira |
| Sobre o rei de Cormyr | `char:azoun`, `event:tuigan-horde` | OK de primeira |
| "Quanto vale uma boa espada aqui?" | `region:amn` | OK depois de uma recusa `UNBACKED_DETAIL:prata`; veja a pendência |
| "Você já viajou pelo mar?" | — | OK de primeira: "Nunca viajei pelo mar, só pelas estradas de Tethyr." |

## Pendência anotada

A resposta de preço passou com "150 a 200 golds" e "tenho uma no estoque", embora Bernard seja taverneiro.
- O verificador de metais (`UNBACKED_DETAIL`) só conhece os nomes em português; o "golds" em inglês e o número do preço escaparam.
- Não é efeito do lote H. A pergunta só chegou ao modelo por causa da CR-2026-027, e antes a resposta seria "não sei".

**Encaminhamento:**
- A correção do verificador segue numa sessão à parte.
- O mantenedor pediu uma regra nova: quem vende itens ou serviços nunca nega o que vende. Bernard, por exemplo, não pode negar a cerveja nem o quarto. Ela será proposta numa CR própria, com o que cada NPC vende tirado da loja do jogo.
