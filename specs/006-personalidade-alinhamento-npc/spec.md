# SPEC-006 — Matriz de personalidade e alinhamento de NPCs

**Status:** PROPOSTA para revisão do mantenedor (2026-11-09). O gerador inicial e seus testes são **somente sintéticos**; não há integração com jogo, memória persistida, LLM ou ações mecânicas.
**Origem:** solicitação do mantenedor em 2026-11-09 para individualizar NPCs, integrar alinhamento de AD&D e documentar perfis.
**Governança:** ADR-0115 (proposto); ADR-0018, ADR-0030/0031/0032, ADR-0042/0059/0062/0113/0114; SPEC-003 (memória e save), SPEC-004 (fala/personas), SPEC-005 (cânone).

## Objetivo

Cada NPC deve ter um perfil **persistente, individualizado, reproduzível e auditável**, responsável por tendências de fala, prioridades, reações e propostas narrativas. A personalidade não substitui fatos, conhecimento adquirido, classe, reputação, alinhamento do motor ou a soberania do host. Uma reação diferente de dois NPCs ao mesmo evento exige percepção e conhecimento legítimos, não acesso ao estado global.

## Matriz principal

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

Três `values` ordenados (ex.: justiça, poder, tradição, autonomia, comunidade); duas `drives` (ex.: proteção, reconhecimento, descoberta) e duas `vulnerabilities` (ex.: traição, perda, rejeição). O gerador atual escolhe rótulos abstratos, **não inventa biografia, origem, eventos passados, crenças adquiridas ou segredos sobre terceiros**. A curadoria pode acrescentar objetivos, vínculos, tabu, estilo de fala e contradições com justificativa narrativa; são metadados privados com ACL própria.

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

## Reação: contrato futuro, não comportamento atualmente implementado

`evento confirmado → exposição/ACL → crença e memória do NPC → perfil-base + estado atual + relação → regras de prioridades/limites → proposta narrativa validada → fala local via SPEC-004`.

Exemplo hipotético: uma autoridade local exige que o grupo denuncie um inocente. Um NPC Leal e Bom pode tentar contestar a ordem por vias institucionais; outro Caótico e Bom pode desobedecer e proteger a vítima; um Leal e Mau pode explorar a ordem em benefício próprio. **Nenhuma fala ou ação é garantida por um rótulo isolado**: o NPC precisa saber do incidente, ter motivos e avaliar riscos. O eixo moral e o ético não substituem personalidade, crenças nem autoria causal.

Fala, recusa, comércio, mudança de facção, deserção, combate, assassinato, revelação de segredo ou alteração do jogo têm *gates diferentes*. LLM só ajuda a formular texto; o host tem autoridade mecânica e ações HIGH exigem aprovação.

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

**Aceite atual:** gerador puro, esquema-exemplo, cenários sintéticos de reprodução, nove alinhamentos e falha segura. **Pendente:** persistência, idempotência, curadoria canônica, contexto do diálogo, reações, evolução e POC real BG2:EE/EEex.
