# Documento 65 — Memória hierárquica, consolidação, retenção e recuperação contextual de NPCs

> **Discovery v6.1 — DEC-065/C aprovada, ADR-0060.** Desenho de arquitetura, dados e testes **CANDIDATOS**, não especificação implementada; nenhuma integração BG2:EE/EEex ou benchmark foi executado.

## 1. Objetivo e invariantes

Permitir que NPCs tenham histórias pessoais contínuas durante campanhas longas e recuperem apenas memórias pertinentes. Consolidar episódios sob demanda sem transformar resumo em acontecimento, reduzir relevância de informações triviais sem apagar provas históricas e proteger compromissos e segredos. Não vincular esquecimento a uma regra simples de decaimento temporal.

**Invariantes:**

1. Cânone anual DEC-060: **separação física obrigatória** `knowledge/periods/<ano>-DR/`; nenhum índice ou base global desprotegida que una todos os anos e facilite vazamento de futuro. Antecedentes somente por validade/ACL; Knowledge Pack DEC-063 referencia versões anuais.
2. Episódios, crenças e sínteses são **por campanha/branch/NPC**, nunca alegações publicadas no diretório anual de lore. DEC-064 rege aquisição e atualização de crenças.
3. `SOURCE_EVENT` confirmado e `NPC_BELIEF` não são sinônimos de `CANON_FACT` nem de `ENGINE_CONFIRMED`; `UNCERTAIN` nunca recebe promoção automática.
4. As fontes e suas licenças, divergências e revisões são regidas pelas DEC-061/062; não há ingestão direta de material em memória de NPC pela publicação editorial.
5. Recuperação aplica permissão e contexto **antes** de buscar/citar, e valida novamente antes de montar prompt, transmitir a nó LAN ou publicar diálogo.
6. Nenhuma alteração de memória escreve diretamente em quest, save, variável, alinhamento, reputação ou estado de party; seguir Action Gateway/host.
7. Não há tempos de retenção, pesos de saliência, limites de tokens, periodicidade, formato físico de banco, chaves, modelos ou thresholds estabelecidos nesta Discovery.

## 2. Camadas de memória — funções e regras de autoridade

| Camada lógica | Conteúdo | Recuperação/atualização | Invariante |
|---|---|---|---|
| `WORKING` — contexto imediato | Trecho atual da cena e referências recentes | Cache por sessão/turno, com revisão e ACL | Descartar cache não apaga episódio nem confirma fato |
| `EPISODIC` — episódios | Observação, diálogo, relato, experiência datada e fontes | Consultar por NPC, identidade, cenário, tempo e permissão | Origem e evidência preservadas; contradições possíveis |
| `CONSOLIDATED` — interpretações/associações | Sínteses reconstruíveis, padrões de relacionamento, lições e crenças acessíveis | Atualizar somente a partir de episódios autorizados e validação | Não cria testemunho, fato nem mudança de crença por atalho |
| `PROTECTED` — âncoras críticas | Referências protegidas a compromissos, segredos, marcos e relações | Proteção por política e justificativa, recuperação seletiva | Proteção contra compactação **não** autoriza divulgar segredo |

Uma lembrança pode ser simultaneamente episódio e âncora, mas não é duplicada como duas verdades. **Criticidade não é sinônimo de certeza**: promessa ou acusação relevante pode ter fonte incompleta ou continuar subjetiva.

### 2.1 Critérios candidatos de saliência

Considerar relevância para cena, vínculo com PCs/NPCs, compromisso ativo, consequências confirmadas, frequência e intensidade de interações, impacto emocional narrativo representado por regras, confiabilidade da fonte, recência contextual, alcance das permissões e riscos de inconsistência. **Nenhum peso ou escore numérico foi aprovado.** Se um classificador LLM sugerir relevância, usar como proposta revisável; não criar fatos ou prioridade de retenção inquestionável.

### 2.2 Proteção e revisão de âncoras

