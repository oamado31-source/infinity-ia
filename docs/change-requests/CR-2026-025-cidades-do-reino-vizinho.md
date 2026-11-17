# CR-2026-025 — Quem é de um reino conhece também as cidades do reino vizinho

**Status:** APPROVED (mantenedor, 2026-11-17: "Sim, ampliar")  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-17

## Motivo e contexto

A CR-2026-021 dá a quem é de um reino o núcleo popular do que é público no nível do reino vizinho: o próprio reino, seus eventos, lugares e costumes. As cidades do vizinho ficavam de fora.

No lote G (o Norte), isso deixou uma lacuna. Quem nasceu em Baldur's Gate conhecia "o Norte" e a Floresta Alta, mas não Águas Profundas, a maior cidade da região, que o jogo cita 171 vezes. No Norte, quase tudo o que importa são as cidades.

## DEC/ADR/SPEC/REQ afetados

- **CR-2026-021:** ampliada. A lista de vizinhos continua no manifesto, curada pelo mantenedor.
- **CR-2026-015:** a mesma ideia, das cidades irmãs, agora vale também para o reino vizinho.
- **CR-2026-017:** o conhecimento popular computado continua sem ser repassado por INQUIRY.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`memory/common_knowledge.py`, `identity_knowledge`:** quem é de um reino (morador ou nascido nele) recebe também o núcleo `POPULAR` das cidades, as regiões abaixo do reino vizinho. O que fica dentro dessas cidades continua de fora: organizações, lugares, tavernas.
2. **Efeito:**
   - quem é da Costa da Espada passa a conhecer Águas Profundas, Luskan e Inverno Remoto no nível popular;
   - um morador de Athkatla passa a conhecer Baldur's Gate, Beregost, Darromar, Zazesspur e Porto Calim;
   - os Lordes de Águas Profundas e o Punho Flamejante, que são de dentro das cidades, continuam de fora;
   - o vizinho do vizinho continua não contando.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Prompt:** as cidades de fora da cadeia da pessoa ficam no fim da fila (CR-2026-014) e só sobem quando a pergunta as nomeia (CR-2026-016). Por isso não tiram espaço das instituições de perto.
- **Compatibilidade:** sem `realm_neighbors`, nada muda.

## Migração e rollback

- **Migração:** novo pin da campanha. O pacote não muda por esta CR; ela entra junto com o lote G, que muda.
- **Rollback:** tirar a linha das cidades vizinhas em `identity_knowledge`.

## Testes

- **`tests/test_realm_neighbors.py`:** dois casos.
  - As cidades do vizinho entram no núcleo popular, mas não o que fica dentro delas (o Conselho dos Seis, a Coroa de Cobre, as Favelas).
  - Quem nasceu em Baldur's Gate conhece Águas Profundas, mas não os Lordes.
- **Testes ajustados:**
  - `test_identity`, posição social;
  - `test_sibling_cities`: o forasteiro de longe agora vem de Halruaa, porque Tethyr é vizinho de Amn;
  - `test_sword_coast`: Amn conhece as cidades da Costa, mas não o Punho Flamejante.
