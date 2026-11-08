# ADR-0057 — Pipeline híbrido de ingestão, validação e publicação curada por ano DR

- **Decisão:** **DEC-062**, opção **C**, aprovada explicitamente em **2026-11-06**.
- **Estado:** **APROVADA como política de Discovery; NÃO implementada e NÃO testada**.
- **Versão:** Infinity AI Discovery **v5.8**.
- **Documento técnico:** `docs/62-pipeline-hibrido-de-ingestao-curadoria-e-publicacao-por-ano.md`.
- **Precedência:** **DEC-060/C e adendo (ADR-0055)** — partições físicas separadas por ano; **DEC-061/C (ADR-0056)** — alegações/fonte, conflitos e resoluções curadas. Esta decisão NÃO substitui essas regras.
- **Relacionadas:** DEC-008/009/011/012/014/015/017/022/028/029/051/052/053/055/056/057/058/059/060/061 e DEC-006/013/018 ainda abertas onde aplicáveis.

## Contexto

Forgotten Realms possui materiais abundantes, edições e narrativas divergentes. A curadoria totalmente manual é custosa, mas deixar um modelo extrair fatos e publicá-los autonomamente como verdade cria erros de cronologia, atribuição, licença e segurança. A ingestão deve escalar **sem converter texto de fontes em instruções** e sem violar o isolamento físico anual definido na DEC-060.

## Alternativas

- **A — Curadoria integralmente manual:** auditável, porém alto custo e cobertura lenta.
- **B — Importação e publicação inteiramente automáticas pela IA:** escalável na aparência, mas risco inaceitável de data errada, consenso inventado, publicação de segredos e conteúdo sem direitos.
- **C — Pipeline híbrido, com extração assistida por IA, verificações independentes e aprovação humana quando necessária:** **APROVADA**.

## Decisão vinculante

1. **Entrada controlada e autorizada.** Aceitar apenas materiais obtidos legitimamente para os quais haja finalidade e permissões de uso registradas. O fato de ser projeto privado/não comercial **não constitui por si só licença de reprodução, redistribuição, extração em massa ou compartilhamento**. Não usar scraping não autorizado nem incluir obras protegidas no ZIP de Discovery. Texto integral de referência, quando legitimamente utilizado, reside em repositório restrito **fora da árvore publicável**, com controles de acesso; o pacote contém só estrutura, regras, metadados mínimos e resumos próprios quando permitidos.
2. **Quarentena e tratamento como dados não confiáveis.** Arquivos, páginas e trechos de fonte são *dados*, jamais comandos. Identificar tipo/risco, separar parser de operações de jogo/sistema, impedir execução de macros/código e ignorar instruções embutidas que tentem alterar políticas, ACL ou autorizações (prompt injection). Sem shell arbitrário ou ferramentas mutativas concedidas ao LLM.
3. **Staging imutável antes do cânone.** Registrar entrada e versão da fonte (`source_id`, origem, edição/licença, hash, localizador, `ingestion_job_id`) em staging privado; deduplicar por identidade + versão + checksum; extrações são *candidatas*, não fatos. Reprocessar não cria publicações duplicadas. O original não é alterado por correções curatoriais.
4. **Extração/classificação assistida.** IA poderá sugerir entidades, nomes alternativos, eventos, organizações, datas/intervalos DR, regiões, relação temporal, afirmações, excertos de apoio limitados e status epistêmico. Toda saída é rastreada ao trecho/localizador da fonte, modelo e versão de prompt. Campo desconhecido vira `UNKNOWN`/`NEEDS_REVIEW`, nunca inferência assertiva sem evidência.
5. **Separação física por ano — invariante rígida.** A publicação canônica ocorre **apenas** em `knowledge/periods/<ano>-DR/{chronology,events,organizations,guilds,characters,regions}/`, em arquivos/manifestos anuais versionados. Índice operacional de pesquisa **não** pode conceder busca transversal por todos os anos. Para intervalo de anos, gerar referências/versionamentos anuais explícitos, comprovadamente vigentes, não replicar automaticamente um fato para todos os anos. Se o ano for indefinido, **não publicar** em ano adivinhado. Consulta primária por ano confirmado; antecedentes só por vigência/ACL; futuro não vira fato passado ou presente. Partições `1369-DR`/`1370-DR` seguem estruturas vazias de lore até publicação efetivamente curada.
6. **Manter proveniência e conflitos — invariante rígida.** Cada `Claim` candidata deve manter `source_id`, trecho/localização verificável, data/precisão DR, perspectiva/edição, entidades e revisão. Contradições seguem como `ConflictSet` separado, não como texto conciliado pela IA. `UNRESOLVED` exige revisão/adiamento proporcional ao risco. Uma resolução curada é auditável e preserva as alternativas (DEC-061).
7. **Gates por risco e revisão humana.** Validadores determinísticos conferem esquema, licença/escopo, ano, precisão, identidade, ACL, duplicação, contradições, proveniência, coerência canônica, formato e política de segurança. Apenas metadados/alegações **LOW-risk** explicitamente permitidos por política curatorial versionada e com evidência suficiente podem ser promovidos automaticamente; **padrão inicial: revisão humana antes de publicar novos fatos canônicos**. Datas ambíguas, conflitos, mudanças históricas significativas, qualquer conteúdo `HIGH/UNCERTAIN`, restrição de licença ou fonte duvidosa exigem revisão humana explícita ou bloqueio. IA não é revisora final.
8. **Publicação auditável e reversível por revisão.** Uma publicação recebe `publish_id`, `curation_revision`, autor/aprovador ou política autoaprovadora rastreável, `partition_year`, versão de índice e hash do manifesto. Publicar por promoção controlada do staging; preservar last-known-good, evitar leitura de estados parciais e definir plano de reversão por revisão (não apagar evidências nem alterações já confirmadas de campanha). Acionamentos de índice/cache devem ser versionados e sem exposição de períodos e segredos proibidos.
9. **Separação entre conhecimento base e história de campanha.** Conteúdo curado **não** equivale a `CampaignEvent`/receipts do BG2:EE. Overlays por campanha/ramo/ano são imutáveis em seus fatos confirmados sem os gates existentes. Atualizar conhecimento nunca reescreve silenciosamente saves, missões, NPCs ou histórico de PCs. Política de consumo de novas revisões por campanhas em andamento fica para **DEC-063**.
10. **Operação local-first e mínima divulgação.** Importadores/LLMs e workers LAN submetem-se ao roteamento DEC-059, pareamento DEC-058, ACL DEC-028, validação DEC-060, quotas DEC-056 e monitoramento DEC-055. Sem nuvem, telemetria, redistribuição de textos ou cópia de materiais para outros nós por padrão. Qualquer uso remoto futuro requer política específica de DEC-006/017 e autorização.
11. **Evidência e cobertura explícitas.** Pastas existentes significam somente organização documental. Catálogos precisam marcar `EMPTY/PARTIAL/REVIEWED` e não inferir lore inexistente; notas de evidência e gaps são auditáveis. Não foi importada nenhuma obra, extraído nenhum fato ou executado teste de BG2:EE/EEex/multiplayer neste Discovery.

