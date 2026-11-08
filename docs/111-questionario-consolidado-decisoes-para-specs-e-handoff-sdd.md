# Infinity AI — Questionário consolidado de decisões para SPECs e início do desenvolvimento

**Edição:** 1.0 · **Base:** Discovery v10.6 / DEC-110/C · **Situação:** perguntas em aberto, **nenhuma resposta presumida**.

## Objetivo

Permitir responder em **um único documento** às decisões de produto, integração e operação que faltam antes de produzir a *Constitution* e as SPECs executáveis. **Não repetir nem substituir decisões já aprovadas.** Cada pergunta indica uma recomendação, mas é o idealizador quem ratifica. Não precisamos abrir um ADR separado para cada teste ou tarefa: agrupar resoluções coerentes em ADRs temáticos e derivar SPECS por feature.

## Estimativa e estratégia

- **O que já existe:** 104 ADRs aprovados; decisões de arquitetura e domínio amplas, sem POC real EEex+BG2:EE+2 clientes comprovada.
- **DECs formalmente abertas antes da DEC-110:** DEC-006, 007, 013, 015, 016, 017 e 018; após DEC-110/C essas **sete** continuam em aberto, além de novas escolhas de implementação.
- **Necessárias para começar a escrever/implementar SPECs:** cerca de **8–12 deliberações/gates agrupados** (não necessariamente 12 novos ADRs). O **bloco P0 contém 12 perguntas** suficientes para o primeiro ciclo, sem esperar o restante.
- **Para um MVP tecnicamente verificável e uma V1 delimitada:** estimativa de **20–30 respostas de escopo/operacionalização ao todo**; este documento traz **28 perguntas** (12 P0 + 16 P1). Novas decisões podem surgir após POCs, sem atrasar toda a implementação.
- **Não prometemos um número final de DECs:** a viabilidade do EEex, da bridge, do multiplayer e dos recursos de runtime ainda precisa de evidências; novos blockers serão controlados por gates, não por entrevistas intermináveis.
- **Prioridade:** fechar P0 em uma única rodada, gerar Constitution/SPECs, iniciar testes de integração e continuar P1 quando necessário. O P1 pode ser respondido junto para economizar conversas.

## Como responder

Edite somente o campo `**Sua escolha:**` de cada pergunta com **A, B ou C**; escreva D quando quiser uma alternativa própria e descreva a mudança. **A opção recomendada não é consentimento implícito.** Você também pode responder em uma única mensagem: `Aprovo todas as recomendações, exceto Q07=A, Q20=C; observações: ...`. Assim consigo registrar as respostas em lote, gerar ADRs temáticos e transformar cada escolha em requisitos `REQ-...` e critérios de aceitação.

**Controle de resposta:**
- Responsável: ____________________
- Data: ____________________
- Baseline revisada: `Discovery v10.6`
- Aceitar todas as recomendações, exceto exceções abaixo? `[ ] Sim` `[ ] Não`
- Exceções / comentários globais: ________________________________________________

## Bloco P0 — decisões para iniciar SPECs executáveis


### Q01 — Recorte demonstrável (P0)

**Pergunta:** Qual vertical slice fecha o primeiro protótipo?

- **A.** Só chat NPC fora do jogo
- **B.** Bridge read-only + dois clientes + NPC com memória + uma proposta sem spawn real
- **C.** Living World com comércio, quest e IA completos

**Recomendação:** B — Valida integração primeiro; memória/efeito podem evoluir por gates sem prometer engine.

**Referências:** DEC-001/003/004/014.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q02 — Build e compatibilidade (P0)

**Pergunta:** Como fixar versões do ambiente inicial?

- **A.** Instalar versões atuais sem manifesto
- **B.** Fixar build/hash/modlist; BG2:EE limpo → EEex isolado → bridge
- **C.** Adicionar EET/IWD/NWN no primeiro build

**Recomendação:** B — Reduz variáveis durante debug e facilita rollback.

**Referências:** DEC-013 aberta; DEC-002/003.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q03 — Gates de teste (P0)

**Pergunta:** Qual regra impede avançar com capability presumida?

- **A.** Testes manuais informais
- **B.** Gates P0–P4 com provas e rollback; novo recurso só após teste na build e 2 clientes
- **C.** Aprovação documental basta

**Recomendação:** B — Evita converter testes sintéticos em alegações de integração.

**Referências:** DEC-015 aberta.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q04 — Bridge e captação (P0)

**Pergunta:** Qual primeiro contrato da bridge?

- **A.** Read-only allowlisted e respostas UNKNOWN quando faltarem dados
- **B.** Leitura de flags ilimitada para simplificar
- **C.** Escrita e spawn desde o primeiro teste

**Recomendação:** A — Primeiro provar observar; mutação exige autorização isolada.

