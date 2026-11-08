# DEC-054 — Política de backups versionados, retenção e restauração testada

**Discovery v5.0.** Documento de projeto candidato, associado ao ADR-0049. **Nenhum componente foi implementado ou ensaiado no BG2:EE**. Nenhuma cadência, limite, chave de criptografia ou destino externo foi contratado/definido.

## 1. Objetivos e premissas

Preservar uma campanha persistente em face de falha de SSD, erro humano, corrupção, restauração de save antigo, atualização de mods e perda parcial de logs. DEC-053 fornece o **checkpoint coordenado elegível**; DEC-054 define sua preservação e capacidade de restauração ao longo do tempo. Backup não equivale a checkpoint: (a) checkpoint = par logicamente consistente; (b) backup = cópia retida e verificável desse par, capaz de ser recuperada em ambiente suportado.

Invariantes:

1. **Nunca misturar** save de uma revisão com snapshot/log de outra, mesmo quando ambos tiverem timestamp próximo.
2. **Não criar um backup declarado válido** sem confirmar que a origem era `PUBLISHED`/verificada, seus artefatos estão presentes e seus hashes coincidem.
3. **Não apagar a única cópia recuperável**. Versões pinadas e dependências de event log devem estar protegidas contra coleta automática.
4. **Nenhum upload externo implícito**; remoto criptografado e autorizado.
5. **Não restaurar sobre o jogo ativo para testar**: operação de ensaio isolada, com cópias e trilha de evidências.
6. **Sem alegar recuperação** quando houver apenas checksum, mas save impossível de carregar ou história incoerente.

## 2. Arquitetura funcional candidata

```text
Checkpoint Coordinator (DEC-053)
  └── published pair + manifest + immutable IDs
         ↓
Backup Planner [cadência/política; não gera save no motor]
         ↓
Backup Packager [cópia consistente, catálogo, hashes]
         ↓
Backup Verifier [completude, integridade, escopo e dependências]
         ↓
Retention Catalog [versões, referências, pins, quotas]
         ├── Destination LOCAL (padrão, se disponível)
         └── Destination INDEPENDENT (opt-in: externo/NAS/remoto cifrado)
         ↓
Restore Drill Runner [cópia isolada, build vinculada, testes]
         ↓
Restore Report / Alerts [sem divulgar segredos, sem autodeclaração de sucesso]
```

**Operação remota não é obrigatória.** Copiar para diretório do mesmo volume não garante resistência à falha física do dispositivo; a interface deve distingui-los. As escolhas de serviço, arquitetura e tecnologia permanecem para SPECS.

## 3. Dados de backup: contrato lógico candidato

| Campo lógico | Finalidade e restrições |
|---|---|
| `backup_set_id` | Identificador único do conjunto; não é ID de save da engine |
| `checkpoint_id` | Referência a checkpoint `PUBLISHED` verificado, sem modificar o snapshot original |
| `campaign_id`, `mode`, `branch_id`, `epoch` | Impedir mistura entre campanhas, Original/Living World e histórias alternativas |
| `build_id`, `mod_manifest_digest` | Associar motor, versão, ordem dos mods e conteúdo compatível |
| `save_digest`, `narrative_snapshot_digest`, `log_watermark` | Comprovar associação entre partes e revisão histórica, sem publicar segredos |
| `artifact_manifest`, `dependency_graph` | Quais arquivos/segmentos/instaladores necessários para recuperar; evitar backup diferencial órfão |
| `created_at`, `verified_at`, `restore_drill_at` | Evidência distinta de captura, integridade e teste real de recuperação |
| `destination_id`, `independent_fault_domain` | Indicar local, mídia, volume e independência observada; sem expor caminhos privados a todos |
| `retention_class`, `pin_reason`, `expires_at` | Rotação e exceções por checkpoint histórico ou pré-migração |
| `encryption_key_ref`, `access_policy_revision` | Identificação segura da chave, sem armazenar segredo ou senha no manifesto compartilhado |
| `status`, `failure_reason`, `evidence_refs` | Histórico auditável, sem afirmar sucesso antes das provas |

