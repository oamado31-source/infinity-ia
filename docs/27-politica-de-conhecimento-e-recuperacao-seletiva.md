# Recuperação seletiva de conhecimento e montagem de contexto — desenho preliminar

**Discovery v2.5 · DEC-028 / ADR-0023 aprovada**  
**Natureza:** documento de arquitetura candidata, não SPEC; nenhuma interface foi implementada ou testada com BG2:EE.

## Objetivo

Uma memória compartilhada do mundo não é conhecimento compartilhado por todos os NPCs. O controle deve ocorrer **antes** da consulta ao repositório e antes da montagem do prompt, com proveniência de cada fato e escopo por destinatário. Narrador, sistema técnico, jogador e personagem são identidades diferentes.

## Entidades distintas

| Entidade | Acesso conceitual | Não implica |
|---|---|---|
| `world_state` | Canon adotado, eventos, snapshots e linhas divergentes da campanha | Conhecimento global por NPCs |
| `narrator` | Contexto mínimo necessário para planejamento autorizado | Revelação automática a todos ou privilégio de mudar a mecânica |
| `npc_actor` | Fatos presenciados, comunicados, descobertos ou legitimamente inferidos | Acesso irrestrito a históricos privados |
| `player_account` | Texto público, texto privado próprio e informações autorizadas de UI | Que seu personagem saiba tudo que o jogador leu |
| `player_character` | Fatos conhecidos na ficção por aquele personagem | Que outros jogadores tenham descoberto o mesmo |
| `specialist_agent` | Somente informações estritamente relevantes ao trabalho autorizado | Permissão para mutação ou acesso global |

## Arquitetura de leitura

```text
World Event Log + Current Projections + Historical Canon + Character Backstories
                                |
                              Storage
                                |
                 Knowledge/ACL Policy Engine (código)
     identity | scope | campaign | purpose | game time | source graph
                                |
                    Authorized Query / Retrieval
                                |
                    Context Builder / Redactor
                 labels of certainty and evidence
                                |
            NPC dialog LLM (local quando aplicável)
                                |
                   Risk policy DEC-027 + Action Gateway DEC-012
                                |
              Optional narrative event / host-confirmed mechanical action
```

`Storage` físico pode ser central, mas os índices, as projeções e as políticas devem impedir **leitura transversal**. A filtragem de metadados após um LLM ter visto o conteúdo é inadequada. Se uma busca semântica for usada, não construir automaticamente um resumo amplo pré-indexado que misture segredos; assegurar filtros verificáveis antes de expor *qualquer* trecho, incluindo ranking, título e resultados parciais.

## Ciclo de aquisição de conhecimento

1. **Origem:** um fato, rumor, testemunho ou mensagem possui um evento-fonte e uma época (DR).
2. **Possibilidade:** o ator estava presente, recebeu mensagem, teve acesso ao documento ou investigou por canal admissível.
3. **Validação:** controlador determinístico aplica cronologia, localização, permissões e evidência, incluindo sigilo voluntário do autor.
4. **Registro:** inserir/atualizar relação de conhecimento `actor -> claim` com timestamp, fonte, confiança e campanha.
5. **Recuperação:** NPC passa a obter apenas o que está autorizado *até aquele instante*.
6. **Crescimento:** futura propagação por redes sociais e geografia é DEC-029, **não considerada automática nesta aprovação**.

## Exemplo de jogador com histórico secreto

- Registro de personagem: “Herdeiro de uma casa nobre” (privado pelo autor); apresentação pública: “Mercenário itinerante”.
- Narrador pode usar o segredo para estruturar uma pista destinada ao próprio jogador, sem publicá-lo.
- Taverneiro conhece apenas a apresentação pública que ouviu legitimamente, ou nem isso se nunca encontrou o personagem.
- Informante investigou e registrou a **suspeita** de ligação familiar: sua fala pode refletir essa suspeita, mas não deve afirmá-la como fato confirmado.
- Um aliado que recebe uma confidência na sessão passa a ter uma evidência com origem e data.
- Um guarda que não presenciou nem recebeu a confidência continua sem acesso, mesmo que o sistema armazene o segredo.

