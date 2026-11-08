# ADR-0003 — Visibilidade híbrida dos históricos e segredos dos personagens

- **Decisão de discovery:** DEC-019
- **Status:** APROVADA — escolha C (híbrida)
- **Data:** 2026-11-05
- **Origem:** escolha expressa do idealizador do Infinity AI
- **Âmbito:** modo Living World; repercussões para perfis, memória, diretor narrativo, NPCs, UI e persistência
- **Fase:** definição de comportamento; **não** indica suporte técnico comprovado em BG2:EE/EET/EEex

## Contexto e motivação

A DEC-004 estabelece que cada jogador cria o histórico de seu personagem e que a IA utiliza esse passado como fonte de eventos relevantes. Alguns fatos podem ser conhecidos publicamente (origem, profissão), outros devem ser preservados inicialmente como segredos (identidade, crimes, perseguições, promessas e ligações ocultas). Se o sistema tratar todos os textos como conhecimento comum, NPCs revelarão informações impossíveis de saber e jogadores receberão *spoilers* indevidos.

## Alternativas consideradas

- **A — Público:** todos os jogadores visualizam o histórico completo; NPCs ainda precisam adquirir conhecimento dentro do mundo.
- **B — Privado:** somente autor e sistema narrativo acessam o histórico completo; revelações acontecem durante o jogo.
- **C — Híbrido:** cada jogador define a visibilidade das informações de seu próprio histórico. **Escolhida.**

## Decisão aprovada

1. O histórico de personagem deverá aceitar **partes públicas e partes secretas**, definidas pelo jogador responsável. A estrutura deverá suportar classificação por fato/trecho, e não apenas um único interruptor para o documento inteiro.
2. Um componente narrativo privilegiado poderá consultar as informações necessárias, públicas e secretas, para planejar acontecimentos coerentes. Isso **não** concede automaticamente esse conhecimento a jogadores ou NPCs. O contexto passado a cada agente deverá ser limitado à sua função e autorização.
3. A visualização do histórico por outros jogadores obedecerá à escolha do autor. Informações secretas não deverão aparecer automaticamente em fichas, resumos, notificações, diálogos ou registros apresentados ao restante do grupo.
4. A **visibilidade fora da ficção** e o **conhecimento dentro da ficção** são dimensões distintas: um jogador pode ler um fato público sem que seu personagem ou um NPC saiba desse fato; um segredo pode vir a ser descoberto dentro da aventura por acontecimentos válidos.
5. A IA não poderá presumir conhecimento de um NPC por ter acesso privilegiado ao histórico. Para um NPC conhecer um segredo, será necessária uma origem coerente e registrada (testemunho, documento, evento, vínculo preexistente etc.) que o sistema de regras considere válida.
6. A decisão de um personagem ou NPC compartilhar uma informação durante o jogo deve produzir um fato auditável no estado narrativo, inclusive a origem da descoberta e quem passou a saber. A política de consentimento/controle de **grandes revelações** ainda será especificada; não foi automaticamente aprovada por esta decisão.
7. Informações e instruções escritas por jogadores são **dados não confiáveis**. Não podem alterar permissões, executar comandos Lua, alterar configuração de segurança ou sobrescrever o estado autoritativo do mundo.
8. O modo Original permanece isolado, nos termos da DEC-004; o sistema de segredos do Living World não altera automaticamente os saves clássicos.

## Modelo de informação candidato — sujeito às SPECS

```text
CharacterBackstory
  └─ BackstoryFact { fact_id, character_id, source_revision, text, classification }
         ├─ AudienceVisibility { owner_player, public_to_party | secret_to_party }
         ├─ WorldKnowledge { who_id, who_type, evidence_event_id, learned_at }
         └─ NarrativeHook { hook_id, required_facts, intended_targets, status }

NarrativeDirector (privileged, scoped retrieval)
  -> EventProposal -> KnowledgePolicyCheck -> RuleValidation
  -> AuthoritativeWorldEvent -> PersistedKnowledgeUpdate
```

