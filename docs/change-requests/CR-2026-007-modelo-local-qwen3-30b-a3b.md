# CR-2026-007 — Modelo local padrão passa a ser o qwen3:30b-a3b

**Status:** APPROVED (mantenedor, 2026-11-14)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-14

## Motivo e contexto

**Pesquisa (2026-11-13):** jogos com NPCs por IA usam modelos pequenos por causa da memória de vídeo disputada com o jogo (NVIDIA ACE: 0,5B a 8B), e os mods de Skyrim usam ajustes finos de 7B/8B em inglês ou a nuvem. Nenhum publica comparação em português nem para regras de conhecimento como as nossas. A medida confiável é o nosso conjunto de testes de fala.

**Comparação** (20 casos x 3 rodadas, M1 Max 64 GB, mesmo validador):

| | qwen3:8b | qwen3:30b-a3b |
|---|---|---|
| Casos | 20/20 | 20/20 |
| Tempo médio por resposta | 1,8 s | 1,1 s |
| p90 | 3,9 s | 2,5 s |
| Memória do modelo | 5,2 GB | 18 GB |

O 30b-a3b ativa cerca de 3B parâmetros por palavra, por isso é mais rápido apesar de maior. Responde à pergunta feita com mais contexto ("Moro em Amn, não aqui. Estou de passagem.") e deixou de copiar o exemplo da regra 8 ("Isso não é da sua conta"). No laboratório (`lab-s1f`, 2026-11-14), seis falas na caixa do jogo, cobrindo pergunta sobre terceiro, suborno, traição e intimidação, saíram sem erro; o mantenedor avaliou que a qualidade das respostas melhorou muito.

**Achados que entram junto:**

- **Traço com o sujeito omitido:** o 30b-a3b disse "Lehtinan? Dono da taverna. Não fala muito, mas é bom com os clientes." O ADR-0121 só pegava traço com o nome na mesma oração.
- **Eco da pergunta:** na conversa em andamento, o 30b-a3b às vezes devolve a própria pergunta do jogador ("E quem é então?").
- **Intimidação sem desconto:** uma ameaça cujas palavras não estavam nas regras de conduta ("Conte ou te machuco") não recebia o −4 de NPC maltratado (Tabela 50).

**Decisão do mantenedor:** adotar o qwen3:30b-a3b como padrão e corrigir os três achados.

## DEC/ADR/SPEC/REQ afetados

- SPEC-004, fluxo item 6 (modelo local).
- ADR-0121 (afirmações sobre terceiros): ampliado por este CR; o ADR permanece inalterado.
- ADR-0126 (teste de moral): intimidação sempre conta como maltrato; o ADR permanece inalterado.

## Diff proposto e impacto no comportamento

- **Modelo padrão** `qwen3:30b-a3b` em `OllamaProvider`, `dialogue_service.py --model` e `run_eval.py --model`. O `qwen3:8b` continua aceito com `--model`.
- **Testes de fala:** cada resposta é cronometrada (com as novas tentativas); um pedido de aquecimento carrega o modelo antes e não conta; opção `--timeout`; o relatório JSON traz `seconds` por rodada e `mean_seconds` por caso. O caso `viajante-nao-mora` passa a aceitar "Não moro aqui" (antes reprovava pela substring).
- **`THIRD_PARTY:TRAIT`** (`dialogue/claims.py`): também numa oração sem sujeito ("Não fala muito", "Ele bebe demais", "mas é avarento"). O sujeito é o último nome conhecido da frase ou das duas anteriores, exceto nome depois de preposição ("Moro em Athkatla. É bom aqui." passa). Verbos de hábito em lista curta escrita por nós; com "é/era", só adjetivos de traço de uma lista nossa. Opinião ("Acho que é avarento") e conselho ("Fala com ele") passam.
- **Eco** (`dialogue/validate.py`): resposta igual à fala do jogador, ou quase igual (semelhança ≥ 0,9 nas palavras), é recusada com o motivo `ECHO`; a nova tentativa explica em português que deve responder à pergunta.
- **Moral** (`personality/morale.py`): gatilho `INTIMIDATION` aplica sempre o −4 de maltratado. **Conduta** (`personality/reaction.py`): "te machuco", "vou te ferir", "te quebro", "corto sua" contam como ameaça.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Memória:** 18 GB em vez de 5,2 GB. Cabe com folga numa máquina de 64 GB; numa de 16 GB, use `--model qwen3:8b`.
- **Mais segundas tentativas:** o 30b-a3b arrisca mais traços; o validador recusa e às vezes a fala cai na reserva (3 de 60 respostas na bateria).
- **Licença:** Qwen3 sob Apache-2.0, baixado pelo Ollama fora do repositório. Nenhum dado do jogo entra no repositório.

## Migração e rollback

Instalar o modelo: `ollama pull qwen3:30b-a3b` (cerca de 19 GB). Rollback: `--model qwen3:8b` no serviço e nos testes, ou voltar o padrão no código.
