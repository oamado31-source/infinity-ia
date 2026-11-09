# Template — pedido de entrada canônica (SPEC-005)

Preencha um bloco por fato. Não copie trechos longos do livro: escreva com suas palavras ou mande foto/paráfrase só para eu resumir. O repositório recebe apenas um resumo curto nosso (≤ 280 caracteres) e a referência da página.

```text
Obra:            (lands-of-intrigue | grand-history-of-the-realms | fr-campaign-setting-3e | bg2-manual)
Edição / ISBN:   (confira no exemplar; usado para confirmar knowledge/sources/<obra>.json)
Página/capítulo: (ex.: "Livro 1, p. 34" ou "cap. Athkatla")
Tipo:            (REGION | EVENT | ORGANIZATION | CHARACTER)
Ano DR:          (o ano a que o fato se refere; validade de/até se souber)
Precisão:        (EXACT_DAY | MONTH_ONLY | YEAR_ONLY | RANGE | APPROX | UNKNOWN)
Região:          (ex.: region:athkatla)
O que o trecho diz, nas suas palavras:
```

Fluxo: eu escrevo a entrada JSON em `knowledge/periods/<ano>-DR/<categoria>/` como `RESEARCH_ONLY`; você confere contra o livro; só então ela vira `SOURCE_CHECKED` (com `checked_by` e `checked_at`). O carregador recusa entradas S0 sem página, resumos longos e citações acima de 15 palavras.
