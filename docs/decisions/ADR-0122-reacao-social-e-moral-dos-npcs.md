# ADR-0122 — Reação social e testes de moral dos NPCs

**Estado:** PROPOSTA — direção arquitetural aceita em princípio pelo mantenedor em 2026-11-11; calibração, contratos finais e POC permanecem pendentes.
**Relaciona-se com:** ADR-0018 (núcleo AD&D 2e), ADR-0030–0032 (alinhamento), ADR-0059 (conhecimento legítimo), ADR-0061/0062 (identidade), ADR-0115 (personalidade, PROPOSTA), ADR-0116 (diálogo no jogo), ADR-0117 (identidade), ADR-0119 (relações), ADR-0120 (estatuto local), SPEC-003, SPEC-004 e SPEC-006.
**Escopo:** disposição social e resistência de NPCs nas interações adicionais do Infinity AI. Não substitui diálogos, scripts, reputação, relações ou decisões nativas do BG2:EE.
**Gate:** primeiro single-player e laboratório S1f; nenhum efeito mecânico ou alteração do jogo é aprovado por esta ADR.

## Contexto

Os testes de Bernard demonstraram que o contexto factual e relacional já consegue fornecer informações sobre Lehtinan e a Coroa de Cobre, mas a resposta ainda depende principalmente da formulação do modelo. Precisamos de um mecanismo determinístico para estabelecer a disposição inicial do NPC e avaliar sua resistência diante de pressão, perigo, tentação ou conflito de lealdade.

O AD&D 2e já separa duas ferramentas que não devem ser confundidas:

- **Encounter Reaction (DMG, Table 59):** orienta a reação de um encontro quando a situação não determina claramente o comportamento. Usa 2d10, a atitude dos personagens jogadores e modificadores aplicáveis.
- **Morale Check (DMG, Tables 49–50 e capítulo de NPCs):** avalia se uma criatura ou NPC mantém sua determinação ou cede/evita uma situação. Usa 2d10 contra um valor de moral modificado e só deve ser acionado quando houver motivo contextual.

O DMG também recomenda primeiro a solução interpretativa: considerar objetivos, personalidade, motivos e fatos conhecidos. Os dados são um recurso auxiliar, não uma autoridade que deva produzir resultados ilógicos.

## Decisão proposta

### 1. Três sinais integrados, com responsabilidades distintas

O sistema deverá combinar:

1. **Reaction nativa do BG2:EE (engine_reaction):** quando puder ser observada de forma confiável, será um sinal proveniente do próprio motor. A documentação do Infinity Engine descreve o trigger Reaction() como uma escala amistoso–hostil calculada por 10 + rmodchr + rmodrep. Ela incorpora os recursos de reação por Carisma e reputação do jogo. Não equivale à rolagem 2d10 da Table 59 e não deve ser convertida em categorias sem calibração.
2. **Encounter Reaction do AD&D 2e (encounter_reaction):** quando a situação não determinar claramente a reação, aplicar a Table 59. Rolar 2d10, selecionar a coluna que corresponde à conduta dos personagens jogadores e aplicar somente modificadores justificados. Os resultados são FLIGHT, FRIENDLY, INDIFFERENT, CAUTIOUS, THREATENING e HOSTILE.
3. **Morale Check (morale_check):** aplicar apenas quando uma situação relevante exigir avaliar determinação, resistência ou tentação. Não é um teste genérico para cada pergunta ou tentativa de persuasão.

A reação nativa do motor, a Table 59 e o Morale Check são sinais complementares, não três rolagens obrigatórias. A política deverá impedir a aplicação duplicada de Carisma ou reputação quando o valor nativo já os incorporar.

### 2. Precedência: interpretação contextual antes dos dados

Antes de qualquer rolagem, o código deverá verificar se a situação e os fatos conhecidos já tornam a reação suficientemente clara.

- Diálogo nativo, script, quest, banter ou fato canônico que determine a resposta prevalece; a camada do Infinity não o substitui.
- Uma ameaça evidente, uma agressão iniciada ou uma oferta manifestamente incompatível com os interesses do NPC pode ter consequência contextual direta, sem rolagem artificial.
- A Table 59 é usada quando a disposição do encontro permanecer genuinamente incerta.
- O Morale Check é usado quando existir um gatilho reconhecido e uma decisão de resistência/cedência ainda não estiver determinada por fatos ou personalidade já estabelecidos.
- O sistema nunca deverá rolar apenas para produzir variedade narrativa.