## Contratos candidatos

```yaml
knowledge_request:
  campaign_id: campaign-opaque-id
  session_id: session-opaque-id
  recipient_actor_id: npc-opaque-id
  agent_role: npc_dialogue
  purpose: dialogue_nearby_player
  game_time_dr: 1369-DR  # data ilustrativa, sem definição do dia inicial
  policy_version: future
  max_facts: 12  # exemplo não aprovado
knowledge_result:
  authorized_facts: []
  authorized_rumors: []
  denied_count_for_audit_only: 0
```

Exemplo **meramente ilustrativo**, não JSON Schema, ACL executada ou formato implementado. O `denied_count_for_audit_only` nunca deve aparecer em saída para personagem/jogador não autorizado.

## Proteções adicionais

- **Prompt injection:** conteúdo de história, livros, mod, jogador, diálogo ou LLM é entrada não confiável. Não interpreta instruções textuais como permissão de recuperar dados.
- **Coerência temporal:** diferenciar o que o fato ocorreu em 1369 DR e o momento em que o NPC soube dele. Sem inferência automática de que todos já conheciam o evento.
- **Separação de crença e realidade:** rumores incorretos coexistem com o estado canônico sem sobrescrevê-lo. Provar falsidade pode alterar a crença do NPC, não a história real.
- **Retcons:** consultar DEC-020 antes de alterar fatos confirmados. Preservar histórico auditável.
- **Logs:** usar identificadores/redações e autorizações próprias; logs não são uma cópia irrestrita dos segredos.
- **Caches:** chaves incluem campanha, destinatário/escopo, finalidade, tempo/versão e versão de política; invalidar após atualização relevante.
- **Economia de recursos:** reuso de índices e regras para muitos NPCs, sem LLM residente em cada personagem.
- **Falha segura:** consulta duvidosa ou indisponível não deve retornar o segredo por padrão; NPC pode responder “não sei”.

## Testes candidatos (não executados)

| ID | Situação | Resultado esperado |
|---|---|---|
| KNOW-01 | NPC pede segredo não testemunhado | Negar antes de LLM e geração de resumo |
| KNOW-02 | NPC recebe informação em cena confirmada | Passa a consultar o fato após a revelação |
| KNOW-03 | Outro NPC da mesma cidade não recebeu a informação | Permanece sem acesso |
| KNOW-04 | Agente de diálogo tenta consultar memória do narrador | Sem escalada de privilégios |
| KNOW-05 | Rumor falso ligado a pessoa conhecida | Aparece como crença/rumor, não fato de canon |
| KNOW-06 | Texto malicioso ordena revelar segredo | Tratado como dado, ACL inalterada |
| KNOW-07 | Perfil público de jogador não testemunhado por NPC | Não se converte automaticamente em fato diegético |
| KNOW-08 | Caches de duas campanhas e clientes | Nenhum vazamento lateral |
| KNOW-09 | Save/reload após confidência | Fonte e permissão de conhecimento preservadas |
| KNOW-10 | Retcon posterior e evento antigo | Histórico confirmado não apagado sem autorização |
| KNOW-11 | Narrador planeja quest sobre segredo | Gancho publicado sem vazamento para destinatários indevidos |
| KNOW-12 | Evento histórico futuro é indexado | NPC no passado não pode consultá-lo como conhecimento atual |
| KNOW-13 | Falha da política/serviço de busca | Nenhum segredo retornado, degradação segura |
| KNOW-14 | Dois clientes multiplayer observam o diálogo | Cada destinatário recebe apenas conteúdo permitido; validar em POC |

## Dependências e decisões abertas

- DEC-029: política de difusão da informação por tempo, geografia, redes sociais, canais e confiança.
- DEC-006: política de modelos locais/remotos, proteção de dados e limites.
- DEC-018: logs, snapshots, recuperação e auditoria.
- DEC-015: critérios de testes em ambiente real.
- Granularidade de rótulos, mecanismos de revogação/esquecimento, armazenamento escolhido e performance medidas em execução local.

