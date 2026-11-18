# SPEC-012 — Enciclopédia Multijogo: Personagens, Criaturas e Recursos

**Projeto:** Infinity AI  
**Versão:** 1.0  
**Data:** 17/11/2026  
**Status:** PROPOSTA PARA REVISÃO. Registrada no repositório em 2026-11-18, a pedido do mantenedor ("vamos adicionar a SPEC-012 ao repositório"). Implementação só depois da revisão das notas abaixo e de uma CR própria (ADR-0111).  
**Natureza:** Diretriz de inventário, extração, normalização, proveniência e manutenção de dados.

---

## Notas de registro (2026-11-18)

Pontos a decidir na revisão, antes de qualquer implementação. O texto da SPEC acima e abaixo está como o mantenedor o escreveu.

1. **Dados extraídos no repositório público.** Hoje o que sai dos arquivos do jogo (resrefs, fichas, lojas, áreas) fica só em inventários locais, fora do repositório (REQ-CANON-004; ADR-0132; SPEC-008). As seções 6 e 7.2 propõem guardar no repositório identificadores, metadados factuais e atributos estruturados extraídos. É preciso uma CR que diga o que vai para o repositório (esquemas, ferramentas, registros curados com resumo próprio) e o que fica local (o catálogo extraído).
2. **Nome da categoria 07.** `knowledge/quests/` já guarda as quests narrativas do próprio projeto (SPEC-011). As missões originais dos jogos devem ficar em outro caminho (por exemplo `knowledge/encyclopedia/quests/`), sem misturar conteúdo do jogo com conteúdo de campanha (seção 13).
3. **Missões originais e spoilers.** Variáveis, ramificações e desfechos das quests originais contam como spoiler (ADR-0095, item 6; ADR-0096). Campos como `branch_refs` e `outcomes` precisam da mesma proteção.
4. **Jogos instalados.** O laboratório tem só o BG2:EE com EEex (`BG2EE-P1`). Extrair BG1, SoD, IWD, IWD2 e NWN pede instalações próprias, com permissão e tamanho informados antes de qualquer download.
5. **Consumidores atuais.** `knowledge/npcs/` (fichas curadas da etapa 3), o pacote de cânone (`knowledge/periods/`) e os inventários locais de habitantes e lojas continuam valendo durante a transição (critério 11).
6. **Uso nas quests (SPEC-011, segundo corte).** Localizar um criminoso ou saber onde está um item cabe em quests narrativas. Recuperar um item ou eliminar uma criatura no jogo pede escrita no jogo (portão P3 e gateway, DEC-012).

---

## 1. Objetivo

Estabelecer uma enciclopédia multijogo centralizada no repositório Infinity AI para catalogar, organizar e relacionar entidades e recursos existentes nos jogos oficiais e expansões contemplados pelo projeto.

A enciclopédia permitirá identificar o que já existe nos materiais de origem antes de criar conteúdo novo. Seus registros preservarão identificadores, atributos, variantes, relações e referências de origem, sem misturar silenciosamente dados de versões ou sistemas de regras diferentes.

A enciclopédia será organizada em oito categorias:

1. **Personagens e NPCs**.
2. **Criaturas**.
3. **Itens e equipamentos**.
4. **Magias e habilidades**.
5. **Raças, classes e regras**.
6. **Facções e organizações**.
7. **Missões e acontecimentos**.
8. **Áreas e localidades**.

As categorias serão subcatálogos independentes para organização, consulta, validação e evolução, mas compartilharão identificadores e relações para permitir consultas integradas.

**Princípio central:** catalogar primeiro, preservar a proveniência, validar os dados e só então disponibilizá-los aos sistemas do Infinity AI. A existência de um registro não significa, por si só, que ele seja canônico para qualquer época, conhecido por qualquer NPC, compatível com BG2:EE ou autorizado para redistribuição.

## 2. Resultados esperados

- Catálogo de personagens e NPCs: companheiros, protagonistas, antagonistas, habitantes, comerciantes, autoridades, personagens históricos e NPCs genéricos identificáveis.
- Catálogo de criaturas, espécies e variantes, com fichas específicas por jogo e versão.
- Catálogos de itens, equipamentos, magias, habilidades, raças, classes, facções, missões, acontecimentos, áreas e localidades.
- Relações entre entidades, recursos e aparições em campanhas, módulos e áreas.
- Identificação de duplicidades, variantes e entidades equivalentes entre jogos, sem apagar diferenças originais.
- Rastreabilidade até o jogo, expansão, versão, recurso interno e fonte externa que sustentam cada dado.
- Processo incremental de extração, conferência, curadoria e aprovação.
- Índices para consultas pelo runtime e ferramentas de desenvolvimento.

