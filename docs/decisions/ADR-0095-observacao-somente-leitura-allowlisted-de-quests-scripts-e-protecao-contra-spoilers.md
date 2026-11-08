# ADR-0095 — DEC-100/C: observação somente-leitura, allowlisted e segregada de estados de quests e scripts

- **Data de aprovação:** 2026-11-07.
- **Decisão expressa:** **DEC-100/C**, aprovada pelo idealizador.
- **Status:** **APROVADA COMO ARQUITETURA — não implementada nem validada no BG2:EE/EEex**.
- **Discovery:** v9.6; preserva byte a byte **94 ADRs anteriores (ADR-0001…ADR-0094)** e todas as decisões DEC-060…DEC-099.
- **Contrato normativo:** `docs/100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md`.
- **Próxima questão:** DEC-101 — mapeamento semântico versionado de estados técnicos de quests em marcos narrativos, com ambiguidade e POCs por build.

## Problema e fronteira

BG2:EE, EEex e mods podem armazenar flags, globals, variáveis de cena, estado de diálogo e scripts cujo simples conteúdo antecipa traições, identidades ocultas ou ramificações futuras. A DEC-099/C proíbe writes indevidos por ownership; ela **não** concede automaticamente leitura, inferência de significado, publicação de flags ou acesso a uma LLM. A compatibilidade por build deve considerar **a operação de leitura específica**, o seu efeito real sobre o motor, o grau de cobertura, o modpack e a identidade do solicitante. `READ_ONLY` é característica comprovada do adaptador, não uma palavra que autoriza chamadas desconhecidas.

## Alternativas consideradas

- **A — Leitura irrestrita:** **REJEITADA**. O acesso global facilita spoilers, metaconhecimento, vazamento de identidades e perda de isolamento entre campanhas e saves.
- **B — LLM interpreta scripts/flags brutos e escolhe o que divulgar:** **REJEITADA**. O modelo não é um motor de permissão, pode inferir segredos por nomes de variáveis e alucinar significado de estados não observados.
- **C — Adaptadores somente-leitura, allowlist por build, liberação mínima por finalidade/ACL e separação de estados técnicos do conhecimento dos atores:** **APROVADA**.

## Invariantes obrigatórias

1. **Read-only demonstrável:** qualquer probe precisa constar em `ObservationCapabilityManifest`, com `build_fingerprint`, `modpack_hash`, ordem/versões de mods, `adapter_revision`, identificador de consulta, pré-condições, escopo e evidência de POC. Um probe nominalmente de leitura que aciona script, diálogo, evento ou side effect fica bloqueado. Sem POC específica não existe capability runtime.
2. **Allowlist positiva, default-deny:** apenas `probe_id`, tipo de consulta, variável e estágio explicitamente aprovados podem ser consultados. Wildcards de estado global, dump de script, inventário indiscriminado de flags, introspecção LLM e consultas por texto livre são proibidos.
3. **Solicitação tipada e restrita:** `ObservationRequest` declara finalidade permitida, destinatário/audiência, `campaign_id`, `branch_id`, `session_id`, `host_epoch`, `checkpoint_epoch`, build/modpack, revisão de adapter, quest/área e identificador semântico. O destino e o propósito precisam pertencer ao manifesto e a uma ACL válida.
4. **Menor exposição possível:** o adaptador devolve, quando autorizado, apenas marcos técnicos semanticamente limitados (`stage_completed`, `stage_not_completed` com prova suficiente, ou `UNKNOWN`), sem repassar nomes brutos de flags, roteiros, diálogos, triggers, IDs ocultos, endings ou caminhos futuros.
5. **Estado interno ≠ conhecimento narrativo:** a engine pode ter um flag verdadeiro enquanto nenhum NPC conhece sua causa. `ObservationEnvelope` fica numa zona técnica protegida. `SafeQuestProjection` só entra no contexto do destinatário quando houver liberação narrativa por finalidade, ACL, stage efetivamente alcançado e confirmação do direito de conhecimento. Nem host nem diretor narrativo recebe acesso universal por sua função.
6. **Proteção explícita de spoilers:** marcadores `QUEST_SECRET`, `FUTURE_BRANCH`, `HIDDEN_IDENTITY`, `ROMANCE_PRIVATE` e termos equivalentes ficam fora de prompts, logs, caches compartilhados, relatórios, dossiês, LAN e mensagens de cliente, salvo especificação separada e autorização legítima. Pistas indiretas como nomes de flag são tratadas como spoilers.
7. **Incerteza e cobertura:** ausência de observação, scanner parcial, hook indisponível, flag não encontrada, versão desconhecida ou leitura vencida significam `UNKNOWN`/`UNAVAILABLE`/`STALE`, nunca `FALSE`, quest concluída ou prova de ausência. `FALSE` só é permitido por mapeamento semântico curado e observação exaustiva comprovada do escopo.
8. **Sem invenção de semântica:** o mapeamento de flags brutas para marcos é **curado, versionado e ancorado em build/modpack/proveniência**. Estados sem significado validado não são interpretados automaticamente por LLM; DEC-101 aprofundará contratos para mapeamentos compostos, inconsistências e transições.
9. **Ciclo de vida e cache:** snapshots de observação vinculam host/checkpoint epochs, sessão, rama, fonte, revisão de adapter, monotonic sequence e cobertura. Cache é segregado por `campaign/branch/audience/purpose/build/epoch`, expira e é invalidado após checkpoint, restauração, transição de quest, mudança de build/modpack ou revogação de acesso; revogação não apaga memória já legitimamente recebida.
10. **Observação não é recibo mecânico:** uma leitura pode orientar planejamento, narrativa ou uma requisição de reconciliação, mas não confirmar execução de um comando do Infinity AI. O Action Gateway DEC-012 e host receipt DEC-011 mantêm a autoridade sobre efeitos físicos e regras de idempotência.
11. **Compatibilidade e ownership separados:** `READ` não significa `WRITE`; permitir observar uma etapa não autoriza alterar globais, NPCs, scripts, inventários, romances ou quests. Observar mod de terceiro depende de direito e capability verificável, ainda que DEC-099 o proteja contra mutação.
12. **Confinamento de dados não confiáveis:** nomes e textos de scripts/mods, inclusive strings legíveis, são **dados não confiáveis**, jamais instruções para agentes; normalize/escape saídas, rejeite prompt injection e não misture metadados brutos com contexto da LLM.
13. **Auditoria mínima:** registrar ids opacos, versão da policy, finalidade autorizada, resultado/status, cobertura e hashes de revisão, sem registrar valores brutos secretos. `DisclosureLedger` e `ObserverKnowledge` respeitam DEC-028/029/064/065/083/085/089/090.
14. **Falha fechada e segurança multiplayer:** clientes e agentes não podem alterar ACL, elevar audiência nem atestar POCs; host e policy service fazem o gate. Ausência de handshake, adaptador divergente, falha de criptografia ou conflito de revisão bloqueiam novas observações.
15. **Mundo e canon:** o índice físico `knowledge/periods/<ANO>-DR/` permanece inalterado. Uma flag de quest não transforma automaticamente a história de FR nem altera overlays de outras campanhas; decisões DEC-004/009/022/060–063 continuam vinculantes.
16. **Limite de evidência:** os exemplos Python e JSON da v9.6 são **somente simulações unitárias com fixtures artificiais**, sem acesso a BG2:EE/EEex. Os **124 testes T100-001..124 são candidatos NÃO EXECUTADOS**. Necessário POC por build com Windows, jogo base, EEex/bridge e depois dois clientes, cobertura observacional, save/load, spoilers e modpacks reais.

