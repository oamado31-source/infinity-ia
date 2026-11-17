# CR-2026-029 — Terras só de conversa nunca são origem nem viagem de um NPC gerado

**Status:** APPROVED (mantenedor, 2026-11-17: "Lote I aprovado", decisões D2 e D3 do arquivo de conferência)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-17

## Motivo e contexto

O gerador de fundo das pessoas genéricas (ADR-0117, `generate_identity`) sorteia a origem e as viagens entre todas as regiões do pacote. O lote I traz três regiões que ninguém da superfície tem como terra natal nem como viagem comum:
- Kara-Tur, outro continente;
- Umbreterna (Underdark), o mundo debaixo da terra;
- Menzoberranzan, a cidade drow.

Ao gravar o lote, um teste mostrou um cliente da taverna de Athkatla "vindo de Kara-Tur". O arquivo de conferência prometeu (D2, D3) que essas terras seriam só assunto de conversa.

## DEC/ADR/SPEC/REQ afetados

- **ADR-0117:** o gerador continua determinístico e só usa regiões do pacote. Agora deixa de fora as terras só de conversa.
- **CR-2026-021:** a revisão do pacote ganha a lista, como ganhou os vizinhos.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **Manifesto da partição:** chave nova `talk_only_regions`, com `region:kara-tur` e `region:underdark`.
2. **`canon/pack.py`:**
   - `CanonPack.talk_only` é a lista com todas as regiões abaixo dela. Hoje entra Menzoberranzan, que fica abaixo de Umbreterna.
   - A lista entra na revisão pinada quando existe.
   - Uma entrada que não é `REGION` é recusada.
3. **`personality/identity.py`, `generate_identity`:** essas regiões nunca são sorteadas como origem nem como viagem.
4. **Efeito:**
   - um NPC gerado nunca "vem de" Kara-Tur, de Umbreterna nem de Menzoberranzan;
   - a curadoria ainda pode dar essas origens a um NPC conferido;
   - as entradas continuam no pacote e respondem pelo que se sabe delas.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Os fundos gerados mudam:** o sorteio usa a lista ordenada de regiões, que já mudava a cada lote que trazia regiões novas. Isso não é novo, e o conhecimento já adquirido fica no banco.
- **Compatibilidade:** sem a chave, nada muda. Com ela, a revisão do pacote muda e pede novo pin, como com qualquer lote.

## Migração e rollback

- **Migração:** novo pin, junto com o lote I.
- **Rollback:** tirar `talk_only_regions` do manifesto.

## Testes

- **`tests/test_talk_only.py`:**
  - a lista fechada inclui Menzoberranzan;
  - 800 fundos gerados (Athkatla e Baldur's Gate) nunca tocam essas terras;
  - a lista muda a revisão;
  - uma entrada que não é região é recusada.
- **Testes ajustados:** os testes que usavam Rashemen como "região que não existe no pacote" passam a usar `region:vaasa`. O teste de nomes do fundo gerado passa a separar os nomes de região com parênteses e hífen ("Kara-Tur").