As estruturas acima **não são schema definitivo**; hashes, formatos, repositório e deduplicação exigem SPEC e validação.

## 4. Cadência, gatilhos e retenção candidatos

- **Gatilhos propostos:** após novo checkpoint certificado, encerramento de sessão, antes de migração (DEC-052), antes de mudança de política com impacto e a pedido do anfitrião. Se o motor não fornecer captura segura, aguardar um checkpoint validado disponível, sem inventar sincronização.
- **Perfis futuros:** econômico (poucas gerações locais), equilibrado (mais pontos de retorno, cópia externa opcional) e protegido (redundância, testes frequentes e pins). Não fixar prazos nem números antes de medir tamanho/velocidade e necessidades do grupo.
- **Retenção em camadas:** versões recentes + marcos selecionados + proteção pré-migração + ao menos último ponto recuperável. Em caso de backup diferencial, dependências anteriores precisam existir.
- **Pressão de disco:** medir espaço livre e informar degradação; suspender novos backups quando necessário; jamais limpar acidentalmente a última versão válida ou o rollback da build anterior.
- **Política de exclusão:** avaliar pins, integridade dos sobreviventes, referências de log, permissões e estado de restauração. Remoções irreversíveis seguem regras autorizadas.
- **RPO/RTO:** metas são parâmetros futuros por perfil de campanha; não prometer tempo nem perda máxima sem testes.

## 5. Redundância e privacidade

1. Destino local é o ponto de partida. Um **segundo destino independente** (volume/dispositivo distinto, NAS ou armazenamento remoto) reduz certos riscos, mas precisa de ativação e autorização explícitas.
2. Nuvem/serviços pagos não são exigência. Cópias remotas devem ser criptografadas, com verificação de segurança e credenciais antes de transmitir. O armazenamento pode estar sujeito a termos/licenças e leis aplicáveis; não embutir arquivos proprietários do jogo/mods em pacotes distribuídos.
3. Backups podem conter informações privadas sobre PCs/NPCs e segredos. O catálogo público de status deve expor apenas contagens/estado autorizado. Logs completos, manifestos e arquivos exigem ACL (DEC-028).
4. Não presumir que senha recuperável por suporte externo exista. **Perda da chave pode inviabilizar todos os backups cifrados**; testar processo de recuperação de chave e alertar sobre esse risco na configuração.
5. Onde suportado, considerar retenção de versões protegidas contra sobrescrita e exclusão (por exemplo, mídia desconectada ou snapshots imutáveis). Isso é defesa opcional, não propriedade universal.

## 6. Pipeline de cópia e publicação (lógico, não implementado)

1. Selecionar `checkpoint_id` verificado e `build_id` exato; congelar a referência para a operação.
2. Listar artefatos e dependências do snapshot/event log; assegurar que são legíveis e que a origem permanece coerente.
3. Copiar para local temporário do destino; gerar catálogo e hashes, sem substituir backup anterior válido.
4. Validar integridade, identidade, completude da cadeia e acesso ao destino. Falha produz backup não publicado e alerta.
5. Publicar conjunto versionado e metadados; marcar nível efetivo de proteção local/independente.
6. Efetuar segunda cópia quando configurada e acessível; falha externa não converte cópia local em redundante.
7. Aplicar rotação só após avaliação de referências/pins e preservação do conjunto mínimo recuperável.
8. Agendar/propor ensaio isolado e armazenar evidências em `RestoreReport`.

## 7. Restauração de ensaio e restauração real

**Ensaio:** copiar conjunto para diretório isolado, reconstruir dependências, validar chaves/manifesto, restaurar banco em cópia e verificar integridade de conhecimento/ramo. Quando houver ambiente de POC, restaurar save na **build exata** e testar carregamento, save/reload, quests, NPCs e consistência do host com dois clientes. A falha de qualquer gate crítico deve resultar em **restauração não verificada**, não em sucesso parcial anunciado como sucesso total.

