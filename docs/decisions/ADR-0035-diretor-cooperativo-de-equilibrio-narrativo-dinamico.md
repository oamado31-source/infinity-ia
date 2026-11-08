# ADR-0035 — Diretor cooperativo de equilíbrio narrativo dinâmico

- **Decisão:** DEC-040 — coordenação de histórias pessoais em multiplayer.
- **Status:** **APROVADA — opção B**.
- **Data:** 2026-11-06.
- **Origem:** escolha explícita do idealizador nesta conversa.
- **Versão de incorporação:** Infinity AI Discovery v3.6.
- **Decisões relacionadas:** DEC-001, 004, 008, 011, 012, 014, 019, 020, 021, 022, 025, 027, 028, 029, 030, 034, 039.

## Contexto

O Living World é cooperativo, com históricos e arcos pessoais persistentes (DEC-004/039). Uma aventura pode nascer de um personagem e envolver outros jogadores; entretanto, o sistema não pode monopolizar a campanha com um protagonista, impor rotação rígida nem expor segredos em nome da colaboração. A configuração e os testes de multiplayer real permanecem pendentes.

## Alternativas consideradas

1. **A — Alternância planejada:** oportunidades uniformemente intercaladas, com risco de interrupções artificiais.
2. **B — Diretor cooperativo com equilíbrio dinâmico:** avaliar relevância, oportunidades, disponibilidade, foco recente e participação livre **(ESCOLHIDA)**.
3. **C — Histórias totalmente independentes:** maior isolamento, risco de descoordenação e dispersão do grupo.

## Decisão aprovada

1. Criar o **Cooperative Story Director (CSD)** como função lógica de orquestração do **Personal Story Director (PSD)**, priorizando oportunidades narrativas por regras rastreáveis. Não requer um LLM executando continuamente.
2. Otimizar **equilíbrio de oportunidades significativas ao longo do tempo**, sem exigir igualdade aritmética de tempo de tela, contagem de missões ou alternância por rodada/sessão.
3. Usar como insumos candidatos: elegibilidade do gancho; situação do mundo; data DR e janelas; personagem titular e disponibilidade; convites aceitos; histórico de foco narrativo; participações recentes; impacto no grupo; coerência com missões ativas; custo/tempo de sessão e nível de risco.
4. O titular mantém seu arco e sua agência: **aceitar, adiar, rejeitar, mudar rumo e decidir o que revelar**. Outros personagens podem desempenhar papéis substanciais mediante contexto e convites autorizados, mas não assumem o controle de fatos secretos ou decisões pessoais do titular.
5. A narrativa cooperativa será **opcional**: não exigir adesão de todo o grupo, dividir automaticamente o grupo, teletransportar personagens, forçar missões ou concluir etapas pessoais de ausentes.
6. A ausência do titular **não autoriza** desfechos pessoais cruciais nem revelações forçadas. O mundo e arcos paralelos podem evoluir conforme DEC-021/022/025, respeitando janelas, consentimentos e autorizações DEC-027/034; detalhes dos limites de progressão em ausência serão parte das SPECS.
7. Diferenciar **contribuição compartilhada** de **autoria/progressão individual**. Reputação, alinhamento, recompensa e marcos devem ser atribuídos por participação e evidência confirmada — não automaticamente a todos os jogadores.
8. Preservar **sigilo e proveniência de conhecimento** (DEC-019/028): a proposta de contribuição cooperativa não concede acesso implícito ao histórico confidencial do titular. Pré-filtrar cada contexto destinado a jogador/NPC/LLM.
9. Qualquer ação mecânica ou mudança persistente depende de gateway de ações permitido, autorização por risco e **confirmação do host**. Tratamento de `UNCERTAIN`, log de eventos, deduplicação e save/load seguem as decisões existentes.
10. O modo **Original** permanece separado e intacto. O CSD constitui arquitetura alvo, **não funcionalidade já implementada/testada no BG2:EE/EEex/multiplayer**.

## Exemplo conceitual

O histórico de uma ladina cria uma investigação de parentesco em Athkatla. O diretor identifica uma pista compatível com a cronologia e apresenta a ela uma oportunidade sem revelá-la a outros. Se a titular aceitar e convidar o grupo, o paladino pode negociar com uma ordem, o mago investigar um objeto e o guerreiro auxiliar na proteção. Cada participante só recebe informações que possa legitimamente conhecer. A ladina pode prosseguir em privado, adiar a missão ou decidir não envolver o grupo.

Uma sessão dedicada à ladina não impede a continuidade natural de sua aventura. Entretanto, se outros jogadores permanecerem repetidamente sem oportunidades relevantes, o diretor deve considerar ganchos desses personagens nos próximos momentos **plausíveis**, sem interromper um clímax necessário nem inventar objetivos artificiais.

## Invariantes obrigatórias

- **Agência:** nenhum jogador é obrigado a aceitar uma missão pessoal de outro.
- **Sigilo:** equidade narrativa não é motivo para divulgar fatos privados.
- **Causalidade:** um marco não é concluído com base apenas em fala de NPC/LLM.
- **Tempo:** respeitar calendário, política offline, janelas e ausência do titular.
- **Canon:** não antecipar fatos oficiais nem dispensar autorização HIGH.
- **Mecânica:** ações do mundo exigem recibo inequívoco do host.
- **Equidade:** medir qualitativamente oportunidade e agência, não equiparar contagem bruta de diálogos a protagonismo.
- **Integridade:** regras versionadas, eventos idempotentes, isolamento por campanha e rollback/reconciliação.

## Critérios de aceitação candidatos

1. Gerar oportunidades para quatro histórias diferentes sem obrigatoriedade de alternância rígida.
2. Garantir que um arco pessoal importante possa continuar naturalmente, sem monopolização sistemática indefinida das oportunidades.
3. O titular pode aceitar, adiar, rejeitar e escolher participação privada ou cooperativa sem penalidade extrínseca automática.
4. Convite ou colaboração não deve expor segredo ou conhecimento proibido.
5. Personagem ausente não sofre resolução pessoal irreversível gerada artificialmente pelo diretor.
6. Cooperação de dois personagens em uma missão não duplica itens, recompensas, flags nem progresso.
7. Gancho indisponível por canon, região, tempo ou recurso não é imposto para cumprir quota de protagonismo.
8. Ações individuais repercutem somente quando atribuição e confirmação são comprovadas.
9. O modo Original e outras campanhas não recebem conteúdo ou memória dessa simulação.
10. O LLM indisponível não bloqueia agendas, regras e eventos já validados.
11. Em caso de resposta `UNCERTAIN` do host, não marcar marco como concluído nem repetir ação sem reconciliação.
12. Reiniciar campanha não altera indevidamente as prioridades e as oportunidades registradas.

## Impacto sobre SPECS e POCs

- Definir no futuro algoritmo de prioridades, janelas, métricas de oportunidade, tamanho de backlog, preferências por jogador, limites de exposição, auditoria e UI de convite.
- Validar integração efetiva PSD/CSD com diálogos, eventos e saves de BG2:EE e sincronização entre 2+ clientes; não presumir capacidade de alterar engine/flags em runtime.
- Estabelecer política de consentimento/autorização quando o arco **de um jogador** produz consequências coletivas ou revela conteúdo de outro, especialmente no contexto de participantes ausentes.

## Próxima discussão — DEC-041

**Quem autoriza decisões compartilhadas que cruzam históricos, segredos e consequências para mais de um jogador?** Considerar autonomia individual, anuência de participantes afetados e política do anfitrião para alterações de alto impacto. **DEC-041 ainda não decidida**.