## 3. Jogos e fontes

### 3.1 Escopo inicial

- **Baldur's Gate:** jogo original, Tales of the Sword Coast e conteúdo aplicável da Enhanced Edition.
- **Siege of Dragonspear:** campanha e recursos próprios.
- **Baldur's Gate II:** Shadows of Amn, Throne of Bhaal e conteúdo aplicável da Enhanced Edition.
- **Icewind Dale:** jogo original, Heart of Winter e Trials of the Luremaster.
- **Icewind Dale II:** campanha e recursos próprios.
- **Neverwinter Nights:** campanha original, Shadows of Undrentide e Hordes of the Underdark.

EET, ports, conversões e mods poderão ser catalogados em coleções de origem próprias. Não deverão ser confundidos com conteúdo original de um jogo-base nem contabilizados automaticamente como novas entidades.

### 3.2 Fontes inicialmente identificadas

As fontes comunitárias servem para descoberta, conferência e contextualização. A extração dos arquivos originais é a referência técnica prioritária para identificadores e dados estruturados.

- **BG1 / Siege of Dragonspear:** TH.GL — <https://baldursgateee.th.gl/>.
- **BG2 / Throne of Bhaal:** Planet Baldur's Gate — <https://pbg.bgforge.net/>; GameBanshee — <https://www.gamebanshee.com/>.
- **IWD / expansões / IWD2:** Planet Baldur's Gate e GameBanshee.
- **NWN:** Neverwinter Vault — <https://neverwintervault.org/>; NWN Wiki — <https://nwn.wiki/>; blueprints e planilhas comunitárias.
- **Infinity Engine:** Near Infinity e parsers compatíveis.
- **NWN:** Aurora Toolset, documentação GFF e parsers de UTC, UTI, UTD, UTE, UTT, DLG e outros formatos aplicáveis.

A lista de fontes é extensível. Cada fonte deverá registrar URL, responsável/editor quando conhecido, data de consulta, versão, escopo, limitações e condições de uso.

### 3.3 Hierarquia de evidência

1. Arquivo original do jogo ou expansão, identificado por instalação e versão.
2. Documentação oficial ou material técnico do desenvolvedor.
3. Repositório ou documentação mantida pelo autor do projeto/mod.
4. Banco de dados comunitário com referências verificáveis.
5. Wiki, guia, fórum ou outra fonte secundária.
6. Inferência ou associação automatizada, sempre marcada como não verificada.

Uma fonte secundária não deverá substituir silenciosamente um dado contraditório encontrado no arquivo original. Divergências deverão ser preservadas e encaminhadas para revisão.

## 4. Categorias da enciclopédia

### 4.1 Categoria 01 — Personagens e NPCs

Catalogar todos os personagens identificáveis presentes nos jogos e expansões, não apenas companheiros recrutáveis.

Inclui protagonistas e personagens jogáveis predefinidos; companheiros; personagens canônicos e históricos; antagonistas e chefes com identidade individual; comerciantes, estalajadeiros e prestadores de serviços; autoridades, nobres, líderes, sacerdotes e representantes de facções; habitantes, viajantes, guardas, mercenários e personagens de missões; NPCs genéricos ou variantes nomeadas quando identificáveis; personagens temporários, invocados ou condicionais quando relevantes.

**Campos recomendados:** `canonical_id`, `display_name`, `alternate_names`, `entity_type`, `source_game`, `source_expansion`, `source_version`, `source_id`/`resref`/blueprint, `race_ref`, `class_refs`, `kit_or_subclass`, `alignment`, `attributes`, `level_by_source`, `hit_points`, `armor_class`, `saving_throws`, `combat_stats`, `skills`, `proficiencies`, `equipment_refs`, `ability_refs`, `spell_refs`, `biography_ref`, `dialogue_refs`, `faction_refs`, `relationship_refs`, `appearance_refs`, `area_refs`, `source_refs` e `verification_status`.

