# ADR-0010 — Relógio híbrido e configurável do Living World

- **Decisão associada:** DEC-022
- **Estado:** **APROVADA — opção C (tempo híbrido e configurável)**
- **Data de aprovação:** 2026-11-06
- **Domínio:** calendário, sessões, catch-up, causalidade, simulação fora de cena
- **Origem:** escolha explícita do idealizador na conversa de Discovery.
- **Relacionamentos:** DEC-021 / ADR-0009 (níveis de atividade), DEC-011 / ADR-0007 (autoridades), DEC-014 / ADR-0008 (regras primeiro), DEC-004 / ADR-0002 (modos isolados), DEC-019 / ADR-0003 (segredos), DEC-020 / ADR-0004 (revisões), DEC-008 (persistência), DEC-009 (canon) e DEC-018 (recuperação/observabilidade).

## Contexto e objetivo

O Living World deve preservar continuidade entre sessões cooperativas privadas, mas sem exigir um servidor ou LLM permanentemente ligado durante períodos em que ninguém joga. Avançar cada região de modo contínuo, ou aplicar todos os eventos acumulados após longas ausências, arriscaria inconsistências, perda de missões importantes e consumo excessivo de recursos. A DEC-021 já determinou simulação escalonada; a DEC-022 define a política de **tempo autorizado** para alimentar essa simulação.

## Decisão aprovada

1. **Durante sessões em andamento:** seguir o calendário e o tempo de jogo reconhecidos pelo host, respeitando as funções existentes do BG2:EE e o isolamento do modo Living World.
2. **Ao encerrar a sessão:** registrar checkpoint do mundo, instante efetivo do calendário de jogo, registro temporal da finalização e versão da política. Sem sessão ativa, não é exigida simulação contínua.
3. **Com jogo/serviços desligados:** a arquitetura permite processar evolução acumulada **somente no retorno** ou no próximo processamento autorizado, sem manter agentes vivos. O decurso de tempo real por si só não significa que uma ação mecânica ocorreu no jogo.
4. **Configuração por campanha/host:** disponibilizar três políticas de ausência — `FROZEN` (nenhum avanço por tempo real), `PARTIAL` (avanço limitado por conversão configurável) e `REALTIME` (referência ao tempo real, com limites de processamento, efeitos e revisão). O anfitrião escolhe a política; conversões, limites e padrão inicial serão detalhados em SPECS posteriores, não foram aprovados como números neste ADR.
5. **Retorno e catch-up:** calcular intervalo admissível, aplicar atualização **bounded**, orientada a lotes/níveis da DEC-021, sem simular cada NPC a cada segundo de ausência; preservar checkpoints, logs e deduplicação. Ações com impacto mecânico no BG2:EE só serão executadas e confirmadas pelo host conforme DEC-011.
6. **Eventos irreversíveis e sensíveis:** a ausência do grupo não autoriza, por si só, morte definitiva de NPC significativo, destruição de locais, eliminação de itens de jogadores, fracasso de missões essenciais, perda permanente ou divulgação de segredos. Tais eventos exigem regras específicas, critérios de autorização e confirmação adequados, a serem definidos e aprovados nas SPECS/DEC-009. O planejador pode registrar **propostas pendentes** em vez de executar esses efeitos.
7. **Multiusuário:** um único avanço temporal autorizado por revisão da campanha. Entradas simultâneas e repetição do mesmo catch-up não podem dobrar eventos ou mover o relógio duas vezes.
8. **Modos separados:** política de relógio do Living World nunca modifica saves, progressão ou calendário da campanha Original.

## Modelo conceitual de relógios

- `world_time`: instante do calendário do mundo no último checkpoint **confirmado** para a campanha.
- `last_session_closed_at_utc`: instante externo da finalização, para calcular ausência; não é relógio de combate.
- `time_policy`: `FROZEN` | `PARTIAL` | `REALTIME`, com `policy_version` e parâmetros versionados por campanha.
- `catchup_cursor` + `world_revision`: intervalo já processado e revisão persistida; impede processamento duplo.
- `pending_changes`: propostas não materializadas por dependência de regras, presença de jogador ou confirmação do host.

O algoritmo concreto de conversão, arredondamento, fuso, aceleração do calendário e limites de avanço **permanece aberto**, assim como a forma de observar o relógio efetivo do BG2:EE. O plano deve empregar timestamps UTC e tratar relógio do sistema incorreto/retrocedido, restaurações de backups e divergência entre save do jogo e banco externo como condições de bloqueio/reconciliação, nunca como autorização para avanço negativo ou arbitrário.

