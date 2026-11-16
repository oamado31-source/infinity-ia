# CR-2026-021 — Quem é de um reino conhece o núcleo popular do reino vizinho

**Status:** APPROVED (mantenedor, 2026-11-16: opção "(b) + (c)" do lote E)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-16

## Motivo e contexto

Pela regra atual (ADR-0117, CR-2026-012 e CR-2026-015), uma região só é conhecida:
- por quem nasceu nela;
- por quem mora nela;
- por quem esteve nela (o núcleo popular, pela viagem);
- pelos irmãos do mesmo reino.

Por isso, um NPC de Athkatla não sabe nem que Tethyr ou a Costa da Espada existem, embora sejam vizinhos de Amn e o jogo os cite o tempo todo (Tethyr 99 vezes, Costa da Espada 91, Calimshan 89).

Na conferência do lote E, o mantenedor escolheu duas mudanças:
- **(b)** vizinhos conhecem o núcleo popular uns dos outros (esta CR);
- **(c)** um tópico no nível de Faerûn com a fama das terras distantes. É conteúdo, não código, e entra no lote E.

## DEC/ADR/SPEC/REQ afetados

- **ADR-0117 e CR-2026-015:** ganham mais um caminho de conhecimento comum. Ele é computado na hora e não é gravado, como os outros.
- **CR-2026-017:** o conhecimento popular computado continua sem ser repassado por INQUIRY.
- **REQ-REL-012:** a lista de vizinhos faz parte da revisão do pacote. Mudá-la exige um novo pin.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`knowledge/periods/1369-DR/manifest.json`:** campo novo `realm_neighbors`, uma lista de pares de reinos curada pelo mantenedor. Primeiros pares: Amn–Tethyr e Amn–Costa da Espada. O lote E acrescenta os pares de Calimshan.
2. **`canon/pack.py`:**
   - `CanonPack.neighbors` é um mapa simétrico entre os reinos;
   - o carregador recusa pares que não sejam reinos, isto é, `REGION` logo abaixo de `region:faerun`;
   - quando existem, os pares entram na revisão do pacote.
3. **`memory/common_knowledge.py`, `identity_knowledge`:** quem é de um reino (morador ou nascido nele) recebe o núcleo `POPULAR` do que é público no nível do reino vizinho:
   - o próprio reino;
   - seus eventos, lugares e costumes.

   Não recebe as cidades nem o que está dentro delas. O vizinho do vizinho não conta.
4. **Efeito:**
   - um morador de Athkatla passa a saber o núcleo popular de Tethyr (a guerra acabou, há monarcas de novo, a Cavaleira Vermelha) e da Costa da Espada (a Fortaleza da Vela, o Braço Amigo, Dragonspear, a trama de Sarevok);
   - Bernard, de Tethyr e morando em Amn, também recebe a Costa, vizinha de Amn;
   - um forasteiro de Tethyr recebe o núcleo popular de Amn.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Prompt mais cheio:** os itens novos são populares e ficam na cauda do atlas (CR-2026-014). Só sobem quando a pergunta os nomeia (CR-2026-016).
- **Curadoria:** a lista de vizinhos é decisão do mantenedor. Não é geografia automática.
- **Compatibilidade:** sem `realm_neighbors`, nada muda.

## Migração e rollback

- **Migração:** novo pin da campanha. No laboratório, `pin_canon_pack.py`; depois, o `--carry-pin` leva o pin aos ramos novos.
- **Rollback:** tirar `realm_neighbors` do manifesto.

## Testes

`tests/test_realm_neighbors.py` cobre sete casos:
- os pares são simétricos;
- só reinos podem ser vizinhos;
- os pares entram na revisão;
- o vizinho dá só o núcleo popular;
- as cidades do vizinho não entram;
- o vizinho do vizinho não conta;
- sem pares, nada muda.

Também foram ajustados os testes:
- de posição social (`test_identity`);
- de tópico (`test_topic`);
- da Costa da Espada (`test_sword_coast`);
- de viagem (`test_world_root`), que agora isola a regra da viagem sem vizinhos.
