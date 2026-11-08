# ADR-0015 — Progressão híbrida dos arcos paralelos com participação opcional

- **Decisão:** DEC-025
- **Estado:** **APROVADA — opção C, progressão híbrida com oportunidades de participação**
- **Aprovada em:** 2026-11-06
- **Fase:** Discovery; decisão arquitetural aprovada, **não é SPEC técnica validada nem prova de implementação no BG2:EE/EET**.
- **Relações obrigatórias:** DEC-024 / ADR-0014 (campanhas paralelas), DEC-009 / ADR-0012 (canon e divergência), DEC-022 / ADR-0010 (relógio híbrido), DEC-021 / ADR-0009 (níveis de atividade), DEC-008 / ADR-0011 (persistência), DEC-011 / ADR-0007 (autoridade), DEC-014 / ADR-0008 (código primeiro), DEC-019 (controle de segredos).

## Problema

No Living World, personagens e tramas das campanhas clássicas devem coexistir com os personagens originais dos jogadores. Se o grupo viajar ou ignorar uma trama, ela não pode ficar congelada indefinidamente; por outro lado, não queremos que decisões relevantes ocorram ou oportunidades desapareçam sem regras explícitas, principalmente durante ausências com o jogo fechado.

## Decisão aprovada

1. **Progressão híbrida por calendário e condições:** cada arco paralelo elegível avança por regras de estado, dependências, janelas temporais, fatos históricos selecionados e decisões confirmadas. O progresso **não depende da presença** do grupo para cada etapa. O tempo relevante é o *tempo do mundo autorizado* pela DEC-022; jamais se assume que dias reais e dias de Forgotten Realms têm conversão fixa.
2. **Participação opcional:** determinados marcos permitem encontro, auxílio, negociação, interferência ou recusa do grupo, por meio de **janelas de oportunidade** detectáveis e vinculadas a região, época e pré-condições. A janela não transforma a missão principal clássica em obrigação do PC do Living World.
3. **Ausência de interferência:** se os jogadores não participarem, o arco poderá continuar rumo à trajetória canônica adotada pela campanha, **desde que** a progressão seja admissível por calendário, fatos confirmados e políticas de proteção de eventos críticos. O sistema não marca missões originais como mecanicamente concluídas só por narrativa gerada.
4. **Intervenção e divergência:** quando jogadores interferem, apenas efeitos realmente verificados podem alterar o resultado. Divergências da cronologia oficial são registradas como ramo causal da campanha, com suspensão de eventos futuros incompatíveis (DEC-009); não fazem alterações silenciosas na campanha Original.
5. **Proteção de momentos críticos:** morte/ressurreição de personagens importantes, mudanças de regime, destruição de localidades e outros desfechos potencialmente irreversíveis não são aplicados automaticamente durante ausência do grupo sem uma política de autorização específica, ainda pendente. O estágio pode ficar `PENDING_CRITICAL_DECISION` e apresentar consequências reversíveis, não antecipar resultado final.
6. **Código primeiro:** agendamento, pré-condições, seleção de janelas, avanço, cooldown, verificação de canon, reconciliação e idempotência devem usar regras determinísticas. LLM local é opcional, sob demanda, para diálogos, rumores e variações narrativas; **não decide se um fato ocorreu** nem executa comandos sem passar pelo controlador.
7. **Integridade de multiplayer:** apenas o host confirma efeitos mecânicos e a bridge transmite comandos permitidos com recibos quando disponíveis. Resultado de execução incerto deve ficar pendente de reconciliação e não pode ser reaplicado cegamente. A prova de sincronização multiplayer BG2:EE/EEex permanece pendente.
8. **Contexto de personagens e conhecimento:** NPCs comentam o arco segundo o que podem saber e quando a notícia alcança sua região; histórico secreto dos jogadores não pode ser exposto porque um agente recebeu o contexto inteiro.
9. **Convivência com legado:** arcos de BG1/IWD anteriores ao ano-base são referências históricas ou repercussões; arcos contemporâneos podem evoluir. Datas incertas de SoD/ToB não são convertidas em deadlines exatos sem curadoria (DEC-023/024).
10. **Política de recuperação:** ao carregar ou fazer catch-up, cada transição é associada a campanha, arco, marco, versão das regras e revisão do tempo; reprocessamentos não duplicam rumor, evento, recompensa, morte nem progressão.

## Comportamento esperado (exemplo ilustrativo, não canon de BG)

Um grupo chega a Athkatla em 1369 DR e encontra um aliado de uma trama clássica. A conversa abre uma oportunidade de fornecer uma informação durante uma janela de dias de jogo. Se o grupo aceitar e concluir a tarefa, o resultado confirmado modifica o arco. Se ignorar, a janela encerra conforme política autorizada e o arco continua por marcos pré-definidos. Se o grupo estiver desconectado, um marco que alteraria irreversivelmente o mundo fica pendente caso a política não autorize seu avanço. Ao regressar, os jogadores podem ouvir um rumor coerente com os fatos confirmados e com a origem da informação.

