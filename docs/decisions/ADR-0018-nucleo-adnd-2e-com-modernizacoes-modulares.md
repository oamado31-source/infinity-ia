# ADR-0018 — Núcleo AD&D 2e com modernizações modulares

- **Decisão:** DEC-005-R — edição das regras
- **Estado:** **APROVADA — opção B**
- **Data da aprovação:** 2026-11-06
- **Domínio:** regras, compatibilidade mecânica, evolução modular e multiplayer.
- **Origem:** decisão expressa do idealizador do Infinity AI nesta conversa.
- **Referências cruzadas:** DEC-005-T / ADR-0017 (modo de combate), DEC-005-E (diretor de encontros — aberta), DEC-001 (cooperativo), DEC-003 (integração progressiva), DEC-011 (autoridade do host), DEC-014 (código primeiro).

## Contexto

A instalação inicial terá Baldur's Gate II: Enhanced Edition como motor-base, com aproveitamento progressivo de EET, conteúdos de Icewind Dale e NWNForBG. Essa base usa regras derivadas de **AD&D 2ª edição**, enquanto Neverwinter Nights / Icewind Dale II utilizam regras associadas à 3ª edição. Converter integralmente BG2:EE para outra edição aumentaria substancialmente o esforço e a incompatibilidade com conteúdos existentes.

A escolha anterior DEC-005-T estabeleceu o **desejo de turnos individuais opcionais**, condicionado a POCs com EEex e multiplayer. **Turnos individuais não implicam conversão de edição.**

## Decisão aprovada

1. **O núcleo das regras permanece AD&D 2e conforme implementado em BG2:EE**, respeitando suas particularidades e adaptações de videogame. A especificação não implica reprodução perfeita do RPG de mesa em todos os detalhes.
2. **Modernizações serão módulos independentes, opcionais e versionados**, especificados em SPECS/Features separadas; esta decisão **não aprova antecipadamente nenhum módulo específico**.
3. **Baseline preservado:** com todos os módulos opcionais desativados, a mecânica deverá reproduzir o comportamento observado e validado no BG2:EE de referência, dentro dos limites de compatibilidade comprovados.
4. **Separar camadas de mudança:** apresentação/UX, comportamento e regras mecânicas. Mudanças em dados, probabilidades, cálculos, classes, magias, itens e efeitos têm exigências de validação mais rigorosas do que mudanças visuais/informativas.
5. **Declaração por campanha:** configurações mecânicas relevantes, versões de módulos e perfil de regras devem ficar vinculados à campanha e ao save. Regras não podem ser trocadas silenciosamente durante um combate ou em um save existente.
6. **Multiplayer consistente:** a mesma sessão deve executar um perfil coerente em todos os clientes; o host permanece autoritativo em resultados mecânicos (DEC-011). A capacidade de validar/sincronizar módulos via BG2:EE/EEex ainda depende de POCs.
7. **Código primeiro:** cálculos, decisões táticas padrão, permissões e alterações de regras são determinísticos/testáveis; LLM não se torna árbitro mecânico e não decide resultados de dados, dano, ataques ou custos.
8. **Sem conversão completa para D&D 3e/5e neste marco.** Qualquer proposta posterior de conversão abrangente exige decisão nova e análise de impacto (ADR), sem revogar implicitamente a presente.

## Perfis lógicos candidatos (não são funcionalidades implementadas)

| Perfil | Significado | Situação |
|---|---|---|
| `legacy_2e` | Baseline AD&D 2e do BG2:EE, sem modernizações mecânicas ativas | **Alvo inicial aprovado** |
| `modernized_2e` | Baseline com seleção explícita de módulos compatíveis, após testes | **Possibilidade aprovada; módulos não escolhidos** |
| `turn_based_2e` | `legacy_2e`/módulos compatíveis com turnos individuais, se viável | **Bloqueado pelos gates da ADR-0017** |

Os nomes são propostos para contratos futuros e podem mudar antes da SPEC. Não afirmar que esses perfis já existem no jogo.

## Contrato mínimo candidato para cada módulo

- `module_id`, `version`, `scope`, `required_engine`, `required_mods`, `dependencies`, `conflicts`;
- recursos afetados: `class`, `spell`, `creature`, `item`, `effect`, `combat_scheduler`, `ui`, `save_state`;
- condições de ativação, limitações multiplayer, migrações e política de desativação/rollback;
- observabilidade e hash/identificação do conjunto de regras para impedir divergência entre clientes;
- testes de regressão da mecânica original, save/load e integração por etapas.

Esses campos são **contratos candidatos**, não schemas aprovados.

## Regras de governança

- Nenhuma modernização mecânica entra na baseline sem SPEC aprovada, prova técnica, testes e rollback.
- Modernização sem impacto em regras (por exemplo, texto de ajuda) não pode ser confundida com conversão de edição.
- A ordem e a compatibilidade de mods da DEC-003 prevalecem sobre a ativação de módulos.
- Alterações dependentes do GemRB-TBC não são consideradas compatíveis automaticamente com BG2:EE + EEex.
- CR das edições recentes não substitui o balanceamento de AD&D 2e: a política concreta de desafio é **DEC-005-E, ainda em aberto**.
- Em caso de conflito/erro, preferir manter `legacy_2e` estável ou impedir abertura de uma campanha incompatível, em vez de reescrever saves.

## Critérios de aceitação candidatos para SPECS

1. Uma partida sem módulos opcionais mantém as estatísticas e comportamentos esperados do baseline (THAC0/AC, salvaguardas, ataques por rodada, efeitos, magias, itens).
2. Alterar configuração de módulos não modifica o modo Original nem saves existentes sem migração/consentimento explícitos.
3. Conflitos e dependências entre módulos são detectados antes de abrir a campanha.
4. Módulos diferentes entre host e cliente não produzem combate divergente: sessão é bloqueada/compatibilizada por protocolo validado.
5. O mesmo save reaberto conserva as versões e configurações necessárias ao seu comportamento.
6. Regressões das áreas/sistemas de EET/IWD/NWNForBG são executadas por etapas quando aplicável, sem presumir compatibilidade.
7. Modo RTwP clássico permanece utilizável mesmo sem implementação de turnos individuais.
8. Eventos mecânicos continuam confirmados pelo host; LLM não pode alterar regras nem confirmar ações diretamente.

## Limitações e pendências

- Não há decisão aprovada sobre **quais** modernizações serão implementadas primeiro, nem suas interfaces.
- Não há comprovação de suporte técnico a overlays/alterações mecânicas por EEex no multiplayer.
- Não há escolha aprovada de fórmula de dificuldade, equivalência de CR ou escalonamento de criaturas: **DEC-005-E aberta**.
- O modo de turnos opcionais mantém as condições técnicas da ADR-0017; esta ADR não as remove.
- Regras de compatibilidade e migração de saves serão detalhadas após pesquisa da instalação real.

## Consequências

**Positivas:** mantém o maior conjunto de conteúdos reutilizáveis, preserva a opção de modernização por etapas, limita o risco de conversão profunda e permite testes comparativos claros.

**Negativas:** surgirão potencialmente diferentes perfis de regras e novos testes combinatórios; alguns módulos de modernização podem ser inviáveis no motor proprietário; não se obtém D&D 5e completo apenas com um pacote de módulos.

**Revisão da decisão:** permitida somente com novo ADR e evidências técnicas; não deve ser substituída automaticamente pelo resultado de uma POC experimental.
