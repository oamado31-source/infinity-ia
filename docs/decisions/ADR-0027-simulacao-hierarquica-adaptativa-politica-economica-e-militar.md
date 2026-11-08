# ADR-0027 — Simulação hierárquica adaptativa política, econômica e militar

- **Decisão:** DEC-032
- **Status:** **APROVADA — opção B**
- **Data:** 2026-11-06
- **Domínio:** macroeconomia, política, diplomacia, logística, facções, simulação militar e desempenho.
- **Origem:** escolha expressa do idealizador com adendo de investigar jogos como Rome: Total War e congêneres para reaproveitar mecanismos relevantes.
- **Referências cruzadas:** DEC-031 (facções/cânone expandido), DEC-021 (ACTIVE/NEAR/DISTANT/DORMANT), DEC-022 (relógio e catch-up), DEC-008/009/023 (persistência, cânone e 1369 DR), DEC-011/012/027 (host, gateway, risco), DEC-014 (código primeiro), DEC-028/029/030 (conhecimento, rumores, reputação), DEC-005-E (encontros).

## Contexto e motivação

Organizações, cidades e regiões devem reagir a economia, guerras, alianças, comércio, escassez, recrutamento e acontecimentos sem exigir simular cada pessoa, objeto e soldado do mundo. Ao mesmo tempo, o Infinity AI é um RPG baseado no BG2:EE, **não um novo simulador de batalhas em larga escala**.

## Decisão vinculante

1. **Adotar simulação hierárquica adaptativa por relevância**, mais detalhada nas regiões e facções próximas/relevantes aos jogadores, e agregada/distante ou suspensa sob demanda nas demais.
2. **Separar camada estratégica externa da camada tática do BG2:EE.** Modelos agregados de território, rotas, produção, riqueza, abastecimento, tropas, moral, relações e objetivos não são automaticamente entidades/objetos do jogo. Os encontros locais continuam com regras BG2:EE/AD&D 2e, Encounter Director e autoridade do host.
3. **Agentes e facções usam metas, prioridades e cálculo de alternativas por regras determinísticas**, com IA local apenas para linguagem, negociação e narrativa quando apropriado. Nada de LLM por organização por tick.
4. **Utilizar um grafo regional historicamente curado** para distância, estradas, rios, portos, comércio, comunicação, suprimentos e movimentações agregadas; criar conexões apenas com fonte ou aprovação de conteúdo original, sem presumir mapas/mods instalados.
5. **Registrar causalidade:** efeitos de interrupção de rotas podem afetar abastecimento e comércio; tensão econômica pode alimentar interesses políticos; decisões de facção podem originar missões e encontros elegíveis. Não gerar efeitos mecânicos sem gateway/recibo do host.
6. **Cânone e história têm precedência sobre simulação não autorizada:** em 1369 DR, nenhuma regra econômica/militar pode declarar de forma automática guerras, anexações, mortes de governantes, mudanças de regime, destruições importantes ou outros fatos `HIGH` sem política especial explícita. Os acontecimentos oficiais do período são fontes para projeções compatíveis; divergências dos jogadores, se confirmadas, exigem overlay e trilha auditável.
7. **Conservar recursos e respeitar limites de capacidade** dentro do modelo que for especificado: recrutamento consome reservas autorizadas, mobilização exige condições, viagens consomem tempo, comércio exige rota válida, produção não gera dinheiro/estoque ilimitado, com regras de abstração claramente documentadas. Fórmulas e unidades exatas ainda não aprovadas.
8. **Processamento em lotes, checkpoints e seeds reproduzíveis**, conforme tempo de campanha DEC-022: `FROZEN` não avança; `PARTIAL` e `REALTIME` apenas catch-up limitado, com eventos críticos pendentes conforme DEC-027.
9. **Representação física é independente:** uma facção pode ter influência ou forças agregadas numa região sem gerar no BG2:EE soldados, construções ou mudanças de preço. Projetar no jogo requer recurso compatível, autorização, bridge e confirmação do host.
10. **Tratar jogos do gênero como referências de engenharia e design, não como motores ou códigos integráveis.** A investigação de Total War / Rome, Bannerlord, Crusader Kings, Stellaris e X4 informa padrões; copiar código, assets proprietários, dados de simulação ou assumir interoperabilidade não é autorizado por esta decisão.