## Modelo de estados candidato — não congelar como implementação

- `NOT_ELIGIBLE`: falta data, recurso, dependência ou evento habilitador.
- `SCHEDULED`: cronologia/condições conhecidas, ainda não elegível.
- `ACTIVE`: arco evoluindo; janelas podem abrir.
- `WINDOW_OPEN`: oportunidade de interação opcional disponível.
- `WINDOW_EXPIRED`: oportunidade encerrada, sem falha geral automática do grupo.
- `PENDING_CRITICAL_DECISION`: marco irreversível aguardando política/autorização.
- `PENDING_MECHANICAL_CONFIRMATION`: intenção validada, mas sem recibo do host.
- `DIVERGED`: ramo causal confirmado diferente do canon-base.
- `COMPLETED`: resultado validado, persistido e reconciliado.
- `BLOCKED_UNVERIFIED`: indisponibilidade de recurso/bridge/compatibilidade impede progressão comprovável.

Esses estados devem ser reconciliados com os estados de alto nível já propostos no ADR-0014; não são duas máquinas de estados independentes automaticamente sincronizadas.

## Consequências arquiteturais

- Criar um **Arc Scheduler** (regras de calendário e dependências), **Opportunity Window Manager** (janelas e elegibilidade), **Arc State Store** (snapshots + eventos) e **Arc/Canon Reconciler**. São responsabilidades lógicas; não pressupõem quatro serviços/processos.
- Diferenciar transições **puramente narrativas** de **mutações mecânicas**. As segundas exigem confirmação do jogo/host, sem exceções baseadas em texto do LLM.
- Cada janela precisa de intervalo temporal com precisão/confiabilidade da fonte, gatilhos de região, opcionalidade e política de expiração. Janelas não existem quando as datas são insuficientemente justificadas: podem ser condicionais, sem data rígida.
- `FROZEN` congela o relógio; `PARTIAL` e `REALTIME` apenas habilitam o *tempo de mundo permitido*, não autorizam automaticamente desfechos críticos.

## Alternativas não adotadas

- **A — Suspender sempre até jogadores chegarem:** congela personagens clássicos e contradiz o mundo vivo.
- **B — Avanço totalmente automático:** pode eliminar personagens ou oportunidades importantes durante ausência, quebrar canon e duplicar estados.
- **C sem proteção adicional:** ausência de janelas e de reconciliação produziria perda de agência e contradições.

## Verificações candidatas para SPEC (ainda não executadas)

1. O arco avança ao receber um marco temporal válido, mesmo quando o grupo está em outra região; não exige um LLM.
2. Uma oportunidade aparece apenas quando intervalo, região, dependências e conhecimento permitem.
3. Recusar/ignorar oportunidade não bloqueia exploração nem transforma o PC em protagonista clássico.
4. Expirar uma janela segue uma regra registrada, sem encerrar indevidamente uma quest do PC.
5. Se o mundo estiver em `FROZEN`, uma semana real offline não avança o arco.
6. `PARTIAL`/`REALTIME` só avançam no tempo efetivamente autorizado e respeitam `PENDING_CRITICAL_DECISION`.
7. Uma intervenção confirmada altera o arco e cria ramo divergente; a versão da história oficial não é alterada.
8. Falha de recibo mecânico deixa o resultado pendente; retry e save/load não duplicam item, NPC, morte ou recompensa.
9. Carregar um save mais antigo não reativa uma janela encerrada sem política de restauração explícita.
10. Rumores respeitam tempo, local e conhecimento de cada NPC, inclusive segredos de PCs.
11. Um arco sem importação técnica comprovada não é declarado executado na área do jogo.
12. Dois clientes recebem o mesmo resultado do host quando o suporte técnico estiver validado.

## Pontos expressamente não resolvidos

- **DEC-026 (próxima):** profundidade de participação dos jogadores nos arcos clássicos (cameos, missões de apoio e intervenções causais significativas) e limites de protagonismo/autorização.
- Políticas de aprovação de desfechos críticos, limiares, timeouts, janela padrão, conversão de tempo e número de arcos ativos.
- Datas exatas, resultados controversos e personagens do canon para cada arco dependem de curadoria e inventário.
- Compatibilidade real de mapeamento de NPCs/flags/quests e sincronização multiplayer no BG2:EE + EEex, EET, IWD e NWNForBG.
- Estratégia de revisão/rollback de arcos quando um save do host for restaurado.

**Nenhuma funcionalidade foi implementada ou executada no motor a partir desta decisão.**
