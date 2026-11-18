# Evidência S1x — ADR-0136: portão P3, a primeira escrita reversível no jogo (2026-11-18)

**Gate:** P3 do doc. 07 ("ação permitida e reversível, com estado anterior e posterior"); ADR-0136; DEC-012.
**Resultado:** **APROVADO no laboratório ARM64/VM.** Os sete pontos da proposta passaram, num save descartável.
- O jogo criou e removeu uma criatura nossa ao lado do grupo, e cada ação foi confirmada pela contagem do próprio jogo.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, save `INFINITY-P3-DESCARTAVEL`) e Claude Code via SSH (`lab_action.py`, `build_templates.py`).

## Preparação

- **Backup da pasta de saves** antes de qualquer escrita: `C:\InfinityLab\tmp\saves-backup-p3-20261118` (54 arquivos, 4,5 MB).
- **Módulo `M_INFAIA.lua` e menu `INFAIAM.menu`** instalados com o jogo fechado.
  - Manifesto fixado de novo (`s1x-manifest-2026-11-18b`): mesma build (`sha256:c05b2b973695`); mudaram só o módulo, o menu e o nosso arquivo de criatura.
  - O pedido (`INFAIACT.lua`) é transitório.
- **Criatura nossa:** `IAP3TEST.CRE`, cópia de um camponês vivo do BG2 (`MTOWN6`), com o nome de script `INFAI_P3TEST`.
  - Os bytes ficam só no override da VM e num registro local, fora do repositório.

## Os sete pontos

| # | Ponto | Resultado |
|---|---|---|
| 1 | Antes: nenhuma criatura nossa | ramo sem criatura nossa; contagem do jogo `before=0` |
| 2 | Criar | `CreateCreature("IAP3TEST",[x.y],0)` no líder; resposta `DONE` com antes 0 e depois 1 (`HOST_CONFIRMED`); a busca viu 63 criaturas na área. No jogo: um camponês vivo ao lado do grupo, que conversou pela caixa com o nome `INFAI_P3TEST` |
| 3 | Salvar e recarregar | salvo num slot novo e recarregado: o camponês no mesmo lugar; o serviço seguiu no mesmo ramo, com a criatura registrada |
| 4 | Save anterior | carregado o save de antes da criação: o camponês não aparece; o ramo novo não lista criatura nossa |
| 5 | Remover | `DestroySelf()` na criatura nossa; resposta antes 1, depois 0 (`HOST_CONFIRMED`); no jogo, ele sumiu |
| 6 | Pedidos inválidos | recusados antes do jogo: arquivo inexistente, ponto pela metade, remover alguém do jogo (Bernard), remover nome nosso não registrado; o módulo recusou a área errada com o jogo aberto (`WRONG_AREA`) |
| 7 | O mesmo pedido de novo | reenviado o mesmo `action_id` depois de concluído: o módulo não o executou (o log seguiu com as duas linhas da primeira vez) |

## Correções feitas no caminho

Cada uma tem teste em `tests/test_actions.py` e está registrada na ADR-0136.

1. **`CreateCreature` no BG2:EE tem três argumentos** (`ACTION.IDS`: criatura, ponto, direção). Com um quarto, o nome de script, o jogo descartou a ação sem aviso, e o gateway ficou em `UNCERTAIN`, como devia. Correção: o nome nosso vai dentro do arquivo da criatura (`build_templates.py`, resref `IA*`, nome `INFAI_*`).
2. **O primeiro modelo era um corpo.** `DPMALE` (camponês do cerco de Saradush) está gravado como morto: o jogo o criou deitado, e a contagem não o achou. Correção: `build_templates.py` recusa modelo em estado de morte (`DEAD_SOURCE_CRE`). O novo modelo é `MTOWN6`.
3. **A busca não via ninguém, por dois motivos:**
   - no EEex, `false` liga a checagem de linha de visão ("`bCheckForLineOfSight or 1`"), e ela partia do canto do mapa; o certo é passar `0`;
   - o raio é de 16 bits com sinal, e 65535 virava -1; o raio agora é 30000.
   - A resposta passou a trazer quantas criaturas a busca viu (`seen`), para separar busca quebrada de criatura ausente.
4. **Ação sem tempo de jogo.** A primeira criação foi gravada sem o tempo, e um ramo aberto por save antigo a herdou. Correção:
   - cada ação grava o tempo de jogo da última linha do probe;
   - o gateway recusa ação sem ele (`NO_GAME_TIME`);
   - a lista das nossas criaturas ignora registros sem tempo.

## Limites

- **Só o mantenedor dispara** (D2). Quest, modelo e caixa ainda não disparam ações.
- **Criaturas mortas** não são vistas pelo seletor do jogo: não são contadas nem removidas pelo módulo.
- **Instalação com o jogo fechado:** arquivos novos de criatura só valem depois de reabrir o jogo (o motor só acha arquivos do override presentes na abertura).
- **Multiplayer (P4):** fora.

## Verificação do ramo

- Suíte OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64.
