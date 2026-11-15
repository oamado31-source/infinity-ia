# Evidência S1j — diálogo só em texto e fala padrão do jogo (single player, 2026-11-15)

**Gate:** etapa 1 (ADR-0113), ADR-0129 sobre SPEC-004.
**Resultado:** a fala padrão ao abrir a caixa e o diálogo só escrito foram **APROVADOS no laboratório ARM64/VM**, com Bernard, outro NPC e um companheiro. Nos companheiros, a fala só funcionou depois da correção dos índices (seção abaixo).
**Executado por:** mantenedor no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`) e Claude Code via SSH (serviço de diálogo no Mac, M1 Max 64 GB).

## Preparação

- **Caixa nova:** copiada com `talk_poc.py --deploy`, e o jogo foi reaberto.
- **Manifesto S1j:** o serviço recusou a build ao vivo (`live matches pinned: False`) porque a caixa nova mudou o hash do modpack, e por isso o Bernard não respondia. A comparação com o manifesto S1h mostrou a mesma build, com só `override/M_INFAIT.lua` diferente. O manifesto novo ficou fora do repositório (`s1j-manifest-2026-11-15-pinned.json`), e o serviço passou a confirmar a build (`live matches pinned: True`).
- **Serviço:** `dialogue_service.py --voice`, sem TTS (o código de voz sintetizada foi retirado).

## Fala padrão

| Origem | Linha (sem texto) |
|---|---|
| log do jogo | `INFAI-TALK-DEBUG fala padrao: 1 opcoes (INITIAL_MEETING), tocada=true` |
| log do jogo | `INFAI-TALK-DEBUG aberta pelo clique direito` |

- **Bernard:** sem fala de seleção, caiu na de primeiro encontro. O mantenedor confirmou que a fala tocou.
- **Sonda:** a leitura funcionou na build pinada (EEex 1.3.1):
  - campo `m_baseStats.m_speech`;
  - slots achados pelo nome em `SOUNDOFF.IDS`;
  - `EEex_Sprite_DisplayTextRef` com o jogo sendo pausado logo em seguida.
- **Repositório:** nenhum áudio ou texto do jogo foi copiado; o log só registra o slot e quantas opções havia.

## Diálogo

| Momento (UTC) | Evento |
|---|---|
| 00:49:06 | `voz … estado=TEXT`: 4,2 s de gravação, STT 0,6 s |
| 00:49:10 | `caixa … entrada=VOICE falante=npc:cre-bernard status=OK` |
| 00:49:24 | `voz … estado=TEXT`: 4,0 s de gravação, STT 0,5 s |
| 00:49:41 | `caixa … entrada=VOICE falante=npc:cre-bernard status=OK` |
| 00:49:52 | `voz … estado=TEXT`: 2,5 s de gravação, STT 0,5 s |
| 00:49:55 | `caixa … entrada=VOICE falante=npc:cre-bernard status=FALLBACK motivo=VALIDATION_FAILED` |

- **Resposta só escrita:** nenhuma voz sintetizada.
- **FALLBACK:** a resposta do modelo foi recusada pelo validador, e a caixa recebeu a resposta segura. É o comportamento de sempre do motor de diálogo e não tem relação com esta mudança.

## Checagens

- **Testes:** 407, todos OK (também com `lupa`); `pyflakes` limpo; `check_historical_adrs` e `check_public_files` OK.
- **Bateria de diálogo:** 21/21, com tempo médio de 0,9 s e p90 de 1,6 s (`20261115T004626Z.json`).

## Companheiros: correção dos índices

| Momento | Linha do log do jogo (sem texto) |
|---|---|
| antes (índices pelo `SOUNDOFF.IDS`) | `fala padrao: nenhuma no conjunto de sons`, em cada clique direito num companheiro |
| depois (índices pelo `SNDSLOT.IDS`) | `fala padrao: 6 opcoes (SELECT_COMMON1), tocada=true` |

- **Causa:** o `SOUNDOFF.IDS` é a tabela do `VerbalConstant`, não as posições na ficha. As posições ficam no `SNDSLOT.IDS`. O primeiro encontro funcionava por coincidência, por ser o slot 0 nas duas tabelas.
- **Correção:** os índices passam a vir do `SNDSLOT.IDS`, com o `SOUNDOFF.IDS` só como reserva. Quando não há fala, o diagnóstico registra as posições preenchidas, só com números.
- **Manifesto:** a caixa mudou de novo, e foi fixado um manifesto novo (`s1j-manifest-2026-11-15b-pinned.json`, fora do repositório): mesma build, só `override/M_INFAIT.lua` diferente.
- **NPC sem fala no conjunto de sons:** ficou em silêncio, como previsto.
- **Avaliação do mantenedor:** "Agora funciona". A fala de seleção dos companheiros foi confirmada no jogo, em três aberturas seguidas, cada uma sorteando entre 6 opções.