## Estado de um lote (modelo candidato, não contrato final)

`REGISTERED → QUARANTINED → EXTRACTED_CANDIDATE → STAGED_CLASSIFIED → VALIDATED → (NEEDS_REVIEW | ELIGIBLE_FOR_POLICY_APPROVAL | BLOCKED) → APPROVED → PUBLISHED`; com `REJECTED`, `DEFERRED`, `SUPERSEDED` e `ROLLBACK_REVISION` controlados. Falhas não liberam publicação; `UNKNOWN` não pode se tornar `APPROVED` por timeout.

## Consequências e trade-offs

- **Benefícios:** evolução progressiva do lore, rastreabilidade e curadoria controlada, prevenção de mistura temporal, menor trabalho repetitivo, proteção das campanhas e revisão posterior possível.
- **Custos:** infraestrutura de staging, scanners/parsers, granularidade temporal, revisão humana, custos de modelos e índices, controles de licença/privacidade, auditoria e backups. Metadados podem ser incompletos, e nenhuma LLM garante precisão.
- **Limites:** formatos aceitos, schemas, critérios de risco e volume, thresholds, ferramentas/OCR, estratégia de índices e latência dependem de SPECS, protótipos, avaliações e diretrizes legais aplicáveis. Nenhum parser é autorizado automaticamente.

## Critérios de aceite candidatos (não executados)

1. Importação com data `1369 DR` publica **somente** em `1369-DR`, após autorização; dado `1370 DR` não aparece em consultas de 1369.
2. Registros com intervalo e continuidade comprovada produzem referências anuais explícitas, não cópia infinita nem fato futuro antecipado.
3. Fonte sem ano certo permanece em staging sem inventar cronologia.
4. Duas fontes conflitantes mantêm `Claim` e `ConflictSet` distintos; não há consenso inventado.
5. Reprocessamento e crash não duplicam entradas; liberação parcial não fica consultável.
6. Fonte com instrução maliciosa não altera prompts de sistema, ACL, runtime, arquivos de jogo ou regras.
7. Licença restritiva/vazia bloqueia publicação/distribuição até verificação permitida; pacote ZIP não inclui trechos extensos protegidos.
8. Atualizar lore não reescreve ramo/campanha; trabalho pendente e revisões são rastreáveis.
9. Worker LAN e índices só recebem informações filtradas, sem vazamentos de anos/segredos.
10. Revisão humana e política allowlist são auditadas; HIGH/UNCERTAIN não têm aprovação automática.

## Decisão seguinte

**DEC-063 — Política de vinculação de versões de conhecimento canônico às campanhas em andamento.** Decidir se os novos *knowledge packs* são aplicados automaticamente, congelados ou oferecidos como atualizações controladas e reversíveis, sem alterar fatos causais nem saves do host. **DEC-006, DEC-013, DEC-015, DEC-017 e DEC-018 seguem abertas** em seus escopos.
