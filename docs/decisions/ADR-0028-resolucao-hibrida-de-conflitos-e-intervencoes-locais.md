# ADR-0028 — Resolução híbrida de conflitos e encontros locais

- **Decisão:** DEC-033
- **Estado:** **APROVADA — opção B**
- **Data:** 2026-11-06
- **Domínio:** conflitos militares, simulação estratégica, participação opcional dos jogadores
- **Referências:** DEC-032, DEC-021, DEC-022, DEC-005-E, DEC-009, DEC-011, DEC-012, DEC-027; ADR-0027.

## Contexto

A DEC-031 criou a arquitetura de facções autônomas, inclusive organizações canônicas não presentes nos jogos. A DEC-032 adotou uma simulação político-econômico-militar hierárquica por relevância. Faltava decidir como traduzir seus conflitos em oportunidades jogáveis, sem exigir enormes exércitos simulados no BG2:EE e sem transformar o RPG em um jogo de estratégia.

## Decisão aprovada — opção B

1. **Conflitos distantes:** resolver em escala estratégica agregada, por regras e recursos limitados. Não instanciar fisicamente tropas nem executar combate no BG2:EE para cada batalha distante.
2. **Conflitos próximos:** quando relevantes, transformar partes de conflitos em patrulhas, emboscadas, escoltas, defesa, reconhecimento, sabotagem, negociação ou combates locais **opcionais**, usando recursos efetivamente disponíveis e compatíveis com a instalação.
3. **Livre participação:** jogadores podem interferir ou ignorar oportunidades, e as forças continuam evoluindo conforme o relógio da campanha e o tier de atividade. Nenhuma missão militar será mandatória por esta decisão.
4. **Consequência proporcional:** o resultado confirmado de um encontro pode alterar a parcela militar e social correspondente; derrotar uma patrulha não equivale a conquistar uma cidade ou terminar a guerra inteira.
5. **Autoridade diferenciada:** o simulador pode registrar um **resultado estratégico externo autorizado**; esse registro **não é recibo mecânico do host**. Dano, morte, itens, objetos, movimentação física e outros efeitos efetivos no jogo exigem confirmação do BG2:EE pelo Action Gateway/bridge e host (DEC-011/012).
6. **Proteção histórica e riscos:** guerras canônicas, quedas de cidades, mortes de figuras históricas e demais consequências irreversíveis relevantes classificadas como `HIGH` continuam **bloqueadas até política especial de autorização**; a opção B não autoriza autoresolver eventos históricos críticos (DEC-009/027).
7. **Consistência:** preservar identidade de subinstância, exclusão de resolução concorrente, idempotência, seeds, checkpoints e replay. Não resolver a mesma unidade/combate simultaneamente pela camada estratégica e local.
8. **Performance e compatibilidade:** simulação externa por regras e lotes; LLM apenas sob demanda narrativa. O sistema respeita ACTIVE/NEAR/DISTANT/DORMANT, FROZEN/PARTIAL/REALTIME e o modo Original. Turnos individuais opcionais (DEC-005-T) **não são pré-requisito** para este desenho e permanecem bloqueados por POCs.

## Matriz de responsabilidades

| Caso | Fonte do fato / autorização | Limite |
|---|---|---|
| Batalha distante resolvida | Simulador estratégico + cânone + política de risco | Sem declarar combate físico executado no host |
| Jogadores enfrentam patrulha | Gateway + BG2:EE/host confirmando o resultado | Sem inventar dano, mortes ou recompensas |
| Notícias sobre guerra | Sistema de conhecimento / rumores com proveniência | Relato falso não altera verdade canônica |
| Morte histórica ou queda de capital | Política específica `HIGH`, ainda não decidida | Bloqueio preventivo até autorização |

## Cenário ilustrativo

Bandidos atacam uma rota comercial. Longe dos jogadores, a simulação pode calcular pressão militar e desabastecimento por regras autorizadas; perto deles, pode surgir uma escolta opcional. A defesa da caravana, se confirmada pelo host, melhora o estado daquela rota ou expedição, sem eliminar automaticamente toda a facção inimiga.

## Consequências

**Positivas:** conflitos dinâmicos em Forgotten Realms com custo controlado, integração coerente ao RPG e missões opcionais; separação macro/micro. **Desafios:** conciliar resultado estratégico com encontros locais, limitar a escala de mudanças e validar a bridge/multiplayer.

## Critérios e POCs candidatos

- Simular confronto distante sem abrir o mapa ou produzir recibo mecânico falso.
- Gerar encontro local opcional somente com recursos presentes e quando for historicamente plausível.
- Confirmar ações locais exclusivamente pelo host; converter seu impacto em mudança estratégica limitada.
- Bloquear dupla resolução da mesma unidade enquanto existe combate local pendente.
- Não aplicar guerra canônica, morte importante ou destruição histórica `HIGH` sem política especial.
- Salvar, restaurar e reconectar dois clientes sem duplicar perdas, spawns ou recompensas.
- Continuar funcionando com RTwP, sem turnos opcionais implementados.
- Preservar o modo Original e o isolamento por campanha.

**Status técnico:** arquitetura aprovada, **não implementada nem validada em BG2:EE/EEex/multiplayer**. Fórmulas, proporções, limites e riscos específicos ainda exigem SPECS e testes.

**Próxima decisão sugerida:** DEC-034 — autorização dos eventos de alto impacto / irreversíveis.
