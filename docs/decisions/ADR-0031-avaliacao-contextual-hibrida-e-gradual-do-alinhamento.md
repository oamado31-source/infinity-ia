# ADR-0031 — Avaliação contextual híbrida e gradual do alinhamento

- **Decisão:** DEC-036 — método de avaliação e evolução dos alinhamentos
- **Status:** **APROVADA — opção B**
- **Data:** 2026-11-06
- **Decisor:** idealizador do Infinity AI, decisão expressa nesta conversa.
- **Escopo:** personagens dos jogadores no modo Living World; avaliações interpretativas de NPCs e efeitos mecânicos específicos requerem decisões/SPECS adicionais.
- **Dependências:** DEC-035/ADR-0030 (alinhamento mutável), DEC-030 (reputação contextual), DEC-028 (segredos), DEC-008 (persistência), DEC-011 (host), DEC-012 (Action Gateway), DEC-014 (código primeiro), DEC-005-R (AD&D 2e), DEC-020 (correção de históricos), DEC-034 (impactos irreversíveis).

## Problema

O jogo deve permitir mudanças éticas e morais conforme as ações dos personagens, mas julgamentos binários por ação isolada ou atribuição livre de um LLM podem ser arbitrários, injustos ou incoerentes. A reputação pública não descreve automaticamente o caráter, e a edição de atributos do BG2:EE pode ter consequências graves para classes, magias, itens e saves.

## Decisão aprovada

1. **Modelo híbrido contextual e gradual, opção B:** regras versionadas, auditáveis e preferencialmente determinísticas avaliam o histórico confirmado do personagem nos **dois eixos separados** de alinhamento (Lawful ↔ Neutral ↔ Chaotic e Good ↔ Neutral ↔ Evil). A IA pode **propor interpretações em situações abertas**, mas não altera sozinha a classificação nem o estado mecânico.
2. **Evidência antes de avaliação:** somente ações/fatos confirmados pelo host ou pelo sistema narrativo autorizado podem influenciar o histórico moral. O avaliador registra quem agiu, quem participou, contexto, ações e resultados conhecidos, com fontes e proveniência; rumor, reputação de terceiros e texto inventado por LLM não servem como prova.
3. **Contexto e causalidade:** considerar, **quando documentados**, coerção, magia de controle, legítima defesa, conhecimento disponível ao personagem, responsabilidade individual, objetivo, meios escolhidos, alternativas razoavelmente perceptíveis e consequências confirmadas. **Não inferir intenção secreta nem informação impossível a partir de um resultado.** Ter boa intenção não elimina automaticamente dano; um mau resultado não implica intenção maligna.
4. **Mudança gradual e estável:** o sistema acompanha tendências e padrões de conduta ao longo da campanha. Atos triviais não alternam imediatamente o alinhamento; ações de grande relevância podem ter influência maior, sob regras específicas ainda a definir. Evitar flutuação a cada clique, contagem duplicada e manipulação por repetição mecânica de ações.
5. **Avaliação por personagem:** uma ação do grupo não transfere automaticamente alterações a todos. Responsabilidade exige participação, ordem/decisão tomada ou outra causalidade comprovável; testemunhar e discordar de uma ação não equivale necessariamente a praticá-la.
6. **Ambiguidade:** quando evidências ou classificação forem insuficientes, registrar `NEEDS_REVIEW`/`UNRESOLVED` como estados candidatos, manter a interpretação provisória e **não efetivar sanções ou mudanças mecânicas irreversíveis sem política específica**. Critérios de revisão, papel do anfitrião e formas de contestação serão especificados posteriormente.
7. **Arbitragem confiável:** a IA local só pode fornecer classificação **proposta** e justificativa com base em contexto autorizado. Um **validador de regras** confere o resultado e o Action Gateway impede alteração não autorizada. Não liberar avaliação moral como texto livre contendo ordens mecânicas.
8. **Dois resultados independentes:** `alignment_projection` (interpretação narrativa/auditável dos eixos) e `social_perception` (reputação que NPCs legitimamente construíram) nunca são inferidos automaticamente um do outro. O atributo `engine_alignment` do BG2:EE é terceiro estado, **não se altera até SPEC, POC e confirmação do host**.
9. **Persistência/versionamento:** manter registro de evidências e explicações vinculados a campanha, personagem, data, versão da política e decisão. Reprocessamento de save/replay deve produzir o mesmo resultado ou divergências diagnosticáveis, sem aplicar duas vezes a mesma ação.
10. **Proteção de modo Original e multiplayer:** avaliação no Living World não reescreve saves originais, nem expõe segredos de históricos a NPCs/clientes não autorizados. O host permanece autoridade para efeitos mecânicos, com estado narrativo coerente entre participantes.
11. **Sem fórmulas definidas nesta ADR:** pesos, janela de avaliação, limiares de transição, taxa de recuperação, dimensão/escala de eixos, impacto exato de delitos, interface, algoritmo final e política de contestação exigem SPECS. A escolha da abordagem **não aprova automaticamente nenhuma pontuação particular**.

