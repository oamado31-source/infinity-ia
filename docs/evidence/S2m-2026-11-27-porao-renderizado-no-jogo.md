# Evidência S2m — ADR-0150: o porão renderizado no jogo (2026-11-27)

**Gate:** etapa 1, single player, save descartável, Docas (AR0300) e Coroa de Cobre (AR0406).
**Resultado:** **aprovado no laboratório ARM64/VM**, na segunda instalação. O mantenedor confirmou no jogo: "Sumiram, tudo passou".

**Executado por:** mantenedor, no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`), e Claude Code.

**Preparação, com o jogo fechado:**
1. A cena do porão, aprovada na prévia v10, foi renderizada no Mac pelo Blender 4.5.17 LTS (`render_area.py`, cerca de 16 s).
2. `build_new_area.py --recipe knowledge/areas/ia0004-porao.json --apply`:
   - gerou o porão `IA0004` (8 arquivos, cerca de 137 KB);
   - verificou contra todos os nomes da build, sem erro nem aviso;
   - gravou no override.
3. O manifesto foi refixado antes e depois de o serviço gravar a lista de quests: mesma build, só arquivos nossos mudaram.
4. Uma quest local de teste (`teste-porao`, fora do repositório) abriu, depois do aceite com Bernard, a passagem entre o cais das Docas (1496, 3570) e o pé da escada do porão (737, 241).

## O que passou

| # | Ponto | Log | No jogo |
|---|---|---|---|
| 1 | O aceite abre as passagens | `NarrativeQuestAccepted teste-porao`, `passagens abertas: 2` | linha do diário |
| 2 | Cais → porão | `AreaEntered IA0004 (de AR0300)`, chegada `descer-ao-porao` | o grupo aparece no pé da escada |
| 3 | O desenho renderizado | — | madeira avermelhada, carga, redes, cela e lanternas, como a prévia aprovada |
| 4 | Onde se anda | — | o casco, as pilhas, os barris, os cavaletes, o mastro, os esteios e as grades bloqueiam |
| 5 | As paredes | — | quem passa atrás das pilhas, do mastro e dos cavaletes fica translúcido |
| 6 | A linha de visão | — | pilhas e mastro fazem sombra; grades e redes não |
| 7 | O mapa da área | — | o porão aparece, com o grupo |
| 8 | Porão → cais | `AreaEntered AR0300 (de IA0004)` | o grupo sobe ao cais |
| 9 | As emendas dos tiles (segunda instalação) | — | as listas horizontais sumiram |

**O que não foi registrado:**
- **A entrega a Bernard.** Não houve `NarrativeQuestResolved` para `teste-porao`. A entrega já tinha passado na S2l e não depende da área.
- **Salvar e carregar dentro do porão.** A segunda rodada começou de um save na Coroa, e o grupo desceu de novo pelo cais.

## O que apareceu no caminho

1. **Listas horizontais a cada 64 px** (primeira instalação).
   - **Causa:** nas páginas de textura, os tiles iam em filas de 16, sem seguir a largura do desenho (15 tiles). O vizinho de baixo na página não era o vizinho de baixo no desenho, e o motor, ao ampliar, misturava a borda do tile com uma linha de outro lugar da sala.
   - **A sala `IA0090`** (12 tiles de largura) tinha o mesmo defeito, mais fraco.
   - **Correção:** cada página guarda um bloco do desenho como ele é, com as bordas repetidas, como as páginas do jogo (AR0310, AR0515).
   - As duas áreas foram reinstaladas, e as listas sumiram.
2. **O aceite pegou duas quests.**
   - Na segunda rodada, a mesma frase aceitou a quest do porão e o broche de Bernard (`bernard-brooch`), que estava oferecido no save carregado.
   - É o mesmo achado da S2l: um aceite genérico vale para todas as ofertas pendentes do mesmo NPC.
   - Fica para a autoria de quests (aceitar só a oferta mais recente).
3. **A cela é fechada:** grades em dois lados, costado e borda da frente. Ninguém do grupo entra; os reféns vão nascer lá dentro.
4. **O desenho passou por dez prévias** antes da aprovação:
   - a madeira e as lanternas no estilo da AR0515;
   - a carga no estilo da AR0318;
   - os sacos trocados por redes de pesca e, depois, por três cavaletes.
   - Tudo foi feito pelo nosso script, só com referência visual, sem copiar desenho.

## Verificação do ramo

- A suíte passa inteira (com `lupa` e `jsonschema`), e `pyflakes` não dá avisos.
- `check_historical_adrs` e `check_public_files` passam.
- **Testes novos:**
  - `tests/test_area_camera.py`;
  - `tests/test_area_scene.py`;
  - em `tests/test_area_files.py`, as páginas como blocos.
- **Fora do repositório**, em `~/.infinity-ai/`: o desenho renderizado, os arquivos gerados e as prévias.
- **No repositório:** só a cena e a receita, em texto.
