# Evidência S2d — ADR-0142: inimigos que lutam (2026-11-23)

**Gate:** etapa 1, single player, save descartável; ADR-0142, sobre o gateway (ADR-0136), a presença (ADR-0138), a contagem (ADR-0140) e as fichas (ADR-0141).
**Resultado:** **APROVADO no laboratório ARM64/VM**, nos sete pontos.
- **Correção do caminho:** o módulo passou a executar as ações do jogo na hora, sem fila (item 4 da ADR).
- **Limite registrado:** criar cópias durante o combate não é confiável. O diretor completou o grupo, mas uma criação ficou com confirmação falsa (ver "O que apareceu no caminho").

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, Favelas AR0400, Capítulo 2, save COMBATE-INICIO) e Claude Code (`build_templates.py`, `lab_action.py`, serviço com `--quest-presence --local-quests`).

## Preparação

- **Fichas locais** (`~/.infinity-ai/sheets/`, fora do repositório):
  - Kalessia com `MAGE5`, `GPSHOUT` e `WTASIGHT`, e as magias do BG1: Imagem Espelhada, 2 Horror e 2 Míssil Mágico;
  - o verbeeg com `GPSHOUT` e `WTASIGHT`;
  - "Guarda do Trono de Ferro" (nova), com os números de um bandido guerreiro do BG2, espada longa e armadura de couro.
- **Criaturas**, construídas com o jogo fechado:
  - `IACARCER` nascido hostil (`--hostile`, EA 255);
  - `IAKALESS` e `IAAGENTE` neutros.
- **Quest local de teste** `teste-combate` (fora do repositório). Bernard oferece; os passos são:
  - `ir-as-favelas`: chegar a AR0400, onde nascem 2 carcereiros;
  - `carcereiros-cairam`: derrota dos carcereiros, depois da qual nascem Kalessia e 2 agentes, com `hostile_from: intimidacao`;
  - `intimidacao`: falar com Kalessia;
  - as derrotas dela e dos agentes.

## Os sete pontos

| # | Ponto | Resultado |
|---|---|---|
| 1 | Leitura de aliança | `lab_action.py hostile` no carcereiro vivo: vivos 1, hostis 1, `HOST_CONFIRMED`. A aliança lida no EEex (`m_typeAI.m_EnemyAlly`) funciona |
| 2 | Carcereiros atacam sozinhos | atacaram o grupo ao surgir (o jogo pausou no primeiro ataque); vigiados (de 2 a 1 a 0) e `DEFEATED`, com o passo e a linha do diário da quest |
| 3 | Célula neutra e conversa | Kalessia (de 0 para 1) e os agentes (de 0 para 1, de 1 para 2) nasceram neutros, fora do combate e sem erro; pela caixa, "Sou Kalessia, emissária de Sembia. Não moro aqui." |
| 4 | Intimidação | "Entregue então o diário de Sarevok." cumpriu o passo e o diretor pediu `SET_HOSTILE`: Kalessia 1/1 e agentes 2/2 hostis, confirmados pelo jogo |
| 5 | Magias e luta | Kalessia lançou magias e os agentes lutaram (mantenedor: "Tudo certo") |
| 6 | Diário e XP | ao cair, Kalessia deixou o diário e o grupo ganhou XP (mantenedor); derrotas vigiadas e `DEFEATED` para os dois grupos |
| 7 | Nome que não é nosso | `hostile --name BERNARD`: `NOT_OURS`; `hostile --name INFAI_INVENTADO`: `NOT_OWNED`; os dois recusados pelo gateway, antes do jogo |

## O que apareceu no caminho

1. **Criação na fila do líder se perde no combate.**
   - **Primeira rodada:** o primeiro carcereiro nasceu hostil e o jogo pausou. O segundo `CreateCreature`, na fila do líder, não aconteceu em 3 segundos (antes 1, depois 1). O diretor reteve a presença (`UNCERTAIN`, `SUSPENDED`), como manda a ADR-0138, e só um gigante apareceu.
   - **Correção:** `CreateCreature`, `Enemy()` e `DestroySelf()` estão no `INSTANT.IDS` da build (conferido). O módulo as executa na hora pelo EEex (`EEex_Action_ExecuteResponseStringOnAIBaseInstantly`), e um teste estático proíbe a fila.
2. **Mesmo na hora, criar no meio da luta falhou uma vez.** Na segunda rodada, respostas do módulo:

   | Pedido | Nossos antes | Nossos depois | Criaturas na área |
   |---|---|---|---|
   | 1º carcereiro | 0 | 1 | 46 |
   | 2º carcereiro | 0 | 1 | 46 |
   | 3º (o diretor completou) | 1 | 2 | 47 |

   - **Leitura:** o 2º pedido não criou ninguém, porque o total da área não subiu. No instante do pedido, o 1º carcereiro não foi contado ("antes 0"), e a confirmação saiu falsa.
   - **O que salvou o resultado:** o diretor contou 1 de 2 no ciclo seguinte e completou o grupo; o mantenedor viu o segundo gigante surgir depois de alguns segundos de luta.
   - **Causa:** não descoberta. Fora do combate, as três criações da célula foram limpas.
   - **Correção proposta, fora desta ADR:** "nascer juntos", com as cópias num pedido só e confirmação pela soma exata.
3. **Hostilidade uma presença por vez.** Kalessia ficou hostil na hora; os agentes, cerca de 25 segundos depois, porque o diretor vigiou a derrota dela antes. Não mudou a luta. Entra na mesma proposta: todas as presenças de um passo hostis no mesmo ciclo.
4. **Kalessia não sabe do próprio diário.** Ela respondeu "Disso eu não sei" à exigência. O passo veio da fala do grupo, como desenhado, mas na quest real ela precisa de identidade curada com o diário e a missão.

## Verificação do ramo

- Suíte OK (624 testes), também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64.
- O módulo instalado na VM é igual ao do ramo (SHA-256 `881e97eb…`); manifesto refixado antes e depois do serviço.
