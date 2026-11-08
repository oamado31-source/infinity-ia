# ADR-0021 — Autonomia de publicação por níveis de risco

- **Decisão:** DEC-027
- **Escolha:** **Opção C — autonomia por níveis de risco**
- **Estado:** **APROVADA**
- **Data:** 2026-11-06
- **Origem:** escolha expressa do idealizador do Infinity AI.
- **Escopo:** conteúdos procedurais e repercussões produzidos/controlados pelo Infinity AI no modo Living World; **não** altera automaticamente scripts, quests e ações nativas do BG2:EE.
- **Dependências:** DEC-003, DEC-008, DEC-009, DEC-010, DEC-011, DEC-012 (aberta), DEC-014, DEC-019, DEC-021/022, DEC-024/025/026, DEC-005-E; ADR-0020.

## Contexto

O Living World deve gerar encontros, rumores, diálogos e pequenas aventuras sem interromper continuamente o anfitrião. Entretanto, eventos que afetam inventário, combate, personagens históricos ou o canon não podem ser aplicados como consequência livre de texto gerado por LLM. Validação narrativa, autorização de publicação e execução mecânica são **etapas distintas**.

## Decisão aprovada

1. Adotar **três faixas de risco** e não exigir aprovação humana para cada acontecimento.
2. **Baixo risco:** conteúdo exclusivamente narrativo, localizado e reversível, como rumores, diálogos e oportunidades sem efeito crítico, pode ser publicado automaticamente **após validação** de canon, data, conhecimento legítimo, segredos, identidade do NPC e campanha.
3. **Médio risco:** quests, encontros, recompensas e mudanças locais podem ser propostos e publicados dentro de contratos seguros após checagem de pré-condições, recursos permitidos, regras, estado e autorização de escopo; **todo efeito mecânico exige confirmação do host** e reconciliação. Confirmar mecanicamente não é o mesmo que pedir clique do anfitrião.
4. **Alto risco:** morte permanente de figura histórica, destruição de localização significativa, alteração política persistente, mudança de desfecho canônico ou desvio importante e irreversível exigem **política de autorização especial**. **Na ausência de política explícita, a ação permanece bloqueada/pendente e não é executada automaticamente.** A política poderá requerer aprovação humana, inclusive do anfitrião, quando definida e validada em SPEC posterior.
5. A classificação considera **efeitos e impactos cumulativos**, não o rótulo ou a intenção declarada pelo texto da IA. Agentes generativos não atribuem seu próprio nível de risco final, não autorizam exceções e não convertem uma alteração crítica em ato trivial para escapar do gate.
6. Toda publicação deve respeitar a separação entre **modo Original e Living World**, cronologia DR, fontes de canon, divergências autorizadas, segredos individuais, evento persistido e autoridade mecânica do host.
7. O orquestrador aplica regras/validação estruturada **antes** de qualquer ação no jogo; o LLM pode propor texto/plano, mas não despachar comandos arbitrários ou confirmar resultados.
8. Erros, timeouts e resultados incertos não permitem repetição cega. O estado fica `UNCERTAIN` até reconciliação com o host, protegendo contra duplicações de spawn, recompensa e efeitos irreversíveis.
9. Publicação e autorização **não implicam viabilidade de integração** no BG2:EE/EEex/multiplayer; a viabilidade precisa de provas de conceito. Novos mapas/recursos seguem os gates de geração offline e compatibilidade definidos pela DEC-010, qualquer que seja sua classificação narrativa.
10. Simulação em ausência e catch-up (DEC-021/022) **não** constituem autorização tácita para eventos críticos irreversíveis.

## Matriz de decisão normativa

| Faixa | Casos típicos | Publicação/autoridade | Comportamento sem validação |
|---|---|---|---|
| `LOW` | Rumor não secreto, diálogo, oportunidade sem mutação mecânica | Automática depois de checagens narrativas, temporais, conhecimento e consistência | Rejeitar, ajustar como proposta ou manter em rascunho |
| `MEDIUM` | Quest estruturada, encontro com criaturas existentes, recompensa ou mudança local controlada | Gates por regras/allowlist/estado; host confirma cada efeito mecânico e seus resultados | Não aplicar efeito; bloquear/publicação parcial segura apenas quando explicitamente separável |
| `HIGH` | Alteração de canon, morte histórica permanente, destruição política ou física importante, desfecho irreversível | Exige política especial explícita por campanha ou tipo de evento, com autorização verificável; aprovação humana se a política assim definir | Bloquear e enviar a pendência para análise/autorização futura |

