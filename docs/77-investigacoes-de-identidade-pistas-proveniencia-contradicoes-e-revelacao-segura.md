# DEC-077 — Investigações de identidade por pistas, proveniência, contradições e divulgação segura

**Discovery v7.3 · ADR-0072 · Opção C aprovada · APENAS ARQUITETURA / NÃO IMPLEMENTADA**  
**Escopo:** investigação de identidades secretas, pseudônimos e atribuição de autoria, sem pressupor mecânica de detecção disponível no BG2:EE.  
**Evidência:** decisão do usuário; **58 testes candidatos T077-01..58, todos NÃO EXECUTADOS**.

## 1. Escopo, objetivos e não objetivos

### Objetivos

- Permitir investigações progressivas de identidades e pseudônimos sem revelação instantânea.
- Preservar evidências independentes, contraditórias e contestáveis, com proveniência auditável.
- Distinguir o fato privado, a suspeita do investigador, a crença de cada observador e o evento de divulgação.
- Manter segredos de PCs/NPCs sob ACL, consentimento, escopo de audiência e limites causais.
- Propor conclusões revisáveis sem dar à LLM autoridade para validar identidades ou punir personagens.

### Não objetivos

- Não implementar polícia, tribunais, condenação, punições, caça, furtividade ou disfarces mecânicos.
- Não garantir hooks de interceptação de diálogos, inventários, perícias, detecção ou rename no BG2:EE/EEex.
- Não importar automaticamente material protegido de Forgotten Realms ou registrar conclusões ficcionais no cânone.
- Não determinar percentuais de certeza, thresholds, UX final ou modelos de LLM nesta fase de Discovery.

## 2. Fronteiras de confiança e partição temporal

```text
knowledge/periods/<ANO>-DR/                # lore canônico por ano, fonte curada; DEC-060–063
  chronology/, events/, characters/, guilds/, organizations/...

campaign-overlays/<campaign>/<branch>/       # DOMÍNIO LÓGICO CANDIDATO, ainda não implementado
  actor-identity/                           # identidade privada comprovada DEC-066
  personas/                                  # pseudônimos DEC-076
  investigations/<investigation_id>/
    leads/                                  # propostas de pistas, ainda não provadas
    evidence/                               # evidências com provenance e ACL
    evidence-source-graph/                  # independência/circularidade
    hypotheses/                             # vínculos suspeitos e alternativas
    assessments/                            # decisões revisáveis e contestadas
    observer-beliefs/                       # visões de indivíduos e facções
    disclosures/                            # quem recebeu o quê, com autorização
    revision-log/                            # eventos append-only, sem retcon
```

O caminho de overlays é **ilustrativo**: o modelo físico final depende de SPECS e testes. **Não fundir os diretórios anuais do cânone com os dados da campanha**, nem replicar lore de todas as épocas em um único banco. O ledger de evidências privado pode referenciar fontes canônicas anuais sem publicar segredos nelas.

## 3. Entidades e contratos candidatos

```text
InvestigationCase {
  campaign_id, branch_id, investigation_id, lead_reason,
  investigator_scope, subject_persona_ids[], candidate_actor_ids[],
  current_state, risk_class, acl, knowledge_pack_revision,
  checkpoint_ref, resolution_epoch, case_revision, created_at_dr
}
InvestigationLead {
  lead_id, investigation_id, discovered_by, discovered_at_dr,
  proposed_question, clue_refs[], unresolved_source_refs[], status,
  audience_acl, revision
}
EvidenceRecord {
  evidence_id, investigation_id, evidence_kind,
  claim_text_or_structured_assertion, origin_actor_ref?, provenance_ref,
  source_chain_id, root_source_ids[], custody_events[], event_ref?,
  observation_time_dr, obtained_time_dr, region_ref?, integrity_state,
  access_acl, supports_hypothesis_ids[], challenges_hypothesis_ids[],
  validity_state: UNVALIDATED|VALID|DISPUTED|INVALIDATED|STALE,
  evidence_revision
}
InvestigationHypothesis {
  hypothesis_id, case_id, persona_id, possible_actor_id?,
  supporting_evidence_ids[], contradicting_evidence_ids[],
  alternatives[], corroboration_state, rationale_redacted,
  state: OPEN|SUSPECTED|CORROBORATING|DISPUTED|INCONCLUSIVE|PRIVATELY_VERIFIED|REJECTED,
  revision
}
InvestigationAssessment {
  decision_id, case_id, case_revision, hypothesis_id,
  outcome, supporting_refs[], contrary_refs[],
  independent_source_roots[], reviewer_or_rule_revision,
  capability_proof_refs[], risk_class, audience_scope,
  authorized_by?, checkpoint_ref, resolution_epoch
}
InvestigationDisclosure {
  disclosure_id, case_id, decision_ref, recipient_acl,
  minimal_claim_payload_ref, source_channel_ref,
  consent_or_permission_ref, risk_gate_ref, time_dr,
  delivery_state: PROPOSED|AUTHORIZED|CONFIRMED|REJECTED|UNCERTAIN,
  deduplication_key
}
```

