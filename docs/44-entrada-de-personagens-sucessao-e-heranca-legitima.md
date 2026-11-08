# DEC-044 — Integração contextual de novos personagens, progressão e herança legítima

**Discovery v4.0 · DEC-044 aprovada — opção C · ADR-0039 · desenho candidato, não SPEC nem implementação**

## 1. Objetivo e limites

Permitir que o grupo continue sua campanha quando um participante entre, troque de personagem, aposente um PC ou sofra morte definitiva. A troca deve conservar o mundo e as histórias anteriores, mas garantir que a nova identidade não se aproprie automaticamente de bens, conhecimento, reputação ou características de outro personagem. O jogo base continua responsável por criações/importações, slots de party, inventário e quaisquer mudanças mecânicas.

A própria possibilidade técnica de trocar o PC durante uma campanha BG2:EE multiplayer **não foi testada**; o fluxo abaixo é um **contrato de intenção a validar**.

## 2. Separação de identidades e fontes de verdade

| Entidade conceitual | Dado / autoridade | Armadilha a evitar |
|---|---|---|
| Jogador (`player_id`) | Conta/controlador autenticado | Identificar todos os PCs pelo jogador |
| Personagem (`pc_id`) | Histórico, escolhas, alinhamento, estado narrativo | Apagar/reciclar ID com morte ou renomeação |
| Slot do motor (`engine_slot_ref`) | Dados observáveis de party/controle (host) | Assumir que slot equivale sempre a um único PC |
| Campanha (`campaign_id`) | Mundo, regras, tempo, política de entrada | Misturar saves/identidades de campanhas diferentes |
| Arco narrativo (`arc_id`) | PSD, marcos, permissões, dependências | Transferir autoria sem fato causal ou consentimento |
| Fato/conhecimento (`fact_id`) | Evento/proveniência, leitores autorizados | Transmitir segredos por vínculo de conta |
| Item (`engine_item_ref`) | Inventário/estoque do host e reivindicações externas | Criar clone por distribuição ou restauração de save |
| Herança (`estate_claim_id`) | Direito alegado/aprovado sob regras da campanha | Equiparar alegação de direito à posse mecânica |

`player_id`, `pc_id`, `engine_slot_ref` e `campaign_id` são **identificadores conceituais**, ainda não schemas nem integrações reais do engine. O identificador do PC precisa ser estável na memória histórica, mesmo após remoção da party.

## 3. Pipeline de ingresso de novo PC

```text
Morte definitiva / aposentadoria / nova adesão
        |
        v
Elegibilidade de ingresso (campanha, jogador, política, estado confirmado)
        |
        v
Criação de identidade/histórico pelo jogador + regras de ficha
        |
        v
Perfil versionado de progressão/recursos + validação de restrições
        |
        v
Personal Story Director propõe entrada no mundo (sem vazar segredos)
        |
        v
Cooperative Story Director avalia oportunidade e contexto do grupo
        |
        v
Action Gateway -> host BG2:EE -> receipt ou UNCERTAIN
        |
        +-- sucesso mecânico comprovado -> vínculo PC / slot / campanha
        |
        +-- não suportado / falha -> sem ingresso fictício; fallback testado
        |
        v
Registro do ingresso e divulgação apenas dos fatos legitimamente conhecidos
```

Uma cena de encontro não antecede necessariamente a criação mecânica; a ordem final depende dos hooks disponíveis. O requisito é **não declarar um efeito executado antes de sua confirmação**.

## 4. Equilíbrio inicial sem clonagem de nível e itens

**Escolhido:** regra configurável de compatibilidade com a etapa atual da campanha, sem herança automática da ficha antiga.

Candidatos a SPECS, não valores aprovados:

- Perfis de nível/XP por faixa da party ou por marcos de campanha, com limites de classe e regras nativas.
- Restrições de equipamento inicial por orçamento/tier, disponibilidade real e risco regional.
- Regras antiabuso para impedir a criação sucessiva de PCs como fonte de XP, itens, ouro, magias raras, recursos ou reputação.
- Políticas de reposição de personagem após morte, aposentadoria e entrada de jogador novo, com fairness e transparência.
- Exceções aprováveis para grupos que preferem recuperação mais árdua ou progressão de nível estrita.

