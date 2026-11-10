# ADR-0119 — Conhecimento relacional e vínculos entre NPCs

**Estado:** APROVADA (decisão explícita do mantenedor, 2026-11-10).  
**Relaciona-se com:** ADR-0059 (aquisição legítima e snapshots), ADR-0114 (conhecimento regional), ADR-0116 (INQUIRY), ADR-0117 (identidade), SPEC-004 (diálogo) e SPEC-005 (pacote canônico).  
**Gate:** etapa 1, single player. A validação sintética não comprova a execução no BG2:EE.

## Contexto

O teste de diálogo com Bernard revelou que o contexto consegue representar sua identidade e o conhecimento regional, mas não relações tipadas entre pessoas e estabelecimentos. A LLM recusou corretamente afirmar algo ausente de FATOS e CONHECIMENTO GERAL; o defeito estava na cobertura do conhecimento, não na matriz WIS + INT.

Uma relação não é uma característica pessoal: “Lehtinan é dono da Coroa de Cobre” liga duas entidades; “Bernard administra a casa para Lehtinan” é um vínculo operacional com audiência mais restrita.

## Decisão

1. **Relações como dados de primeira classe.** O pacote canônico aceita entradas RELATIONSHIP com subject_id, predicate, object_id e context_id opcional. Lugares são entidades PLACE. Relações têm proveniência, validade temporal, região e política de acesso; não são adicionadas a self_facts.
2. **Conhecimento público regional.** Uma relação COMMON_REGIONAL com audiência REGIONAL_PUBLIC segue os canais existentes ORIGIN, RESIDENCE e INQUIRY. A elegibilidade continua condicionada ao pin, ano, gate de cânone e região mapeada.
3. **Conhecimento restrito por afiliação.** Uma relação RESTRICTED só entra no contexto quando uma afiliação curada do NPC corresponde a eligible_affiliations, ou quando o NPC está em allowed_npc_ids. Estar na mesma área, por si só, nunca concede acesso. A curadoria da identidade guarda afiliações explícitas, como place:copper-coronet:STAFF e place:copper-coronet:REGULAR.
4. **INQUIRY sem vazamento.** A propagação existente continua aceitando somente COMMON_REGIONAL. Uma relação restrita não é compartilhada automaticamente com companheiros, mesmo quando aparece no contexto do falante. Uma futura política de compartilhamento privado exigirá decisão própria e autorização explícita.
5. **Profundidade, não permissão.** WIS + INT continuam determinando as camadas de compreensão e a forma de expressão; nunca concedem acesso a uma relação. O LLM formula a fala a partir dos fatos recebidos e não cria arestas, vínculos ou permissões.
6. **Proveniência de decisão do mantenedor.** A classe S4_MAINTAINER_CURATED registra decisões explicitamente aprovadas pelo mantenedor. Ela não é fonte externa nem equivale a S0/S1. O gate só a aceita em entradas CAMPAIGN_CANON com checked_by e checked_at; para SOURCE_CHECKED, continuam exigidas fontes S0/S1.
7. **Memória e linha temporal.** Relações públicas aprendidas por INQUIRY usam o mecanismo de snapshot existente, com idempotência, ramo, tempo e pin. Atualizar o pacote não reescreve o que já foi aprendido.
8. **Caso inicial — Coroa de Cobre.**
   - rel:lehtinan-owns-copper-coronet: Lehtinan é proprietário da Coroa de Cobre; conhecimento público local de Athkatla.
   - rel:bernard-manages-copper-coronet: Bernard coordena a operação cotidiana para Lehtinan; conhecimento restrito a afiliações STAFF ou REGULAR.
   - Bernard recebe a afiliação STAFF em sua curadoria. Frequentadores só recebem REGULAR quando houver curadoria explícita; não se infere frequência pela presença ocasional no mapa.

## Consequências

- A matriz de personalidade e as regras de validação de fala permanecem inalteradas.
- O pacote 1369 DR ganha tipos PLACE e RELATIONSHIP, e a revisão do pacote muda.
- Campanhas já pinadas precisam de atualização explícita do pin para usar as novas entradas. Não há atualização retroativa nem concessão silenciosa de conhecimento.
- Relações restritas não são ensinadas por INQUIRY na implementação inicial.
- O grafo pode crescer para vínculos familiares, comerciais, políticos, profissionais, facções, alianças e rivalidades, mantendo a mesma proveniência e política de acesso.

## Evidências e limites

- A decisão do mantenedor em 2026-11-10 estabelece a propriedade pública local e a política de acesso operacional para o caso inicial.
- A localização da Coroa de Cobre em AR0406 usa o inventário local do jogo já referenciado na curadoria de Bernard.
- A entrada S4 é cânone do projeto/campanha, não uma afirmação de que a fonte externa foi verificada independentemente.
- A validação real no BG2:EE ainda depende de repinar o pacote no ambiente de laboratório e repetir os diálogos com Bernard e outros NPCs.
