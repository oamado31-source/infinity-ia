# Metodologia de desenvolvimento orientado a especificações

**Versão:** 0.1 (proposta)  
**Fundamentos pesquisados:** GitHub Spec Kit, OpenSpec e convenção EARS utilizada em Kiro.

## Princípios

- A **SPEC descreve o comportamento observável** (o que e por que), não a implementação interna.
- A **arquitetura/desenho** determina como realizar o comportamento e qual tecnologia usar.
- Cada **tarefa** deve mapear a requisitos e possuir evidências de conclusão.
- Todo comportamento novo deve ter **cenários verificáveis**, incluindo falhas e estados degradados.
- Arquitetura e features devem respeitar uma **constituição** compartilhada.
- As mudanças devem preservar rastreabilidade: decisão → requisito → plano → tarefa → teste → evidência.

## Ciclo proposto

0. Discovery: visão, perguntas, restrições, evidências e ADRs.
1. Constitution: princípios obrigatórios aprovados.
2. Specify: `spec.md` por feature, com requisitos identificados e critérios de aceitação.
3. Clarify: análise de ambiguidades e hipóteses não confirmadas.
4. Plan: `plan.md` com desenho, contratos, dependências, dados, riscos e testes.
5. Tasks: `tasks.md` pequena, ordenada e rastreável.
6. Analyze: confronto entre todos os artefatos antes do código.
7. Implement: código por tarefas, com revisão e validação.
8. Converge: provas de que o comportamento observado atende à SPEC; registrar desvios.

## Estrutura de repositório futura (proposta, ainda não gerada)

```text
infinity-ai/
├── README.md
├── constitution.md
├── docs/
│   ├── vision.md
│   ├── roadmap.md
│   ├── research/
│   ├── architecture/
│   ├── decisions/ADR-0001-*.md
│   ├── risk-register.md
│   └── compatibility-matrix.md
├── specs/
│   ├── 001-game-bridge/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   └── tests.md
│   ├── 002-world-state/
│   ├── 003-ai-npc-dialogue/
│   ├── 004-dynamic-events/
│   ├── 005-multiplayer-sync/
│   └── 006-content-catalog/
├── src/             # somente após as SPECS aprovadas
└── tests/           # somente após as SPECS aprovadas
```

## Exemplo de requisito testável (provisório)

**REQ-NPC-001 — Recordação consistente**

> QUANDO o mesmo personagem jogador voltar a conversar com um NPC, o sistema DEVERÁ recuperar fatos relevantes das interações anteriores que estejam registrados como conhecidos pelo NPC, sem atribuir-lhe conhecimento de eventos não observados nem compartilhados.

**Cenários de aceitação:**
- Conversa inicial salva um fato; após reinício, o fato pode ser recuperado.
- Dois jogadores com relações diferentes com o NPC não têm memórias pessoais confundidas.
- Falha no provedor de IA não causa alterações inválidas no estado do jogo.

## Gates de qualidade

- **G0 / Discovery:** decisões essenciais aprovadas, riscos e provas de conceito previstos.
- **G1 / Spec:** requisitos completos, sem ambiguidades materiais e com critérios testáveis.
- **G2 / Design:** contratos, segurança e estratégia de fallback revisados.
- **G3 / Tarefas:** dependências claras, tarefas pequenas e rastreadas.
- **G4 / Execução:** testes automatizados e evidências de integração, incluindo multiplayer.
- **G5 / Convergência:** demonstrar que implementação e documentação correspondem.

## Gestão de mudanças

Em caso de mudança relevante, abrir proposta de mudança, registrar impacto em requisitos, decisões e testes, atualizar a SPEC e só depois mudar código. Para dependências externas, registrar versão/hash e ordem de instalação, com procedimento de reversão.

## Fontes

- https://github.github.com/spec-kit/quickstart.html
- https://github.github.com/spec-kit/reference/agentic-sdd.html
- https://openspec.dev/docs/schemas/spec-driven
- https://kiro.dev/docs/specs/feature-specs/

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Na passagem Discovery→SPECS, DEC-072 exige schemas de catálogo, fixtures, evidências de capability por build e gates de segurança antes de implementar um adapter; 48 testes candidatos ainda pendentes.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

As SPECS futuras deverão comprovar origem, acesso epistêmico, cadeia de retransmissão, família de evidências, ACL, riscos e critérios verificáveis; T089 permanecem cenários candidatos.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Dossiê, ACL, views e entregas são contratos candidatos que exigem SPECS, fixtures de sigilo/contradições e POCs read-only antes de afirmar funcionalidades da engine. Preservar decisões como ADRs imutáveis.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

No SDD, decompor DEC-091 em validação de proposta, evidência, consentimento, reserva, dispatch, receipt e auditoria antes de qualquer SPEC/POC.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

SDD deve transformar DEC-092/C em SPEC executável somente após fixture determinística, matriz de gates e POC host+2 clientes para comandos mecânicos.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C exige prova testável por build, snapshots/epochs, CAS e propostas sem escrita; casos T102 continuam não executados. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para método SDD e gates de validação do código determinístico, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para descoberta SDD, testes e gates de implementação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Rastreabilidade de decisão, testes sintéticos e critérios de aceite sem equiparar propostas a implementação. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Matriz de testes distingue laboratório sintético de POC real de host. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Handoff SDD — questionário único pós-DEC-110 (Discovery v10.6)

O questionário `docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md` agrupa **12 perguntas P0 + 16 P1**; recomendações não contam como respostas. `docs/112-plano-de-transicao-discovery-specs-e-primeiro-ciclo-executavel.md` propõe Constitution, SPEC-001 bridge read-only, SPEC-002 authority multiplayer e SPEC-003 estado/memória; gates de prova antes de claims de integração. ADR-0105 vincula escrow a capabilities reais; até lá é somente promessa/proposta narrativa. A DEC-111 de governança SDD ainda está aberta.
