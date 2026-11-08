# SPEC-001 — Estados, erros, fallback e rollback

**Status:** contrato sintético implementado em `src/infinity_ai/bridge/`; **POC real P0–P4 NÃO EXECUTADA.**
Testes: `tests/test_bridge_spec001.py` (sintéticos; não contam como evidência de bridge, EEex ou multiplayer).

## Ordem de verificação (fail closed)

Toda requisição passa pelas etapas abaixo **antes** de qualquer leitura no adapter. A primeira que falhar define o resultado; nenhuma etapa posterior roda.

| # | Verificação | Falha → status / reason | REQ |
|---|---|---|---|
| 1 | Requisição é um objeto com `operation == "read"` exato | `BLOCKED_CAPABILITY` / `WRITE_FORBIDDEN` | REQ-BRIDGE-003 |
| 2 | Somente as chaves `operation`, `field`, `purpose`, `audience`; valores válidos | `BLOCKED_CAPABILITY` / `MALFORMED_REQUEST` | REQ-BRIDGE-003 |
| 3 | Sessão validada no `connect()` (campanha/branch, fingerprint, modpack, versão do adapter, epoch) | `BLOCKED_CAPABILITY` / `*_MISMATCH`, `SESSION_NOT_VALIDATED` ou `ADAPTER_UNAVAILABLE` | REQ-BRIDGE-001 |
| 4 | Campo presente na allowlist pinada para a build | `BLOCKED_CAPABILITY` / `FIELD_NOT_ALLOWLISTED` | REQ-BRIDGE-002 |
| 5 | Finalidade permitida para o campo | `DENIED` / `ACL_PURPOSE` | REQ-BRIDGE-004 |
| 6 | Audiência com acesso à visibilidade do campo (`SECRET` nunca é projetado) | `DENIED` / `ACL_AUDIENCE` | REQ-BRIDGE-004 |
| 7 | Leitura no adapter | exceção ou resposta inválida → `UNKNOWN` / `ADAPTER_UNAVAILABLE` | REQ-BRIDGE-005 |
| 8 | Epoch informado na leitura igual ao pinado | `BLOCKED_CAPABILITY` / `EPOCH_MISMATCH` e a sessão é fechada | REQ-BRIDGE-001 |
| 9 | Valor não vazio e com cobertura | `UNKNOWN` / `NOT_OBSERVED` | REQ-BRIDGE-002/005 |
| — | Tudo certo | `OBSERVED` / `NONE`, com valor, cobertura e proveniência | REQ-BRIDGE-002 |

## Significado dos estados

- `OBSERVED` — valor lido pelo adapter na sessão e epoch validados. Com `evidence: SYNTHETIC` é só fixture; somente `POC_VERIFIED` pode sustentar uma capability, e só após o gate correspondente.
- `UNKNOWN` — não há dado suficiente. **Nunca equivale a `false`, a "não aconteceu" ou a permissão.** Consumidores (memória NPC, diálogo, LLM) devem tratar como lacuna.
- `BLOCKED_CAPABILITY` — a operação não é suportada ou não foi comprovada para esta build/sessão. Inclui toda tentativa de escrita.
- `DENIED` — o dado pode existir, mas a finalidade ou a audiência não têm acesso. O valor não é lido do adapter.

Invariantes garantidos pelo tipo `ObservationEnvelope` e pelo schema `observation_envelope_v1`: só `OBSERVED` carrega valor; estados não observados exigem `reason` explícito e cobertura `NONE`.

## Fallback

- **Bridge ou adapter fora do ar:** `connect()` falha fechado; leituras retornam `BLOCKED_CAPABILITY`/`UNKNOWN`. O jogo continua normalmente, porque a bridge não escreve nada no host.
- **LLM fora do ar:** a bridge não depende de LLM (rascunho REQ-BRIDGE-006). Nenhum estado é inferido por modelo.
- **Save/load ou reconexão:** o epoch muda; a próxima leitura detecta a divergência, fecha a sessão e exige novo `connect()` com a identidade pinada atualizada pelo host.
- **Build ou modpack alterados:** nova coleta P0 (`tools/windows-lab/`) gera novo fingerprint; allowlist antiga não vale para a build nova.

## Rollback

Esta etapa não tem efeitos colaterais no jogo, então o rollback é de código: reverter o merge da PR remove `src/infinity_ai/bridge/`, os schemas e os testes, sem migração de dados. O stub anterior `src/infinity_ai/contracts.py` permanece intacto. Nas POCs reais, rollback de ambiente = descartar a cópia dedicada do jogo e o save descartável (ADR-0005 item 5).

## Fora do escopo desta etapa

Adapter EEex real, IPC, rede, dois clientes, escrita de qualquer tipo, mapeamento de campos reais do BG2:EE. Os nomes de campo nos testes (`host.current_area_id` etc.) são fixtures, não hooks comprovados.