- Âncoras podem referenciar salvar um familiar, dívida vitalícia, promessa, traição, segredo, morte, reencontro, arco pessoal, evento histórico reconhecido pelo NPC.
- Vincular cada âncora a fonte/episódio/ramo, motivo de proteção, responsável/política, revisão, classificação e dependências de quests/relacionamentos. Não existe marcação irreversível concedida apenas por texto de LLM.
- Se houver múltiplas âncoras repetidas, manter referências consistentes, sem consolidar pessoas/acontecimentos diferentes por semelhança superficial.
- Pedidos legítimos de apagamento e exigências legais/privacidade exigem procedimento próprio: proteção narrativa **não** é justificativa para guardar dados privados indefinidamente.

## 3. Contratos de dados candidatos (não implementados)

```text
MemoryEvent {
  event_id, campaign_id, branch_id, npc_identity_id,
  observed_at_dr, recorded_at_revision, kind,
  source_event_id?, source_claim_id?, witness_channel?, location?,
  reliability_markers?, acl_classification, content_ref,
  host_confirmation_id?, state: CONFIRMED | SUBJECTIVE | UNCERTAIN
}

ConsolidationRecord {
  summary_id, campaign_id, branch_id, npc_identity_id,
  source_event_ids[], source_revision_hashes[],
  claim_and_belief_revision?, knowledge_pack_id?,
  created_at_revision, permissions_fingerprint,
  summary_ref, uncertainty_flags[], status: CANDIDATE | VALIDATED | STALE | REJECTED
}

ProtectedAnchor {
  anchor_id, campaign_id, branch_id, npc_identity_id,
  event_refs[], anchor_kind, reason, policy_revision,
  acl_classification, eligibility_for_review, content_hash
}

MemoryRetrievalRequest {
  campaign_id, branch_id, npc_identity_id, world_clock_dr,
  scene_id, knowledge_pack_id, requester_identity,
  requester_acl, query_purpose, latency_budget_class,
  narrative_state_revision, observation_revision
}

MemoryRetrievalResult {
  selected_event_refs[], selected_consolidations[],
  protected_refs_used[], provenance[], uncertainty_tags[],
  access_decisions[], revision, expires_on_change,
  state: READY | PARTIAL_SAFE | DEFER | DENIED | UNCERTAIN
}
```

Os nomes são ilustrativos. **`npc_identity_id` é contrato lógico não resolvido:** a correspondência com objetos do BG2:EE fica para DEC-066 e provas de conceito; não atribuir memória de NPC pelo nome isolado.

## 4. Pipeline de aquisição, consolidação e recuperação

```text
Host/bridge e eventos narrativos verificados
         |
  [aquisição legítima DEC-064 + ACL DEC-028/029]
         v
MemoryEvent por campanha/ramo/NPC -- classificação de relevância --> âncoras protegidas
         |                                                   |
         +------ agenda de consolidação (DEC-056) -----------+
                        |
               síntese derivada + links às fontes
                        |
                  validação DEC-060
                        |
                versão de projeção candidata
                        |
          commit coordenado/checkpoint DEC-053
                        |
              índice consultável com ACL
                        |
          recuperação por cena e NPC -> contexto mínimo -> Model Router DEC-059
                        |
                  validação de saída DEC-060
                        |
               proposta narrativa / diálogo
```

**Consolidação:**

1. Selecionar subconjunto de episódios *pertencentes ao mesmo NPC, campanha e branch*, autorizados à tarefa; não misturar anos do cânone nem timelines incompatíveis.
2. Obter dependências e versões, analisar materializações/duplicatas, conservar distinção entre observação, rumor e crença. Uma síntese nunca é prova de que um episódio ocorreu.
3. Criar resumo candidato citando `source_event_ids`; usar regras determinísticas onde suficientes e LLM opcional conforme roteador/privacidade. Nenhum modelo pode autenticar sozinho o evento.
4. Validar relações, referências, contradições, confidencialidade e compatibilidade temporal; rejeitar ou adiar se faltarem fontes.
5. Publicar materialização versionada após gates e checkpoint elegíveis; preservar evento de origem segundo política de retenção aplicável.
6. Ao mudar uma fonte, permissão, crença ou ramo, invalidar projeções dependentes e reconstruir apenas quando seguro. Em overload, usar evento verificado disponível ou adiar; não sintetizar falsa recordação.

