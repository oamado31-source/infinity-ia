# ADR-0033 — Jornadas personalizadas de redenção, juramentos e transformação

- **Decisão:** DEC-038 — redenção, recuperação de poderes e trajetórias após evolução de alinhamento.
- **Status:** **APROVADA — opção B**.
- **Data:** 2026-11-06.
- **Origem:** escolha expressa do idealizador do Infinity AI.
- **Escopo inicial:** personagens dos jogadores no **Living World**; não altera o modo Original nem estabelece regras para todos os NPCs.
- **Relacionamentos:** DEC-004/019/020 (históricos/segredos), DEC-008/009 (persistência/cânone), DEC-010/027 (geração/risco), DEC-005-R (AD&D 2e e módulos), DEC-011/012 (host/gateway), DEC-014 (código primeiro), DEC-028/029/030/031 (conhecimento, rumores, reputação e facções), DEC-034 (eventos críticos), DEC-035/036/037 (alinhamento dinâmico, interpretação contextual e consequências mecânicas).

## Contexto

Após perder compatibilidade com uma classe, juramento, fé ou poder, um personagem pode se arrepender e desejar reparar atos anteriores, procurar uma nova filiação ou aceitar a transformação. A arquitetura não deve forçar retorno ao alinhamento de origem, apagar decisões confirmadas ou conceder mecanicamente habilidades sem suporte em BG2:EE/EEex. A narrativa pode incluir provas, reconciliação, ordens religiosas, divindades, NPCs e facções historicamente coerentes. A lógica de mecânica e regras de AD&D 2e permanece em validação.

## Decisão aprovada

1. **Opção B — jornadas de redenção e transformação com histórias personalizadas.** Criar **arcos pessoais opcionais**, baseados em ações confirmadas, origem do personagem, alinhamento atual, histórico persistente, vínculos e conjuntura de Forgotten Realms, com escolhas legítimas e consequências duradouras.
2. **Agência narrativa:** o jogador pode buscar redenção, renovar/romper um juramento, negociar com uma ordem/facção, mudar sua fé ou **permanecer** em seu caminho atual. Não há retorno moral compulsório nem conversão de classe como prêmio automático.
3. **Reparação proporcional:** pedidos de desculpa, restituição, provas de lealdade, busca por perdão e reparações são **possibilidades narrativas candidatas**, não uma tabela automática de absolvição. Responsabilidade e consequências confirmadas são preservadas, inclusive quando terceiros não perdoam ou quando prejuízos não podem ser desfeitos.
4. **Canon e fontes:** apenas instituições, deuses, ordens e recursos existentes e compatíveis com a época/região da campanha podem ser apresentados como canônicos. Extensões procedurais são identificadas como conteúdo daquela campanha, sem falsificar fontes de FR. Eventos históricos de alto risco continuam sujeitos à DEC-034.
5. **Separação de dimensões:** evolução moral (DEC-035/036), relacionamento com patrono/facção, reputação por observador (DEC-030) e atributo/estado mecânico BG2:EE (DEC-037) são entidades independentes. Completar uma aventura não força alinhamento, restauração de reputação nem reconciliação com todos os interessados.
6. **Geração e validação:** o orquestrador pode propor etapas e diálogos com LLM local sob demanda, mas a progressão depende de objetivos predefinidos/validados, evidências, condições, permissões, cronologia, segredos e estado da campanha. Nenhum modelo pode autoaprovar sanções ou recompensas mecânicas.
7. **Recuperação de poderes condicionada:** recuperar habilidades, reconsagrar-se, trocar divindade, kit ou classe só é elegível se houver **regras especificadas e módulo tecnicamente validado**, respeitando as condições da instalação/versão e a escolha da campanha. Não há garantia de suporte pelo BG2:EE/EEex, nem criação implícita de uma nova classe.
8. **Autorização e execução:** efeitos físicos devem passar por Action Gateway (DEC-012), verificação de versão/perfil de regras e confirmação do host (DEC-011). Recibos e operações idempotentes; em `UNCERTAIN`, reconciliar antes de repetir; não modificar saves de outros personagens ou modo Original.
9. **Persistência e revisão:** cada arco registra origem causal, etapas, decisões, vínculos, resultados e bloqueios técnicos. Retcons de histórico dependem da DEC-020; a restauração de um save não duplica recompensa nem 'desfaz' julgamento social automaticamente.
10. **Não exclusividade:** arcos pessoais podem coexistir com aventuras clássicas paralelas e outras quests, sem assumir o papel de protagonistas tradicionais; não obrigar o grupo a acompanhar a redenção de outro personagem.