### 3. Encounter Reaction — Table 59

A Table 59 recebe:

- comportamento observável dos personagens jogadores: FRIENDLY, INDIFFERENT, THREATENING ou HOSTILE;
- resultado de 2d10;
- modificadores da descrição da criatura e os modificadores de moral da Table 50 que realmente se aplicarem;
- ajuste de reação de Carisma do PHB, quando o personagem iniciador estiver identificado e o ajuste não estiver já incorporado em engine_reaction.

Um ajuste positivo de reação deve melhorar a reação: no cálculo da Table 59, subtrai-se o bônus positivo do total; um ajuste negativo piora o total. A implementação deverá testar explicitamente o sinal para impedir inversões.

A classificação da conduta do jogador deve ser determinística e auditável, preferencialmente a partir de ações/eventos estruturados. Texto livre pode ser analisado por regras locais; uma sugestão de LLM não decide a coluna nem o resultado. Se a conduta ou o personagem iniciador não puderem ser determinados com segurança, não inventar dados ausentes: usar a solução contextual ou um comportamento neutro/fallback documentado.

O resultado da Table 59 é uma disposição geral, não uma fala pronta nem uma ordem mecânica. A interpretação deverá respeitar a cena, os objetivos, o conhecimento e os limites do NPC.

### 4. Morale Check — determinação e tentação

A regra-base é:

- obter o valor de moral aplicável, com sua proveniência;
- aplicar os modificadores pertinentes;
- rolar 2d10;
- se o total for igual ou inferior à moral modificada, o NPC mantém sua determinação;
- se o total for maior, falha no teste e toma uma resposta coerente com a situação: ceder à tentação, evitar, recuar, fugir, render-se ou outra consequência contextual apropriada.

Gatilhos possíveis incluem os previstos no DMG: perigo claramente superior, perda de aliados/líder, tarefa heroicamente perigosa, tentação (suborno, oportunidade de roubo, injustiça a corrigir, vingança ou conflito com empregador), ordem de atuar como retaguarda e oportunidade de rendição após condições pertinentes. A lista não autoriza rolar em toda ameaça ou conversa; o contexto e a lógica narrativa continuam prevalecendo.

Em diálogos, o Morale Check poderá avaliar, por exemplo, se Bernard aceita uma oferta para contrariar Lehtinan, se um guarda abandona seu posto diante de risco real ou se um NPC cede a uma tentação que conflita com sua lealdade. Falhar em um teste de tentação significa ceder à tentação relevante; não significa necessariamente confessar tudo imediatamente ou executar uma ação específica sem considerar oportunidade, risco, conhecimento e consequências.

**Não executar Morale Checks para personagens controlados por jogadores.** A autonomia do jogador permanece preservada, conforme a regra do AD&D 2e.

### 5. Origem do valor de moral e dos modificadores

A precedência proposta para obter o valor-base é:

1. estatística efetiva do ator no motor, se a leitura por EEex for validada e somente de leitura;
2. campo correspondente no CRE local da build pinada, com versão e proveniência registradas;
3. valor de referência do DMG, somente quando a categoria de criatura/NPC estiver comprovada por dados ou curadoria;
4. se não houver base confiável, não inventar um valor numérico: aplicar a solução interpretativa ou retornar MORALE_UNRESOLVED.

O campo CRE denominado Morale Break não deve ser confundido automaticamente com o valor de moral usado na rolagem AD&D. A equivalência e o comportamento efetivo do motor precisam ser verificados na build alvo.

O DMG apresenta contextos diferentes para moral de criaturas e para moral de hirelings/henchmen. Os valores dessas seções não devem ser fundidos em um padrão universal. A política deverá registrar qual fonte/tabela foi usada e resolver a correspondência antes de habilitar defaults para habitantes genéricos.

Modificadores oficiais devem ser aplicados somente quando seus pré-requisitos forem comprovados:

- Table 50: modificadores situacionais, incluindo alinhamento ético Lawful/Chaotic, tratamento, perigo, vantagem e perdas.
- Table 71: modificadores permanentes de NPCs associados ao personagem, incluindo Good/Evil, diferença de raça e duração do vínculo. Os modificadores Lawful/Chaotic que também constam na Table 50 **não podem ser aplicados duas vezes**.
- Ajustes de Carisma da Table 6 do PHB pertencem à reação social; não devem ser confundidos com o valor-base de moral.

