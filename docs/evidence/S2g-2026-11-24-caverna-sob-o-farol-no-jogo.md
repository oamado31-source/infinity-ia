# Evidência S2g — ADR-0146: a caverna sob o Farol, e a quest "O diário perdido de Sarevok" concluída (2026-11-24)

**Gate:** etapa 1, single player, saves descartáveis (DIARIO-GREGOR e seguintes).
**Resultado:** **aprovado no laboratório ARM64/VM.** A área nossa `IA0001` e as passagens funcionaram, e a quest foi concluída do começo ao fim.

**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`, Capítulo 2) e Claude Code (`build_area.py`, `lab_action.py where`, serviço com `--quest-presence`).

## Preparação

- `build_area.py --source AR0310 --name IA0001 --apply` com o jogo fechado: seis arquivos (`ARE`, `WED`, `MOS` e os três `BMP`, cerca de 64 KB), só no override da VM, conferidos pelo tamanho. O desenho original não foi copiado.
- Módulo com passagens e `WHERE` (SHA-256 igual ao do ramo); `INFAIDOR.lua` instalado vazio; manifesto refixado.

## Os pontos

| # | Ponto | Resultado |
|---|---|---|
| 1 | O ponto de entrada | `lab_action.py where` leu o líder primeiro ao lado do navio do cais sul, em (3544, 3030), e depois **ao pé do Farol, em (3832, 3210)**, escolhido pelo mantenedor ("facilita encontrar a localização") |
| 2 | Descer | com o líder parado no ponto, o módulo levou os 5 membros do grupo para `IA0001` (recibo `DONE`, 5) |
| 3 | A célula já estava lá (ADR-0145) | ao carregar a área: Kalessia de 0 para 1 e os guardas de 0 para 3, área de 5 para 9, confirmados pela soma; o passo `esconderijo` foi marcado |
| 4 | A luta | Kalessia derrotada, diário no inventário do grupo, 650 de XP |
| 5 | Voltar e descer de novo | pela saída da caverna o grupo voltou ao pé do Farol, e desceu de novo pelo Farol (mantenedor: "funcionou") |
| 6 | O fim | à noite, Tamoko recebeu o diário ("Obrigada... em paz... o diário está seguro... agora..."), o passo `descanso` foi marcado e ela saiu do mapa; na Coroa, Garoll agradeceu e a quest foi concluída |

## O que apareceu no caminho

1. **A AR0310 é uma caverna, não um porão de navio.** A fase 1 deduziu "navio" pela tripulação de piratas, sem ver a sala. Os minimapas das outras candidatas mostraram um quarto de hospedaria (AR0515) e um convés em alto-mar com a nave githyanki (AR1607). O mantenedor decidiu: uma caverna sob as Docas, e depois sob o Farol.
   - **Lição:** conferir o minimapa (`MOS`) de uma área antes de propô-la.
2. **Falas de clique herdadas:** Tamoko disse "Oh... e aí?", uma fala do camponês cujo corpo ela usa. O gerador ganhou `sounds: "silent"`, e Tamoko, Gregor e Kalessia foram reconstruídos sem essas falas.
   - A reconstrução de Tamoko pediu fixar o escudo (`SHLD06`), pela regra de itens ambíguos da ADR-0141, posterior à criação dela.
   - Conferido nos arquivos da VM: nenhuma fala sobrou nos três.

## Verificação do ramo

- Suíte OK, também com `lupa` e `jsonschema`; `pyflakes` sem avisos.
- `check_historical_adrs` e `check_public_files` OK.
- Suíte com 651 testes; bateria de diálogo 68/68.
