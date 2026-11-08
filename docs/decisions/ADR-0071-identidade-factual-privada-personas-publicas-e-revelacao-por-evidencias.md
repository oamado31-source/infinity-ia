# ADR-0071 — Identidade factual privada, personas públicas e revelação por evidências

- **Decisão:** **DEC-076**, opção **C**, aprovada expressamente pelo idealizador em **2026-11-06**.
- **Estado:** APROVADA **somente em arquitetura**, Discovery **v7.2**; **NÃO IMPLEMENTADA**.
- **Documento técnico:** `docs/76-identidade-privada-pseudonimos-disfarces-reconhecimento-e-revelacao-segura.md` — **56 testes candidatos T076-01..T076-56, NÃO EXECUTADOS**.
- **Preservação:** DEC-060 a DEC-075 e ADR-0055 a ADR-0070 permanecem integralmente aprovados e **byte a byte idênticos** aos documentos v7.1. Mantêm-se também os demais ADRs prévios.

## Contexto

DEC-075 separou autoria factual de reconhecimento público. Em campanhas cooperativas, um PC pode agir anonimamente, ser conhecido por pseudônimo, tentar um disfarce, ser falsamente associado a outro ator ou ter sua identidade revelada apenas a certos indivíduos. Um NPC pode ter identidades sociais diferentes em localidades ou facções. A narrativa deve suportar esses estados **sem** considerar que conhecimento factual privado implica conhecimento universal, ou que BG2:EE dispõe de mecânica de disfarce/renomeação de instâncias em runtime. Um rótulo visível na UI, nome de recurso ou telemetria não é automaticamente prova epistêmica de um NPC.

## Alternativas e decisão

- **A — Identidade factual sempre pública:** rejeitada por eliminar anonimato, espionagem e histórias de infiltração e por vazar segredos.
- **B — Personas eternamente isoladas:** rejeitada por impossibilitar descoberta legítima, investigação, correção e consequências de revelação.
- **C — Identidade factual privada e personas públicas contextuais, com vínculos/revelações baseados em evidências:** **APROVADA**.

## Regras vinculantes

