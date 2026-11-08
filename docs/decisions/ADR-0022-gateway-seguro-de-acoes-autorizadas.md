# ADR-0022 — Gateway seguro de ações autorizadas

- **Decisão:** DEC-012 — Segurança, autorização e execução de ações dos agentes.
- **Estado:** **APROVADA — opção B**.
- **Data:** 2026-11-06.
- **Motivação:** permitir NPCs e acontecimentos espontâneos sem fornecer ao LLM acesso arbitrário ao processo BG2:EE, Lua, filesystem ou poderes administrativos.
- **Dependências vinculantes:** DEC-011 (autoridade do host), DEC-014 (código primeiro), DEC-027 (risco de publicação), DEC-003 (integração progressiva), DEC-008 (persistência), DEC-019 (segredos), DEC-021/022 (simulação e tempo), DEC-010 (conteúdo validado).

## Contexto

EEex e ferramentas de controle externo podem expor ações privilegiadas e até execução de Lua. Conversas e conteúdo gerado são **dados não confiáveis**: um NPC, um jogador ou um resultado de LLM não deve conseguir converter texto em código executável. A escolha entre publicar narrativa, autorizar uma tentativa e confirmar mudança mecânica deve ser operacionalmente distinta.

## Decisão arquitetural aprovada

1. Estabelecer um **Action Gateway** entre orquestrador/agentes e o adaptador/bridge do jogo. Agentes criam **pedidos de ações tipadas** que só podem corresponder a uma **allowlist explícita** de operações com parâmetros e consequências previamente contratados.
2. Aplicar **negação por padrão (default deny)**: qualquer ação desconhecida, parâmetro inválido, escopo incorreto, versão não suportada ou autorização ausente é rejeitado **antes** de tocar o motor.
3. A decisão de permissão deve ser tomada por **código e políticas determinísticas**, não pelo texto de um LLM. Um modelo não executa Lua arbitrário, shell, comandos do SO, leitura de arquivos ou escrita direta em saves/estado do jogo.
4. Cada pedido deve ser contextualizado pela identidade da **campanha**, modo (`Living World`, não `Original`), sessão, agente/ator e, quando necessário, região, fase cronológica, recursos disponíveis, versão de build, pré-condições, quotas e risco agregado. Privilegios são mínimos e específicos por operação.
5. Incorporar a **DEC-027**: `LOW` pode ser publicação narrativa validada e **não equivale a permissão mecânica**; `MEDIUM` exige gates de operação e confirmação mecânica do host; `HIGH` permanece **bloqueado sem política especial de autorização explícita**, que será definida em SPECS/decisão específica. **Esta ADR não define quem aprova HIGH nem habilita execução automática.**
6. O **host/jogo tem autoridade sobre resultados mecânicos**. Gateway autoriza tentativa; bridge remete uma ação permitida, verifica resposta e, após confirmação do host, persiste os fatos. Um comando autorizado **não equivale a um efeito ocorrido**.
7. Proteger contra duplicações e divergências: cada pedido terá ID de idempotência e transições auditáveis. Em timeout/erro incerto, marcar `UNCERTAIN`, consultar/reconciliar o estado do host e **nunca repetir cegamente** spawn/recompensa/quest.
8. Exigir separação entre privilégios de **leitura**, criação de propostas narrativas, alterações externas de narrativa e **mutações mecânicas**. Informações secretas e dados privados não são expostos a agentes por terem permissão de executar uma operação. Regras detalhadas de **recuperação de contexto / ACL de leitura** ficam para a DEC-028.
9. Preferir isolamento do serviço de IA em processo separado e canal local protegido, sem porta exposta à rede por padrão; acesso ao console/EEex deve estar restrito a um **adaptador confiável**. Limitar recursos, tempo e volume de ações. Qualquer mecanismo específico de transporte/autenticação será especificado/testado depois.
10. Manter versionamento das capacidades, políticas, manifestos e logs de auditoria por campanha; logs não devem vazar segredos. Integração e multiplayer são **gates de prova técnica**, não capacidades comprovadas por esta decisão.
11. Inicialmente, realizar POCs de **leitura não mutável**; avançar para alterações controladas em ambiente de teste, somente depois para dois clientes multiplayer. Para falha de validação, falha de autorização, transporte indisponível ou estado não conciliado, falhar de modo seguro.

## Fluxo de confiança conceitual

```text
Untrusted text (NPC/dialogue/player/LLM) -> proposal only
       |
       v
Typed action envelope -> schema validation / identity & scope
       |
       v
Canonical time + knowledge + permissions + risk aggregation
       |
       +-> DENIED / HOLD (HIGH w/o explicit policy) / DRAFT
       |
       v
Allowlisted operation / quotas / preconditions / idempotency
       |
       v
Trusted host-side adapter -> actual game mechanics (if supported)
       |
       v
Host confirmation / reconciliation -> durable event & projection
```

**As setas representam requisitos de arquitetura, não APIs existentes.**

## Exemplos de operações candidatas (não implementadas)

