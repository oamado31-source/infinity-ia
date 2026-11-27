# Evidência S2l — ADR-0149: a primeira área feita só por código, no jogo (2026-11-27)

**Gate:** etapa 1, single player, save descartável, Docas (AR0300) e Coroa de Cobre (AR0406).
**Resultado:** **aprovado no laboratório ARM64/VM**, na segunda instalação. O mantenedor confirmou no jogo: "Tudo passou".

**Executado por:** mantenedor, no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`), e Claude Code.

**Preparação, com o jogo fechado:**
- `build_new_area.py --recipe knowledge/areas/ia0090-sala-de-teste.json --apply` gerou a sala `IA0090` só a partir da receita, sem nenhum byte do jogo, verificou contra todos os nomes da build e gravou 8 arquivos (cerca de 34 KB) no override;
- o manifesto foi refixado antes e depois de o serviço gravar a lista de quests: mesma build, só arquivos nossos mudaram;
- uma quest local de teste (`teste-sala-nova`, fora do repositório) abriu, depois do aceite com Bernard, uma passagem entre o cais das Docas, no ponto (1496, 3570) lido no jogo com `lab_action.py where`, e a sala, no ponto (384, 500).

## O que passou

| # | Ponto | Log | No jogo |
|---|---|---|---|
| 1 | O aceite abre as passagens | `NarrativeQuestAccepted teste-sala-nova`, `passagens abertas: 2` | linha do diário |
| 2 | Cais → sala | `AreaEntered IA0090 (de AR0300)`, chegada `entrar-na-sala` | o grupo aparece na entrada sul |
| 3 | O desenho | — | piso de tábuas, parede de pedra, bordas e pilar, como a prévia local |
| 4 | Onde se anda | — | a parede norte, as bordas e o pé do pilar bloqueiam |
| 5 | A linha de visão | — | o pé do pilar (código 0) faz sombra a partir do grupo, como um obstáculo do jogo |
| 6 | O mapa da área | — | a sala aparece inteira, com o grupo |
| 7 | A parede do pilar (segunda instalação) | — | quem fica atrás do pilar aparece translúcido, como atrás das paredes do jogo; quem está na frente continua sólido |
| 8 | Sala → cais | `AreaEntered AR0300 (de IA0090)`, duas vezes | o grupo volta ao cais |
| 9 | A entrega | `NarrativeQuestResolved teste-sala-nova`, `passagens abertas: 0` | Bernard agradece; duas linhas do diário |

**Salvar e carregar:** o mantenedor reabriu o jogo e carregou um save, e a sala carregou de novo, com a parede corrigida. O save carregado estava na Coroa de Cobre: o log não registra um carregamento feito dentro da sala.

## O que apareceu no caminho

1. **A parede do pilar não escondia ninguém** (primeira instalação).
   - O motor usa os **dois primeiros pontos** de um polígono de parede como a linha de base (o pé da parede). Quem está acima dessa linha fica atrás.
   - Confirmado de dois jeitos:
     - no GemRB, que reimplementa o motor: só lido, nada copiado;
     - nas paredes das salas do jogo, que começam pelo canto de baixo.
   - O nosso retângulo começava pelo lado de cima, então ninguém ficava acima da linha.
   - **Correção:** todo retângulo de parede começa pela borda de baixo. O verificador ganhou o aviso `WALL_BASELINE` para polígonos cuja linha de base não está no pé.
2. **Atrás de uma parede, o personagem fica translúcido.** As Enhanced Editions não escondem o personagem por inteiro: ele fica translúcido, para o jogador não perder o grupo de vista.
3. **Duas quests oferecidas pelo mesmo NPC.**
   - O primeiro aceite ("sim") pegou o broche de Bernard (`bernard-brooch`), oferecido num teste antigo, e não a quest da sala: cada quest confere as próprias formas de aceitar.
   - Fica como achado para a autoria de quests: aceitar só a oferta mais recente do mesmo NPC.
   - Não foi mexido nesta ADR.
4. **O estilo.** O mantenedor notou que a sala não tem o estilo dos mapas de BG. É esperado: a sala testa os formatos. O estilo vem na fase 3, com o render no Blender.
5. **O chamado de DRUNK1** (quest de Sarevok) foi `DENIED` algumas vezes, sem relação com a sala.

## Verificação do ramo

- A suíte passa inteira (com `lupa` e `jsonschema`), e `pyflakes` não dá avisos.
- `check_historical_adrs` e `check_public_files` passam. O segundo agora também recusa `.tis`, `.pvrz` e `.pvr`.
- **Testes novos:**
  - `tests/test_area_files.py`;
  - `tests/test_area_recipe.py`: inclui a linha de base do pilar e o aviso `WALL_BASELINE`.
- **Conferência no laboratório:** `area_preview.py --roundtrip` em AR0310, AR0515 e AR1607. Desenho entre 41 e 43 dB, mapa de busca e paredes iguais, e grupos de parede que contêm os do jogo.
- **Arquivos:** os arquivos gerados e as prévias ficaram em `~/.infinity-ai/`, fora do repositório.