## Contrato de saída

`ObservationPreflight` produz `BLOCKED_NOT_ALLOWLISTED`, `BLOCKED_ACCESS`, `BLOCKED_SPOILER`, `BLOCKED_CAPABILITY`, `BLOCKED_KNOWLEDGE`, `STALE`, `UNAVAILABLE`, `UNKNOWN`, `OBSERVED_TECHNICAL_ONLY` ou `RELEASE_SEMANTIC_MINIMAL`; todos são **decisões somente-leitura**, sem disparar transições mecânicas. Nenhuma saída de erro deve conter valor de flag, nome confidencial de script ou estado de ramo futuro. `RELEASE_SEMANTIC_MINIMAL` representa conteúdo permitido a uma audiência específica — não transmissão consumada, nem compreensão ou conhecimento de NPC.

## Critérios de aceite ainda não demonstrados

- POC por `build_fingerprint/modpack_hash/adapter_revision/probe_id` comprova que leitura não modifica contadores, flags, scripts, cenas, romances, save ou multiplayer.
- Probes não aprovados, future branches e identidades ocultas jamais aparecem em LLM/logs/clientes; diretório de quest flags não é copiado para prompts.
- Observação de quest concluída usa mapeamento curado; ausência e scan parcial permanecem unknown; flags equivalentes e modificadas por mods não são adivinhadas.
- Restauração, troca de build, passagem de host epoch, perda de conexão e mudança de ACL invalidam cache e capacidade sem vazar observações antigas.
- Testes com 1 host + 2 clientes demonstram isolamento por audiência, branch e owner, com reconciliação auditável e zero mutações por probes.

## Vinculações preservadas

DEC-003/004 (modo e integração), DEC-009/022 (tempo/canon), DEC-011/012 (host/gateway), DEC-014 (LLM sob demanda), DEC-027/028/029 (risco, ACL e propagação), DEC-041/045/046 (agência/delegação), DEC-050/051/052 (quest/mod/versão), DEC-053/055/057/058/059 (checkpoint, logs, LAN, prompts), DEC-060–065 (curadoria/canon/memória), DEC-076/077/083–090 (segredos/evidências), DEC-096–099 (regras, composição, materialização e ownership). **Nenhuma dessas decisões é substituída.**
