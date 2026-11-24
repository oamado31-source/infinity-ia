# CR-2026-033 — O pedido da quest em primeiro e o jeito de falar curado

**Estado:** APROVADA (mantenedor, 2026-11-24: "Aprovar como proposta", D1 a D4 na opção recomendada).

**Origem:** o teste no jogo da quest "O diário perdido de Sarevok" (ADR-0144), em 2026-11-24.
- **O pedido sumia atrás de um fato fixo.** "Para que você precisa de ajuda?" disparou a oferta, mas Garoll respondeu duas vezes com o fato fixo dele ("Só quero que paguem uma bebida"). A regra 8 do diálogo manda usar só o fato que responde à pergunta, e o modelo achou que a bebida também respondia.
- **Garoll não falava como bêbado.** A voz dele no jogo soluça e ri, e a fala na caixa saía sóbria. O jeito de falar vinha só da Sabedoria (ADR-0117).

**Relaciona-se com:** SPEC-011, ADR-0117, ADR-0144 e a curadoria de identidade (etapa 3).

## Mudança

1. **O fato da quest em primeiro (D1):**
   - só o que uma mudança da quest fez **nesta fala** fica marcado com `(agora)`: a oferta, o aceite, um passo cumprido, a entrega. O que a pessoa continua dizendo (a espera, um passo já contado, a quest resolvida) entra como fato comum (`QuestTurn.fresh`);
   - os fatos marcados vêm primeiro em FATOS, e uma regra diz: "Um fato marcado (agora) é o assunto desta fala e precisa aparecer nela, mesmo que a pergunta seja sobre outra coisa: diga-o antes de qualquer outro fato.";
   - uma resposta válida que deixa de fora o fato marcado é pedida mais uma vez (`QUEST_FACT_MISSING`). Se a segunda não for melhor, vale a primeira, nunca a resposta de recurso;
   - sem fato marcado, o texto enviado ao modelo não muda.
2. **O jeito de falar curado (D2):**
   - a curadoria de identidade ganha o campo opcional `speech` (até 200 caracteres), conferido pelo mantenedor; curadoria com `speech` inválido não carrega;
   - ele entra logo depois da linha de estilo: "Seu jeito de falar: …. Mostre esse jeito na própria escrita da frase, sem asteriscos, parênteses nem rubricas; ele é só forma: não acrescenta fato nenhum e não deixa de fora o fato marcado (agora).";
   - **achados na bateria:**
     - no meio da descrição da pessoa, o jeito era ignorado; na linha de estilo, passou a ser seguido;
     - com `*hic*` o validador recusava a fala (`MARKUP`);
     - um exemplo de som na instrução ("hic, rá") fez Tamoko soluçar; a instrução ficou sem exemplo.
3. **As pessoas da quest (D3 e teste de 2026-11-24):**
   - **Garoll:** "bêbado: arrasta e enrola as palavras, solta um hic ou um arroto no meio da frase, ri à toa (rá, rá) e às vezes repete uma palavra" (o texto aprovado, sem asteriscos);
   - **Tamoko:**
     - "visão de uma clériga morta de Kara-Tur: fala baixo, pausado e solene, frases que se perdem em reticências, tom de lamento e saudade, às vezes repete uma palavra como um eco";
     - o fato 2 dela passa a dizer só onde ela vaga ("À noite, sua visão vaga perto de um túmulo sem nome no cemitério de Athkatla."). O texto anterior ("não sabe como nem onde morreu") competia com o passo `visao`, e ela chegou a inventar "morri aqui".
4. **Bateria (D4):**
   - `garoll-pedido-da-quest-em-primeiro`: "Para que você precisa de ajuda?" fala do fantasma, não da bebida;
   - `garoll-fala-como-bebado`: "Onde você trabalha?" responde com o fato de coveiro, no jeito de bêbado;
   - `tamoko-conta-na-visao`: a pergunta de duas partes do jogo ("Quem é você? Por que assombra esse local?") tem de trazer o fato da visão, sem "morri aqui";
   - um caso pode dizer `quest_told: true` (o fato só lembrado). O de Bernard depois do broche passou a usar isso: lá, o fato da quest é lembrança e não pode tomar a fala sobre a arena.

## Motivo

O que a quest entrega é decidido pelo código naquela fala e precisa chegar ao jogador. O jeito de falar é parte da pessoa, como a voz do jogo, e não pode trazer fatos.

## Diff

- `src/infinity_ai/quests/narrative.py`: `QuestTurn.fresh`, os fatos que uma mudança fez nesta fala;
- `src/infinity_ai/dialogue/engine.py`: a marca `(agora)`, a ordem, a regra condicional, a segunda tentativa e a linha do jeito de falar;
- `tools/windows-lab/dialogue_service.py`: passa os fatos novos (`quest_now`);
- `src/infinity_ai/dialogue/context.py`: `speech` no contexto;
- `src/infinity_ai/personality/identity.py`: `speech` na curadoria e na identidade (`MAX_SPEECH = 200`);
- `src/infinity_ai/dialogue/evaluation.py`: `speech` nos casos da bateria;
- `knowledge/npcs/drunk1.pt_BR.json` e `knowledge/npcs/tamoko.pt_BR.json`: os jeitos de falar e o fato 2 de Tamoko;
- `tests/test_quest_line_and_speech.py` e os dois casos novos da bateria.

## Rollback

Remover a marca e a regra do `engine.py` e o campo `speech`; as curadorias com `speech` voltam a carregar sem ele.

## Verificação

- Suíte OK (642 testes); `pyflakes` sem avisos.
- Bateria: 66/67 na rodada completa. Os casos de quest e de jeito de falar, repetidos 3 vezes: 3/3 cada.
- `tamoko-conta-na-visao` é o mais difícil. Depois do fato 2 novo, 4 de 6 respostas citam o Trono de Ferro, Gregor ou a morte; as outras falam só do diário.
- **No jogo:** junto com a evidência da quest.
