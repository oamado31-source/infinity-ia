# ADR-0127 — Voz do jogador na caixa do jogo: push-to-talk e transcrição local

**Estado:** APROVADA (plano aprovado pelo mantenedor, 2026-11-14). Cobre só a fala do jogador. A voz do NPC (TTS) fica para um ADR seguinte.
**Origem:** o ADR-0107 (política aprovada) prevê push-to-talk opcional com STT local e texto revisável. A caixa do jogo (ADR-0116) já reservava o botão, e o protocolo já aceitava `input: VOICE`.
**Relaciona-se com:** ADR-0107 (política de voz), ADR-0116 (caixa no jogo), SPEC-004 (REQ-VOICE-001..004) e ADR-0005 (Windows nativo como plataforma final).
**Gate:** etapa 1, single player. Nada é escrito no estado do jogo.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-14.

1. **Onde o microfone abre:** no host do serviço de diálogo, nunca no jogo, já que Lua não captura áudio.
   - No laboratório, o host é o Mac em que o jogador está.
   - No Windows nativo, o serviço roda no mesmo PC do jogo, com o mesmo desenho.
   - **Escolha do microfone:** o embutido, pelo nome. O índice 0 pode ser outro aparelho, como o iPhone por Continuity. Dá para trocar com `--mic-device`.
2. **Protocolo** (mesmo canal de log e `override` da caixa):
   - **Caixa → serviço:** linhas `INFAI-PTT {"schema":"infinity-ai.ptt.v1","ptt_id","action":"START|STOP|CANCEL","session_seq","clock_ms"}`, lidas com parsing estrito.
   - **Serviço → caixa:** `override\INFAIPTT.lua` define só `INFAI_PTT_State = {ptt_id, state, text}`, com literais escapados. Os estados são `REC`, `TEXT`, `FAILED` e `CANCELLED`.
   - **Hash do modpack:** o arquivo fica em `override` desde o início do serviço (o motor só acha arquivos presentes ao abrir o jogo) e entra em `TRANSIENT_OVERRIDE`.
3. **Fluxo:**
   - "Falar" manda `START`, e a caixa mostra "Preparando o microfone…" até receber `REC`;
   - "Parar" manda `STOP`, o serviço transcreve, e o texto vai para o campo de edição;
   - o jogador revisa e envia, e o pedido sai com `input:"VOICE"`, pelo mesmo motor e o mesmo validador;
   - fechar a caixa manda `CANCEL`.
4. **Limites:**
   - a gravação para sozinha aos 20 s (`--max-voice-s`);
   - o nível de áudio abaixo de `--min-voice-level` é silêncio: o STT nem roda, para o Whisper não inventar palavras;
   - a caixa desiste sem `REC` em 10 s e sem texto em 40 s;
   - um pressionamento já presente no log quando o serviço inicia nunca abre o microfone, nem um de outra sessão do jogo ou com mais de 20 s em relação à última leitura da sonda (`fresh_ptt_signals`).
5. **STT:** whisper.cpp (`whisper-cli`, MIT, Metal no Mac e CPU/GPU no Windows), atrás da porta `SttProvider` (`src/infinity_ai/voice/stt.py`).
   - **Configuração:** português (`-l pt`) e um vocabulário de nomes públicos do pacote canônico (`--prompt`), que acerta a grafia de "Athkatla" e "Coroa de Cobre".
   - **Modelo padrão:** Whisper large-v3-turbo q5_0 (574 MB, SHA-256 `394221709cd5…ffa7e2`), em `~/.infinity-ai/models/`, fora do repositório.
6. **Privacidade (ADR-0107, itens 4 e 6):**
   - o áudio vai para um diretório temporário `0700`, apagado logo depois da transcrição, em qualquer resultado;
   - nada é gravado em repouso;
   - o log registra só metadados (`voz ptt=… estado=TEXT duracao=… stt=… nivel=… chars=…`), sem a transcrição.