## Fluxo candidato (não implementado)

```text
[Host encerra sessão] -> checkpoint confirmado (game time + UTC + revisão + política)
[Jogo desligado]      -> nenhum loop necessário
[Próxima sessão]
   -> validar identidade da campanha, save do host, checkpoint e relógio externo
   -> carregar política escolhida e calcular intervalo admissível
   -> aplicar limites e classificar regiões ACTIVE/NEAR/DISTANT/DORMANT
   -> gerar atualizações por regras determinísticas/seed em lotes
   -> avaliar canon, permissões, segredos e possíveis efeitos irreversíveis
   -> registrar somente fatos autorizados; manter demais propostas pendentes
   -> materializar no host apenas operações permitidas e confirmáveis
   -> atualizar cursor/revisão e publicar resumo para jogadores
```

**Importante:** este fluxo é um desenho de requisitos, não prova de integração entre EEex e multiplayer.

## Alternativas consideradas

- **A — Tempo apenas com jogo aberto:** menos risco, mas limita a evolução entre sessões.
- **B — Tempo real permanente:** maior continuidade, porém custo, prazos e mudanças irreversíveis potencialmente injustas.
- **C — Tempo híbrido e configurável:** **aprovada**; conserva liberdade do grupo com consumo previsível e proteções de continuidade.

## Garantias e limites

- Sem inferência LLM por NPC/frame ou por segundo de ausência; código e lotes primeiro, LLM local apenas quando um evento aberto justificar (DEC-014).
- Um evento potencial não vira fato confirmado por mera sugestão do modelo.
- Nenhuma modificação silenciosa no modo Original nem efeitos mecânicos sem evidência do host (DEC-011).
- Controle de causalidade/segredos por personagem e NPC (DEC-019), incluindo informação que não poderia ter circulado na ausência dos jogadores.
- Backstory editado não retroage em fatos confirmados sem autorização (DEC-020).
- Restauração de save anterior ou divergência de revisões não pode aplicar automaticamente um catch-up contra a linha temporal escolhida.

## Pendências explícitas (não aprovadas)

1. Configuração padrão de ausência, fatores de conversão, limites máximos de avanço de calendário e frequência de atualização.
2. Categorias exatas de eventos reversíveis, eventos que podem acontecer offline e quais exigem votação/consentimento ou presença dos jogadores (DEC-009).
3. Persistência técnica, formato de snapshots, transações, autoridade de mudanças narrativas e recuperação de falhas (DEC-008 / DEC-018).
4. Compatibilidade de leitura e materialização de relógio/eventos do BG2:EE via bridge e sincronização com outros clientes.
5. Tratamento de sessões interrompidas sem encerramento, relógio local alterado, mudança de host e política alterada no meio de uma ausência.

## Cenários candidatos de verificação

1. `FROZEN`: sete dias reais de ausência não fazem o `world_time` avançar por tempo real.
2. `PARTIAL`: período sem jogadores produz avanço conforme parâmetros versionados, dentro de limite configurado.
3. `REALTIME`: período real é base de cálculo, mas processamento mecânico não acontece enquanto o host está desligado; limites são respeitados na retomada.
4. Retorno duplicado ou dois clientes simultâneos produzem **uma** atualização temporal para a mesma revisão.
5. Retorno após longa ausência não gera milhares de chamadas LLM e respeita orçamento por região.
6. A IA propõe morte de NPC importante durante ausência; estado mantém `PENDING` até autorização aplicável, nunca marca morte como confirmada.
7. Tempo do sistema retrocede ou é inconsistente; catch-up é bloqueado para inspeção, sem tempo negativo.
8. Recuperação de save antigo com banco mais recente interrompe avanço, solicita reconciliação e preserva cópia segura dos dados.
9. Atualizações entre sessões não vazam histórico secreto aos NPCs sem cadeia causal verificável.
10. O modo Original permanece byte a byte intacto durante catch-up no Living World (verificado sobre cópia de teste).
11. O mesmo intervalo processado novamente com mesma revisão/seed não duplica fatos, inventário, encontros ou mudanças.
12. Queda no meio do catch-up conserva checkpoint consistente e permite retomada segura e idempotente.

**Status técnico:** regras de produto aprovadas, contratos e testes ainda candidatos; nenhuma integração ou teste real executado neste estágio.