Campos e enums são **contratos candidatos**, não esquema persistente implementado. `actor_id` não equivale automaticamente a nome, retrato ou objeto observado; relaciona-se por DEC-066. A estimativa de qualidade será justificativa revisável, não score mágico. Uma prova pode corroborar um aspecto e contradizer outro; duplicações por origem não se tornam evidência independente.

## 4. Pipeline investigativo proposto

1. **Abrir caso:** o evento causador e a audiência autorizada definem motivo e contexto; segredos privados não são anexados automaticamente.
2. **Coletar pistas:** fontes legítimas oferecem observações, documentos, testemunhos ou rumores, com tempo, lugar, proveniência e visibilidade.
3. **Verificar integridade:** recuperar fontes com ACL, avaliar se estão disponíveis na época certa e preservar origem/cadeia de obtenção; marcar faltas.
4. **Resolver ancestralidade:** diferenciar duas testemunhas independentes de duas pessoas repetindo a mesma notícia; impedir double counting e ciclos de boato.
5. **Analisar hipóteses:** gerar explicações alternativas, buscar evidências favoráveis/contrárias e identificar lacunas; LLM pode propor perguntas, nunca validar a verdade sozinha.
6. **Revisar estado:** classificar suspeita/contradição/insuficiência; uma suspeita pode continuar por tempo indefinido sem obrigar resolução narrativa.
7. **Verificar ligação restrita:** quando houver provas adequadas, gate de risco e identidade DEC-066, produzir `PRIVATELY_VERIFIED` apenas em domínio autorizado; não divulgar.
8. **Avaliar divulgação separada:** exigir motivo, consentimento, audiência, canal, versão/tempo, escopo e aprovação adicional quando sensível; `UNCERTAIN` fail-closed.
9. **Propagar conhecimento situado:** destinatário informado pode adquirir crença, não necessariamente verdade; rumores e repercussões seguem DEC-029/064/074/075.
10. **Auditar e reabrir:** nova contraprova ou restauração cria revisão; rejeitar mensagens de worker ou checkpoint obsoleto.

## 5. Transições exemplificativas

```text
OPEN -> COLLECTING -> SUSPECTED -> CORROBORATING
                                |            |
                                v            v
                            CONTRADICTED -> DISPUTED
                                |            |
                                v            v
                           INCONCLUSIVE  INCONCLUSIVE
                                             |
                (somente prova + gate) -------+--> PRIVATELY_VERIFIED
                                                      |
                                            (gate específico de divulgação)
                                                      v
                                               DISCLOSED_TO_SCOPE
```

É apenas desenho conceitual. `DISCLOSED_TO_SCOPE` é um evento de conhecimento por destinatário, não transforma todos os observadores em conhecedores. Avaliações antigas continuam no ledger ao serem contestadas. Não permitir transição de rumor → verdade/fato ou `SUSPECTED` → `DISCLOSED` por impulso narrativo.

## 6. Independência, falsificações e cadeia de origem

