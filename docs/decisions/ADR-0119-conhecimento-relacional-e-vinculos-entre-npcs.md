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
3. **Conhecimento restrito por afiliação.** Uma relação RESTRICTED só entra no contexto quando uma afiliação curada do NPC corresponde a eligible_affiliations, ou quando o NPC está em allowed_npc_ids, ou quando o NPC é **parte da relação** (`subject_id` ou `object_id`). Assim, Lehtinan sabe que Bernard administra a Coroa de Cobre para ele sem curadoria própria (decisão do mantenedor após o laboratório S1f, 2026-11-10). Estar na mesma área, por si só, nunca concede acesso. A curadoria da identidade guarda afiliações explícitas, como place:copper-coronet:STAFF e place:copper-coronet:REGULAR.
4. **INQUIRY sem vazamento.** A propagação existente continua aceitando somente COMMON_REGIONAL. Uma relação restrita não é compartilhada automaticamente com companheiros, mesmo quando aparece no contexto do falante. Uma futura política de compartilhamento privado exigirá decisão própria e autorização explícita.
5. **Profundidade, não permissão.** WIS + INT continuam determinando as camadas de compreensão e a forma de expressão; nunca concedem acesso a uma relação. O contexto apresenta conhecimento público e restrito em seções separadas; relações restritas identificam seu sujeito para validar falas sobre o próprio NPC. O LLM formula a fala a partir dos fatos recebidos e não cria arestas, vínculos ou permissões.
6. **Proveniência de decisão do mantenedor.** A classe S4_MAINTAINER_CURATED registra decisões explicitamente aprovadas pelo mantenedor. Ela não é fonte externa nem equivale a S0/S1. O gate só a aceita em entradas CAMPAIGN_CANON com checked_by e checked_at; para SOURCE_CHECKED, continuam exigidas fontes S0/S1.
7. **Memória e linha temporal.** Relações públicas aprendidas por INQUIRY usam o mecanismo de snapshot existente, com idempotência, ramo, tempo e pin. Atualizar o pacote não reescreve o que já foi aprendido.
8. **Caso inicial — Coroa de Cobre.**
   - rel:lehtinan-owns-copper-coronet: Lehtinan é proprietário da Coroa de Cobre; conhecimento público local de Athkatla.
   - rel:bernard-manages-copper-coronet: Bernard coordena a operação cotidiana para Lehtinan; conhecimento restrito a afiliações STAFF ou REGULAR.
   - Bernard recebe a afiliação STAFF em sua curadoria. Frequentadores só recebem REGULAR quando houver curadoria explícita; não se infere frequência pela presença ocasional no mapa.
9. **Ajustes do laboratório S1f** (decisões do mantenedor, 2026-11-10).
   - **Caixa também para companheiros:** o clique direito num companheiro do grupo (retratos 1–5 do motor; o protagonista é o 0) abre a mesma caixa usada com habitantes. O companheiro fala pelo caminho de companheiro (memórias do grupo e o que aprendeu), sem primeiro contato da SPEC-006 e sem ensinar ninguém por INQUIRY.
   - **Matriz de Sabedoria/Inteligência também para companheiros na caixa:** a caixa lê Sabedoria e Inteligência da criatura no jogo (`EEex_Sprite_GetActiveStats`, só leitura) e a matriz do ADR-0117 vale como para os habitantes: define a profundidade do que ele aprendeu e o modo de falar, nunca o acesso. O overlay, que não recebe esses valores, continua com o resumo inteiro.
   - **Falas sobre si:** itens de conhecimento cujo sujeito é o próprio NPC aparecem marcados "(sobre você)" no prompt; a regra 8 pede o id exato do item usado, e o validador `SELF_CLAIM` aceita o que estiver nesses itens.
   - **Pedidos já respondidos:** após reiniciar o serviço, um pedido de companheiro já atendido não é respondido de novo (ids guardados ao lado do banco da campanha, sem texto).

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
- Validação no BG2:EE: evidência S1f (`docs/evidence/S1f-2026-11-10-laboratorio-arm64.md`), com Bernard (STAFF), NPCs sem afiliação e Salvanas (REGULAR curado).
