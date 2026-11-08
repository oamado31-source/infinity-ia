# Jornadas de redenção, juramentos e transformação pessoal

**Discovery v3.4** | **Modelo técnico preliminar, não SPEC final** | **DEC-038 aprovada (opção B)**

## Propósito

Transformar a evolução ética/moral em oportunidades de narrativa **opt-in**, apoiadas por histórico do personagem, facções, deuses e instituições de Forgotten Realms, com limites claros entre trama, regras e mutações físicas.

## Responsabilidades por camada

| Camada | Entrada | Saída permitida | Proibido presumir |
|---|---|---|---|
| Alinhamento contextual (DEC-036) | Ações confirmadas, contexto e autor | Tendência/estado narrativo e justificativa | Escrever atributo do engine ou dar perdão automático |
| Personal Arc Planner (candidato) | Histórico autorizado, vínculos, contexto temporal e objetivos | Proposta de jornada e marcos opt-in | Inventar cânone, forçar escolha moral ou classe |
| Lore/Knowledge Guard (DEC-009/028) | História oficial, data, região, segredos | Validação do conteúdo que NPC pode conhecer | Vazamento de segredo/contaminação de canon |
| Quest State/World Memory (DEC-008/025) | Aceite, metas, evidências e eventos | Estado persistente, eventos e projeções | Declarar ação mecânica não executada |
| Risk/Action Gateway (DEC-027/034/012) | Proposta de impacto e permissões | Permissão, rejeição ou pendência de autorização | Executar código livre da IA |
| BG2:EE host/bridge (DEC-011/037) | Operação tipada tecnicamente suportada | Resultado mecânico confirmável | Garantir suporte EEex, multiplayer ou *fallen* sem POC |

## Invariantes de design

- **Jornada ≠ absolvição:** conclusão narrativa não apaga danos, dívidas ou reputação adversa; reparação exige acontecimentos efetivos, e NPCs/facções podem continuar desconfiando.
- **Escolha informada e livre:** o jogador pode aceitar, rejeitar ou interromper o arco. Não há obrigação de trocar fé, classe ou alinhamento.
- **Eixos separados:** alinhamento, fé, voto/juramento, acesso a poderes, relações e reputação não são um único valor.
- **Versão da campanha:** registrar perfil de regras, fontes de lore, escolha de classes/kits e versão dos módulos; mudança de módulos não reinterpreta saves existentes sem migração aprovada.
- **Original isolado:** conteúdo personalizado do Living World não ativa flags nas campanhas clássicas.
- **Código primeiro:** o estado e os marcos são validados por regras; LLM local pode redigir diálogos ou sugerir etapas, nunca executar a mudança mecânica.

## Etapas conceituais de uma jornada (não prescritivas)

```text
EVENT_CONFIRMED (ações / tendência) 
 -> ARC_CANDIDATE (relação com histórico, fé, ordem, aliados)
 -> LORE_AND_PERMISSION_CHECK (tempo, segredo, impacto, versão)
 -> OFFERED (jogador vê oportunidade legítima)
 -> ACCEPTED / DECLINED / DEFERRED
 -> MILESTONES (evidências, objetivos, pactos, reparação, dilemas)
 -> NARRATIVE_OUTCOME (registro e consequências sociais)
 -> IF mechanical restoration requested:
       RULES_PREFLIGHT -> HOST_COMMAND (somente se validado)
       -> HOST_RECEIPT -> PERSIST / UNCERTAIN_RECONCILE
```

A política de tempo da DEC-022 permite etapas pendentes, mas não força progresso irreversível enquanto o jogo estiver fechado.

## Contrato de dados candidato

```yaml
arc_id: personal_arc_unique_id
campaign_id: campaign_id
subject_player_character: character_instance_id
arc_type: redemption_or_transformation
origin_event_ids: [confirmed_event_id]
current_stage: proposed
accepted: null
alignment_projection_ref: external_alignment_state_ref
relationships_ref: []
canon_sources_ref: []
secrecy_policy_ref: player_backstory_acl
rule_profile_version: pinned_version
milestones: []
rewards:
  narrative: pending
  mechanical: blocked_until_validated
critical_change_policy: default_deny
host_receipt: null
```

Os campos/nomes são ilustrativos. `milestones` não significa conceder poderes; `host_receipt` só existe após o motor confirmar a operação. Endereços de arquivos ou IDs não são defaults de implementação.