**Referências:** DEC-011/012/099/100.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q05 — Autoridade multiplayer (P0)

**Pergunta:** Qual é o critério de aceite para dois clientes?

- **A.** Basta o host confirmar
- **B.** Host e dois clientes observam resultados coerentes após save/reload, com auditoria de divergências
- **C.** Deixar o segundo cliente para depois do MVP

**Recomendação:** B — Multiplayer é requisito do projeto, não uma feature tardia.

**Referências:** DEC-001/011/041/045.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q06 — Política operacional de LLM (P0)

**Pergunta:** Como lidar com modelos, hardware e API remota?

- **A.** Somente modelo local sem alternativa
- **B.** Modelo local por padrão; remoto só opt-in explícito, contexto filtrado e teto de gasto
- **C.** Remoto por padrão e sem confirmação

**Recomendação:** B — Mantém local-first e prevê indisponibilidade e privacidade.

**Referências:** DEC-006 aberta; DEC-014.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q07 — UI de diálogos (P0)

**Pergunta:** Como apresentar conversas e ações?

- **A.** Somente diálogos nativos
- **B.** Overlay/janela externa até comprovar UI nativa segura; adaptar para nativa quando viável
- **C.** Modificar arquivos de diálogo por LLM em runtime

**Recomendação:** B — Permite POC sem depender de hook de UI incerto.

**Referências:** DEC-007 e DEC-016 abertas.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q08 — Persistência mínima (P0)

**Pergunta:** Qual baseline técnico inicial de estado e eventos?

- **A.** Arquivos JSON pontuais sem log
- **B.** SQLite local + log append-only + snapshots/epochs e separação por campanha
- **C.** Servidor remoto obrigatório desde o início

**Recomendação:** B — O backend continua substituível via contratos; mantém rastreabilidade local.

**Referências:** DEC-008/011/053/060/066.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q09 — Autorizações na sessão (P0)

**Pergunta:** Como coletar autorização para ações?

- **A.** Host autoriza tudo pelos outros
- **B.** Consentimento do titular + host para mecânica; categorias HIGH fail-closed
- **C.** A IA decide pelo grupo após votação automática

**Recomendação:** B — Não substitui agência de PCs ausentes ou delegados.

**Referências:** DEC-011/012/027/041–046.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q10 — Logs e recuperação (P0)

**Pergunta:** Como registrar evidência de execução e falha?

- **A.** Somente prints de console
- **B.** Logs estruturados locais + action IDs, checkpoints, redaction e replay sintético
- **C.** Telemetria remota obrigatória

**Recomendação:** B — Essencial para diagnosticar desync e evitar duplicidade.

**Referências:** DEC-018 aberta; DEC-053/055.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q11 — Fallback da integração (P0)

**Pergunta:** Se EEex/bridge falhar na POC, qual tratamento?

- **A.** Bloquear mutações e continuar SPEC/testes no simulador, sem fingir integração
- **B.** Migrar imediatamente todo o projeto para GemRB
- **C.** Assumir capabilities não comprovadas e prosseguir

**Recomendação:** A — Separar viabilidade real e lógica simulada.

**Referências:** DEC-003/012/015.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q12 — Método SDD / handoff (P0)

**Pergunta:** Como aprovar e versionar SPECs futuras?

- **A.** Modificar SPECs diretamente sem registro
- **B.** Constitution + SPECs numeradas; change request com diff, impacto, teste e baseline
- **C.** Congelar todas as SPECs permanentemente

**Recomendação:** B — Rastreabilidade sem burocracia excessiva; DEC-111 ainda por ratificar.

**Referências:** DEC-111 proposta; docs/01.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


## Bloco P1 — implementação posterior, escopo de V1 e funcionalidades dependentes de POCs


### Q13 — Custódia e garantias (P1)

**Pergunta:** Em qual fase tentar escrow mecânico real?

- **A.** Antes da bridge read-only
- **B.** Após POC de inventário, ownership e 2 clientes; até lá só registro narrativo
- **C.** Nunca implementar nem mesmo se viável

**Recomendação:** B — DEC-110 foi aprovada; esta pergunta escolhe prioridade, não reabre a decisão.

**Referências:** DEC-110/C aprovada.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q14 — Conteúdo e licenças (P1)

**Pergunta:** Qual política de importação de assets e mods?

- **A.** Copiar indiscriminadamente recursos para um pacote distribuível
- **B.** Referenciar instalações legítimas locais; não redistribuir assets protegidos; curadoria e proveniência
- **C.** Gerar substitutos por IA sem revisar direitos

**Recomendação:** B — Distingue uso privado de distribuição e evita dependências ocultas.

**Referências:** DEC-017 aberta.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q15 — Memória de NPCs (P1)

**Pergunta:** Quanto do histórico manter no MVP?

