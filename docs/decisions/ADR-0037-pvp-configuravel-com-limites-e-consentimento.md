# ADR-0037 — PvP configurável, com limites e consentimento

- **Decisão:** DEC-042 — ações hostis entre personagens de jogadores.
- **Status:** **APROVADA — opção C**.
- **Aprovação:** 2026-11-06 (escolha expressa do idealizador do Infinity AI).
- **Fase:** Discovery; nenhuma funcionalidade está implementada nem testada.
- **Versão do pacote:** Discovery v3.8.
- **Referências:** DEC-001/003 (coop/multiplayer e POCs), DEC-004 (modos separados), DEC-008 (persistência), DEC-011 (host), DEC-012 (Action Gateway), DEC-019/020 (segredos/históricos), DEC-027/034 (risco e canon), DEC-028 (conhecimento), DEC-035–038 (alinhamento/consequências), DEC-040/041 (histórias compartilhadas e autoridade).

## Contexto e motivação

O Infinity AI prioriza uma campanha **cooperativa privada**, mas permite que personagens tenham divergências éticas, rivalidades e objetivos incompatíveis. A DEC-041 confirma a autonomia dos controladores de personagens, sem dar a qualquer jogador o direito de impor escolhas a outro. Faltava determinar se e em quais condições um PC pode atacar, roubar, afetar magicamente, danificar, prender ou matar outro PC.

A seleção do usuário foi a **opção C**, não PvP irrestrito nem proibição permanente de todo conflito mecânico.

## Decisão vinculante

1. **Política configurável por campanha:** o anfitrião poderá configurar limites para ações hostis PC→PC. A configuração deve ser transparente aos participantes, versionada e **consistente** em todos os clientes da sessão. Sua existência na interface ainda depende de SPECS/POCs.
2. **Proteção e consentimento do jogador afetado:** permitir interações hostis requer compatibilidade com a política da campanha e o tipo de autorização pertinente. Habilitar genericamente uma campanha PvP não equivale, sem uma regra expressa escolhida por seus participantes, a consentimento ilimitado para todas as formas de dano, furto, coerção ou morte permanente.
3. **Categorias separadas:** discussão e rivalidade *narrativas*; duelo/ataque/dano; furto ou transferência coerciva de itens; controle mental/magia hostil; prisão/impedimento de ações; morte permanente e outros efeitos persistentes graves possuem permissões independentes.
4. **Default seguro proposto:** modo cooperativo sem ações mecânicas hostis PC→PC até opt-in explícito, para evitar a ativação implícita de comportamentos prejudiciais. O perfil seguro é uma proposta de baseline que deve ser detalhada antes de implementação; a opção C permite outros perfis configurados legitimamente.
5. **Consentimento OOC ≠ vontade do personagem:** autorização da pessoa que controla o personagem para determinada modalidade de PvP não implica que o personagem *deseje* ou *aceite* o ataque dentro da ficção. Nenhum agente ou outro jogador pode escrever o consentimento ou a fala do PC afetado.
6. **Escopo e validade:** autorização deve indicar participantes, modalidade, duração/validade, riscos e limites de consequência, com possibilidade de interrupção conforme protocolo previamente escolhido. A política de revogação para uma ação já mecanicamente confirmada exige definição adicional; revogar não reescreve fatos confirmados.
7. **Restrições para ausentes/desconectados:** não inferir consentimento novo de jogadores ausentes. Sem delegação explícita e política validada, bloquear operações hostis iniciadas durante ausência ou desconexão; não simular respostas, rendição ou escolhas por IA.
8. **Sem atalhos indiretos:** efeitos de área, armadilhas, invocações, NPCs comandados, manipulação de facções, itens e efeitos ambientais não podem ser usados para contornar a política PC→PC. Se o motor não permitir bloquear a execução, tratar como limitação de alto risco e reconciliar eventos mecânicos confirmados sem fingir que foram prevenidos.
9. **Autoridade técnica:** regras/Action Gateway avaliam escopo e autorização; BG2:EE host é autoridade sobre efeitos mecânicos; resultados `UNCERTAIN` não permitem retry cego; o mundo persistente registra somente efeitos comprovados. Logs de consentimento são informações de controle com acesso restrito.
10. **Cânone e alinhamento:** PvP pode afetar reputação, relacionamentos e avaliação moral conforme autoria/ações confirmadas, não automaticamente por uma etiqueta PvP; acontecimentos HIGH e desvios históricos continuam sob DEC-027/034. Morte permanente de PC precisa de política específica adicional à permissão genérica de combate.
11. **Modo Original isolado:** a política do Living World não deve alterar saves, configurações e mecânicas do modo Original.
12. **Governança de sessão:** anfitrião **configura** políticas mas não consente por outro jogador. Mudanças materiais na política durante uma sessão exigem aviso, reapreciação dos participantes atingidos e fronteira de aplicação segura; não ativar silenciosamente uma regra mais permissiva.

## Matriz de permissões candidata

