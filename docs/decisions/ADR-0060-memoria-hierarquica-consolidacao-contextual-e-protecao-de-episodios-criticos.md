# ADR-0060 — Memória hierárquica, consolidação contextual e proteção de experiências essenciais dos NPCs

- **Decisão:** DEC-065 — **opção C**, aprovada expressamente pelo idealizador do Infinity AI em 2026-11-06.
- **Status:** APROVADA como política de Discovery v6.1; **não implementada, não validada em jogo e sem benchmarks**.
- **Documento técnico:** `docs/65-memoria-hierarquica-consolidacao-retencao-e-recuperacao-contextual-npc.md`.
- **Preservação integral:** DEC-060 (ADR-0055: cânone em **diretórios físicos separados por ano DR**), DEC-061 (ADR-0056: proveniência/conflitos curatoriais), DEC-062 (ADR-0057: ingestão/curadoria controladas), DEC-063 (ADR-0058: Knowledge Pack pinado à campanha), DEC-064 (ADR-0059: aquisição legítima, memória episódica e revisão de crenças sem retcon).

## Contexto

A campanha pode durar anos dentro do relógio de Forgotten Realms. NPCs acumulam conversas, testemunhos, dívidas, promessas, lembranças privadas e crenças contraditórias. Enviar toda a história ao modelo em cada diálogo é incompatível com metas de desempenho e controles de acesso; descartar automaticamente lembranças antigas ou pouco acessadas quebraria a causalidade e a narrativa persistente. **A memória subjetiva do NPC não é o cânone, não equivale ao estado confirmado pelo host e não concede acesso irrestrito a segredos.**

## Alternativas consideradas

- **A — Memória integral sempre disponível no contexto:** rejeitada como política de recuperação; não se exige que todo episódio seja incluído num prompt ou lido integralmente por chamada.
- **B — Esquecimento automático pelo tempo decorrido:** rejeitada; um acontecimento fundador de uma relação pode ser antigo e essencial.
- **C — Memória hierárquica, consolidação contextual e proteção de experiências essenciais:** **APROVADA**.

## Decisão vinculante

1. **Quatro níveis conceituais:** (i) memória imediata/de trabalho, derivada e limitada por orçamento; (ii) memórias episódicas contextualizadas, com origem, tempo e relações; (iii) memória consolidada/semântica de conhecimentos, relações, convicções e generalizações, sempre com vínculos às evidências; (iv) âncoras críticas protegidas, com compromissos, segredos, acontecimentos fundadores e consequências relevantes. Níveis são **projeções e classificações**, não quatro verdades independentes.
2. **Causalidade e proveniência:** cada síntese deve referenciar episódios/fontes reais e a revisão de crença DEC-064. Nunca promover uma inferência LLM a episódio testemunhado, fato do cânone ou ação do motor. Divergências e incertezas permanecem explícitas.
3. **Consolidação não destrutiva por padrão:** resumos são materializações derivadas e reconstruíveis; reduzir recuperação, granularidade de índice ou prioridade não equivale a excluir dados de origem. Não há expiração de eventos, prazos, pesos, top-k ou algoritmos estabelecidos nesta fase.
4. **Memórias críticas protegidas:** sinais de proteção (ex.: promessa, segredo, salvamento, trauma narrativo, ruptura, morte e legado, fatos de quests confirmadas) são candidatos verificados com fonte, motivo, ACL, prazo/política e revisão; simples texto de LLM não cria imutabilidade eterna. Nenhum processo de otimização descarta âncoras ou vínculos necessários sem avaliação/autorização apropriada.
5. **Recuperação episódica sob demanda:** considerar NPC/identidade, campanha e branch, tempo DR confirmado, contexto da cena, relações, saliência, acessibilidade temporal e social, ACL/classificação de segredos, revisão do Knowledge Pack, limites de latência e orçamento. Validar autorizações **antes** de buscas em índice, resumos ou prompts. Proteção não significa revelação automática.
6. **Validade e revisões:** sínteses carregam `source_event_ids`/hashes, revisão de projeção, contexto de permissão e versão; em eventos, correções, migração de Knowledge Pack, revogação ou mudança de branch, invalidar ou reconstruir projeções dependentes. Saída stale/duplicada falha fechada.
7. **Eventos críticos do host:** estados e efeitos mecânicos continuam sujeitos a confirmações DEC-011/012; `UNCERTAIN` nunca é transformado em lembrança de fato confirmado. Resumos não reescrevem saves, história da campanha ou diálogos anteriores.
8. **Escopo físico:** lore de Forgotten Realms permanece fisicamente em `knowledge/periods/<ano>-DR/...`; memórias privadas dos NPCs residem no estado de campanha/ramo, **não** são copiadas para o diretório anual nem se tornam biblioteca global de cânone. Um Knowledge Pack é manifesto de referências anuais, não um corpus mesclado.
9. **Privacidade, retenção e direitos:** separar política de recuperação e política de eliminação. Requisições legítimas de supressão/retificação, expiração autorizada, cópias/backups e consentimento serão especificadas com obrigações legais/operacionais; o caráter auditável do log não autoriza retenção ilegal ou exposição de conteúdo privado. Quando possível, manter referência auditável minimizada/redigida, sem preservar o segredo.
10. **Sobrecarga e execução:** priorizar gameplay, multiplayer, interações urgentes e eventos confirmados. Executar consolidação em lotes e segundo DEC-021/022/056, sem LLM por NPC/tick; falha de workers ou LLM causa atraso/uso de material confiável disponível, **não** esquecimento arbitrário.

## Consequências e limites

- **Benefícios:** continuidade de relacionamentos, lembranças relevantes, manutenção de promessas e segredos, resposta contextual sem recuperar o histórico integral, custo mais controlável.
- **Custos:** índices por NPC/ramo, dependências auditáveis de sínteses, invalidação de caches, orçamento e retenção, classificação de proteção e análise de privacidade.
- **Riscos:** resumo alucinado, segredo exfiltrado por busca, lembrança crítica eliminada, duplicidade/stale em workers LAN, associação de memória a NPC errado, inconsistência de snapshots e degradação por excesso de âncoras. Mitigar por gates e testes candidatos.
- **Não comprova:** qualquer suporte de EEex a observação/identidade de todos os NPCs, métricas de contexto, qualidade de síntese, latência, limites de armazenamento, protocolos LAN ou capacidade de restore in-game. Tudo continua SPECS/POCs.

## Evidências e verificação

- **Evidência da decisão:** escolha do idealizador para DEC-065/C neste diálogo, 2026-11-06.
- **Testes candidatos:** `T065-01`–`T065-32` no documento técnico 65; **nenhum executado**.
- **Compatibilidade:** DEC-028/029, DEC-039/049, DEC-052/053/054/055, DEC-056/057/058/059/060/064 e DEC-008/009/011/012. DEC-006/007/013/015/017/018 continuam abertas.

## Próxima decisão

**DEC-066 — identidade persistente e reconhecimento seguro de NPCs ao longo de saves, regiões e mudanças de build.** A continuidade de memória depende de vincular episódios ao mesmo NPC sem associar registros indevidamente a entidades distintas; não presumir que nome ou identificador temporário do motor é globalmente estável. Opções: A — identificador bruto do motor; B — correspondência heurística por nome/área; C — identidade lógica estável por campanha + correspondência verificada com bloqueio em ambiguidades.