7. **Memória:** o serviço pede ao Ollama `num_ctx` de 8192. Sem isso, o `qwen3:30b-a3b` carrega com contexto de 262144 (45 GB) e tira memória do STT. Com o limite, ocupa 19 GB.
8. **Desligado por padrão:** a voz só funciona com `--voice` no serviço. Sem ela, a caixa avisa que o microfone não respondeu, e o texto continua funcionando (REQ-VOICE-004).

## Comparação de modelos

`tools/voice-eval/run_stt_eval.py`: 12 frases nossas no estilo da caixa (`tests/voice_eval/phrases.pt_BR.json`), M1 Max.

**Vozes sintéticas pt-BR do macOS (3 vozes × 12 frases), só um teste de fumaça:**

| Modelo | Vocabulário | Erro de palavras | Nomes certos | Tempo médio |
|---|---|---|---|---|
| large-v3-turbo q5_0 | não | 26,7% | 8/33 | 0,83 s |
| large-v3-turbo q5_0 | sim | 22,3% | 15/33 | 0,83 s |
| small | não | 37,5% | 7/33 | 0,47 s |
| small | sim | 29,7% | 17/33 | 0,48 s |

As vozes sintéticas soletram "Amn" ("a-eme-ene"), o que derruba os nomes nos dois modelos. A comparação com a voz do mantenedor (`--record` e `--recorded`) continua pendente.

## Evidência de laboratório (S1h, 2026-11-14)

Três perguntas por voz a Bernard, na Coroa de Cobre, transcritas sem erro pelo turbo e respondidas sem recusas. A transcrição levou 1,6 a 1,7 s; a gravação, 12 a 18 s, contando a espera da leitura do log. Detalhes em `docs/evidence/S1h-2026-11-14-voz-ptt-arm64.md`.

**Corrigido durante o teste:**
- **Transcrição lenta (26,8 s):** falta de memória com o contexto padrão do Ollama; resolvida com o `num_ctx` (item 7).
- **Microfone aberto sem clique:** um serviço reiniciado tratou dois pressionamentos antigos como novos, e o microfone abriu sozinho por 2 a 3 s, em silêncio. O áudio foi apagado e o STT não rodou. Resolvido com o filtro de frescor (item 4).

## Consequências

- **Código:**
  - `src/infinity_ai/voice/` (`capture.py`, `stt.py`, `session.py`);
  - `src/infinity_ai/dialogue/llm.py` (`num_ctx`);
  - `src/infinity_ai/bridge/talk.py` (`parse_ptt_signals`, `render_ptt_state`);
  - `tools/eeex-probe/M_INFAIT.lua` e `INFAITLK.menu` (botão "Falar");
  - `tools/windows-lab/dialogue_service.py` (`VoiceListener`, `--voice`; o log da caixa ganha `entrada=`);
  - `tools/voice-eval/run_stt_eval.py`.
- **Testes:**
  - `tests/test_voice.py` (sessão, captura, STT; fumaça com `say` quando há modelo);
  - `tests/test_talk.py` (protocolo e a caixa rodando em Lua com o motor simulado).
- **Laboratório:** trocar a caixa muda o hash do modpack, então é preciso fixar um manifesto novo.

## Riscos e limites

- **Atraso:** o serviço lê o log do jogo por SSH a cada 3 s, então "Preparando o microfone…" pode durar alguns segundos, e a gravação leva alguns segundos de silêncio no fim. No Windows nativo, a leitura é local.
- **Permissão:** na primeira gravação, o macOS pede permissão de microfone para o app que roda o serviço. Só o jogador pode aprovar.
- **Nomes que só aparecem no começo de frase** nos resumos públicos não entram no vocabulário. O vocabulário é só um viés, e a revisão do texto corrige o resto.
- **Não é comando:** a transcrição é texto para revisar (REQ-VOICE-002) e passa pelo mesmo validador da fala digitada.