## Padrões escolhidos como direção (não como fórmulas finais)

| Referência | Padrão a estudar | Política Infinity AI |
|---|---|---|
| Total War / ROME REMASTERED | Camada estratégica separada de batalha; regiões, comércio, objetivos diplomáticos | Grafo de regiões + ações estratégicas propostas + host resolve combate local |
| Mount & Blade II: Bannerlord | Produção/consumo, oficinas, caravanas, interrupção e renda militar interdependentes | Indicadores agregados e consequências de rotas; NPCs próximos só quando relevante |
| Crusader Kings III | Relações pessoais, vassalagem, legitimidade, intrigas e sucessão | Influência de líderes e vínculos entre facções, com restrições do cânone |
| X4: Foundations | Produção e oferta/demanda interligadas | Indicadores de escassez/excedentes nas regiões ativas, sem cadeia completa de cada item |
| Stellaris 4.0 | Agrupamento/abstração para reduzir cálculo em larga escala | Grupos e agregados distantes, expansão sob demanda, métricas de custo |

**Fontes verificadas:** ver `docs/31-pesquisa-comparativa-simuladores-estrategicos.md`, com URLs e limites de evidência.

## Fronteiras e invariantes

- O ambiente de teste continua **BG2:EE Windows nativo** (DEC-002/003), e o **ano-base é 1369 DR** por DEC-023.
- **Original** nunca herda a simulação do **Living World** por acidente.
- **Canônico ≠ simulado ≠ executado no host:** catálogo de lore, estado estratégico da campanha, memória narrativa e estado mecânico exigem proveniências e autoridades diferentes.
- Facção catalogada no cânone não significa tropa/NPC/mapa implantado, nem simulação ativa.
- A política de risco DEC-027 continua em vigor: `LOW` e `MEDIUM` condicionais; `HIGH` sem política especial fica bloqueado, inclusive durante catch-up offline.
- Rumores, preços e mudanças de lealdade não vazam conhecimento que um NPC não possua legitimamente (DEC-028/029/030).
- Operações incertas requerem reconciliação, nunca efeitos duplicados ou retries cegos (DEC-011/012).

## Evidência e limites

A pesquisa demonstrou **padrões públicos/documentados de design**, não acesso aos motores internos proprietários ou benchmark comparativo de desempenho. O repositório público da Feral para Rome Remastered contém documentação oficial de fórmula, economia, diplomacia e pathfinding; isso não prova reutilização técnica de código no BG2:EE.

## Consequências

**Benefícios:** mundo persistente reativo; desempenho compatível em tese com PC pessoal; narrativa com consequências econômicas/militares e comércio/regiões com identidade; cobertura progressiva de facções canônicas.

**Custos e riscos:** modelos agregados podem parecer inconsistentes quando os jogadores chegam; reconciliação de estatísticas abstratas com NPCs específicos é complexa; risco de desequilíbrio ou inflação; grande quantidade de dados de cânone; testes de calendário, recuperação, multiplayer e autorização.

## O que permanece sem aprovação/implementação

- Taxas de atualização, moeda/unidades, recursos-chave, população simulada, fórmulas de preços/recrutamento, números de tropas, escala geográfica, ranking de prioridades e política de resolução de conflitos militares.
- Aplicação de preços reais às lojas do BG2:EE, geração de patrulhas em runtime, mudança de controle de mapas, cercos ou grandes batalhas.
- Orçamento de CPU/RAM, esquema definitivo do banco e correspondência entre mapas instalados e grafo de regiões.
- Implementação ou POCs com EEex/bridge, EET, IWD, NWNForBG e multiplayer.

## Próxima decisão indicada

**DEC-033 — Como resolver conflitos militares entre facções na passagem do macro para o jogo:** apenas resolução abstrata, solução híbrida com encontros locais e participação opcional, ou simulação completa de exércitos no BG2:EE. Propõe-se a híbrida, sem pressupor autorização de eventos HIGH.
