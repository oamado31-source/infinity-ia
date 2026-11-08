# ADR-0029 — Autonomia controlada com proteção especial do cânone

- **Decisão:** DEC-034 — política de eventos irreversíveis de alto impacto
- **Status:** **APROVADA — opção C**
- **Data:** 2026-11-06
- **Origem:** escolha explícita do idealizador nesta conversa.
- **Escopo:** Living World; canon de Forgotten Realms, facções, acontecimentos irreversíveis, intervenções dos jogadores.
- **Relações:** DEC-009, DEC-011, DEC-012, DEC-021/022, DEC-025/026, DEC-027, DEC-032/033, DEC-034, DEC-035.

## Contexto

O Living World combina acontecimentos canônicos, simulação autônoma, histórias paralelas e intervenções dos jogadores. Parte das consequências é local/reversível; outras transformam de forma permanente a cronologia da campanha. Uma facção simulada não pode matar automaticamente uma figura histórica central ou destruir uma cidade importante sem autorização, mas tampouco deve solicitar aprovação humana para cada patrulha, negociação ou mudança de influência local.

## Alternativas avaliadas

- **A — Aprovação manual de todo HIGH:** rejeitada como regra única por gerar interrupções; preserva-se aprovação explícita para classes de efeitos críticos.
- **B — Autorizações automáticas preconfiguradas sem proteção específica:** rejeitada como regra geral; risco de mudanças centrais indesejadas.
- **C — Autonomia controlada com proteção especial do cânone:** **aprovada**.

## Decisão

1. **Regra geral:** fatos e consequências de risco LOW/MEDIUM seguem os gates existentes da DEC-027/012. Mudanças importantes **reversíveis e limitadas** podem ser previamente autorizadas pelo anfitrião por **escopo específico de campanha**, condicionadas a limites e validação.
2. **Eventos centrais e irreversíveis:** mortes definitivas de personagens históricos relevantes, destruição de cidades canônicas, mudança duradoura de soberania, queda de reinos, guerras de impacto histórico e alterações centrais de arcos exigem **proteção especial**. Na ausência de política compatível e autorização explícita, o evento fica `PENDING/BLOCKED` (default-deny); **não** é convertido em fato do mundo por simulação, diálogo ou catch-up.
3. **Campanhas alternativas:** o anfitrião pode escolher deliberadamente políticas de divergência canônica **delimitadas por tipo de acontecimento, região, sujeitos e período**, registradas e versionadas. A opção de campanha alternativa **não é permissão genérica** para todo e qualquer regicídio, destruição ou alteração histórica.
4. **Agência dos jogadores:** proteger, investigar, apoiar ou participar de conspirações são escolhas legítimas. A escolha em si não força aprovação de toda consequência canônica; o sistema deve apresentar oportunidades e resultados compatíveis com os gates. Não obrigar um único caminho moral.
5. **Prevenção antes de irreversibilidade:** ações com possível resultado crítico devem preferencialmente passar por **pré-validação** e bloqueio/redirecionamento seguro *antes* da execução host. Se uma ação já aconteceu materialmente no BG2:EE, **não inventar rollback**: conservar evidências host, sinalizar conflito, suspender a promoção histórica e pedir resolução autorizada. Não apagar ou falsificar um resultado mecânico confirmado.
6. **Autoridade:** IA/facções propõem; classificador de risco por código, políticas e Action Gateway autorizam; host confirma mutações mecânicas; persistência registra apenas efeitos autorizados e confirmados. Nem texto do LLM nem percepção dos NPCs constituem prova de morte ou destruição.
7. **Impacto agregado:** várias operações isoladamente pequenas que, combinadas, alterem fatos históricos críticos devem ser reclassificadas como HIGH. Não dividir mudança crítica em eventos LOW/MEDIUM para contornar aprovação.
8. **Tempo e multiplayer:** sem progresso irreversível de evento HIGH durante período offline não autorizado; replay e reconexão não repetem autorizações nem efeitos. Políticas e manifestações de consentimento são vinculadas a campanha, versão, escopo, evento e estado.
9. **Canon e divergências:** cronologia oficial permanece baseline da DEC-009; divergências causadas por jogadores ou simulação autorizada têm causalidade, origem, checkpoint e linha histórica alternativa da campanha identificados. Mudanças no canon da campanha não alteram bases oficiais.
10. **Separação dos modos:** nada neste ADR modifica automaticamente o modo Original.

## Contrato de aprovação candidato (não é esquema implementado)

`event_id`, `campaign_id`, `world_time`, `affected_entities`, `canonical_significance`, `irreversibility`, `aggregate_impact`, `required_authority`, `allowed_scope`, `policy_id/version`, `consent_ref`, `preflight_state`, `host_receipt`, `idempotency_key`, `canonical_branch`, `decision_log`, `expiry`.

Um consentimento precisa referir o evento ou categoria explicitamente autorizada, estar válido no momento da ação e permanecer rastreável. Interfaces de autorização, papéis, prazos e política de emergência **não estão decididos**.

## Testes candidatos

1. Conspiração contra governante canônico → HIGH; sem consentimento, permanece pendente.
2. Escolha dos jogadores entre investigar, defender ou apoiar conspiração → três caminhos disponíveis, efeitos diferenciados mas validados.
3. Facção distante tenta concluir golpe durante FROZEN/offline → não aplica resultado HIGH.
4. Anfitrião pré-autoriza mudança limitada em posto secundário → pode avançar dentro do escopo.
5. Autorização de posto secundário não concede morte de governante/cidade destruída.
6. Um conjunto de ações MEDIUM conduz a mudança HIGH → escalonamento, sem bypass.
7. Host confirma algo inesperadamente irreversível → registrar evidência, suspender narrativa histórica, sem rollback fictício.
8. Falha de comunicação após execução → `UNCERTAIN` e reconciliação, sem retry duplo.
9. Reconexão multiplayer/save/load → uma única consequência com a mesma cadeia causal.
10. Linha de campanha alternativa → divergência versionada preserva fonte canônica intacta.
11. Nenhum efeito residual no modo Original.

## Consequências e lacunas

**Benefícios:** mundo autônomo sem decisões canônicas arbitrárias, agência moral do jogador, rastreabilidade e proteção de saves. **Custos:** classificador de impacto mais sofisticado, pré-validação de eventos, tratamento de falhas host e uma UI de autorização quando necessário.

**Pendências para SPECS:** papéis e UI de consentimento, política para ações diretas de jogadores sobre NPCs críticos, resolução de conflitos pós-host, graus de irreversibilidade e recuperação, limiares de impacto, tempo de retenção de logs. **Nenhum desses mecanismos foi implementado ou testado no jogo.**

## Decisão adicional associada

O adendo do idealizador aprova **alinhamento mutável por ações**, formalizado separadamente na **DEC-035 / ADR-0030**, para não confundir aprovação de acontecimentos com cálculo moral do personagem. Alinhamento não é reputação social (DEC-030).
