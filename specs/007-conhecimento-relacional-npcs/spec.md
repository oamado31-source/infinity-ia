# SPEC-007 — Conhecimento relacional de NPCs

**Status:** APROVADA para implementação inicial (2026-11-10).  
**Rastreabilidade:** ADR-0119; ADR-0059/0114/0116/0117; SPEC-004/005.

## Objetivo

Representar relações entre NPCs, lugares, organizações e outros atores como dados tipados, com proveniência, validade, audiência e política de acesso. A camada deve complementar identidade, personalidade e memória sem alterar o motor do jogo.

## Escopo inicial

- Entidades PLACE e arestas RELATIONSHIP no pacote canônico por ano DR.
- Predicados tipados e IDs estáveis de sujeito/objeto/contexto.
- Audiências REGIONAL_PUBLIC, AFFILIATED e EXPLICIT_NPCS.
- Afiliações curadas na identidade do NPC.
- Integração de relações públicas aos canais existentes de conhecimento regional e INQUIRY.
- Inclusão de relações restritas no contexto apenas para NPCs elegíveis.
- Aplicação de WIS + INT às camadas de compreensão já existentes.
- Caso de validação: Lehtinan, Coroa de Cobre e Bernard.

## Requisitos EARS

- **REQ-REL-001:** QUANDO uma relação for curada, DEVERÁ ser representada por uma entrada RELATIONSHIP com sujeito, predicado, objeto e proveniência.
- **REQ-REL-002:** QUANDO uma relação apontar para um lugar do pacote, DEVERÁ usar ID estável e verificável de entidade PLACE.
- **REQ-REL-003:** QUANDO uma relação for REGIONAL_PUBLIC/COMMON_REGIONAL, DEVERÁ respeitar pin, ano, gate e região, e poderá ser adquirida pelos canais ORIGIN, RESIDENCE e INQUIRY.
- **REQ-REL-004:** QUANDO uma relação for RESTRICTED/AFFILIATED, DEVERÁ exigir interseção entre afiliações curadas do NPC e eligible_affiliations.
- **REQ-REL-005:** QUANDO uma relação for RESTRICTED/EXPLICIT_NPCS, DEVERÁ exigir correspondência exata em allowed_npc_ids.
- **REQ-REL-006:** SE um NPC estiver apenas presente na mesma área, NÃO DEVERÁ receber uma relação restrita sem afiliação ou allowlist.
- **REQ-REL-007:** QUANDO a fala utilizar uma relação pública, INQUIRY poderá compartilhar somente o conteúdo efetivamente transmitido, preservando snapshots e causalidade.
- **REQ-REL-008:** RELATIONSHIP/RESTRICTED NÃO DEVERÁ ser propagada pelo INQUIRY público.
- **REQ-REL-009:** WIS + INT DEVERÃO controlar profundidade de compreensão, nunca elegibilidade de acesso.
- **REQ-REL-010:** LLM NÃO DEVERÁ criar, alterar ou conceder relações; somente verbalizar fatos presentes no contexto.
- **REQ-REL-011:** S4_MAINTAINER_CURATED DEVERÁ ser aceito apenas para CAMPAIGN_CANON conferido; não poderá substituir fontes S0/S1 em SOURCE_CHECKED.
- **REQ-REL-012:** Alteração do pacote DEVERÁ mudar sua revisão; campanhas pinadas não receberão o novo conhecimento até atualização explícita.

## Critérios de aceite

1. O pacote 1369 DR carrega o lugar Coroa de Cobre e as duas relações iniciais sem erro de schema.
2. Um NPC com origem/residência elegível em Athkatla recebe a relação pública de propriedade.
3. Bernard, com afiliação STAFF, recebe a relação operacional restrita.
4. Um estranho sem afiliação não recebe a relação operacional, mesmo na mesma área.
5. Um NPC com afiliação REGULAR recebe a relação operacional restrita.
6. INQUIRY compartilha a relação pública quando ela é dita e não compartilha a relação restrita.
7. A fala de Bernard pode citar Lehtinan e a propriedade sem unknown, com o ID de conhecimento correto.
8. Fontes S4 não passam pelo gate quando a entrada não é CAMPAIGN_CANON.
9. A suíte automatizada passa; a validação em jogo permanece pendente até repin e teste real.