A ausência de um atributo na fonte deverá ser representada como ausente ou desconhecida, nunca preenchida por suposição. Personagens criados pelo jogador ou gerados dinamicamente deverão ser distinguidos dos personagens definidos pelos desenvolvedores.

### 4.2 Categoria 02 — Criaturas

Catalogar espécies, famílias, subtipos e variantes presentes nos jogos e expansões.

Inclui animais e bestas; humanoides monstruosos; gigantes; mortos-vivos; dragões e criaturas dracônicas; aberrações; construtos; elementais; extraplanares; criaturas subterrâneas; plantas e criaturas vegetais; criaturas mágicas e monstros especiais; familiares, invocações e criaturas conjuradas.

**Campos recomendados:** `canonical_id`, `display_name`, `species`, `family`, `subtype`, `variant`, `source_game`, `source_expansion`, `source_version`, `source_id`/`resref`/blueprint, `creature_type`, `attributes`, `hit_dice`, `level_or_challenge_data`, `hit_points`, `armor_class`, `attacks`, `damage`, `resistances`, `immunities`, `saving_throws`, `special_abilities`, `spell_refs`, `treasure_refs`, `animation_refs`, `sound_refs`, `appearance_refs`, `area_refs`, `source_refs` e `verification_status`.

Uma espécie compartilhada entre jogos poderá ter identidade conceitual comum, mas cada ficha de origem deverá permanecer separada. Estatísticas de um jogo não deverão ser copiadas para outro apenas porque o nome ou a aparência são semelhantes.

### 4.3 Categoria 03 — Itens e equipamentos

Catalogar recursos utilizáveis, equipáveis, consumíveis, colecionáveis, mágicos ou relevantes à economia e à progressão.

Inclui armas e munições; armaduras, escudos e vestimentas; anéis, amuletos, cintos, capas, botas, luvas e acessórios; artefatos e itens únicos; poções, pergaminhos e consumíveis; componentes, materiais, gemas e tesouros; itens de missão e objetos narrativos; itens comuns, mágicos, amaldiçoados ou de uso restrito.

**Campos recomendados:** `canonical_id`, `display_name`, `item_type`, `item_subtype`, `source_game`, `source_expansion`, `source_version`, `source_id`/`resref`/blueprint, `description_reference`, `weight`, `value`, `rarity_or_quality`, `damage_profile`, `armor_or_defense_data`, `proficiencies`, `magical_properties`, `charges`, `requirements`, `restrictions`, `effects`, `owner_or_appearance_refs`, `area_refs`, `source_refs` e `verification_status`.

Descrições extensas de livros, itens ou outros textos protegidos não deverão ser copiadas integralmente para o repositório. Poderão ser armazenados metadados factuais, propriedades estruturadas, referências e resumos originais dentro dos limites de uso aplicáveis.

### 4.4 Categoria 04 — Magias e habilidades

Catalogar magias, poderes, talentos, habilidades especiais e efeitos mecânicos.

Inclui magias arcanas e divinas; magias por círculo, escola ou esfera; habilidades raciais e de classe; talentos e perícias quando aplicáveis; poderes especiais de NPCs e criaturas; efeitos de status, buffs, debuffs e efeitos persistentes; habilidades ativáveis e passivas.

**Campos recomendados:** `canonical_id`, `display_name`, `ability_type`, `school_or_category`, `source_game`, `source_expansion`, `source_version`, `source_id`/`resref`, `spell_level_or_rank`, `class_or_race_restrictions`, `casting_or_activation_data`, `range`, `area_of_effect`, `duration`, `saving_throw`, `resistance_or_dispel_data`, `effects`, `resource_refs`, `source_refs` e `verification_status`.

A mesma magia poderá ter implementações ou parâmetros diferentes entre jogos. A identidade conceitual poderá relacioná-las, mas os dados mecânicos originais deverão permanecer específicos por fonte.

### 4.5 Categoria 05 — Raças, classes e regras

Registrar opções de personagem e elementos de regras necessários para interpretar fichas e progressão.

Inclui raças e sub-raças; classes e subclasses; kits e especializações; alinhamentos; atributos e modificadores; proficiências, perícias e talentos; regras de progressão, níveis e experiência; restrições e requisitos; diferenças entre AD&D 2e, regras adaptadas de Infinity Engine, regras de NWN e outros sistemas presentes no escopo.

