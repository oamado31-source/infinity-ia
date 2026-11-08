# ADR-0113 — Single player primeiro; multiplayer cooperativo como segunda etapa

**Estado:** APROVADA (decisão explícita do mantenedor, 2026-11-08).
**Origem:** redirecionamento do desenvolvimento após os gates P0–P2 no laboratório (CR-2026-001); CR-2026-003.
**Substitui parcialmente (sem editar):** ADR-0001, decisão item 1 (ordem do primeiro marco); ADR-0108, itens 1, 2 e 5 (ordem do primeiro vertical slice e critério "dois clientes" para a primeira entrega).
**Gate:** decisão de ordem e escopo; não comprova capability nova no BG2:EE/EEex.

## Contexto

O ADR-0001 fez do coop privado o primeiro marco jogável, e o ADR-0108 colocou o gate P4 (host + 2 clientes) logo depois da bridge read-only. Até 2026-11-08 o projeto aprovou P0, P1 e P2 no laboratório Windows 11 ARM64 (CR-2026-001), com observação real de área e tempo de jogo pelo probe EEex.

Ao preparar o P4 surgiram custos e riscos que não ajudam a validar o núcleo do produto (memória de NPC, diálogo contextual, persistência): segunda licença do jogo e do Windows, VMs simultâneas sem rede real e, principalmente, a declaração do autor do EEex (issue Bubb13/EEex#37, maio de 2025) de que o EEex "most likely never" suportará multiplayer para mudanças que não sejam só do cliente. O mantenedor decidiu implementar e testar tudo primeiro em single player e integrar o multiplayer depois.

## Alternativas consideradas

- **A — Manter a ordem do ADR-0108** (P4 antes de memória e diálogo): valida sincronização cedo, mas trava o núcleo narrativo atrás de licenças, VMs e de uma limitação upstream do EEex.
- **B — Single player primeiro, multiplayer na etapa 2:** **selecionada.** Entrega um ciclo jogável completo cedo, com menos variáveis, e mantém os contratos prontos para o coop.
- **C — Abandonar o multiplayer:** contraria a intenção de produto do ADR-0001; rejeitada.

## Decisão e responsável

Responsável: mantenedor do projeto, em 2026-11-08.

1. **Etapa 1 — single player.** O primeiro marco jogável é uma campanha single player em BG2:EE com: bridge read-only (SPEC-001), persistência e memória de NPC (SPEC-003), diálogo em overlay de texto (SPEC-004, voz depois da UI de texto) e canon curado (SPEC-005). Implementação e testes reais acontecem em single player.
2. **Critério de entrega da etapa 1:** observação segura, memória de NPC persistente, save/load com épocas coerentes, auditoria e zero efeito não autorizado, **numa instância single player**. O critério "dois clientes" do ADR-0108 item 5 passa a valer para a etapa 2.
3. **Etapa 2 — multiplayer cooperativo.** SPEC-002 e gate P4 (P4a anfitrião + 1, P4b anfitrião + 2, conforme CR-2026-002 quando aprovado) ficam para depois da etapa 1. A intenção de produto do ADR-0001 (coop privado persistente) continua valendo; só a ordem muda.
4. **Contratos prontos para o coop.** Nenhum atalho de single player pode remover dos contratos a autoridade do host, a identidade e a propriedade do PC, `campaign_id`/`branch_id`/`host_epoch`, consentimento e receipts. Em single player o jogo local é o host e o único PC pertence ao jogador; os caminhos de verificação continuam existindo e testados.
5. **P3 em single player.** A mutação reversível em save descartável (P3), opcional e sempre isolada, pode ser explorada em single player, onde o EEex é suportado; continua não sendo requisito para ler ou conversar.
6. **Evidência:** as evidências da etapa 1 dizem explicitamente "single player"; nenhuma delas pode ser citada como prova de multiplayer (Constitution item 10).

## Consequências

- Roadmap reordenado: SPEC-001 → SPEC-003 → SPEC-004 → SPEC-005 em single player; depois SPEC-002 e P4.
- O trabalho já iniciado do P4a (scripts de laboratório, comparação de pares, sessão P4 e CR-2026-002) fica guardado para a etapa 2; scripts de instalação reaproveitáveis podem entrar antes, em PR própria.
- Riscos de sincronização multiplayer são descobertos mais tarde; a etapa 2 pode exigir outro caminho para ações mecânicas compartilhadas (ADR-0001: "se os testes de sincronização falharem, reavaliar a ponte ou motor").
- Toda funcionalidade da etapa 1 deve declarar como se comportará com mais de um PC, mesmo que o teste real seja só single player.

## Contratos e SPECs vinculadas

SPEC-001 (concluída no laboratório até P2), SPEC-003, SPEC-004, SPEC-005 na etapa 1; SPEC-002 na etapa 2. `docs/architecture/roadmap.md` e `docs/architecture/testing.md` refletem a nova ordem.

## Evidências, riscos e hipóteses não verificadas

- Evidências de partida: `docs/evidence/P0-…`, `P1-…`, `P2-2026-11-08-laboratorio-arm64.md` (single player, laboratório ARM64).
- Hipótese não verificada: os contratos de autoridade e consentimento desenhados para coop funcionam sem retrabalho quando a etapa 2 começar; mitigada pelo item 4.
- Risco: limitação do EEex em multiplayer pode inviabilizar efeitos mecânicos compartilhados via EEex; não afeta a etapa 1.
