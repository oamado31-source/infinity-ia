# Discovery — Cooperative Story Director: equilíbrio narrativo dinâmico

**Versão:** v3.6 | **Estado:** desenho técnico candidato, não SPEC nem implementação | **Decisão vinculante:** DEC-040/ADR-0035.

## Escopo

Promover oportunidades de protagonismo relevantes e voluntárias em campanhas cooperativas com históricos pessoais, sem rotação mecânica, imposição de missões ou abertura indevida de segredos. O serviço é um **orquestrador por eventos** sobre arcos pessoais do PSD, e não um narrador de IA que dirige todas as decisões.

## Diagrama lógico (não implica suporte já comprovado do BG2:EE)

```text
Host-confirmed world events + campaign chronology + actor availability
          |                  |                   |
          v                  v                   v
 Personal Story Director -- Cooperative Story Director
        |                    |    |
        |                    |    +-- focus/opportunity history
        |                    |    +-- eligibility + scheduling rules
        |                    |    +-- consent & knowledge filters
        |                    v
        +-------------- candidate offer ----------------------+
                                                              |
                 Offered to authorized character/party only <-+
                        | accept / defer / decline
                        v
         Risk/Canon/Knowledge guards + Action Gateway
                        v
            Host execution receipt -> Event Log
                        v
       Personal arcs, relationships & shared consequences
```

## Componentes conceituais

| Módulo | Papel | Restrições |
|---|---|---|
| PSD (DEC-039) | Fornece arcos, marcos, objetivos e dependências | Titular e decisões individuais não são substituídos |
| CSD | Seleciona oportunidades e coordena convites opcionais | Não administra mundo por LLM contínuo |
| Focus Ledger | Histórico de oportunidades oferecidas, aceitas e efetivamente vividas por personagem | Contagem pura de diálogos não mede mérito ou satisfação |
| Eligibility Engine | Confere data DR, região, tempo, personagens presentes, recursos, canon e conflitos | Não fabrica gancho para preencher quota |
| Knowledge & Consent Guard | Filtra informações por destinatário e aplica preferências/consentimento existente | Consentimento coletivo detalhado DEC-041 ainda aberto |
| Group Event Composer | Mapeia contribuições voluntárias e papéis cooperativos | Convites não concedem segredos nem poderes arbitrários |
| Action Gateway + host | Autoriza/valida e confirma alterações mecânicas | Sem Lua livre, sem efeito presumido |
| Persistência | Log, snapshots, versões de regras e checkpoints | Isolamento de modo e idempotência |

## Modelo de dados candidato

```yaml
campaign_id: campaign-001
rule_profile_id: pinned-rule-profile
story_director_version: pending
focus_ledger:
  - character_id: character-a
    offered_opportunity_ids: []
    played_milestone_ids: []
    recent_focus: not_scored
    last_meaningful_opportunity_at: null
proposed_offer:
  offer_id: offer-uuid
  arc_id: arc-existing
  owner_character_id: character-a
  invited_character_ids: []
  visibility: owner_only
  earliest_world_time: null
  latest_world_time: null
  prerequisites: []
  requires_owner_presence: true
  risk_classification: pending
  state: PROPOSED
  host_receipt_ids: []
```

Campos e valores são hipóteses a detalhar nas SPECS. `recent_focus` **não** implica a escolha de um escore, fórmula ou intervalo de sessões.

## Algoritmo lógico candidato (regras primeiro)

1. Receber um evento relevante, uma abertura narrativa real ou início de sessão; **não consultar LLM por tick**.
2. Examinar arcos ativos e oportunidades elegíveis por **cronologia, disponibilidade, requisitos, contexto e compatibilidade**.
3. Consultar ledger de oportunidades e participações anteriores, permitindo priorizar personagens menos contemplados quando houver oportunidades comparáveis; sem quota rígida.
4. Avaliar se a oferta é individual, cooperativa ou híbrida; não revelar história secreta na montagem do convite.
5. Gerar proposta e solicitar confirmação do titular para aceitar/compartilhar/adiar, respeitando a forma final de UI a ser especificada.
6. Oferecer papéis voluntários aos demais jogadores após filtros de conhecimento, sem impor a presença deles.
7. Aplicar as regras de autorização do evento, da DEC-027/034, e as futuras regras de consentimento da DEC-041. Executar apenas ações técnicas comprovadas e autorizadas.
8. Atualizar foco e progressão **após participação/eventos confirmados**, com recibos mecânicos idempotentes quando aplicáveis.
9. Em ausência, falha, conflito ou recurso indisponível: deferir/suspender/reavaliar, em vez de fabricar um sucesso ou impor missão.

