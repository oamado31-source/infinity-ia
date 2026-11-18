# Evidência S1w — SPEC-012 fase 1: o censo dos personagens do BG2:EE (2026-11-18)

**Gate:** SPEC-012 (fase 1 e primeiro corte da fase 2), CR-2026-030.
**Resultado:** **EXECUTADO no laboratório ARM64/VM.** Só leitura, em memória. O catálogo derivado ficou na máquina do mantenedor, fora do repositório.

**Executado por:** Claude Code via SSH (`tools/windows-lab/build_encyclopedia.py --characters`), na cópia `BG2EE-P1`.

## Resultado

- **Build:** `sha256:c05b2b973695`, idioma `pt_BR`; leitura de cerca de 1 minuto.
- **Áreas lidas:** as 423 do índice do jogo (nada no override).
- **Entradas:** 1.949, sendo 1.596 personagens e 353 criaturas sem nome próprio (categoria 02, fase 3).
- **Personagens:**
  - 1.274 com diálogo próprio;
  - 92 que abrem uma loja;
  - 24 já com ficha curada. Os três companheiros com ficha não aparecem, porque o jogo não os põe nas áreas.
- **Catálogo local:** `~/.infinity-ai/encyclopedia/install-c05b2b973695b622/census.pt_BR.json`.
- **Relatório para o mantenedor** (fora do repositório): `~/Downloads/INFINITY_AI_Censo_Personagens_BG2.md`, com personagens por área e a fila sugerida de curadoria.
- **Posição e horário:** conferidos com um caso conhecido. Yarin está em AR0406, na mesma posição que a leitura manual de S1v achou, presente o dia todo.

## Ajuste feito com o resultado

- **A primeira regra** contava como personagem só o humanoide com nome e com nome de script ou diálogo.
- **O que apareceu:** um NPC curado da Coroa de Cobre tem, no jogo, ficha de criatura não humanoide. A SPEC (seção 4.1) põe na categoria 01 os antagonistas com identidade individual.
- **A regra agora:** também é personagem quem tem nome, nome de script e diálogo próprio, mesmo sem ser humanoide. A contagem passou de 1.488 para 1.596 personagens. Um animal sem diálogo continua sendo criatura. Teste em `tests/test_encyclopedia.py`.

## Limites

- **Capítulo:** depende dos scripts do jogo e ficou fora desta contagem.
- **Nomes de área:** algumas áreas não têm nome no inventário local. Algumas saem com a grafia do próprio jogo.
- **Nada do catálogo entra no repositório;** o teste `HygieneTests` confere.

## Verificação do ramo

- Suíte: 565 testes OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Bateria de diálogo: 64/64.
