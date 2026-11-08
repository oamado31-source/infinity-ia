# ADR-0001 — Multijogador cooperativo como primeiro marco

- **Decisão relacionada:** DEC-001
- **Estado:** APROVADA
- **Data:** 2026-11-05
- **Responsável pela decisão:** idealizador do projeto
- **Registro:** escolha explícita da **opção C** na conversa de discovery.

## Contexto

O Infinity AI pretende aproveitar recursos da Infinity Engine em uma experiência multiplayer com NPCs, eventos e conteúdo dinâmicos por IA. O objetivo de longo prazo admite mundo persistente compartilhado por vários grupos, mas a base candidata BG2:EE oferece originalmente multiplayer cooperativo centrado em um grupo. Não está comprovado que EEex/EET/adaptações forneçam sincronização confiável de comandos gerados por IA para grupos simultâneos.

## Alternativas consideradas

- **A — Coop privado apenas:** menor escopo, mas não explicita a evolução desejada.
- **B — Mundo compartilhado desde o início:** ampla complexidade de servidores, consistência, múltiplos grupos e escalabilidade, sem prova de viabilidade sobre BG2:EE.
- **C — Coop privado primeiro, projetar contratos para evolução futura:** opção selecionada.

## Decisão

**Aprovar a opção C:**

1. O primeiro marco jogável atenderá uma **sessão privada cooperativa** com participantes humanos controlando seus personagens, com IA atuando sobre NPCs e eventos autorizados.
2. O estado dessa campanha deve **persistir entre sessões** e ser coerente entre participantes da mesma sessão.
3. As SPECS arquiteturais futuras devem **separar**: identidade de personagens/jogadores, mundo/campanha, estado persistente, regras e integração com o motor.
4. Não presumir que os recursos de multiplayer do BG2:EE suportam vários grupos independentes nem que um serviço externo possa sincronizar qualquer evento sem testes.
5. A futura fase de **mundo compartilhado entre grupos** é um objetivo de evolução, não um requisito do primeiro MVP nem uma capacidade comprovada do motor.

## Consequências e guardrails de design

- Criar interfaces de estado do mundo e eventos que possam ser substituídas por implementação diferente no futuro; evitar espalhar dependências diretas de savegame/EEex por agentes de IA.
- Na fase 1, definir o host/sessão como autoridade **a confirmar tecnicamente**; nenhuma escrita direta de estado por modelos generativos sem validação, registro e idempotência apropriada.
- Propor identificadores e limites explícitos para mundo, campanha/sessão, personagem e NPC nas SPECS de persistência.
- Adotar um ciclo obrigatório de testes de sincronização em **dois clientes** antes de declarar eventos dinâmicos multiplayer como funcionais.
- Não introduzir sistemas de shard, economia multigrupos, PvP massivo, centenas de jogadores ou servidores distribuídos no primeiro marco.
- Se os testes de sincronização do BG2:EE falharem, reavaliar a ponte ou motor sem alterar a intenção de produto da decisão.

## Critérios de saída para fase 1 (propostos; ainda não SPECS aprovadas)

- Dois jogadores participam de uma sessão cooperativa e observam o mesmo estado após evento validado pelo host.
- Um fato de NPC persiste após fechar e reabrir a campanha sem alterar saves de maneira inválida.
- Repetir um mesmo comando de geração de evento não duplica entidades ou recompensas.
- Com falha do serviço de IA, os clientes mantêm jogo e saves íntegros.

## Hipóteses a validar

- Compatibilidade de BG2:EE + EEex + Remote Console + multiplayer; não demonstrada.
- Compatibilidade incremental de EET + mapas de IWD + NWNForBG; requer matriz de versões e testes de regressão.
- Possibilidade de evolução para grupos independentes sem troca de motor: **não presumida**.

## Decisões pendentes associadas

- DEC-004: campanha original versus modo livre (próxima rodada de discovery).
- DEC-002/DEC-003: plataforma, versão do motor e estratégia de instalação de mods.
- DEC-008/DEC-011: persistência e autoridade do estado.

## Relação com features futuras

A partir deste ADR, poderão ser especificadas features como sessão privada, bridge de eventos segura, estado persistente de campanha, sincronização host-cliente e memória de NPCs. Nenhuma dessas features é declarada implementada ou aprovada neste momento.
