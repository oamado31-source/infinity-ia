# Documento 64 — Memória individual, aprendizado e revisão de crenças NPC

> **Status:** Discovery v6.0; DEC-064/C aprovada no ADR-0059. Esquemas, estados, fluxos e testes a seguir são **propostas técnicas**, não APIs implementadas. Preservar integralmente DEC-060/061/062/063, DEC-028/029 e autoridade do host.

## 1. Objetivo e separação de responsabilidades

A hipótese de que uma guilda é responsável por crimes pode existir como rumor propagado entre cidadãos de Athkatla sem ser verdade canônica ou fato confirmado. Um NPC que ouviu a acusação pode acreditar nela, ignorá-la, questioná-la ou reconsiderá-la depois de receber provas. A fonte corretiva pode chegar à curadoria antes de o NPC saber dela; atualização de base **não é comunicação diegética**.

| Camada | Fonte de autoridade | Persistência | Acesso do NPC |
|---|---|---|---|
| Cânone por ano DR | DEC-060/061/062 (fatos/alegações curados) | `knowledge/periods/<ano>-DR/...`, revisões anuais | Somente projeções por ano, vigência, ACL e conhecimento adquirido |
| Pack por campanha | DEC-063 | Manifesto imutável de **referências anuais** | Referência, não corpus de todo lore |
| Fatos confirmados da campanha | Host/gateway e evento narrativo validado | Log + snapshots de campanha/ramo | Apenas conforme testemunho, canal e autorização |
| Episódios de NPC | Observação, relato ou descoberta legitimamente recebida | Memória específica do NPC, campanha/ramo, com proveniência | Vínculo a evidência e permissões |
| Crença atual | Interpretação contextual de evidência legitimamente adquirida | Projeção versionada da história individual | Pode divergir do cânone e de outros NPCs |
| Reputação / alinhamento | Políticas narrativas e gates próprios | Projeções e eventos independentes | Nunca atualizados só por nova fonte editorial |

Os registros de memória privada **não** são armazenados como alegações canônicas nas pastas físicas anuais. O catálogo por ano continua separado. O sistema global de eventos estruturados da DEC-028 pode fornecer infraestrutura lógica, sem que isso signifique um repositório único de lore de todas as épocas.

## 2. Contratos candidatos (ainda não schemas estáveis)

```text
NpcExperienceEvent {
  event_id, idempotency_key, campaign_id, branch_id,
  npc_identity, world_time_DR, location_id,
  acquisition_mode: OBSERVED|TOLD|READ|INVESTIGATED|OTHER_VERIFIED,
  claim_ref, claim_version, originator_ref,
  transmission_ref?, observation_receipt?,
  disclosed_under_acl_revision, knowledge_pack_ref,
  confidence_of_source_evidence, access_scope,
  provenance_chain_ref, confirmed_or_provisional
}
NpcBeliefRevision {
  belief_id, revision_id, previous_revision_id?, npc_identity,
  campaign_id, branch_id, world_time_DR,
  claim_ref, stance: ACCEPTED|DOUBTFUL|REJECTED|SUSPENDED|INVESTIGATING,
  source_experience_ids[], competing_claim_refs[],
  assessment_basis_refs[], reason_codes[], policy_revision,
  authored_by: RULES_OR_APPROVED_ACTION,
  world_event_dep_refs[], visibility_scope, committed_at_checkpoint_ref?
}
NpcBeliefProjection {
  npc_identity, campaign_id, branch_id, clock_revision,
  active_knowledge_pack_ref, belief_revision_refs[],
  accessible_experiences[], permissions_epoch, projection_hash
}
BeliefAssessmentProposal {
  proposal_id, npc_identity, received_evidence_ids[],
  current_belief_rev, eligibility_result, source_provenance_result,
  temporal_check, acl_check, conflict_status,
  suggested_stance, uncertainty_flags[], downstream_candidate_events[]
}
```

IDs e valores de status são ilustrativos, não promessas de compatibilidade. Uma mesma informação pode ter testemunhos concorrentes e confiabilidade desigual; isso não implica atribuir probabilidades artificiais. Não registrar textos longos licenciados ou segredos em logs de depuração.

## 3. Fluxo de aprendizagem e correção

