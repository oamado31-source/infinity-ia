# SPEC-008 — Enciclopédia canônica e conhecimento individual dos NPCs

**Status:** APROVADA para implementação inicial (CR-2026-011, decisões D1–D12, 2026-11-15).
**Rastreabilidade:** CR-2026-011; ADR-0130; ADR-0023/0024/0056–0059/0071/0107/0109/0114/0116/0117/0119/0123/0124/0129; SPEC-003/004/005/006/007/009.

## Objetivo

Fazer dos NPCs fontes de conhecimento do mundo para o jogador, cada um limitado ao que sabe de forma legítima. Para isso, a SPEC separa quatro coisas:
- o **mundo curado**: cânone com fonte, ano DR e revisão;
- **quem é o NPC**: ficha, identidade e biografia;
- **o que ele sabe ou acredita**: a projeção de conhecimento por NPC;
- **o que aprende** depois de cada conversa.

**Princípio:** a base sabe mais que o NPC, e o modelo de linguagem nunca completa lacunas factuais.

## Escopo inicial

- **Corpus:** o pacote canônico existente, por ano DR (SPEC-005), com os valores atuais de `canon_entry_v1`:
  - `verification_status`: `RESEARCH_ONLY`, `CROSS_REFERENCED`, `SOURCE_CHECKED`, `DISPUTED`, `CAMPAIGN_CANON`;
  - `access_scope`: `CANON_REFERENCE`, `COMMON_REGIONAL`, `RESTRICTED`;
  - `audience`: `REGIONAL_PUBLIC`, `AFFILIATED`, `EXPLICIT_NPCS`.

  A classe de sigilo (SPEC-009) é o único campo novo, com migração versionada e padrão compatível.
  **Extensão pelo CR-2026-013:** o tipo de entrada `TOPIC` (prefixo `topic:`), para costumes, moedas, línguas, modos de falar e religião. Exige região, não tem área do jogo e não é ponta de relação. É conhecido pelas mesmas regras das outras entradas regionais.
- **Biografia:** a identidade curada atual (ADR-0117) mais eventos biográficos com local, intervalo DR, evidência e privacidade.
  - **Oficial:** só com respaldo.
  - **NPC gerado:** biografia fixada uma vez, persistida e versionada (D2); só vira `CAMPAIGN_CANON` depois de curadoria.
- **Conhecimento por NPC (`NpcKnowledgeHolding`, nome candidato):** referência à entrada, canal de aquisição, evento de evidência, momento de jogo, ramo, profundidade (`POPULAR`/`INFORMED`/`STUDIED`), estado epistêmico (`KNOWS`, `HEARD`, `RUMOR`, `SUSPECTS`) e atribuição da fonte.
  - Rumor, hipótese e crença existem **só aqui**, nunca no cânone.
- **Canais de aquisição:**
  - **existentes:** `ORIGIN`, `RESIDENCE` (só fora do grupo) e `INQUIRY` (companheiros);
  - **v1:** `DIRECT_DIALOGUE` (o NPC abordado, D10);
  - **depois:** `NPC_TO_NPC`;
  - **bloqueados até haver prova no host (D11):** `VERIFIED_OVERHEARING` e `NATIVE_DIALOGUE_CAPTURE`.
- **Notoriedade:** só episódios curados na v1 (D4), sem rolagens e sem o nível como fator (D5).
- **Privacidade (D12, ADR-0107 item 6):** a v1 não persiste texto do jogador; só IDs de entradas curadas casadas de forma determinística.

## Requisitos EARS

### Corpus e biografia

- **REQ-KNOW-001:** QUANDO uma obra for usada, DEVERÁ haver acesso legítimo, fonte localizada, classe, escopo de direitos e status de verificação; o texto da obra NÃO DEVERÁ entrar no repositório.
- **REQ-KNOW-002:** QUANDO fontes ou épocas divergirem, o sistema DEVERÁ preservar as alegações distintas (`DISPUTED`) e NÃO DEVERÁ afirmar uma delas sem resolução curada.
- **REQ-KNOW-003:** QUANDO um NPC consultar conhecimento, a recuperação DEVERÁ obedecer a campanha, ramo, ano DR, identidade, proveniência e canal de aquisição, **antes** de qualquer contexto de modelo.
- **REQ-KNOW-004:** SE um fato biográfico de NPC oficial não tiver respaldo, NÃO DEVERÁ ser gerado como cânone.
- **REQ-KNOW-005:** QUANDO um NPC gerado for confirmado, sua biografia DEVERÁ ficar estável entre sessões, recargas e ramos.
- **REQ-KNOW-006:** WIS e INT PODERÃO mudar a profundidade e a compreensão por regra versionada, mas NÃO DEVERÃO dar acesso a conhecimento nunca adquirido.
- **REQ-KNOW-007:** SE o pacote canônico mudar de revisão, o conhecimento já adquirido NÃO DEVERÁ ser reescrito em silêncio.

### Notoriedade (v1: só curada)

