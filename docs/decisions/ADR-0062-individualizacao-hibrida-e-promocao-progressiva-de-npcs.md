# ADR-0062 — Individualização híbrida e promoção progressiva de NPCs

- **Decisão:** DEC-067 — **opção C**, aprovada expressamente pelo idealizador em 2026-11-06.
- **Status:** APROVADA como arquitetura de Discovery **v6.3**; NÃO IMPLEMENTADA, SEM POCs BG2:EE/EEex nem testes multiplayer executados.
- **Documento técnico:** `docs/67-individualizacao-progressiva-promocao-e-persistencia-seletiva-de-npcs.md`.
- **Preservação integral:** DEC-060 a DEC-066 e ADR-0055 a ADR-0061 continuam vinculantes e não foram modificados.

## Contexto

O Living World precisa permitir relações duradouras com um guarda ou comerciante comum sem simular cada habitante, spawn ou figurante com memória, LLM e agenda individual a todo momento. O BG2:EE e seus scripts podem recriar NPCs genéricos, reutilizar referências, gerar homônimos ou apresentar duplicatas. A importância narrativa é dinâmica: uma pessoa inicialmente secundária pode se tornar personagem central por escolhas dos jogadores. Não existem POCs comprovando IDs estáveis nem controle genérico de NPCs na engine.

## Opções consideradas

- **A — Individualização universal:** rejeitada como padrão, pelo custo potencial não limitado e por atribuição indevida de identidade em spawns genéricos.
- **B — Somente NPCs únicos/curados:** rejeitada como regra exclusiva; impede que personagens emergentes criem história duradoura.
- **C — Individualização híbrida e progressiva:** **APROVADA**; priorizar únicos/companheiros curados, representar figurantes inicialmente de forma agregada ou efêmera e promover candidatos com evidências, relevância e orçamento.

## Decisão vinculante

