# Template de partição histórica — AAAA-DR

Copiar esta estrutura para um ano DR **somente quando houver necessidade de curadoria**. Nenhum fato é presumido.

Categorias: `chronology/`, `events/`, `organizations/`, `guilds/`, `characters/`, `regions/`.

Manifesto do ano (modelo candidato): `year_DR`, `partition_revision`, `coverage_status=EMPTY|PARTIAL|CURATED`, `source_refs`, `categories`, `validation_status`, `reviewer`, `last_curated`, `dependency_years`.

Cada entrada candidata precisa de ID estável, ano de partição, data/intervalo de validade, precisão temporal, referências verificáveis, status da fonte, relação geográfica, vínculos com entidades e versões conflitantes. Não preencher dias, marcos, autoridades ou nomes com base em suposições. Usar resumos originais e respeitar direitos de reprodução.

Uma entidade ativa em anos sucessivos pode ter versões pontuais com intervalo de validade e referência ao registro-base, **não** cópias repetidas sem controle. A consulta ao histórico deve abrir anos antecedentes explicitamente quando necessários e permitidos.

## Complemento para conflitos de fontes no mesmo ano — DEC-061/C

O manifesto futuro da partição deve distinguir referências (`Source`), alegações (`Claim`), conjuntos de conflito (`ConflictSet`) e resoluções curatoriais (`CuratedResolution`). Campos candidatos: `source_id`, `claim_id`, `conflict_set_id`, `edition`, `perspective`, `world_year_DR`, `valid_from/valid_to`, `time_precision`, `curation_status`, `resolution_scope`, `reviewer_id`, `curation_revision`. Não preencher com dados inventados nem copiar trechos extensos de obras. Resoluções preservam versões alternativas e jamais unem diretórios anuais em corpus único.

## DEC-062/C — manifesto de publicação anual curada

Publicações futuras devem vincular `source_id`, `source_locator`, revisão de origem, `claim_id`, `conflict_set_id`, validade do fato, ano DR, `curation_revision`, `reviewer_or_policy_id`, `publish_id`, `manifest_hash` e `rights_status` verificados. Campos faltantes cruciais bloqueiam a promoção. Nunca mover fonte bruta ou staging privado para a partição pública; nunca auto-preencher fatos de outro ano. Revisão anual se ativa apenas após validação consistente, mantendo last-known-good e histórico editorial. O estado atual é de **template**, sem fatos históricos.