A escolha B (herança automática) **não foi aprovada**. Benefícios, itens ou experiência do personagem antigo só podem ser concedidos quando forem válidos pelas regras, não por identidade da conta.

## 5. Espólio, propriedade e transferências

Um PC falecido pode deixar inventário em cadáver, party, baú, espólio ou outro estado que a build realmente produza. **Não supor que o cadáver existe ou que itens são transferíveis sem verificar o motor.**

Modelo candidato de reivindicação:

```yaml
estate_claim_id: claim-unique
campaign_id: campaign-ref
source_pc_id: pc-falecido
candidate_heir_pc_id: pc-novo
item_refs: [engine-item-ref]
claim_basis: witnessed_will          # exemplo; não implica autenticidade
world_evidence_refs: [document-or-witness]
policy_version: campaign-policy-ref
owner_or_party_authorization_ref: null
risk_level: pending
host_receipt: null
status: PROPOSED                    # candidato, não estado oficial aprovado
```

Fluxo obrigatório: evidência do direito e disponibilidade real -> regras de propriedade/PvP/consentimento -> ação tipada com idempotência -> confirmação do host -> atualização de propriedade e conhecimento. Em caso `UNCERTAIN`, não liberar crédito de item nem repetir a transferência.

## 6. Metaconhecimento, rumores e reputação

- O **jogador humano** pode conhecer os segredos do antigo PC, mas o **novo PC** não. Expor segredos na interface do autor do antigo PC não autoriza inseri-los em diálogos ou decisões de NPCs.
- Um vínculo público de parentesco, amizade ou pertença a uma ordem pode ser proposto como parte do histórico e validado por cânone, tempo e evidências. Mesmo quando aceito, não cria recordações de fatos desconhecidos.
- NPCs poderão reagir de forma contextual ao vínculo legítimo (por exemplo, reconhecer um herdeiro), mas não importar automaticamente fama/hostilidade/temor quantitativos do PC anterior.
- Uma nova relação de herança não implica propriedade imediata, nem acesso a segredos privados, nem autoria de feitos passados.
- Arcos pessoais interrompidos podem permanecer abertos, encerrar com evidência ou originar novos ganchos; não transferir protagonismo/objetivos sem escolha do novo jogador e validação do PSD.

## 7. Casos específicos

| Cenário | Tratamento de arquitetura | Pendência técnica |
|---|---|---|
| PC morre definitivamente | Legado permanece; novo PC independente | Game-over, slot e importação |
| PC morre, depois retorna por ressurreição | Identidade original permanece distinta da do substituto | Coordenação e capacidade de party |
| Aposentadoria voluntária | PC anterior continua existindo/ausente conforme ações reais | Remoção/posicionamento na build |
| Novo jogador ingressa | Novo histórico e progressão de entrada por política | Multiplayer drop-in, slots e controle |
| Jogador usa outro PC após troca | Não copiar conhecimento privado | Troca de controlador e isolamento |
| Item do falecido é oferecido a novo PC | Só entrega confirmada e legítima | Inventário, ownership, receipt |
| Ente querido do falecido entra no grupo | Relação é candidata, não memória automática | Validação de histórico, canon e ACL |
| Save recarregado antes da morte | Reconciliar linha temporal e identidades | Fingerprints, rollback, replay e dedup |
| PC ausente por desconexão temporária | **Não** aposentar/substituir automaticamente | DEC-045 ainda aberta |
| Morte causada por outro jogador | Permadeath requer permissão distinta de duelo | DEC-042, limites do engine |

## 8. Interface candidata

A interface de entrada (não implementada) precisaria esclarecer: motivo do ingresso, nível/recursos permitidos, autoria do histórico, limites de conhecimento, efeitos de propriedade/herança e quando o novo PC passa a existir mecanicamente. Avisos e erros não devem revelar segredos de outras histórias. Não prometer que existe um botão de trocar PC em BG2:EE.

