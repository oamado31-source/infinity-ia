# CR-2026-037 — O NPC não inventa o que aconteceu antes

**Estado:** APROVADA (mantenedor, 2026-11-27: "Aprovar como proposta", D1 a D4 na opção recomendada). **Revista** no mesmo dia, depois da medição ("Checagem no código"): D1 e D3 saíram e entrou a D5.

**Origem:** achado da evidência S2o. Neste save o broche estava só oferecido, mas Bernard disse "já resolvemos o problema do broche". Tínhamos anotado: "a memória das conversas parece não respeitar a linha do save".

**Relaciona-se com:** ADR-0121 (o que se afirma sobre outra pessoa), ADR-0124 (memória das conversas), SPEC-003 (ramos e saves), SPEC-011 (quests narrativas), CR-2026-033 (fatos da quest na fala) e CR-2026-036 (oferta em foco).

## O que a investigação mostrou

**A memória respeitou a linha do save.** O ramo da sessão da S2o foi conferido no banco, só para leitura:

| O que o serviço sabia | Valor | Bate com o save? |
|---|---|---|
| Estado do broche | `OFERECIDA` (oferta de 18/11, num ramo ancestral) | sim |
| Broche resolvido | o `NarrativeQuestResolved` está num ramo **irmão**, de 18/11: não visível | sim |
| Marco "broche resolvido" | `marcos=[]`, confiança `NEUTRO` | sim |
| Lembranças de Bernard (`lembra=4`) | 4 conversas em ramos ancestrais (18/11 e 23/11), nenhuma sobre o broche, sem assuntos | sim |

**De onde veio a frase:**
- a fala saiu do modelo local (`qwen3:30b-a3b`);
- para o broche, o contexto levava só o fato da oferta;
- das conversas anteriores, levava só "Você já conversou com o jogador antes (4 vezes…)", sem assunto;
- o "já resolvemos" foi invenção do modelo.

**Um limite da regra dos ramos (D4, só registrado):**
- o serviço não sabe qual save foi carregado e deduz a linha pelo tempo de jogo (SPEC-003);
- um save mais adiante no tempo continua o ramo ativo, mesmo que tenha vindo de outra jogada;
- neste caso a dedução acertou.

## A medição

**Caso novo na bateria de diálogo:** `bernard-oferece-o-broche-com-lembranca`.
- Bernard com a oferta do broche já contada antes, e 4 conversas anteriores sem assunto.
- A pergunta é "Tem trabalho para nós?".
- A bateria ganhou o campo `recall`, com as conversas anteriores como o serviço as dá.

**Resultado:**
- O "broche resolvido" não se repetiu em 40 rodadas.
- Apareceu o mesmo tipo de erro, um passado inventado: "Já falei com Yarin, mas ele não quer falar".
- A invenção nasce do próprio fato da oferta ("quer que o grupo pergunte a Yarin").

| Versão (modelo local, 30 rodadas) | Passado inventado na fala final | Outros problemas |
|---|---|---|
| Antes da correção | 2 | — |
| D1 (linha de estado da quest) + D3 (regra no prompt) | 2 a 5, conforme a redação | a linha de estado foi repetida na fala (2) |
| **D2 + D5 (esta CR)** | **0** (a checagem pegou 1, e a nova tentativa corrigiu) | — |

## Mudança

1. **A lembrança sem assunto (D2, `src/infinity_ai/dialogue/recall.py`):**
   - **antes:** "Você já conversou com o jogador antes (4 vezes, a última há 3 dias).";
   - **agora:** "…(4 vezes, a última há 3 dias), sem nada que tenha ficado marcado.";
   - com assunto registrado, a linha "Vocês falaram sobre: …" continua como antes.