**Restauração real:** anfitrião escolhe ponto válido, entende que isso pode retroceder progresso e autoriza a operação. Preservar cópia da situação atual quando possível. Usar `checkpoint_id` correspondente, reconciliar `UNCERTAIN`, isolar branch/epoch quando necessário, verificar versão e direitos de acesso; nenhuma reexecução automática de mutações irreversíveis. Caso os pré-requisitos falhem, bloquear e explicar o motivo.

**Estados candidatos distintos:** `COPYING`, `INTEGRITY_VERIFIED`, `LOCAL_ONLY`, `REDUNDANT`, `DEGRADED`, `RESTORE_UNTESTED`, `RESTORE_VERIFIED`, `FAILED`, `QUARANTINED`. Estes não são estados nativos de BG2:EE; status de cópia não deve ser confundido com recuperabilidade funcional.

## 8. Riscos e respostas operacionais

| Falha | Detecção/conduta |
|---|---|
| Disco principal falha | Recuperar segunda cópia **se configurada e íntegra**; não assumir redundância local |
| Backup interrompido | Marcar parcial e conservar backup anterior |
| Corrupção silenciosa | Hash/catálogo e ensaios regulares de leitura |
| Data store íntegro mas save inválido | Ensaio funcional identifica; bloquear restauração para produção |
| Exclusão por política de espaço | Rejeitar coleta da última cópia íntegra e conjuntos pinados |
| Ransomware/overwrite | Permissões mínimas; cópia independente, offline ou imutável onde possível |
| Chave criptográfica perdida | Informar impossibilidade de descriptografar; testar custódia autorizada |
| Backup de build diferente | Exigir mesmo build ou migração controlada DEC-052 |
| Vazamento de histórico secreto | ACL, criptografia, minimização de metadados e logs de acesso |
| Save antigo após retorno | Isolamento de ramos DEC-053; sem conhecimento do futuro |
| Restore parcial | Bloquear; não declarar recuperação mesmo que uma metade pareça correta |

## 9. Vinte e oito testes candidatos (NÃO executados)

| ID | Cenário | Resultado esperado |
|---|---|---|
| T-054-01 | Backup de checkpoint publicado e íntegro | Conjunto com save, snapshot/log e manifest completo |
| T-054-02 | Candidato apenas PREPARING | Não aceitar como origem elegível |
| T-054-03 | Somente save mecânico disponível | Não declarar backup recuperável |
| T-054-04 | Somente snapshot narrativo disponível | Não declarar backup recuperável |
| T-054-05 | Interrupção durante cópia | Backup parcial não publicado; anterior preservado |
| T-054-06 | Arquivo alterado depois da cópia | Validação de integridade detecta divergência |
| T-054-07 | Recuperação de cadeia event log incompleta | Bloquear elegibilidade e indicar dependência |
| T-054-08 | Pares de builds diferentes no destino | Bloquear cruzamento de versões |
| T-054-09 | Pares Original e Living World misturados | Bloquear e manter isolamento |
| T-054-10 | Ramo antigo + log futuro | Recuperar apenas revisão do ramo autorizado |
| T-054-11 | Configuração sem armazenamento externo | Backup local permitido, risco de falha de dispositivo explícito |
| T-054-12 | Ativar segunda cópia em disco externo | Exigir autorização e indicar independência real |
| T-054-13 | Destino NAS desconectado | Alerta e estado DEGRADED, sem sucesso falso |
| T-054-14 | Tentativa de upload remoto sem adesão | Proibir qualquer transferência |
| T-054-15 | Cópia remota com criptografia configurada | Não transmitir segredos em claro |
| T-054-16 | Chave de criptografia perdida/incorreta | Recuperação falha explicitamente sem tentativa de contorno |
| T-054-17 | Limpeza atinge última cópia recuperável | Bloquear exclusão |
| T-054-18 | Rotação alcança versão pinada pré-migração | Preservar cópia até liberação válida |
| T-054-19 | Armazenamento sem espaço durante backup | Falhar fechado, preservar último conjunto válido |
| T-054-20 | Restauração de teste em diretório isolado | Não alterar campanha ativa |
| T-054-21 | Hashes válidos mas save não progride em quest | Não declarar recuperação funcional aprovada |
| T-054-22 | Ensaio multiplayer host + dois clientes | Validar sincronização antes de anunciar sucesso |
| T-054-23 | Backup restaurado com ação UNCERTAIN | Sem replay de recompensa/morte até reconciliação |
| T-054-24 | Restaurar versão anterior da build A após falha B | Par coerente A e manifest A; nenhuma alteração em dados ativos |
| T-054-25 | Usuário sem permissão tenta abrir segredos em backup | Negar e registrar apenas metadados autorizados |
| T-054-26 | Operador tenta restaurar outra campanha | Bloquear escopo campaign_id e owner |
| T-054-27 | Backup local corrompido, cópia independente íntegra | Permitir ensaio a partir da segunda cópia verificada |
| T-054-28 | Teste de restore vencido ou nunca realizado | Indicador de recuperabilidade não verificada e alerta apropriado |