**Campos recomendados:** `canonical_id`, `display_name`, `rule_family`, `source_game`, `source_expansion`, `source_version`, `category`, `requirements`, `restrictions`, `progression_data`, `attribute_modifiers`, `ability_refs`, `related_rule_refs`, `source_refs` e `verification_status`.

Esta SPEC não converte automaticamente todos os jogos para um único sistema de regras. A camada deverá preservar a implementação original e permitir mapeamentos explícitos quando necessários.

### 4.6 Categoria 06 — Facções e organizações

Catalogar grupos sociais, políticos, religiosos, militares, criminosos e mágicos.

Inclui ordens e organizações religiosas; guildas e associações profissionais; facções criminosas; organizações políticas e nobres; exércitos, guardas e forças mercenárias; cultos e sociedades secretas; organizações mágicas e acadêmicas; facções regionais e extraplanares.

**Campos recomendados:** `canonical_id`, `display_name`, `alternate_names`, `organization_type`, `source_game`, `source_expansion`, `source_version`, `region_refs`, `headquarters_area_refs`, `leader_refs`, `member_refs`, `allied_faction_refs`, `rival_faction_refs`, `relationship_data`, `historical_events`, `source_refs` e `verification_status`.

Relações de aliança, rivalidade, hierarquia ou pertencimento deverão possuir proveniência e, quando aplicável, validade temporal.

### 4.7 Categoria 07 — Missões e acontecimentos

Catalogar missões, arcos narrativos, acontecimentos históricos e eventos relevantes das campanhas.

Inclui missões principais e secundárias; arcos de companheiros; eventos históricos do cenário; eventos locais e regionais; acontecimentos condicionais e ramificações; decisões e consequências relevantes; eventos associados a facções, personagens e localidades.

**Campos recomendados:** `canonical_id`, `display_name`, `event_or_quest_type`, `source_game`, `source_expansion`, `source_version`, `campaign_refs`, `chronology_refs`, `time_or_date`, `region_refs`, `area_refs`, `character_refs`, `creature_refs`, `faction_refs`, `item_refs`, `prerequisites`, `outcomes`, `branch_refs`, `dialogue_refs`, `source_refs` e `verification_status`.

Esta categoria deverá distinguir eventos canônicos publicados nos materiais oficiais de eventos que só ocorrem em uma campanha específica do jogador. Eventos de campanha não deverão ser promovidos automaticamente ao cânone geral de Forgotten Realms.

### 4.8 Categoria 08 — Áreas e localidades

Manter referências normalizadas às regiões, cidades, localidades e mapas, integrando-se à SPEC-010.

Inclui regiões geográficas; cidades, distritos e vilas; castelos, keeps e fortalezas; masmorras, cavernas e complexos subterrâneos; templos, ruínas e locais históricos; florestas, montanhas, desertos e áreas selvagens; interiores e mapas de edifícios; planos e localidades extraplanares.

**Campos recomendados:** `canonical_id`, `display_name`, `alternate_names`, `location_type`, `source_game`, `source_expansion`, `source_version`, `region_ref`, `parent_location_ref`, `area_refs`, `map_resource_refs`, `character_refs`, `creature_refs`, `item_refs`, `faction_refs`, `quest_refs`, `event_refs`, `chronology_refs`, `source_refs` e `verification_status`.

A SPEC-010 permanece responsável pelo inventário técnico, disponibilidade, deduplicação, compatibilidade e direitos dos mapas. A categoria 08 desta SPEC deverá consumir e relacionar os identificadores da SPEC-010, evitando manter um segundo inventário geográfico conflitante.

## 5. Identidade, variantes e relações multijogo

### 5.1 Identificadores

Cada registro deverá distinguir:

- `canonical_id`: identidade conceitual compartilhada entre fontes ou jogos, quando a equivalência estiver comprovada.
- `source_id`: identificador original do recurso, como `RESREF`, blueprint ou identificador interno.
- `source_instance_id`: ocorrência específica em campanha, módulo, save ou área.
- `variant_of`: relação opcional com entidade ou variante conceitual relacionada.

Os identificadores deverão ser estáveis, únicos e independentes do nome exibido. Renomear uma entidade não deverá quebrar referências existentes.

### 5.2 Entidades compartilhadas entre jogos