- **A.** Tudo no prompt do modelo
- **B.** Fatos tipados e resumos por NPC/PC, proveniência, janela e ACL; recuperar sob demanda
- **C.** Somente memória da sessão corrente

**Recomendação:** B — Permite consistência e limita custo/contexto.

**Referências:** DEC-064–066/028.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q16 — Matriz cronológica (P1)

**Pergunta:** Qual escopo do primeiro pacote canônico validado?

- **A.** Todo Forgotten Realms de uma vez
- **B.** Um recorte por ano DR e duas regiões, com fontes e datas curadas
- **C.** Cronologia elaborada livremente pela LLM

**Recomendação:** B — Começa com fixture auditável, sem bloquear expansão.

**Referências:** DEC-060–063/096/097.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q17 — Catch-up regional (P1)

**Pergunta:** Qual nível de simulação fora de cena no MVP?

- **A.** Simular cada NPC em tempo real
- **B.** Ativo perto do grupo; agregado/dormant distante, com orçamento e checkpoints
- **C.** Pular todo avanço temporal offscreen

**Recomendação:** B — Respeita limites de CPU e evita eventos arbitrários.

**Referências:** DEC-021/022/068–074/098.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q18 — Primeiro evento emergente (P1)

**Pergunta:** Qual primeira prova de evento dinâmico?

- **A.** Spawn livre de criaturas
- **B.** Template de encontro seguro em save descartável, após read-only + capability provada
- **C.** Gerar dungeon procedural no primeiro sprint

**Recomendação:** B — Compõe conteúdo compatível com a build e isola risco.

**Referências:** DEC-005-E/072–074/091–098.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q19 — Quests originais (P1)

**Pergunta:** Quando incluir interpretação de quests originais?

- **A.** Na primeira POC de bridge
- **B.** Depois da leitura segura: um mapeamento semântico de quest em build fixa
- **C.** Mapear todas as quests e mods simultaneamente

**Recomendação:** B — Respeita spoilers, versões e provas.

**Referências:** DEC-050/099–104.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q20 — Voz e TTS (P1)

**Pergunta:** Qual prioridade de voz no protótipo?

- **A.** Obrigatória em todo diálogo
- **B.** Texto primeiro; TTS opcional após estabilidade da memória e da UI
- **C.** Somente voz, sem texto

**Recomendação:** B — Evita bloqueio por latência/áudio e acessibilidade.

**Referências:** DEC-007/014/016.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q21 — Expansões/modpacks (P1)

**Pergunta:** Quando incorporar EET, IWD e NWNForBG?

- **A.** Tudo na primeira instalação
- **B.** Após gate BG2:EE+EEex+bridge+2 clientes e regressão por mod
- **C.** Nunca considerar expansões

**Recomendação:** B — Mantém ambiente reproduzível.

**Referências:** DEC-003/013/051.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q22 — Combate em turnos (P1)

**Pergunta:** Qual posição do combate por turnos opcional?

- **A.** Bloqueia o MVP até funcionar
- **B.** Trilha experimental separada; MVP usa combate nativo BG2:EE
- **C.** Ativar por mudança de script sem POC

**Recomendação:** B — Já aprovado como objetivo, ainda sem viabilidade.

**Referências:** DEC-005-T bloqueada por teste.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q23 — Economia e facções (P1)

**Pergunta:** Qual profundidade econômica da V1?

- **A.** Economia mundial granular por comerciante
- **B.** Índices regionais agregados e regras curadas; preços mecânicos só se testados
- **C.** Deixar LLM escolher preços

**Recomendação:** B — Evita simulação custosa e manipulação arbitrária.

**Referências:** DEC-029–034/096/097.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q24 — Saves e migrações (P1)

**Pergunta:** Como tratar revisões de regras entre saves?

- **A.** Migrar tudo silenciosamente
- **B.** Versionar ruleset, snapshot, pacote canônico e migração explícita com rollback
- **C.** Sempre reiniciar campanha

**Recomendação:** B — Evita misturar timelines e alterar fatos históricos.

**Referências:** DEC-004/053/063/098/102.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q25 — Conexão de jogadores (P1)

**Pergunta:** Como será a conexão prioritária do primeiro teste multiplayer?

- **A.** Servidor público acessível na internet
- **B.** Rede privada/LAN ou VPN aprovada, autenticação e mínimo acesso
- **C.** Expor porta publicamente por conveniência

**Recomendação:** B — Coop privado é decisão aprovada; reduz superfície de ataque.

**Referências:** DEC-001/002/057/058.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q26 — Painel de explicabilidade (P1)

**Pergunta:** Que informações mostrar na interface administrativa?

- **A.** Somente resultado final
- **B.** Proposta → evidências → consentimentos → ação → receipt → divergências, com filtro de segredos
- **C.** Logs brutos de todos os NPCs visíveis aos jogadores

