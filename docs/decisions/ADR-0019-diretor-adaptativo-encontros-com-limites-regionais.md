# ADR-0019 — Diretor adaptativo de encontros com limites regionais

- **ID da decisão:** DEC-005-E — política de encontros e balanceamento.
- **Status:** **APROVADA — opção B**.
- **Data:** 2026-11-06.
- **Origem:** escolha expressa do idealizador do Infinity AI.
- **Contexto:** Living World cooperativo, motor-base BG2:EE, núcleo AD&D 2e (DEC-005-R).
- **Referências:** DEC-005-R / ADR-0018; DEC-005-T / ADR-0017; DEC-003 / ADR-0006; DEC-011 / ADR-0007; DEC-014 / ADR-0008; DEC-021 / ADR-0009; DEC-008 / ADR-0011; DEC-009 / ADR-0012; DEC-023 / ADR-0013.

## Questão

Como gerar encontros que respeitem a ecologia, a narrativa e os perigos efetivos de cada região sem que todo inimigo acompanhe automaticamente o nível dos jogadores?

## Alternativas consideradas

- **A — Encontros regionalmente fixos:** mantém perigo e contexto, porém menos flexível à composição do grupo.
- **B — Diretor adaptativo com limites regionais:** combina orçamento de risco/contexto e seleção de criaturas por regras com limites fixados pela região.
- **C — Escalonamento global:** dificulta a percepção de progresso e pode violar o cenário.

## Decisão aprovada — opção B

1. **Identidade regional primeiro:** cada região terá bioma/áreas, facções, épocas, espécies e perigos plausíveis, limites mínimos e máximos de encontro, exceções e ameaças especiais derivadas de fatos persistidos ou curados. A composição não muda arbitrariamente para acompanhar nível.
2. **Dificuldade contextual, não garantia de vitória:** dentro dos limites regionais, o Encounter Director selecionará encontros de acordo com a força e as condições do grupo. Encontros difíceis, evitáveis ou perigosos demais podem continuar existindo e devem ter possibilidades coerentes de detecção, fuga, contorno, diplomacia ou preparo quando aplicável. Não há promessa de balancear todo confronto para ser vencível.
3. **Código determinístico primeiro:** tabelas, regras, pesos, cooldowns e sementes rastreáveis selecionam *se*, *quando*, *onde* e *quais* criaturas aparecem. LLM não escolhe resultados mecânicos nem é invocado por tick, por criatura ou por encontro simples. Pode ser usado sob demanda para contextualização narrativa validada.
4. **Compatibilidade AD&D 2e:** parâmetros observáveis de BG2:EE (por exemplo, THAC0, CA, salvaguardas, magias, resistências, ataques por rodada, efeitos e scripts táticos) orientam avaliação de perigo. CR de 3e/5e não é equivalente diretamente. Algoritmo e pesos concretos dependem de SPECS e testes.
5. **História e ecologia persistentes:** fatos de Forgotten Realms por época, ações confirmadas dos jogadores, presença de facções, reputações, mudanças regionais e consequências anteriores podem alterar o conjunto de criaturas disponíveis. O sistema não cria/ressuscita um inimigo único já eliminado ou realiza eventos mecânicos offscreen sem política válida.
6. **Autoridade do motor e sincronização:** a saída do diretor é apenas **proposta** de encontro. Spawns, posições, inventário e consequências dependem da validação e confirmação mecânica do host/bridge (DEC-011); comandos desconhecidos devem permanecer `UNCERTAIN` até reconciliação. Testes multiplayer são obrigatórios.
7. **Antifarming e orçamento:** controlar repetição, densidade de spawns, frequência por região, recompensas e limites de processamento. Não criar recompensas diretamente fora do motor nem permitir duplicação por retry, reload ou reconexão.
8. **Separação dos modos:** alterações de encontros do Living World não modificam silenciosamente modo Original nem campanhas com perfil diferente. Controle do diretor e suas versões são associados à campanha.
9. **Caminhos de evolução:** regras e dados de encontro serão desacoplados do agendador de combate, permitindo testes no RTwP atual e no futuro turno opcional se este passar pelos gates da DEC-005-T.

## Fatos confirmados x propostas

Aprova-se a **política arquitetural**, não a implementação ou números. Não foram escolhidos multiplicadores, nível mínimo/máximo por região, lista de monstros, probabilidades ou fórmulas finais de dificuldade.

