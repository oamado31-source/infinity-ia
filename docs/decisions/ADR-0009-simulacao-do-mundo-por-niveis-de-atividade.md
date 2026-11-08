# ADR-0009 — Simulação do mundo por níveis de atividade

- **Decisão associada:** DEC-021
- **Estado:** **APROVADA — opção C (simulação por níveis de atividade)**
- **Data da aprovação:** 2026-11-06
- **Domínio:** simulação de NPCs, regiões e tempo, escalabilidade, consistência e inferência sob demanda
- **Origem:** escolha explícita do idealizador no diálogo de discovery.
- **Relacionamentos:** DEC-001/ADR-0001 (coop e evolução futura), DEC-004/ADR-0002 (Living World), DEC-011/ADR-0007 (autoridade), DEC-014/ADR-0008 (código primeiro), DEC-019/ADR-0003 (segredos), DEC-020/ADR-0004 (revisões), DEC-008 (persistência), DEC-009 (canon/cronologia), DEC-006 (política de LLM).

## Contexto

O Living World deverá dar a impressão de que cidades, NPCs, facções e rotas possuem continuidade mesmo quando o grupo viaja para outra região. Simular todos os NPCs continuamente, com pathfinding, combate e inferência a cada tick, seria desnecessário e incompatível com o objetivo de executar Baldur's Gate II: Enhanced Edition em hardware modesto. Por outro lado, congelar completamente tudo fora da área do jogador reduz o dinamismo do mundo.

## Decisão aprovada

Adotar **simulação escalonada conforme o nível de atividade**, com quatro regimes lógicos:

1. **Ativa / com jogadores:** o motor do jogo executa estado mecânico de entidades carregadas e interações. O Infinity AI coordena eventos autorizados, comportamento por regras e IA somente quando necessário; não tenta assumir a autoridade mecânica do host.
2. **Próxima / relevante:** executar lógica leve de agendas, deslocamentos abstratos, prazos, rumores ou conflitos por eventos e regras, sem mover fisicamente cada criatura a cada quadro. A distância/ligação entre áreas e as condições de promoção a esse nível serão definidas em SPEC.
3. **Distante:** aplicar evolução resumida em lotes/eventos, de maneira limitada e reproduzível, levando em conta calendário, estado confirmado, prioridades de facções e histórias pertinentes. Não manter IA nem simulação frame a frame.
4. **Inativa/dormente:** suspender processamento contínuo. Ao surgir uma demanda, reativação ou evento autorizado, computar apenas a atualização necessária dentro de limites de execução e do relógio definido futuramente.

A alternância de níveis deve ser orientada por presença de jogadores, relevância narrativa, dependências e recursos disponíveis, sem exigir um modelo por NPC. O modo Original permanece isolado: nenhum desses processos altera o progresso de campanhas originais (DEC-004).

## Condições inegociáveis derivadas de decisões anteriores

- **Determinístico primeiro (DEC-014):** schedules, estados, tabelas de eventos, conflitos mecânicos simplificados e economia seguem código e seeds versionadas. LLM local só participa de criação/interpretação aberta, sob demanda, com quota e validação; nenhuma consulta contínua a LLM para NPCs ausentes.
- **Autoridade (DEC-011):** o resultado simulado fora de cena é um fato narrativo condicionado ao domínio correto. Mudança de inventário, spawn real, dano, morte ou alteração de área no BG2:EE não deve ser declarada como aplicada sem mecanismo de execução e confirmação no host. Se não há garantia técnica, gerar proposta/fato narrativo compatível e marcar efeitos mecânicos como pendentes de materialização e reconciliação.
- **Conhecimento/privacidade (DEC-019):** uma região distante não pode fazer NPCs 'descobrirem' segredos de personagens por onisciência da IA; cada aquisição de conhecimento precisa de via causal registrada.
- **Canon/revisões (DEC-020):** eventos e consequências já confirmados têm precedência sobre simulações hipotéticas. Mudanças de passado não alteram eventos efetivos automaticamente.
- **Custo e previsibilidade:** restringir CPU, filas, tempo de processamento e quantidade de eventos por região/intervalo. Valores quantitativos dependerão de benchmarks e SPECS; em sobrecarga, priorizar regiões ativas e adiar atualizações distantes.
- **Mundo compartilhado futuro (DEC-001):** prever identificadores por campanha, região e revisão de mundo, evitando processamento simultâneo conflitante, mas não declarar que BG2:EE já suporte vários grupos independentes.
- **Isolamento e rollback:** checkpoints do mundo narrativo, deduplicação e auditabilidade; uma atualização em lote precisa poder ser interrompida e retomada sem duplicar eventos.