## Caminhos narrativos exemplificativos

- **Redenção:** reparação material, confissão, serviço à comunidade, reconciliação com ordem religiosa — sem garantia de perdão geral.
- **Persistência no novo caminho:** aceitar perda legítima de poderes e trilhar carreira alternativa apenas em termos narrativos até SPEC de classe.
- **Transformação não religiosa:** reformular código pessoal, vínculos de facção ou lealdades; não todo personagem é paladino ou clérigo.
- **Fé e patronos:** relação pode mudar conforme a lore e as decisões; uma divindade não precisa conceder magia ou responder diretamente, e nenhum acesso técnico a poderes é presumido.
- **Jornada com consequências históricas:** cumprir objetivo pode desencadear rumor/hostilidade/alinhamento, mas qualquer evento crítico mantém aprovação especial.

## Matriz de testes candidatos

| ID | Cenário | Resultado esperado |
|---|---|---|
| REDEM-01 | Paladino decide buscar redenção | Oportunidade opcional; nenhum poder restaurado somente pela escolha |
| REDEM-02 | Paladino recusa jornada | Consequências confirmadas persistem; personagem continua jogável se motor permitir |
| REDEM-03 | Personagem sem classe religiosa muda moralmente | Caminho coerente sem indução forçada a religião ou mudança de classe |
| REDEM-04 | Conclusão da quest sem POC mecânica disponível | Final narrativo persistido, efeito mecânico `PENDING_TECH_VALIDATION` |
| REDEM-05 | Aplicação confirmada de módulo de recuperação futuramente validado | Recibo do host, no máximo uma aplicação e logs recuperáveis |
| REDEM-06 | Falha da bridge após pedido de poder | Reconciliar, sem tentar duas vezes por padrão |
| REDEM-07 | Rumor de arrependimento chega a guilda rival | Reputação por facção pode reagir sem modificar alinhamento por boato |
| REDEM-08 | NPC conheceu segredo apenas via prompt de narração | Não sabe/expõe informação sem proveniência legítima |
| REDEM-09 | Ordem/divindade inexistente em 1369 DR | Bloquear como cânone; oferecer alternativa ficcional explicitamente identificada |
| REDEM-10 | Jogador abandona a jornada | Estado recuperável; nenhuma sanção extra inventada pela IA |
| REDEM-11 | Save/reload em marco intermediário | Etapa e evidências preservadas, sem duplicar missão/recompensa |
| REDEM-12 | Dois personagens possuem motivos diferentes | Condições e objetivos individuais, sem vazamento de histórico de terceiros |
| REDEM-13 | Personagem pede perdão por dano irreparável | Conclusão possível sem apagar vítimas, histórico ou culpa pública |
| REDEM-14 | Jornada produziria alteração histórica HIGH | Gate de autorização DEC-034, nenhuma publicação automática |
| REDEM-15 | Divergência da modlist, classe/kit não suportados | Bloquear efeitos mecânicos, manter registro e diagnóstico |
| REDEM-16 | Segundo cliente desconecta durante conclusão | Estado do host é autoridade; sincronizar antes de consolidar |
| REDEM-17 | Jogador retoma save anterior com arco já concluído | Coerência entre save e event log; replay e idempotência |
| REDEM-18 | Modo Original com personagem semelhante | Nenhuma modificação do modo Original ou suas flags |

## Pendências para SPECS e testes

1. Progressão dos objetivos e sistema de geração de quests pessoais (**DEC-039 proposta**).
2. Catálogo histórico de instituições, deuses, juramentos, relações de patronato e profissões/classe por data e região.
3. Elegibilidade mecânica para redenção e recuperação por classe/kit (especialmente paladinos/rangers/clérigos e estados *fallen* conforme BG2:EE instalado).
4. Preflight do gateway, protocolo host, configuração compartilhada em multiplayer, reabertura do save e rollback real.
5. Parâmetros para marcos, falhas, alternativas e consequências, evitando opções narrativas coercitivas ou triviais.

**Estado técnico:** projeto em Discovery, nenhuma mudança de classe/habilidade instalada ou confirmada em BG2:EE/EEex.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Redenção/juramentos não revelam flags futuras de romances nem saltam etapas sem provas narrativas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para arcos pessoais exigem coerência das crenças e memória de cada NPC, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para arcos pessoais e confiança progressiva, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
