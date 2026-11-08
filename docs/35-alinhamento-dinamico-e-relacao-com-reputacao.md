# Alinhamento dinâmico e separação de reputação — DEC-035

**Estado:** desenho técnico preliminar de Discovery v3.1; **não é implementação/SPEC final**.  
**Decisão aprovada:** alinhamento mutável conforme ações e contexto; ADR-0030.  
**Próxima decisão:** DEC-036 — como arbitrar mudanças morais/éticas concretas.

## Domínios separados

| Registro | Pergunta que responde | Fonte de atualização | Efeito |
|---|---|---|---|
| `confirmed_event` | O que ocorreu, quem participou e quando? | Host/evento narrativo autorizado | Verdade da campanha, persistida |
| `alignment_projection` | Como o personagem tem agido nos eixos moral e ético? | Avaliação de ações confirmadas e contexto | Orientação moral/ética, independente da opinião pública |
| `social_perception` | O que determinado NPC/facção acredita sobre o personagem? | Conhecimento legítimo + rumores | Reputação, confiança, temor e relações (DEC-030) |
| `engine_alignment` | Qual alinhamento mecânico o BG2:EE registra? | Somente alterações por integração validada | Restrições e efeitos concretos do motor |
| `engine_reputation` | Qual o valor global de reputação do BG2:EE? | Lógica nativa do jogo | Compatibilidade e mecânicas originais |

**Nunca derivar `alignment_projection` diretamente de `social_perception`** nem presumir que uma mudança externa foi aplicada no `engine_alignment`. Um criminoso pode ser visto como herói por sua guilda; um herói anônimo pode ter nenhuma reputação pública.

## Nove alinhamentos — interpretação por eixos

| Eixo ético (ordem ↔ autonomia) | Eixo moral (altruísmo ↔ dano/egoísmo) | Possíveis rótulos |
|---|---|---|
| Lawful / Neutral / Chaotic | Good / Neutral / Evil | LG, NG, CG, LN, TN, CN, LE, NE, CE |

Os nomes dos eixos são explicações simplificadas, não fórmulas aprovadas. A passagem de Chaotic Good para Lawful Good corresponde primariamente a mudança de eixo ético; a passagem para Chaotic Evil envolve mudança moral, independentemente da reputação.

## Fluxo candidato (não aprovado como método de pontuação)

```text
Ação do personagem / decisão em quest
  → Evidência de participação + resultado host/autoridade narrativa
  → Contexto verificável (defesa própria, coerção, conhecimento, intenção, consequências)
  → Registro de acontecimento imutável/corrigível por política DEC-020
  → Avaliador moral/ético (DEC-036 aberta)
  → Estado narrativo de alinhamento + explicação auditável
  → Separadamente, repasse social a observadores com conhecimento legítimo
  → Efeito mecânico *somente* se módulo aprovado/POC/host confirmar
```

### Exemplos de interpretação, não tabelas automáticas

- Um personagem **Chaotic Good** investiga e impede assassinato por respeito à vida. Isso não o torna automaticamente *Lawful*; seguir leis é diferente de proteger alguém.
- Outro personagem participa da conspiração porque o governante oprime inocentes. O ato não é automaticamente *Evil* sem contexto de objetivos, meios e danos.
- Um personagem executa deliberadamente pessoas inocentes para obter poder. Isso pode contribuir para tendência *Evil* mesmo se ninguém testemunhou. Sua reputação pública pode permanecer inalterada.
- Uma cidade acredita que o grupo cometeu crime que não cometeu. Sua reputação piora, **não** seu alinhamento moral.

## Compatibilidade BG2:EE: ponto de risco elevado

O manual oficial de **Baldur's Gate II: Enhanced Edition** afirma que algumas classes têm opções de alinhamento limitadas (o paladino comum é Lawful Good) e que desvios severos podem ter consequências e perda de habilidades. **Fonte:** [BG2:EE — Amn Survival Guide, seção Alignment, página impressa 34](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/257350/manuals/BGIIEE_-_Amn_Survival_Guide.pdf).

