# CR-2026-013 — Tipo de entrada `TOPIC` para costumes, religião e cultura

**Status:** APPROVED (mantenedor, 2026-11-15)  **Autor:** mantenedor (com Claude Code)  **Data:** 2026-11-15

## Motivo e contexto

O lote A da enciclopédia base (Athkatla e Amn) trouxe um tipo de conhecimento que nenhum dos seis tipos de entrada comporta. São coisas que o povo sabe e que dão vida às conversas, mas que não são região, lugar, evento, organização, personagem nem relação. Exemplos:
- as moedas de Amn;
- a escala social por metais e o jeito de falar ("Bons negócios!");
- o uso do Thorass nos contratos.

A SPEC-008 diz que o único campo novo da enciclopédia é a classe de sigilo. Por isso, um tipo novo precisa deste CR.

A alternativa era dobrar esses costumes nas camadas de `region:amn`. Ela foi descartada: as camadas ficariam longas e misturadas, e cada costume perderia a própria fonte, página e conferência.

## DEC/ADR/SPEC/REQ afetados

- **SPEC-005 (pacote canônico) e SPEC-008 (corpus da enciclopédia):** ampliados por este CR, com um tipo novo no `canon_entry_v1`. Nenhum ADR é editado.
- **Regras de quem sabe o quê:** inalteradas (ADR-0114, ADR-0117, ADR-0120 e CR-2026-012). Um `TOPIC` é conhecido pelas mesmas regras de qualquer entrada regional: origem, residência, viagem (núcleo popular) e o nível de Faerûn.

## Diff proposto e impacto no comportamento

1. **Schema `canon_entry_v1`:**
   - `kind` aceita `TOPIC`, e o `id` aceita o prefixo `topic:`;
   - um `TOPIC` exige `region_id`, a região onde o costume é conhecido (pode ser `region:faerun`);
   - um `TOPIC` não tem áreas do jogo (`area_resrefs` vazio), porque não é um lugar.
2. **`canon/pack.py`:** `KIND_PREFIX` ganha `TOPIC: 'topic'`, e a validação recusa um `TOPIC` sem região ou com área.
3. **Pacote:** a categoria `topics` entra no manifesto da partição. Os arquivos ficam em `knowledge/periods/<ano>-DR/topics/`.
4. **Relações:** um `TOPIC` não pode ser sujeito, objeto nem contexto de uma relação, porque a relação continua sendo entre entidades.
5. **Uso previsto:** costumes, moedas, línguas e modos de falar, leis e práticas, e conhecimento geral de religião e cultura. Deuses e igrejas podem usar `TOPIC`, ou `CHARACTER` e `ORGANIZATION` quando houver uma entidade com nome e ação no mundo; a curadoria escolhe caso a caso.

**Efeito hoje:** nenhum. O pacote atual não tem `TOPIC`. As primeiras entradas vêm com o lote A, cada uma com fonte e conferência do mantenedor.

## Riscos/ameaças, licenças, dados privados e compatibilidade

- **Tipo "gaveta":** o risco é virar depósito do que não se encaixa. Contenção: cada `TOPIC` precisa de região, fonte e página como qualquer entrada, e o rascunho diz por que não cabe nos outros tipos.
- **Compatibilidade:** os pacotes antigos continuam válidos. Campanhas fixadas não veem os tópicos novos até um novo pin (REQ-REL-012).
- **Nada do jogo ou dos livros entra no repositório:** só resumos próprios com obra e página (ADR-0109, REQ-CANON-004).

## Migração e rollback

- **Migração:** sem migração de banco.
- **Rollback:** remover o tipo do schema e do `KIND_PREFIX`, a categoria `topics` do manifesto e os arquivos `topics/` da partição. As entradas dos outros tipos não são afetadas.