**Recuperação:**

1. Confirmar identidade do NPC, campanha, branch, época DR, revision, propósito e permissões do solicitante. `UNCERTAIN` → DEFER.
2. Aplicar ACL e classificação **antes da busca e da seleção**; um segredo não aparece em metadados, ranking, logs ou resposta de acesso não autorizado.
3. Selecionar lembranças relacionadas à situação, à pessoa, ao tema, às promessas e às relações; âncoras relevantes recebem proteção contra exclusão de índice, não passagem automática ao prompt.
4. Verificar tempo, fonte, revisão e credibilidade; crenças divergentes podem ser expressas como ponto de vista do NPC, não como verdade do narrador.
5. Montar contexto mínimo e enviar apenas a executor permitido DEC-057/058/059; validar saída DEC-060 antes da narração/diálogo.
6. Se resumo estiver stale, recuperar fontes mínimas verificadas ou adiar. Nunca preencher silenciosamente a lacuna com informação inventada.

## 5. Política de esquecimento versus retenção

| Ação | Pode ocorrer? | Condição |
|---|---|---|
| Descartar cache de trabalho | Sim | Sem eliminar episódio histórico nem obrigação narrativa |
| Reduzir prioridade de recuperação de evento trivial | Sim, por política | Evidência, ACL e possibilidade de recuperação conservadas |
| Gerar resumo com referência | Sim, após validação | Deve ser auditável e reconstruível, sem criar fato novo |
| Esconder detalhe da resposta do NPC | Sim | Falha de lembrança/recuperação ≠ exclusão da evidência |
| Excluir evento histórico de forma automática por idade | **Não aprovado** | Requer decisão de retenção/privacidade específica |
| Apagar evento/segredo por demanda legítima de privacidade | Somente por política apropriada | Redação, eliminação segura e implicações de snapshots/backups especificadas e auditadas |
| Excluir âncora crítica por otimização de armazenamento | Não | Necessita procedimento explícito de revisão e dependências |
| Reescrever fato do host, quest ou cânone por resumo | Nunca | Host/gateway, curadoria e atos confirmados prevalecem |

## 6. Escopo temporal, conhecimento e campanhas

- **Fatos canônicos:** `knowledge/periods/<ano>-DR/` e seus arquivos separados fisicamente DEC-060. Não criar `all-years.db` como corpus indiscriminado. Índices auxiliares, se propostos em SPECS, devem conservar isolamento por partição/ano, autorização e proveniência, sem acessos multi-ano indiscriminados.
- **Fontes conflitantes:** DEC-061 mantém cada fonte/versão, `UNRESOLVED` não vira consenso por consolidação.
- **Ingestão:** DEC-062 é única porta de publicação no cânone; resumo de memória NPC não entra no diretório anual por esse processo.
- **Knowledge Pack:** manifesto versionado da DEC-063; atualização editorial não muda automaticamente crenças, episódios e resumos dos NPCs. Reindexação após migração exige revisão do diff, ACL e estado.
- **Crença:** DEC-064 mantém episódios de aquisição, história de revisão e divergência subjetiva; resumo de crença não sobrescreve uma opinião passada documentada.
- **Relógio:** respeitar relógio híbrido DEC-022, revisões de campanhas, eventos retroativos controlados e simulação ACT/NEAR/DISTANT/DORMANT DEC-021; não enviar eventos futuros para NPCs do passado.

## 7. Distribuição, consistência e proteção de dados

- **Local-first:** o host mantém a autoridade mecânica; trabalhadores LAN pareados (DEC-057/058) só recebem dados minimizados pertinentes e devolvem resultados candidatos. Revogação invalida caches e tarefas pendentes, sem prometer retirada de dados anteriormente vistos pelo nó.
- **Resource Director:** consolidação é trabalho não urgente agendável, com filas duráveis, limites por NPC/campanha e backpressure. Diálogo urgente consulta índices/projeções validados; sem inferência universal a cada tick.
- **Idempotência:** jobs usam chave composta por campanha, branch, NPC, janela de eventos, fonte/revisão, ACL, propósito e versão do algoritmo. Retries/stale não fazem commit duplo.
- **Checkpoints:** snapshot e log incluem revisões/manifestos suficientes para reconstruir projeções por NPC; backup conserva vínculo com evento mecânico/narrativo confirmado. Restauração de branch A não injeta memória de B.
- **Observabilidade:** medir recursos e erros de cache/índice sem registrar segredos pessoais, prompts integrais ou identidades sensíveis em telemetria não consentida.
- **Privacidade/exclusão:** políticas de manutenção, retenção, expurgo, backups, pseudonimização e eventuais pedidos legítimos de eliminação dependem de SPECS e obrigações aplicáveis. Não confundir trilha causal com autorização irrestrita de retenção.

