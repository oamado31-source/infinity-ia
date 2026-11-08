# ADR-0055 — Validação híbrida das saídas de IA por risco e evidência

- **Decisão:** DEC-060, opção **C**, aprovada em 2026-11-06.
- **Status:** APROVADA como arquitetura, sem implementação.
- **Discovery:** v5.6.
- **Detalhamento:** `docs/60-validacao-de-respostas-coerencia-canonica-e-gates-por-risco.md`.

## Contexto

O AI Model Router (DEC-059) seleciona modelos autorizados, mas respostas fluentes podem inventar fatos, violar cronologia de Forgotten Realms, divulgar segredos ou sugerir mudanças mecânicas incompatíveis com BG2:EE e mods. Um segundo LLM não é fonte autoritativa de verdade.

## Decisão

1. **Pipeline em camadas e proporcional ao risco.** Verificar identidade da tarefa e contexto, schema e limites, autorização/ACL, conhecimento legítimo do falante, cronologia/cânone/ramo, coerência com quests/estado de build e regras de publicação. Conteúdo com impacto maior exige evidência e revisão mais rigorosas.
2. **Separar categorias de conteúdo:** fala efêmera, rumor/opinião, informação factual, proposta de missão, atualização persistente e ação mecânica. Não converter uma fala em fato confirmado automaticamente.
3. **Fonte e proveniência:** vincular alegações verificáveis a fonte curada ou eventos confirmados com data, local, identidade, versão e grau de confiança; ausência de fonte = desconhecido, não verdadeiro. Diferenciar cânone base, divergência legítima da campanha, rumor e invenção criativa explicitamente permitida.
4. **Conhecimento não onisciente:** checar ACL antes de geração e antes de publicação; NPC só afirma como conhecido aquilo a que teve acesso legítimo. Rumores podem ser falsos se rotulados como crença e não como fato.
5. **Validação determinística prioritária:** regras de autorização, schemas, invariantes, versões, quests e tempo não são substituídas por julgamento probabilístico. Avaliador LLM opcional como sinal auxiliar, nunca como autoridade final.
6. **Estados de decisão:** `ACCEPT`, `REVISE`, `DEFER`, `REJECT`, `ESCALATE`; política fail-closed quando faltar prova de segurança, especialmente para irreversíveis, ações mecânicas, cânone protegido e vazamento de segredos. Revisões não podem ampliar permissões.
7. **Controle de efeitos:** qualquer mudança persistente requer evento confirmado/revisão correta; efeitos mecânicos só por Action Gateway tipado, com receipt do host. Saída de LLM não executa comandos.
8. **Risco e latência:** diálogo trivial pode usar verificações leves sem LLM revisor obrigatório; missões, relações, fatos canônicos e consequências irreversíveis exigem gates crescentes. Definição de thresholds e métricas fica para SPECS/DEC-015.
9. **Resiliência:** falha de verificador, timeout, resultado stale ou inconsistência não libera publicação; usar conteúdo já validado, revisão ou pendência conforme risco. Não reexecutar mutações `UNCERTAIN`.
10. **Auditoria e privacidade:** registrar razões e IDs de evidência, não segredos brutos; vincular `campaign_id`, `branch_id`, `build_fingerprint`, `world_revision`, `permission_epoch`, modelo/worker e política. Revisar falsos positivos e falsos negativos com conjuntos de teste.

## Consequências e limites

- Compatível com DEC-009/023/024/025/026 (cronologia e arcos), DEC-028/029/030 (conhecimento, rumores e reputação), DEC-050/051 (scripts e inventário), DEC-027/012 (risco/gateway), DEC-053/055 (persistência/saúde), DEC-058/059 (LAN/roteamento).
- Não garante infalibilidade factual nem determina modelos, fontes completas, thresholds ou integrações BG2:EE/EEex.
- DEC-006, DEC-013, DEC-015 e DEC-018 continuam abertas.
- Próxima: **DEC-061 — política de fontes, conflitos entre evidências e revisão humana do conhecimento canônico**.

## Adendo aprovado: organização física do conhecimento por período (Discovery v5.6.1)

**Solicitação expressa do idealizador:** a base de conhecimento do cânone **não** deverá ser uma coleção monolítica de fatos de todas as épocas. O conteúdo de cada período, com granularidade anual inicial, deverá residir em **diretórios fisicamente separados**. Exemplo: `knowledge/periods/1369-DR/`, contendo `chronology/`, `events/`, `organizations/`, `guilds/`, `characters/` e `regions/`. Os dados de outros anos não serão copiados indiscriminadamente para essa pasta.

**Consulta contextual obrigatória:** para uma interação situada em **1369 DR**, o resolvedor selecionará primeiro o catálogo de `1369-DR` pelo calendário e ramo *confirmados da campanha*. Conteúdos de anos anteriores só poderão ser recuperados mediante pedido histórico/continuidade explícita e filtro temporal `as-of`, e apenas se permanecerem relevantes e disponíveis naquele momento; **conteúdo do futuro não entra como fato conhecido nem como evento consumado**. Não é permitido fazer busca semântica indiscriminada em um índice de todos os anos e filtrar depois da exposição ao modelo.

**As pastas não concedem conhecimento ao NPC.** O conteúdo recuperado permanece sujeito às políticas DEC-028/029 (ACL, fontes, local, propagação, `learned_at`) e às verificações DEC-060. A aplicação do filtro e do contexto deve ocorrer **antes do prompt**, tanto para inferência no host quanto para workers LAN da DEC-057/058/059.

**Separação adicional:** a história específica dos jogadores e mudanças causais pertencem a um *overlay* persistente por `campaign_id`, `branch_id`, ano e revisão; não alteram o conteúdo curado do cânone, que permanece versionado e tratado como somente-leitura em tempo de jogo. O overlay respeita as decisões DEC-008/009/022/053/054.

**Metadados e interfaces candidatos:** cada diretório de ano deve ter manifesto/versionamento, precisão de data, fonte, status de curadoria, validade temporal, escopo geográfico, entidade e referências a fatos anteriores. Índices globais podem guardar **somente roteamento/metadados seguros**, nunca substituir partições anuais com um corpus único consultado por padrão. Formato concreto, esquema de arquivos, indexação física e atomicidade seguem para SPECS/POCs.

**Limites:** diretório não torna um fato verdadeiro, não resolve conflitos entre fontes da **mesma** época nem exige criar hoje todo o catálogo de 1369 DR. A DEC-061 continua **aberta** para governança de proveniência/contradições editoriais. Esta é uma **emenda à DEC-060/C**, não uma DEC independente nem um novo ADR; mantém-se o número de 55 ADRs. Ver `docs/60a-base-temporal-particionada-por-ano-e-recuperacao-contextual.md` e a árvore vazia de `knowledge/`.

## Decisão complementar DEC-061/C (Discovery v5.7)

A DEC-061, agora aprovada no ADR-0056, detalha como rastrear fontes conflitantes e curar interpretações contextualizadas **dentro da mesma pasta anual**. A emenda física à DEC-060 permanece inalterada: diretórios separados por ano DR, busca primária no ano confirmado, passado apenas por referência válida, futuro não consumado e overlays de campanha isolados. `UNRESOLVED` não autoriza afirmar fato nem dispensar os gates de risco/ACL; LLM avaliador continua auxiliar, não fonte de verdade. Ver documento 61.