- Cada ficha de origem deverá ser preservada separadamente.
- Uma identidade conceitual compartilhada poderá relacionar os registros.
- Diferenças de atributos, nível, classe, equipamento, habilidades e aparência deverão permanecer explícitas.
- A equivalência deverá registrar evidência e nível de confiança.
- Registros apenas semelhantes não deverão ser fundidos automaticamente.

### 5.3 Instâncias e aparições

A enciclopédia deverá distinguir o blueprint ou modelo de uma entidade de suas aparições concretas. Um NPC pode possuir mais de um recurso ou versão; uma criatura pode aparecer em diversas áreas; um item pode existir como definição e aparecer em inventários, baús ou comerciantes; uma facção pode possuir membros e sedes em localidades diferentes. As relações deverão ser armazenadas por referência, evitando duplicar a ficha completa em cada ocorrência.

## 6. Organização proposta no repositório

```text
knowledge/
├── encyclopedia/
│   ├── manifest.json
│   ├── sources.json
│   ├── schemas/
│   │   ├── character.schema.json
│   │   ├── creature.schema.json
│   │   ├── item.schema.json
│   │   ├── spell.schema.json
│   │   ├── race.schema.json
│   │   ├── class.schema.json
│   │   ├── faction.schema.json
│   │   ├── quest.schema.json
│   │   ├── event.schema.json
│   │   └── location.schema.json
│   ├── characters/{bg1,sod,bg2,tob,iwd1,iwd2,nwn}/
│   ├── creatures/{bg1,sod,bg2,tob,iwd1,iwd2,nwn}/
│   ├── items/
│   ├── spells/
│   ├── abilities/
│   ├── races/
│   ├── classes/
│   ├── factions/
│   ├── quests/
│   ├── events/
│   ├── locations/
│   └── indexes/
└── npcs/
    └── ...
```

Esta estrutura é uma proposta lógica, não autorização para mover ou substituir imediatamente diretórios existentes. Antes de qualquer migração, deverão ser identificados os consumidores atuais de `knowledge/npcs/` e outros caminhos já utilizados.

### 6.1 Estratégia de armazenamento

- Personagens importantes e NPCs com identidade própria poderão ter arquivos individuais.
- Criaturas poderão ser agrupadas por jogo, família ou espécie quando isso facilitar manutenção e revisão.
- Itens e magias poderão ser agrupados por jogo e categoria, respeitando limites de tamanho e revisão.
- Índices deverão permitir localizar registros por nome, identificador, jogo, expansão, categoria, área, facção e relações.
- Dados derivados ou índices gerados deverão ser reproduzíveis a partir dos registros-fonte.
- Não deverá existir um único arquivo monolítico contendo toda a enciclopédia.

## 7. Proveniência, direitos e integridade

### 7.1 Proveniência por registro e campo

Cada registro deverá identificar suas fontes. Quando campos relevantes vierem de fontes diferentes, a proveniência deverá poder ser associada ao campo ou grupo de campos.

Metadados mínimos: fonte e URL; jogo, expansão e versão; identificador do recurso original; ferramenta e versão do extrator; data da extração; hash do recurso quando aplicável; estado de validação; observações sobre divergências.

### 7.2 Direitos autorais e distribuição

- Não incluir arquivos binários proprietários dos jogos no repositório público.
- Não espelhar integralmente recursos gráficos, áudio, modelos, mapas ou diálogos protegidos.
- Armazenar identificadores, metadados factuais, atributos estruturados e referências de origem, respeitando a legislação e os termos aplicáveis.
- Registrar licença, permissões e restrições de cada fonte comunitária.
- Manter recursos locais de laboratório fora do repositório público quando necessário.
- Não classificar uma fonte como reutilizável sem verificação específica de seus direitos.

### 7.3 Integridade e atualização

- Registros aprovados deverão possuir histórico de alterações.
- Extrações repetidas deverão ser idempotentes.
- Mudanças em uma fonte não deverão sobrescrever silenciosamente curadoria manual.
- Divergências deverão ser registradas para revisão.
- Índices gerados deverão indicar a versão dos registros que os originaram.

## 8. Estados de validação