## 8. Estados de operação e exemplos

| Condição | Resultado seguro proposto |
|---|---|
| Resumo válido com fontes e ACL coerentes | `READY` / incluir somente trechos relevantes |
| Fonte parcial confiável e nenhum segredo | `PARTIAL_SAFE` com incerteza preservada |
| Evento do host ainda `UNCERTAIN` | `DEFER`, sem afirmar acontecimento confirmado |
| Identidade de NPC ambígua | `DEFER`, deixar correlação para DEC-066 |
| Conhecimento de ano futuro não autorizado | `DENIED`, não usar como fato presente |
| Resumo stale por mudança de pack/branch/ACL | `DEFER` ou reconstrução com fontes autorizadas |
| Worker LAN revogado | Ignorar resultado, revogar novas tarefas e invalidar projeções |
| Falha de consolidação | Manter eventos válidos e usar última projeção compatível, ou adiar |

### Exemplo hipotético — taverneiro entre 1369 e 1379 DR

- Um episódio confirmado de 1369 registra que um aventureiro salvou sua família. Classificar como **âncora relacional**, preservar origem e consequências sem presumir que todo detalhe estará no prompt.
- Em 1379, o NPC pode lembrar-se de gratidão mesmo depois de muitas interações triviais; obter os episódios fundadores se a conversa exigir detalhes específicos.
- Uma acusação ouvida de terceiros pode permanecer como crença controversa, com identificação do informante e possibilidade de reavaliação DEC-064.
- Pedidos de taberna triviais não precisam figurar em todos os diálogos; nenhum prazo automático de perda é fixado.
- Se um personagem com o mesmo nome aparecer em outro local, não compartilhar memórias até identidade validada (DEC-066).

## 9. Testes candidatos — NÃO EXECUTADOS

1. **T065-01:** Memória de trabalho pode ser descartada sem perder episódio persistido.
2. **T065-02:** Episódio preserva fonte, data DR, campanha, ramo e identidade NPC.
3. **T065-03:** Síntese contém vínculo auditável com eventos-fonte autorizados.
4. **T065-04:** Síntese não inventa testemunho, relação ou acontecimento ausente.
5. **T065-05:** Rumor falso não vira fato canônico após consolidação.
6. **T065-06:** Mudança de crença não apaga episódio nem crença antiga.
7. **T065-07:** Memória crítica de resgate familiar mantém referência após anos.
8. **T065-08:** Uma memória antiga trivial pode sair do prompt sem apagar fonte.
9. **T065-09:** Segredo protegido nunca aparece a solicitante sem ACL.
10. **T065-10:** Classificação de proteção não obriga revelação no diálogo.
11. **T065-11:** Busca aplica ACL antes de ranking e retorno de metadados.
12. **T065-12:** Revogação de acesso invalida resumo e cache derivados.
13. **T065-13:** Resultado de worker LAN revogado não é incorporado.
14. **T065-14:** Retransmissão idempotente não duplica síntese publicada.
15. **T065-15:** Síntese stale de outra revisão é rejeitada ou reconstruída.
16. **T065-16:** Branch B não recebe episódios exclusivos da branch A.
17. **T065-17:** NPC diferente com mesmo nome não herda memória.
18. **T065-18:** Identidade ambígua causa DEFER, sem merge por heurística.
19. **T065-19:** Fato de 1370 não vaza como ocorrido em 1369.
20. **T065-20:** Índice auxilia sem quebrar partições físicas anuais do cânone.
21. **T065-21:** Atualização de Knowledge Pack não altera crença automaticamente.
22. **T065-22:** Fonte curatorial UNRESOLVED não vira certeza em resumo.
23. **T065-23:** Evento mecânico UNCERTAIN não é lembrança confirmada.
24. **T065-24:** Resumo não altera quest, reputação ou alinhamento diretamente.
25. **T065-25:** Falha do LLM não inventa memória nem bloqueia gameplay básico.
26. **T065-26:** Saturação agenda consolidação sem loop por NPC/tick.
27. **T065-27:** Restauração de checkpoint recupera eventos, âncoras e revisões compatíveis.
28. **T065-28:** Backup desatualizado não sobrescreve eventos confirmados posteriores.
29. **T065-29:** Traço de observabilidade não contém segredo nem prompt integral.
30. **T065-30:** Pedido legítimo de expurgo é encaminhado à política e não ignorado por etiqueta crítica.
31. **T065-31:** Memória de relação antiga é recuperada por contexto sem busca exaustiva.
32. **T065-32:** Relatório registra ausência de medição/compatibilidade real em BG2:EE/EEex.

