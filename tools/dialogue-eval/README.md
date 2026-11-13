# Testes de fala com o modelo local

Conjunto fixo de perguntas com o comportamento esperado de cada NPC, para pegar regressões de prompt, validador ou contexto sem precisar jogar. Os casos foram tirados dos laboratórios S1e–S1g.

## Como rodar

Com o Ollama local no ar e o modelo `qwen3:8b` instalado (o comando nunca encerra nem reinicia o Ollama):

```bash
.venv/bin/python tools/dialogue-eval/run_eval.py
```

- **Opções:**
  - `--case <id>`: roda só um caso (pode repetir);
  - `--runs N`: número de rodadas (padrão 3);
  - `--model`;
  - `--ollama-url`.
- **Tempo:** cerca de 1 minuto para os 13 casos.
- **Resultado:** o comando sai com erro (código 1) se algum caso não passar. Rode antes de abrir um PR que mexa em prompt, validador ou contexto.

## Como ler

Cada linha mostra:
- o caso;
- os acertos (por exemplo `2/3`);
- quantas rodadas caíram na fala de reserva;
- as recusas do validador, como `SELF_CLAIM:WORK` ou `THIRD_PARTY:ROLE`.

Quando um caso falha, aparecem também o motivo e a fala de cada rodada errada.

O relatório completo, com todas as falas, fica em `~/.infinity-ai/dialogue-eval/<data>.json`, fora do repositório.

## Como escrever um caso

Em `tests/dialogue_eval/cases.pt_BR.json`, cada caso tem:
- **`speaker`:**
  - `kind`: `resident` ou `companion`;
  - `npc_id`, `name`;
  - `wis` e `int`;
  - `standing` e `origin`;
  - `occupation`, `self_facts` e `affiliations`;
  - `knows`: entradas ouvidas por INQUIRY;
  - `party`;
- **`history`:** turnos anteriores, como `[pergunta, resposta]`;
- **`question`**;
- **`checks`:**
  - `status`: permitidos;
  - `uses`: entradas;
  - `mentions_any` e `mentions_none`;
  - `unknown`;
  - `max_chars`;
  - `not_copy_of`: semelhança com a camada popular abaixo de 0,85;
  - `first_try`.

O contexto é montado com o mesmo código do serviço: identidade, estatuto, conhecimento regional e relacional, camada de Sabedoria/Inteligência e memória da conversa. O CI (`tests/test_dialogue_eval.py`) confere a forma dos casos e o verificador com um modelo falso.
