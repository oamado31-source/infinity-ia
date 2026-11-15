# ADR-0128 — Voz dos NPCs e dos personagens: TTS local com vozes de escalação

**Estado:** SUBSTITUÍDA pelo [ADR-0129](ADR-0129-dialogo-so-texto-e-fala-padrao.md) em 2026-11-15, antes do merge. O plano foi aprovado pelo mantenedor em 2026-11-14 e testado no laboratório. O código de TTS saiu da branch.
**Origem:** a resposta do NPC só aparecia em texto. O ADR-0107 prevê TTS opcional (REQ-VOICE-003).
**Relaciona-se com:** ADR-0107 (política de voz), ADR-0127 (voz do jogador), ADR-0116 (caixa no jogo), SPEC-004 e REQ-CANON-004.
**Gate:** etapa 1, single player. Nada foi escrito no jogo.

## O que foi decidido e testado (2026-11-14)

1. **Limite:** nenhuma voz clonada nem derivada de gravações do jogo ou de dubladores.
   - **Fonte das vozes:** descrições escritas por nós e aprovadas de ouvido pelo mantenedor.
   - **Validação do elenco:** recusava campos além de `npc_id`, `voice` e `note`.
2. **Motores testados:**
   - **Qwen3-TTS** (Apache-2.0, local, `mlx-audio`): o VoiceDesign criava a voz a partir da descrição, e o Base falava imitando o clipe de referência. Foi o que soou muito melhor.
   - **Kokoro** (servidor de outro projeto, vozes `pf_dora`, `pm_alex` e `pm_santa`): ficou como reserva.
   - **Piper** (vozes CC0): instalado, mas não entrou no elenco.
   - **ElevenLabs** (remoto, opcional): nunca usado.
   - **Chatterbox Multilingual:** descartado, por soar pior na escuta e levar de 7 a 16 s por fala.
3. **Escolha da voz:** elenco curado (Imoen, Minsc, Jaheira, Bernard, Jierdan, Salvanas e Lehtinan), vozes de gente comum pelo gênero da ficha e uma voz para a fala digitada do personagem do jogador.
4. **Onde tocava:** no host do serviço, com `--tts`. A voz do NPC era gerada frase a frase, enquanto a anterior tocava.
5. **Sotaque:**
   - **Problema:** o Qwen3-TTS só tem o idioma "portuguese" e não separa Brasil de Portugal. Várias vozes puxaram para o português de Portugal ou para o inglês.
   - **Tentativas:** descrições pedindo sotaque brasileiro de forma explícita e textos de referência com marcas do Brasil.
   - **Achado medido:** o modelo Base imita o clipe, mas ignora a descrição e "normaliza" a voz. No Lehtinan, a periodicidade (valor baixo = mais sussurrado) subiu de 0,25 na candidata para 0,39 a 0,56 nas falas geradas, e o sussurro se perdeu.
   - **Contorno:** falar pelo VoiceDesign, com a descrição e uma semente fixa (modo `design`), devolveu o sussurro e o sotaque. Lehtinan e Salvanas foram aprovados no jogo assim.

## Por que foi substituída

O sotaque continuou incomodando nas vozes em português. O mantenedor decidiu seguir o padrão do jogo original (ADR-0129): diálogo só escrito e, ao abrir a caixa, a fala padrão da própria criatura, com o áudio do jogo.

**O que fica deste trabalho:** as melhorias de latência da caixa, medidas na evidência S1i:
- PowerShell permanente na VM e leitura incremental do log;
- `whisper-server`;
- lista de microfones guardada;
- regras fixas no início do prompt;
- `keep_alive` do modelo.

**O que saiu:**
- `src/infinity_ai/voice/tts.py` e `casting.py`;
- `knowledge/voices/`;
- `tools/tts-server/`;
- as ferramentas de escuta;
- `--tts` e as opções de voz no serviço;
- os testes correspondentes.
