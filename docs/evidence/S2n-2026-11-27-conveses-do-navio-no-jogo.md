# Evidência S2n — ADR-0151: os conveses da *Estrela de Waukeen* no jogo (2026-11-27)

**Gate:** etapa 1, single player, save descartável, Docas (AR0300) e Coroa de Cobre (AR0406).
**Resultado:** **aprovado no laboratório ARM64/VM**, na quarta instalação do convés superior. O mantenedor confirmou: "Tudo passou".

**Executado por:** mantenedor, no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`), e Claude Code.

**Preparação, com o jogo fechado, a cada rodada:**
1. As cenas foram renderizadas no Mac (`render_area.py`).
2. `build_new_area.py --apply` instalou as áreas: verificadas contra todos os nomes da build, sem erro nem aviso.
3. O manifesto foi refixado antes e depois de o serviço gravar a lista de quests: mesma build, só arquivos nossos.
4. Uma quest local de teste (`teste-navio`, fora do repositório) abriu, depois do aceite com Bernard, as oito passagens do navio.

## O que passou

| # | Ponto | Log | No jogo |
|---|---|---|---|
| 1 | O aceite abre as oito passagens | `NarrativeQuestAccepted teste-navio`, `passagens abertas: 8` | linha do diário |
| 2 | Cais → barco | `AreaEntered IA0002 (de AR0300)`, chegada `subir-a-bordo` | o grupo no barco a remo, ao pé da escada de corda |
| 3 | Subir a bordo | — | pela escada e pelas redes de abordagem, e não pelo casco (quarta instalação) |
| 4 | O convés superior | — | mar até as bordas da tela, mapa já explorado, tombadilho pela escada, leme, porta dos camarotes |
| 5 | Convés superior → convés do meio → porão, e de volta | `IA0002 → IA0003 → IA0004 → IA0003 → IA0002` | alçapões e escadas |
| 6 | Convés superior → camarotes | `AreaEntered IA0005 (de IA0002)` | porta sob o tombadilho |
| 7 | Navio → cais | `AreaEntered AR0300 (de IA0002)` | o grupo volta às Docas (segunda rodada) |

**O que não foi registrado:**
- **A volta dos camarotes ao convés:** a última rodada termina com a entrada nos camarotes. É a mesma regra das outras passagens, que voltaram pelo mesmo ponto.
- **A entrega a Bernard:** não houve `NarrativeQuestResolved`. Ela já passou na S2l e não depende das áreas.
- **Salvar e carregar dentro do navio:** não foi feito. As rodadas começaram de saves na Coroa.

## O que apareceu no caminho

1. **Recorte escuro e tela sem mar** (primeira instalação).
   - **Causa:** a névoa de guerra da área não explorada, mais as sombras de visão do mastro, da carga e da amurada, numa área de 1280 × 960, menor que a tela.
   - **Correção:**
     - área de 2560 × 1920 com o navio no centro;
     - `ARE` com o mapa de exploração todo marcado (o formato foi medido em oito áreas de um save);
     - nada no convés aberto tapa a visão.
   - O círculo de visão do grupo continua, como em toda área; à noite ele aparece mais.
2. **O grupo subia pelo casco** (instalações 1 a 3).
   - A faixa de subida era primeiro inclinada e larga demais.
   - Depois, colada na escada, ficou com uma célula: o motor empurrava quem esperava a vez para o casco ao lado.
   - Uma escada de 1,2 m também não resolveu.
   - **Correção, pela ideia do mantenedor:** escada estreita, **redes de abordagem** dos dois lados e cordas soltas, com a faixa de subida cobrindo escada e redes.
3. **Uma falha do Blender passou em silêncio.** O desenho da rede quebrou no script, e a ferramenta manteve o desenho anterior. Agora a ferramenta apaga o desenho antes e falha com erro.
4. **Erros de banco de dados no serviço:**
   - dois `OperationalError`: uma fala de Bernard e uma rodada das presenças;
   - a operação seguinte funcionou;
   - é a trava do SQLite já anotada como pendência (busy-timeout), sem relação com as áreas.
5. **O aceite e o broche:** com as formas de aceitar restritas a "vamos" e "topamos", o broche de Bernard não foi aceito junto em nenhuma rodada.

## Verificação do ramo

- A suíte passa inteira (com `lupa` e `jsonschema`), e `pyflakes` não dá avisos.
- `check_historical_adrs` e `check_public_files` passam.
- **Testes novos:** em `tests/test_area_scene.py`, o navio, o tombadilho, a subida a bordo e o mar aberto.
- **Fora do repositório**, em `~/.infinity-ai/`: os desenhos renderizados, os arquivos gerados e as prévias.
- **No repositório:** só as cenas e as receitas, em texto.