1. **Separação ontológica:** distinguir `FactualActorIdentity` (identificador de ator comprovado e acessível apenas a componentes autorizados), `Persona` (nome/apresentação contextual), `PersonaClaim` (alegação sobre quem alguém é), `IdentityLinkEvidence` (evidência de correlação), `IdentityLinkAssessment` (avaliação de ligação), `ObserverBelief` (o que cada observador acredita) e `DisclosureEvent` (quem foi informado, por qual canal e com quais permissões). Não converter alegação, suspeita ou rumor em ligação factual.
2. **Escopos:** identidades e personas sempre ligadas a `campaign_id`, `branch_id`, `actor_identity_id`, `persona_id`, revisão, tempo DR e contextos regional/social/faccional. Nenhum link cruza campanhas/branches sem migração explicitamente autorizada e reconciliada.
3. **Vínculo factual restrito:** o mapeamento real de uma persona a um ator só existe quando há evidência confiável e identidade lógica verificada DEC-066. A titularidade do PC, controle temporário DEC-045/046 e nome/persona são campos distintos. Não reconhecer ator por igualdade textual, raça, classe, roupa, localização, avatar ou semelhança descrita.
4. **Personas podem coexistir:** uma identidade factual pode manter várias personas simultâneas; uma mesma denominação pública pode ser utilizada por diferentes atores, ficando `AMBIGUOUS`. Um alias não prova unicidade, nem transfere memórias ou crédito.
5. **Conhecimento por observador:** NPCs/facções só recebem a associação persona↔ator por percepção demonstrável, prova legítima, documento confiável, investigação ou difusão temporal/social DEC-029/074. A base privada pode conhecer o vínculo sem revelar aos NPCs. Observações de quem não poderia saber são rejeitadas.
6. **Estados de ligação candidatos:** `UNLINKED`, `SUSPECTED`, `VERIFIED_PRIVATE`, `DISCLOSED_TO_SCOPE`, `DISPUTED`, `REVOKED/STALE`. `SUSPECTED` não revela identidade verdadeira nem concede certeza. `VERIFIED_PRIVATE` não implica `DISCLOSED_TO_SCOPE`.
7. **Proveniência de provas:** qualquer hipótese de identidade registra fonte, evidência, janela temporal, região, cadeia de custódia conceitual, validade, confiança e contestação. Documentos forjados/boatos podem ser alegações de personagens, jamais confirmação automática.
8. **Revelação com gates:** correlacionar internamente, contar a um NPC, revelar à guilda ou divulgar publicamente são ações diferentes, com `purpose`, `audience`, `scope`, `risk`, prazo e política aplicável. Divulgação de segredos de PC/histórico exige política de consentimento DEC-019/041/046, ACL DEC-028, necessidade narrativa e autorização explícita conforme grau de risco. Não usar conhecimento de auditoria/host como permissão de publicação.
9. **Ausência de decisão automática crítica:** exposição involuntária de identidade secreta de jogador, consequências permanentes, retaliações graves, PVP ou dano severo dependem dos gates MEDIUM/HIGH e de consentimento/autorizações aplicáveis. Se houver dúvida sobre permissão, **fail-closed**, mantendo a hipótese privada ou pendente.
10. **Reconhecimento versus disfarce mecânico:** a engine pode exibir nomes, retratos, aparência ou scripts nativos. A narrativa não pode prometer ocultar ao cliente dados mecânicos visíveis. Disfarce visual, troca de identidade de ator, efeitos de detecção e compatibilidade de mods requerem SPEC e POC por build/host+2 clientes. Até lá, personas são **modelo narrativo**, não capacidade provada da engine.
11. **Não retroatividade automática:** revelar um pseudônimo hoje não reescreve fatos, diálogos passados, autoria confirmada ou percepções anteriores. Pode criar um episódio de descoberta, seguido de novas crenças e repercussões causais. Reconciliação de reputação social não é soma cega de valores entre personas.
12. **Reputação por persona e público:** DEC-030 permite perfis percebidos por NPC, facção e região; a reputação factual do ator e as reputações atribuídas às personas são vistas separadas. Descoberta pode gerar proposta de revisão pontual, proporcional, deduplicada e autorizada, não fusão global instantânea.
13. **Ledger e idempotência:** divulgação usa identificadores estáveis `disclosure_id`, `evidence_id`, `identity_link_revision`, `audience_scope`, `cause_event_id`, `rule_revision` e `resolution_epoch`; repetição, rumor reenviado, reload ou worker de LAN não revelam nem aplicam impactos duas vezes.
14. **Temporalidade e persistência:** vínculo e suspeita obedecem ano DR, conhecimento disponível naquele instante, Knowledge Pack pinado DEC-063, checkpoint, branch e clock DEC-022. Restaurar save anterior não importa revelação futura; caches/contextos ligados a persona antiga são invalidados quando ocorre revogação/branch mismatch.
15. **Segurança local-first e minimização:** roteador de modelos DEC-059, workers LAN DEC-057/058 e prompts só recebem pseudônimos e contexto filtrado quando a identidade privada não for necessária; secrets e correlações explícitas não vazam por logs, embeddings de índice, cache, UI ou telemetria sem ACL. Não há opt-in de compartilhamento implícito.
16. **Separação de dados:** diretórios canônicos físicos `knowledge/periods/<ANO>-DR/` DEC-060 contêm lore curado, sem segredos ou personas dinâmicas da campanha. Provas, aliases, relações entre personas, crenças e descobertas pertencem exclusivamente ao **overlay privado por campanha e branch**; proveniência DEC-061/062 e pack versionado DEC-063 permanecem válidos.
17. **Segurança mecânica:** criar alias, disfarce narrativo, rumor ou reconhecimento não altera nome nativo, aparência, facção/rep mecânica, alinhamento, quests, XP ou inventário. Qualquer ação de engine usa DEC-012, confirmação do host DEC-011, risco DEC-027 e capability testada. LLM não autoriza sozinho.
18. **Revelação contestável:** evidência posteriormente refutada cria reavaliação documentada `DISPUTED/REVOKED`; percepções podem evoluir gradualmente DEC-064, sem apagar que alguém acreditou na identidade falsa. Sem "desfazer" automaticamente danos sociais já confirmados.
19. **Cooperativo justo:** titular do personagem controla visibilidade de seu histórico conforme DEC-019; delegação, ausência e consentimento são explicitados DEC-041/045/046. Um jogador não obtém automaticamente acesso ao segredo de outro por estar na mesma party ou operar NPC delegado.
20. **Recursos e auditoria:** filtros determinísticos antes do LLM, avaliação assistida de evidências apenas como proposta DEC-060, filas e limites DEC-056; registrar motivo legível de vínculo, suspeita, recusa ou divulgação sem expor no próprio log o segredo ao destinatário errado.
21. **Implementação progressiva:** fixtures sintéticas primeiro, gates de ACL e dedup, reputações por persona, testemunhas conflitantes, restore, co-op, POC bridge read-only, depois host+2 clientes. Nenhuma capacidade do motor foi validada.

## Exemplo hipotético

Uma ladina ajuda uma guilda sob o pseudônimo **Corvo Cinzento**. O ledger factual privado vincula ações à personagem somente quando houver prova; para os NPCs da guilda ela é "Corvo Cinzento". Uma testemunha pode suspeitar da ligação com outra identidade sem receber automaticamente confirmação. Se prova válida for obtida e a divulgação passar pelos gates, somente o público destinatário legítimo poderá aprender a relação; reputação e confiança poderão mudar por eventos causais novos. A existência desse exemplo **não** afirma mecânica de disfarce ou reconhecimento disponível em BG2:EE.

## Consequências, riscos e POCs

- **Benefícios:** anonimato com coerência causal, histórias de investigação, reputação social contextual e não onisciência de NPCs.
- **Custos:** ACL e visibilidade por persona, mapeamento privado, provas de identidade, revisões, revogações, testes de vazamento e consentimento no co-op.
- **Riscos:** revelação acidental por prompts/logs/UI, correlação por nome, desvios de branch e exposição indevida em LAN; mitigados por fail-closed e testes previstos.
- **Evidência real:** somente a escolha de design aprovada; **56 testes candidatos não executados**. Sem POC de disfarce, mudança visual ou rename em BG2:EE/EEex multiplayer.

## Próxima DEC-077 — em aberto

**Investigação e contestação de vínculos secretos de identidade:** A) revelação por uma única pista; B) LLM decide livremente se a pista prova a ligação; **C (recomendada)**: fluxo investigativo por pistas com proveniência, evidências corroboradas/contraditórias, níveis de suspeita, contestação e gates de divulgação, sem condenação ou exposição automática.