- `DISCOVERED`: identificado em uma fonte, ainda sem extração confirmada.
- `EXTRACTED`: extraído de arquivo ou fonte estruturada.
- `CROSS_REFERENCED`: comparado com uma ou mais fontes independentes.
- `SOURCE_VERIFIED`: conferido com o recurso original ou documentação primária.
- `CURATED`: normalizado e revisado por curadoria.
- `APPROVED`: aprovado para utilização pelos consumidores definidos do Infinity AI.
- `DISPUTED`: existem divergências não resolvidas.
- `RESTRICTED`: uso limitado por licença, direitos, privacidade ou outra restrição.

O estado de validação não substitui metadados de licença ou compatibilidade. Um registro `SOURCE_VERIFIED` não é automaticamente `APPROVED` nem `RIGHTS_CLEARED`.

## 9. Requisitos normativos (EARS)

- **REQ-ENC-001:** QUANDO uma entidade for catalogada, DEVERÁ pertencer a uma das oito categorias definidas nesta SPEC ou a uma subcategoria formalmente aprovada.
- **REQ-ENC-002:** QUANDO um registro for criado, DEVERÁ possuir identificador estável e metadados de origem suficientes para rastrear jogo, expansão e recurso de origem, quando disponíveis.
- **REQ-ENC-003:** QUANDO uma entidade aparecer em mais de um jogo, o sistema DEVERÁ preservar fichas específicas por fonte e só DEVERÁ relacioná-las a uma identidade compartilhada mediante evidência documentada.
- **REQ-ENC-004:** QUANDO dados de versões ou sistemas de regras divergirem, o sistema DEVERÁ preservar as variantes e NÃO DEVERÁ sobrescrever uma versão com dados de outra.
- **REQ-ENC-005:** QUANDO um registro não possuir determinado atributo na fonte, o sistema DEVERÁ representá-lo como ausente ou desconhecido, sem inventar um valor.
- **REQ-ENC-006:** QUANDO uma entidade possuir aparições em áreas, campanhas ou módulos, o sistema DEVERÁ registrar referências às instâncias sem duplicar desnecessariamente sua ficha.
- **REQ-ENC-007:** QUANDO uma fonte comunitária for utilizada, o registro DEVERÁ incluir identificação, URL, data de consulta e condições de uso conhecidas.
- **REQ-ENC-008:** QUANDO houver dúvida sobre licença ou permissão, o recurso DEVERÁ permanecer restrito para reutilização até revisão.
- **REQ-ENC-009:** QUANDO um dado for extraído automaticamente, o sistema DEVERÁ registrar a ferramenta e a versão do processo de extração.
- **REQ-ENC-010:** QUANDO uma extração for repetida com a mesma fonte e versão, o processo DEVERÁ ser idempotente e NÃO DEVERÁ duplicar registros.
- **REQ-ENC-011:** QUANDO uma atualização de fonte alterar dados já curados, o sistema DEVERÁ sinalizar a divergência e preservar a revisão anterior até aprovação.
- **REQ-ENC-012:** QUANDO a categoria 08 referenciar áreas, DEVERÁ utilizar os identificadores e estados da SPEC-010, evitando manter inventário geográfico conflitante.
- **REQ-ENC-013:** QUANDO a enciclopédia for consumida pela SPEC-008, o sistema DEVERÁ distinguir dados catalogados de conhecimento efetivamente adquirido por cada NPC.
- **REQ-ENC-014:** QUANDO o runtime consultar uma entidade, DEVERÁ respeitar campanha, ramo, cronologia, fonte, versão e estado de aprovação aplicáveis.
- **REQ-ENC-015:** QUANDO um NPC ou criatura possuir ficha original em diferentes jogos, o sistema DEVERÁ manter os atributos específicos de cada origem e não aplicar conversão implícita.
- **REQ-ENC-016:** QUANDO um registro for aprovado, DEVERÁ passar pela validação do schema correspondente e pelas verificações de integridade referencial.
- **REQ-ENC-017:** QUANDO um registro fizer referência a outro registro, o destino DEVERÁ existir ou a referência deverá ser explicitamente marcada como pendente.
- **REQ-ENC-018:** QUANDO textos protegidos forem encontrados nas fontes, o repositório NÃO DEVERÁ armazenar sua reprodução integral sem autorização adequada.
- **REQ-ENC-019:** QUANDO um registro for criado ou alterado manualmente, o autor, a data e a justificativa da alteração DEVERÃO ser rastreáveis.
- **REQ-ENC-020:** QUANDO uma categoria receber novos campos, o schema deverá ser versionado e os registros anteriores deverão continuar interpretáveis ou receber migração explícita.

