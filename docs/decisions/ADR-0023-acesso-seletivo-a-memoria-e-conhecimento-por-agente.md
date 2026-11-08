# ADR-0023 — Memória compartilhada com acesso seletivo por agente

- **ID da decisão:** DEC-028
- **Status:** **APROVADA — opção B**
- **Aprovação:** 2026-11-06, escolha expressa do idealizador do Infinity AI.
- **Objetivo:** evitar onisciência e vazamento de históricos/segredos; alimentar NPCs e especialistas com o contexto mínimo ao qual têm direito.
- **Ligação:** DEC-019/ADR-0003 (público e secreto), DEC-020 (retcons e versões), DEC-008/ADR-0011 (eventos e snapshots), DEC-009/ADR-0012 (canon), DEC-014/ADR-0008 (orquestração), DEC-011 (host), DEC-012/ADR-0022 (fronteira de execução), DEC-027 (riscos), DEC-021/022 (simulação e tempo).

## Contexto e alternativas

A memória persistente do Living World contém históricos privados, fatos públicos, segredos revelados, rumores imprecisos, eventos mecânicos confirmados e informações de narrador. Um NPC não deve receber tudo apenas porque o banco de dados contém essas informações. Prompting para “não revelar” depois de entregar segredos ao modelo é proteção insuficiente.

- **A — Contexto integral filtrado só na resposta:** rejeitada; expõe dados que o modelo não deveria receber.
- **B — Memória compartilhada com autorização na leitura:** **aprovada**; armazenamento estruturado comum, projeções por destinatário e composição de contexto antes do LLM.
- **C — Banco independente por NPC:** rejeitada como requisito; múltiplos bancos completos dificultam consistência, propagação e auditabilidade. Isolamento lógico pode existir mesmo com armazenamento comum.

## Decisão

1. **Memória global estruturada e persistente:** armazenar fatos, histórico de eventos, origem e projeções sem conferir aos NPCs ou agentes permissão automática sobre toda a base. A arquitetura deve prover isolamento lógico por modo, campanha e personagem, mesmo quando compartilha infraestrutura física de armazenamento.
2. **Autorização antes da recuperação e do contexto:** uma camada de política de conhecimento define fatos visíveis a um **destinatário específico** (NPC, personagem de jogador, jogador fora de personagem, módulo narrativo ou agente especializado), com **identidade, campanha, finalidade, instante e fonte** antes da consulta, resumo, busca semântica ou composição do prompt. **Não usar um LLM como controle primário de acesso.**
3. **Três dimensões independentes:** (a) visibilidade editorial do histórico de um jogador (público/privado), (b) conhecimento diegético de personagens dentro da ficção e (c) privilégio operacional do sistema/narrador. Ser público ao jogador não equivale a ser conhecido por todos os personagens; um agente de execução não recebe automaticamente o conhecimento do narrador.
4. **Proveniência e evidências:** a atribuição de conhecimento deve basear-se em fatos legitimados, como testemunho, comunicação, descoberta, documento acessado, investigação ou rumor recebido. Manter origem, destinatário, período, escopo e grau de confirmação/confiabilidade quando relevantes; distinguir **fato**, **crença/suspeita**, **rumor** e **afirmação falsa** sem reclassificar automaticamente como verdade.
5. **Acesso do narrador com mínimo necessário:** o narrador/orquestrador pode usar um histórico secreto autorizado para planejar ganchos individuais, mas jamais transferi-lo diretamente a um NPC ou a outros jogadores. Privilegios ampliados têm escopo e finalidade definidos; uma tarefa que não requer o segredo não deverá recebê-lo.
6. **Atualização causal:** a descoberta ou divulgação válida cria/atualiza um evento de conhecimento no contexto da campanha, com identidades e temporalidade. Propagação posterior **não é automática para todo o mundo**: depende da política a decidir em DEC-029. Se uma fonte recebe retcon (DEC-020), preservar fatos in-world já confirmados até tratamento autorizado.
7. **Negações e separações obrigatórias:** ausência de fonte, destinatário errado, campanha errada, finalidade não permitida, contexto temporal incompatível ou identidade ambígua -> negar a recuperação. A política de leitura não concede poderes de escrita/execução; DEC-012 continua governando mudanças de estado.
8. **Proteção de canais secundários:** resumos, memórias de curto prazo, embeddings, caches, respostas de busca, diálogos, interfaces, telemetria, logs e erros não podem vazar dados que o destinatário não pode ler. Preferir filtragem prévia à recuperação, indexação isolada ou mecanismo com garantia de filtragem e auditoria; evitar enviar corpus global bruto ao LLM.
9. **Texto do mundo é dado não confiável:** conteúdo de NPCs, histórico de jogador, arquivos de mod ou uma resposta de modelo não altera ACL por instrução em linguagem natural. O gateway rejeita tentativas de elevar privilégios ou forjar proveniência sem evento validado.
10. **Desempenho:** utilizar consultas indexadas, cache por escopo/política/versão e projeções compactas. Não executar LLM por NPC/tick para construir conhecimento. Em caso de falha da política, **falhar fechado** e responder com informação pública ou desconhecimento, nunca com segredo.
11. **Modo Original separado:** nenhuma recuperação de memória do Living World deve modificar nem contaminar o modo Original, seus prompts e saves.
12. **Validação ainda necessária:** a decisão estabelece os invariantes lógicos; os schemas, ACLs efetivas, modelo de dados, política de retenção, logs técnicos, integração com BG2:EE, sincronização multiplayer e tratamentos de rumores não estão implementados nem comprovados.

