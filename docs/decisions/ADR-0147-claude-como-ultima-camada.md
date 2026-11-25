# ADR-0147 — O Claude como última camada das falas

**Estado:** APROVADA (mantenedor, 2026-11-24: "Aprovar como proposta", D1 a D5 na opção recomendada; adendo da reação, D6, aprovado no mesmo dia depois da fase 1). Fecha a parte de nuvem da DEC-006.

**Origem:** pedido do mantenedor em 2026-11-24:
- integrar o Claude pela API e testar a qualidade dos diálogos, começando pelo Haiku;
- o Claude é a última camada, depois do código e do Ollama, e refina o que os dois primeiros não atendem;
- perguntas diretas ("qual é o seu nome?") são respondidas pelo código;
- a camada segue INT e SAB:
  - baixas: código;
  - medianas: Ollama;
  - altas: Claude.

**Relaciona-se com:** DEC-006, DEC-014, DEC-059, ADR-0052, ADR-0054, ADR-0106, ADR-0117, ADR-0131 e ADR-0132.

**Gate:** etapa 1, laboratório, single player.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-24.

1. **Consentimento (DEC-006, parte de nuvem):**
   - o Claude é opcional, por campanha, ligado pelo anfitrião; desligado, nada sai da máquina;
   - a subida para a nuvem fica declarada na configuração, nunca implícita (ADR-0054);
   - a chave fica no ambiente do anfitrião (`ANTHROPIC_API_KEY`), nunca no repositório nem no chat;
   - **vai para a API:**
     - o texto de regras, a persona e o jeito de falar;
     - os fatos que o NPC pode contar, já filtrados;
     - o pedido da quest;
     - a fala do jogador e as falas anteriores da conversa;
   - **nunca vai:** saves, arquivos do jogo, o banco da campanha, os segredos que o NPC não pode contar, os livros e a chave;
   - **teto de gasto mensal (D5):** US$ 5 no laboratório, contado localmente pela resposta da API. Ao atingir o teto, as falas voltam para o Ollama;
   - hardware e modelos locais continuam abertos na DEC-006.
2. **As camadas:**
   - **perguntas simples** (nome, saudação, despedida, ofício, lugar, venda): o código responde com o que está curado, para todos os NPCs, inclusive os da camada Claude (D4);
   - **perguntas abertas (D1):**

     | Camada | Regra |
     |---|---|
     | código | INT e SAB as duas até 7: o núcleo popular de um fato que a pergunta nomeia, ou "não entendo disso" |
     | Ollama | o meio |
     | Claude | INT ou SAB a partir de 15 |

   - **a reação também escolhe a camada (D6, pedido do mantenedor depois da fase 1):**

     | Reação do NPC (ADR-0125) | Pergunta aberta |
     |---|---|
     | amistosa | Claude, mesmo com INT e SAB medianas |
     | indiferente, ou sem rolagem | pela regra de INT e SAB |
     | cautelosa, ameaçadora, hostil ou fuga | nunca Claude: Ollama, mesmo com INT ou SAB altas; fala curta e seca |

     - a camada de código fica no código: a reação amistosa não torna eloquente quem tem INT e SAB baixas;
     - companheiros não rolam reação: contam como amistosos com confiança CONFIANTE ou ÍNTIMO (ADR-0133) e como negativos com DESCONFIADO;
   - **a curadoria pode corrigir INT e SAB (D2):** a correção muda junto o nível de conhecimento (ADR-0117) e a camada. Motivo: no jogo, 15 dos 19 NPCs curados lidos têm INT 9, o padrão para figurantes;
   - **refinamento (D3):** com o Claude ligado, uma fala que o Ollama não fez passar na validação em duas tentativas sobe para o Claude, em vez de cair na frase reserva; nunca a de um NPC de reação negativa;
   - **para baixo, sempre:** sem chave, sem rede, com erro, com demora acima do limite ou no teto de gasto, responde o Ollama;
   - o pedido de quest "(agora)" segue a regra da CR-2026-033 em qualquer camada.
3. **O provedor (`dialogue/llm.py`, `AnthropicProvider`):**
   - mesmo contrato do `OllamaProvider`, com o SDK oficial `anthropic`, importado só quando o anfitrião pede o Claude;
   - modelo `claude-haiku-5-5`;
   - a primeira mensagem de sistema vira o prompt de sistema da API, marcado para o cache; as dicas de nova tentativa continuam como mensagens de sistema no meio da conversa;
   - raciocínio desligado e esforço baixo, para a fala chegar rápido;
   - a resposta usa a saída estruturada da API com o mesmo JSON (fala, fatos usados, "não sei") e passa pela mesma validação;
   - qualquer falha vira "modelo indisponível" (`LlmError`); recusa também;
   - registra os tokens de cada pedido, para o custo e o teto.
4. **Fases:**
   - **fase 1, avaliação sem jogo:**
     - a bateria ganha `--provider claude`, com tokens e custo estimado no relatório;
     - os 68 casos rodam 3 vezes no qwen3 e no Haiku;
     - `blind_sample.py` monta uma amostra cega de 15 falas para o mantenedor dar nota;
   - **fase 2, no jogo:** as respostas por código, as camadas, a correção da curadoria, o refinamento, o teto e a opção `--claude` do serviço, com evidência própria.

## Consequências

- Os NPCs mais inteligentes e sábios ganham falas mais ricas, e os demais seguem locais, sem custo.
- O jogo continua funcionando sem rede e sem chave, como hoje.
- **Fora:** o agente de quests, a persona dos NPCs, multiplayer, outros provedores de nuvem e a parte de hardware da DEC-006.

## Verificação

- **Fase 1:**
  - `tests/test_llm_provider.py`:
    - o prompt de regras vai em cache e as dicas ficam no lugar;
    - o JSON da resposta é exigido, com raciocínio desligado e sem parâmetros de amostragem;
    - qualquer falha ou recusa vira modelo indisponível;
    - os tokens somam e têm custo;
  - `tests/test_blind_sample.py`: a folha não diz qual modelo escreveu cada resposta, e a chave aponta de volta;
  - a comparação da bateria e a avaliação da amostra cega: `docs/evidence/S2h-2026-11-24-claude-na-bateria.md`.
- **Fase 2:**
  - testes da camada escolhida, das perguntas simples sem chamar modelo, da descida para o Ollama e da subida por refinamento;
  - nada vai para a API com o Claude desligado;
  - os segredos filtrados nunca aparecem no texto enviado;
  - evidência no jogo: `docs/evidence/S2i-2026-11-24-camadas-no-jogo.md`.
