# ADR-0067 — Catálogo modular de encontros e componentes validados por build

- **Decisão:** DEC-072 — **opção C**, escolhida expressamente pelo idealizador em 2026-11-06.
- **Estado:** **APROVADA como arquitetura de Discovery v6.8, NÃO IMPLEMENTADA**. Nenhum catálogo executável, template, adapter de spawn, script dinâmico, mod pack ou POC multiplayer foi comprovado.
- **Documento técnico:** `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos T072-01..48; nenhum executado**).
- **Preservação vinculante:** DEC-060 a DEC-071 e os respectivos ADR-0055 a ADR-0066 **inalterados**. Permanecem aplicáveis DEC-003/005-E/010/011/012/015/017/027/033/034/050/051/052/053/056.

## Contexto e problema

A DEC-071 permite a transição controlada de um incidente pendente para uma **oportunidade** de encontro local, mas não autoriza inventar um mapa, criar NPCs ou assumir que um script está disponível e seguro em determinada instalação de BG2:EE. Builds com EEex, EET e mods podem divergir radicalmente. A composição precisa aproveitar recursos existentes, ser compatível com scripts/quests/romances, garantir acesso legítimo a assets e não comprometer o estado compartilhado em multiplayer.

## Alternativas e escolha

- **A — Apenas encontros nativos preexistentes:** rejeitada como restrição permanente; não permite expansões compatíveis preparadas e testadas.
- **B — Gerar livremente componentes, scripts, NPCs e encontros durante a sessão:** rejeitada como padrão; supõe capacidades não demonstradas da Infinity Engine e expõe saves, conteúdo e multiplayer a riscos inaceitáveis.
- **C — Catálogo modular de templates, componentes e adapters validados por build, com expansão offline controlada:** **APROVADA**. Seleção condicionada por manifesto, proveniência, capability e gates de validação; novos recursos são preparados e testados fora da campanha antes de habilitação. Geração runtime de engine não está aprovada e só poderá ser discutida após POCs e decisão apropriada.

## Regras vinculantes

1. **Catálogo explícito, não geração arbitrária.** O sistema manterá, para cada build validada, templates de encontro e componentes tipados: áreas, atores/creatures, diálogos, comportamentos, encontros, gatilhos, scripts/adapters e regras de limpeza. Identificadores de catálogo não provam que a engine suporta sua execução.
2. **Inventário vs capacidade comprovada.** Separar `DISCOVERED`, `PRESENT`, `STATIC_VALIDATED`, `POC_VERIFIED`, `HOST_MP_VERIFIED`, `UNSUPPORTED` e `STALE` (vocabulário candidato, sujeito a SPECS). Presença de `.CRE`, `.ARE`, `.DLG`, `.BCS` ou outro asset não equivale a capacidade de spawn, injeção, substituição ou disparo seguro.
3. **Manifesto por build.** `build_fingerprint`/manifest DEC-051 deve incluir, conforme permitido, versão do jogo, EEex, expansões, ordem de mods, overrides, hashes, dependências e provenance. Divergência de build invalida a elegibilidade, inclusive entre host e clientes. Nenhuma versão é declarada compatível sem testes.
4. **Templates com contrato de escopo.** Cada `EncounterTemplate` declara `template_id`, revisão imutável, categoria, participantes elegíveis, recursos/áreas/regras, restrições de horário/região, pré-condições, efeitos máximos e riscos permitidos. Não presumir que uma composição textual altera assets reais.
5. **Componentes com origem, direitos e dependências.** Cada `EncounterComponent` aponta para identificador de recurso, mod de origem, versão/hash, condições de licença, dependências, conflitos, capacidade validada, ciclo de vida e permissões de uso. Não redistribuir obras, DLC/mods ou recursos protegidos sem autorização.
6. **Adapters testados por capability.** A execução de qualquer componente local exige adapter tipado explicitamente testado para a função e build. Adapters desconhecidos, desativados ou `STALE` não podem executar ações; nenhum Lua, shell, escrita direta em save ou script arbitrário gerado por LLM.
7. **Composição como proposta.** O diretor de encontros/LLM pode escolher entre templates conhecidos e sugerir parâmetros dentro de limites; a composição não se torna execução nem evento ocorrido antes da validação e confirmação pertinente.
8. **Vinculação causal a incidente.** Preservar `incident_id` DEC-070/071, `encounter_proposal_id`, template revision, autoria, `campaign_id`, `branch_id`, `checkpoint_epoch`, `build_fingerprint` e `idempotency_key`. É proibido criar nova causalidade paralela para o mesmo incidente.
9. **Reserva e não duplicação.** A DEC-071 continua controlando `LOCAL_RESERVED`, fencing, `resolution_epoch`, ledger e exclusão offscreen/local. Aprovação de composição não equivale a aquisição do direito de resolver nem libera a reserva automaticamente.
10. **Área realmente utilizável.** Região canônica e diretório anual não provam que existe área carregável na build. Exigir condição verificável de área, instância, scripts e presença de party pelo host; mapa inexistente gera `UNSUPPORTED`/alternativa narrativa.
11. **NPCs e instâncias.** DEC-066 exige identidade verificada para personagens persistentes; nomes, CRE, sprites, coordenadas e modelos iguais não autorizam atribuir lembranças ou gerar uma cópia. Ator preexistente e ator composto não devem coexistir como duplicatas causais.
12. **Compatibilidade nativa DEC-050.** Templates devem declarar pré-condições de missões, scripts, romances, diálogos, flags e interações; conflitos desconhecidos bloqueiam execução. Não alterar conteúdo original in situ sem POC específica e migração validada.
13. **Gates de risco e agência.** LOW narrativa allowlisted; MEDIUM avaliação/autorização; HIGH default-deny e approvals/receipts quando aplicável (DEC-027/034/070/071). Template aparentemente benigno com efeitos acumulados de alto impacto é reclassificado. Consentimento multiplayer e política de jogadores ausentes não são inferidos pelo modelo.
14. **Host autoridade mecânica.** Apenas host pode confirmar presença, spawn, combate, HP, XP, inventário, loot, quests e estados de engine; workers e clientes não confirmam efeitos. Gateway DEC-012 somente com ações tipadas comprovadas e receipt DEC-011; `UNCERTAIN` falha fechado.
15. **Revisões e imutabilidade.** Catálogo e templates terão revisões imutáveis, associadas ao build; mudanças exigem nova revisão e análise de diff/impacto no incidente/campanha. Templates usados em encontros pendentes não são alterados silenciosamente.
16. **Preparação offline controlada.** Assets e encontros personalizados serão criados/importados em workspace isolado, com verificação de integridade, malware/entrada, licenças, dependências, conflitos, testes offline, backups e rollout reversível comprovado antes de publicação. Nenhum download/instalação automática silenciosa no host ou nos clientes.
17. **Conhecimento histórico isolado.** DEC-060 mantém **diretórios físicos por ano DR**; DEC-061/062 curadoria/proveniência; DEC-063 fixa Knowledge Packs. Os templates são conteúdo operacional distinto do cânone e de memórias NPC. Eventos e efeitos somente em overlay privado da campanha/ramo, nunca na base histórica anual.
18. **Degradação segura.** Sem template/adapters elegíveis ou sem orçamento do RPD DEC-056, manter proposta pendente ou alternativa narrativa segura. Não criar combate, loot, área, NPC ou fala supostamente executada para mascarar impossibilidade técnica.
19. **Observabilidade e recuperação.** Registrar seleção, proveniência, versão, decisão de compatibilidade, riscos, gating, operação host, receipts e estado de incidentes, com redação de segredos. Checkpoints, backups, monitoramento e migração DEC-052/053/054/055 precedem habilitação em sessões persistentes.
20. **Aplicação incremental.** Primeiro inventário passivo em BG2:EE limpo, depois adapters read-only, POCs offline isoladas, teste de um template benigno permitido, restore/save/load, host+dois clientes, e só então expansões com flags positivas. Implementação real pode nunca suportar determinadas classes de componente.

## Trade-offs

- **Benefícios:** crescimento controlado de variedade de encontros, rastreabilidade de assets, previsibilidade de instalação e condições explícitas para compatibilidade multiplayer.
- **Custos:** manutenção de manifests, revisões, curadoria, packaging, testes por build e múltiplos adapters; um mod atualizado pode tornar templates indisponíveis.
- **Limite consciente:** o catálogo pode armazenar ideias sem capability executável; documentação de suporte não é evidência de funcionamento. A opção C não autoriza runtime codegen nem redistribuição de materiais de terceiros.

## Evidência e critérios futuros

Esta decisão é **aprovação de projeto**, não teste. Especificar na SPECS o esquema final de manifests e templates, regras de licença/proveniência, matriz de capabilities, atomicidade de resolução, estratégia de empacotamento, rollback seguro e comprovação com host + dois clientes. Documento 72 propõe **48 testes T072-01..48, todos NÃO EXECUTADOS**. Não há prova de spawn, alteração de scripts, multiplayer, instalador ou compatibilidade EEex/EET/NWNForBG.

## Próxima decisão — DEC-073 (em aberto)

**Ciclo de vida e pós-encontro dos recursos e consequências locais:** A) remover todos os componentes temporários ao terminar; B) preservar automaticamente tudo que foi materializado; **C, recomendada)** reconciliação por ownership e receipts, com persistência seletiva de consequências confirmadas e limpeza segura de recursos temporários, sem tocar assets nativos de outros mods e sem apagar evidências da campanha. DEC-072 define o que pode compor o encontro; DEC-073 definirá como encerrar e preservar seus efeitos corretamente.
