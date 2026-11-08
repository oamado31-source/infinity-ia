# Domain — Contexto e regras de negócio

## Visão
Infinity AI é a camada independente que acrescenta mundo narrativo persistente, memória contextual, cronologia oficial curada e interações opcionais a campanhas privadas cooperativas BG2:EE, preservando a autoria do host, a agência dos jogadores e a integridade do jogo original.

## Contextos delimitados (*bounded contexts*)

| Contexto | Propriedade | Não autorizado |
|---|---|---|
| Game Observation | Leituras allowlisted pinadas à build | Modificar flags/scripts/quests |
| Host Action Gateway | Validar propostas e recibos do host | LLM operar motor diretamente |
| Narrative & Knowledge | Histórias, crenças, memória por NPC e visibilidade | Conhecimento global instantâneo |
| World Chronology | Ano DR, regiões, eventos/canon | Alterar eventos irreversíveis sem política |
| Campaign State | Campanha, branch, epochs e snapshots | Misturar saves ou overwrite silencioso |
| Speech Interaction | STT push-to-talk e TTS opt-in | Captura contínua de microfone |
| Multiplayer Identity | Identidade/consentimento dos PCs e host | Delegação sem prova |
| Mod/Content Governance | Manifests, licenças, proveniência | Redistribuir assets protegidos |

## Regras invariantes
1. Verdade observada != conhecimento de NPC; fato narrativo != flag mecânica.
2. Proposta != autorização != ação despachada != recibo confirmado.
3. Valor desconhecido nunca equivale a ausência/negativa demonstrada.
4. PC ausente mantém agency; alterações sensíveis exigem titular + host.
5. A cronologia parte do recorte 1369 DR e mapas observáveis BG2:EE, ampliável por versionamento.
6. Primeira demonstração: host + 2 clientes, read-only, NPC com memória, save/load e auditoria, sem efeitos não autorizados.

## Fora do MVP
Mundo público massivo, reescrita universal de quests, GemRB como motor obrigatório, todas as regiões FR, geração procedural ao vivo, economia granular global, escrow mecânico sem capability, combate por turnos sem prova.