| Operação lógica | Categoria | Requisitos extras |
|---|---|---|
| `propose_rumor` | narrativa `LOW` | validação de conhecimento e canon, sem mudança mecânica |
| `propose_quest` | estado narrativo `MEDIUM` | estrutura, recursos, risco e autorização de publicação |
| `request_encounter` | mutação mecânica `MEDIUM` | tabela regional, limitações, host e idempotência |
| `request_item_reward` | mutação mecânica `MEDIUM` | regras de economia, inventário, host e idempotência |
| `request_world_state_change` | potencial `HIGH` | avaliar efeitos e dependências; bloquear quando crítico sem política especial |

Os nomes são **rótulos de Discovery**, sem contratos implementados e sem presunção de que o EEex oferece hooks suficientes.

## Estados e confirmação

`PROPOSED` -> `SCHEMA_VALID` -> `AUTHORIZED` -> `DISPATCHED` -> `HOST_CONFIRMED` -> `COMMITTED`.

Alternativas: `REJECTED`, `BLOCKED_HIGH`, `UNCERTAIN`, `RECONCILED`, `EXPIRED`, `CANCELLED`; nenhuma transição pode inventar o `HOST_CONFIRMED`. Eventos narrativos de baixo risco que não exigem host usam fluxo separado de publicação validada.

## Medidas de proteção essenciais

- **Prompt injection**: instruções fornecidas em diálogo, livros, descrições, URLs e conteúdos de usuários são dados, não comandos para alterar permissões.
- **Transporte**: vincular emissor e contexto de campanha; proteger canais, não abrir o console Lua à LAN/Internet, rejeitar mensagens não autenticadas; detalhes só após POC.
- **Permissão**: capacidade específica por operação, sem privilégios amplos `execute_lua`, `run_shell` ou `filesystem_write` para agentes.
- **Contexto**: verificar estado atual no momento de despachar, pois um NPC pode ter morrido, item esgotado, grupo saído da área ou época avançado desde a proposta.
- **Recuperação**: se não houver consulta de confirmação confiável, não afirmar sucesso; manter `UNCERTAIN`, reavaliar manualmente se preciso e não repetir mutações.
- **Auditoria**: evento mínimo com IDs e razões de aprovação/rejeição, evitando texto integral de histórico privado em logs comuns.
- **Privilégios do SO**: executar processos com o mínimo de permissões compatível com o motor; separar chaves e arquivos de save, limitar IPC.
- **Múltiplos clientes**: somente host processa mutações autoritativas; clientes não executam comandos diretos no adaptador.

## SPECS e testes candidatos

1. Pedido com operação fora da allowlist é rejeitado sem chegar ao jogo.
2. Parâmetro inesperado, tipo inválido ou referência a recurso inexistente não atravessa o gateway.
3. Prompt malicioso dentro do diálogo de um NPC é tratado como texto, não como autoridade.
4. Pedido em modo Original, outra campanha ou sessão vencida é negado.
5. `LOW` com segredo ilegítimo é bloqueado mesmo sem efeito mecânico.
6. Quest/loot/spawn `MEDIUM` permanece pendente até recibo positivo do host.
7. Comando `HIGH` sem política especial é bloqueado, mesmo quando combinado com outros pedidos menores.
8. Repetição do mesmo ID não duplica spawn/recompensa; timeout gera `UNCERTAIN`.
9. Verificação de pré-condição impede execução após mudança de área, morte do NPC ou mudança de versão.
10. Cliente não-host não consegue modificar estado autoritativo.
11. Falha de bridge, reinício ou queda de comunicação não cria confirmação artificial.
12. Auditoria distingue aprovação, despacho, resultado e reconciliação, sem publicar dados secretos.
13. POC com dois clientes comprova consistência antes de liberar qualquer feature mecânica.
14. Mudanças no manifesto de capacidades/versões causam revalidação das ações pendentes.

## Em aberto

- Nomes finais e schemas de operações, formato de tokens/permissões, quotas, autenticação/transporte, expiração, UI e política de backups: SPECS após POCs.
- Política especial e papéis humanos para eventos `HIGH` **não foram escolhidos**; manter bloqueio padrão.
- Persistência operacional, logs/replay e recuperação detalhada: DEC-018/SPECS.
- **DEC-028 (próxima):** autorização de **leitura/contexto** antes da inferência: que conhecimentos e memórias cada NPC, narrador ou agente de tarefa pode receber (além do princípio aprovado na DEC-019).
- Comprovação de hooks do EEex/Remote Console, viabilidade de runtime, sincronização multiplayer e compatibilidade com EET/IWD/NWNForBG.

## Consequências

**Benefícios:** autonomia para ações comuns sem acesso irrestrito ao motor; superfície de ataque menor; decisões mecânicas rastreáveis; separação entre conteúdo gerado e fatos confirmados.

**Custos e riscos:** construção de contratos e mecanismos de reconciliação; possibilidade de negar ações narrativamente desejáveis; esforço de testes de segurança, multiplayer e save/load; proteção da bridge exige isolamento correto do processo privilegiado.

**Revisão:** somente mediante novo ADR, sem relaxar as decisões anteriores de autoridade e risco inadvertidamente.