2. **A checagem do contato passado (D5):**
   - **Onde:** `past_contact_claim`, em `src/infinity_ai/dialogue/claims.py`, chamada por `validate_reply`.
   - **O que pega:** o NPC dizer que já teve contato com uma pessoa nomeada: "já falei com Yarin", "já perguntei ao Yarin", "já conversei com o Yarin", "já mandei…". Isso só vale se um texto que ele sabe nomear a pessoa com um verbo de contato.
   - **Sem isso:** a fala volta ao modelo uma vez (`PAST_CONTACT:<nome>`), com a dica: "você disse que já falou ou tratou com Yarin, e isso não está no que você sabe…".
   - **O que passa:**
     - pedir o contato ("perguntem a Yarin");
     - falar com o grupo ("já falei com vocês");
     - falar **de** alguém ("já falei de Zaranda");
     - o contato que está nos fatos;
     - o próprio nome.
   - **O que não pega:** o mesmo dito sem "já", ou com pronome no lugar do nome. A checagem estreita a invenção, não prova a verdade, como as outras do ADR-0121.
3. **D1 e D3 saíram:** a linha de estado da quest e a regra no prompt não reduziram a invenção na medição.

4. **Unger no lugar de Yarin na quest do broche (`knowledge/quests/bernard-brooch.pt_BR.json`):**
   - **Motivo:** no teste no jogo, o mantenedor não achou Yarin: "Não sei onde está Yarin, mude o NPC".
   - **Onde fica cada um** (censo da instalação):
     - Yarin fica no canto de cima do mapa, a cerca de 725 px de Bernard;
     - **Unger Colinaescura** (`npc:scdur`) bebe ao lado do balcão, a 166 px de Bernard, o dia todo.
   - Ele é frequentador curado da casa e "prefere observar a falar", então é quem viu o furto.
   - **O que mudou:**
     - o passo virou `ask-unger`;
     - a oferta, a espera, o fato do passo, a entrega e as linhas do diário falam de Unger;
     - nas palavras da entrega, "yarin" virou "unger";
     - a curadoria registra o pedido.
   - **No jogo, a primeira oferta juntou as duas pessoas:** Bernard chamou Unger de "o batedor de carteiras novato". No fato da oferta, o suspeito vinha logo antes do nome dele.
     - A oferta foi reescrita: primeiro o ladrão desconhecido, depois Unger, "um freguês antigo e honesto".
     - A bateria ganhou a checagem dessa mistura: nenhuma das 30 rodadas misturou.
   - O resto da quest não muda.
5. **Um teste da CR-2026-036 corrigido (`tests/test_state_store.py`):**
   - **O defeito:** a "gravação que espera" segurava a trava numa thread com a conexão de outra thread. O SQLite recusava a conexão, a trava nunca era segurada, e o teste passava sem testar a espera.
   - **A correção:** a thread abre a própria conexão, e o teste confere que a outra gravação esperou de fato (mais de 0,5 s).

**O que não muda:**
- a regra dos ramos e a memória (ADR-0124);
- a oferta em foco (CR-2026-036);
- nenhum texto do jogador é gravado.

## Verificação

- **`tests/test_conversation_recall.py`:** a lembrança sem assunto ganha o complemento; com assunto, não muda.
- **`tests/test_third_party.py`:**
  - o contato inventado é recusado, com a dica;
  - o pedido de contato, falar com o grupo e falar de alguém passam;
  - o contato que está nos fatos passa, e o próprio nome também.
- **`tests/test_dialogue_eval.py`:**
  - o campo `recall` errado é recusado;
  - o caso novo leva a lembrança ao prompt.
- **`tests/test_narrative_quests.py` e testes de quest:** o passo do broche agora é de Unger (`ask-unger`, `npc:scdur`).
- **Bateria de diálogo:**
  - o caso novo passa 30 de 30;
  - a bateria inteira passa 70 de 70, antes e depois da troca por Unger;
  - com Unger, os quatro casos do broche passam 10 de 10, inclusive `unger-conta-do-batedor`, que substitui o de Yarin.
- **No jogo:** evidência S2p, aprovada.
  - Bernard com o broche oferecido, num save com conversas anteriores: ele oferece o trabalho, manda falar com Unger e não diz que está feito.
  - Unger, perguntado sobre o broche, conta o que viu.

## Rollback

Reverter o PR:
- a lembrança sem assunto volta à linha curta;
- a fala com contato inventado volta a passar;
- a quest do broche volta a mandar falar com Yarin.
