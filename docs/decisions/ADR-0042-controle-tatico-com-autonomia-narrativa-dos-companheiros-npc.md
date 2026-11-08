# ADR-0042 — Controle tático humano com autonomia narrativa e personalidade dos companheiros NPC

- **Decisão de produto:** DEC-047 — autonomia dos companheiros NPC recrutáveis no Living World.
- **Escolha:** **C — controle tático pelos jogadores e autonomia narrativa/personagem dos NPCs**.
- **Estado:** **APROVADA** pelo idealizador em 2026-11-06.
- **Versão:** Infinity AI Discovery **v4.3**.
- **Fase:** SDD/Discovery — diretriz arquitetural; **não é implementação funcional, SPEC final, nem demonstração de integração com BG2:EE/EEex multiplayer**.
- **Relacionamentos:** DEC-003, 004, 005-R, 008–012, 014, 019–022, 024–030, 031–034, 035–041, 043, 045–046. Referência técnica: `docs/47-companheiros-npc-controle-tatico-e-autonomia-narrativa.md`.

## Contexto

O Living World contém **PCs de jogadores** (com titular, histórico autoral e regras de delegação DEC-041/045/046) e **companheiros NPCs** (pessoas do mundo com história, motivações, lealdades, conhecimento e relações próprias). BG2:EE permite controlar taticamente companheiros da party, porém o comando mecânico não precisa significar submissão narrativa absoluta. O projeto deve preservar a experiência de combate e exploração típica do jogo e, paralelamente, dar consequências inteligíveis às convicções e experiências individuais dos NPCs.

## Decisão vinculante

1. **Separação de domínios:** jogadores mantêm **controle tático/operacional** dos companheiros recrutados, dentro das possibilidades nativas do motor e das regras da campanha. O **agente narrativo do NPC** mantém identidade, crenças, desejos, limites, relações, memória e objetivos próprios, sem adquirir autoridade mecânica unilateral.
2. **NPC não é PC delegado:** não há titular humano de biografia do NPC nem procuração automática de identidade; a atribuição de slots e os grants da DEC-046 se referem a PCs de titulares humanos, e não se aplicam indistintamente à personalidade de companheiros NPCs. Quando algum NPC estiver sob controle tático de um jogador, comandos não equivalem a vontade, consentimento ou conhecimento ilimitado desse NPC.
3. **Respostas narrativas causais:** personagens podem **aprovar, discordar, aconselhar, protestar, negociar, propor missões, estabelecer limites e, quando permitido e tecnicamente validado, tentar sair da party**. Gatilhos dependem de acontecimentos confirmados ou crenças com proveniência, contexto, relacionamentos, alinhamento/valores próprios e oportunidade narrativa.
4. **Autonomia gradual, não aleatória:** reação deve ser proporcional, explicável e preferencialmente progressiva. Uma desaprovação momentânea não exige deserção; padrões graves podem elevar o conflito. Critérios, severidades, limiares, cadência e mecanismos de saída **são SPECS futuras**, assunto central da DEC-048.
5. **Conhecimento legítimo e privacidade:** NPCs somente reagem a fatos presenciados, informações que legitimamente receberam ou crenças/rumores atribuídos e rastreáveis. Nunca recebem automaticamente segredos privados de PCs, fatos de outras regiões nem informações do jogador humano só por integrarem a party. DEC-019/028/029/041 continuam vigentes.
6. **Fidelidade ao cânone:** companheiros oficiais de BG2:EE devem conservar, como ponto de partida, personalidade, relações, arco, contexto temporal e regras de seus conteúdos originais, sujeitos a curadoria por fonte e cronologia. Acontecimentos divergentes confirmados podem alterar trajetórias dentro das salvaguardas aprovadas, sem retcon silencioso nem substituição indiscriminada de diálogos, banters, scripts, romance ou flags já existentes. NPCs inéditos requerem validação e limites equivalentes.
7. **Regras primeiro; IA sob demanda:** estados, elegibilidade e avaliação de reação serão determinados prioritariamente por regras determinísticas e registros; IA local auxiliará na formulação de conversas e opções abertas filtradas. Não manter um LLM constantemente ativo por companheiro, não criar comandos arbitrários, não permitir que um modelo determine sozinho perda de recursos, retirada ou efeitos na party.
8. **Consequências em camadas:** sentimentos, intenções e sugestões narrativas podem ser registradas pelo serviço narrativo; mudanças efetivas de party, ordens, posição, inventário, quest flags, recrutamento, saída, combate e outros efeitos do motor **somente após gateway autorizado e recibo do host**. `UNCERTAIN` deve ser reconciliado, nunca repetido cegamente.
9. **A autonomia não viola a agência dos PCs:** um NPC pode discordar e oferecer consequências legítimas, mas não inventa fala, consentimento, amor, confissão, alinhamento ou ações de um PC. Ausência de um jogador não concede à IA autorização para interpretar seu personagem. PvP, morte, eventos HIGH e proteção do cânone mantêm seus controles.
10. **Compatibilidade e fallback:** se o motor não suportar impedir ordens incompatíveis ou executar saída/recusa segura, registrar apenas reação narrativa verificável ou usar interações roteirizadas existentes, sem declarar veto mecânico implementado. Não sequestrar o controle do personagem nem forçar save state inconsistente.
11. **Escala e persistência:** memória/relacionamentos dos NPCs utilizam snapshots + ledger por campanha, observadores e proveniência, com comportamento escalonado por região e tempo DEC-021/022; evitar inferência a cada tick/ataque e duplicar eventos no save/load ou após reconexões.
12. **Isolamento de modos:** o modo Original permanece fiel às regras e aos conteúdos originais, separado de saves e políticas do Living World.

