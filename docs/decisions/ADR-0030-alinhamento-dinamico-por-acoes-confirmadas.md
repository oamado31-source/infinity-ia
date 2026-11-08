# ADR-0030 — Alinhamento dinâmico dos personagens conforme ações

- **Decisão:** DEC-035 — adendo explícito à DEC-034, registrado como decisão independente por impacto em regras e narrativa
- **Status:** **APROVADA — princípio de alinhamento mutável**
- **Data:** 2026-11-06
- **Fonte:** escolha expressa do idealizador: o personagem pode começar, por exemplo, **Chaotic Good** e evoluir para outro alinhamento conforme suas ações, com consequências para a reputação.
- **Escopo:** personagens dos jogadores no Living World; integração mecânica sujeita a SPECS/POCs.
- **Relações:** DEC-004/019/020, DEC-005-R, DEC-008/011/012/014, DEC-026/027/029/030, DEC-034.

## Contexto

Os jogadores têm liberdade de participar, impedir ou apoiar conspirações e outros acontecimentos. A identidade moral/ética dos personagens deverá poder mudar com suas escolhas e histórico confirmado, e não permanecer congelada no alinhamento declarado na criação.

A implementação BG2:EE baseia-se em AD&D 2e e possui **restrições de classe e efeitos mecânicos ligados ao alinhamento**. O manual de BG2:EE registra restrições de alinhamento para certas classes (como paladinos) e possíveis perdas de habilidades quando o personagem se desvia severamente. Logo, permitir evolução narrativa do alinhamento não autoriza editar indiscriminadamente a variável mecânica no motor sem testes.

**Fontes de verificação:**
- Manual BG2:EE, *Amn Survival Guide*, seção Character Generation → Alignment (página impressa 34): https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/257350/manuals/BGIIEE_-_Amn_Survival_Guide.pdf
- Documentação de regras revisadas em mods (*Talents of Faerûn*), exemplo de alterações de restrições de classe; útil como referência, não como implementação aprovada: https://gibberlings3.github.io/Documentation/readmes/readme-dw_talents.html

## Decisão aprovada

1. **Alinhamento não é imutável.** O personagem seleciona um alinhamento inicial compatível com criação e regras-base, mas poderá evoluir para outro ao longo da campanha em função de ações efetivas, padrões de escolha e consequências verificadas.
2. **Dois eixos distintos:** a representação respeitará o enquadramento AD&D 2e, com dimensão ética **Lawful ↔ Neutral ↔ Chaotic** e dimensão moral **Good ↔ Neutral ↔ Evil**, compondo os nove alinhamentos clássicos. Ser mais lawful não significa ser mais good, nem ser chaotic significa ser evil.
3. **Ações com causalidade:** registrar participação, intenção/condições quando legitimamente disponíveis, autoria, resultado confirmado pelo host ou por evento narrativo autorizado e contexto da decisão. Rumor, opinião de NPC, reputação negativa, classe ou discurso isolado **não alteram automaticamente a moral objetiva**.
4. **Alinhamento ≠ reputação.** O alinhamento descreve orientação ética/moral do personagem; reputação DEC-030 é a percepção contextual de outros. Uma escolha pode influenciar ambos por mecanismos **independentes**, sem mapear diretamente escore de reputação para eixo moral.
5. **Atribuição individual:** cada personagem possui histórico e estado próprios. Ações do grupo não alteram o alinhamento de todos automaticamente, salvo participação/consentimento e causalidade válidos.
6. **Mudança ao longo do tempo:** evitar transição arbitrária por evento trivial e evitar 'farm' moral. A frequência, intensidade, escalas e políticas de reversão ainda **não foram aprovadas**.
7. **Consequências narrativas:** oportunidades de roleplay, alianças, conflitos de consciência, reações de NPCs com conhecimento legítimo e desenvolvimento de arco pessoal poderão refletir o alinhamento. A IA local pode escrever contextualização, não arbitrar sozinha escores nem inventar ações.
8. **Impacto mecânico condicionado:** alteração real do atributo de alinhamento no BG2:EE, restrição de classes/kits, status de paladino/ranger/cleric/druid, magia, itens, diálogos, requisitos e habilidades exigem **SPEC específica, avaliação de compatibilidade DEC-005-R, autorização gateway e confirmação do host**. Até isso ser comprovado, alinhar estado narrativo externo não equivale a mudança mecânica no executável.
9. **Persistência/versionamento:** manter histórico de eventos com origem e data, estados derivados e transições auditáveis; não recalcular o passado a partir de rumores; preservar consistência de saves e dois clientes, sem interferir no modo Original.
10. **Não há escolha aprovada de árbitro algorítmico**, pesos, limiares, UI, possíveis exceções de classe nem papel exato do anfitrião em decisões ambíguas: serão discutidos na **DEC-036**.

## Exemplo não prescritivo

Um personagem **Chaotic Good** pode apoiar uma causa altruísta inicialmente, mas passar a agir de modo sistematicamente autoritário, podendo aproximar-se de **Lawful Good**, ou praticar violência instrumental e desrespeito aos outros, podendo mover-se em direção a **Neutral/Evil**. Mudanças de eixo dependem das circunstâncias e do padrão de ações confirmado — não de uma associação automática entre ordem e bondade.

Defender um governante, investigar uma conspiração ou participar dela **não tem rótulo moral fixo**: legitimidade, violência, compromissos, vítimas, motivação e alternativas importam. A transição concreta não é determinada aqui.

## Testes candidatos

1. Chaotic Good pratica ações persistentes de observância de regras sem mudar Good → somente eixo ético candidato à mudança.
2. Defesa de um governante corrupto por motivos egoístas não recebe automaticamente bônus moral Good.
3. Boato falso produz hostilidade pública, mas não altera alinhamento real.
4. Uma ação de jogador A não muda alinhamento de jogador B sem evidência de participação.
5. Ação mecanicamente confirmada entra uma vez no histórico após save/reload.
6. Escolhas opostas e ações contraditórias são tratadas por política de tendência ainda a especificar; sem oscilação de alinhamento a cada clique.
7. Mudança para alinhamento incompatível com paladino/kits solicita verificação de regras antes de mexer no estado mecânico.
8. A IA não pontua arbitrariamente ações: decisões por contrato e revisão/validação quando ambíguas.
9. Narrativa externa de alinhamento e estado mecânico BG2:EE não são confundidos durante falha de bridge.
10. Modo Original permanece inalterado, e duas máquinas cooperativas não divergem no estado confirmado.

## Lacunas e riscos

- Como atribuir peso moral/ético às decisões (contexto vs tabelas vs julgamento humano).
- Como tratar ações sem testemunha, auto-defesa, coerção, magia de controle, classes e filiação religiosa.
- Como comunicar mudanças ao jogador e permitir contestação/ajuste sem reescrever eventos confirmados.
- Como operar com restrições reais de alinhamento, equipamentos e classes do BG2:EE, incluindo multiplayer e EEex.

**Não implementado:** não foi criado sistema de alinhamento, alteração de saves, mod, hook, pipeline de avaliação nem integração do jogo nesta decisão.