Quando alinhamento for UNKNOWN, não sortear nem inferir um modificador. Reputação, alinhamento mecânico, alinhamento projetado e relação pessoal continuam sendo dados distintos.

### 6. Influência da personalidade e do alinhamento

A personalidade e o alinhamento influenciam diretamente a interação, mas em papéis separados:

- **P1 — HEXACO ficcional:** influencia a interpretação, o tom, a tolerância, a expressividade e a forma de resistir ou demonstrar desconforto. O DMG também orienta que a moral de NPCs seja coerente com a personalidade conhecida. Não converter diretamente cada ponto HEXACO em bônus/penalidade AD&D sem uma política numérica versionada, calibrada e testada.
- **P2 — alinhamento AD&D:** aplica os modificadores oficiais quando a tabela e o contexto os autorizarem; também orienta valores e expressão. Não determina automaticamente simpatia, hostilidade, honestidade ou obediência.
- **P3 — valores, motivações e vulnerabilidades:** determina quais tentações, ameaças e conflitos têm significado para aquele NPC, desde que estejam presentes em seu perfil autorizado e sejam relevantes para a situação.
- **P4 — estado e relações:** confiança, lealdade, tratamento recebido, experiências e vínculos influenciam a reação somente quando houver eventos válidos e visíveis no ramo. Reutilizar ADR-0119 e SPEC-003; não criar uma segunda fonte de verdade relacional.

Os modificadores psicológicos próprios do Infinity serão identificados separadamente dos modificadores oficiais AD&D. Não aplicar números improvisados nem alterar o alinhamento mecânico do jogo.

### 7. Persistência, escopo e auditoria

- A disposição inicial será associada a um episódio de interação e ao par NPC/personagem iniciador quando esse identificador estiver comprovado. Não rerrolar a cada pergunta.
- Uma nova avaliação exige novo encontro ou mudança contextual relevante, com justificativa registrada.
- Para NPCs CANDIDATE/efêmeros, o resultado fica limitado ao escopo seguro da instância/sessão/cena; não cria identidade, relação ou memória persistente.
- Para NPCs VERIFIED, relações e evolução seguem os gates de identidade, ramo e eventos da SPEC-003/ADR-0061/0062/0119.
- Cada resolução deve ser idempotente e auditável, registrando regra/tabela/versão, gatilho, dados rolados, modificadores, fonte do valor-base, resultado e evento de origem. Repetir a mesma requisição não pode gerar uma nova rolagem.
- Eventos candidatos: NpcEncounterReactionResolved e NpcMoraleCheckResolved, com categoria, visibilidade e política de persistência a validar com SPEC-003 antes da implementação.
- A disposição pode orientar a fala durante o episódio, mas não cria fatos, conhecimento, segredos, relações ou ações mecânicas.

### 8. Responsabilidades do código e do LLM

- EncounterReactionResolver: Table 59, colunas, modificadores e resultado.
- MoraleResolver: gatilhos, valor-base, modificadores, 2d10 e resultado.
- InteractionDisposition: disposição vigente no episódio.
- DialogueBehaviorPolicy: combinação auditável de disposição, personalidade, alinhamento, relações e contexto.
- DialogueEngine: recebe uma política já resolvida e produz/valida a fala.

Código determinístico escolhe se há teste, calcula modificadores, rola dados, decide o resultado e registra eventos. O LLM apenas expressa a reação em linguagem natural a partir do contexto autorizado. Não escolhe os dados, não muda estado, não concede conhecimento e não executa ações no jogo.

Nenhum componente desta ADR pode escrever em CRE, alterar engine_alignment, reputação, scripts, quests, diálogos nativos ou save. Qualquer ação mecânica futura exige gate próprio e autoridade do host (ADR-0018 e ADR-0007).

## Evidências técnicas e lacunas atuais

- A documentação do Infinity Engine descreve o trigger Reaction() como 10 + rmodchr + rmodrep; o recurso rmodchr.2da associa modificadores à Carisma. Isso confirma a existência do mecanismo nativo, mas não prova que o Infinity já consegue ler seu valor numérico em runtime.
- A documentação CRE V1.0 identifica Carisma em 0x23E, Morale em 0x23F e Morale Break em 0x240. O parser atual de src/infinity_ai/gamedata/formats.py lê identidade, alinhamento, Sabedoria e Inteligência, mas ainda não expõe esses três campos.
- O probe atual usa leitura de Sabedoria e Inteligência. A leitura efetiva de Carisma, Morale e Morale Break por EEex_Sprite_GetActiveStats ainda precisa ser testada na build BG2:EE pinada.
- A observação atual de NpcDialogueStarted não comprova necessariamente qual personagem do grupo iniciou a interação. Sem esse dado confiável, não aplicar ajuste de Carisma de um personagem escolhido por suposição.