```text
FONTE DO MUNDO (canon anual curado ou evento host-confirmado)
             |
             v
ACONTECIMENTO SOCIAL LEGÍTIMO (observação, documento, rumor, investigação)
             |
             v
VERIFICAÇÃO: ANO DR + CAMPANHA/RAMO + CANAL + PROVENIÊNCIA + ACL
             |
      [falha / falta de prova] ------------------> DEFER/REJECT
             |
             v
REGISTRAR EXPERIÊNCIA DO NPC UMA VEZ (idempotente, versionada)
             |
             v
AVALIAR EVIDÊNCIA DISPONÍVEL, CONFLITOS E CRENÇAS ANTERIORES
             |
         +---+-----------+------------------------+
         |               |                        |
     MANTER/DUVIDAR   INVESTIGAR             ACEITAR/REJEITAR
         |               |                        |
         +---------------+------------------------+
             |
             v
APPEND DE REVISÃO DE CRENÇA (sem apagar episódio nem diálogo passado)
             |
             v
PROPOSTA DE DIÁLOGO/REAÇÃO -> DEC-060 valida output
             |
             v
POSSÍVEL CONSEQUÊNCIA POR RISCO -> DEC-012, host ou gate narrativo
```

A cadeia de difusão DEC-029 não impõe crença à chegada da notícia: **receber** e **acreditar** são atos separados. Um NPC pode manter duas fontes inconciliáveis na memória como `SUSPENDED` e buscar evidências sem inventar síntese.

## 4. Avaliação contextual por regras e IA limitada

- **Evidência direta:** observação plausível do NPC em local/instante confirmado, sujeita a limitações de percepção e validação.
- **Relatos:** proveniência de fonte e transmissões, incentivos, reputação contextual e cadeia de confiança, sem certeza artificial.
- **Documentos:** acesso legítimo ao documento, data e autenticidade possível; notícia recém-publicada no catálogo não implica leitura pelo NPC.
- **Viés/persona:** personalidade, crença prévia, lealdade e experiência podem modular a reação, mas jamais contornar ACL/cânone ou alterar evento confirmado.
- **Conflito canônico:** `UNRESOLVED` na DEC-061 jamais vira fato em razão de persuasão; NPC pode escolher uma interpretação pessoal rotulada como crença subjetiva.
- **LLM:** permitido para formulação verbal ou **proposta** de motivação/diálogo, com contexto mínimo aprovado e outputs sob DEC-059/060. Não escreve `NpcExperienceEvent` nem `NpcBeliefRevision` diretamente e não cria observações falsas como evidência.
- **Consequências:** um pedido de desculpas ou hostilidade é candidato narrativo; quando altera quests, relação mecânica, reputação, alinhamento, combate, mortes, itens ou flags, as políticas e gates respectivos permanecem obrigatórios.

## 5. Temporalidade, diretórios físicos anuais e overlay de campanha

```text
Campanha A, ramo R, relógio confirmado = 1369 DR
  -> binding Pack A1 [referencia revisão física knowledge/periods/1369-DR]
  -> query primária no diretório físico 1369-DR (DEC-060)
  -> antecedentes em outros diretórios só se vigência/ACL permitirem
  -> overlays confirmados da campanha/ramo (não alteram cânone)
  -> [episódios NPC em sua memória, filtrados pela identidade + ACL]
  -> [projeção de crenças NPC na revisão permitida]
  -> saída de diálogo com validação DEC-060
```

- Se um novo pack 1.1 corrige alegação sobre uma guilda, a campanha A continua com A1 até migração DEC-063 aprovada. Mesmo depois, NPC só aprende a correção mediante episódio legítimo de aquisição.
- Se o NPC ouviu um boato em 1369, a memória do episódio permanece como registro histórico de ter ouvido, mesmo após rejeitar o conteúdo da crença.
- Se a campanha avançou para 1370, o estado mental pode persistir enquanto o fato continuar lembrado/pertinente; isso **não** autoriza acessar clandestinamente a base canônica de 1370 quando o relógio ainda era 1369, nem torna futuro conhecido.
- Dois ramos da mesma campanha podem conservar memórias e crenças diferentes. Restaurar um checkpoint exige recuperar também versões de memória/revisões epistêmicas compatíveis.
- Segredos de jogador são segregados por ACL; o fato de alguém saber fora da ficção não autoriza a aquisição diegética.

## 6. Segurança, idempotência, prioridades e comportamento em falhas