## Caminho conceitual aprovado

```text
Fatos e eventos compartilhados (campanha, tempo, proveniência, classificação)
         |
Request: identity + purpose + recipient + campaign + current_world_time
         |
   Knowledge Policy Engine (regras determinísticas, default deny)
         |
Authorized retrieval / permitted fact IDs & scopes
         |
Context builder (minimização + citações de origem + limites)
         |
NPC/agent local LLM (quando necessário) ou regra/FSM
         |
Validação narrativa + publicação por risco (DEC-027) + Action Gateway (DEC-012)
```

O fluxo é um **alvo de arquitetura**, não uma API testada.

## Estrutura mínima candidata (não é schema final)

- **Fato**: `campaign_id`, `fact_id`, `subject`, `predicate`, `claim`, `source_event_id`, `occurred_at_dr`, `truth_status`, `classification`, `version`.
- **Conhecimento/atribuição**: `recipient_id`, `fact_id`, `acquisition_event_id`, `acquired_at_dr`, `channel`, `belief_strength`, `confidence`, `scope`, `expiry_or_revocation` se aplicável.
- **Consulta**: `request_id`, `campaign_id`, `actor_id`, `agent_role`, `purpose`, `current_time`, `rule_profile`, `policy_version`, `max_context`.
- **Saída**: somente `authorized_facts` com rótulos fato/rumor/suspeita e proveniência acessível ao destinatário; dados secretos ausentes do texto e dos metadados entregues.

Tais campos são **candidatos para SPECS**, não decisões sobre criptografia, formato físico de banco ou tecnologias específicas.

## Critérios de aceitação candidatos

1. NPC comum desconhece uma identidade secreta sem fonte legitimadora; não recebe nem o texto nem embeddings/resumos deriváveis do segredo.
2. Um espião pode conhecer uma suspeita registrada sem que ela seja promovida a verdade canônica.
3. Um jogador pode ler informação **publicada no perfil** de outro jogador, mas seu personagem e NPCs não passam a conhecê-la automaticamente.
4. Um narrador pode recuperar segredo para planejar missão particular, mas proposta publicada ao grupo é redigida conforme destinatário e contexto.
5. NPC que presenciou revelação obtém o fato após evento confirmado e continua a reconhecê-lo depois de save/load; NPC distante não o obtém por contágio automático.
6. Retcon não apaga retroativamente conhecimento validado in-world sem política/consentimento DEC-020.
7. Dados de campanha A não aparecem em consultas da campanha B nem do modo Original, mesmo em caches e histórico de recuperação.
8. Prompt injection em um diálogo ou livro não consegue alterar permissões nem adicionar fatos falsamente confirmados.
9. Erro de consulta/ACL não revela conteúdo por mensagens de exceção, telemetria, logs ou tokens recuperados.
10. Sob carga com muitos NPCs, o motor de políticas funciona por código/cache e LLM só é acionado para tarefas abertas, respeitando DEC-014.
11. Conhecimento adquirido depois da data da campanha não pode ser recuperado para cenas históricas anteriores (sem exceção narrativa justificada).
12. Multicliente: dois jogadores recebem somente informações autorizadas para a própria identidade e campanha; não inferir que a bridge suporta isso sem POC.

## Riscos e consequências

- **Benefício:** continuidade com conhecimento causal, segredos e rumores verossímeis; menor uso de tokens; histórico auditável.
- **Custo:** exige política de acesso independente, indexação segura, observabilidade restrita e reconciliação de retcons/rumores.
- **Perigo:** confiar apenas em instrução do modelo gera vazamentos; uma busca vetorial sem filtros pode contaminar o contexto.

## Itens deliberadamente em aberto

- **DEC-029 (próxima):** propagação de rumores, notícias e segredos entre NPCs/regiões, com tempo, canais e confiabilidade.
- Granularidade exata de rótulos, regras de expiração/revogação e critérios para memória falsa/esquecimento.
- Interface de visibilidade, armazenamento/criptografia, retenção, modelo semântico e consentimento de serviços remotos (DEC-006).
- Mapeamento técnico de personagens e sessões no multiplayer BG2:EE/EEex, sem promessas de viabilidade testada.
