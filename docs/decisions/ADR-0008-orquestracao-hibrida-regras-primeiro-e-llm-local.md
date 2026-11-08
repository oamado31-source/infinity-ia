# ADR-0008 — Orquestração híbrida: regras primeiro, IA local prioritária

- **Decisão associada:** DEC-014
- **Estado:** **APROVADA — opção C com adendos determinístico-first e LLM local-first**
- **Data de aprovação:** 2026-11-06
- **Domínio:** topologia dos agentes, execução de regras, custo/latência, segurança da inferência
- **Fundamentação:** escolha expressa do idealizador nesta conversa.
- **Relações:** DEC-011 / ADR-0007 (autoridade de estado), DEC-004 / ADR-0002 (históricos), DEC-019 / ADR-0003 (segredos); DEC-006 (política detalhada de modelos) e DEC-021 (autonomia temporal de NPCs) **em aberto**.

## Contexto

O Infinity AI pretende criar mundo dinâmico com grande número de NPCs e eventos, sem perder a leveza do cliente BG2:EE. Não é razoável convocar LLM a cada ataque, rotina, deslocamento, ataque de oportunidade, preço ou verificação de condições previamente definidas. Isto adicionaria latência, custo, não determinismo e risco de comportamentos incoerentes.

## Decisão aprovada

1. **Orquestrador central com módulos/agentes especializados** (NPC, narrativa/quest, mundo e encontros), com contratos distintos. No primeiro MVP esses papéis podem ser módulos do mesmo serviço e compartilhar **um único modelo local**; **não** é requisito ter processo, sessão ou LLM exclusivo para cada NPC.
2. **Regra fundamental: código primeiro.** Toda ação expressável satisfatoriamente por regras, tabelas de decisão, máquina de estados, árvore de comportamento, eventos e código determinístico deverá seguir esse caminho, sem acionar LLM. Os agentes só serão acionados quando houver necessidade real de geração, interpretação ou planejamento de caráter aberto.
3. Reações normais e combate (ex.: NPC atacado, fugir, pedir ajuda, defender-se, negociar, render-se) são selecionados pelo **motor de regras** de acordo com atributos e contexto: moral, alinhamento, facção, personalidade, ameaça, recursos, histórico, testemunhas e presença de guardas. A edição de regras de D&D e a fórmula exata de moral/CR continuam pendentes de DEC-005. **Alinhamento isoladamente não predetermina a reação.**
4. **Inferência local como padrão preferencial** quando um LLM for necessário e um modelo adequado estiver disponível. A chamada para API externa não será automática: modelo, privacidade, política de consentimento, fallback, custos e limites técnicos serão definidos em DEC-006 e nas SPECS. Sem LLM disponível, o jogo deverá continuar com regras, diálogos pré-gerados ou fallback planejado.
5. O **jogo/host** continua autoritativo para estado mecânico; **Infinity AI** mantém os fatos narrativos conforme DEC-011. Modelos, locais ou remotos, **não** executam Lua, SQL, sistema de arquivos ou comandos de engine livremente: produzem propostas estruturadas, validadas por esquema, permissão, estado, capacidade e bridge allowlisted.
6. Memória por personagem/NPC é **dado persistente e consultado sob demanda**, não uma sessão de LLM continuamente ativa. Eventual ativação pode ocorrer por interação relevante, missão ou planejamento agendado; rotinas triviais devem ser dirigidas por eventos/sistemas tradicionais.
7. A escolha **não implica** que modelos locais sejam gratuitos em termos de CPU/GPU, memória, eletricidade, energia ou qualidade. A viabilidade será medida no hardware real, sem pressupor placa gráfica dedicada. A IA pode executar fora da máquina cliente, conforme ADR-0005.
8. Observabilidade obrigatória: classificar decisões por origem (`RULE`, `LOCAL_LLM`, `REMOTE_LLM`, `FALLBACK`), registrar versão da regra/modelo, latência, custo estimado/uso e resultado de validação, sempre respeitando segredos da DEC-019.
9. Projetar limites: orçamento de inferência por sessão, timeout, fila, deduplicação, cache com invalidação, prioridades e degradação controlada; valores e políticas finais são SPECS futuras, não definidos aqui.