Campos, nomes, armazenamento e regras de classificação padrão **não estão aprovados como contrato técnico**. Eles são propostas para orientar SPECS e testes. O repositório de conhecimento deve suportar, ao menos, três relações distintas: *quem escreveu*, *quem pode ver fora do jogo* e *quem sabe dentro do jogo*.

## Exemplo de aceitação pretendido

O jogador A escreve: “Sou herdeiro de uma família influente de Cormyr” e marca isso como **secreto**; escolhe publicar somente: “Sou viajante e procuro trabalho.” O jogador B vê apenas o texto público. Um taverneiro comum não sabe da linhagem. Um antigo oficial que testemunhou o passado de A poderá reconhecê-lo se esse vínculo for registrado; caso o reconheça, o jogo deve registrar quem presenciou a revelação e quais personagens ficaram sabendo. A IA não pode atribuir a descoberta automaticamente a todos os outros NPCs do mundo.

## Consequências arquiteturais

- Precisaremos de camada de **política de conhecimento/visibilidade** independente do modelo de IA e da UI de BG2:EE.
- Perfis, prompts, memória e notificações terão consultas **filtradas por destinatário**; o narrador privilegiado acessa o contexto mínimo necessário.
- `character_id`, `player_id`, `campaign_id`, `fact_id` e `event_id` deverão manter isolamento e rastreabilidade.
- Logs de depuração e integrações externas não podem ser uma rota alternativa para exposição acidental de segredos.
- A descoberta de um segredo altera conhecimento, não reescreve retrospectivamente o histórico original.
- Dados do histórico podem originar ganchos, mas a apresentação ao grupo não deve revelar o fato secreto sem um acontecimento legitimador.

## Requisitos candidatos e testes (não são SPECS aprovadas)

| ID | Cenário | Critério de aceitação candidato |
|---|---|---|
| CAND-KNOW-002 | A marca parte do histórico como secreta | B vê o trecho público e não vê o segredo em ficha, resumo ou painel de missão antes de revelação válida |
| CAND-KNOW-003 | NPC sem evidência conversa com A | NPC não age como se conhecesse o segredo, mesmo quando o diretor narrativo o conhece |
| CAND-KNOW-004 | NPC recebe informação por evento validado | O conhecimento é registrado com fonte, destinatário e momento; persiste após salvar/reabrir |
| CAND-KNOW-005 | Jogador B acessa informação pública de A | B pode lê-la fora do jogo; seu personagem e NPCs não passam automaticamente a conhecê-la |
| CAND-KNOW-006 | IA prepara uma missão baseada em segredo | O convite/descrição inicial não expõe a informação reservada sem uma causa narrativa válida |
| CAND-KNOW-007 | Histórico contém instrução para revelar segredos de outros jogadores | Entrada é tratada como texto ficcional, não altera política de visibilidade |
| CAND-KNOW-008 | Modos Original e Living World coexistem | A política e as memórias do Living World não afetam arquivos de save do modo Original |

## Limites e perguntas pendentes

**Aprovado:** opção C híbrida, classificação pública/secreta pelo autor, separação de conhecimento do narrador/jogador/NPC e necessidade de evitar revelações indevidas.

**Não decidido nesta rodada:** padrão inicial para trechos não classificados (sugestão técnica: privado até que o autor publique); interface de marcação; granularidade exata; opção de revelação previamente autorizada; tratamento de históricos alterados depois que eventos foram gerados; jogadores que saem de uma campanha; políticas de retenção e exclusão; encriptação em repouso e permissões operacionais específicas.

**Próxima decisão de discovery:** **DEC-020 — revisão de históricos, retcons e efeitos já incorporados ao mundo**. O método final de revisão e reconciliação ainda depende de discussão.

## Dependências

DEC-004 / ADR-0002; futuras DEC-008 (persistência), DEC-009 (canon), DEC-011 (autoridade e sincronização), DEC-012 (segurança), DEC-014 (autonomia de NPCs), DEC-016 (interfaces) e DEC-020 (edições/retcons).