## 10. Pendências para SPECS e próxima decisão

Definir identidade do NPC e reconciliação com entidades da engine (DEC-066), storage e política de retenção legal/privada, topologia local, estratégia de índices com ACL, saliência/configuração, custo de tokens, limites de I/O, critérios mensuráveis de qualidade, thresholds de risco, versões de modelos e orçamento, qualidade de diálogos, e matriz de POCs por build/multiplayer. **Nenhum teste acima é evidência de funcionamento; todos são hipóteses verificáveis.**

**Próxima DEC-066:** mecanismo de identidade persistente de NPCs através de saves, spawns, regiões, sessões e migrações de build. Alternativas A — somente IDs do motor; B — nome/posição/heurísticas; C — ID lógico estável por campanha com mapeamento validado, detecção de ambiguidade e fail-closed (recomendada).

### Integração DEC-066/C — identidade como pré-condição de memória (v6.2)

Os contratos candidatos do doc. 65 passam a depender de `NPCIdentity` persistente e `VerifiedBinding` com `EngineObservation` atual, definidos conceitualmente no doc. 66. Recuperação, âncoras e consolidações não passam a homônimo, clone, spawn genérico ou branch divergente sem correspondência positiva. `AMBIGUOUS`/`STALE` bloqueiam personalização e invalidam índices dependentes; memórias não são apagadas por falha de match. DEC-060–065 continuam intactas, inclusive cânone por ano DR e overlay de campanha.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Memória de NPC promovido DEC-067 segue camadas DEC-065, ACL e proteção de âncoras críticas; reduzir simulação não é apagar episódios. Sem LLM contínuo.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

DEC-068/C suspende atividade e conserva índices/âncoras da memória por NPC, sem descartar episódios ao entrar em DORMANT. Reidratação aplica ACL, identidade verificada, epoch e saliência; resumir não equivale a inventar vida fora de cena.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: episódios de viagem confirmados podem ser memórias recuperáveis com fontes; não gerar retrospectivamente aventuras apenas porque o NPC esteve ausente.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: eventos relevantes devidamente confirmados podem ser âncoras; propostas/boatos não se consolidam como experiências vividas. Retenção/ACL separada de cronologia canônica.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Registro de encontro DEC-071 confirmado vira episódio derivado com evento de origem; deduplicar a mesma experiência gerada por offscreen/local e proteger âncoras sem inventar testemunho.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Memória NPC DEC-065 não deve tratar template DEC-072 pendente como evento ocorrido. Resumos e âncoras só referenciam episódios efetivamente confirmados e com ACL.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Âncoras críticas e proveniência de lembranças confirmadas persistem mesmo quando o encounter remove componente temporário.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Mensagens DEC-074 podem ser recuperadas como lembranças com proveniência, saliência e ACL; deduplicação de relatos não equivale a perda das experiências pessoais. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Consolidar lembranças de testemunhos sem perder origem, confiança, distinção fato/rumor e reconhecimento; não transformar síntese em recibo de host.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Resumo de memória não deve fundir duas personas por semelhança textual, nem expor `actor_identity_id` oculto em prompts. Âncoras críticas e provas retêm sua ACL.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação por evidências (Discovery v7.3; não implementada)