## 10. Gates de validação e critérios de bloqueio

- **G1:** captura real de checkpoint em BG2:EE demonstrada sem prometer API/atomicidade inexistente.
- **G2:** backup preserva vínculo de save/snapshot/watermark, integridade e políticas por modo/ramo.
- **G3:** falha entre cópias não apaga backup anterior e estado degradado fica visível.
- **G4:** retenção segura com quota, pins e proteção da última cópia restaurável.
- **G5:** controle de acesso e criptografia de cópia remota; ativação explícita.
- **G6:** restauração de ensaio em ambiente isolado; host + dois clientes, save/load e progressão quando houver integração.
- **G7:** backup pré-migração e prova de rollback entre builds sem cruzar estados.

**No-go:** tentativa de restaurar checkpoint parcial, ausência de chave necessária, manifesto/cadeia incompleta, build incorreta, ACL insuficiente, backup único prestes a ser apagado, `UNCERTAIN` impeditivo, save funcionalmente corrompido ou ensaio que ameaça campanha ativa.

## 11. Integração e próximas decisões

- DEC-053: fonte do par certificado; DEC-052: antes/depois de migração; DEC-028: ACL/segredos; DEC-018: operação, logs, observabilidade e resposta a incidentes ainda em aberto; DEC-015: critérios de aceitação gerais.
- DEC-013: versões exatas/compatibilidade; DEC-006: políticas de IA local e eventual consentimento para chamadas externas **não autorizam upload de backups**.
- **DEC-055 proposta:** política de observabilidade, alertas e resposta segura a incidentes em serviços, saves, gateway, sincronização e backups; definir quanto o sistema pode automatizar sem assumir decisões do anfitrião.

## Integração posterior — DEC-055 (Discovery v5.1)

Falhas de destino, espaço, integridade, expiração do último teste de restauração e ausência de cópia independente configurada são observadas pelo World Health Monitor. O monitor alerta e permite apenas ações LOW idempotentes, mas não exclui automaticamente backups protegidos, não promove backup incompleto e não executa restore em produção sem autorização. Ver ADR-0050/doc. 55.

## Integração DEC-063/C — retenção dos manifestos históricos (v5.9)

Backups e restaurações devem preservar a revisão/manifesto de *knowledge pack* de cada campanha/ramo e todos os hashes/arquivos de partições anuais ainda referenciados pelos checkpoints. Não excluir um pack antigo enquanto restauração autorizada precisar dele. Retenção de material protegido segue direitos/ACL; não colocar fontes integrais ou saves privados no pacote Discovery. Rollback editorial não apaga eventos do jogo confirmados após adoção de revisão nova; exige análise causal, último checkpoint verificado e consentimento apropriado.

## Integração DEC-064/C — aprendizado e crenças sem onisciência (v6.0)

Backups candidatos DEC-064/C devem permitir recuperar sequência de aquisição e revisão de crenças no contexto correto, com ACL e minimização de segredos. Proteção de dados e licenças evita cópia de diálogos privados em logs. Estratégia quantitativa de retenção/consolidação e esquecimento será decidida na DEC-065; não apagar eventos críticos prematuramente.


### Política de memória e backups — DEC-065/C (Discovery v6.1)

