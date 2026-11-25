# Evidência S2h — ADR-0147, fase 1: o Claude Haiku 5.5 na bateria de diálogo (2026-11-24)

**Gate:** etapa 1, sem jogo: a bateria fixa de diálogo e uma amostra cega.
**Resultado:** **aprovado.** O Haiku passou nos mesmos 68 casos que o qwen3 local, com falas mais completas na avaliação do mantenedor, e por US$ 0,03 nas 204 falas.

**Executado por:** Claude Code (`run_eval.py --runs 3`, nos dois provedores; `blind_sample.py`) e mantenedor (avaliação da amostra cega).

## Como

- **Os dois modelos:**
  - `qwen3:30b-a3b` no Ollama local, como o serviço do laboratório;
  - `claude-haiku-5-5` pela API, pelo `AnthropicProvider`: raciocínio desligado, esforço baixo, prompt de regras em cache e saída estruturada com o JSON de sempre.
- **A chave:** fica no ambiente do anfitrião (`~/.zshenv`, só o dono lê), digitada pelo mantenedor no próprio terminal, nunca no chat.
- **Os relatórios** ficam fora do repositório, em `~/.infinity-ai/dialogue-eval/`: `20261124T235325Z.json` (qwen3) e `20261125T000009Z.json` (Haiku).

## A bateria

| | qwen3 (local) | Haiku 5.5 (API) |
|---|---|---|
| Casos aprovados | 68/68 | 68/68 |
| Rodadas aprovadas | 201/204 | 202/204 |
| Casos com as 3 rodadas certas | 65 | 66 |
| Frase reserva | 5 | 2 |
| Falas com nova tentativa | 14 | 15 |
| Tempo médio / p90 / pior | 1,5 s / 2,4 s / 28,0 s | 1,4 s / 2,0 s / 3,4 s |
| Tamanho médio da fala | 73 caracteres | 131 caracteres |
| Custo | US$ 0 | US$ 0,0306 |

**Tokens do Haiku em 201 pedidos:**
- 364.787 lidos do cache, 133.364 gravados no cache e 5.809 sem cache;
- 19.350 de saída.

**Leituras:**
- o cache cobriu 73% da entrada; uma fala sai por cerca de US$ 0,00015;
- as regras seguram os dois igualmente: as novas tentativas acontecem quase o mesmo número de vezes;
- o Haiku caiu menos vezes na frase reserva, e o tempo dele é estável.

## A amostra cega

- 15 perguntas sorteadas (semente 1) e, em cada uma, a primeira resposta de cada modelo, em ordem sorteada.
- A folha não dizia o modelo; a chave ficou fora do repositório.
- **Avaliação do mantenedor:** "as respostas ficam muito mais completas e bem elaboradas" no Haiku.
- **A chave, revelada depois:** nas 15 perguntas, a resposta mais longa e elaborada era a do Haiku, que estava em 1 em oito delas e em 2 nas outras sete.
- **Limite:** a bateria quase só tem NPCs de SAB e INT 9, que pela regra das camadas ficam no Ollama. A diferença nos NPCs da camada Claude será vista no jogo, na fase 2.

## Decisão que saiu daqui

O mantenedor pediu que a reação também escolha a camada (adendo D6 da ADR-0147):
- a reação amistosa fala pelo Claude;
- a reação negativa nunca vai para o Claude e fala curto, pelo Ollama.

## Verificação do ramo

- Suíte OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Testes novos: `tests/test_llm_provider.py` (pedido ao Claude) e `tests/test_blind_sample.py` (folha cega).