## Ordem de roteamento (conceitual, não código de produção)

```text
Evento do jogo
  -> normalizar + identificar contexto autorizado
  -> regra determinística aplicável?
       SIM: executar decisão regrada -> controlador/host -> confirmar efeito
       NÃO: há template/resultado em cache válido?
         SIM: reutilizar com validação
         NÃO: tarefa aberta justifica LLM?
           SIM: LLM local elegível -> proposta estruturada -> validar -> controlador/host
             indisponível/insuficiente: fallback seguro; remoto apenas sob política DEC-006
           NÃO: regra conservadora / nenhuma ação
  -> registrar somente efeitos confirmados no estado persistente
```

### Exemplo: NPC é atacado por um jogador

1. Evento `NPC_ATTACKED` traz atacante, vítima, dano confirmado, contexto da região e referências de sessão.
2. O código consulta se a vítima está viva, regras de hostilidade, moral, relação de força, facção, alinhamento, personalidade, recursos e presença de guardas.
3. Uma **tabela de decisão versionada** decide: defender-se, fugir, pedir ajuda, tentar rendição ou mudar para um comportamento de combate existente no motor.
4. Controlador solicita ação admitida ao host; em multiplayer, a aplicação/sincronização precisa ser comprovada na POC da bridge.
5. Se houver uma necessidade **narrativa aberta** (ex.: negociar depois da rendição ou gerar uma fala singular), pode-se convocar um LLM local **apenas para essa parte**, sob limites e política de conhecimento. O modelo não calcula dano, modifica inventário nem decide se o ataque ocorreu.

> Uma tabela com `if/elif`, máquina de estados ou árvore de comportamento são alternativas de implementação; esta ADR não fixa uma linguagem ou biblioteca específica para as regras.

## Benefícios e custos

- **Benefícios:** menor uso de tokens e latência; comportamento mecânico previsível; replays/testes mais reproduzíveis; serviço de IA menor; funcionamento degradado sem LLM; menos oportunidades de prompt injection; separação clara de fatos e propostas.
- **Custos:** precisa construir e manter regras e tabelas; comportamentos rígidos exigem boas exceções; classificação de tarefas e roteamento podem errar; modelos locais podem ter limitações de memória e qualidade; uma interação aberta pode exigir ferramentas de recuperação e síntese estruturada.

## Alternativas recusadas

- **A — Um agente único decide tudo:** mistura responsabilidades e chama inferência sem necessidade.
- **B — Agente autônomo por NPC:** custos e concorrência maiores, sem justificar execução contínua para personagens inativos.
- **Usar LLM para qualquer decisão de IA:** recusado expressamente; o requisito é *regras primeiro*, não *LLM primeiro*.

## Critérios candidatos para validação posterior

- Ataque comum contra NPC não causa chamada LLM e gera ação de regras rastreável.
- Repetir evento/estado com seed fixo produz a mesma decisão determinística (na camada sob nosso controle).
- Modelo local indisponível não trava exploração/combat; há fallback seguro, sem assumir sucesso de comando.
- NPCs diferentes não compartilham memória/segredos sem evento de descoberta autorizado.
- LLM retornando comando não permitido não provoca execução no EEex/bridge.
- Sessão com múltiplos NPCs ociosos não gera chamadas periódicas desnecessárias ao modelo.
- Medir uso de tokens/inferência, latência e consumo de RAM/CPU/GPU antes de definir orçamento.
- Nenhum evento narrativo dependente de efeito mecânico vira fato confirmado sem evidência do host (ADR-0007).

## Questões não resolvidas

- **DEC-006:** ferramentas locais, tamanho/quantização e requisitos de hardware, limite de tokens/custo por sessão, condições de uso remoto e consentimentos.
- **DEC-021:** em que condições NPCs e regiões distantes da party evoluem sem interação dos jogadores.
- **DEC-005:** formulação de moral, facções, alinhamento, combate e edição de regras.
- **DEC-008/012/015:** persistência, autorização, observabilidade e gates de latência/multiplayer.

**Status:** escolha arquitetural aprovada, mas nenhum agente, modelo ou integração foi implementado ou validado localmente.
