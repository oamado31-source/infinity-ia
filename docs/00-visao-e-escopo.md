# Visão e escopo — Infinity AI

**Versão:** 0.1 (rascunho)  
**Estado:** discovery; itens pendentes não devem ser interpretados como decisões aprovadas.

## Visão

Criar uma experiência pessoal de RPG multiplayer baseada na estética e nos conteúdos da Infinity Engine, onde o universo reage aos jogadores com NPCs, eventos, missões, encontros e memória persistente assistidos por agentes de IA. O mesmo lugar deve permitir novas experiências em visitas posteriores, com consistência narrativa e mecânica.

## Intenções já expressas pelo idealizador

- Uso privado para entretenimento, sem pretensão comercial nesta fase.
- Preferência forte pela estética isométrica 2D e pelos requisitos gráficos reduzidos de Baldur's Gate em relação a Neverwinter Nights 3D.
- Reaproveitamento de mapas e conteúdo existente de Baldur's Gate, Icewind Dale e adaptações de Neverwinter Nights compatíveis.
- Multiplayer é parte essencial da visão, mas o **modelo de sessão** permanece indefinido.
- Primeira fase não precisa de intervenções de um GM humano; a IA sustenta a dinâmica do mundo.
- NPCs conversam e reagem a contexto, têm memória e podem ofertar tarefas, comércio e consequências.
- Geração de encontros, criaturas, ruínas/masmorras e conteúdo, condicionada às limitações do motor.
- Organizar primeiro o projeto por Spec-Driven Development (SDD), com arquivos Markdown; só depois implementar código e realizar testes reais.

## Proposta de fronteiras do sistema (a validar)

1. **Cliente visual e mecânico:** BG2:EE / EET, sujeito a teste.
2. **Integração com o jogo:** recursos nativos de modding, WeiDU, EEex e ferramenta de integração externa, sujeitos a teste de versões e multiplayer.
3. **Controlador de ações:** serviço intermediário de validação, autorização, limites e logging; não executar código Lua gerado livremente pelo modelo.
4. **IA narrativa e diretor de conteúdo:** diálogos, planos e propostas de mudanças com respostas estruturadas.
5. **Estado do mundo:** persistência de fatos, NPCs, acontecimentos, missões e compartilhamento entre jogadores quando aplicável.
6. **Biblioteca de recursos:** indexação de áreas/criaturas/itens/efeitos disponíveis e adaptadores para mods.

## Não objetivos iniciais sugeridos (não aprovados)

- Criar um motor gráfico novo.
- Produzir automaticamente milhares de mapas originais em tempo real.
- Suportar dezenas ou centenas de usuários simultâneos no MVP.
- Permitir que a IA altere scripts ou arquivos dos jogos sem validação.
- Criar um editor de poderes de GM na primeira entrega.

## Primeiro ciclo demonstrável proposto

Um grupo visita uma área preexistente, conversa com um NPC via IA, sai, retorna mais tarde e encontra o NPC com memória contextual. Um novo acontecimento usa recursos válidos do jogo, grava alterações no mundo e é consistente para os participantes de uma sessão multiplayer.

**Atenção:** a viabilidade técnica do ciclo acima ainda não foi demonstrada em instalação real com EEex + EET + multiplayer.

## Dependências de decisão

- DEC-001 — modelo de multiplayer.
- DEC-002 — ambiente de desenvolvimento e plataforma prioritária.
- DEC-003 — motor/versão e política de expansão dos mods.
- DEC-004 — sistema de regras e equilíbrio de encontros.
- DEC-005 — escopo de persistência e continuidade entre sessões.
- DEC-006 — provedor/modelos de IA, operação local/remota, custos e latência.
- DEC-007 — política de geração e importação de mapas novos.
- DEC-008 — tratamento de textos, vozes, personalidades e continuidade narrativa.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

DEC-072 limita encontros emergentes a composição de templates/componentes versionados e comprovados por build; não promete geração dinâmica de assets nem spawn.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Personagens podem operar sob personas narrativas e anonimato contextual; segredos e reputações não ficam automaticamente visíveis para todo o mundo. Separar identidade privada comprovada, o nome usado e a crença de cada observador.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Responsabilidade de agentes, chefias e instituições só após investigação contextual; eventos de abuso geram narrativa sem punição mecânica presumida.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Proteção de fonte é um requisito narrativo/segurança; permite testemunhos redigidos sem supor invisibilidade, imunidade ou mecânica de proteção no BG2:EE.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Testemunhas podem pedir ajuda e enfrentar ameaças contextualizadas, sem invulnerabilidade, teleporte ou perseguições inventadas; a ação real depende de recursos e host.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Operações de proteção e descoberta parcial por NPCs só evoluem por evidência/canal legítimos; segredos de missão não se tornam visíveis por constarem no estado interno.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Enganos defensivos permitidos como operações narrativas autorizadas com recursos, destinatário e consequência rastreáveis, jamais como alteração da verdade do mundo.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

A política de NPCs persistentes comporta lealdades múltiplas com motivações comprovadas; personagens de jogadores conservam autoria de seus compromissos. Suspeita de traição não equivale a fato.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Informantes voluntários são agentes sociais persistentes: propostas não criam automaticamente acordos, recursos ou conhecimento. Narrativa social usa fatos e consentimentos.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

O produto distingue informe entregue, alegação, corroboração independente e verdade privada. Narrativas de espionagem não usam a LLM como detector infalível de mentiras.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

O mundo cooperativo poderá ter dossiês de investigação privados, versões filtradas para autoridades/aliados e transmissão por canais legítimos; não confundir haver informação no overlay com conhecimento de NPC.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

O Living World pode sugerir planos a partir de dossiês incompletos, mas não executa ações por interpretação textual da IA; PCs mantêm decisões próprias.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Escopo living world passa a incluir alterações seguras de planos após eventos confirmados; não confundir pausa de scheduler com pausa nativa BG2:EE.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

O Living World pode manter operações independentes em paralelo com recursos e tempo compatíveis; o scheduler lógico não controla diretamente o BG2:EE nem substitui consentimento dos PCs.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

As operações do Living World podem progredir em paralelo, mas a recuperação de espera circular ou starvation é uma decisão de segurança: não interromper PC, apagar evento ou duplicar NPC por conveniência narrativa.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Operações parcialmente realizadas usam Saga de compensações verificáveis DEC-095, sem rollback universal. Proposta DEC-096: matriz de cronologia DR/locais/efeitos condicionais indexada (ainda não aprovada), com lore separado de regras e overlay.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.


### Integração DEC-102/C (Discovery v9.8)

A reconciliação de quests DEC-102/C não muda o motor nem a história confirmada: corrige no máximo projeções derivadas mediante revisão autorizada. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para governança do escopo e distinção fato/boato/opinião, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para escopo Living World e limites de autoridade, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Papéis separados (acordo, claim, receipt, contestação) e não coerção. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Escopo continua cooperativo privado: acordos entre facções não atribuem decisões aos PCs. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Incluir garantias condicionais como capacidade futura, não MVP obrigatório; até validação EEex, nenhum bem está mecanicamente custodiado. As 28 decisões do questionário delimitam o primeiro ciclo SPEC sem exigir todo Living World pronto.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