1. **Níveis distintos de representação:** NPCs únicos/companheiros e demais atores curados terão prioridade para identidade individual, observadas as limitações da engine. População de fundo pode ser representada por agregados regionais e agentes efêmeros; *nenhuma interação efêmera implica automaticamente uma pessoa persistente*.
2. **Promoção por significado causal verificável:** interações recorrentes, promessa, testemunho, missão, vínculo social, resgate, traição ou consequência confirmada podem tornar um ator candidato. Saliência não é classificada somente pela frequência ou pelo texto de LLM.
3. **Gate de identidade DEC-066:** criação/ativação de vínculo de memória pessoal exige evidência positiva suficiente de que aquele ator é indivíduo distinguível no escopo da campanha/ramo. `CANDIDATE`, `AMBIGUOUS`, `STALE`, `UNCERTAIN`, homônimos e IDs reciclados não autorizam vinculação nem herança de memória. Se o motor não permitir distinção confiável, manter candidato pendente ou interação genérica; não inventar rastreabilidade.
4. **Promoção atômica lógica e idempotente:** registrar evidência de evento confirmado, política autorizadora, `NPCIdentity` e vínculo `EngineObservation` verificado, revisão/época/checkpoint, quando aplicável. Evitar que o mesmo NPC seja promovido duas vezes e que sua representação apareça simultaneamente no agregado e no individual com efeitos duplicados.
5. **História sem retroinvenção:** persistir somente experiências demonstradas e legitimamente adquiridas; não criar passado, segredos, origem, profissão, relações ou poderes ausentes apenas para completar a biografia. Histórias derivadas podem ser propostas, jamais convertidas em fatos sem validação DEC-060 e autorização aplicável.
6. **Memória e relação por campanha:** episódios e crenças de indivíduos promovidos seguem DEC-064/065: níveis hierárquicos, eventos de aquisição, proveniência, revisões, ACL, proteção de âncoras críticas; dados pessoais não são publicados no cânone. O NPC não conhece fatos de um Knowledge Pack por simples promoção.
7. **Autonomia graduada por prioridade:** a promoção habilita persistência lógica e elegibilidade para agenda/objetivos, mas NÃO obriga LLM contínuo, pathfinding por tick, spawning ou materialização mecânica. A execução acompanha DEC-021/022 e o Resource Director DEC-056: ACTIVE/NEAR mais detalhado, DISTANT em lotes, DORMANT sob demanda. Os limites numéricos aguardam SPECS/benchmarks.
8. **Risco e autoridade:** conteúdo de baixo risco pode ser proposto por regras e aplicado somente se política expressa e evidência verificável permitirem; impactos em quests, vida/morte, romance, controle, facções, eventos canônicos ou efeitos mecânicos seguem DEC-011/012/027/034/041/050 e exigem gates/receipts do host. `UNCERTAIN` não equivale a confirmação.
9. **Permanência e hibernação:** ausência de jogador, saída da área ou queda de relevância não extinguem identidade e memórias críticas. Arquivamento/reativação e limites de retenção serão definidos separadamente, sem descarte automático de fatos, direitos ou compromissos. A política detalhada para NPC promovido fora de cena é objeto da DEC-068.
10. **Isolamento e direito de acesso:** Original Mode, outras campanhas, branches divergentes ou nós LAN não autorizados não compartilham identidades/memórias; conhecimento/ACL filtrados antes de contexto LLM, incluindo filtros sobre memórias de jogadores. Spawn genérico não é automaticamente o mesmo indivíduo após save/load.
11. **Precedência de DEC-060–066:** manter diretórios canônicos físicos `knowledge/periods/<ano>-DR/` (DEC-060), proveniência/curadoria (061), staging e publicação validada (062), packs fixados por campanha (063), aquisição epistêmica legítima (064), consolidação protegida (065) e correspondência de identidade comprovada (066). Novas identidades vivem no overlay de campanha/ramo, não na árvore canônica anual.
12. **Sem promessas técnicas:** capacidade de observar spawns, preservar identidades genéricas, alterar scripts ou controlar NPCs fora do grupo é hipótese para SPECS/POCs; não é funcionalidade demonstrada da Infinity Engine/EEex.

## Consequências e riscos

- **Benefícios:** histórias emergentes com habitantes comuns; limites computacionais; pessoalidade sem confundir NPCs homônimos; continuidade com saves e escolhas.
- **Trade-offs:** gerenciamento de candidato, individualização e agregado; curadoria de gatilhos e quotas; manutenção de índices e auditorias de duplicidade; necessidade de evidência de identidade na engine.
- **Falha segura:** se identidade/continuidade não for demonstrável, oferecer interação genérica aprovada e reter o candidato para análise, não atribuir segredos ou memórias privadas a um ator semelhante.
- **Não implica:** geração automática de novos CREs, instâncias permanentes dentro do motor, mudanças mecânicas de companion, disponibilidade de cada NPC em qualquer mapa ou IA individual por tick.

## Evidência, dependências e testes

- Fonte da decisão: escolha expressa **C** em 2026-11-06; trata-se de decisão de arquitetura, não resultado experimental.
- Documento 67 define contratos conceituais, estados, transferência agregado/indivíduo, autorizações, degradação e **36 testes candidatos não executados** (`T067-01`–`T067-36`).
- Dependências: DEC-008/011/012/021/022/027/028/029/030/034/041/043/047/048/049/050/051/052/053/054/055/056/057/058/059/060–066. DEC-006/007/013/015/017/018 permanecem em aberto.

## Próxima decisão

**DEC-068 — Ciclo de vida dos NPCs promovidos fora de cena:** (A) manter individualização/simulação detalhada continuamente; (B) rebaixar e descartar memórias automaticamente ao perder relevância; (C, recomendada) conservar identidade, memórias e fatos críticos, mas ajustar dinamicamente a atividade e arquivar/reativar com catch-up limitado, sem apagamento silencioso. Não confundir arquivamento operacional com exclusão de dados ou esquecimento.
