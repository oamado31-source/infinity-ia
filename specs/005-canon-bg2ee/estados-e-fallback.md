# SPEC-005 — Estados, fontes, limites e rollback (etapa 1)

**Status:** infraestrutura implementada (`src/infinity_ai/gamedata/`, `src/infinity_ai/canon/`); inventário real extraído no laboratório; **primeiro lote de curadoria conferido** (6 entradas; ano da campanha = 1369 DR por decisão do mantenedor).

## Duas fontes S0, dois destinos

| Fonte | O que dá | Onde fica |
|---|---|---|
| Instalação do jogo (KEY/BIFF/WMP/TLK) | áreas existentes na build e nomes exibidos no mapa-múndi, no idioma do jogo | `~/.infinity-ai/knowledge/install-<fingerprint>/areas.<idioma>.json` — **fora do repo** |
| Livros do mantenedor | fatos de 1369 DR com obra e página | `knowledge/periods/1369-DR/` — resumo nosso + referência |

Inventário: só leitura; leitura remota no laboratório traz fatias para a memória, sem salvar arquivos do jogo; nome só vem do mapa-múndi (área fora dele fica sem nome, sem adivinhar). Novo `build_fingerprint` → inventário novo (o antigo não é usado).

## Gate (REQ-CANON-001/002)

| Status | Quando |
|---|---|
| `CANON_OK` | ano da campanha = partição e dentro da validade; região com ≥ 1 área na build; entrada `SOURCE_CHECKED`/`CAMPAIGN_CANON`; todas as fontes S0/S1 |
| `UNKNOWN` | entrada ou região ausente; inventário indisponível |
| `WRONG_YEAR` | partição ou validade não cobre o ano da campanha |
| `UNMAPPED_REGION` | nenhuma área da região existe na build (não materializar consequências) |
| `WEAK_SOURCE` | `RESEARCH_ONLY`/`CROSS_REFERENCED`/`DISPUTED`, fonte S2/S3, ou obra ambientada em outro ano sem validade explícita (ex.: FR3e, 1372 DR) |

## Pin por campanha (ADR-0058)

`KnowledgePackPinned` (`CAMPAIGN_FACT`) grava ano e revisão (hash do conteúdo publicado). `check_pin` → `MATCH`, `NOT_PINNED` ou `REVISION_CHANGED`; nada se atualiza sozinho.

## Uso no diálogo

Só nomes de área: jogo (S0) → curadoria provisória → "um lugar que você não sabe nomear". Fatos canônicos só entram no prompt de um NPC que os adquiriu por um canal do ADR-0114 (conhecimento comum regional, `access_scope = COMMON_REGIONAL`). Cada aquisição exige pin `MATCH` e gate `CANON_OK` e guarda um instantâneo do resumo; corrigir o pacote ou fazer novo pin não altera o que já foi aprendido. Estados e falhas: `specs/003-persistencia-memoria/estados-e-fallback.md`.

## Fora desta parte

REQ-CANON-003 (eventos pessoais N1/N2) e a segunda região (ADR-0109 item 3) ficam para depois do inventário de mapas e da curadoria.

## Rollback

Código: reverter a PR. Dados do jogo: apagar `~/.infinity-ai/knowledge/install-*`. Cânone: entradas são arquivos versionados; revisões antigas continuam reproduzíveis pelo pin.