- Evidência `E1` contém o rumor de um viajante; `E2` é a transcrição de E1 por uma taverna. E1 e E2 têm a **mesma fonte raiz**, não reforço independente.
- Um documento de procedência legítima pode conter mentira; autenticidade do meio e verdade do conteúdo são avaliações distintas.
- Um álibi pode ser falso, verdadeiro ou não comprovado; a IA não preenche automaticamente os horários desconhecidos.
- Contradições geram `DISPUTED`/`INCONCLUSIVE`; falsos testemunhos podem existir ficcionalmente, mas não alterar o fato real privado sem prova.
- Qualquer revisão deve mostrar, a usuários autorizados, evidências favoráveis e contrárias sem vazar segredos a públicos não autorizados.
- A ausência de prova não significa prova de ausência. Nem suspeita significa condenação.

## 7. Política de consentimento, privacidade e divulgação

- Antes de retrieval, prompt, cache, embedding, UI e LAN: aplicar ACL por campanha, branch, ator, propósito e público. Um investigador não recebe o gabarito factual privado apenas por abrir caso.
- Titularidade de PC e controlador temporário DEC-045/046 são distintos; estar no grupo não concede leitura de segredos individuais DEC-019/041.
- Revelação restrita à testemunha A, comunicação à guilda B e publicação geral são **operações diferentes** que exigem gates próprios.
- Segredo sensível/alto impacto requer autorização específica; `UNCERTAIN` ou audience ausente mantém a revelação bloqueada.
- Telemetria, logs e logs explicativos não devem expor material secreto; diagnósticos usam identificadores/redações seguras.
- Uma prova privada pode ajudar a prevenir falsa atribuição internamente, mas não autoriza o NPC a conhecer o resultado.

## 8. Autoridade mecânica, riscos e consequências

- DEC-011/012: host e Action Gateway controlam efeitos mecânicos; a IA produz apenas texto/propostas.
- DEC-027/034: classificação LOW/MEDIUM/HIGH por consequência e risco agregado; consequências irreversíveis default deny e autorizações especiais.
- DEC-075: autoria factual não é percepção social; NPC que acusa pode estar errado mesmo que tenha convicção subjetiva.
- Nenhum NPC é preso, morto, punido, privado de itens, condenado ou obrigado a revelar identidade por mera inferência LLM.
- Qualquer detecção ou interrogação apoiada em mecânica nativa exige capability testada, prova de interação e receipt do host; nenhuma hoje demonstrada.
- Direito local e justiça variam por região, data e facção; **DEC-078 permanece proposta aberta**, não há política de sanções aprovada nesta decisão.

## 9. Temporização, filas e idempotência

- `campaign_id`, `branch_id`, `checkpoint_ref`, `knowledge_pack_revision`, `resolution_epoch`, `investigation_id`, `evidence_id`, `case_revision` e `audience_scope` cercam a operação.
- Restore invalida casos/eventos do futuro do ramo restaurado. Mensagens `STALE`, `UNCERTAIN` ou de nó LAN revogado são rejeitadas/retidas para auditoria restrita.
- Deduplicar pistas por `evidence_id` e ancestralidade real; deduplicar divulgação por `decision_id`/audiência/época. O mesmo boato não acumula provas nem reputação duas vezes.
- Não processar LLM por NPC/tick: priorizar diálogo imediato e investigações ativas; tarefas longas por lote/filas duráveis e canceláveis, DEC-056.

## 10. Plano de POC e gates de aceite

1. **Fixtures offline** de três identidades homônimas, documento forjado, testemunhos independentes e rumor circular, álibi legítimo/falso e segredo de PC.
2. **Validação de dados** e replay determinístico com evidências antigas/novas, correções e alegações refutadas.
3. **Teste ACL e consentimento** por jogador, NPC, guilda, host e worker LAN; tentar extração por prompt/erro/UI/índice.
4. **Teste de persistência** com save/load, restauração de branch anterior, dedup e tratamento de `UNCERTAIN`.
5. **Benchmarks de carga** para grafo de evidências com filas sem competir com gameplay/multiplayer.
6. **POC bridge read-only** de capacidades observáveis: disponibilidade real de falas, percepções, diálogos, objetos e NPCs em BG2:EE clean e EEex.
7. **POCs host+dois clientes**, por build e mods, antes de habilitar qualquer interação mecânica. Sem sucesso comprovado, manter apenas investigação narrativa permitida.
8. Elaborar SPECS após gates, mantendo DEC-006/007/013/015/017/018 abertas e sem prometer suporte do motor.