**Regra de precedência:** caso existam múltiplos efeitos, aplicar o risco do efeito mais alto; múltiplos efeitos menores com impacto crítico agregado devem receber classificação `HIGH`. Escopos de autorização e limiares numéricos específicos **ainda não foram definidos**.

## Fluxo lógico candidato

```text
LLM / Template / Simulation proposes ContentDraft
      ↓
Schema and provenance checks (idempotent ID / version / creator)
      ↓
Canonical timeline + NPC knowledge + resources + impact analysis
      ↓
Risk classification by deterministic policy (not by LLM)
      ├── LOW → validated narrative publication (subject to interface availability)
      ├── MEDIUM → approved allowlisted proposal → host command → receipt/reconciliation
      └── HIGH → special policy gate → BLOCK unless explicitly authorized
      ↓
Persistent event log + projection, only after appropriate confirmation
```

Os rótulos técnicos e o fluxo ainda são desenho de Discovery, não API implementada.

## Fronteiras de segurança

- A validação de conteúdo não concede privilégios de execução. EEex Remote Console pode expor Lua poderosa; uma saída textual de LLM **nunca** deve ser enviada diretamente como Lua arbitrária.
- Política de risco não substitui **DEC-012** sobre permissões, allowlist, isolamento, escopos de comando e backups.
- Um resultado de validação não equivale a um `host_receipt` confirmado. Não registrar sucesso mecânico antes de evidência do motor (DEC-011).
- Segredos dos históricos dos jogadores não podem ser publicados apenas porque o narrador conhece a informação (DEC-019).
- O conteúdo publicado em uma campanha não se torna canon global das demais (DEC-009).
- O risco de um evento pode aumentar devido a efeitos indiretos, relações políticas ou consequências posteriores; mudanças de classificação exigem reavaliação antes da execução.
- Um conteúdo de baixo risco ainda precisa ser bloqueado se depender de recursos inexistentes, uma interface não suportada, scripts incompatíveis ou condição não confirmada.

## Evidências e critérios candidatos para SPECS

1. Rumor coerente e não secreto passa pelo gate `LOW`; rumor que revela segredo de outro personagem é rejeitado.
2. Quest de risco `MEDIUM` é validada estruturalmente; recompensa só é persistida depois de `host_receipt`.
3. Falha na bridge não converte ação pendente em realizada.
4. Evento `HIGH` sem política aprovada não é aplicado, mesmo se o LLM solicitar urgência.
5. Propostas de baixo risco encadeadas para eliminar um governante são promovidas a `HIGH` por avaliação de impacto agregado.
6. Atualização de regra/classificação invalida uma autorização antiga incompatível e exige nova avaliação.
7. Reexecução após timeout/reload não cria segunda quest, recompensa ou criatura.
8. Dois clientes não devem divergir na percepção de evento autorizado, sujeito à POC de multiplayer.
9. Uma sessão sem LLM mantém templates e regras seguras quando disponíveis.
10. Evento irreversível durante `DISTANT`/catch-up é retido sem autorização especial.
11. Modo Original e campanhas diferentes não compartilham autorizações ou estados derivados.
12. Nova área pré-gerada e aprovada narrativamente ainda depende de POC de carregamento, build e testes técnicos.
13. Uma proposta que tenta usar comando Lua fora da allowlist é recusada antes de chegar ao motor.
14. Eventos futuros oficiais não são publicados antecipadamente sem condições cronológicas e de conhecimento.

## Decisões ainda pendentes

- **DEC-012 (próxima):** modelo de segurança e autorização dos comandos, allowlist, permissões e auditoria de execução.
- Quem pode aprovar, para quais classes de evento, em qual momento, se autorização por sessão/campanha e política de expiração/retificação: **não definido por esta decisão**.
- Thresholds de classificação, escalonamento de impacto, limites de repetição, quotas e interface de aprovação: futura SPEC.
- Contratos e implementação de bridge, UI e multiplayer: POCs e SPEC ainda necessários.
- Distribuição/licenciamento de recursos gerados ou importados: DEC-017.

## Consequências

**Benefícios:** espontaneidade para eventos cotidianos; previsibilidade para ações mecânicas; controle de mudanças históricas e proteção de saves, canon e multiplayer.  
**Custos/riscos:** classificação conservadora pode suspender conteúdo; análise de impacto pode ser difícil; etapas de autorização e reconciliação aumentam a complexidade.

**Revisão:** exige novo ADR. A escolha C não aprova, por si só, a execução automática de eventos de alto risco.
