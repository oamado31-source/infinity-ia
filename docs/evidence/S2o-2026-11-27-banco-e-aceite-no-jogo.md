# Evidência S2o — CR-2026-036: o banco e o aceite da oferta certa, no jogo (2026-11-27)

**Gate:** etapa 1, single player, save descartável, Coroa de Cobre (AR0406).
**Resultado:** **aprovado no laboratório ARM64/VM.**

**Executado por:** mantenedor, no jogo (cópia `BG2EE-P1`, campanha `lab-s1f`), e Claude Code.

**Preparação:**
- os três arquivos da CR foram copiados para o checkout do laboratório e conferidos byte a byte;
- o serviço foi reiniciado com uma quest local de teste (`teste-aceite`, fora do repositório): Bernard oferece "o navio" e aceita com as mesmas palavras comuns do broche ("sim", "aceito", "pode deixar").

## O que passou

| # | Ponto | Log | No jogo |
|---|---|---|---|
| 1 | O banco abre em WAL | `PRAGMA journal_mode` → `wal`; arquivos `-wal` e `-shm` ao lado do banco | — |
| 2 | Duas ofertas do mesmo NPC | `bernard-brooch=OFERECIDA` (deste save) e `teste-aceite:NarrativeQuestOffered` | "Tem trabalho para nós?" e "E sobre o navio nas Docas?" |
| 3 | Um "sim" aceita só a oferta em foco | `teste-aceite:NarrativeQuestAccepted`; `bernard-brooch=OFERECIDA` continua | "Sim, aceito": Bernard prepara o barco; diário do navio |
| 4 | Nenhuma trava do banco | nenhum `OperationalError` na sessão | — |

Antes da CR, "aceito" aceitava as duas ofertas (evidência S2m).

## O que apareceu no caminho (fora desta CR)

1. **A memória de Bernard vale entre saves.**
   - Neste save o broche estava só oferecido, mas Bernard disse "já resolvemos o problema do broche".
   - Ele tinha 4 lembranças (`lembra=4`) de conversas de saves anteriores, em que o broche foi resolvido, e o modelo seguiu a lembrança.
   - **Achado:** a memória das conversas do NPC parece não respeitar a linha do save. Fica para investigar à parte.
2. **O fato da oferta repetido com a instrução.**
   - O modelo local repetiu o fato da oferta da quest de teste com "Pergunte se o grupo aceita." no fim.
   - O texto é da quest local de teste, não de uma quest do repositório.
   - A skill de autoria já pede esse fecho como desejo do NPC, mas o modelo pode repeti-lo literalmente.
   - Fica anotado para a montagem da quest dos reféns.

## Verificação do ramo

- A suíte passa inteira (762 testes, com `lupa` e `jsonschema`), e `pyflakes` não dá avisos.
- `check_historical_adrs` e `check_public_files` passam.
- **Testes novos:**
  - em `tests/test_state_store.py`: WAL, leitura sem travar gravação, gravação que espera;
  - em `tests/test_narrative_quests.py`: duas ofertas e o foco.
