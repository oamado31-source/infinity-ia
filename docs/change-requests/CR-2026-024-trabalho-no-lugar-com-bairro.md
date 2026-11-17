# CR-2026-024 — "Trabalho na Coroa de Cobre" volta a ser barrado quando o lugar traz o bairro

**Status:** APPROVED (mantenedor, 2026-11-17: "Faça esta tarefa aqui")  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-17

## Motivo e contexto

Na bateria do lote F, o caso `sem-staff-trabalho` deixou passar a fala "Trabalho na Coroa de Cobre, sim. Moro nas Favelas.". Quem disse foi um frequentador sem vínculo de equipe (`STAFF`), que não trabalha lá (ADR-0119 e ADR-0120).

A checagem da CR-2026-005 compara a fala com o lugar onde a pessoa está (`resident_of`). Desde a correção de laboratório de 2026-11-15 (#41, "o bairro na frase do lugar"), esse lugar chega como "a Coroa de Cobre, nas Favelas". A checagem procurava "trabalho na Coroa de Cobre, nas Favelas" e não reconhecia a frase curta.

As outras tentativas do caso eram barradas porque o modelo dizia "trabalho aqui", que é a outra parte da checagem. Os testes da CR-2026-005 usavam o lugar sem o bairro, por isso não pegaram a regressão.

## DEC/ADR/SPEC/REQ afetados

- **CR-2026-005:** volta a valer com o lugar como o serviço o monta hoje.
- **CR-2026-009:** inalterada. A pergunta do jogador repetida ("Trabalho na Coroa de Cobre? Não.") continua sem contar como afirmação.
- Nenhum ADR é editado.

## Diff proposto e impacto no comportamento

1. **`dialogue/validate.py`, `_works_at_place`:** o lugar de trabalho é o estabelecimento, a parte antes da vírgula, e nunca o bairro em volta.
2. **Efeito:**
   - "Trabalho na Coroa de Cobre" sem vínculo `STAFF` volta a ser recusado (`SELF_CLAIM:WORK`);
   - "Trabalho nas Favelas", que é o bairro, continua permitido: um carregador pode trabalhar no bairro.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Lugar com vírgula no próprio nome:** nenhum no pacote hoje. Se aparecer, a checagem pegaria só a primeira parte do nome. É um risco pequeno e fácil de ver num teste.
- **Instabilidade restante do caso:** às vezes, depois da recusa, a nova tentativa cai noutra regra (`THIRD_PARTY:TRAIT`) e a resposta vira a fala de reserva. A afirmação falsa não passa mais; quando falha, o caso falha para o lado seguro.

## Migração e rollback

- **Migração:** nenhuma.
- **Rollback:** voltar a comparar com `resident_of` inteiro.

## Testes

- **`tests/test_identity.py`, caso novo** com o lugar como o serviço o monta ("a Coroa de Cobre, nas Favelas"). Sem a correção, ele falha. Cobre quatro frases:
  - a frase da bateria;
  - "trabalho aqui na Coroa de Cobre";
  - quem é `STAFF`;
  - o bairro e a pergunta repetida.
- **Bateria:** `sem-staff-trabalho` 5/5. Nas cinco rodadas, a afirmação foi recusada antes de a nova tentativa acertar.
