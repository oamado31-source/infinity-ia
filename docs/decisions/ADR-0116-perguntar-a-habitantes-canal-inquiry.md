# ADR-0116 — Perguntar a habitantes: canal INQUIRY e habitantes pelos dados do jogo

**Estado:** APROVADA (decisões explícitas do mantenedor, 2026-11-09).
**Origem:** ADR-0114 deixou `INQUIRY` reservado; regra do mantenedor: companheiros só aprendem o que é comum numa região perguntando a quem sabe.
**Relaciona-se com:** ADR-0115 (matriz de personalidade, PROPOSTA) e SPEC-006: esta decisão fornece o produtor real de `NpcDialogueStarted` e usa o perfil de primeiro contato na fala.
**Substitui parcialmente (sem editar):** ADR-0114, item 3 (prazo de residência), só para habitantes colocados pelo jogo; ADR-0114, item 5 (`INQUIRY` reservado), que passa a ser concedido.
**Gate:** etapa 1 (single player, ADR-0113). A caixa de diálogo no jogo é capability nova do EEex, sujeita a POC no laboratório. Testes sintéticos não a comprovam.

## Contexto

Pelo ADR-0114, nenhum companheiro sem origem curada sabe o conhecimento comum de uma região. O canal que falta é o ato de perguntar a alguém do lugar.

O mantenedor decidiu:
- a pergunta é feita dentro do jogo, numa caixa no estilo do diálogo nativo, com texto livre em vez de uma lista de opções;
- os habitantes que sabem são as criaturas que o próprio jogo coloca nas áreas da região;
- aprendem os companheiros que estão no mesmo ambiente;
- o probe confirma quem está presente.

## Alternativas consideradas

- **A — Observar o diálogo nativo do jogo:** o motor não informa o assunto da conversa; não serve como prova do que foi dito. Rejeitada.
- **B — Perguntar pelo overlay externo:** funciona, mas tira o jogador da tela do jogo. Fica como alternativa se a caixa no jogo falhar.
- **C — Caixa de diálogo no jogo, com texto livre, falando com quem está sob o cursor:** **selecionada.**

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-09.

1. **Habitantes pelos dados do jogo.**
   - **Quem conta:** as criaturas que os arquivos da instalação local (ARE e CRE) põem numa área ligada a uma região do pacote. Ficam de fora inimigos (EA ≥ 200) e quem não é humanoide (animais, monstros).
   - **Inventário:** é gravado só fora do repositório (REQ-CANON-004).
   - **Identidade:** `npc:<script name>`, ou `npc:cre-<resref>` quando a criatura não tem script name.
   - **Conhecimento:** são residentes **estabelecidos** (`RESIDENCE` com evidência `GAME_DATA:<área>#<cre>@<build>`) e sabem o que é comum na região mais específica onde estão e nas regiões ancestrais, a partir do pin, sem o prazo do ADR-0114 item 3.
2. **Caixa de diálogo no jogo** (`tools/eeex-probe/M_INFAIT.lua` + `INFAITLK.menu`).
   - **Abertura:** com o cursor sobre uma criatura fora do grupo, uma tecla (F9, configurável) abre um painel com nome, histórico, campo de texto e os botões Enviar e Sair.
   - **Pedido:** o texto sai pelo console como `INFAI-TALK {json}`. A linha leva falante (script name, CRE, nome, se está vivo), área, tempo e os **ouvintes**: os companheiros dos retratos 1–5 dentro do alcance visual (448) e com linha de visão do falante.
   - **Resposta:** volta pelo arquivo `override/INFAIRSP.lua`, que define só uma tabela com o id do pedido e um texto escapado; nada do modelo vira código no jogo. O arquivo existe desde a abertura do jogo (o motor só acha arquivos do `override` presentes nessa hora) e fica fora do hash do modpack. Antes de cada leitura, a caixa descarta o recurso do cache (`EEex_Resource_Fetch` + `dimmDump`, como faz `EEex_Menu_Eval`), porque o motor guarda o conteúdo lido na primeira vez. O overlay repete a última troca, como alternativa.
   - **Sem efeito no jogo:** a caixa não altera variáveis, diário, diálogos nem save.
   - **Voz depois:** a caixa reserva o botão "aperte para falar" (ADR-0107) para a etapa de voz da SPEC-004; o protocolo já tem o campo `input` (`TEXT`, `VOICE` reservado).