## 10. Integração com as SPECs existentes

| Documento | Responsabilidade | Integração com SPEC-012 |
|---|---|---|
| SPEC-005 | Cânone, cronologia e proveniência do mundo | Define contexto histórico e validação canônica de fatos |
| SPEC-006 | Identidade, personalidade e alinhamento dos NPCs | Consome identidade e ficha de origem, sem substituir a curadoria psicológica |
| SPEC-007 | Relações e sistemas relacionados, conforme escopo vigente | Consome referências de personagens e facções |
| SPEC-008 | Biografia, conhecimento individual e aprendizado dos NPCs | Usa o catálogo como referência; não presume que todo dado catalogado seja conhecido pelo NPC |
| SPEC-009 | Confiança, sigilo e política de divulgação | Usa referências de identidade e conteúdo, mas determina o que pode ser revelado |
| SPEC-010 | Inventário geográfico e áreas reutilizáveis | Compartilha identificadores de localidades, áreas e recursos |
| **SPEC-012** | Enciclopédia multijogo | Mantém os oito subcatálogos e suas relações |

### 10.1 Catálogo não é conhecimento individual

A enciclopédia poderá conter informações sobre uma cidade, personagem, criatura ou acontecimento que um NPC específico desconhece. A SPEC-008 continuará determinando o que cada NPC sabe, ouviu, suspeita ou aprendeu, com base em origem, experiência, memória e evidência. A SPEC-012 não concederá conhecimento automaticamente a nenhum NPC.

### 10.2 Identidade não é biografia

A ficha técnica descreve os dados disponíveis no recurso de origem. A biografia canônica ou criada, os eventos pessoais, a privacidade e a memória de campanha continuam sob as regras de curadoria e conhecimento aplicáveis, especialmente SPEC-005 e SPEC-008.

## 11. Plano de implementação

A implementação deverá ocorrer de forma incremental, sem antecipar migrações que quebrem os sistemas atuais.

### Fase 1 — Fundação

- [ ] Auditar diretórios e schemas já existentes no repositório.
- [ ] Definir `manifest.json`, `sources.json` e convenções de identificadores.
- [ ] Criar schemas versionados para as oito categorias.
- [ ] Definir política de proveniência, licenças e dados restritos.
- [ ] Criar testes de validação estrutural e integridade referencial.

### Fase 2 — Personagens e NPCs

- [ ] Inventariar os registros existentes em `knowledge/npcs/`.
- [ ] Mapear NPCs e personagens de BG1 e Siege of Dragonspear.
- [ ] Confrontar TH.GL com os arquivos originais.
- [ ] Mapear BG2 e Throne of Bhaal usando Planet Baldur's Gate, GameBanshee e extração.
- [ ] Mapear NPCs e personagens de IWD1, expansões e IWD2.
- [ ] Extrair e catalogar blueprints e instâncias de NWN e expansões.
- [ ] Resolver identidades compartilhadas e variantes sem apagar fichas por jogo.

### Fase 3 — Criaturas

- [ ] Extrair recursos de criaturas dos jogos da Infinity Engine.
- [ ] Extrair blueprints e instâncias de criaturas de NWN.
- [ ] Classificar famílias, espécies, subtipos e variantes.
- [ ] Relacionar criaturas às áreas em que aparecem.
- [ ] Validar fichas e diferenças entre jogos.

### Fase 4 — Itens e equipamentos

- [ ] Extrair itens e equipamentos de BG1, SoD, BG2, ToB, IWD1, IWD2 e NWN.
- [ ] Classificar tipos, propriedades, requisitos e efeitos.
- [ ] Relacionar itens a personagens, criaturas, comerciantes, tesouros e áreas.
- [ ] Deduplicar conceitos sem apagar implementações específicas.

### Fase 5 — Magias, habilidades, raças e classes

- [ ] Catalogar magias e habilidades por jogo.
- [ ] Catalogar raças, sub-raças, classes, kits e regras.
- [ ] Registrar diferenças de implementação e sistemas de regras.
- [ ] Relacionar habilidades a personagens e criaturas.

### Fase 6 — Facções, missões e acontecimentos

- [ ] Catalogar facções e organizações.
- [ ] Relacionar membros, líderes, sedes, aliados e rivais.
- [ ] Catalogar missões e acontecimentos por campanha e cronologia.
- [ ] Preservar ramificações e consequências específicas de cada campanha.

