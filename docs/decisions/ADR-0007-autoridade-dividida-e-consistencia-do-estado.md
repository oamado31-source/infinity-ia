# ADR-0007 — Autoridade dividida e consistência entre motor, IA e persistência

- **DEC associada:** DEC-011
- **Estado:** **APROVADA — opção A (autoridade dividida por responsabilidade)**
- **Data de aprovação:** 2026-11-06
- **Domínio:** integração, estado mecânico, estado narrativo, multiplayer e persistência
- **Evidência:** escolha explícita do idealizador na conversa de Discovery.
- **Relacionamentos:** ADR-0001 (coop privado); ADR-0002/0003/0004 (Living World, histórico, segredos e revisões); ADR-0005/0006 (Windows, integração progressiva). DEC-008, DEC-012, DEC-014, DEC-015 e DEC-018 continuam abertas.

## Contexto

O Infinity AI orquestrará cenas, NPCs, missões e consequências sobre BG2:EE, aproveitando as mecânicas originais. Uma IA que decide criar criatura, entregar item ou completar missão não pode se tornar, só por gerar texto, a fonte de verdade do jogo. O host original, a bridge, os clientes e um armazenamento externo podem observar estados divergentes, sobretudo em multiplayer, latência, reinício ou desconexão. Não foi comprovada no projeto uma confirmação confiável de alterações BG2:EE/EEex que cubra todos esses casos.

## Decisão aprovada

1. **Autoridade mecânica:** o host/motor de BG2:EE é o dono do resultado de combate, atributos, movimentação, inventário, recursos de jogo, scripts e demais fatos mecânicos durante a sessão. Clientes não podem constituir uma segunda fonte autoritativa apenas por exibirem uma mudança.
2. **Autoridade narrativa externa:** o serviço Infinity AI mantém o registro autorizado dos históricos de personagem, ganchos, memórias, conhecimento individual, relações, intenções e consequências narrativas já confirmadas — sempre identificando campanha, modo (Original vs Living World), personagem e, quando aplicável, sessão e versão.
3. **IA não é autoridade de execução:** agentes geram **propostas estruturadas**, nunca confirmam por conta própria a aplicação de um item, spawn, recompensa, morte, comércio ou outra consequência mecânica.
4. **Bridge como fronteira de confiança:** controlador valida tipo de comando, pré-condições, permissões, alvo, limites e idempotência lógica; encaminha ao jogo apenas operações allowlisted. Modelos de IA jamais fornecem Lua arbitrário para execução direta.
5. **Confirmação antes do fato:** consequências narrativas dependentes do jogo só viram fatos confirmados após evidência de resultado efetivo obtida de uma integração compatível. Uma resposta de envio bem-sucedido **não** equivale necessariamente à confirmação da execução no host.
6. **Falha ou timeout:** mudança mecânica sem confirmação verificável assume estado **INCERTO / PENDENTE DE RECONCILIAÇÃO**. Não registrar sucesso, não presumir fracasso e não repetir cegamente comandos com efeitos colaterais. Consultar o estado real, correlacionar IDs e executar reconciliação antes de reenvio.
7. **Entrega repetida e divergências:** cada intenção recebe `event_id`, `command_id`, contexto de campanha/sessão e registro de tentativas. Sempre que o motor permitir, validar pré-condições e resultados para reduzir duplicação. **Exactly-once não é uma garantia assumida**, pois depende da bridge e das capacidades do jogo.
8. **Multiplayer:** testar a consistência entre host e pelo menos dois clientes, incluindo save/load e desconexão, antes de aprovar efeitos dinâmicos para coop. Nenhuma capacidade de sincronização foi ainda comprovada.
9. **Fronteiras de modo:** Living World e Original mantêm dados e saves separados; nenhum evento gerado pela IA deve alterar o progresso do modo Original sem SPEC e autorização específicos.
10. **Evolução futura:** contratos não deverão pressupor um banco global compartilhado nem comunicação direta de cada cliente com o LLM. A eventual migração para mundo persistente com múltiplos grupos exigirá nova decisão técnica.