## 11. Matriz de 58 testes candidatos — NÃO EXECUTADOS

| ID | Cenário / critério esperado | Estado |
|---|---|---|
| T077-01 | Uma pista isolada não revela nem verifica automaticamente uma identidade. | NÃO EXECUTADO |
| T077-02 | Duas pistas derivadas do mesmo boato não contam como corroboração independente. | NÃO EXECUTADO |
| T077-03 | Uma pista corroborada por origem realmente independente pode elevar suspeita sem divulgação. | NÃO EXECUTADO |
| T077-04 | Testemunho falso permanece alegação, nunca fato confirmado apenas por fluência da IA. | NÃO EXECUTADO |
| T077-05 | Carta autêntica com assinatura falsificada não prova autor material. | NÃO EXECUTADO |
| T077-06 | Carta com proveniência desconhecida entra em quarentena até validação. | NÃO EXECUTADO |
| T077-07 | Álibi com horário conflitante mantém caso DISPUTED. | NÃO EXECUTADO |
| T077-08 | Álibi legítimo pode reduzir ou retirar suspeita, preservando histórico. | NÃO EXECUTADO |
| T077-09 | Contraevidência apresentada após resolução reabre revisão, sem apagar decisão anterior. | NÃO EXECUTADO |
| T077-10 | Nenhum score numérico arbitrário de certeza substitui evidências. | NÃO EXECUTADO |
| T077-11 | Pistas de ano DR futuro não aparecem em investigação do passado. | NÃO EXECUTADO |
| T077-12 | Descoberta de outro branch não aparece após restaurar checkpoint antigo. | NÃO EXECUTADO |
| T077-13 | Identidade de homônimo não é fundida por mesmo alias. | NÃO EXECUTADO |
| T077-14 | Sem prova DEC-066, instância de NPC não recebe evidência de pessoa distinta. | NÃO EXECUTADO |
| T077-15 | Investigador não acessa prova que só outro grupo encontrou. | NÃO EXECUTADO |
| T077-16 | NPC não sabe de carta localizada no ledger privado sem canal de descoberta. | NÃO EXECUTADO |
| T077-17 | Membro de party não vê automaticamente segredo de outro PC. | NÃO EXECUTADO |
| T077-18 | PC ausente mantém política de consentimento e backstory. | NÃO EXECUTADO |
| T077-19 | Jogador que controla PC delegado não vira titular da identidade. | NÃO EXECUTADO |
| T077-20 | Vínculo VERIFIED_PRIVATE [modelo conceitual] não divulga segredo a testemunha. | NÃO EXECUTADO |
| T077-21 | Disclosure a uma guilda não publica a identidade para cidade inteira. | NÃO EXECUTADO |
| T077-22 | Vazamento indireto por mensagem de erro é barrado por ACL. | NÃO EXECUTADO |
| T077-23 | Busca/índice e embeddings respeitam filtro de segredo antes do retrieval. | NÃO EXECUTADO |
| T077-24 | Prompt de LLM para NPC contém somente pistas que o NPC pode conhecer. | NÃO EXECUTADO |
| T077-25 | Retorno de LLM inventando testemunha é rejeitado. | NÃO EXECUTADO |
| T077-26 | LLM sugerindo culpado não altera avaliação factual. | NÃO EXECUTADO |
| T077-27 | Pistas duplicadas por retry são deduplicadas por evidence_id e fonte. | NÃO EXECUTADO |
| T077-28 | Dois investigadores em concorrência não produzem decisões contraditórias confirmadas. | NÃO EXECUTADO |
| T077-29 | Fila stale de worker LAN não altera investigação após restore. | NÃO EXECUTADO |
| T077-30 | Worker não autorizado não acessa testemunho privado. | NÃO EXECUTADO |
| T077-31 | Revogação de nó LAN bloqueia novas pesquisas e divulgações. | NÃO EXECUTADO |
| T077-32 | Incidente UNCERTAIN impede anúncio/retry cego. | NÃO EXECUTADO |
| T077-33 | Documento manipulado mantém versões e autoria declarada com provenance. | NÃO EXECUTADO |
| T077-34 | Cadeia de custódia interrompida reduz status de prova, não é preenchida por IA. | NÃO EXECUTADO |
| T077-35 | Fonte contraditória é preservada, não sobrescrita. | NÃO EXECUTADO |
| T077-36 | Falsas acusações podem existir como crença social, nunca como condenação factual. | NÃO EXECUTADO |
| T077-37 | Reputação associada à persona não é fundida globalmente por suspeita. | NÃO EXECUTADO |
| T077-38 | Nenhuma prisão ou punição mecânica ocorre por mera investigação. | NÃO EXECUTADO |
| T077-39 | Nenhum XP/quest flag/inventário muda por conclusão narrativa sem receipt host. | NÃO EXECUTADO |
| T077-40 | Gate HIGH exige autorização especial antes de divulgação sensível. | NÃO EXECUTADO |
| T077-41 | Efeitos LOW sucessivos não contornam gate HIGH por composição. | NÃO EXECUTADO |
| T077-42 | Audiência mal especificada provoca fail-closed. | NÃO EXECUTADO |
| T077-43 | Reconhecimentos de disfarce dependem de POC da engine antes de anúncio de suporte. | NÃO EXECUTADO |
| T077-44 | UI nativa visível no cliente não equivale a conhecimento diegético do NPC. | NÃO EXECUTADO |
| T077-45 | Percepção do NPC pode permanecer equivocada mesmo com verdade restrita conhecida. | NÃO EXECUTADO |
| T077-46 | Correção de crença gera novo episódio sem editar lembrança antiga. | NÃO EXECUTADO |
| T077-47 | Relato de investigação atravessa rotas com atraso e origem preservados. | NÃO EXECUTADO |
| T077-48 | Boato repetido não gera novas provas independentes. | NÃO EXECUTADO |
| T077-49 | Decisão de investigação registra evidências favoráveis e contrárias. | NÃO EXECUTADO |
| T077-50 | Uma investigação INCONCLUSIVE não é completada automaticamente para satisfazer quest. | NÃO EXECUTADO |
| T077-51 | Caso CLOSED_NO_LINK mantém histórico auditável e não obriga inocência universal. | NÃO EXECUTADO |
| T077-52 | Uma investigação contestada suspende divulgação adicional não autorizada. | NÃO EXECUTADO |
| T077-53 | Reabertura de caso respeita revisão de Knowledge Pack por campanha. | NÃO EXECUTADO |
| T077-54 | Diretório anual canônico não recebe pistas privadas de PC. | NÃO EXECUTADO |
| T077-55 | Prova do ano 1369 DR é pesquisada na partição apropriada, com checagem de continuidade. | NÃO EXECUTADO |
| T077-56 | Modelo menor insuficiente não faz fallback a worker sem permissão de dados. | NÃO EXECUTADO |
| T077-57 | Processamento em lote não bloqueia host/gameplay e respeita limite de backlog. | NÃO EXECUTADO |
| T077-58 | POC host+dois clientes e matriz por build são exigidos antes de prometer gameplay de investigação. | NÃO EXECUTADO |