Preservar âncoras/episódios necessários à continuidade em backups **coerentes com seu checkpoint**, mas não inferir retenção ilimitada nem impedir requisições legítimas de exclusão. Restauração precisa evitar ressuscitar segredo revogado, índice stale ou projeção de outro ramo; mecanismos de expurgo nos backups exigem SPECS/ensaios. Consolidação não constitui um backup nem substitui ledger.

### Integração DEC-066/C — restore e auditoria de vínculos de identidade (v6.2)

Ensaiar restauração do estado narrativo de identidades junto aos checkpoints válidos; o backup conserva evidências e revisões suficientes para invalidar relações pós-checkpoint. Não aceitar bindings de build diferente ou de ramo irmão. Redação/privacidade de registros de prova segue políticas existentes; testes de restore in-game continuam pendentes.

## Integração DEC-067/C — individualização progressiva de NPCs (Discovery v6.3)

Ensaios de restore para DEC-067 devem conferir identidades, episódios críticos, contagem agregada, pendências de promoção e branches; não tratar memória persistente como cache descartável.

## Integração DEC-068/C — ciclo de vida offscreen (Discovery v6.4)

Backups DEC-068 preservam NPCIdentity, memórias, checkpoints e jobs/versionamento relevantes, observando retenção e privacidade. Restaurar campanha anterior não injeta eventos que ocorreram após esse checkpoint. Testar restore + DORMANT→ACTIVE futuramente.

## Integração com DEC-069/C — Discovery v6.5

DEC-069: backups retêm itinerários, versões e evidências de observação, respeitando ACL. Restaurar snapshot antigo não reaplica chegada, evento ou spawn de período futuro.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070: recuperação de backup invalida incidentes futuros por epoch/branch, preserva trilha auditável e bloqueia replay de alterações mecânicas cujo resultado é UNCERTAIN.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Em ensaios de restauração, verificar que ledger de DEC-071 e estado host/branch voltam à mesma época; operações cuja confirmação é incerta permanecem bloqueadas. Não reincorporar efeitos de encontros futuros de outro snapshot.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Ensaios de restore DEC-054 para DEC-072 devem incluir catálogo/revisões, dependências de mods, receipts e efeitos confirmados sem restaurar assets incompatíveis ou duplicar encontro.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Restore deve preservar apenas os efeitos de encounter/cleanup do ramo e checkpoint efetivamente restaurados; não reutilizar operação destrutiva do futuro.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.


### Integração DEC-074/C — Discovery v7.0 (aprovada, não implementada)

Restauração de branch não reexecuta rumores/effects do futuro; ledger de notícias e impactos DEC-074 acompanha snapshot consistente e retenção/ACL. Veja ADR-0069 e documento técnico 74; **52 testes candidatos NÃO EXECUTADOS**. DEC-060–073 preservadas.

### Integração DEC-075/C — Discovery v7.1 (arquitetura aprovada, NÃO implementada)

Backups devem preservar o encadeamento evento→evidência→atribuição→relato→efeito e suas ACL, sem recompensas duplicadas na restauração.

**Referências:** ADR-0070 e documento técnico 75; DEC-060–074 preservadas, cânone particionado fisicamente por ano DR, resultados no overlay privado. **54 testes T075-* candidatos NÃO EXECUTADOS.**

## Integração da DEC-076/C — personas, pseudônimos e reconhecimento (Discovery v7.2)

Backup/restore inclui ledger privado de personas com controles de acesso equivalentes; restaurar época anterior não divulga identidades descobertas mais tarde. Retenção não equivale à publicação de segredos.

**Estado:** arquitetura candidata aprovada, sem código ou POCs BG2:EE/EEex multiplayer. DEC-060–075 preservadas; não alterar ADRs históricos.

### Integração DEC-078/C — justiça contextual e consequências seguras (Discovery v7.4)

Backup e restore exigem coerência entre caso DEC-078, policy revision, recibos do host e estado da campanha; nunca herdar condenação de futuro restaurado.

**Referências:** ADR-0073 e documento técnico 78; DEC-060–077 preservadas, sem implementação de engine. **60 testes T078-* candidatos NÃO EXECUTADOS.**

