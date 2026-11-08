# ADR-0036 — Autoridade distribuída, agência dos jogadores e consequências cruzadas

- **Decisão:** DEC-041 — consentimento e autoridade em decisões narrativas coletivas.
- **Status:** **APROVADA — opção C**.
- **Data:** 2026-11-06.
- **Origem:** escolha expressa do idealizador na entrevista arquitetural do Infinity AI.
- **Pacote:** Discovery v3.7.
- **Relacionadas:** DEC-001, 004, 008, 009, 011, 012, 014, 019, 020, 022, 025–028, 030, 034, 035–040.

## Contexto

Históricos particulares, missões do Personal Story Director (PSD) e oportunidades compartilhadas do Cooperative Story Director (CSD) podem se cruzar. Uma ação legítima de um jogador pode revelar pistas sobre outro, prejudicar uma facção ligada a ele, interromper uma investigação ou influenciar sua reputação. O sistema precisa distinguir entre **decisões sobre o próprio personagem** e **consequências do mundo compartilhado**. Nenhum agente de IA deve assumir o papel ou a vontade de um jogador real.

## Alternativas

- **A — Anfitrião decide conflitos de histórias:** simples, porém centraliza a autoria e pode reduzir agência individual.
- **B — Titular tem veto absoluto sobre impactos:** protege o histórico, mas tornaria impossíveis consequências legítimas de outros jogadores e do mundo.
- **C — Autoridade distribuída por personagem, mundo e risco:** **ESCOLHIDA**. Preserva autoria individual e permite consequências causais verificáveis com regras de autorização.

## Decisão aprovada

1. **Agência do jogador:** cada jogador controla falas, intenções, escolhas, consentimentos, convites e ações voluntárias de seu próprio personagem. O PSD/CSD, NPCs ou LLM **não podem atribuir decisões, confissões, compromissos, consentimento ou motivações ocultas** a um personagem de jogador sem uma fonte de autorização/registro correspondente.
2. **Titularidade do histórico:** o autor decide aspectos públicos e secretos de seu histórico (DEC-019) e autoriza revisões/retcons próprios (DEC-020). Nenhum outro jogador, NPC ou agente pode editar silenciosamente esse histórico ou inventar que o personagem realizou atos passados não estabelecidos.
3. **Mundo compartilhado:** um jogador pode agir livremente sobre fatos, NPCs, organizações e situações que estejam ao seu alcance e dentro das regras. Tais ações podem **causar consequências para outros personagens**, mesmo sem seu consentimento específico para cada consequência, desde que a ação seja legítima, seus efeitos confirmados e os limites da campanha respeitados. A titularidade do arco não é um veto sobre a causalidade do mundo.
4. **Segredos e investigação:** ninguém adquire conhecimento só por estar na mesma missão. O titular controla **a revelação voluntária**; terceiros podem investigar e descobrir por meios legítimos, observações e evidências registradas, observada a política de conhecimento (DEC-028), a proveniência, a cronologia e quaisquer limites previamente estabelecidos para a campanha. Uma descoberta plausível não autoriza o sistema a inventar arbitrariamente fatos secretos.
5. **Conhecimento não é verdade:** suspeitas, rumores e acusações permanecem distinguíveis de fatos comprovados. Acusar a ladina de um crime não autoriza marcar esse crime como evento de seu passado; efeitos reputacionais de rumores são possíveis conforme DEC-029/030 e o conhecimento do observador.
6. **Autoridade do anfitrião:** o anfitrião define políticas gerais, configurações de campanha, regras de consentimento e intervenções de risco pertinentes; **não decide automaticamente o que um personagem de jogador pensa, diz ou aceita**. Configuração de votação/veto, se houver, depende de futura decisão/SPEC, não foi aprovada aqui.
7. **Mecânica e canon:** o **host de BG2:EE** confirma qualquer ação mecânica; o **Action Gateway** controla operações permitidas (DEC-011/012). Eventos históricos HIGH e irreversíveis preservam a proteção DEC-027/034 e não podem ser autorizados apenas pelo interesse narrativo do PSD/CSD. O narrador não converte uma proposta em resultado confirmado.
8. **Ausência e delegação:** se um jogador está ausente, IA/CSD não assumem sua personagem nem decidem por ele. O mundo pode continuar progredindo dentro da DEC-021/022/025; acontecimentos que exijam sua decisão pessoal ficam pendentes. Representantes, delegação explícita, automação de comportamento ou modos desconectados exigem regras futuras, não presumidas.
9. **Eventos cruzados rastreáveis:** propostas e efeitos registram campanha, atores/autoria, destinatários afetados, permissões aplicadas, evidências, política de risco, resultados e referências de fatos/históricos. Falhas `UNCERTAIN` aguardam reconciliação; sem retry cego nem aplicação duplicada.
10. **Limite de escopo:** a DEC-041 define **autoridade narrativa** e não estabelece permissões para combate jogador-contra-jogador (PvP), furtos entre jogadores, coerção mágica sobre PCs ou morte permanente por outro jogador. Essas interações serão debatidas na **DEC-042**.

## Matriz de autoridade aprovada