### Fase 7 — Áreas e localidades

- [ ] Integrar os registros da SPEC-010.
- [ ] Relacionar personagens, criaturas, itens, facções e missões às áreas.
- [ ] Validar referências pendentes e duplicidades.
- [ ] Gerar índices de consulta geográfica e por campanha.

### Fase 8 — Consolidação e consumo

- [ ] Gerar índices de busca por nome, identificador, jogo, categoria e relação.
- [ ] Implementar consultas de leitura sem alterar os dados-fonte.
- [ ] Integrar os consumidores previstos, respeitando suas SPECs.
- [ ] Executar testes de regressão e validação no laboratório.
- [ ] Documentar cobertura, lacunas e limitações conhecidas.

## 12. Critérios de aceite

A fundação desta SPEC será considerada implementada quando:

1. As oito categorias possuírem schemas versionados e documentação.
2. O manifesto e o registro de fontes estiverem operacionais.
3. Os registros preservarem jogo, expansão, versão e identificador de origem.
4. A validação detectar campos inválidos, identificadores duplicados e referências quebradas.
5. A extração repetida não gerar duplicidades.
6. Entidades compartilhadas preservarem fichas específicas por jogo.
7. Registros sem evidência suficiente permanecerem pendentes ou não verificados.
8. As regras de proveniência e direitos estiverem aplicadas.
9. A integração com SPEC-008 não conceder conhecimento automático aos NPCs.
10. A categoria geográfica utilizar a SPEC-010 como fonte de referência.
11. O inventário existente de NPCs continuar compatível durante a transição.
12. O laboratório conseguir consultar catálogos aprovados sem modificar os recursos originais dos jogos.

A conclusão de uma fase não significa que todas as entidades de todos os jogos foram inventariadas. A cobertura deverá ser publicada por jogo, expansão, categoria e estado de validação.

## 13. Governança e limites

- Esta SPEC é uma diretriz de inventário e organização; não autoriza por si só implementação no runtime, migração destrutiva, instalação de mods ou redistribuição de recursos.
- Mudanças estruturais deverão seguir o processo de CR/ADR aplicável.
- A aprovação de uma fonte ou registro deverá ser rastreável.
- A cobertura incompleta deverá ser declarada explicitamente.
- Nenhuma entidade, ficha, biografia, relação ou evento deverá ser inventado para preencher lacunas do inventário.
- Conteúdo criado para campanhas do Infinity AI deverá ser distinguido do conteúdo original dos jogos e do cânone publicado.
- Novas categorias somente poderão ser adicionadas por revisão formal, preservando o princípio de catálogo modular e integrado.

## Apêndice A — Exemplo ilustrativo de registro

O exemplo demonstra a estrutura conceitual. Campos não conhecidos devem permanecer ausentes ou nulos; os valores ilustrativos não constituem uma ficha validada.

```json
{
  "canonical_id": "character:example",
  "display_name": "Example Character",
  "category": "CHARACTER",
  "source_records": [
    {
      "source_game": "BG2",
      "source_expansion": "SOA",
      "source_id": "EXAMPLE",
      "source_version": "UNVERIFIED",
      "verification_status": "DISCOVERED"
    }
  ],
  "variant_of": null,
  "relationships": [],
  "appearance_refs": [],
  "source_refs": []
}
```

## Apêndice B — Glossário de termos

- **Catálogo:** conjunto estruturado de registros de uma categoria.
- **Entidade canônica:** identidade conceitual usada para relacionar registros equivalentes, quando a equivalência está comprovada.
- **Registro de origem:** representação de uma entidade em determinado jogo, expansão e versão.
- **Blueprint:** definição reutilizável de personagem, criatura, item ou outro recurso, conforme a engine.
- **Instância:** ocorrência concreta de um recurso em uma área, campanha ou módulo.
- **RESREF:** identificador interno de recurso utilizado por jogos da Infinity Engine.
- **Proveniência:** informação que permite rastrear a origem de um dado.
- **Curadoria:** revisão humana e documentada para normalizar ou aprovar um registro.
- **Variante:** versão distinta de uma entidade, que pode diferir em atributos, aparência, regras ou contexto.

---

**Fim da SPEC-012 — Enciclopédia Multijogo: Personagens, Criaturas e Recursos.**
