# ADR-0059 — Memória persistente e revisão contextual de crenças individuais dos NPCs

- **Decisão:** **DEC-064, opção C**, aprovada expressamente pelo idealizador do Infinity AI em 2026-11-06.
- **Estado:** **APROVADA como política de Discovery; ainda NÃO implementada, testada ou validada no BG2:EE/EEex**.
- **Discovery:** v6.0; documento complementar `docs/64-memoria-crencas-aprendizado-e-correcao-contextual-de-npcs.md`.
- **Precedência preservada sem alterações:** DEC-060 (ADR-0055, **base canônica fisicamente segregada por ano DR**, recuperação com vigência/ACL e overlays); DEC-061 (ADR-0056, alegações com fontes, conflitos e curadoria); DEC-062 (ADR-0057, ingestão em staging e publicação curada); DEC-063 (ADR-0058, *Knowledge Packs* versionados e pinados por campanha, sem atualização automática).
- **Integrações:** DEC-008/009/011/012/019/020/021/022/028/029/030/031/035/036/037/039/041/047/048/049/052/053/054/055/056/059 e política de validação de saída da DEC-060. DEC-006/007/013/015/017/018 permanecem abertas.

## Contexto e alternativas

O conhecimento canônico curado e a experiência subjetiva de um NPC são camadas diferentes. Uma correção de fonte de 1369 DR pode demonstrar que um boato era falso, mas não significa que todos os NPCs ouviram essa correção. Da mesma forma, a lembrança de uma declaração errada ou a crença passada de um NPC não pode desaparecer retroativamente. O mundo precisa permitir aprendizado, dúvidas, convicções persistentes e retificações sem onisciência e sem sobrescrever a história confirmada.

- **A — Substituir automaticamente crenças ao atualizar o cânone:** rejeitada; dá onisciência, quebra causalidade e pode vazar segredos.
- **B — Memórias e crenças imutáveis para sempre:** rejeitada como política total; impede evolução por nova evidência e relações sociais.
- **C — Memória persistente com aprendizado e correção por evidência/contexto legítimos:** **APROVADA**.

## Decisão vinculante

1. **Separação epistêmica obrigatória:** distinguir (a) `CANON_CLAIM` curado na partição do **ano DR** apropriado; (b) `CAMPAIGN_FACT`/evento confirmado no ramo pelo host/orquestrador autorizado; (c) `OBSERVATION`/testemunho, (d) `REPORT`/rumor recebido, (e) `BELIEF` e seu estado subjetivo, (f) `MEMORY` de aquisição e interpretação, e (g) `REPUTATION`/atitude contextual. Nenhuma dessas categorias se converte automaticamente em outra.
2. **Conhecimento adquirido legitimamente:** NPC somente adquire nova informação por observação possível, conversa/testemunho, carta/documento acessível, investigação, rumor via rede social, revelação consentida ou evento narrativo comprovado na janela temporal apropriada. O filtro DEC-028 e as regras de transmissão DEC-029 operam **antes** de qualquer contexto LLM; IA não cria artificialmente encontro, viagem, fonte ou autorização.
3. **Atualização de *Knowledge Pack* não atualiza mentes:** DEC-063 publica/adota uma revisão de referências anuais para uma campanha, mas não injeta automaticamente as correções em NPCs, organizações ou personagens. A revisão pode gerar **candidatos a oportunidades legítimas de descoberta**; nunca autoescrever lembranças nem retroagir diálogos.
4. **Memória imutável da ocorrência, crença versionada:** persistir os episódios de aquisição (`quem informou`, `o quê`, `onde`, `quando DR`, `qual canal`, `fonte e revisão`, `permissão`, `evento/observação comprovado`) e, separadamente, estados de crença que podem evoluir. Corrigir crença produz **transição auditável**, não edição/desaparecimento da memória passada ou da fala proferida.
5. **Avaliação contextual da evidência:** regras e dados de proveniência ponderam observação direta, confiabilidade da fonte, qualidade documental, relações sociais, interesse do NPC, experiências anteriores, conflito de alegações e posição temporal. Pode haver `ACCEPTED`, `DOUBTFUL`, `REJECTED`, `SUSPENDED` ou `INVESTIGATING` como estados **candidatos**, sem percentuais mágicos nem confiança numérica fixada em Discovery. Modelo LLM pode propor interpretação verbal, mas não decide factualidade/ACL nem escreve diretamente estado persistente.
6. **Crenças falsas e rumores são possíveis:** NPC pode continuar crendo num boato falso sem torná-lo `CANON_CLAIM`; pode descobrir prova e mudar gradualmente ou resistir. A falsidade de uma crença não significa uma falha de validação de diálogo quando está corretamente enquadrada como perspectiva subjetiva, com origem e limites; não apresentar rumor como certeza onisciente do narrador.
7. **Aprendizado e correção não homogêneos:** NPCs podem interpretar a mesma evidência de modos diferentes de acordo com memória, relação, papel social e acesso legítimo. O sistema não exige revisão por segundo LLM em cada interação, não executa LLM a cada tick/NPC e respeita Resource & Performance Director (DEC-056).
8. **Preservar continuidade e causalidade:** a versão anterior de crença, o episódio de aquisição, diálogos e decisões já confirmadas permanecem no histórico daquele ramo. A atualização de uma crença **não desfaz** missão, morte, relacionamento, alinhamento, reputação ou evento mecânico confirmado. Consequências comportamentais são propostas narrativas avaliadas pelos gates correspondentes e Action Gateway/host quando houver efeito mecânico.
9. **Vinculação temporal e por campanha:** `campaign_id`, `branch_id`, `world_time_DR`, `knowledge_pack_revision`, `npc_identity`, ACL e revisão da memória definem a projeção. Nenhuma correção cruzará campanha, ramo ou ano por busca global; consultar o diretório físico anual do momento confirmado, antecedentes somente se houver continuidade/proveniência e autorização, futuro nunca como fato já consumado. Memória NPC é um **overlay específico de campanha/ramo**, não lore canônico armazenado na pasta física anual.
10. **Privacidade e consentimento:** visibilidade do histórico do jogador DEC-019 não equivale a conhecimento de NPC. Uma fonte pública da enciclopédia não concede ao NPC um segredo pessoal ou um fato inacessível. Mudanças em ACL invalidam caches/prompts e bloqueiam mensagens não autorizadas. Workers LAN recebem apenas projeções autorizadas e mínimas; logs não devem registrar histórias privadas em claro.
11. **Coerência de persistência:** cada aquisição/correção usa IDs de evento e chave idempotente, ordenação causal, branch/revisão, política de catch-up limitada e vínculo com checkpoint da campanha. Resposta LLM tardia, evidência de revisão obsoleta ou transferência duplicada não é reaplicada. Divergência `UNCERTAIN` em fato/host/gateway não pode ser convertida em memória confirmada.
12. **Falha segura:** ausência de evidência, fonte não curada, canal impossível, desconhecimento de ACL, partição histórica indisponível, conflito não resolvido ou identidade incerta leva a `DEFER`/`INVESTIGATE`/`REJECT`, nunca suposição de aquisição/correção. É permitido expressar dúvida diegética sem criar fato canônico.
13. **Alterações narrativas de segundo grau:** pedidos de desculpas, reconciliação, indignação, mudança de lealdade, abertura de missão e suspeita de manipulação podem ser propostos a partir da revisão de crenças; respeitar autonomia, consentimento PvP, reputação contextual, níveis de risco e autoridade mecânica de decisões anteriores. Nenhuma mudança automática de alinhamento ou reputação simplesmente por retificação editorial.
14. **Limite explícito de escopo:** política de **quando e por que** crenças mudam. Compressão de memória, retenção episódica, esquecimento e esquemas de resumos de longa duração são matéria da **DEC-065**, ainda aberta. Não definir modelo LLM, thresholds de persuasão, taxas de esquecimento, mecanismos de busca ou APIs nesta decisão.

