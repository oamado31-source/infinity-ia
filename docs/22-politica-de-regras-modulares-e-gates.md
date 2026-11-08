# Política de regras modulares e validação — DEC-005-R

**Discovery v2.0** · **Documento técnico preliminar (não é SPEC final)**  
**Decisão vinculante:** DEC-005-R / ADR-0018; **dependência:** DEC-005-T / ADR-0017.

## Princípio

O motor BG2:EE permanece a autoridade sobre regras e resultados mecânicos na baseline AD&D 2e. Modernizações serão extensões isoladas e explicitamente escolhidas, preferencialmente sem substituir o motor ou portar todas as regras de D&D 3e/5e.

### Três classes de alterações

| Classe | Exemplos de candidatos | Risco inicial | Política |
|---|---|---|---|
| `presentation` | ajuda contextual, descrição de THAC0/AC, log de ações | Menor | Sem mudar cálculos ou saves |
| `behavior` | opções de pausa automática e suporte de interface | Médio | Confirmar efeitos de temporização/host |
| `mechanical` | mudanças em regras de ações, efeitos, progressão, classes ou magias | Elevado | SPEC + POC + regressão + multiplayer + save/load obrigatórios |

Os exemplos não foram aprovados como features.

## Interação com outros sistemas

```text
Campaign Rule Profile (configurado, validado e congelado por sessão)
       |
       +--> AD&D 2e baseline [BG2:EE]
       |
       +--> Optional Module Registry [somente mods compatíveis e validados]
       |
       +--> Combat Mode: RTwP [disponível] / Turn-based [POCs pendentes]
       |
       +--> Encounter Director [DEC-005-E pendente]
       |
       v
Host executes mechanical results / bridge reports receipts
       |
       v
Infinity AI persists authoritative narrative effects, only after confirmation
```

Essa arquitetura lógica não comprova existência de hooks, comunicação ou multiplayer modificado em BG2:EE.

## Contrato de módulo — schema candidato

```yaml
module_id: example-module
version: 0.1.0
class: presentation  # presentation | behavior | mechanical
enabled_by_default: false
supported_engine: [BG2EE_TESTED_VERSION]
requires: []
conflicts: []
affected_resources: []
save_compatibility: requires_validation
multiplayer_validation: pending
rollback: disable_only_after_validation
```

Valores são ilustrativos, não inventário de versões realmente suportadas.

## Política de ativação

- A campanha declara um **perfil** com lista de módulos/versionamentos; o host compara com o manifesto de instalação antes da sessão.
- Troca de regra mecânica não ocorre silenciosamente durante combate, entre clientes ou em save existente.
- O modo Original permanece separado do Living World.
- Padrão seguro: desativar módulos opcionais até sua compatibilidade estar aprovada.
- Um erro de módulo mecânico deve produzir diagnóstico e restauração de baseline compatível, não alteração silenciosa de personagem/inventário.
- O efeito exato da troca de perfil sobre campanhas já iniciadas fica para uma futura SPEC de migração.

## Provas de conceito e testes candidatos

| Teste | Ação | Resultado esperado |
|---|---|---|
| RULE-01 | Rodar BG2:EE sem módulos | Baseline verificável de ataques, salvaguardas, magias e itens |
| RULE-02 | Habilitar apenas módulo de apresentação | Valores mecânicos e saves inalterados |
| RULE-03 | Simular combinação de módulos incompatíveis | Rejeição antes da sessão |
| RULE-04 | Testar descompasso de perfis entre 2 clientes | Não permitir resultados de combate divergentes |
| RULE-05 | Salvar/reabrir campanha com versão fixada | Mesma configuração e resultados coerentes |
| RULE-06 | Desabilitar módulo após regressão | Recuperar estado compatível sem corromper o save |
| RULE-07 | Com / sem modo TBC quando disponível | RTwP não sofre regressão; turnos passam gates separados |
| RULE-08 | Gerar encontro por regra, sem LLM | Decisões mecânicas determinísticas e evidência do host |

## Pontos pendentes

1. Catálogo dos primeiros módulos desejados, por prioridade e custo.
2. Versões exatas de BG2:EE, EEex, mods e máquinas de teste.
3. MECÂNICA DE DIFICULDADE — DEC-005-E: tabelas por região, diretor adaptativo limitado ou escalonamento global.
4. Definição de seeds, logging, RNG, observabilidade e níveis de segurança para eventos de encontro.
5. Contrato final de save/load, migração, rollback e sincronização multiplayer.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

O tempo DR e os estados FROZEN/PARTIAL/REALTIME condicionam triggers, novas janelas e atualizações de plano; não avançar agenda de mundo só pelo monitor.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C só pode avaliar transições permitidas pelo world-clock do host; não se baseia na data real ou tick do OS. FROZEN/PARTIAL/REALTIME devem preservar ordem causal e histórico das fases.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.

## Integração DEC-098/C — Materialização regional (Discovery v9.4)

FROZEN/PARTIAL/REALTIME determinam orçamento de catch-up DEC-098; no modo FROZEN não avançar ticks por tempo real do OS.

**Referências:** ADR-0093; `docs/98-materializacao-incremental-regioes-snapshots-deltas-catchup-e-reconciliacao.md`. 104 testes de integração/aceitação T098-* **NÃO EXECUTADOS**; nenhuma API BG2:EE/EEex comprovada. Os ADRs previamente aprovados não foram alterados.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Clock FROZEN/PARTIAL/REALTIME não implica progresso de quest não confirmado por eventos/host.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **tempo e calendário**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para calendário e janelas temporais condicionais, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-108/C — Cumprimento de acordos e provas host-confirmed

Prazos, tolerâncias e janelas de acordo seguem exclusivamente calendário DR autorizado. **Não presumir** inadimplência, quitação, sanção, devolução, reputação ou mutação mecânica a partir de prazo/claim. Fonte: ADR-0103 / doc.108. DEC-060..107 permanecem vinculantes; POCs BG2:EE/EEex e 160 casos candidatos **não executados**.

### Integração DEC-109/C — Obrigações condicionais multipartes

Janelas de ativação e prazos pertencem ao calendário DR validado. **Condição comprovada ≠ autorização ≠ execução**: DEC-107/108 são pré-condições; DAG versionado/DR/ACL/receipts/fencing e host gates obrigatórios. Fonte ADR-0104 / doc.109. POCs de BG2:EE/EEex e 168 cenários candidatos **NÃO EXECUTADOS**.
