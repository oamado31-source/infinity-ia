# ADR-0004 — Versionamento e revisão de históricos de personagens

- **DEC associada:** DEC-020
- **Estado:** **APROVADA — opção C (histórico versionado e editável)**
- **Data de aprovação:** 2026-11-06
- **Domínio:** identidade do personagem, narrativa persistente, cronologia, reconciliação e autoria
- **Fundamentação:** escolha explícita do idealizador registrada em conversa; amplia ADR-0002 e ADR-0003.
- **Âmbito:** modo Living World; o modo Original permanece isolado pela DEC-004.

## Contexto

O jogador poderá complementar ou reinterpretar o passado de seu personagem depois que a campanha começou. Entretanto, ganchos, missões, conhecimento de NPCs e eventos compartilhados podem já ter sido produzidos com base nas informações antigas. Sobrescrever o histórico sem preservar as dependências cria contradições e pode apagar indevidamente ações de outros jogadores.

**Exemplo:** o personagem é perseguido porque foi acusado de traição em Cormyr. Após dez sessões, o autor acrescenta que na verdade era um espião infiltrado. O novo passado pode explicar as perseguições — mas não autoriza apagar perseguições que ocorreram ou reescrever a memória dos demais personagens sem decisão explícita.

## Decisão aprovada

Adotar **opção C: histórico versionado e editável**, sujeito aos seguintes princípios vinculantes:

1. **Autoria e editabilidade.** O jogador pode propor revisões ou adições ao histórico do personagem de sua autoria. Nenhuma revisão substitui silenciosamente versões anteriores.
2. **Versionamento auditável.** Cada revisão mantém identificador, autor, data, referência à versão anterior, mudanças propostas e classificação de visibilidade. A granularidade e o armazenamento definitivo serão especificados posteriormente.
3. **Análise antes da ativação.** Antes de uma revisão afetar a narrativa, o sistema identifica inconsistências potenciais com fatos de mundo, acontecimentos confirmados, memória/conhecimento de NPCs, lore, cronologia e missões/ganchos derivados.
4. **Sugestões, não decisões automáticas.** A IA poderá sugerir uma reconciliação (nova revelação, fato adicional, reinterpretação, desativação de futuro gancho etc.). O usuário deverá ter meios de revisar as implicações e decidir se aceita a proposta.
5. **Fatos confirmados preservados por padrão.** Uma edição de histórico **não** altera retroativamente acontecimentos, recompensas, transações, mortes, revelações ou outras consequências já confirmadas no mundo. Alterações retroativas (retcons) requerem **aprovação explícita**, em fluxo próprio, com escopo e impacto apresentados.
6. **Isolamento do estado compartilhado.** Mudanças que afetem a experiência ou a história de outros jogadores não serão aplicadas silenciosamente. A regra de consentimento/autoridade e quem deve aprovar alterações de estado compartilhado ainda serão definidos em DEC-008, DEC-009 e DEC-011; até lá, não há retcon automático do estado compartilhado.
7. **Coerência do conhecimento.** Revisar um fato não remove automaticamente uma informação já descoberta por um NPC ou outro personagem. O sistema deve representar a diferença entre *o que foi dito ou acreditado*, *o que realmente aconteceu* e *o que é conhecido*. Ver ADR-0003.
8. **Rastreabilidade dos ganchos.** Ganchos e eventos candidatos vinculam-se às revisões e fatos que os originaram. Após uma mudança aprovada, propostas ainda não executadas devem ser revalidadas; as que ficaram inválidas não poderão ser aplicadas automaticamente.
9. **Recuperação e segurança.** Deve existir histórico consultável e mecanismo de restauração/reconciliação de revisões sem alterar indiscriminadamente o estado autoritativo. Texto de histórico é dado não confiável, não instrução de execução para IA/bridge.
10. **Limites de escopo.** Não alterar saves do modo Original. A compatibilidade da experiência com o multiplayer real de BG2:EE continuará sujeita a prova de conceito.

## Fluxo de aprovação — comportamento de produto, não implementação

```text
Histórico ativo (rev N)
      ↓
Jogador propõe nova redação (rascunho rev N+1)
      ↓
Análise de diferenças, dependências e conflitos
      ↓
IA sugere reconciliações / impactos e alternativas
      ↓
Revisão e aprovação explícita da proposta
      ├── Sem retcon global: ativar versão, revalidar ganchos futuros
      └── Com retcon: aprovação adicional e controle de impacto no estado compartilhado
      ↓
Novo histórico ativo + registro de decisões e consequências
```

**Importante:** a transição de versões sem conflitos depende da aprovação do autor; requisitos de aprovação para efeitos compartilhados permanecem pendentes. Enquanto não houver contrato de autoridade, alterações que exijam retcon de fatos confirmados ficam bloqueadas.