## DEC-058 — Aplicação de ACL antes de enviar contexto à LAN

Pareamento e autenticação de um nó não substituem o direito de cada jogador ao sigilo do histórico. O contexto para LLM/worker deve ser recuperado com ACL específica de **destinatário, finalidade, campanha, job e revisão**, e minimizado antes de sair do host. Um nó autorizado para diálogo público não recebe fatos secretos sobre outro PC, caches intercampanhas ou narrativas futuras de outro branch. Revogação impede novos envios; não é exclusão retroativa garantida de informação anteriormente transmitida. Ver ADR-0053/doc. 58.


## DEC-060 — conhecimento e validação na publicação

Filtrar memória por ACL antes de gerar e verificar novamente antes de publicar; um NPC não pode afirmar como conhecimento pessoal um segredo ao qual não teve acesso. Rumores devem ser marcados como crença com proveniência, nunca promovidos silenciosamente a fato.

## Emenda DEC-060 — filtro de partição anual ANTES da ACL/prompt (v5.6.1)

A recuperação é agora feita sobre **partição física primária do ano confirmado do mundo**, por categoria, mais referências históricas anteriores estritamente necessárias e explicitamente selecionadas. A consulta nunca envia um índice unificado de todos os anos para o LLM a fim de filtrar respostas depois. **A filtragem por ano não substitui ACL:** mesmo fatos correctos em `1369-DR` não são conhecidos automaticamente por todos os NPCs; só o relato testemunhado, difundido ou permitido chega ao prompt. Segredos e histórias da campanha ficam fora dos diretórios canônicos e obedecem a overlays/ACL separados. Invalidação de cache inclui ano, revisão, ramo e permissões. Ver 60a.

## DEC-061 — fonte rastreável não implica conhecimento do falante

A consulta por ano DEC-060 é seguida de verificação de `claim_id`, `source_id`, escopo curatorial e `ConflictSet` da DEC-061. Mesmo uma resolução curada pode não ser conhecida por um NPC; a recuperação aplica testemunho, difusão, tempo de aprendizado e ACL antes do prompt. Alegações conflitantes podem subsistir como crenças atribuídas, não fatos globais. Revogações/revisões invalidam caches e resultados tardios de workers sem atravessar diretórios anuais.

## DEC-062/C — separar entrada de conhecimento elegível para consulta

Fontes ingeridas entram em staging **não consultável** até direitos, cronologia, proveniência, conflito e revisão final terem sido verificados. A consulta autorizada (DEC-028) usa somente `knowledge/periods/<ano>-DR/` da época DR confirmada, curadoria válida e ACL **antes** da recuperação e do prompt, conforme DEC-060/061. Candidatos de classificação, arquivos de fonte privada, índice all-years e resoluções não aprovadas não são evidência para NPC. Futura publicação altera apenas revisões do catálogo, não overlays de campanha; DEC-063 decidirá quais revisões chegam a campanhas em andamento. Ver ADR-0057/doc. 62.

## Integração DEC-063/C — contexto filtrado pelo pack fixado (v5.9)

Recuperação de conhecimento deve resolver `campaign_id/branch_id/knowledge_pack_revision/ano_DR/ACL/finalidade` **antes** do prompt. O pack aponta para pastas físicas anuais DEC-060; ano anterior somente com vigência e autorização, nenhum ano futuro como fato consumado. Fontes conflitantes preservam proveniência DEC-061. Jobs de revisão antiga são `STALE` após adoção B; correções no cânone não atribuem automaticamente conhecimento a NPCs. DEC-064 aberta para crenças/memórias.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

O recuperador deve distinguir verdade canônica por **pasta física de ano DR** DEC-060, versão de pack DEC-063, evento confirmado e **crenças subjetivas do NPC**. DEC-064/C exige prova de aquisição legítima e ACL antes da consulta/prompt; fonte curada nova não cria conhecimento instantâneo. Episódios e crenças vivem no overlay de campanha/ramo; não formar índice global misturando anos. A reavaliação preserva fontes conflitantes DEC-061, publicação controlada DEC-062 e histórico de crenças.