## Máquina conceitual de revisão de crenças (não implementada)

`RECEIVED_EVIDENCE → VERIFY_TIME_SOURCE_ACL → CONTEXTUAL_ASSESSMENT → {DISCARD, HOLD_UNCERTAIN, INVESTIGATE, ACCEPT, REJECT} → APPEND_BELIEF_REVISION → VALIDATE_OUTPUT/CONSEQUENCES`.

`APPEND_BELIEF_REVISION` só ocorre após passagem pelos contratos de integridade, domínio e autorização da campanha. Isso não equivale a emitir uma ação mecânica no BG2:EE.

## Consequências, tradeoffs e riscos

- **Benefícios:** NPCs capazes de aprender sem onisciência, memórias causais, rumores verossímeis, consequências narrativas rastreáveis e bases canônicas curadas sem retcon subjetivo automático.
- **Custos:** maior estado persistente por NPC, projeções subjetivas, gestão de evidências, fontes e ACL, testes de causalidade e estratégias futuras de compactação para não explodir custo.
- **Riscos:** crença subjetiva tratada como fato, segredo vazado em prompt, falso testemunho fabricado pela IA, memória sobrescrita, mudanças retroativas de reputação, difusão instantânea sem canal ou repetição de atualizações stale.
- **Sem comprovação:** não existem ainda runtime de memória NPC, testes de BG2:EE/EEex, garantias de observabilidade de diálogos, instalação/mods, multiplayer ou integração mecânica. O desenho será especificado e validado em SPECS/POCs.

## Verificação candidata

Ver `docs/64-memoria-crencas-aprendizado-e-correcao-contextual-de-npcs.md` para contratos preliminares e testes **T064-01 a T064-30**, não executados. Nenhum benchmark ou integração real foi confirmado.

## Próxima decisão

**DEC-065:** como preservar, sintetizar e eventualmente esquecer experiências individuais ao longo de anos sem perder fatos, segredos ou consequências narrativas críticas; alternativas entre memória integral sem limites, expiração simples e memória hierárquica por importância com proteção de eventos essenciais. Não confundir essa escolha com a decisão já aprovada de revisão contextual da crença.
