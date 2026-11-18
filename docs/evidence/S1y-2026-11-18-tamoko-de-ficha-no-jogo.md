# Evidência S1y — ADR-0137 (P3b): Tamoko, de BG1, gerada da ficha e posta no jogo como visão (2026-11-18)

**Gate:** etapa 1, single player, save descartável; ADR-0137 sobre o portão P3 (ADR-0136).
**Resultado:** **APROVADO no laboratório ARM64/VM.** A primeira personagem de outro jogo apareceu no BG2:EE, gerada de uma ficha e com a aparência de visão. Ela conversou pela caixa como quem é e foi removida, com o jogo confirmando cada ação.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, save descartável na Coroa de Cobre, AR0406) e Claude Code via SSH (`build_templates.py --from-sheet`, `lab_action.py`).

## Preparação

- **Ficha local** `~/.infinity-ai/sheets/bg1/tamoko.json` (fora do repositório, CR-2026-030):
  - os números vêm da TH.GL, consultada por entidade;
  - as cores do corpo saíram da imagem do BG1:EE na wiki, casadas com a paleta de gradientes da build (`MPAL256`). O arquivo de criatura de Tamoko não existe no BG2:EE.
- **Criatura nossa:** `IATAMOKO.CRE`, nome de script `INFAI_TAMOKO`, construída com o jogo fechado:
  - corpo de um camponês vivo do BG2 (`MTOWN6`), copiado, nunca editado no lugar;
  - animação `CLERIC_FEMALE_HUMAN`, a mesma da wiki;
  - o nome é o texto "Tamoko", que o `dialog.tlk` da build já tem;
  - itens achados pelo nome: Armadura da Escuridão +1 (`PLAT05`), Mangual +1 (`BLUN03`), Escudo Grande +1 (`SHLD06`);
  - `--vision`: translucidez (opcode 66) e brilho pálido pulsando no corpo inteiro (opcode 50).
- **Manifesto fixado de novo** (`s1x-manifest-2026-11-18b`): a mesma build, e só mudou `iatamoko.cre`.
- **Curadoria** `knowledge/npcs/tamoko.pt_BR.json`, conferida pelo mantenedor: a visão, a morte sem causa conhecida e o diário perdido.

## O teste

| # | Ponto | Resultado |
|---|---|---|
| 1 | Criar | pedido `SPAWN_CREATURE IATAMOKO` em AR0406; resposta `DONE`, antes 0, depois 1 (`HOST_CONFIRMED`) |
| 2 | Aparência | mantenedor: "Translúcida com brilho, Aparência ok": clériga em placas, com escudo grande e mangual |
| 3 | Nome | mantenedor: "Nome ok" (Tamoko) |
| 4 | Conversa, primeira tentativa | **falhou:** "Sou Tamoko, clériga de Kara-Tur." e, perguntada o que fazia ali, respondeu que estava de passagem e não conhecia os costumes. Os fatos de forasteira venceram os de visão |
| 5 | Conversa, depois da correção | "Sou Tamoko, clériga morta." e, perguntada o que fazia ali, disse que quer descobrir como e onde morreu. Log: estatuto `VISAO`, identidade `CURATED`, sem recusas, `status=OK` nos dois turnos |
| 6 | Remover | pedido `DESPAWN INFAI_TAMOKO`; resposta `DONE`, antes 1, depois 0 (`HOST_CONFIRMED`); o ramo ficou sem criatura nossa |

## Correção feita no caminho

**A visão não é viajante** (ADR-0137, item 8). Com o estatuto `FORASTEIRO`, os fatos gerados ("está de passagem por Athkatla", "não conhece bem os costumes daqui") disputavam com os fatos de visão. A curadoria passou a aceitar o estatuto `VISAO`, só curado e nunca gerado:
- ela sabe o mesmo que um forasteiro;
- os fatos dizem que ela aparece ali como visão e de onde era em vida;
- a validação recusa, numa visão, dizer que está de passagem, que é viajante ou que mora aqui (`SELF_CLAIM:VISION`).

Os testes estão em `tests/test_identity.py`.

## Limites

- **Sem combate e sem magias** (D3, D5): é neutra e conversa só pela caixa.
- **CA:** a CA final de −5 não foi lida no jogo. O gerador grava a CA natural 10, e o jogo soma armadura, escudo e Destreza.
- **Só o mantenedor dispara** a criação. Pela quest, isso fica para a peça A da quest "O diário perdido de Sarevok".

## Verificação do ramo

- Suíte OK (588 testes), também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64.
