# CR-2026-032 — Recursos convertidos de outros jogos (módulo da SPEC-012)

**Status:** APPROVED (mantenedor, 2026-11-23: "Aprovar como proposta", decisões D1 a D4 na opção recomendada, com o download da pasta do verbeeg autorizado na D2)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-23

## Motivo e contexto

O primeiro grande objetivo do projeto traz ao BG2:EE criaturas de outros jogos (Icewind Dale, IWD2, NWN). Importar uma criatura é mais do que gerar o `.CRE` (ADR-0137, ADR-0141): pede animação (`INI` e `BAM`), sons (`WAV`), às vezes scripts (`BCS`), itens e magias (`ITM`, `SPL`).

O verbeeg mostrou o problema:
- o BG2:EE define a animação dele (`E251.INI`, desenhos `MGVE`), mas não traz os desenhos, que vêm do Icewind Dale: EE;
- a criatura existia, era contada e ficava invisível (S2c);
- os desenhos vieram de um projeto de conversão da comunidade (Infinity Animations), instalados só no override do laboratório, e desenharam com porte de gigante.

O mantenedor propôs um inventário de recursos convertidos dentro da SPEC-012 e trouxe nove projetos para avaliar. A análise está no registro desta CR.

## DEC/ADR/SPEC/REQ afetados

- **SPEC-012:** ganha o módulo "Recursos convertidos" (D1); seção 7.2, direitos.
- **CR-2026-030:** continua valendo; esta CR aplica a mesma divisão (esquema no repositório, dados locais) aos recursos convertidos.
- **ADR-0137 e ADR-0141:** o gerador e a recusa de animação sem desenhos viram a primeira etapa de validação.
- **REQ-CANON-004:** continua valendo.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **Duas fichas por criatura convertida:**
   - a ficha de origem (números do jogo ou do livro), local, em `~/.infinity-ai/sheets/`;
   - a ficha convertida (o que o BG2:EE usa), no registro local de criaturas (`templates.json`).
2. **Inventário local de recursos convertidos** (D4), em `~/.infinity-ai/resources/install-<build>/resources.json`, com um registro por criatura convertida. Os campos:
   - `source_game` e `source_creature_id`;
   - `converted_cre_id`;
   - `animation_ref` e `animation_assets` (cada arquivo, o tipo e se está na build);
   - `sound_refs` e `script_refs`;
   - `original_stats_ref` e `converted_stats_ref`;
   - `conversion_source` (a fonte registrada) e `target_engine`;
   - `rights_status` e `validation_status`.

   No repositório fica só o **esquema** (`knowledge/encyclopedia/schemas/converted-resource.v1.schema.json`) e o validador (`encyclopedia/resources.py`).
3. **Estados de validação,** em ordem:
   - `DECLARED`: registrado;
   - `ASSETS_PRESENT`: todos os arquivos estão na build ou no override (a checagem da ADR-0141);
   - `DRAWN_IN_GAME`: conferido no jogo pelo mantenedor;
   - `APPROVED`: aprovado para uso numa quest.
4. **Projetos de conversão viram fontes registradas,** com os tipos novos `CONVERSION_PROJECT` e `TOOL`, a licença e o que oferecem:
   - Infinity Animations;
   - Trials of the Luremaster for BG2:EE;
   - IWD1_EET e IWD2_EET;
   - NWNForBG;
   - IWDification;
   - PortraitScout.
5. **Regras de direitos (D3):**
   - recurso de outro jogo só entra no override da VM, nunca no repositório;
   - cada download é pedido com o nome, a origem e o tamanho;
   - projeto sem licença ou com arte de terceiros: só uso local no laboratório (`rights_status.use = LAB_ONLY`), com o aceite do mantenedor por projeto;
   - projeto com licença aberta (CC BY-SA, MIT): citado e adaptado nos termos dela, e a arte dos jogos continua fora do repositório;
   - o validador recusa `OPEN` para um projeto sem licença.
6. **Primeiro registro:** o verbeeg (`IACARCER`), com os desenhos e sons do Infinity Animations, em `DRAWN_IN_GAME` (S2c).

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Direitos:** os desenhos e sons são arte dos jogos (Beamdog/WotC) redistribuída pela comunidade. Ficam só na cópia do laboratório, como para um jogador que instala o mod.
- **Instalação parcial:** copiar os desenhos de um projeto com os nomes do INI do BG2:EE funcionou para o verbeeg; cada criatura precisa do próprio teste.
- **Compatibilidade:** nenhum consumidor atual muda. O inventário não alimenta o diálogo.

## Migração e rollback

- **Migração:** nenhuma; o inventário é novo.
- **Rollback:** apagar o esquema, o validador, os tipos de fonte novos e o inventário local; tirar do override os arquivos do Infinity Animations (`MGVE*.BAM`, `VERBEE*.WAV`).