3. **Quem pode responder.** Qualquer pessoa viva sob o cursor, fora do grupo (SPEC-006: NPC é qualquer pessoa encontrada).
   - **O que sabe:** só o conhecimento comum que adquiriu (itens `K`, sem memórias do grupo); quem não é habitante pelo item 1 não sabe nada da região e responde que não sabe.
   - **Presença:** um habitante só responde numa das áreas onde o jogo o coloca.
   - **Personalidade (SPEC-006):** cada pedido da caixa é gravado como `NpcDialogueStarted` (observação, sem texto) e passa pelo `FirstContactService`. Criatura **sem** script name é `CANDIDATE`, e o id da instância no motor é o token da cena: perfil temporário, estável para aquela pessoa na mesma sessão e área, nunca persistido. Criatura **com** script name é um indivíduo do jogo: `CANONICAL`, sem sorteio, e fala com estilo neutro até haver curadoria (SPEC-005). `VERIFIED` nunca é produzido aqui.
   - **Efeito do perfil:** só define o estilo da fala e a orientação do alinhamento; não acrescenta fatos.
4. **Canal `INQUIRY`.** Quando a fala validada do habitante usa entradas `K`:
   - cada ouvinte que é companheiro no grupo naquele momento aprende **só essas entradas**, e só as que a fala de fato nomeia (alguma palavra do título da entrada); entrada declarada pelo modelo mas ausente da fala é recusada (`NOT_SPOKEN`);
   - o falante precisa ter a entrada no ramo, e nunca pode ser membro do grupo (companheiro não ensina companheiro);
   - um evento `KnowledgeShared` (`CAMPAIGN_OBSERVATION`), **sem texto**, com falante, ouvintes, entradas e revisão, é o gatilho;
   - o pedido é idempotente pelo id;
   - a visibilidade segue o ramo (ADR-0114 item 7);
   - recusas tipadas: `SPEAKER_IN_PARTY`, `SPEAKER_DOES_NOT_KNOW`, `NOT_SPOKEN`, `NOT_A_LISTENER`, `NOT_PINNED`.
5. **Privacidade.** O texto do jogador passa pelo log do jogo (recriado a cada abertura) e só fica na memória do serviço; o console do serviço registra só metadados (ADR-0107 item 6).

## Consequências

- Companheiros passam a aprender conhecimento comum só perguntando a habitantes, como pede a regra do mantenedor.
- Testes: `tests/test_common_knowledge.py`, `tests/test_talk.py` (protocolo, módulo Lua e primeiro contato) e `tests/test_gamedata.py` (ARE/CRE sintéticos).
- Regra prática a revisar: "tem script name" como sinal de indivíduo do jogo (`CANONICAL`). Ela deixa figurantes com script genérico sem perfil, e figurantes nomeados sem script (Bernard) com perfil temporário.
- O transporte do laboratório (`lab_ssh.run_ps`) passou a enviar a entrada padrão em uma linha. `ReadToEnd()` travava de forma intermitente acima de ~4 KB.

## Contratos e SPECs vinculadas

SPEC-003 (`share_knowledge`, `residents_as_stays`), SPEC-004 (`build_resident_context`, `respond_resident`, caixa no jogo), SPEC-006 (`src/infinity_ai/personality/in_game.py`: `record_dialogue_start`, `profile_for`), SPEC-005 (inventário de habitantes, `src/infinity_ai/gamedata/`), SPEC-001 (protocolo `INFAI-TALK`, `src/infinity_ai/bridge/talk.py`).

## Evidências, riscos e hipóteses não verificadas

- Evidência: `docs/evidence/S1e-2026-11-09-laboratorio-arm64.md` (single player).
- Verificado no laboratório (S1e): menu com campo de texto, criatura sob o cursor, ouvintes com linha de visão e leitura da resposta (depois de descartar o cache). Não verificado: perfil temporário da SPEC-006 com uma pessoa sem script name.
- Risco: habitantes colocados pelo jogo podem já ter morrido ou saído; o probe confirma que estão vivos, mas não confirma o horário de presença (agenda do ator).
- Risco: o log não é autenticado (qualquer mod pode imprimir `INFAI-TALK`). Isso serve ao laboratório, não ao multiplayer.