| Falha/condição | Resposta segura |
|---|---|
| Revisão de pack ou ACL alterada durante geração | Invalidar contexto/resultado anterior; refazer somente se autorizado. |
| Evidência sem evento/canal comprovável | Não registrar observação; manter dúvida ou adiar. |
| Rumor duplicado pelo mesmo caminho | Não adicionar episódio novo artificial nem ampliar convicção por duplicação técnica. |
| Duas versões da mesma fonte conflitantes | Preservar ambas com origem e diferenciar confiança sem declarar verdade. |
| `UNCERTAIN` de ação ou evento mecânico | Impedir memória factual confirmada até reconciliar receipt com host. |
| Ausência de diretório anual/revisão curada | Sem fallback a índice global de lore; reportar cobertura insuficiente. |
| Revogação de nó LAN enquanto executa job | Rejeitar output; revogação não desfaz conteúdo já recebido, portanto minimizar antes de despachar. |
| LLM lento em combate/multiplayer | Deferir interpretação não essencial, usar resposta segura aprovada ou aguardar; não bloquear o loop do jogo. |
| Recuperação de checkpoint anterior | Restaurar projeções e eventos NPC da linha causal, sem reproduzir correção posterior. |
| Crença aceita que leva a ação de alto risco | Avaliar ação separadamente no gateway/host; crença não é autorização. |

Relógio FROZEN/PARTIAL/REALTIME (DEC-022) e regimes ACTIVE/NEAR/DISTANT/DORMANT (DEC-021) limitam tanto a difusão quanto a reavaliação contextual. Nenhum tick offscreen gera LLM por NPC. Caches e resultados são segmentados por campanha/ramo/ano/pack/epoch/permissões. Backups/restauração DEC-053/054 abrangem vínculo causal da memória, sob POCs ainda pendentes. DEC-055 monitora sem revelar segredos.

## 7. Cenário narrativo concreto — rumor de culpa da guilda (hipotético)

1. Em 1369 DR, uma testemunha T relata a NPC-A que a guilda G cometeu assassinatos. O sistema registra a **recepção** do relato com referência à transmissão e não o transforma em fato canônico.
2. NPC-A, com confiança em T, registra uma crença `ACCEPTED`. NPC-B, que não ouviu T, permanece desconhecedor; NPC-C ouve outro relato e registra `DOUBTFUL`.
3. Curador publica nova fonte contraditória em revisão anual 1369-DR; o pack da campanha **não muda** automaticamente. Quando a campanha adota nova revisão, nenhum NPC recebe crença corrigida por telepatia.
4. Mais tarde, o jogador mostra a NPC-A documento autorizado e verificável. O NPC pode revisar a crença para `DOUBTFUL`/`REJECTED`, mantendo a lembrança de que acreditou no boato no passado.
5. NPC-A pode desejar pedir desculpas, reparar reputação ou investigar a origem da mentira. Cada consequência é examinada conforme risco, autoridade e estado histórico; não gera alteração mecânica espontânea.

O cenário usa entidades fictícias genéricas, não afirma eventos históricos de Forgotten Realms nem presença de personagens/mods específicos no BG2:EE.

