# CR-2026-030 — Enciclopédia: registro curado no repositório, catálogo extraído local

**Status:** APPROVED (mantenedor, 2026-11-18: "Aprovar como proposta", fase 1 da SPEC-012, decisões D1 a D4 na primeira opção)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-18

## Motivo e contexto

A SPEC-012 (seções 6 e 7.2) propõe guardar no repositório identificadores, metadados factuais e atributos estruturados extraídos dos jogos. A regra atual mantém o que sai dos arquivos do jogo em inventários locais, fora do repositório (REQ-CANON-004; ADR-0132; SPEC-008). A nota 1 do registro da SPEC-012 pediu esta CR antes de qualquer implementação.

## DEC/ADR/SPEC/REQ afetados

- **SPEC-012:** fase 1 (fundação) e o primeiro corte da fase 2 (o censo dos personagens do BG2:EE).
- **REQ-CANON-004:** continua valendo. Esta CR diz como ele se aplica à enciclopédia.
- **ADR-0132 e SPEC-008:** os inventários locais de áreas, habitantes e lojas seguem iguais.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **Duas camadas:**

   | Camada | Onde | O que guarda |
   |---|---|---|
   | Catálogo extraído | local, `~/.infinity-ai/encyclopedia/install-<build>/` | o que sai dos arquivos: atributos, níveis, propriedades, aparições por área, horários, posições e nomes do `dialog.tlk`; gerado de novo por ferramenta, de forma idempotente |
   | Registro curado | repositório, `knowledge/encyclopedia/` | identidade estável, nome, categoria, jogo e expansão, resref só como referência, resumo próprio (até 280 caracteres), relações, fontes, estado de validação e curadoria |

2. **O resref é uma referência:** um registro curado pode citar o resref do recurso, como as fichas da etapa 3 já citam no localizador. Atributos numéricos e textos do jogo não entram no repositório. O teste recusa um registro curado com campo de atributo extraído.
3. **No repositório:** os esquemas (`knowledge/encyclopedia/schemas/`), o manifesto, o registro de fontes, as ferramentas e os registros curados.
4. **Fontes comunitárias** (TH.GL, Planet Baldur's Gate, GameBanshee, NWN Vault e NWN Wiki): só registro (URL, data, escopo e termos a confirmar) e conferência manual nesta fase. Nada de raspagem automática nem cópia de texto.
5. **Missões originais** em `knowledge/encyclopedia/quests/`, separadas das quests do projeto (`knowledge/quests/`, SPEC-011). Ramificações e desfechos seguem a proteção contra spoilers da ADR-0095.
6. **Nada é movido:** as fichas curadas (`knowledge/npcs/`) e o pacote de cânone continuam sendo a fonte da identidade e do conhecimento. O registro da enciclopédia aponta para eles.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Direitos:** o repositório guarda só fatos curtos e referências, com resumo próprio. O catálogo extraído, que repete dados do jogo, fica na máquina do mantenedor.
- **Spoilers:** os registros de missões originais não podem levar ramificações ou desfechos para prompts nem logs (ADR-0095).
- **Compatibilidade:** nenhum consumidor atual muda. A enciclopédia ainda não alimenta o diálogo.

## Migração e rollback

- **Migração:** nenhuma. São diretórios novos.
- **Rollback:** apagar `knowledge/encyclopedia/` e o catálogo local.

## Testes

- **`tests/test_encyclopedia.py`:**
  - os esquemas validam os registros;
  - `canonical_id` único;
  - referências que existem ou estão marcadas como pendentes;
  - um campo de atributo extraído é recusado;
  - cada NPC com ficha curada tem registro, e cada registro aponta para a ficha certa;
  - o censo é idempotente, testado com áreas e criaturas inventadas.
