# ADR-0146 — Uma área nossa e a passagem para ela

**Estado:** APROVADA (mantenedor, 2026-11-24: "Aprovar como proposta", D1 a D3 na opção recomendada). Fase 2 da CR-2026-034.

**Origem:** a fase 1 da CR-2026-034, aprovada em 2026-11-24.
- Nenhum mod com área de navio tem licença aberta (o Dark Tidings é "todos os direitos reservados").
- A fase 1 apontou três salas do próprio BG2 como interiores de navio (AR0310, AR0515 e AR1607), pela tripulação de cada uma.
- O esconderijo de Kalessia é uma **cópia da AR0310** como área nossa, `IA0001`.
- **Achado no teste:** a AR0310 não é um porão de navio, como a fase 1 supôs pela tripulação de piratas, mas uma **caverna** (o mantenedor viu no jogo). As outras duas candidatas também não são porões: a AR0515 é um quarto de hospedaria, e a AR1607, o convés de um navio em alto-mar. O mantenedor decidiu manter a caverna como **uma caverna sob o Farol das Docas**.
- A entrada fica **ao pé do Farol das Docas** (o ponto (3832, 3210), lido no jogo), sem porta nem passagem do jogo ali; o Farol facilita achar o lugar.

**Relaciona-se com:** CR-2026-030, CR-2026-032, CR-2026-034, ADR-0136, ADR-0144 e ADR-0145.

**Gate:** etapa 1, single player, save descartável.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-24.

1. **A área nossa** (`src/infinity_ai/actions/areas.py`, `tools/windows-lab/build_area.py`):
   - copia da build o `ARE`, o `WED`, o `MOS` e os três `BMP` da sala com o nome nosso (`IA` e quatro dígitos); o `WED` continua apontando para o desenho original (`AR0310.TIS`), que não é copiado;
   - no `ARE` nosso nada do jogo age:
     - sem criaturas, sem pontos de surgimento e sem script de área;
     - sem baús (nenhum item do jogo copiado);
     - sem as passagens do jogo (a saída para a taverna some);
   - grava só no override do laboratório, com o jogo fechado; recusa nome que não seja nosso.
2. **As passagens (operação `TRAVEL`, D1 e D3):**
   - a quest declara `passages`: área e ponto de origem, área e ponto de chegada, direção e os passos depois dos quais abre. Só de ou para uma área nossa, nunca entre duas áreas do jogo;
   - o serviço grava o **plano de passagens** (`INFAIDOR.lua`), validado pelo gateway, com as passagens que a quest já abriu;
   - o módulo lê o plano ao carregar a área (e a cada 5 s). Com o líder **parado a até 60 px do ponto por 1 s**, sem inimigo vivo na área, leva o grupo pela ação do próprio jogo `LeaveAreaLUA` (do `INSTANT.IDS`, de modelo fixo), um membro por vez, na hora;
   - uma passagem só volta a valer depois de o líder sair do ponto, para não voltar ao chegar;
   - na quest: o **Farol** (Docas → caverna) e a **saída da caverna** (caverna → Farol), abertos depois de `gregor-conta`.
3. **O ponto do Farol (D2):** `lab_action.py where` lê onde o líder está (operação `WHERE`, só leitura) para escrever o ponto exato na quest.
4. **Segurança:**
   - `INFAIDOR.lua` está nos arquivos que mudam durante o jogo (`TRANSIENT_OVERRIDE`) e é instalado vazio pelo `talk_poc.py --deploy`;
   - um teste estático garante um modelo só de `LeaveAreaLUA` e a regra de área nossa no módulo.

5. **Falas de clique (achado no teste):** as criaturas da quest herdavam do corpo de base (`MTOWN6`) as falas de um camponês homem, com voz masculina. Tamoko, por exemplo, dizia "Oh... e aí?" ao ser clicada. A ficha local ganha `sounds: "silent"`, que tira todas essas falas; Tamoko, Gregor e Kalessia foram reconstruídos assim. Os guardas mantêm as falas de rufião do corpo deles. O jogo não tem frases novas para pôr no lugar: só daria para usar uma que já existe.

## Consequências

- O esconderijo existe sem mexer em nenhuma área do jogo, e funciona em saves antigos.
- Quem já entrou na caverna dos piratas reconhece a sala; na quest ela é a caverna sob o Farol.
- **Fora:** arte nova e áreas de outros jogos (licença); a volta para neutro e o multiplayer.

## Verificação

- `tests/test_passages.py`:
  - a cópia mantém o desenho e tira o que age;
  - passagens só de ou para áreas nossas;
  - `WHERE` lê o ponto;
  - a passagem do Farol abre depois de Gregor contar;
  - o módulo, com motor simulado, leva o grupo só com o líder parado 1 s no ponto, uma vez, e nunca com inimigo vivo.
- **No jogo:** evidência própria.