Logo, as opções de produto exigem POCs distintas para mudança narrativa, alteração efetiva do atributo do personagem e todas as dependências mecânicas (classe/kit, itens, magias, reações, diálogos e estado de *fallen*). A implementação poderá começar pela projeção narrativa externa sem prometer que o engine já aceita todos os cruzamentos.

As regras-base AD&D 2e permanecem conforme DEC-005-R. Modernização das restrições de classes é uma **feature separada**, não uma consequência automaticamente autorizada desta decisão.

## Testes candidatos

| ID | Caso | Verificação |
|---|---|---|
| ALIGN-01 | Jogador CG acumula comportamento autoritário recorrente | Eixo ético pode evoluir sem mudança moral compulsória |
| ALIGN-02 | Personagem comete ato egoísta longe de testemunhas | Alinhamento pode mudar; reputação pública não ganha conhecimento automaticamente |
| ALIGN-03 | Rumor falso incrimina personagem | Reputação pode variar, alinhamento confirmado não |
| ALIGN-04 | Jogador 1 faz ato sem ajuda do jogador 2 | Não mudar alinhamento de jogador 2 sem autoria causal |
| ALIGN-05 | Personagem protege governante corrupto | Contexto determina interpretação, não rótulo pré-definido |
| ALIGN-06 | Personagem paladino é avaliado como não Lawful Good | Exige política de classe e POC antes de mutar engine |
| ALIGN-07 | Estado narrativo e engine temporariamente diferentes | Marcar estado mecânico pendente, sem afirmar mudança efetiva |
| ALIGN-08 | Save/reload/replay | Mesma sequência moral/ética, sem dupla contagem |
| ALIGN-09 | Modo Original | Alinhamento original preservado sem modificação externa |
| ALIGN-10 | Multiplayer | Transição e autoridade consistentes entre jogadores |
| ALIGN-11 | Contexto ambíguo ou coação | Não atribuir automaticamente julgamento forte; política DEC-036 |
| ALIGN-12 | Atos contrários em sequência | Não oscilar de alinhamento a cada clique; limiares ainda a definir |
| ALIGN-13 | Segredos de histórico | Não expor motivações privadas em diálogos de NPC sem descoberta legítima |
| ALIGN-14 | Evento crítico HIGH | Exige DEC-034 independentemente de possível consequência moral |

## Itens em aberto para a DEC-036

1. Método de apuração da evolução (tabela de ações, inferência narrativa, sistema híbrido contextual).
2. Critérios para coerção, legítima defesa, intenção, padrão de escolhas e mudanças graduais.
3. Mudanças morais de NPCs clássicos vs personagens jogadores (escopo desta aprovação concentra-se nos jogadores).
4. Informação e consentimento do jogador sobre penalidades de classe e possibilidade de recuperação.
5. Exibição da tendência sem revelar segredos a outros NPCs/clientes.


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Alinhamento não é alterado pela leitura de uma quest flag; exige acontecimentos confirmados e regras específicas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração arquitetural DEC-104/C — retificação de consequências (Discovery v10.0)

No domínio de **política de risco**, aplicar ADR-0099 e `docs/104-retificacao-causal-consequencias-de-quests-contencao-compensacoes-e-conhecimento.md`: retificações curadas exigem grafo de proveniência por campanha/ramo/epoch; **conter apenas novos despachos elegíveis**, quarentenar `DISPATCHED/UNCERTAIN`, preservar recibos e conhecimentos já registrados, propor revisões CAS e Sagas DEC-095 apenas com autorização. Nenhuma correção por LLM ou exclusão retroativa; efeitos mecânicos requerem Action Gateway/host. **Arquitetura aprovada; integração e 140 casos T104-* NÃO EXECUTADOS.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para alinhamento não pode ser alterado por correção de rumor, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para alinhamento não é restaurado por reputação, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
