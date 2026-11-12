# SPEC-006 — Matriz de personalidade e alinhamento de NPCs

**Status:** PROPOSTA para revisão do mantenedor (2026-11-09). O gerador inicial e seus testes são **somente sintéticos**; não há integração com jogo, memória persistida, LLM ou ações mecânicas.
**Origem:** solicitação do mantenedor em 2026-11-09 para individualizar NPCs, integrar alinhamento de AD&D e documentar perfis.
**Governança:** ADR-0115 (proposto), ADR-0122 (proposto); ADR-0018, ADR-0030/0031/0032, ADR-0042/0059/0062/0113/0114/0116/0117/0119/0120; SPEC-003 (memória e save), SPEC-004 (fala/personas), SPEC-005 (cânone).

## Objetivo

Cada NPC deve ter um perfil **persistente, individualizado, reproduzível e auditável**, responsável por tendências de fala, prioridades, reações e propostas narrativas. A personalidade não substitui fatos, conhecimento adquirido, classe, reputação, alinhamento do motor ou a soberania do host. Uma reação diferente de dois NPCs ao mesmo evento exige percepção e conhecimento legítimos, não acesso ao estado global.

## Matriz principal

### Camada P0 — identidade (ADR-0117)

Quem o NPC é: nome, ofício, onde vive, de onde veio e por onde passou. A precedência é curadoria do mantenedor (`knowledge/npcs/`) > dados do jogo (ficha CRE, área, papel no nome) > geração fechada para genéricos (vocabulário de ofícios e só regiões do pacote canônico; nunca pessoas nem acontecimentos). Persiste como a personalidade: `CANONICAL` sem geração, `CANDIDATE` temporária por instância, `VERIFIED` gravada no `NpcPersonalityAssigned`. No diálogo, vira fatos "SOBRE VOCÊ"; o NPC só afirma sobre si o que está neles. Código: `src/infinity_ai/personality/identity.py`.

### Camada P1 — seis eixos psicológicos (0–100)