A investigação de personas DEC-076 usará ledger privado por campanha/ramo, com pistas e hipóteses revisáveis, origem/independência de fontes, contraprovas e estados inconclusivos. Suspeita ou fala LLM não confirma identidade e não permite divulgação; vínculo factual restrito exige evidências/DEC-066, e revelação exige ACL/consentimento/risk gate por audiência (DEC-019/028/041/045/046). Rumores e repercussões DEC-029/074/075 são separados de fato e punição. **Preservar `knowledge/periods/<ANO>-DR/` fisicamente por ano, sem evidências privadas no cânone.** ADR-0072/documento 77; 58 testes não executados, sem POC BG2:EE/EEex/multiplayer.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Memória de acusado/autoridade DEC-078 registra episódios e decisões sem apagar fontes contrárias ou converter alegação em fato confirmado.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Memória da recepção/recusa/negociação de pedido DEC-079 preserva fontes e ACL; resumir episódio não transforma autoridade incerta em poder reconhecido.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Uma revogação DEC-080 conhecida não apaga o episódio anterior em que NPC acreditava no mandado; distinguir correção de crença e estado da ordem.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Memórias de danos e de reparação são episódios distintos, com proveniência/ACL; limpeza de NPC temporário ou pedido de desculpas não remove memória de fato.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Resumo de memória de autoridade mantém origem/certeza dos relatos e não simplifica boato de corrupção em conclusão factual.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Consolidação não remove rótulos de sigilo/proveniência ou revela nome em resumos de memória; revisões mantêm trilha.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Âncoras de proteção e ameaças confirmadas preservam proveniência/ACL; resumo de memórias não vaza identidade/rotas.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Consolidação de memória não completa campos sigilosos ausentes, nem torna rumor verdadeiro; representar informação parcial sem expor ProtectedPlanTruth.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Consolidar rumor falso preservando source chain e status epistêmico; sumarização não transforma alegações repetidas em fatos.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Consolidação de memória não funde falsas acusações com compromissos verificados nem expõe segredos em sumários de baixa ACL.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Consolidar memórias de NPC não une ofertas de homônimos nem elimina cláusulas/ressalvas; retenção de termos sigilosos respeita ACL.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Resumo hierárquico de NPC preserva âncoras da fonte/contradição ou indicador de ausência de prova; não consolida relatos dependentes em fato.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Resumo de memória deve reter qualifier, origem permitida e ACL, sem comprimir contradições importantes nem revelar dados do dossiê bruto a observador não autorizado.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Memória consolidada pode armazenar que um NPC pretende fazer algo, não que já o realizou; distinguir proposta/receipt.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Consolidação de memória não apaga que um NPC acreditou em versão antiga; mudança de plano não gera amnésia universal.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Memória consolidada não inventa participação simultânea de NPC singular, nem cria acesso a plano confidencial a partir de metadados de reserva.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Sumarização de memórias não deve converter descontinuidade de lease em acontecimento testemunhado, nem publicar metadados confidenciais.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Lembretes/sínteses de NPC DEC-096 só usam acontecimentos aprendidos em período/campanha corretos, não tabela física global.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Resumo NPC de evento DEC-096/C preserva origem/recepção/tempo, nunca memória onisciente de guerra distante.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Snapshot agregado DEC-097/C não pode virar relato onisciente de NPC, que precisa de canais e proveniência próprios.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Consolidação de memória/retensão não recebe informação privada de snapshots sem aquisição causal nem altera estado mecânico local.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Consolidação de memória narrativa não atualiza engine_instance_generation nem campos protegidos.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Crenças e confabulações de NPCs não validam valor de flag técnico privado.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Memória NPC decorre de aquisição causal, não de observação host ou rebase de projeção DEC-102. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **memória falível**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para consolidação de memória sem apagar notícia antiga ou fonte de crença, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para memória histórica mantém acusação e correção, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Recebimento de carta não implica crença em quitação. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Rumores de pagamentos não substituem comprovantes host-confirmed. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