## Ciclo conceitual de uma ação mecânica (proposta para implementação)

```text
NarrativeAgent -> ActionProposal
            -> PolicyValidator -> ActionIntent(PENDING)
            -> EngineBridge -> Host BG2:EE
                                  |
                                  +-> Evidence/Observation (when supported)
                                          |
                              Reconciler -> CONFIRMED / REJECTED / UNCERTAIN
                                          |
                                 NarrativeEvent (only if confirmed)
                                          |
                                   PersistentMemory
```

**A aprovação deste ADR fixa a responsabilidade e o princípio de confirmação; NÃO escolhe ainda o protocolo, banco, formato de eventos, nível de confiabilidade nem estado final de todos os comandos.** São tópicos de SPECS e POCs.

### Exemplo ilustrativo: mercador entrega um item

1. A IA propõe a entrega (o objeto continua somente em proposta).
2. O controlador confere sessão, mercador, inventário e comando permitido.
3. A bridge encaminha a ação com ID estável.
4. O motor altera o inventário; integração tenta coletar evidência observável.
5. Se verificado, o registro narrativo confirma a entrega; se incerto, preserva a operação em reconciliação e não realiza nova entrega automaticamente.
6. Um segundo cliente e um save recarregado devem refletir o resultado no gate multiplayer.

## Invariantes a converter em SPECS

- **INV-AUTH-001:** nenhuma resposta livre de LLM se torna fato mecânico confirmado.
- **INV-AUTH-002:** nenhuma recompensa/spawn é reenviada automaticamente após timeout com resultado desconhecido.
- **INV-AUTH-003:** evento narrativo dependente de mecânica referencia comando e evidência de execução, quando comprovadamente disponível.
- **INV-AUTH-004:** cliente não confirma sozinho transação ou estado mecânico; divergências são detectadas.
- **INV-AUTH-005:** as permissões e os dados de campanha/segredos do DEC-019 permanecem isolados nas consultas e respostas.
- **INV-AUTH-006:** saves, registros de eventos e resultados de teste podem ser associados por build/sessão sem modificar os saves do modo Original.

## Consequências

**Vantagens:** reutiliza o motor existente; facilita auditoria; diminui probabilidade de duplicação e de missões concluídas sem execução; mantém possibilidade de substituir a bridge ou a tecnologia de persistência.

**Custos:** exige identificadores, rastreabilidade, reconciliação, limites de comando e estados intermediários. Banco externo e jogo não terão transações ACID conjuntas nativamente. Parte dos efeitos talvez exija adaptação no motor ou seja inviável sob multiplayer.

## Alternativas descartadas nesta fase

- **B — Infinity AI controla também todo o estado mecânico:** demanda substituir boa parte da lógica do motor e introduz risco elevado de conflito com BG2:EE.
- **C — controle distribuído entre clientes e IA:** aumenta riscos de divergência, duplicação, fraudes e incoerência narrativa.

## Validação, bloqueios e revisões futuras

- **POC G2:** leitura da bridge (sem mutação), com logs, permissões e IDs.
- **POC G3:** ação reversível offline; testar confirmação, queda da bridge e repetição de requisição.
- **POC G4:** ação com dois clientes, estado após save/load, duplicação e perda de conexão.
- **Não avançar** como se houvesse confirmação quando a bridge apenas informa que um comando foi transmitido.
- **DEC-008:** quais fatos pertencem à persistência, e por quanto tempo.
- **DEC-012:** segurança de execução e privilégio da bridge.
- **DEC-014:** topologia dos agentes, papéis e autonomia dos NPCs (próxima discussão sugerida).
- **DEC-015 / DEC-018:** critérios mensuráveis de testes, telemetria, reconciliação e recuperação.

**Estado dos testes:** ainda não executados. Este documento registra uma decisão de arquitetura, não o resultado de implementação.