## Semântica de participação

- **Titular:** personagem cujo histórico originou a trama. Ele determina como deseja envolver outras pessoas, dentro das consequências reais já estabelecidas pela campanha.
- **Convidado:** jogador que opta por apoiar um arco. Recebe uma visão compatível com o que seu personagem sabe, jamais o histórico íntegro do titular por padrão.
- **Impacto de grupo:** ações compartilhadas podem causar consequências globais confirmadas, mas as escolhas individuais não são atribuídas automaticamente ao grupo.
- **Ausente:** não assume escolhas, não revela segredo e não recebe penalidade arbitrária por perder a sessão. O avanço permitido de terceiros e eventos públicos segue DEC-022/025/034.
- **Múltiplos protagonistas:** quando dois arcos convergem, preservar titularidade, procedência e escolha de cada um; conflitos seguem para revisão/consentimento futuro, não fusão automática de backstories.

## Riscos e mitigação

| ID | Risco | Mitigação proposta |
|---|---|---|
| CSD-R01 | Um jogador monopoliza a experiência | Ledger de oportunidades e regras sensíveis à relevância, sem alternância artificial |
| CSD-R02 | Algoritmo força um arco incoerente para equilibrar | Eligibilidade por canon, localização, recursos e condição; deferimento legítimo |
| CSD-R03 | Missão cooperativa revela um segredo | Filtragem antes de prompts, convites, logs, UI e NPCs |
| CSD-R04 | Jogador ausente perde decisão pessoal crítica | Presença/autorização como pré-condição de marcos de alto impacto |
| CSD-R05 | Dois arcos competem pelo mesmo NPC, item ou flag | Reservas e resolução de dependências antes de ativação |
| CSD-R06 | Um convidado ganha recompensa duas vezes | IDs únicos, receipts do host, commit idempotente |
| CSD-R07 | NPC atribui intenção do grupo a um personagem | Verificação de autoria/participação antes de alinhamento e reputação |
| CSD-R08 | Queda do LLM interrompe a campanha | Fallback por templates e regras; IA sob demanda |
| CSD-R09 | Arcos individuais desequilibram calendário ou multiplayer | Política DEC-022, host autoritativo, estado compartilhado versionado |
| CSD-R10 | O modo Original recebe efeitos do Living World | Isolamento estrito por modo e campanha |

## Testes de aceitação candidatos (não executados)

| ID | Cenário | Resultado esperado |
|---|---|---|
| CSD-01 | Grupo de quatro com quatro históricos e ganchos distintos | Oportunidades plausíveis, não um só protagonista indefinidamente |
| CSD-02 | Uma trama exige continuidade em sessão consecutiva | Diretor pode mantê-la sem alternância arbitrária |
| CSD-03 | Jogador recusa convite para quest pessoal | Não é coagido nem punido por recusa extrínseca |
| CSD-04 | Titular aceita ajuda sem divulgar segredo | Convidados recebem somente contexto autorizado |
| CSD-05 | Titular decide investigar sozinho | Arco privado continua possível, se suportado por recursos técnicos |
| CSD-06 | Titular ausente e marco de alto impacto próximo | Não é concluído por escolha simulada do titular |
| CSD-07 | Arco de outro jogador continua durante ausência | Segue regras de tempo, risco, consentimento e confirmação pertinentes |
| CSD-08 | Dois arcos solicitam mesmo NPC ou item indivisível | Conflito detectado; sem duplicar recurso |
| CSD-09 | História não é compatível com 1369 DR | Bloqueio/adaptação verificada sem canon inventado |
| CSD-10 | Dois jogadores participam do mesmo encontro | Atribuição correta e idempotente de contribuições/recompensas |
| CSD-11 | LLM indisponível na sessão | Regras, scheduler e eventos já validados seguem operacionais |
| CSD-12 | Eventos mecânicos retornam `UNCERTAIN` | Arco fica pendente sem commit ou retry cego |
| CSD-13 | Salvar/reabrir depois de convites e progressões | Ledger, convites e marcos persistem sem duplicatas |
| CSD-14 | Abrir modo Original | Nenhuma intervenção de histórias pessoais do Living World |
| CSD-15 | Um rumor menciona segredo de histórico | Não há atribuição de conhecimento sem origem válida |
| CSD-16 | Convite exige compartilhar parte privada do histórico | Não divulgar antes de permissão legítima |
| CSD-17 | Um jogador participou, os demais só observaram | Alinhamento/reputação pessoal não são atribuídos indiscriminadamente |
| CSD-18 | História gera evento HIGH em outra região | Política DEC-034 prevalece sobre prioridade narrativa |
| CSD-19 | Uma história está sem recursos importados no mod | Suspender/replanejar sem afirmar conteúdo gerado in-game |
| CSD-20 | Dois clientes têm versão de agendamento diferente | Host valida configuração e não permite divergência persistente |

