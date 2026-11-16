# CR-2026-020 — Pin levado ao ramo aberto por um save antigo

**Status:** APPROVED (mantenedor, 2026-11-16: "Sim, propor CR")  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-16

## Motivo e contexto

No laboratório, carregar um save antigo abre um ramo novo da campanha (SPEC-003). O ramo herda o pin do momento do save, e não o pin mais recente. O pacote de conhecimento fica desligado nesse ramo até um novo pin manual (REQ-REL-012). O serviço só avisa no log (`AVISO`, CR-2026-017).

Isso aconteceu três vezes nos testes reais. Na última (2026-11-16), as perguntas a Bernard e a Unger, depois dos lotes D e C2, foram todas respondidas sem a enciclopédia:
- os ramos `br-20184c5c981e` e `br-8c55e05ecb4d` nasceram com a revisão anterior aos lotes;
- o aviso saiu no log, mas ninguém o viu a tempo.

## DEC/ADR/SPEC/REQ afetados

- **ADR-0058, item 6:** a adoção de uma revisão continua dependendo de aprovação explícita. A automação é permitida "somente por política pré-autorizada, limitada, auditável e comprovada por testes". Esta CR é essa política, limitada ao caso abaixo.
- **REQ-REL-012:** continua valendo. Uma revisão que o mantenedor nunca pinou não chega a nenhum ramo sozinha.
- **CR-2026-017:** o `AVISO` continua. Agora ele só aparece quando a revisão nunca foi pinada na campanha (ou com o serviço sem `--carry-pin`).
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`state/store.py`:** `campaign_events(event_type)`, os eventos de um tipo em qualquer ramo da campanha. É só leitura.
2. **`canon/pin.py`:**
   - **`approved_pin(store, pack)`:** o último pin **manual** desta mesma revisão em qualquer ramo da campanha. Um pin levado nunca aprova outro.
   - **`carry_pin(store, branch_id, pack, game_time=...)`:** só age quando o ramo não está em `MATCH` e existe um pin aprovado. Nesse caso grava um `KnowledgePackPinned` no ramo com:
     - a mesma revisão;
     - a evidência do pin de origem;
     - o tempo de jogo atual, que é a âncora da ADR-0114;
     - `carried_from` = o id do pin manual.
   - **`pin_pack`:** se o ramo já tem esta revisão, devolve o pin existente. Antes, um pin manual depois de um levado dava `IdempotencyConflict`.
3. **`tools/windows-lab/dialogue_service.py`:**
   - opção nova `--carry-pin`, desligada por padrão e ligada no comando do laboratório;
   - a cada observação, antes de adquirir conhecimento, o serviço chama `carry_pin`;
   - quando um pin é levado, o log registra: `pin levado ao ramo <ramo>: revisao ..., aprovada no pin <id> do ramo <ramo>`.
4. **Efeito:** depois de carregar um save, o ramo novo passa a usar a revisão que o mantenedor já aprovou nesta campanha, sem pin manual.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Critério 11 do ADR-0058** ("restauração para save anterior reconstitui pack e branch corretos"): o save é anterior à revisão, mas o serviço só carrega o pacote atual. Por isso a escolha real é entre ficar sem conhecimento ou usar a revisão já aprovada. A regra fica restrita à mesma campanha e ao mesmo ano DR, e a uma revisão pinada à mão.
- **Auditoria:** cada pin levado diz de qual pin manual veio (`carried_from`) e sai no log.
- **Escopo:** é uma ferramenta do laboratório. Fora do laboratório, nada muda sem `--carry-pin`.
- **Dados privados:** nenhum.

## Migração e rollback

- **Migração:** nenhuma. Os eventos novos usam o tipo e as colunas que já existem.
- **Rollback:** tirar `--carry-pin` do comando do serviço. Os pins já levados ficam registrados, como qualquer pin.

## Testes

`tests/test_carry_pin.py` cobre seis casos:
- o save antigo abre um ramo com o pin velho;
- o ramo recebe a revisão pinada à mão, e um segundo pedido não faz nada;
- uma revisão nunca pinada continua desligada;
- um pin levado não aprova outro;
- um ramo em `MATCH` fica intocado;
- um pin manual depois de um levado é idempotente.