### Integração DEC-079/C — cooperação interjurisdicional (Discovery v7.5)

Em restore, mensagens e decisões interjurisdicionais DEC-079 de futuro abandonado ficam STALE. Backups não revertem punição mecânica sem comprovação e consentimento.

**Referências:** `docs/decisions/ADR-0074-cooperacao-interjurisdicional-reconhecimento-contextual-e-mandados.md` e `docs/79-mandados-interjurisdicionais-transmissao-reconhecimento-e-conflitos-de-autoridade.md`; DEC-060–078 preservadas; **62 testes candidatos NÃO EXECUTADOS**, sem capability BG2:EE/EEex/multiplayer comprovada.


## Integração DEC-080/C — Discovery v7.6 (aprovada, não implementada)

Backups DEC-080 preservam ledger imutável de ordens, tombstones e conhecimento local no ramo adequado; restaurar não reativa mandados por mensagens atrasadas.

**Referências:** ADR-0075 e documento técnico 80; **64 testes candidatos NÃO EXECUTADOS**. DEC-060–079 e ADRs anteriores preservados.

## Integração DEC-081/C — Reparação contextual (Discovery v7.7)

Ensaiar restore com dano confirmado, pedido pendente e compensação parcialmente executada; evitar ressurgimento de restituição de outro branch ou perda de histórico.

**Referências:** `docs/decisions/ADR-0076-reparacao-contextual-proporcional-e-rastreavel-apos-injusticas.md` e `docs/81-revisao-de-injusticas-restituicao-reabilitacao-e-reparacao-causal.md`; **66 testes candidatos NÃO EXECUTADOS**; DEC-060–080 e ADRs anteriores preservados.

## Integração DEC-082/C — responsabilização institucional (Discovery v7.8)

Preservar prova, versões de processo, decisões e receipts em backup; restore isola branch e não reexecuta penalidades já aplicadas.

**Referências:** ADR-0077/documento técnico 82; **68 testes candidatos NÃO EXECUTADOS**. DEC-060–081 e seus ADRs preservados; nenhuma integração BG2:EE/EEex/multiplayer comprovada.

## Integração DEC-083/C — proteção de fontes e divulgação proporcional (Discovery v7.9)

Backups preservam dados e políticas de fontes com a mesma proteção; restaurar não importa audiência ou revelação de branch posterior.

**Referências:** ADR-0078/documento 83; **70 testes T083-* candidatos NÃO EXECUTADOS**. DEC-060–082 e ADRs anteriores preservados; nenhuma capacidade BG2:EE/EEex/multiplayer de proteção implementada.

## Integração DEC-084/C — Discovery v8.0

Backup do caso preserva evidências e versões de planos protegidos por ACL; restore não importa perseguição ou abrigo do futuro abandonado.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**


## Integração DEC-085/C — Discovery v8.1 (aprovada, NÃO implementada)

Backup mantém proteção de segredos e grants; restore não revela refúgio por rollback de ACL, e provas antigas permanecem auditáveis.

**Referências:** ADR-0080, documento técnico 85. DEC-060–084 preservadas, corpus físico por ano DR intacto, planos só em overlay privado. **74 testes candidatos T085-* NÃO EXECUTADOS**.

## Integração da DEC-086/C — iscas e desinformação rastreável (Discovery v8.2)

Restaurar operação de isca exige reconstituir ACL de plano verdadeiro, reservas e disseminação idempotente. Backup não concede publicidade da identidade da fonte.

**Estado:** arquitetura aprovada, sem prova de funcionalidade BG2:EE/EEex multiplayer; 76 testes T086-* candidatos NÃO EXECUTADOS. DEC-060–085/ADRs prévios integralmente preservados.

## Integração da DEC-087/C — lealdades dinâmicas e agentes duplos (Discovery v8.3)

Backups incluem compromissos secretos do overlay com ACL equivalente, sem importar revisões posteriores a um checkpoint anterior.