## O que ainda não foi decidido

- Fórmula, pesos, quotas, janelas, interface e notificações, cadência de oportunidades, definição precisa de *meaningful opportunity*.
- Se e como divisão de grupo, cenas privadas e várias áreas simultâneas funcionarão no multiplayer BG2:EE/EEex.
- Consentimento distribuído para atos coletivos e revelação de segredos que envolvem múltiplos personagens (DEC-041).
- Interface para preferências narrativas; tempo de sessão estimado; mecanismos de migração de saves.
- Schemas finais, benchmarks de latência, autorização real e POCs com dois clientes.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

NPCs emergentes DEC-067 podem reforçar histórias de um ou mais jogadores; não promover por frequência isolada, nem transferir segredos ou protagonismo sem autorização DEC-041.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Reconhecer trabalho coletivo e suporte, sem score secreto competitivo nem crédito obrigatório uniforme; ausentes/delegados sujeitos a consentimento e evidência.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Uma persona secreta não pode forçar outro PC a conhecer ou divulgar segredo; agência de jogadores e consentimento se mantêm. Narrativa de disfarce é distinta de mecânica implementada.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Quest de investigação institucional não força jogadores a apoiar/denunciar autoridade, nem transforma narrativa coop em decisão individual de PC.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Depoimentos e sigilos de PCs em história coletiva exigem consentimento; outro jogador não recebe acesso automático por ser membro da party.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Jogadores podem cooperar em proteção/abrigo/escolta, respeitando consentimento individual e decisões autônomas; o modelo não assume controle de PCs.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Partilhar missão não concede acesso global à rota sigilosa de outro PC; cooperação ocorre dentro de autorização de titular e papel.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Iscas e enganos entre membros do grupo não permitem violar agência de outro PC; efeitos cruzados seguem consentimento e risco, sem expor segredos por estar na party.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Cooperativo não pode usar suspeita de NPC como imposição de PvP, decisão secreta de PC ou revelação a outro membro da party sem consentimento/ACL.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Recrutamento cooperativo registra ownership e consentimento. Conflitos pessoais de vários PCs não autorizam um jogador a vender o segredo de outro.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Diretor cooperativo protege conhecimento assimétrico entre jogadores. Informação de um jogador sobre fonte não fica automaticamente disponível aos demais PCs.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Views por audiência da party preservam controle individual de segredos e agência, sem compartilhar todos os históricos apenas por cooperação.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Coordenação cooperativa pode comparar planos candidatos e conflitos, mantendo consentimento individual de cada PC.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

CSD preserva decisões individuais em mudança de planos compartilhados: PC que sai não é movimentado automaticamente; outros podem reavaliar de forma independente.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Arbitragem de recursos entre grupos deve ser justa e auditável sem beneficiar automaticamente uma party; PC titular decide aceitar substituição, atraso ou nova ação.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Fairness entre operações não se confunde com autorização para sacrificar missão ou compromisso de outro jogador; propostas de replanejamento dependem de consentimentos.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-097/C — Discovery v9.3

Impactos históricos compostos DEC-097/C geram oportunidades narrativas opcionais; não forçam participação de PCs.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Diretor cooperativo não assume autoridade sobre PCs, cenas ou quests por urgência ou protagonismo narrativo.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Cooperative Story Director não pode cruzar segredos de quests/PCs a partir de acesso técnico global.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

A DEC-102/C trata divergências entre milestone validado do host e projeção derivada do Living World: exigir mapeamento DEC-101, observação DEC-100, epoch/branch e receipts, e preservar o host, facts ledger e conhecimento dos NPCs. Somente proposta de revisão CAS/autorizada; detalhes em ADR-0097/doc. 102. **Sem POC mecânica.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para coop não permite que NPCs ajam por PCs ou assimilem crenças de PCs, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para autonomia cooperativa e decisões de PCs, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-109/C — Obrigações condicionais multipartes

Agendas narrativas não obrigam PCs a aceitar pactos de outros jogadores. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
