# Evidência S1s — lote J (história antiga) no jogo (single player, 2026-11-17)

**Gate:** etapa 4 do plano de conhecimento (testes reais).
**Resultado:** **APROVADO no laboratório ARM64/VM** (mantenedor: "Tudo ok, aprovado"). Bernard respondeu de primeira, sem recusa, sobre a origem dos drows, a Contagem dos Vales e as Guerras da Coroa. Perguntado sobre Ahghairon, disse que não sabe, como decidido em D1.
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço no Mac, `--voice --carry-pin`).

## Preparação

- **Pacote:** 170 entradas, revisão `sha256:9f0d517e423e`, pinada à mão no ramo `br-c10e8c5d3d47`.
- **Pin levado:** ao carregar o save, o ramo `br-b582292d42f5` recebeu sozinho a mesma revisão (CR-2026-020), sem `AVISO`.
- **Caixa e manifesto:** sem mudança (`s1j-manifest-2026-11-15e-pinned.json`).

## Incidentes do laboratório (não são do lote)

- **A VM foi fechada no meio do teste.** O serviço registrou `leitura do log falhou: RemoteShellError`. Quando o SSH voltou, no mesmo IP, o serviço foi reiniciado e a instalação conferiu com o manifesto pinado.
- **Dois jogos abertos:** depois de reabrir a VM, havia dois `Baldur.exe`, o antigo da sessão anterior e o novo. O antigo foi fechado, com o aval do mantenedor.
- **Colar na caixa não funcionava:** o texto colado era maior do que o campo aceita. A caixa corta o que envia em 500 caracteres (`INFAI_TALK_MAX_TEXT`).

## Turnos

Bernard, reação amistosa, com 118 assuntos no prompt (112 antes do lote J). O log não guarda as falas (ADR-0107).

| Pergunta | Entradas | Resultado |
|---|---|---|
| A origem dos drows | `event:descent-of-the-drow` | OK de primeira |
| A Contagem dos Vales | `event:standing-stone` | OK de primeira: o título com os dois nomes achou a entrada |
| As Guerras da Coroa | `event:crown-wars`, `event:dragonspear-war`, `event:murann-spice-war` | OK de primeira. A palavra "Guerra" dos títulos trouxe outras guerras ao prompt. |
| Ahghairon (2 turnos) | — | `ABSENCE:NOT_KNOWN`, o esperado: Ahghairon é do nível de Águas Profundas (D1) |

## Ajustes feitos antes do teste (depois da aprovação)

- **`event:jhaamdath`:** o título "Jhaamdath e as Doze Cidades da Espada" virou "Jhaamdath", porque a palavra comum "Cidades" puxava a entrada em qualquer pergunta com "cidade".
- **`event:standing-stone`:** o título passou a nomear também a Contagem dos Vales, porque a pergunta "Por que contamos os anos pela Contagem dos Vales?" não achava a entrada.

## Pendência anotada

Títulos de eventos com palavras comuns ("Guerra", "Coroa", "Pedra") trazem outras entradas para o prompt quando a pergunta usa essas palavras. Isso só reordena o prompt e não leva ao "não sei" (CR-2026-027), mas pode tirar o foco da resposta.
