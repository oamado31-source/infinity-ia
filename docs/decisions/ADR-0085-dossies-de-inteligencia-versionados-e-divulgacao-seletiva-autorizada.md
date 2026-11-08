# ADR-0085 — Dossiês de inteligência versionados e divulgação seletiva autorizada

- **Decisão:** **DEC-090**, opção **C**, aprovada expressamente pelo idealizador em **2026-11-07**.
- **Estado:** **APROVADA COMO ARQUITETURA DE DISCOVERY; NÃO IMPLEMENTADA**.
- **Discovery:** **v8.6**.
- **Documento técnico:** `docs/90-dossies-de-inteligencia-proveniencia-views-acl-compartilhamento-e-difusao-causal.md` (**86 testes candidatos T090-01..T090-86, TODOS NÃO EXECUTADOS**).
- **Preservação:** todas as decisões **DEC-060 a DEC-089** permanecem aprovadas integralmente. Todos os **84 ADRs anteriores (ADR-0001..ADR-0084) permanecem byte a byte idênticos** aos da versão v8.5; nenhuma decisão histórica foi substituída.

## Contexto

A DEC-089/C estabeleceu que um informe entregue não é verdade factual e que corroborações precisam ser independentes, contraditórias e revisáveis. Uma campanha pode reunir depoimentos, documentos, perfis de fontes e hipóteses de investigação; o mesmo conjunto não deve ser revelado integralmente a qualquer aliado, autoridade ou facção. As DEC-019/028/041/076/083–088 já protegem segredos de PCs, pseudônimos, testemunhas, operações de contraespionagem e acordos com informantes. Entretanto, ainda não havia uma política para compor, versionar, filtrar e **transmitir dossiês** com prova de quais campos foram realmente expostos a qual destinatário, quando, por que e por qual canal.

Os NPCs não podem acessar bancos internos de host/IA. O fato de um dossiê existir no overlay privado não significa que os personagens o conheçam. Da mesma forma, uma versão redigida não deve esconder campos apenas na interface, mas impedir que esses dados entrem no payload, prompt, índice, cache ou fila não autorizado.

## Alternativas

- **A — Compartilhamento integral e automático:** rejeitada; vaza fontes, identidades e planos, cria conhecimento universal e suprime incerteza contextual.
- **B — Seleção e divulgação livres pela LLM:** rejeitada; não fornece garantia de ACL, proveniência, exatidão, direitos de divulgação nem recebimento real.
- **C — Dossiês tipados, versionados, filtrados por escopo e autorizados antes da difusão causal:** **APROVADA**.

## Regras vinculantes