| Objeto ou ação | Autoridade principal | Restrições |
|---|---|---|
| Fala, escolha, intenção, convite ou revelação voluntária de um PC | Jogador controlador | Não inventar escolha se ausente; efeitos de ações obedecem regras |
| Revisão de backstory e segredos autorais | Titular do histórico | Não sobrescrever fatos em mundo confirmados sem autorização explícita e reconciliação (DEC-020) |
| Descoberta por observação, investigação, terceiros | Mundo / regras / evidências | Proveniência, ACL antes da IA e proteção de dados; suspeita ≠ verdade |
| Resultado de combate, inventário, conjuração, movimento | Host do jogo | Gateway, permissões, compatibilidade e receipt inequívoco |
| Consequência narrativa legítima de ação confirmada | Motor narrativo sujeito a regras | Persistência, causalidade e repercussões proporcionais; não fala em nome do afetado |
| Configurações globais, política de consentimento e risco | Anfitrião | Não pode editar vontade de PC; proteções HIGH e canon aplicáveis |
| Fato histórico canônico ou divergência irreversível | Política de canon/risco + evidência | DEC-009/034; sem consolidação automática não autorizada |
| Mediação textual, ganchos e alternativas | PSD/CSD/LLM sob demanda | Não são árbitros soberanos de vontade, verdade histórica ou mecânica |

## Cenários ilustrativos

- **Paladino investiga uma organização ligada secretamente à ladina.** Pode seguir pistas e falar com testemunhas. A ladina decide como reagir e se conta o segredo. O sistema não inventa uma confissão em seu nome; caso provas reais a identifiquem, a investigação pode produzir consequências no mundo, segundo as políticas da campanha.
- **Jogador ausente durante decisão pessoal.** O mundo avança dentro dos limites autorizados, mas a IA não decide que o ausente admitiu culpa, aceitou um contrato ou revelou seu passado.
- **Boato falso sobre o grupo.** NPCs podem acreditar e reagir à suspeita; o acontecimento não altera retroativamente a verdade, nem o alinhamento moral de quem não praticou o ato.
- **Arco de um jogador exige NPC compartilhado.** CSD pode coordenar a oportunidade sem sequestrar o NPC de outra trama, duplicar recurso ou obrigar adesão.
- **Conspiração com impacto no canon.** Participação voluntária pode criar divergência somente quando ação e autorizações forem demonstradas; nenhuma autorização HIGH é inferida por ser missão pessoal.

## Invariantes

1. **Sem autoria indevida:** nenhum agente produz decisão de jogador sem autorização.
2. **Sem segredos globais:** filtragem de conhecimento ocorre antes do prompt, da UI e do log visível a terceiros.
3. **Sem veto universal:** consequências legítimas do mundo não exigem autorização do alvo para cada fato externo; ações PvP diretamente prejudiciais têm política futura própria.
4. **Sem retcon silencioso:** histórico editável não apaga fatos confirmados, e fatos confirmados não inventam backstory.
5. **Sem coerção pela IA:** convites e participação permanecem voluntários.
6. **Sem bypass:** Action Gateway, host mecânico e HIGH prevalecem sobre o interesse narrativo.
7. **Sem consequência duplicada:** persistência por campanha com idempotência, reconciliação e isolamento do modo Original.

## Testes candidatos para SPECS

1. Dois PCs investigam o mesmo NPC; suas ações são atribuídas individualmente e o progresso coletivo é consistente.
2. Um jogador solicita que o LLM declare que outro confessou; o comando é rejeitado por falta de autoria.
3. O titular convida o grupo a uma missão privada sem revelar seu segredo; a UI e os prompts mantêm o sigilo.
4. Terceiro obtém pista legítima sobre histórico secreto; acesso filtrado, fonte e limites de campanha são respeitados.
5. Um rumor falso prejudica reputação local mas não grava o crime como fato nem afeta alinhamento sem autoria comprovada.
6. Jogador ausente não é representado por IA para revelar segredo, contratar serviços ou escolher desfecho.
7. Um ato legítimo altera controle de NPC/recurso compartilhado, sem modificar inventário de outro PC sem confirmação mecânica.
8. Ação pretende alterar canon HIGH; processo bloqueado até autorização específica e confirmação pertinente.
9. Anfitrião tenta usar regra global para forçar fala/confissão de jogador; vontade do PC não é substituída.
10. Save/load preserva provas, permissões, decisões e visibilidade sem vazamento ou duplicação.
11. Consulta do narrador não expõe dados privados em resposta direcionada a NPC não autorizado.
12. `UNCERTAIN` do host não resolve desfecho nem autoriza repetição automática.
13. Dois clientes com versões distintas de política não executam eventos inconsistentes.
14. Modo Original não herda eventos, convites ou segredos do Living World.
15. Texto malicioso de NPC/LLM não altera ACL, autoria ou nível HIGH da operação.
16. Dilema entre PCs gera consequências de mundo sem presumir dano PvP, morte ou coerção habilitados.

## Pendências e limites

- A política de **interações hostis entre PCs** (PvP, roubo, coerção, duelo, morte permanente e limites do grupo) permanece **DEC-042 aberta**.
- Definições quantitativas de conflitos, UX de escolha/consentimento, votações, consentimento prévio por categoria, notificações, delegação, desconexão e migração de saves são trabalho futuro de SPECS.
- Não há comprovação de isolamento de falas privadas, cenas paralelas ou imposição dessas regras no multiplayer real do BG2:EE/EEex; exigem POCs.
- As regras do jogo base podem permitir ações que a ponte ainda não consiga impedir. Não presumir bloqueio preventivo até testes de engine; registrar e reconciliar efeitos involuntários.

## Consequências

**Positivas:** favorece agência individual, cooperação voluntária, histórias que se influenciam e segredos descobertos causalmente.

**Riscos:** conflitos de preferências, divulgação de informações não prevista, exposição de dados no prompt/cliente e limites técnicos para impedir ações mecânicas entre PCs.

**Próxima discussão:** **DEC-042 — política de PvP e ações diretamente prejudiciais entre personagens de jogadores.**