- **REQ-KNOW-008:** QUANDO a notoriedade de alguém for registrada, DEVERÁ referenciar a persona pública, os feitos ou relatos, as regiões e as épocas, com fonte, validade, status e escopo.
- **REQ-KNOW-009:** O nível ou o poder de um personagem NÃO DEVERÁ ser tratado como notoriedade nem exposto como conhecimento do observador.
- **REQ-KNOW-010:** QUANDO um feito de campanha mudar a notoriedade, a mudança DEVERÁ vir de evento confirmado e NÃO DEVERÁ se duplicar ao reprocessar saves.
- **REQ-KNOW-011:** QUANDO um relato circular, DEVERÁ preservar fonte, conteúdo alegado, região, tempo, estado epistêmico e persona, sem virar fato.

### Aprendizado em conversa

- **REQ-KNOW-012:** QUANDO uma fala **validada e publicada** transmitir uma entrada identificável a um ouvinte identificado, o sistema DEVERÁ avaliar a aquisição desse ouvinte. Uma pergunta, um rascunho, um ID só presente em `used_facts` ou uma resposta recusada pelo validador NÃO DEVERÃO ensinar nada.
- **REQ-KNOW-013:** QUANDO um NPC aprender, DEVERÁ registrar um evento causal com emissor, ouvinte, campanha, ramo, tempo, canal, entrada, estado epistêmico, revisão e chave idempotente, sem transcrição.
- **REQ-KNOW-014** (a partir da v2 de privacidade): SE a afirmação não tiver respaldo no estado do mundo, o sistema SÓ PODERÁ registrá-la como alegação atribuída, tipada e sem texto livre, e NÃO DEVERÁ promovê-la a `CAMPAIGN_CANON` ou `SOURCE_CHECKED`. **Na v1, gera `NO_ACQUISITION`.**
- **REQ-KNOW-015:** QUANDO só o nome de um terceiro for transmitido, o ouvinte PODERÁ passar a `HEARD_NAME`, sem biografia, feitos, atributos ou identidade ausentes da fala.
- **REQ-KNOW-016:** QUANDO o NPC for perguntado de novo depois de aprender, DEVERÁ recuperar o que aprendeu, com a atribuição ("você me contou", "Bernard me disse"), sem refazer a aquisição.
- **REQ-KNOW-017:** SE um NPC for só um possível espectador, NÃO DEVERÁ aprender sem prova de que podia ouvir e compreender; a escuta passiva e a captura de diálogo nativo ficam bloqueadas até prova técnica e política própria.
- **REQ-KNOW-018:** QUANDO surgirem relatos contraditórios, a memória DEVERÁ preservar os episódios anteriores e permitir revisão versionada de crença, sem tocar no cânone.
- **REQ-KNOW-019:** QUANDO uma fala for reprocessada (retry, reconnect ou save), NÃO DEVERÁ duplicar aquisições, e o que foi aprendido num ramo posterior NÃO DEVERÁ aparecer num ramo anterior nem em outra campanha.
- **REQ-KNOW-020:** QUANDO uma transmissão for elegível, os limites do `INQUIRY` e da política de divulgação (SPEC-009) DEVERÃO valer **antes** de conceder conhecimento, e `RESTRICTED` NÃO DEVERÁ se propagar por canal público.
- **REQ-KNOW-021:** QUANDO a fala do jogador for usada para aprendizado, o casamento com entradas curadas DEVERÁ ser **determinístico**, por nomes, aliases e predicado, **nunca por LLM**. Casamento parcial ou ambíguo DEVERÁ resultar em `NO_ACQUISITION`.
- **REQ-KNOW-022:** O texto do jogador NÃO DEVERÁ ser persistido pela v1 do aprendizado (ADR-0107 item 6). Só IDs de entradas casadas, atribuição, ouvinte, ramo, tempo e chave idempotente.

## Critérios de aceite do primeiro corte

1. Perguntado sobre um familiar que não está na ficha, o NPC não inventa ninguém.
2. Bernard responde fiel ao ofício curado.
3. O `INQUIRY` só ensina o que foi dito na fala publicada.
4. O jogador conta a um NPC um fato curado que ele desconhecia: o NPC aprende só essa entrada, atribuída ao PC, com recibo idempotente e sem texto do jogador persistido.
5. Ao fechar e reabrir a caixa, o mesmo NPC lembra o que aprendeu e de quem ouviu, sem improvisar mais nada.
6. Uma entrada só presente em `used_facts`, mas não enunciada, não ensina.
7. Uma resposta recusada pelo validador não ensina.
8. A mesma fala recebida duas vezes gera uma única aquisição por ouvinte e entrada.
9. Um save anterior à conversa não vê o que foi aprendido depois.
10. Um relato não confirmado do jogador gera `NO_ACQUISITION` na v1.
11. A suíte automatizada passa e a bateria de diálogo (`tools/dialogue-eval/`) continua passando. A validação no jogo fica pendente até o teste no laboratório.
