# ADR-0016 — Participação em níveis e intervenções causais nos arcos clássicos

- **Decisão associada:** DEC-026
- **Estado:** **APROVADA — opção C**
- **Data de aprovação:** 2026-11-06
- **Domínio:** interação opcional com campanhas clássicas, influência causal, proteção de canon e persistência
- **Fundamentação:** escolha expressa do idealizador do Infinity AI.
- **Relacionamentos:** DEC-024 / ADR-0014; DEC-025 / ADR-0015; DEC-009 / ADR-0012; DEC-011 / ADR-0007; DEC-008 / ADR-0011; DEC-019 / ADR-0003; DEC-022 / ADR-0010.

## Contexto

O Living World (primeiros testes referenciados em 1369 DR) inclui personagens e arcos históricos dos jogos originais, sem exigir que jogadores interpretem o protagonista original nem sigam as missões clássicas. O grupo deve poder conversar, ajudar e, quando houver causas e validações adequadas, modificar acontecimentos importantes. Uma intervenção de alto impacto não pode ser tratada como mero texto do LLM ou sobrescrever automaticamente flags/scripts da campanha original.

## Decisão aprovada

1. **Três níveis de participação:**
   - **N1 — Interação:** encontros, diálogos, informação, comércio e relações. Geram memória, reputação e oportunidades, sem alteração de marcos essenciais por si só.
   - **N2 — Participação:** ajuda em atividades, investigação, combate ou suporte logístico relacionados a arcos originais, com consequências locais ou progresso rastreado de objetivos, sem apropriação automática do protagonismo.
   - **N3 — Intervenção histórica:** ações verificadas podem evitar, modificar ou antecipar desfechos importantes, originando **divergências causais versionadas** em relação à linha histórica principal.
2. **Consentimento narrativo e agência dos jogadores:** encontrar ou apoiar personagens originais é sempre opcional. Nenhum jogador é convertido no Bhaalspawn ou obrigado a cumprir o roteiro central.
3. **Causalidade obrigatória:** uma divergência N3 só pode existir após uma cadeia verificável de precondições, intervenção, evidência e confirmação da consequência. A IA pode sugerir alternativas, jamais confirmar um efeito apenas por tê-lo proposto.
4. **Autoridade dividida preservada:** o host é autoridade de estado mecânico e o Infinity AI é autoridade dos registros narrativos. Comandos passam pelo controlador e allowlist; perda de confirmação produz estado pendente, sem repetição cega e sem itens/mortes fictícios.
5. **Proteção de marcos críticos:** eventos irreversíveis têm classificação de risco, conflitos com cronologia e dependências avaliadas antes de autorizar a transição. A política exata de aprovação (automática para quais casos, anfitrião, consenso do grupo) **não foi decidida** e precisa de SPEC/decisão posterior; até lá, mudanças críticas ficam bloqueadas ou pendentes.
6. **Canon e persistência:** alterações confirmadas produzem branch por campanha com proveniência, causalidade e consequências; o material histórico original permanece como referência rastreável e não é apagado. Restaurações de save exigem reconciliação e prevenção de duplicidade.
7. **Performance:** validação, agendamento e regras de progressão usam código determinístico; LLM local fica reservado a diálogos e criação narrativa aberta, sob demanda.
8. **Separação de modos:** Original e Living World têm saves, scripts e estado isolados. Mods e integrações reais continuam sujeitos a provas de conceito com BG2:EE, EEex, EET e multiplayer.

## Consequências e limitações

- Arcos passam a expor oportunidades classificadas por nível e não apenas marcadores binários de missão.
- N3 exige mecanismo de dependências entre acontecimentos, auditoria de fatos e proteção de entidades históricas.
- **Não é uma promessa de acesso livre a todos os scripts/cenas originais**: participações e ramificações exigem adaptação técnica e testes de compatibilidade.
- O motor do jogo pode não permitir determinados efeitos em tempo real; quando a bridge não tiver capacidade comprovada, tratar o conteúdo como apenas planejado/antecipado, sem anunciar implementação.
- A decisão não aprova que mudanças globais críticas sejam executadas automaticamente nem define o órgão de aprovação.

## Testes de aceitação candidatos — para futuras SPECS

1. NPC clássico N1 responde sem movimentar flags do arco original ou revelar informação não conhecida.
2. Apoio N2 validado atualiza a tarefa e o histórico do grupo sem alterar a identidade do protagonista original.
3. Falha numa tarefa N2 não conclui nem duplica a recompensa.
4. Intervenção N3 com causa e permissão verificadas produz branch narrativo rastreável; fatos anteriores permanecem acessíveis.
5. Tentativa N3 sem permissão ou condição resulta em bloqueio, sem mudança narrativa ou mecânica.
6. Save anterior/restauração não duplica intervenções, NPCs, recompensas ou consequências.
7. Dois clientes recebem estado coerente depois da confirmação do host; não presumir sincronização EEex sem prova.
8. Ausência dos jogadores usa DEC-025/022 e não executa um marco irreversível sem política aprovada.
9. O NPC não passa a conhecer um segredo apenas porque um LLM teve acesso a ele.
10. Alteração de canon não modifica saves do modo Original.

## Pendências explícitas

- Política de consentimento/aprovação dos eventos críticos: anfitrião, consenso, regras automáticas aprovadas por classe de evento.
- Categorias concretas de gravidade e restrições de mudanças em NPCs canônicos.
- Mapeamento de flags/quests do motor, limites EEex, reconciliação e sincronização multiplayer.
- DEC-005 (sistema de regras e dificuldade), DEC-006 (runtime de IA), DEC-012 (segurança), DEC-015 (gates de testes).

## Próxima discussão

**DEC-005 — Base de regras e balanceamento de encontros**: preservar AD&D/Infinity Engine como autoridade mecânica e definir como o gerador de encontros estimará dificuldade sem supor que CR de outras edições seja diretamente compatível.