| Categoria | Condição mínima de autorização | Estado inicial recomendado |
|---|---|---|
| Desentendimento, investigação, competição social | Regras narrativas DEC-041 e DEC-028 | Permitido sem controlar outro PC |
| Duelo consensual com limites claros | Política de campanha e concordância dos participantes atingidos no escopo previsto | Desativado até configuração/consentimento |
| Ataque, dano direto, efeitos de área intencionais | Política por categoria e validação de consentimento/escopo | Desativado |
| Furto ou transferência de item entre PCs | Política específica, validação do item e confirmação do host | Desativado |
| Feitiço hostil/coerção/encantamento sobre PC | Política específica, limites de agência e motor validado | Desativado |
| Aprisionamento/privação de controle | Política própria de restrição de ações e consentimento | Desativado |
| Morte permanente, perda definitiva, efeitos irreversíveis | Proteção especial/consentimento explícito e regras próprias, inclusive políticas HIGH se aplicáveis | Bloqueado até SPECS e POCs |

**Importante:** a tabela é uma proposta de política operacional, **não uma lista de funções implementadas ou garantias de interceptação no BG2:EE**.

## Exemplos de perfis candidatos (sem ativação automática)

- `coop_safe` — rivalidades narrativas permitidas; interações PC→PC prejudiciais bloqueadas por padrão.
- `duels_consensual` — duelos opt-in entre participantes, com limites e prazo; não autoriza automaticamente furto, coerção ou morte permanente.
- `custom_pvp` — categorias e escopos explicitamente pactuados pela campanha, após POCs de aplicabilidade.

Nenhum perfil, parâmetro ou fluxo de UI está tecnicamente comprovado. Requisitos específicos para votação, consentimento por sessão vs. por ato, revogação e *friendly fire* ficam para SPECS.

## Invariantes e consequências

- Nenhum PC é representado ou autorizado por um LLM sem escolha humana correspondente.
- Ação externa legítima e repercussão do mundo (DEC-041) **não** são passe livre para atacar/roubar outro PC.
- Política de PvP e classificação de risco são verificadas por regras; texto de NPC/LLM não as modifica.
- Host é autoridade mecânica; registro de permissão não é recibo de execução e vice-versa.
- Não prometer bloqueio mecânico preventivo em uma instalação não testada.
- Dados de perfil e consentimento persistem por campanha de modo protegido e auditável, evitando vazamento de históricos.
- Uma transferência host-confirmada não pode ser duplicada por reconnect/retry nem removida do log por revogação posterior.
- Campanha configurada como coop segura permanece jogável ainda que modos PvP não sejam viáveis tecnicamente.

## Critérios candidatos para SPECS e POCs

1. PvP desativado: ataque direto PC→PC é bloqueado quando houver hook viável; quando não houver, detecção/falha segura sem prometer reversão mecânica automática.
2. Configuração de duelo só permite ações entre participantes autorizados e dentro do escopo do duelo; não autoriza ações contra terceiros.
3. Jogador desconectado não é considerado participante autorizador de novas hostilidades.
4. Convite narrativo/quest não concede consentimento mecânico automaticamente.
5. Política veda furto, mas permite duelo: transferência de item é recusada pela camada autorizativa.
6. Magias hostis e efeitos de área respeitam o alvo real e o escopo; dano colateral não passa despercebido.
7. Ação por familiar, armadilha, invocação ou NPC controlado não burla política PC→PC.
8. Mudança de configuração durante combate não ativa novas permissões sem protocolo seguro.
9. O anfitrião não consegue consentir em nome de outro controlador de PC.
10. Host confirma resultado mecânico; `UNCERTAIN` é reconciliado antes de replay.
11. Save/load mantém perfil de sessão/campanha e registros de consentimento válidos.
12. Modo Original não herda qualquer regra PvP do Living World.
13. Morte permanente exige política expressa distinta de duelo e segue restrições técnicas.
14. Reputação/alinhamento de participantes são calculados separadamente a partir de autoria/ações confirmadas.
15. Texto malicioso tentando induzir gateway a habilitar PvP não altera configuração.
16. Dois clientes discordando sobre política/versionamento não aplicam mutações inconsistentes.
17. Jogador que recusa PvP ainda pode participar de quests cooperativas sem coerção.
18. Reabrir save ou retomar após desconexão não repete dano, perda de item ou outras consequências.

## Pendências e riscos

- **Integração não comprovada:** BG2:EE e EEex talvez não permitam interceptar **todas** as categorias, sobretudo efeitos de área, controle indireto e alterações de save já executadas. POC em host + 2 clientes é gate obrigatório antes de oferecer controles como garantidos.
- **Consentimento concreto pendente:** granularidade por ato, tipo, sessão, reciprocidade, revogação e interface não foram decididas; dependerão de SPECS/decisões posteriores.
- **Morte/ressurreição:** políticas de morte permanente, ressurreição e efeitos persistentes sobre PCs são tema de **DEC-043 (próxima)**.
- **Proteção de jogadores:** consentimento para ações diretas prejudiciais e suas categorias é distinto de aceitar que o mundo tenha consequências causais legítimas ou rumores sobre o personagem.

## Próxima discussão

**DEC-043 — morte, ressurreição e permanência dos personagens de jogadores:** comparar regra clássica, proteções cooperativas e política configurável com consequências narrativas persistentes.