## Por que esta opção foi escolhida

- **Em relação à A**, preserva controle tático e compatibilidade de jogo, mas evita tratar companheiros como peças sem história ou convicções.
- **Em relação à B**, evita substituir o combate controlável do BG2:EE por agentes inteiramente autônomos, com risco alto de latência, comportamento inesperado e sincronização multiplayer.
- **Com C**, comando mecânico e agência narrativa coexistem, com fronteiras explícitas entre narrativa, proposta e estado do motor.

## Invariantes

- `TACTICAL_CONTROLLER != NPC_NARRATIVE_AUTHOR`; `NPC != PC_DELEGATED`.
- `NPC_REACTION != HOST_MECHANICAL_EFFECT`; `PROPOSAL != ENGINE_RECEIPT`.
- `NPC_KNOWLEDGE = LAWFUL_OBSERVATION + PROVENANCED_REPORTS`, nunca onisciência do LLM.
- `CANON_IDENTITY != INALTERABLE_FUTURE`; divergências exigem causa, cronologia e proteção do cânone.
- `NARRATIVE_DISSENT != PROVEN_ENGINE_REFUSAL`; sem POC não prometer bloqueio de comandos/saída da party.
- `OWNER_AUTHORITY(PC) != CONTROLLER_AUTHORITY(NPC)`; nenhuma escolha pessoal de PC pode ser inventada pelo companheiro.

## Riscos e provas pendentes

- Falta inventariar scripts, diálogos, reações, conflitos e sistemas de romance/party dos NPCs originais da instalação real, inclusive alterações por mods/EET.
- Não comprovados: bloqueio de ordens em combate, estados de aprovação nativos, saída/recrutamento dinâmicos, suspensão/retomada de banters, alteração segura de flags, sincronização cliente/host e persistência em BG2:EE + EEex multiplayer.
- Riscos: duas fontes de autoridade competirem pela mesma ação; LLM contradizer o caráter canônico; segredos vazarem; dupla aplicação de deserção/quest; saída ocorrer em momento inseguro; NPC reagir ao que não testemunhou.
- Provas: baseline BG2:EE limpo → leitura/observação de eventos → reação apenas narrativa → proposta tipada de efeito → teste de integração isolado host+2 clientes → regressões EET/IWD/NWN; rollback seguro apenas quando comprovado.
- Referência: `docs/47-companheiros-npc-controle-tatico-e-autonomia-narrativa.md` contém modelo candidato, matriz de riscos, gates e testes.

## Próxima decisão

**DEC-048 — Como os NPCs deverão expressar desacordo e chegar a recusar ordens, romper alianças ou deixar a party?** Examinar um sistema gradual e contextual de limites, avisos, negociação e consequências, distinguindo autonomia narrativa de coerção mecânica e respeitando suporte validado do motor.

**Nenhum código foi escrito ou validado nesta decisão.**