## Fluxo conceitual

```text
Acontecimento confirmado na campanha
  -> autoria/participação e contexto comprovável
  -> evento de evidência versionado (idempotente)
  -> regras e taxonomia contextual; LLM local somente se interpretação aberta necessária
  -> validação/revisão quando houver ambiguidade
  -> tendência por eixo e estado narrativo auditável
  -> atualização de percepções sociais somente pelo conhecimento legítimo (DEC-028/029/030)
  -> alteração BG2:EE SOMENTE após futura SPEC, gateway, POC, host e decisão DEC-037
```

## Exemplos não prescritivos

- Um **Chaotic Good** que repetidamente cumpre compromissos e regras por convicção pode aproximar-se de uma orientação mais **Lawful**, sem deixar de ser **Good** por isso.
- Um personagem liberta pessoas escravizadas violando uma lei abusiva: ilegalidade **não implica maldade**. Eixos ético e moral não devem ser confundidos.
- Um personagem coagido ou sob magia de controle pode ter responsabilidade diminuída, conforme o que for comprovável; a avaliação não presume livre-arbítrio.
- O grupo é difamado em outra cidade: os **rumores podem afetar a reputação**, mas não reescrevem seu alinhamento real.
- Um paladino perde sua tendência Lawful Good na projeção narrativa: **não alterar automaticamente suas habilidades no motor** sem especificação de consequências e compatibilidade.

## Requisitos técnicos e segurança

- Nenhum LLM recebe autoridade de escrita direta sobre `engine_alignment`, classes, itens ou magias.
- A taxonomia e as regras devem ser versionadas para que mudanças no avaliador não reescrevam o passado silenciosamente.
- Autoria causal por personagem; evento de origem, hash/idempotency key, justificativa, grau de incerteza e trilha de revisão.
- Resumos de modelo são auxiliares: não substituir evidências originais nem vazar segredos via logs, notificações, multiplayer ou diálogos.
- A avaliação pode levar a orientações narrativas, mas efeitos mecânicos continuam em **DEC-037 (aberta)**, sujeitos aos limites de BG2:EE/AD&D 2e e POCs.

## Testes candidatos

| ID | Cenário | Resultado esperado |
|---|---|---|
| ALIGN-EVAL-01 | Boa ação fora da lei | Não converter automaticamente ilegalidade em Evil |
| ALIGN-EVAL-02 | Ação por coerção/magia comprovada | Política contextual considera agência reduzida |
| ALIGN-EVAL-03 | Intenção desconhecida | Não inventar motivação; inconclusivo quando necessário |
| ALIGN-EVAL-04 | Acusação falsa por rumor | Reputação pode mudar, alinhamento não |
| ALIGN-EVAL-05 | Jogador 1 age sozinho | Não imputar moral automaticamente ao jogador 2 |
| ALIGN-EVAL-06 | Escolhas triviais repetidas | Limites contra manipulação e oscilação imotivada |
| ALIGN-EVAL-07 | Sequência de atos relevantes | Tendência gradual e por eixo, regra versionada |
| ALIGN-EVAL-08 | Mesma ação após load/retry | Idempotência, sem dupla contagem |
| ALIGN-EVAL-09 | Avaliação aberta por LLM | Proposta revisável, sem acesso a ações mecânicas |
| ALIGN-EVAL-10 | Caso ambíguo | Pendência de revisão sem penalidade mecânica automática |
| ALIGN-EVAL-11 | Paladino muda tendência narrativa | Sem mudar engine/kit até SPEC e POC |
| ALIGN-EVAL-12 | Histórico secreto de um jogador | Acesso restrito; NPC não informado não conhece segredo |
| ALIGN-EVAL-13 | Dois clientes conectados | Estado coerente, sem dupla atualização nem vazamentos |
| ALIGN-EVAL-14 | Modo Original | Nenhuma alteração externa de atributos do jogo |
| ALIGN-EVAL-15 | Upgrade da regra avaliadora | Reprocessamento comparável; sem retcon silencioso |
| ALIGN-EVAL-16 | Evento histórico crítico | DEC-034 preservada independentemente do julgamento moral |

## Consequências e limites

**Benefícios:** continuidade de personagem, contexto moral, explicações auditáveis, mudança graduada e separação reputação/alinhamento. **Custos:** curadoria de taxonomia, revisão de ambiguidade, versionamento e testes de consistência. **Não demonstrado:** alteração segura de alinhamento no BG2:EE, restrições de classes e funcionamento efetivo da bridge em multiplayer.

## Próxima discussão

**DEC-037 — Consequências mecânicas e salvaguardas de mudança de alinhamento:** como tratar classes/kits, habilidades, magias, itens e avisos ao jogador quando o alinhamento narrativo passa a divergir das regras nativas, sem corromper saves nem frustrar a agência do personagem.
