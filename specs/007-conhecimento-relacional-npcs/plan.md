# Plano de implementação — SPEC-007

1. **Modelo canônico:** estender o schema v1 com PLACE/RELATIONSHIP e metadados de aresta; preservar o carregamento por partição e o hash da revisão.
2. **Proveniência:** adicionar S4_MAINTAINER_CURATED com regra restrita no gate; documentar que não é fonte externa.
3. **Acesso:** adicionar resolvedor determinístico de relações restritas por afiliação curada; manter as relações públicas no canal regional existente.
4. **Diálogo:** unir conhecimento público, memória e relações restritas no contexto do habitante; filtrar INQUIRY para COMMON_REGIONAL.
5. **Curadoria:** registrar a Coroa de Cobre, a propriedade pública e a relação operacional de Bernard.
6. **Validação:** testes de schema, gate, elegibilidade, INQUIRY, contexto e resposta de Bernard.
7. **Laboratório:** usar a campanha isolada `lab-s1f`, com banco próprio (sem reutilizar `lab-s1e`); atualizar explicitamente o pin 1369 DR e repetir a conversa com Bernard, um estranho sem afiliação e um frequentador REGULAR curado.
