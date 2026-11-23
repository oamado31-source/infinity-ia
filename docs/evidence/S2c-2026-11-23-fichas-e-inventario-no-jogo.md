# Evidência S2c — ADR-0141: Gregor, Kalessia e os carcereiros, e o diário no inventário (2026-11-22/23)

**Gate:** etapa 1, single player, save descartável; ADR-0141, sobre o gerador da ADR-0137.
**Resultado:** **APROVADO no laboratório ARM64/VM.** As três criaturas novas, com o diário de Sarevok na mochila de Kalessia, passaram no jogo. O carcereiro chegou à aparência de verbeeg, do tamanho de gigante, depois de duas tentativas e de um experimento aprovado (CR-2026-032).

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, Favelas AR0400, Capítulo 2, save FICHAS-INICIO) e Claude Code (`build_templates.py`, `lab_action.py`).

## Preparação

- **Fichas locais** (`~/.infinity-ai/sheets/`, fora do repositório):
  - Gregor e Kalessia da wiki do BG;
  - o verbeeg do Complete Compendium (*Monstrous Manual*), convertido para o motor.
- **Criaturas**, construídas com o jogo fechado:
  - `IAGREGOR`: corpo `MTOWN6`, sem itens;
  - `IAKALESS`: corpo `MTOWN6`; traje `CLCK09` e cajado `STAF01` (fixado); diário `SCRL3F` na mochila (`--carry`);
  - `IACARCER`: corpo `OGRHAL01`, animação `GIANT_VERBEEG`; clava `BLUN01` e escudo `SHLD03`, fixados.
- **Curadorias de Gregor e Kalessia** carregadas: 30 identidades curadas.

## Os sete pontos

| # | Ponto | Resultado |
|---|---|---|
| 1 | Gregor | criado (de 0 para 1); ladrão humano sem armas; pela caixa, "Sou Gregor, desertor do Trono de Ferro. Meu pai, líder do Trono, foi assassinado em 1368." (identidade curada, sem recusas) |
| 2 | Kalessia | criada (de 0 para 1); maga humana com traje e cajado; "Sou Kalessia, emissária de Sembia." e, sobre o diário, "Não entrego a ninguém." |
| 3 | O diário na mochila | Kalessia apagada pelo console; caíram o traje, o cajado, 23 de ouro e **"O diário de Sarevok"**, pego para a mochila do grupo |
| 4 | O carcereiro | **1ª tentativa:** invisível, porque o BG2:EE define a animação de verbeeg, mas não tem os desenhos. **2ª:** meio-ogro, visível, mas de porte humano. **3ª:** com os desenhos do Infinity Animations no override, **verbeeg, tamanho de gigante**, nome "Carcereiro" (captura do mantenedor) |
| 5 | Duas cópias | criadas uma a uma (de 0 para 1, de 1 para 2), contagem 2, nas três tentativas |
| 6 | Item ambíguo | ficha com "Cajado" sem resref: `ITEM_AMBIGUOUS`, com os sete candidatos listados; nada instalado |
| 7 | Remoção | carcereiros (de 2 para 0), Gregor (de 1 para 0) e Kalessia (o corpo não conta, `NOT_FOUND` com contagem 0), todos `HOST_CONFIRMED` |

## O que apareceu no caminho

1. **Animação definida, mas sem desenhos.** O `ANIMATE.IDS` e o `E251.INI` do BG2:EE descrevem o verbeeg com o prefixo `MGVE`, mas os desenhos só vêm no IWD:EE. O mesmo vale para os gigantes do gelo, da colina e do fogo de IWD.
   - Correção: `build_templates.py` lê o INI e recusa a animação sem desenhos na build ou no override ("a criatura ficaria invisível"). Conferido no laboratório: verbeeg recusado antes da instalação dos desenhos e aceito depois.
2. **O motor não escala criaturas.** O tamanho vem do desenho; o meio-ogro tem porte humano.
3. **Os desenhos do verbeeg** vieram do Infinity Animations (CR-2026-032, aprovada):
   - pasta `archives/iwd/iwd_giant_verbeeg`, 24 desenhos `BAMC` e 9 sons `WAVC`, com o commit de origem anotado;
   - renomeados para o que o INI espera e copiados por `scp` (o envio pelo PowerShell estourou o tempo num desenho grande);
   - conferidos pelo tamanho na VM; nada sobrescrito;
   - só no override do laboratório, nunca no repositório.
4. **O laço do zsh** não separa argumentos de uma variável: a primeira tentativa de construir não fez nada; refeita com os comandos explícitos.
5. **O manifesto** passou a incluir os 33 arquivos do verbeeg e o arquivo de resposta da caixa zerado pelo serviço.

## Verificação do ramo

- Suíte OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64.