## Fluxo proposto (não implementado)

```text
Evento de entrada/saída da região / tick de campanha / demanda narrativa
  -> identificar sessão, campanha, relógio, revisão e regiões envolvidas
  -> classificar atividade: ATIVA | PROXIMA | DISTANTE | DORMENTE
  -> definir orçamento e janela de atualização
  -> selecionar regras / cronogramas / eventos com seed e versão
  -> propor mudanças narrativas e mecânicas diferenciadas
  -> validar lore, causalidade, conhecimento e conflitos
  -> persistir efeitos narrativos autorizados; enviar efeitos mecânicos
     ao host somente se tecnicamente executáveis e confirmáveis
  -> salvar cursor/checkpoint e telemetria; reprocessamento idempotente
```

## Alternativas consideradas

- **A — Apenas regiões ativas:** simplicidade maior, mas continuidade limitada para mundo aberto.
- **B — Mundo totalmente simulado continuamente:** flexível, porém custo, complexidade, risco de divergência e consumo de processamento desproporcionais.
- **C — Níveis de atividade:** **aprovada**, preserva continuidade com orçamento controlável.

## Consequências e riscos

**Benefícios:** mundo evolutivo com custos proporcionais à atividade, baixa frequência de inferência, condições para simulação offline em lotes (se futuramente aprovada), testes reproduzíveis e compatibilidade conceitual com multiplayer cooperativo.

**Riscos:** mudanças inconsistentes entre áreas, explosão de catch-up após longa ausência, eventos impossíveis em cenas não carregadas, rumores sem origem, divergência entre saves do host e DB externo, mortes/inventário gerados sem confirmação, perda de isolamento entre campanhas.

**Mitigações planejadas:** limites por janela, filas com prioridade, revisão otimista ou lock por região, IDs idempotentes, trilhas de proveniência, reidratação de áreas com validação e checkpoints versionados. Os detalhes de implementação continuam pendentes.

## Limites explícitos da aprovação

A DEC-021 **não escolhe ainda**:
- se o relógio avança quando o jogo/servidor está fechado, nem por quanto tempo (proposta de nova DEC-022);
- fórmula de proximidade entre regiões, cadence de lotes e limites em minutos/CPU;
- quais transformações fora de cena podem ser irrevogáveis (morte de NPC importante, destruição de local, perda de itens etc.); sujeitos às DEC-008, DEC-009 e SPECS;
- suporte técnico real para modificações dinâmicas de áreas/entidades via EEex em sessões multiplayer; depende de POC;
- o modelo de LLM local, o hardware e suas cotas; DEC-006.

## Testes candidatos (antes de aceitar features)

1. Dez NPCs ociosos fora da área ativa não disparam chamadas periódicas ao LLM.
2. Uma região distante com os mesmos fatos, seed, versão de regras e intervalo produz o mesmo resumo de eventos.
3. Saída/retorno de uma região aplica evolução por lotes uma única vez, sem duplicar recompensas, criaturas ou fatos.
4. Se dois clientes solicitam reentrada ao mesmo tempo, ambos recebem a mesma revisão narrativa; conflitos e sincronização mecânica são rejeitados/conciliados pelo host.
5. Um NPC distante não revela segredo que não descobriu em evento causal autorizado.
6. Falha no processamento de um lote mantém checkpoint anterior e permite retomada idempotente.
7. Modelo local desligado não impede combate, navegação, cronograma ou atualização determinística.
8. O modo Original permanece intocado após simulação longa do Living World.
9. Um lote que proponha morte, mudança de itens ou spawn no motor não marca sucesso sem evidência do domínio mecânico.
10. Simulações com orçamento excedido adiam ou simplificam regiões distantes sem travar o gameplay.

**Situação real:** decisão de arquitetura documentada. Nenhuma dessas garantias foi validada no jogo neste estágio de Discovery.
