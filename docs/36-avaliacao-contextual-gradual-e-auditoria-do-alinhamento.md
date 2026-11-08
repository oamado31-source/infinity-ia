# Avaliação contextual e gradual de alinhamento — desenho técnico preliminar

- **Discovery:** v3.2 — DEC-036 **aprovada, opção B**; ADR-0031.
- **Status:** propostas de estruturas, testes e fluxo para SPECS; **nenhuma implementação ou fórmula numérica aprovada**.
- **Relações:** DEC-035, DEC-030, DEC-028, DEC-029, DEC-014, DEC-011, DEC-012, DEC-020, DEC-005-R, DEC-034; **DEC-037 permanece aberta**.

## Fronteiras de verdade

| Estado lógico | Dono/fonte | O que é permitido | O que NÃO significa |
|---|---|---|---|
| `world_event` | Evento confirmado host/narrativa autorizada | Fatos, autoria, data e fonte com evidência | Um julgamento ético por si só |
| `moral_evidence` | Projeção verificada de contexto | Fatos sobre escolhas e circunstâncias legitimamente registradas | Leitura de pensamentos ou conclusões infalíveis |
| `alignment_trend` | Regras versionadas | Tendência contextual por cada eixo, com explicação e incerteza | `engine_alignment` atualizado automaticamente |
| `social_perception` | Conhecimento/reputação DEC-028/029/030 | Crença do observador e sua proveniência | Caráter objetivo do personagem |
| `engine_alignment` | BG2:EE e host | Estado mecânico tal como confirmado pelo jogo | Projeção narrativa externa sempre sincronizada |

## Pipeline candidato

```text
EVENT COMMIT / ACK
  -> Checar identidade, campanha, autoria, evento único
  -> Consultar contexto de fatos autorizado e versionado
  -> Taxonomia de situações e regras de avaliação (código)
       -> se ambíguo: análise local sob demanda, limitada a sugerir
       -> se inconclusivo: estado pendente e revisão humana sob política futura
  -> Compor tendência por eixo, preservando os fatos anteriores
  -> Gerar explicação auditável, com referência às evidências
  -> Atualizar apenas o estado narrativo autorizado
  -> Notificar mecanicamente o host APENAS por futuro módulo validado e com autorização
```

## Envelope de evento candidato

```json
{
  "campaign_id": "example-campaign",
  "character_id": "example-character",
  "event_id": "example-event-123",
  "world_time": "1369-DR-date-to-be-defined",
  "source": "host-confirmed-or-authorized-narrative",
  "participants": [{"character_id":"example-character","role":"actor"}],
  "facts": ["confirmed-fact-id"],
  "context": {
    "available_knowledge": ["fact-id"],
    "coercion_evidence": "unknown",
    "harm_evidence": "unknown",
    "intention_evidence": "unknown"
  },
  "evaluation_policy_version": "example-policy-v0",
  "status": "NEEDS_REVIEW"
}
```

**Exemplo de contrato, não API implementada.** Em particular, `unknown` nunca autoriza o modelo a inventar intenção. A autoria real também pode ser múltipla/indeterminada e deverá ser representada sem culpabilidade automática.

## Escolhas de avaliação (a detalhar somente em SPECS)

- **Taxonomia de condutas:** categorias verificáveis de escolha/ação e contexto; ordem e bondade avaliadas em eixos independentes. A taxonomia não pode se reduzir a 'obedecer lei = Good' ou 'desobedecer = Evil'.
- **Agência e intenção conhecida:** separar o que o personagem decidiu, o que sabia, o que foi coagido a fazer e o que aconteceu. Não exigir que a IA leia motivações invisíveis.
- **Gradualidade:** tendências, inércia, relevância de eventos e tratamento de comportamentos conflitantes; evitar que opções repetitivas facilitem 'farm' de alinhamento.
- **Casos controversos:** suspender decisão (`NEEDS_REVIEW`) em vez de impor penalidade; oferecer explicação e eventual revisão do julgamento **sem apagar o evento**.
- **Persistência:** avaliações versionadas e reproduzíveis, com vínculo ao mundo e ao save; armazenar evidências em local autorizado, não necessariamente no prompt do NPC.
- **Relevância:** avaliar preferencialmente eventos de decisão efetiva, não cada microação de combate nem cada diálogo trivial.
- **Mecânicas BG2:EE:** não sincronizar automaticamente classe, status fallen, magias, equipamentos ou alinhamento de engine com a projeção externa.

## Testes de aceitação candidatos

| Teste | Condição | Resultado esperado |
|---|---|---|
| CTX-01 | Chaotic Good segue acordo por convicção | Potencial tendência ética, sem mudar Good compulsoriamente |
| CTX-02 | Personagem comete crime para salvar inocente | Separação entre legalidade e moralidade; contexto obrigatório |
| CTX-03 | Assassinato com intencionalidade desconhecida | Classificação suspensa/restrita quando contexto insuficiente |
| CTX-04 | Personagem sob magia de dominação | Análise considera coerção comprovada |
| CTX-05 | Rumor falso | Nenhum efeito em alinhamento, ainda que reputação se altere |
| CTX-06 | Ação individual num grupo de 6 | Outros não recebem alteração automática |
| CTX-07 | Mesmo evento recebido duas vezes | Uma única evidência e uma única avaliação |
| CTX-08 | Histórico versionado e retcon solicitado | Verifica decisão DEC-020; nada é reescrito silenciosamente |
| CTX-09 | LLM alucina motivação | Proposta descartada pela validação sem fonte |
| CTX-10 | Caso controverso | Pendente, com justificativa e sem mudança mecânica não aprovada |
| CTX-11 | Paladino muda projeção para Neutral | Sem alteração no motor sem gate de compatibilidade |
| CTX-12 | Cliente coop diverge na avaliação | Bloqueio/reconciliação antes de consolidar resultado |
| CTX-13 | Regras avaliadoras atualizadas | Snapshot antigo mantém versão ou migração expressa |
| CTX-14 | Segredo de personagem em avaliação | Não aparece em prompt de NPC ou log sem autorização |
| CTX-15 | Acidente gera dano não intencional | Não atribuir intenção maligna por resultado isolado |
| CTX-16 | Jogo fechado por semanas | Não inferir novas ações morais sem eventos autorizados |

## Dívidas explícitas

1. Escolher escala interna, pesos, limiares, janela temporal e ajustes de tendência sem tornar rótulos artificiais.
2. Definir revisão/adjudicação em situações ambíguas, transparência e critérios de contestação.
3. Definir consequências mecânicas de classes, kits, magias, equipamentos e restrições originais: **DEC-037**.
4. Validar a viabilidade técnica de leitura/alteração do alinhamento, gatilhos e notificações via BG2:EE/EEex, incluindo host/clientes e save/load.
5. Decidir se e como aplicar essa lógica aos NPCs clássicos; não pressupor que DEC-035 abrange todos os personagens.

Não houve instalação, teste técnico ou alteração do jogo nesta etapa.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Avaliação moral não presume fatos por flags técnicos sem contexto causal e sem conhecimento legítimo.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