A nomenclatura inspira-se nos seis domínios do **HEXACO** (Lee/Ashton; https://www.hexaco.org/scaledescriptions), sem utilizar, reproduzir ou distribuir o questionário HEXACO-PI-R. Os valores são parâmetros **ficcionais**, não escores de teste ou diagnósticos humanos.

| Chave | Domínio | Tendência no extremo baixo | Tendência no extremo alto |
|---|---|---|---|
| `honesty_humility` | Honestidade-Humildade | Instrumentalidade/autoimportância | Sinceridade/modéstia/equidade |
| `emotionality` | Emocionalidade | Menor preocupação/necessidade de amparo | Sensibilidade, apego, cautela emocional |
| `extraversion` | Extroversão | Reserva social | Sociabilidade/expressividade |
| `agreeableness` | Amabilidade (vs. raiva) | Impaciência/ressentimento | Paciência/perdão/flexibilidade |
| `conscientiousness` | Conscienciosidade | Espontaneidade/menor planejamento | Organização/prudência/diligência |
| `openness` | Abertura à experiência | Preferência pelo familiar | Curiosidade/criatividade |

Os extremos não são "classes", não impõem condutas universais e não autorizam inferir alinhamento, crime, inteligência ou moralidade. Facetas finas, vieses, estilos de humor e contradições pessoais são expansões versionadas futuras.

### Camada P2 — alinhamento AD&D 2e: dois eixos e nove possibilidades

É **parte obrigatória do perfil inicial** dos NPCs criados, mas é um campo separado dos seis traços. Eixo ético: `LAWFUL`, `NEUTRAL`, `CHAOTIC`; eixo moral: `GOOD`, `NEUTRAL`, `EVIL`.

| Ética / Moral | GOOD | NEUTRAL | EVIL |
|---|---|---|---|
| LAWFUL | LG | LN | LE |
| NEUTRAL | NG | TN | NE |
| CHAOTIC | CG | CN | CE |

O alinhamento descreve convicções e orientação narrativa; não é uma fórmula `H → GOOD`, `C → LAWFUL`, nem equivale à reputação ou obediência a uma lei local. É possível um NPC organizado/disciplinado e Caótico, ou um NPC cordial e Mau, quando houver motivação coerente. A distribuição inicial pode ter pesos por cenário e papel **explicitamente curados** (não estereótipos por raça, cultura ou deficiência). Distribuição uniforme é apenas default experimental; não representa população canônica.

Distinguir `alignment_initial` (origem/curadoria), `alignment_projection` (orientação narrativa dinâmica auditável, ADR-0030/31) e `engine_alignment` (atributo mecânico observado pelo jogo). **Jamais escrever `engine_alignment` automaticamente.** Restrições de classe/kit requerem validação separada (ADR-0032).

### Camada P3 — valores, motivações e vulnerabilidades

Três `values` ordenados (ex.: justiça, poder, tradição, autonomia, comunidade); duas `drives` (ex.: proteção, reconhecimento, descoberta) e duas `vulnerabilities` (ex.: traição, perda, rejeição). O gerador de personalidade escolhe rótulos abstratos e **não inventa eventos passados, crenças adquiridas nem segredos sobre terceiros**. O histórico mínimo (ofício, origem, tempo no lugar, lugares por onde passou) é da camada P0, com vocabulário fechado (ADR-0117). A curadoria pode acrescentar objetivos, vínculos, tabu, estilo de fala e contradições com justificativa narrativa; são metadados privados com ACL própria.

### Camada P4 — estado dinâmico (futuro)

Emoções temporárias, relações por observador, memórias, crenças, estresse, confiança e alinhamento projetado mudam **somente a partir de eventos/experiências elegíveis**, em campanha/branch/epoch. Mudanças graduais exigem regras e evidência; LLM não altera estado, não inventa intenção, não aplica penalidade e não reescreve passado. O estado-base não é re-sorteado durante a campanha.

## Fontes e política de identidade

1. **Companheiro/NPC oficial identificado:** `origin=CANONICAL`; alinhamento e traços iniciais por fonte conferida no manual/instalação, sob SPEC-005. Se desconhecido, marcar `UNKNOWN`; nunca sortear para preencher lacuna. A personalidade pode evoluir por acontecimentos legítimos, respeitando scripts, romances e arcos existentes (ADR-0042).
2. **NPC original criado pelo Infinity AI:** `origin=CREATED`, identidade exclusiva `npc:generated:<id>`, perfil sorteado **uma única vez na criação**, armazenado em snapshot versionado.
3. **NPC genérico de jogo promovido:** só individualizar após gate de identidade positiva (ADR-0062). O vínculo com NPC oficial/observado exige proveniência, não se resolve com nome visual. Perfil provisório não equivale a identidade persistente.

## Sorteio e persistência

`src/infinity_ai/personality/generator.py` implementa um primeiro gerador **puro e sintético**:
- Entradas: `world_seed`, `campaign_id`, `creation_branch_id`, `npc_id`, `npc_origin=CREATED`, `alignment_weights` opcionais, versão de política. A semente é derivada por hash desses campos; não depende do RNG global.
- Seis traços inteiros de 0–100 sorteados por distribuição triangular centrada em 50 (heurística ficcional, **não psicometria validada**).
- Um dos nove alinhamentos por amostragem categórica independente, com pesos não negativos e soma positiva; perfil não força relação causal entre alinhamento e traços.
- Valores/motivações/vulnerabilidades escolhidos de vocabulários fechados e curados.
- Saída: snapshot JSON `infinity-ai.personality.v1`, `generator_version`, fingerprint da semente, campanha/ramo de criação, `alignment_initial` e fatores.
- **Persistência ainda pendente:** o orquestrador deverá gravar o snapshot uma vez em registro append-only, com idempotência e prova de identidade. Recarregar save, trocar versão ou reabrir sessão **nunca** deve rerrolar um NPC já criado. Ramo filho herda perfil anterior ao fork; NPC novo criado após fork tem identidade/ramo próprio; evitar colisões.
- O gerador sozinho não garante identidade nem armazenamento: estes são gates futuros do serviço de criação, sob ADR-0062 e SPEC-003.

## Reação social e moral: contrato futuro (ADR-0122; não implementado)

A reação deverá seguir o fluxo:

evento confirmado → exposição/ACL → crenças e memórias legítimas → perfil-base + estado atual + relação → solução contextual → Reaction Table 59 quando houver incerteza → Morale Check somente quando houver gatilho → política de comportamento validada → fala local via SPEC-004.

### Separação dos mecanismos

1. **Solução contextual:** primeira opção. Se fatos, scripts, objetivos e personalidade já determinarem uma reação coerente, não rolar dados.
2. **Reaction nativa do BG2:EE:** Reaction() usa a escala nativa 10 + rmodchr + rmodrep. É um sinal do motor, não a Table 59. Não converter em categorias nem combinar com novos modificadores até validar sua leitura e calibração na build pinada.
3. **Encounter Reaction (AD&D 2e, DMG Table 59):** quando a disposição permanecer incerta, rolar 2d10, escolher a coluna segundo a conduta observável dos personagens jogadores (FRIENDLY, INDIFFERENT, THREATENING, HOSTILE) e aplicar os modificadores pertinentes. Resultados: FLIGHT, FRIENDLY, INDIFFERENT, CAUTIOUS, THREATENING, HOSTILE. Ajuste positivo de reação por Carisma melhora o resultado (subtrai-se o bônus positivo do total); não contar Carisma/reputação duas vezes quando já incorporados no sinal nativo.
4. **Morale Check (AD&D 2e, DMG Tables 49–50 e capítulo de NPCs):** rolar 2d10 apenas diante de gatilho relevante. Total igual ou inferior à moral modificada = mantém a determinação; total maior = falha e toma uma resposta contextual (ceder à tentação, evitar, recuar, fugir, render-se ou outra saída coerente). Falhar diante de uma tentação significa ceder à tentação relevante, não necessariamente confessar ou agir de imediato.
5. **Personalidade, alinhamento e relações:** influenciam a escolha contextual, a interpretação e a expressão da disposição; não são substitutos uns dos outros.

### Influência de P1–P4

- **P1 (HEXACO ficcional):** influencia tom, expressividade, paciência, cautela, franqueza e a coerência psicológica da resistência. Não converter diretamente pontos HEXACO em modificadores AD&D sem uma tabela própria, versionada, calibrada e testada.
- **P2 (alinhamento AD&D):** aplica modificadores oficiais apenas quando a tabela e o contexto os autorizarem. Lawful/Chaotic e Good/Evil não são rótulos automáticos de simpatia ou hostilidade. Não duplicar Lawful/Chaotic entre Table 50 e Table 71; UNKNOWN não recebe modificador inventado.
- **P3 (valores, motivações e vulnerabilidades):** informa quais tentações, ameaças e conflitos têm significado para o NPC, somente se os dados estiverem em seu perfil autorizado.
- **P4 (relações, memória e estado):** tratamento recebido, confiança, lealdade e experiências podem influenciar o resultado quando registrados e visíveis no ramo; reutilizar ADR-0119 e SPEC-003.

O valor-base de moral deve vir de estatística efetiva do motor, CRE local validado ou categoria DMG comprovada. Morale Break não deve ser tratado automaticamente como o valor de moral AD&D. Se a proveniência ou categoria não estiver resolvida, não inventar um número: usar solução contextual ou MORALE_UNRESOLVED. As seções/tabelas do DMG para criaturas e para NPCs associados a personagens têm contextos diferentes; não criar um valor universal para todo habitante, empregado ou trabalhador.

### Gatilhos e estabilidade

Gatilhos possíveis para Morale Check incluem perigo claramente superior, perdas relevantes, líder derrotado, tarefa heroicamente perigosa, tentação (suborno, oportunidade de roubo, injustiça, vingança ou conflito com empregador), retaguarda e rendição quando as condições se aplicarem. Não rolar em toda ameaça, pergunta ou tentativa de persuasão. O DMG recomenda não deixar os dados sobrepor lógica e drama.

A disposição da Table 59 fica estável durante o mesmo episódio de interação. Não rerrolar a cada pergunta. Nova avaliação exige novo encontro ou mudança contextual relevante. Um Morale Check é idempotente por gatilho; repetição da mesma requisição não produz uma nova rolagem.

### Identidade, eventos e autoridade

- NPCs CANDIDATE/efêmeros mantêm a avaliação somente no escopo seguro da instância/sessão/cena; não criam identidade, relação ou memória persistente.
- NPCs VERIFIED seguem os gates de identidade, ramo e eventos da SPEC-003/ADR-0061/0062/0119.
- Eventos candidatos: NpcEncounterReactionResolved e NpcMoraleCheckResolved; categoria, visibilidade e persistência serão validadas com SPEC-003 antes da implementação.
- Registrar tabela/versão, gatilho, dados rolados, modificadores, proveniência do valor-base e resultado. Não registrar texto de diálogo desnecessário.
- Não executar Morale Check para personagens controlados pelos jogadores.
- Scripts, quests, banters e diálogos nativos prevalecem. Nenhuma reação autoriza escrita em CRE, alteração de engine_alignment, reputação, save ou ação mecânica.
- Código determinístico escolhe gatilho, calcula modificadores, rola e registra. A LLM recebe a disposição já resolvida e apenas formula a fala a partir do conhecimento autorizado; não decide dados, moral, fatos ou ações.

### Limites técnicos atuais

O parser CRE atual expõe alinhamento, Sabedoria e Inteligência, mas ainda não expõe Carisma, Morale ou Morale Break. A leitura desses campos no CRE e em EEex_Sprite_GetActiveStats, assim como a observação confiável do personagem iniciador, exige POC na build BG2:EE pinada. Até essa validação, os valores não podem ser presumidos.

Exemplo hipotético: uma autoridade local exige que o grupo denuncie um inocente. Um NPC Leal e Bom pode tentar contestar a ordem por vias institucionais; outro Caótico e Bom pode desobedecer e proteger a vítima; um Leal e Mau pode explorar a ordem em benefício próprio. A disposição pode modular a fala, mas o NPC precisa conhecer o incidente, ter motivos e avaliar riscos. Nenhum rótulo isolado garante uma fala ou ação.

Fala, recusa, comércio, mudança de facção, deserção, combate, assassinato, revelação de segredo ou alteração do jogo têm gates diferentes. LLM só ajuda a formular texto; o host tem autoridade mecânica e ações HIGH exigem aprovação.

## Requisitos EARS e critérios de aceite

- **REQ-PERS-001:** QUANDO NPC original for criado, gerar perfil com seis traços 0–100, alinhamento de duas dimensões, valores, motivações, vulnerabilidades e proveniência.
- **REQ-PERS-002:** QUANDO a mesma identidade/seed/política for simulada, gerar perfil idêntico; QUANDO o perfil já tiver sido persistido, usar snapshot sem novo sorteio.
- **REQ-PERS-003:** SE o NPC for canônico ou sua identidade for incerta, NÃO sortear alinhamento/perfil no lugar da curadoria.
- **REQ-PERS-004:** SE pesos de alinhamento forem inválidos/ausentes do conjunto esperado, falhar com erro tipado; nunca interpretar HEXACO como alinhamento.
- **REQ-PERS-005:** QUANDO houver save/load/fork, respeitar ramo, tempo de criação, proveniência, política e idempotência.
- **REQ-PERS-006:** QUANDO o NPC reagir, usar apenas fatos legitimamente conhecidos e perfil autorizado; não revelar objetivos privados, segredos ou nomes não adquiridos.
- **REQ-PERS-007:** QUANDO alinhamento evoluir, usar acontecimentos confirmados, versão de regra e contexto (ADR-0030/31); NÃO alterar automaticamente atributo mecânico ou reputação.
- **REQ-PERS-008:** QUANDO LLM falhar, preservar perfil/estado e fornecer resposta neutra de fallback; nunca permitir mutação de jogo.
- **REQ-PERS-009:** QUANDO NPC oficial possuir restrições de classe, preservar compatibilidade e bloquear mudanças mecânicas até POC e autorização.

**Aceite atual:** gerador puro, primeiro contato por evento sintético observado, perfil efêmero, snapshot persistente append-only para identidade verificada, diálogo genérico sintético, testes de ramificação/fallback; ainda sem prova de clique no jogo. **Pendente:** identidade verificada por engine, interceptação de qualquer pessoa, curadoria canônica, evolução, alinhamento mecânico e POC real BG2:EE/EEex.

## Extensão aprovada como intenção de produto — NPC é qualquer pessoa encontrada

**Esclarecimento do mantenedor (2026-11-09):** NPC não significa somente companheiro, inimigo, aventureiro ou personagem nomeado. Inclui habitantes comuns, pessoas nas ruas, mendigos, camponeses, guardas, vendedores, viajantes e outros atores presentes numa cena. A intenção é que o jogador possa iniciar uma interação com qualquer pessoa *realmente apresentada pelo jogo ou pelo sistema de encontros autorizado*, mesmo que o jogo original não tenha diálogo roteirizado. Isso **não comprova** a existência de um hook de clique ou capacidade de dialogar com todos os CREs de BG2:EE; tal integração exige uma POC específica, autorização e proteção de scripts/diálogos originais.

### Provisionamento preguiçoso (lazy) no primeiro diálogo

1. Não gerar nem executar LLM para todos os transeuntes. O adaptador de observação deverá emitir `NpcDialogueStarted` **somente após um clique/interação de diálogo efetivamente reconhecido**, com tempo, cena, sessão, alvo visível, permissão e estado de identidade.
2. Verificar o evento gravado no banco **pelo lado confiável do servidor**. Um texto do jogador ou um campo arbitrário de HTTP não é evidência de alvo nem de identidade. Se observação ausente/inválida, falhar fechado.
3. **NPC canônico/roteirizado:** `CANONICAL` conserva persona/alinhamento do jogo; nunca sobrescrever o diálogo do jogo sem regra de compatibilidade.
4. **Pessoa não identificada** (`CANDIDATE`, `AMBIGUOUS`, `STALE`): gerar personalidade e alinhamento **temporários para o encontro**, sem recuperar memória pessoal de outro ator, sem criar identidade permanente nem registrar `NpcPersonalityAssigned`. Se o adaptador provar token único no escopo da sessão/cena, contatos subsequentes ali reutilizam o perfil; se não, **cada interação é independente**.
5. **Pessoa de identidade verificada** (`VERIFIED`): exigir evento `NpcIdentityVerified` anterior, visível no ramo, compatível com NPC, sessão, área e instância. Recuperar `NpcPersonalityAssigned` já visível ou gravar uma única atribuição append-only contendo snapshot e prova. Uma restauração herda somente o passado admitido pela linha do tempo e um fork anterior não herda evento posterior.
6. O `role` é rótulo observável controlado (`BEGGAR`, `COMMONER`, `PEASANT`, `MERCHANT`, `GUARD`, `TRAVELER`, `ARTISAN`, `NOBLE`, `OTHER`), **não** biografia presumida, status moral, profissão comprovada, fonte de conhecimento ou distribuição de alinhamento. O comportamento pode ser coerente com o perfil sem estereotipar pobreza, cultura ou condição social.
7. O primeiro diálogo usa persona gerada com estilo/valores/alinhamento **como orientação de fala**, não como fonte de fatos. Sem conhecimento/episódios conferidos, o sistema deve reconhecer que não sabe. Segurança, segredos e ações no jogo continuam separados.
8. Crescer em importância (reencontro, missão, amizade, comércio, rumor ou promessa) pode gerar **candidatura** à promoção, mas só uma identificação `VERIFIED` comprovada autoriza perfil persistente, relações e memória privada (ADR-0061/0062). Não migrar automaticamente lembranças efêmeras para a nova identidade.

### Contratos sintéticos implementados

- `src/infinity_ai/personality/first_contact.py`: `FirstContactService.begin(contact_event_id, branch_id, at_game_time)`, requer observação válida, trata canônicos, encontro temporário e perfil persistente.
- Eventos da camada de estado já existente (sem migração SQL nova): `NpcDialogueStarted` (`CAMPAIGN_OBSERVATION`), `NpcIdentityVerified` e `NpcPersonalityAssigned` (`CAMPAIGN_FACT`), no armazenamento append-only da SPEC-003.
- `src/infinity_ai/personality/encounter_dialogue.py`: `NpcEncounterDialogue` com `LlmProvider` local/falso, validação de saída e fallback; não substitui a conversa do jogo por padrão e **não registra transcrições**.
- `tools/windows-lab/dialogue_service.py`: rota autenticada `POST /v1/encounter-dialogue`, recebendo somente `contact_event_id` e `text`, após observação já registrada e conferência de área; **não cria** observações nem expõe um endpoint para inventar identidades/perfis.
- `tests/test_first_contact.py`: cenários sintéticos de mendigo, camponês, guarda e demais papéis, estabilidade/isolamento de encontro, ambiguidade, canonicidade, prova de identidade, persistência, save/load/fork, segurança e LLM indisponível.

### POC necessária para interação de qualquer pessoa em BG2:EE

Ainda **não existe** detecção validada do clique em qualquer CRE nem evento `NpcDialogueStarted` vindo de EEex. O probe vigente informa apenas área, tempo e integrantes da party. O comportamento ao clicar num figurante sem diálogo no jogo deve ser inspecionado em uma cópia descartável e em build pinada. Gate proposto: observar alvo e início de diálogo sem bloquear banters/quests originais; impedir colisões de IDs de instâncias e interface; emitir contato read-only; testar falhas, save/load, mudança de área e desempenho; somente depois ligar a rota do laboratório a uma UI de interação disponível.