1. **Planos epistêmicos independentes:** diferenciar `Dossier` (estrutura restrita), `DossierRevision` (snapshot versionado), `DossierClaim` (alegação com avaliação DEC-089), `EvidenceCitation` (referência verificável e admissível), `DisclosureView` (artefato minimizado para uma audiência), `ShareAuthorization` (consentimento/finalidade), `TransmissionEvent` (envio causal), `RecipientReceipt` (recebimento confirmado) e `ObserverBelief` (compreensão/crença do destinatário). **Dossiê criado ≠ versão autorizada ≠ enviada ≠ recebida ≠ compreendida ≠ verdade factual.**
2. **Proveniência obrigatória:** alegações citam `claim_id`, `assessment_revision`, `EvidenceFamily` de origem, evidências sustentadoras/contraditórias, escopo temporal/espacial e qualificador de confiança. Nenhuma conclusão editorial ou LLM promove hipótese a fato. DEC-061/064/077/089 prevalecem.
3. **Estados explícitos de avaliação:** cada alegação retém a classificação relevante de DEC-089, como `UNVERIFIED`, `PARTIALLY_CORROBORATED`, `CORROBORATED_WITH_SCOPE`, `CONTRADICTED`, `INCONCLUSIVE` ou `STALE`. O dossiê não pode redigir uma conclusão mais forte do que o substrato de evidências; ausência de citação permanece `UNKNOWN`, não confirmação.
4. **Dossiê e versões imutáveis:** criar nova revisão para inclusões, contradições, reavaliações, retratações e atualizações; histórico anterior não é apagado. Uma versão entregue fica referenciável por `dossier_id`, `revision`, `snapshot_hash`, `policy_revision`, `knowledge_pack_binding`, `checkpoint_ref` e `resolution_epoch`. Dossiê de campanha não é lore canônico.
5. **ACL por campo, origem e finalidade:** aplicar proteção de testemunhas DEC-083, PC DEC-019/041/045/046, pseudônimos DEC-076, planos DEC-084/085, desinformação DEC-086, compromissos DEC-087/088, evidências DEC-089 e classificações internas do host. Uma pessoa com acesso ao sumário não ganha acesso ao documento bruto. Uma cópia do dossiê não aumenta permissões do receptor.
6. **Filtragem antes da geração:** produzir `DisclosureView` por **interseção** entre ACL de cada campo, autorização do titular, necessidade da finalidade, competência do receptor, política local e risco agregado. Filtrar **antes** de LLM, RAG, impressão, UI, log, export, LAN, cache ou transmissão. Nenhuma redação puramente cosmética na UI constitui sanitização.
7. **Metadados também são sigilosos:** referências a horários exclusivos, endereços de refúgio, pistas de autoria, nomes de arquivos, IDs visíveis, quantidade de testemunhas, hash acessível ao observador ou padrões de lacunas podem reidentificar uma fonte. Empregar citações públicas desvinculadas, granularidade, supressão e testes de inferência contextual.
8. **Versões por audiência:** o mesmo `DossierRevision` pode gerar `DisclosureView` distinta para investigador autorizado, jogador titular, membro da party, guilda aliada ou autoridade competente. Não reutilizar indiscriminadamente view com ACL mais permissiva; `audience_scope`, `recipient_id`, `purpose`, `policy_revision` e `redaction_manifest` são vinculantes.
9. **Consentimento cooperativo:** um PC só divulga voluntariamente informações/segredos seus conforme sua agência. O host não pode inferir autorização de um delegado, ausência, propriedade de item ou presença na party. Consequências legítimas de outros atores DEC-041/042 permanecem possíveis sob gates — não há veto universal sobre informação que outro NPC conhece legitimamente.
10. **Compartilhamento é ato separado:** compor relatório não envia nada. Solicitar envio requer `ShareProposal` com remetente competente, destinatário, classificação, canal, tempo, confirmação de posse/acesso, consentimento e grau de risco DEC-027/034; `ShareAuthorization` deve ser verificada antes da publicação.
11. **Difusão causal, não instantânea:** só após `TransmissionEvent` válido, disponibilidade/tempo/canais DEC-029/069/074 e `RecipientReceipt` comprovado a audiência recebe a informação. `PENDING` ou `UNCERTAIN` não implica leitura. Um NPC pode receber apenas um resumo e **não** o documento anexo.
12. **Conhecimento e percepção individual:** a entrega não prova que o destinatário entendeu, acreditou ou aceitou a conclusão. `ObserverBelief` se atualiza seletivamente de acordo com percepção/credibilidade DEC-064/065 e narrativas acessíveis; compartilhar com líder não implica que toda a facção saiba instantaneamente.
13. **Fatos brutos e desinformação:** uma `PlantedClaim` DEC-086 pode aparecer rotulada como alegação plantada/suspeita quando isso for acessível à audiência. Nunca reclassificar isca como prova confirmada por incluí-la num dossiê; não revelar o plano verdadeiro ou sua natureza de isca para receptores não autorizados.
14. **Retificações e aviso de correção:** nova prova ou revisão gera nova versão e eventual `CorrectionNotice` com vínculo à versão anterior, público e canal. O sistema pode solicitar retransmissão autorizada e propagar correções gradualmente, não fazer NPCs esquecerem o que receberam nem apagar danos passados. DEC-080/081 se aplicam a efeitos de ordens, injustiças e reparações.
15. **Retransmissão controlada e realista:** cópia posterior, republicação, vazamento ou relato indireto requer evento causal próprio, fonte/posse legítima e risco. A política proíbe retransmissão indevida no software, mas não afirma poder impedir uma divulgação narrativa que NPC capaz de agir efetivamente realize; denúncias de vazamento passam pela DEC-077/085.
16. **Multiplayer e host:** fonte de fatos mecânicos permanece host DEC-011; uma `DisclosureView` não pode criar objetos/documentos dentro da engine nem abrir diálogo/quest, alterar alinhamento, reputação mecânica, inventário, ouro ou flag sem gateway DEC-012, autorização, capabilities testadas e recibo confiável. Em conflito `UNCERTAIN`, não fazer retry cego.
17. **Segurança local-first:** workers LAN DEC-057/058 e modelos alternativos DEC-059 não herdam segredo por capacidade de hardware; ACL é aplicada antes de solicitar inferência, os serviços recebem mínimo payload e as saídas são validadas contra a view autorizada, com logging redigido.
18. **Temporalidade e segmentação:** escopos `campaign_id`, `branch_id`, `year_DR`, `valid_time_window`, `checkpoint`, `resolution_epoch`, `knowledge_pack_revision`. Não utilizar informação futura, dossiê de outro ramo ou avaliação posterior à versão enviada, inclusive após restore. Anos DR do cânone ficam **fisicamente separados** em `knowledge/periods/<ANO>-DR/` DEC-060; dossiês dinâmicos somente no overlay privado da campanha.
19. **Idempotência, filas e invalidação:** deduplicar por chave composta (`dossier_id`, `revision`, `view_id`, `recipient_id`, `purpose`, `transmission_event_id`, `resolution_epoch`). Revogação de ACL invalida emissões futuras e jobs pendentes; **não apaga memória legitimamente adquirida** nem presume retirada de cópias já entregues. Migração DEC-052 e checkpoint DEC-053 precisam reconciliar índices, conteúdo e entregas.
20. **Princípio de minimização e custo:** composições determinísticas e diffs primeiro; sumários assistidos por LLM local só quando úteis, com corpus de input filtrado e output validado. Não gerar um dossiê novo por tick de NPC; recuperar/atualizar por evento, assinando revisões e aplicando cache por política/escopo DEC-056.
21. **Falhas seguras:** ACL desconhecida, prova sem origem, destino inconclusivo, receptor sem competência, canal indisponível, payload grande demais, revisão obsoleta, link de branch errado ou teste de vazamento falho => `REJECTED/STALE/PENDING` com justificativa redigida, não compartilhamento permissivo.
22. **Limite de implementação:** o modelo é arquitetura e contratos candidatos. Não há POC de journal, documentos/itens nativos, UI de dossiê, sincronização por dois clientes, troca de documentos ou divulgação real via EEex/BG2:EE comprovada.