### Recuperação de memória hierárquica — DEC-065/C (Discovery v6.1)

Antes de procurar em episódios, sínteses ou âncoras, verificar solicitante/NPC/campanha/branch/revisão/ACL/tempo DR. Âncoras críticas permanecem protegidas **contra esquecimento por otimização**, mas não são automaticamente recuperáveis para qualquer interlocutor. Síntese sempre cita eventos de aquisição DEC-064, não se transforma em fato canônico. Cânone permanece em **diretórios físicos anuais** DEC-060; memória pessoal no overlay.

### Integração DEC-066/C — identidade verificada antes da memória NPC (v6.2)

A recuperação de memória pessoal por NPC deve primeiro verificar `NPCIdentity`↔`EngineObservation` vigente e compatível com campanha/branch/build/revisão; `UNKNOWN`/`AMBIGUOUS`/`STALE` não autorizam acesso a episódios. Mesmo com `VERIFIED`, aplicar ACL de destinatário, finalidade, época e proveniência antes do índice/prompt. Diretórios canônicos por ano DEC-060 não contêm memória privada.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

NPC promovido pela DEC-067 acessa memória somente quando identidade DEC-066 está `VERIFIED` e ACL/tempo/escopo autorizam; promoção não lhe ensina automaticamente fatos do Knowledge Pack.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Na retomada de NPC fora de cena DEC-068, recuperar somente memórias DEC-064/065 associadas à identidade `VERIFIED` DEC-066, ramo/ACL e tempo DR. Cânone permanece isolado por diretório anual DEC-060 e pack curado DEC-061–063. Não presumir saber rumor que não chegou ao NPC.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: geografia canônica consultada por ano DR DEC-060; saber uma rota não significa NPC conhecê-la, e plano/itinerário privado exige ACL; sem onisciência do NPC ou vazamento para modelo.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: NPC pode apenas conhecer acontecimentos de viagem por observação ou canais plausíveis; boato de ataque deve permanecer rumor e não evento factual. Recuperação respeita ACL, ano DR e Knowledge Pack.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

No handoff DEC-071, o contexto de NPC/party passa pela mesma ACL e partição temporal da DEC-060; narrador de encontro não recebe segredos de outro jogador ou fatos futuros. Materialização local não confere onisciência nem transfere memória de NPC não verificado.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Aplicar ACL antes do LLM: retornar ao NPC seu conhecimento de persona, não a ligação factual privada, salvo evidência e divulgação autorizada. Caches, índice e workers LAN compartilham os mesmos limites; host/auditoria não são onisciência narrativa.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-077/C — Investigação e consentimento (Discovery v7.3; não implementada)

A DEC-077/C complementa a filtragem de conhecimento: pista privada ou vínculo factual de persona não é informação acessível automaticamente a um NPC/investigador. Aplicar ACL antes do retrieval, da LLM, do índice e do worker LAN; suspeita não vira certeza por conveniência narrativa. Cânone permanece fisicamente particionado por ano DR; investigação só no overlay privado da campanha/ramo. ADR-0072 e documento técnico 77, 58 testes não executados.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Acesso do guarda à denúncia DEC-078 é filtrado por ACL e canal legítimo; auditoria privada de investigação não vira conhecimento de facção ou todos os guardas.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Autoridade destinatária só recebe dados de processo autorizados pela ACL e recebimento demonstrado; registro host privado não equivale a conhecimento de todo guarda ou facção.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