**Estado:** arquitetura aprovada, sem integração BG2:EE/EEex/multiplayer comprovada; preservar DEC-060–086 e todos os ADRs anteriores.

## Integração da DEC-088/C — recrutamento voluntário e acordos de informantes (Discovery v8.4)

Backups de overlay protegido devem conservar acordos/ACL sem divulgar fontes; restore deve reconciliar pagamentos e não importar contratos futuros.

**Estado:** decisão arquitetural aprovada, não implementada; sem testes BG2:EE/EEex. DEC-060–087 e ADRs prévios preservados.

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Backup de overlay de inteligência contém ACL e origem protegidas; restauração deve testar impossibilidade de vazamento entre ramos e versões.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-090/C — Discovery v8.6

Backup de dossiê confidencial exige controles de acesso equivalentes, criptografia quando aplicável e teste de restore de versões/recibos, evitando acesso por cópia administrativa.

**Status:** documentação de arquitetura DEC-090/C, sem implementação ou POC; DEC-060–089 e ADRs anteriores preservados. O documento 90 lista 86 testes não executados.

## Integração DEC-091/C — Discovery v8.7

Backup inclui revisões e ledgers de plano, respeitando ACL; restaurar não implica repetir ação já confirmada.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Backup/restore deve contemplar operações e suas revisões sem misturar branch, futuro ou segredos de outro checkpoint; ensaios necessários.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração da DEC-093/C — simultaneidade, recursos e arbitragem (Discovery v8.9)

Ensaios de restore devem cobrir reservas órfãs, fence antigo, consumo confirmado e ações UNCERTAIN; back-up não cria atomicidade host↔scheduler.

**Estado:** decisão arquitetural somente; sem API/scheduler/POC BG2:EE validada. ADRs históricos inalterados, DEC-060–092 preservadas.

## Integração DEC-094/C (Discovery v9.0)

Ensaio de restauração deverá validar invariantes de leases, epoch, deadlock e idempotência sem desfazer ações BG2:EE já confirmadas.

**Estado:** arquitetura aprovada, ainda sem SPECS/POCs ou implementação BG2:EE/EEex; decisões anteriores e ADRs preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Tests de restore devem garantir que Saga compensada não duplique moedas/itens e que ImpactRule DEC-096 não reaplique efeito histórico em reabertura de save.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

Restauração DEC-096/C exige reconciliação de state/ledger, pins e versão de regras; cenários canônicos antigos são baseline e não reencenação.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-097/C — Discovery v9.3

Backup/restauração DEC-097/C preserva policy revision e valores host-confirmed; cache não é fonte de verdade.

**Referência:** ADR-0092 e doc 97; somente arquitetura aprovada. **102 testes candidatos T097-* NÃO EXECUTADOS**; casos unitários sintéticos não comprovam engine. DEC-060–096 e ADRs anteriores preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

Backup/restore não autoriza reaplicar spawn e efeitos. Diffs posteriores ao restore devem comparar ramo, checkpoint e receipt compatíveis.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Backups e restaurações preservam ownership e comprovantes, e invalidam writes contra build/epoch divergente.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Backup e recuperação precisam preservar audit log mínimo sem copiar flags privadas para relatórios.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

## Integração DEC-101/C — Discovery v9.7

**Contrato transversal:** Catalogues by exact build/modpack/quest/script fingerprint, curated proof of semantic milestone and valid transition; an observed flag or stage is never an authorized quest write or host receipt. On patch or restore, invalidate semantic cache and avoid generic stage inference. Referências normativas: ADR-0096, documento técnico 101 e DEC-100 (probes somente-leitura). Mapeamento curado por build/modpack/script e prova de transição são obrigatórios; resultados incertos permanecem sem efeitos. **T101-001..128: candidatos NÃO EXECUTADOS**; nenhuma POC EEex/BG2:EE foi demonstrada.


### Integração DEC-102/C (Discovery v9.8)

Restore DEC-102 exige trilha de evidências, branch e checkpoint; arquivos históricos imutáveis. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **recovery**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para restauração de backup preserva histórico de entregas por linhagem, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para save restaurado mantém ramo e histórico separado, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