## 9. Testes candidatos (20)

| ID | Cenário | Resultado esperado |
|---|---|---|
| SUC-01 | Jogador morre e cria PC novo | `pc_id` novo, histórico do falecido intacto |
| SUC-02 | Usuário tenta usar `player_id` como `pc_id` | Separação de identidade impede mistura de dados |
| SUC-03 | Mesmo jogador sabe segredo do falecido | Novo PC não recebe segredo em prompt, UI in-world ou memória |
| SUC-04 | Novo PC afirma ser familiar do falecido | Vínculo depende de histórico e validação; sem memória mágica |
| SUC-05 | Falecido tinha reputação elevada | PC novo não herda automaticamente reputação nem alinhamento |
| SUC-06 | Novo PC recebe item por doação legítima | Transferência ocorre apenas após comprovante do host |
| SUC-07 | LLM sugere espólio que não existe no save | Não criar item; rejeitar/investigar proposta |
| SUC-08 | Novo PC é importado no host + dois clientes | Identidade, ficha e controle consistentes (se recurso suportado) |
| SUC-09 | Host rejeita inclusão por slot cheio | Não publicar ingresso mecânico fictício |
| SUC-10 | Protagonista morreu e engine encerra sessão | Não anunciar continuidade sem workaround testado |
| SUC-11 | Ressurreição do antigo PC após novo ingresso | Evitar duplicar slots, controle, itens e perfis |
| SUC-12 | Queda de rede durante transferência de inventário | Estado UNCERTAIN e reconciliação antes de retry |
| SUC-13 | Nova ficha tenta classe/kit incompatível | Regras da build bloqueiam alteração irregular |
| SUC-14 | Várias trocas criam riqueza artificial | Política de recursos detecta tentativa de exploit |
| SUC-15 | Novo PC surge em região distante e sem ligação | Diretores propõem entrada plausível, sem teleporte fictício |
| SUC-16 | Alteração de save/rollback desfaz ingresso | IDs/eventos conciliados, sem duplicação e sem retcon silencioso |
| SUC-17 | PC aposentado permanece vivo no mundo | História e relações intactas, sem morte inventada |
| SUC-18 | Outro jogador exige propriedade do espólio | Regras de titularidade/PvP/consentimento governam disputa |
| SUC-19 | Abrir modo Original ou outra campanha | Zero vazamento de PCs, recursos, segredos ou configuração |
| SUC-20 | Jogador ausente temporariamente é tratado como falecido | Proibição de substituição sem decisão/estado confirmados |

## 10. Riscos, perguntas e gates

**Gates técnicos não satisfeitos:** criação/importação de novos PCs, troca em sessão, protagonismo, slots da party, escolha de controlador, propriedade de inventário, XP inicial, interação do PSD com o jogo, NPCs representando aposentados, save/load e reconciliação multiplayer. Primeiro BG2:EE limpo + 2 clientes, depois EEex e mods em fases controladas (DEC-003).

**Riscos principais:** criação de itens/XP por repetição de sucessões, duplicação ao reconectar/carregar, mistura de identidades, vazamento de históricos secretos, propriedade falsa, retcon de morte e transição não suportada do protagonista.

**DEC-045 aberta:** continuidade da sessão quando o jogador se desconecta ou falta, incluindo proteção de agência, risco para PC ausente e recuperação ao reconectar. Não presumir que ausência é aposentadoria ou permissão de controle automático por IA.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Mudanças de sucessão/entrada de PC não migram automaticamente responsabilidades e aprovações de uma revisão operacional anterior.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Heranças e transferências confirmadas não revertem para o dono do template/CRE.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Sucessão de PC não transfere os segredos privados ou leitura de quests do personagem anterior.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Distinguir acusação e fato, resposta e confissão, recusa e culpa, mediação privada e decisão jurídica. Preservar fontes e memória falível; prova contraditória não concede veredito, e assinatura de termo não implica perdão nem reparação automática. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**