## Modelo conceitual candidato — não constitui contrato de dados aprovado

```text
Character (character_id, campaign_id, owner_player_id)
 ├─ BackstoryRevision (revision_id, parent_revision_id, author, timestamp, status)
 │   └─ BackstoryFact (fact_id, revision_id, assertion, visibility, validity_status)
 ├─ RevisionDiff / ConflictReport
 ├─ ReconciliationProposal (proposal_id, affected_facts, affected_events, approval_status)
 └─ NarrativeHook (hook_id, originating_fact_ids, originating_revision_id, lifecycle_status)

WorldEvent (event_id, authoritative_status, occurred_at)  # preservado
KnowledgeEvent (knower_id, source_event_id, known_as_of)  # preservado ou reconciliado explicitamente
```

Status possíveis da revisão e estados de ganchos são **propostas** para o desenho técnico; nomes/campos exatos, event sourcing versus snapshots, e mecanismo de migração não foram decididos.

## Cenários de aceitação candidatos (a transformar em SPECS)

| ID | Cenário | Resultado esperado |
|---|---|---|
| CAND-REV-001 | Autor complementa o histórico com um novo parentesco | Existe nova revisão rastreável, e a anterior permanece recuperável |
| CAND-REV-002 | Autor retira acusação que já originou perseguição no jogo | Sistema sinaliza conflitos; perseguição confirmada continua registrada até reconciliação aprovada |
| CAND-REV-003 | IA sugere que a acusação era uma armação | Jogador visualiza implicações e aprova/rejeita; IA não aplica a versão automaticamente |
| CAND-REV-004 | Revisão invalida encontro ainda não executado | Gancho é reavaliado ou bloqueado; não gera um evento contraditório |
| CAND-REV-005 | Outro jogador ouviu uma confissão antes da revisão | Sua memória/registro não é apagado automaticamente; distingue o que ouviu do fato revisado |
| CAND-REV-006 | Revisão contém partes secretas | Diff, notificações e logs visíveis respeitam a política híbrida da DEC-019 |
| CAND-REV-007 | Revisão depende de retcon de recompensa, morte ou missão compartilhada | Sistema impede aplicação silenciosa; exige aprovação explícita por política ainda a definir |
| CAND-REV-008 | Sessão é encerrada e aberta novamente | Histórico ativo, revisões, decisões e fatos confirmados permanecem coerentes, sem duplicação de eventos |
| CAND-REV-009 | Falha de IA durante reconciliação | Revisão não é aplicada parcialmente; estado confirmado permanece consistente |
| CAND-REV-010 | Edição tenta instruir agente a executar Lua ou expor segredos | Texto é tratado como dado; nenhuma permissão ou comando é alterado |

## Consequências arquiteturais

- Necessitamos **separar os registros de autoria** (históricos/versões), **interpretações narrativas** (ganchos e hipóteses) e **fatos de mundo confirmados** (eventos autoritativos).
- Introduzir relações de proveniência entre fatos de backstory, ganchos, propostas, consequências e conhecimento de NPCs.
- Mudanças terão análise de impacto, validação e aprovação explícita para alterações confirmadas; reindexação de memória/consultas deve respeitar revisões ativas e conhecimento pré-existente.
- Os testes deverão cobrir concorrência de multiplayer, vazamentos de segredos, falhas parciais de IA e recuperação após reinício.
- Critérios de aprovação para eventos compartilhados, políticas de retenção/exclusão, snapshots e rollback operacional **não estão aprovados** nesta decisão.

## Alternativas rejeitadas

- **A — histórico imutável:** inviabiliza expansão criativa do personagem após a criação.
- **B — edição livre com adaptação retroativa automática:** arrisca apagar consequências, quebrar a continuidade e afetar outros jogadores sem aprovação.

## Relações e pendências

- DEC-001/ADR-0001 — coop privado inicialmente, mas sem assumir isolamento definitivo.
- DEC-004/ADR-0002 — histórico como motor da narrativa no Living World e modos separados.
- DEC-019/ADR-0003 — visibilidade híbrida e conhecimento diegético.
- DEC-008/DEC-009 — persistência, verdade do mundo, canon e cronologia.
- DEC-011 — autoridade da sessão e aprovação de eventos que alterem outros jogadores.
- DEC-012 — isolamento, registros de alterações e controles de segurança.
- DEC-014/DEC-015 — comportamento de NPCs e critérios de testes.

**Próxima discussão sugerida:** DEC-002 — ambiente de execução, desenvolvimento e compatibilidade prioritária para o primeiro protótipo.