## Alternativas consideradas

- **LLM decide reação, moral e rolagens:** rejeitada; não é reproduzível, auditável nem compatível com a diretriz código primeiro.
- **Morale Check a cada pergunta:** rejeitada; produz instabilidade e banaliza a regra.
- **Somente personalidade/HEXACO:** rejeitada; perde a compatibilidade com AD&D 2e e o motor BG2:EE.
- **Uma única rolagem para reação e moral:** rejeitada; os mecanismos respondem a perguntas diferentes.
- **Usar sempre a Table 59, mesmo quando a situação é clara:** rejeitada; contradiz a orientação do DMG de privilegiar a interpretação contextual.

## Critérios de aceite para a implementação futura

1. Testes de tabela cobrem todos os resultados e as quatro colunas da Table 59, inclusive extremos e modificadores positivos/negativos.
2. Testes de Morale Check verificam comparação 2d10, limites, modificadores, gatilhos, resultado contextual e ausência de rolagem quando não justificada.
3. Testes provam que modificadores Lawful/Chaotic não são duplicados entre Table 50 e Table 71.
4. Testes provam que Carisma/reputação nativos não são contados novamente quando engine_reaction já os inclui.
5. Testes cobrem moral desconhecida, proveniência, categorias distintas de NPC, UNKNOWN alignment e MORALE_UNRESOLVED.
6. Repetição/idempotência, save/load, forks, NPC efêmero e identidade verificada mantêm escopo e resultados corretos.
7. A personalidade muda a expressão e a avaliação contextual sem criar fatos nem produzir modificadores HEXACO não aprovados.
8. A LLM indisponível não altera rolagens, estado ou disposição; fallback continua funcional.
9. POC BG2:EE/EEex comprova leitura de atributos e observação do iniciador sem escrita no jogo e sem interferir em scripts/diálogos originais.
10. A evidência de laboratório usa save descartável e comprova zero mutação não autorizada.

## Pendências explícitas antes da implementação integrada

- Validar na build BG2:EE os campos CRE e os valores ativos de Carisma, Morale e Morale Break.
- Descobrir se o valor de Reaction() pode ser consultado de forma read-only pelo adaptador; documentar a semântica de rmodchr e rmodrep da build pinada.
- Resolver a correspondência entre categorias CRE/engine e os valores-base/tabelas de moral do DMG, sem assumir que todo trabalhador é hireling.
- Definir a classificação determinística da abordagem do jogador e obter o personagem iniciador por observação confiável.
- Calibrar, em política versionada, qualquer influência numérica própria de HEXACO; até lá, HEXACO orienta interpretação e expressão, não recebe bônus arbitrários.
- Validar os contratos de eventos e persistência com SPEC-003 e a integração de fala com SPEC-004.
- Manter a POC e a implementação isoladas da branch principal até revisão e aprovação.

## Referências

- AD&D 2nd Edition, Dungeon Master's Guide, Chapter 11, Table 59 — Encounter Reactions: https://adnd2e.fandom.com/wiki/Encounter_Reactions_(DMG)
- AD&D 2nd Edition, Dungeon Master's Guide, Chapter 9, Tables 49–50 — Morale: https://adnd2e.fandom.com/wiki/Morale_(DMG)
- AD&D 2nd Edition, Dungeon Master's Guide, Chapter 12, NPC Morale / Table 71: https://adnd2e.fandom.com/wiki/Personality_(DMG)
- AD&D 2nd Edition, Player's Handbook, Table 6 — Charisma: https://adnd2e.fandom.com/wiki/Charisma_(PHB)
- IESDP, BGEE script triggers, Reaction(): https://gibberlings3.github.io/iesdp/scripting/triggers/bgeetriggers.htm
- IESDP, CRE V1.0 file format: https://argent77.github.io/iesdp/file_formats/ie_formats/cre_v1.htm
- IESDP, BGEE 2DA file index (rmodchr e rmodrep): https://gibberlings3.github.io/iesdp/files/2da/2da_bgee/index.htm