## 8. Testes candidatos — T064 (nenhum executado)
1. **T064-01:** Conversa NPC-A/NPC-B: só A recebe notícia; B não aprende por atualização global.
2. **T064-02:** Atualização de knowledge pack 1.0→1.1 não cria memórias ou novas crenças em NPCs.
3. **T064-03:** NPC recebe fonte por canal plausível e registra aquisição idempotente com data DR.
4. **T064-04:** Conteúdo privado de PC não é enviado ao NPC sem ACL/permissão e revelação legítima.
5. **T064-05:** Rumor falso é representado como crença/relato, nunca como CANON_CLAIM confirmado.
6. **T064-06:** Evidência direta válida modifica crença mas preserva episódio e revisão anteriores.
7. **T064-07:** Informação trazida por fonte pouco confiável pode levar a DOUBTFUL sem imposição numérica.
8. **T064-08:** Duas alegações contraditórias permanecem referenciadas sem consenso sintético do LLM.
9. **T064-09:** Novo livro inserido em staging DEC-062 não é tratado como saber adquirido pelo NPC.
10. **T064-10:** Revisão de 1369 DR não consulta fatos de 1370 DR como consumados.
11. **T064-11:** Consulta anterior a 1369 ocorre somente por validade temporal, proveniência e ACL.
12. **T064-12:** Recuperação de conhecimento respeita partições físicas anuais, sem índice global cruzado.
13. **T064-13:** Alteração causal de facção em ramo A não altera memória de NPC no ramo B.
14. **T064-14:** Após restaurar checkpoint, a crença posterior não aparece antes de seu evento causal.
15. **T064-15:** Boato retransmitido duas vezes tecnicamente não gera aprendizado duplicado.
16. **T064-16:** Rumor legítimo difundido em DISTANT segue limites de clock/catch-up sem LLM por NPC/tick.
17. **T064-17:** NPC em DORMANT não aprende instantaneamente notícia sem reidratação e canal plausível.
18. **T064-18:** Nó LAN autorizado recebe apenas contexto mínimo de crença, nunca história completa privada.
19. **T064-19:** Revogação de nó e job LLM tardio impedem commit de crença ou divulgação futura.
20. **T064-20:** Mudança de permissões invalida cache e prompt de revisão anterior.
21. **T064-21:** Resposta LLM que sugere memória falsa não gera evento de aquisição.
22. **T064-22:** Operação mecânica UNCERTAIN não é registrada como observação confirmada.
23. **T064-23:** Alteração de crença não muda automaticamente alinhamento nem reputação mecânica.
24. **T064-24:** Pedido de desculpas pode ser proposto narrativamente sem editar quest/script confirmado.
25. **T064-25:** Um NPC pode manter crença falsa mesmo após correção editorial no cânone.
26. **T064-26:** NPC pode revisar voluntariamente interpretação com nova prova e preservar fala histórica.
27. **T064-27:** Backups restauram branch, pack, memória e revisão de crença coerentes com checkpoint.
28. **T064-28:** Ausência de revisão anual necessária resulta em DEFER, não fallback global.
29. **T064-29:** Observabilidade/telemetria redige conteúdo protegido e nomes/segredos privados.
30. **T064-30:** Suíte de testes reporta POC e benchmarks BG2:EE/EEex como NÃO EXECUTADOS até evidência.

## 9. Fora do escopo e próxima decisão

**DEC-065:** como **reter, consolidar, resumir e eventualmente esquecer** memórias individuais ao longo de décadas de campanha, equilibrando desempenho e fidelidade. Esta DEC-064 fixa apenas a trilha de aquisição e a revisão contextual, sem limites quantitativos de armazenamento, política de retenção ou formato definitivo. Modelos/runtime DEC-006, métricas DEC-015, logs/backup DEC-018 e infraestrutura BG2:EE/EEex carecem de validação.


## 10. Complemento aprovado DEC-065/C — memórias hierárquicas (Discovery v6.1)

A decisão posterior aprova camadas `WORKING`, `EPISODIC`, `CONSOLIDATED` e `PROTECTED`; sínteses devem citar episódios e permissões e não alteram a crença DEC-064 por atalho. Proteção crítica impede exclusão automática por otimização, não autoriza divulgação nem exige retenção ilegal. A busca seletiva considera NPC/branch/época/ACL/revisão sem sempre recuperar tudo e não impõe TTL arbitrário. Ver ADR-0060 e `65-memoria-hierarquica-consolidacao-retencao-e-recuperacao-contextual-npc.md`. **DEC-060–063 seguem preservadas**, incluindo cânone fisicamente organizado por ano e memória NPC externa a essas pastas. O parágrafo anterior que menciona DEC-065 como futura é histórico.

### Integração DEC-066/C — vinculação confiável de episódios e crenças (v6.2)

A identidade lógica persistente atribui episódios/crenças a um indivíduo por campanha/branch; cada nova observação do jogo deve ser reconciliada antes de recuperar ou atualizar sua memória. Nome, forma ou ID do motor não bastam. Se ambígua, negar leitura privada e adiar gravação de nova experiência personalizada. Não alterar regras de aquisição legítima, revisão de crenças ou separação canônica anual DEC-060.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Ao promover NPC DEC-067, criar memória somente de experiências legitimamente adquiridas; nenhuma biografia retroativa, rumor como fato ou onisciência derivada do catálogo.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Durante dormência DEC-068, crenças não são automaticamente corrigidas pela verdade do Knowledge Pack. Aprendizagem requer aquisição plausível por evento/canal e horário; não criar diálogos retroativos para justificar mudança epistêmica.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: NPC pode acreditar num roteiro ou ouvir notícia de chegada sem que isso confirme sua localização; memórias de viagem só entram como eventos legítimos.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: episódio de viagem confirmado LOW pode alimentar memória epistêmica; rumor não concede testemunho e relato de ataque não cria ferimento mecânico. NPC só aprende por canal legítimo.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