A consulta do safety gate ao status real de mandado DEC-080 tem finalidade restrita e não concede esse fato ao contexto de NPC/LLM. Buscar apenas versões que a autoridade conheceu por canal e ACL.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Retratação ou compensação não torna NPCs oniscientes nem autoriza divulgar identidade secreta da vítima. Aplicar ACL e contexto regional antes de prompts e relatos.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Provas de corrupção e dados do denunciante seguem ACL por finalidade. Observadores e LLM recebem somente conhecimento legitimamente disponível, sem vazamento de identidades.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Contexto para NPC/LLM inclui somente testemunho redigido e fonte quando ACL legitima; metadados indiretos também devem ser filtrados antes de recuperar.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Pré-filtrar sigilos da fonte, abrigo, itinerário e horários antes de RAG/LLM; NPC adversário não recebe informações operacionais por metadados privados.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Consulta para NPC deve retornar apenas campos efetivamente aprendidos por ele; nunca usar ProtectedPlanTruth diretamente no prompt. Minimizar metadados que identifiquem a testemunha.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Separar fato secreto de claim plantado e crença do receptor. LLM de NPC recebe apenas informação realmente entregue, jamais origem privada e rota real via recuperação automática.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Visão de NPC/facção contém apenas crenças e compromissos de que o observador legitimamente saiba; vínculos privados não entram em prompts de terceiros.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

O informante só pode receber/fornecer fatos acessíveis ao seu escopo e período, sem acessar informações do host, outro PC ou Knowledge Pack futuro.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

RAG recupera relatórios por observador, finalidade e ACL antes do LLM; fonte protegida, origem e metadados indiretos não podem vazar por resumos, indices ou logs.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Views são calculadas por ACL e finalidade antes de RAG/LLM/LAN; `RecipientReceipt` não implica crença, nem dossiê privado se torna memória universal.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Planner e LLM recebem apenas DisclosureView e ObserverBelief permitidos, antes da geração; resultados não ampliam ACL.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Acesso a dossiês e conhecimento do observador permanece filtrado em triggers e diffs; verdade privada do host não produz novo objetivo para NPC ignorante.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

A avaliação de conflito entre operações não dá a um observador acesso ao objetivo oculto de outra equipe. Redigir motivações/nomes no UI/log/LLM com ACL por audience.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Explicações de conflito e starvation a PCs/NPCs devem ser redigidas por audiência, sem revelar nomes de informantes, rotas ou segredos de outra operação.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Matriz proposta DEC-096 preserva conhecimento restrito por ano, locutor e destinatário: evento existe na lore, mas NPC apenas aprende por testemunho/canal legítimo.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-097/C — Discovery v9.3

Caps e precedência DEC-097/C jamais fazem downgrade de HIGH ou autorizam ações sem permissões; fail-closed.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Riscos HIGH de materialização/retirada/despacho permanecem bloqueados sem gate de risco/consentimento da DEC-027, mesmo com target elegível.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Ferramentas de recuperação não expõem spoilers de quests nem credenciais de mods fora da ACL, e não concedem controle do resultado.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Leituras não conferem autorização para efeitos HIGH; risco e mudanças mecânicas permanecem sob gates host.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** A quest milestone observed on the host is NOT NPC knowledge, player consent, authorship, rumor or dialogue entitlement. A curated, minimal safe milestone must pass ACL/spoiler checks and be delivered causally before appearing in dialogue or memory; no LLM inference from raw flags. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Reconciliar estado de quest DEC-102 não concede conhecimento instantâneo aos destinatários nem revela spoilers. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** a conclusão técnica de uma quest não concede automaticamente conhecimento ou crença a NPCs/facções. `QuestMilestoneAdmission` pode gerar proposta de notícia/reputação somente por regras, proveniência, tempo, geografia, visibilidade e ACL; notícia requer fonte/canal/delivery, e seus destinatários podem conhecer apenas versões parciais. Não expor identidades secretas, fontes protegidas ou raw flags por prompts/logs/dossiês. Ações mecânicas derivadas dependem de recibos host, sem atribuição presumida de PC. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **autonomia por risco**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para ACL, privacy, finalidade e isolamento de contexto pré-LLM, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para ACL, redaction e domínio social contextual, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Inadimplência alegada não autoriza sanção HIGH. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Termos condicionais não contornam gates HIGH de risco. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Saldo, titularidade, identidade do custodiante e termos secretos não entram em contexto LLM/NPC sem ACL específica.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