## Exemplo hipotético — paladino em crise

1. Paladino originalmente Lawful Good toma uma série de decisões graves; avaliação da DEC-036 registra mudança/possível incompatibilidade, sem atribuir poderes ou punições mecânicas não comprovadas.
2. Descobre uma oportunidade de conversar com uma ordem que aceita investigar sua conduta. O contato depende de notícias/relacionamentos legítimos e pode impor condições narrativas coerentes.
3. O personagem **escolhe** buscar reparação, recusar a proposta ou ingressar em outra tradição/organização. Qualquer uma dessas escolhas pode abrir aventuras diferentes.
4. Completar uma jornada **não assegura** restauração de todos os poderes: depende da regra de classe/kit e integração validada; o dano e a reputação social não são apagados.

## Estados candidatos do arco (não são API nem engine implementados)

```text
POTENTIAL -> OFFERED -> ACCEPTED -> ACTIVE -> RESOLUTION_PENDING
   |           |          |         |           |
   |           +--> DECLINED         |           +--> NARRATIVE_RESOLVED
   |                      |          |           +--> MECHANICAL_PENDING_VALIDATION
   +----> DORMANT          +--> ABANDONED        +--> HOST_CONFIRMED
                                   |             +--> FAILED / UNCERTAIN_RECONCILE
                                   +--> REVISITABLE (quando condições permitirem)
```

Os estados e transições definitivos serão definidos em SPEC. `NARRATIVE_RESOLVED` não implica `HOST_CONFIRMED`; uma missão pode ter final narrativo sem efeito físico compatível no motor.

## Requisitos candidatos de aceitação

1. O jogador que mudou alinhamento recebe oportunidade narrativa coerente sem obrigação de aceitá-la.
2. Dois personagens com históricos e decisões diferentes não recebem automaticamente a mesma jornada ou consequência.
3. Recusar redenção não impede participação normal no Living World nem cancela sanções legítimas já comprovadas.
4. O sistema não restaura classe/poder somente por alterar o alinhamento ou concluir um diálogo.
5. Falha técnica ao aplicar poder deixa estado pendente/reconciliável, não sucesso fictício.
6. Consequências sociais e da fé persistem separadamente, podendo divergir do resultado moral/mecânico.
7. Instituições históricas respeitam ano, lugar, fonte e eventos canônicos divergentes da campanha.
8. Uma missão pessoal não vaza segredos de histórico a outro jogador ou NPC não autorizado.
9. Eventos HIGH de redenção/transformação que alterem fatos históricos continuam bloqueados pela DEC-034.
10. Save/reload e dois clientes não duplicam recompensa nem alteram personagens terceiros.
11. Modlist/classe incompatível impede efeitos mecânicos e informa pendência sem corromper estado.
12. Modo Original permanece inalterado.

## Não decidido nesta ADR

- Pré-requisitos precisos, roteiros, provas, duração e número de etapas; custos, chances, limiares de alinhamento e fórmula de recuperação.
- Quais classes/kits/deuses/ordens aceitam reconsagração, troca de patrono, recuperação ou nova carreira, inclusive regras de *fallen*.
- Interface, aprovação individual, gatilhos, disponibilidade de novos kits/classes e migração de saves; requer SPECS, POCs e autorizações específicas.
- Método concreto para criação e apresentação de **todas** as quests pessoais (proposto como tema da **DEC-039**, sem aprovação neste ADR).

## Consequências

**Benefícios:** decisões morais transformam-se em aventuras com agência e continuidade; mantém consequências, valoriza histórias individuais e não reescreve regras do BG2:EE prematuramente.

**Custos/riscos:** orquestração adicional de quests, revisão de lore, dependências de classe, risco de exploits de restauração de poderes, necessidade de testes e UX clara. **Status técnico:** nenhuma dessas mecânicas foi instalada ou testada.

**Próxima decisão proposta:** DEC-039 — método de geração e gerenciamento dos arcos pessoais (históricos, redenção, aliados e escolhas) no Living World.
