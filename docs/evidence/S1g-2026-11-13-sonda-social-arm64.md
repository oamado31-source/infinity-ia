# Evidência S1g — sonda só de leitura de Carisma, Moral e líder selecionado (ADR-0122) (single player, 2026-11-13)

**Gate:** primeiro passo de validação do ADR-0122 (PROPOSTA). Etapa 1, single player.
**Resultado:**
- As leituras de Carisma e Morale Break de base batem com a ficha (CRE) dos NPCs testados.
- A moral atual do motor e o Morale Break ativo **podem diferir** da ficha.
- `selected_leader` acompanha a seleção do grupo, mas **não prova** quem inicia o diálogo.

Nada foi escrito no jogo, e esses valores ainda não entram em nenhuma fala.

**Executado por:** o mantenedor, no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`); Claude Code, via SSH.

## Ambiente

- **Jogo e EEex:** BG2:EE 2.7.3.0 (`Baldur.exe` x64 sob emulação no Windows 11 ARM64/VMware) com EEex v1.3.1 (evidência P1).
- **Manifesto fixado:** `s1f-manifest-2026-11-10-pinned.json`, refeito em 2026-11-13 depois de publicar a caixa desta branch (o manifesto vivo confere com ele).
- **Código no laboratório:** `main` com esta branch, a CR-2026-004 e o ADR-0123, numa cópia local. A combinação de `M_INFAIT.lua` e `talk.py` é a mesma que entrou nesta branch no merge `83f3711`.
- **Ficha de referência:** bytes 0x23E (Carisma), 0x23F (Moral) e 0x240 (Morale Break) dos arquivos CRE da build, lidos por SSH e só exibidos (nada gravado no repositório).

## Atributos do NPC: caixa no jogo × ficha

| NPC | Carisma ativo/base | Moral atual do motor | Morale Break ativo/base | Ficha (CHR / Moral / Morale Break) |
|---|---|---|---|---|
| Bernard (`BERNARD.CRE`) | 9 / 9 | 10 | 2 / 2 | 9 / 10 / 2 |
| Salvanas (`SALVANAS.CRE`) | 15 / 15 | 10 | 7 / 7 | 15 / 10 / 7 |
| Campesino (`MTOWN6.CRE`) | 9 / 9 | 10 | 7 / 7 | 9 / 10 / 7 |
| Lorde Jierdan (`FIRKRA01.CRE`) | 12 / 12 | **10** | **0** / 1 | 12 / **20** / 1 |

- **Carisma e Morale Break de base** batem com a ficha nos quatro NPCs.
- **Moral atual do motor:** é 10 nos quatro, inclusive em Jierdan, cuja ficha registra 20. A moral atual é um estado do jogo, e não o valor da ficha nem a moral do AD&D (ADR-0122, item 5).
- **Morale Break ativo:** em Jierdan é 0, contra 1 na base. Algum efeito ou script altera o valor ativo.
- Os valores do NPC não mudaram com a troca de personagem selecionado (Bernard e Salvanas, cada um com os quatro membros do grupo).

## Líder selecionado (`selected_leader`)

| Seleção feita no jogo | `selected_leader` |
|---|---|
| só Imoen | retrato 1, Carisma 16 |
| só Minsc | retrato 2, Carisma 9 |
| só Jaheira | retrato 3, Carisma 15 |
| protagonista (só ele ou o grupo todo) | retrato 0, Carisma 14 |

- Com um personagem de cada vez, o campo acompanhou a seleção nas 4 combinações, com o retrato e o Carisma corretos.
- Com o grupo todo selecionado, o campo indicou o retrato 0. Não foi comparado com o personagem que o motor usa ao iniciar um diálogo nativo, então o iniciador **continua não comprovado**. Até haver prova, nenhum ajuste de Carisma é aplicado (ADR-0122).

## Limites e próximos passos

- Fazer um teste com um diálogo nativo equivalente, para comparar quem o motor usa como iniciador.
- Investigar por que a moral atual de Jierdan é 10 e o Morale Break ativo é 0 (efeitos ou scripts), antes de definir a origem da moral do AD&D (ADR-0122, item 5).
- Os campos são só diagnóstico: não entram na `DialogueEngine` nem em nenhum cálculo de reação ou moral.