NPC só adquire memória DEC-071 depois de observação/narrativa autorizada ou receipt mecânico apropriado; encontro apenas proposto não é vivência. Identidade e ACL DEC-066/028 continuam determinantes.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Diálogo produzido por template DEC-072 só se torna episódio de memória NPC após interação e evidência autorizada; composição textual não cria testemunha ou aprendizagem retrospectiva.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Memórias e crenças NPC não são eliminadas pelo cleanup de instância; só episódios/observações realmente confirmados alimentam história pessoal.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

DEC-074 registra recebimento legítimo, evidência de fonte e mudança de crença DEC-064; não apaga memória de rumor falso quando a verdade aparece. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

NPC pode atribuir mérito erroneamente e rever crença após evidência legítima, preservando episódio original e sem reescrever ator verdadeiro no ledger.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Memória de NPC registra quem ele acredita que uma persona é e fonte da crença. Reconhecimento real exige provas distintas; correção posterior preserva a antiga suspeita.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Guarda NPC DEC-078 pode acreditar na acusação, ser enganado ou revisar sua crença; veredito ficcional não é memória factual universal.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

NPC guarda pode acreditar em boato de mandado DEC-079 sem ter prova ou autoridade para agir. Crenças só se atualizam por canais e evidências; fato de ledger não é onisciência.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Destinatário DEC-080 pode acreditar em versão antiga até receber notícia válida, e sua memória se corrige progressivamente, com proveniência, sem contato telepático com o safety gate.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

A autoridade/mercador pode lembrar acusação falsa e depois receber retificação; DEC-081 corrige crenças via comunicação sem apagar o episódio vivido.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

NPC distingue crença em denúncia de responsabilidade comprovada; nova prova corrige crença preservando relato histórico.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

NPC memoriza somente relato recebido; conhecimento de identidade da fonte tem ACL individual e proveniência, não onisciência por audit ledger.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Ameaças testemunhadas e pedidos de ajuda geram memórias com fonte e certeza; NPC não passa a conhecer localização do abrigo sem canal legítimo.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

NPC mantém pistas e crenças de abrigo com grau de certeza e origem; conhecer local antigo não significa conhecer novo trajeto.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

NPC pode recordar que acreditou numa isca falsa e posteriormente corrigir sua crença; não apagar percepções originais nem alterar fatos confirmados.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

NPC pode acreditar erroneamente que colega traiu a guilda; memória mantém fonte e contradições separadas da lealdade privada verdadeira.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Memória NPC distingue contato, proposta, acordo e entrega. Uma fonte pode acreditar em informação incorreta; confiança não prova veracidade.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

NPC armazena crença e origem do rumor, não verdade privada do host. Novas provas podem corrigir crença sem apagar memória histórica de ter acreditado antes.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

NPC pode acreditar em resumo recebido e desconhecer anexos ou fontes; recebimento não é crença e correção posterior não apaga memória histórica, exige atualização causal.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

NPC só pode escolher ações com base em suas crenças/contexto conhecidos; planner não entrega verdade host-only a ele.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Crenças do NPC sobre mudança de plano dependem de relato que ele pode ter recebido; conhecimento host-only não entra em memória narrativa.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Um NPC só pode explicar conflito de agenda ou descobrir missão rival quando dispõe de percepção/canal de informação legítimos; registro do scheduler não equivale a memória social.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

NPC não adquire conhecimento de conflitos secretos por existir aresta no scheduler; memória reflete somente eventos observados causalmente.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

CanonEvent elegível DEC-096 não vira memória de NPC; exige KnowledgeAcquisition de canal plausível DEC-064/029.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Memória NPC DEC-064 só incorpora repercussão DEC-096/C após aquisição causal por canal e ACL; não ler arquivo global da cronologia como lembrança pessoal.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Decaimento de preço DEC-097/C não apaga memória do NPC; percepção depende de conhecimento observável legitimado.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Memória NPC é estado narrativo individual, não cache de engine instance; unload/despawn visual não remove fatos e crenças confirmados.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Memória de NPC pode errar sobre origem e identidade; não prova ownership ou presença mecânica.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Memória falível de NPC não ganha acesso automático à engine; só atualiza por evento de conhecimento legítimo.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Uma correção técnica DEC-102 não apaga lembranças ou transmite conhecimento a NPCs. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **memória e crença**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para crenças falíveis, estados contraditórios e reavaliação contextual, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para crença falível não é restaurada por ordem, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Memória de NPC não é apagada por renegociação. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Memórias e crenças de NPCs não são reescritas por emendas. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