**Recomendação:** B — Ajuda depuração e respeita conhecimento contextual.

**Referências:** DEC-025–028/055/091–095.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q27 — Conteúdo narrativo (P1)

**Pergunta:** Quanto protagonismo emergente na primeira V1?

- **A.** Campanhas oficiais substituídas
- **B.** Arcos oficiais preservados; eventos pessoais opcionais N1/N2 antes de N3
- **C.** Intervenção N3 automática por IA

**Recomendação:** B — Respeita canon, agência e progresso por condições.

**Referências:** DEC-025/026/039/040/072.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


### Q28 — Critério de primeira entrega (P1)

**Pergunta:** Qual é o Definition of Done da primeira versão demonstrável?

- **A.** Demonstração visual sem persistência
- **B.** 2 clientes, observação segura, NPC com memória, save/load, auditoria e nenhum efeito não autorizado
- **C.** Todas as 100+ decisões implementadas

**Recomendação:** B — Critério técnico alcançável que não exige implementar toda a visão.

**Referências:** DEC-003/015; docs/01.

**Sua escolha:** `[  ]`  **Observação/alternativa D:** ________________________________________________


## Matriz de rastreabilidade e prioridade

| Bloco | Respostas | Artefato a gerar após aprovação | Gate |
|---|---|---|---|
| P0 / núcleo | Q01–Q12 | Constitution, SPEC-001 read-only bridge, SPEC-002 autoridade/host, SPEC-003 estado local/memória, planos, tasks, testes | P0–P4 |
| P1 / experiência | Q13–Q22 | Backlog priorizado de funcionalidades, SPEC-004 diálogos, SPEC-005 eventos regionais, SPEC-006 quests | Somente após capability correspondente |
| P1 / produção privada | Q23–Q28 | Especificações de economia/facções, save migration, segurança e observabilidade | Regresso e segurança |

## Mapeamento dos sete DECs anteriores ainda abertas

- DEC-006 → Q06.
- DEC-007 → Q07 e Q20.
- DEC-013 → Q02 e Q21.
- DEC-015 → Q03 e Q28.
- DEC-016 → Q07 e Q26.
- DEC-017 → Q14.
- DEC-018 → Q10 e Q24.

A **DEC-110/C está aprovada**, mas seu cronograma de implementação ainda é escolha P1 em Q13. A DEC-111 (governança da baseline das SPECs, Q12) permanece **proposta** até ratificação. As escolhas que implementarem decisões aprovadas não as substituem; se houver conflito com ADR anterior, abrir *change proposal* explícita.

## Critérios da Constitution (a ratificar; não assumir aprovados automaticamente)

1. Host autoritativo em efeitos mecânicos; LLM não emite comandos executáveis sem gateway.
2. Nenhum estado `UNKNOWN` vira afirmação, autorização, capability ou recibo.
3. Permissões de PC/owner e controle de segredos são gates independentes.
4. Compatibilidade por build; falhar fechado para alterações perigosas.
5. IDs estáveis, save branch/epochs, checkpoints e deduplicação.
6. Local-first, logs minimizados e histórico auditável.
7. Diferenciar testes sintéticos de integração real.
8. POC no BG2:EE limpo, EEex e dois clientes antes de expandir EET/IWD/NWN.

## Depois das respostas — entregáveis esperados (sem prometer implementação pronta)

1. **Constitution v1** com política de segurança, autoridade, privacidade, performance e verificação.
2. **Consolidação de ADRs temáticos:** resolver as sete DECs anteriores abertas e deliberações novas por assunto; atualizar mapa, dependências e changelog, mantendo ADRs aprovados históricos imutáveis.
3. **SPECS iniciais:** requisitos observáveis em EARS, cenários de aceite e não objetivos para bridge read-only, autoridade multiplayer e estado persistente.
4. **Plans & tasks:** contratos, sequenciamento de POCs, critérios de entrada/saída e evidências esperadas.
5. **Testes e matriz de compatibilidade:** distinguir simulação offline e provas reais em Windows/BG2:EE/EEex, host e dois clientes.
6. **Gestão de mudanças futura:** `CR-xxxx` → impacto em ADR/SPEC → `plan.md` → tarefas → testes → nova baseline. Mudar SPEC antes do código quando a alteração for arquitetural.

## Riscos e travas

Mesmo com todas as perguntas respondidas, **não há garantia de viabilidade da bridge EEex, mutação segura ou sincronização multiplayer**. Os gates P0–P4 serão as primeiras tarefas reais. Se um gate falhar, continuar com simulação e especificações isoladas, preservando o ambiente do jogo, sem inventar que o requisito foi implementado.

**Status do questionário:** AGUARDANDO RESPOSTAS. Nenhuma recomendação foi registrada como decisão do usuário automaticamente.