## Exemplo hipotético

Um grupo reúne dez depoimentos e três documentos sobre reuniões clandestinas em Athkatla. A versão privada inclui identidades de testemunhas, um plano de refúgio e uma fonte alegando que a reunião será no armazém norte. A view de uma autoridade competente pode incluir determinadas evidências com origem protegida; a view de um aliado pode incluir apenas a hipótese parcialmente corroborada e seus limites. Uma terceira facção não recebe nada enquanto não houver transmissão legítima. Uma correção posterior gera revisão e aviso **somente** para os públicos alcançáveis, sem reescrever o que as pessoas acreditaram no passado.

## Consequências e riscos

- **Benefício:** coordenação cooperativa sem onisciência, cópias auditáveis, fontes protegidas, evidência com incerteza visível e transmissão contextual.
- **Custo:** política por campo, análise de inferências indiretas, reviews de risco, versões/assinaturas, receipts de distribuição e preservação de crenças históricas.
- **Riscos:** metadados reidentificadores, truncamento enganoso, discurso da LLM reforçando alegações, views excessivas, reenvio indevido, caches stale e branch leakage.
- **Evidência:** aprovação da decisão; **86 testes T090-01..86 candidatos NÃO EXECUTADOS**. Não há integração mecânica comprovada.

## Próxima DEC-091 — aberta

**Planejamento e ações a partir de inteligência incerta:** A) dossiês corroborados autorizam automaticamente ações; B) LLM escolhe e executa operações; **C (recomendada)** planos operacionais fundamentados por validade temporal e qualidade da evidência, risco, recursos, consentimento e autoridade, com passagem por gates do host e resultados verificáveis; informes incertos podem orientar investigação sem disparar coerção.