## Modelo conceitual

```text
Region State + Time/Canon + World Events + Party Snapshot + Ruleset
                         |
              Encounter Eligibility
            (bioma, facção, raridade,
              condições e proibições)
                         |
           Deterministic Threat Planner
          (orçamento limitado, RNG seed,
           cooldowns e ecologia regional)
                         |
              Encounter Proposal
                         |
        Security + Authority + Multiplayer Gate
                         |
                   BG2:EE Host
                         |
          Confirmed Outcome / Reconcile
                         |
                Persistent Event Log
```

### Contratos candidatos (não SPECS)

`RegionEncounterProfile`: `region_id`, `era`, `biome`, `factions`, `allowed_creature_ids`, `threat_bands`, `exception_rules`, `spawn_constraints`, `cooldowns`, `source_provenance`, `profile_version`.

`PartyThreatSnapshot`: `party_id`, `level_summary`, `effective_capabilities`, `hp_resources`, `spell_resources`, `equipment_capabilities`, `recent_encounters`, `campaign_ruleset`, `measurement_timestamp`.

`EncounterProposal`: `proposal_id`, `campaign_id`, `world_revision`, `region_id`, `profile_version`, `seed`, `creatures`, `spawn_conditions`, `risk_label`, `warnings`, `preconditions`, `expires_at`.

`EncounterOutcome`: `proposal_id`, `host_receipt`, `status`, `confirmed_creatures`, `confirmed_rewards`, `world_revision`.

Esses nomes e campos são propostas de desenho; não são contratos executáveis já suportados.

## Critérios de aceitação candidatos

1. O diretor jamais adiciona uma criatura incompatível com as restrições explícitas de região/época sem exceção curada e registrada.
2. Alterar a força do grupo pode mudar a composição **dentro** dos limites regionais; não deve converter automaticamente qualquer região em escala global de níveis.
3. Um local deliberadamente perigoso continua perigoso para grupos fracos; o sistema não cria vitória garantida.
4. Com os mesmos dados/seed/versões, a **proposta** de encontro é reproduzível; aleatoriedade e resultados do motor exigem testes separados.
5. O orçamento de spawn, cooldown e proteção contra duplicações evita encontros/recompensas repetidos indevidamente após reload/retry.
6. Em dois clientes, só o host confirmado altera o estado mecânico; solicitações incertas são reconciliadas.
7. O sistema não executa chamadas LLM durante o cálculo mecânico do encontro nem cria NPC fora da allowlist.
8. A remoção/retorno de NPCs únicos respeita história confirmada, cronologia e regras específicas de ressurreição.
9. A política de encontro permanece compatível com o modo clássico, independentemente da POC TBC.
10. Saves e campanhas distintas preservam perfis/versionamentos de região e regras sem alterações implícitas.

## Riscos e contramedidas

- **Escalonamento oculto/artificial:** registrar limites regionais, manter ameaças independentes do grupo e permitir progressão real.
- **Dificuldade impraticável ou excessivamente trivial:** testes de combate simulados/observados em amostras de grupos variados; revisão humana de regiões especiais.
- **Recompensas duplicadas ou spawn abusivo:** idempotência, limites por área, audit trail e confirmação do host.
- **Regiões e criaturas de mods com mecânica diferente:** inventário por recurso/versão e adaptação condicionada a testes.
- **Incompatibilidade com lore/história:** catálogo com proveniência e validação de época, facções e estados confirmados.
- **Sincronização de multiplayer:** POC de spawn em 2 clientes como gate; não alegar que já funciona.

## Consequências e pendências

**Benefícios:** mantém o mundo crível e a progressão significativa, aproveita criaturas e estatísticas originais, cria variedade com custo controlável e sem inferência permanente.

**Custos:** curadoria por região/época, maior necessidade de telemetria de encontros e testes com composições heterogêneas, especialmente em mods com recursos importados.

**Pendente de SPECS:** métricas, fórmulas, limites de orçamento, níveis de ameaça, proteções de encontros únicos, recompensas, listas de criaturas e UX de avisos ao jogador. O modo opcional de turnos permanece condicionado a POCs (ADR-0017).

**Próxima decisão arquitetural:** **DEC-010 — estratégia de conteúdo**: criado/curado previamente versus geração procedural em runtime versus arquitetura híbrida.