## 12. Relações e próxima decisão

- **DEC-060:** conhecimento canônico em diretórios físicos por ano DR, separado de casos privados.
- **DEC-061–063:** proveniência, curadoria e Knowledge Pack versionado; consulta a fatos anteriores só com validade temporal.
- **DEC-064–068:** crenças e memórias falíveis, identidades NPC verificadas, hibernação e persistência.
- **DEC-069–075:** viagens, encontros e atribuição de mérito com fatos confirmados separados de relatos.
- **DEC-076:** identidades factuais privadas, personas públicas e estado de divulgação por audiência.
- **DEC-019/028/041/045/046:** segredo, consentimento e multiplayer.
- **DEC-006/007/013/015/017/018:** ainda abertas, sem escolhas de runtime, UI e gates técnicos confirmados.
- **Próxima DEC-078 (EM ABERTO):** como tratar acusações e decisões de autoridades/guildas após uma investigação: A) sanções automáticas por suspeita; B) efeitos apenas narrativos sem estrutura; **C) procedimentos contextuais por jurisdição com evidências, contraditório, risco e confirmação/autorizações específicas**.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

DEC-078 recebe evidências e hipóteses DEC-077, nunca transforma INCONCLUSIVE em crime confirmado por veredito. Competência regional/faccional, contraditório contextual e consequências exigem gates independentes.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Pistas e álibis no caso DEC-079 mantêm cadeia de proveniência e contradições, sem converter pedidos em culpa; testemunho ao destinatário é informação filtrada.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Contraprova investigativa DEC-077 pode fundamentar correção/revogação DEC-080, mas suspeita isolada não altera status autoritativo sem competência/revisão.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Pistas DEC-077 podem revisar acusação e gerar proposta de reparação DEC-081, mas investigação inconclusa não prova dano, crime ou direito à compensação.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Mesmos controles de independência/provenance e hipóteses contestáveis se aplicam a casos de corrupção; LLM não declara veredito.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Investigação DEC-077 pode utilizar depoimento protegido com origem e independência; contraditório pode consultar extratos sem direito de descobrir o nome.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Provas de ameaça ou descoberta de abrigo precisam de procedência, contraditório e risco; investigação não autoriza automaticamente represália física.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Investigação de esconderijo obedece proveniência, contradições e fontes independentes; pistas do plano são claims parciais, não confirmação de toda identidade.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Pista falsa deliberada entra como evidência de uma alegação, com origem privada e cadeia de transmissão; investigação deve questioná-la, nunca promovê-la a confirmação por texto.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Investigação de possível agente duplo separa pistas, fontes e hipótese; nenhuma conclusão LLM isolada confirma traição ou executa sanção.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Recrutamento não confirma veracidade de informe; distinguir relato, evidência, contradição e hipótese; DEC-089 definirá procedimento específico.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Caso investigativo pode juntar informes conflitantes com linhagem/contradições e manter INCONCLUSIVE; suspeita jamais vira confirmação automática de identidade.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Dossiês encapsulam pistas e conclusões revisáveis da investigação sem amplificar certeza; divulgação de identidade segue gates e audiência DEC-077.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Planos de intervenção policial/judicial requerem evidências verificadas, contraditório e gates; suspeita isolada não valida ação HIGH.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Nova hipótese em investigação pode motivar revisão, mas suspeita não basta para mudar alvos coercitivos nem validar identidade real.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Dois observadores disputando NPC/área não provam identidade secreta ou culpa; conflito não libera pistas privadas nem transforma suspeita em fato.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Recovery redige grafos de espera antes de notificar investigadores, sem transformar ID de recurso em pista pública de identidade.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Evento cronológico DEC-096 não torna pista privada descoberta; rumores e documentos devem ter proveniência e adquirir por canais reais.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Canônico DEC-096/C não torna rumorejo de NPC verdade verificada nem confere pista secreta ao grupo; exige origem e aquisição.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Efeito composto DEC-097/C não vale como evidência de verdade de rumor; proveniência de fontes permanece separada.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

A observação de NPC/efeito não prova automaticamente fatos investigativos privados; fontes e evidências seguem regras da DEC-077.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Investigação por evidência não autoriza revelar quest states fora de ACL nem inferir owner por texto.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Investigação exige pistas acessíveis aos atores; probe técnico não constitui pista recebida.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Quest state, mapping rule names and even flag metadata may expose future branches, romance or hidden identities; they remain private technical evidence. Dossiers, sources and NPCs receive only authorized safe milestones through independently confirmed disclosure; no belief is promoted to fact from ambiguous observations. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **investigação baseada em evidências**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para investigação verifica origem independente e contradições de relatos, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para evidência independente e respeito à contestação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Cadeia de evidências de prestação e contraditório, sem self-certification. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Evidência de entrega e contestação mantêm cadeia independente. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
