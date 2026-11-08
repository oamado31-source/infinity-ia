# Encounter Director — limites regionais e adaptação contextual

**Discovery v2.1 — rascunho técnico; NÃO é SPEC pronta nem código de produção.**  
**Decisão vinculante:** DEC-005-E / ADR-0019 (opção B, aprovada em 2026-11-06).

## Objetivos

- Preservar **perigos naturais do cenário** e o significado de viajar de regiões tranquilas para zonas de alto risco.
- Escolher variantes de encontro com base no grupo sem tornar cada criatura uma cópia escalada do nível do jogador.
- Respeitar época de Forgotten Realms, facções, histórico do grupo e eventos persistentes.
- Manter encontros mecânicos sob código + host do BG2:EE, com narrativas de IA apenas sob demanda.
- Suportar o multiplayer cooperativo e o modo RTwP desde o primeiro protótipo.

## Camadas lógicas

1. **Contexto:** calendário DR, mapa/área, biome, facções, distúrbios, presença de criaturas únicas, fontes e exceções históricas.
2. **Elegibilidade:** aplicar bloqueios rígidos (ex.: espécie ausente, indivíduo já morto, local inacessível, evento futuro, flag incompatível) antes de cálculos de risco.
3. **Força efetiva do grupo:** estimativa a partir do estado observado do host e composição: números, níveis, classes, HP, equipamentos, repertório de magias, efeitos, resistências e condições recentes. **Não inventar atributos não observados**; quando parcial, aplicar política conservadora.
4. **Orçamento de encontros:** sorteio limitado com seed rastreável, cooldowns e riscos regionais, sem comprometer a ecologia nem reduzir todas as ameaças ao nível do grupo.
5. **Contextualização:** diálogo/rumor/opção de evitar combate; LLM eventual somente para texto aberto, sem arbitrar estatísticas.
6. **Proposta e execução:** validador de integridade, allowlist, ponte, host e confirmação para cada spawn/recompensa/remoção.
7. **Persistência:** registrar proposta, estado `CONFIRMED|REJECTED|UNCERTAIN`, evidência e revisão do mundo; efeitos indiretos dependem de confirmação.

## Matriz conceitual de risco

| Tipo de região | Limites estruturais | Exemplo de comportamento do diretor |
|---|---|---|
| Estrada patrulhada | Predominância de viajantes, fauna e ameaças locais coerentes | O grupo experiente não transforma bandidos comuns automaticamente em monstros lendários |
| Floresta de ameaça variável | Encontros comuns, raros e perigosos conforme ecologia e eventos | Grupo pouco preparado tende a encontros menores, mas pode detectar perigos extremos |
| Zona de risco alto | Ameaças poderosas persistem por história/local | Iniciantes devem poder evitar ou reconhecer perigo quando narrativamente plausível; vitória não garantida |
| Masmorra/território de facção | Preservar guardas, bosses, recursos especiais e estado da facção | Não trocar o líder por inimigo genérico apenas para ajustar dificuldade |
| Regiões com evento histórico | Configuração variável por tempo DR e resultados do mundo | Invasão e epidemia mudam elegibilidade conforme fatos e datas verificadas |

Os exemplos são **cenários hipotéticos**, não afirmações de populações específicas de cada área do cânone.

## Perfis: categorias de dados (não valores fechados)

- Identidade: identificador da área, mapa, campanha, época, origem do mod e versão.
- Ecologia: tags de criatura, grupos/facções, comportamento e disponibilidade por cronologia.
- Perigo: classificação local, encontros raros e ameaças fixas que não escalonam.
- Adaptatividade: janela permitida de variações de densidade, composição e frequência, sem substituições que violem restrições rígidas.
- Controles: orçamento de spawn, cooldown, limite de processamento e condições de repetição.
- Evidência: fontes históricas de regras, presets curados e registros do host para mudanças emergentes.

## Regras de balanceamento AD&D 2e

A avaliação deve levar em conta **THAC0, Classe de Armadura, ataques por rodada, HP, salvaguardas, magias, resistências, imunidades, efeitos e composição dos grupos**; não somar níveis cegamente. Não importar CR da 3ª/5ª edição como conversão automática. Fórmulas, pesos, cobertura estatística e thresholds exigem teste com dados reais da instalação.

## Exemplo ilustrativo — contexto idêntico, grupos diferentes

**Região:** floresta hipotética com fauna local, bandidos e uma ameaça excepcional fixa.

- **Grupo iniciante:** dentro dos limites ecológicos, pode ser apresentado a patrulha pequena, trilhas de evasão e sinais de perigo.
- **Grupo experiente:** encontra patrulhas maiores, mais organizadas ou consequências de suas ações anteriores, mas não automaticamente lobos com atributos de dragões.
- **Ameaça excepcional já existente:** permanece parte da região para ambos; se encontrada, oferece riscos efetivos. Quando possível, o jogo permitirá perceber, negociar, evitar ou fugir.

## Dependências técnicas e gates

- BG2:EE baseline com versões verificadas (DEC-003).
- EEex + bridge controlada não presumidos compatíveis antes de POCs.
- Spawn, scripts de IA, recompensas e efeitos mecânicos dependem da autoridade do host (DEC-011).
- Perfis e resultados por campanha (DEC-008), tempo e estado DR (DEC-009/022/023), atividade de região (DEC-021).
- Compatibilidade de criaturas importadas dos mods deve ser testada separadamente; não presumir equivalência de edições.
- Turnos individuais opcionais continuam sob gate GemRB-TBC/EEex/multiplayer (DEC-005-T).

## Testes candidatos (nenhum executado)

| ID | Cenário | Aceite pretendido |
|---|---|---|
| ENC-01 | Mesmo contexto + seed + versões | Proposta de encontro reprodutível sem LLM |
| ENC-02 | Grupo de nível baixo em região perigosíssima | Perigo permanece alto, com sinais/evasão quando plausível, sem garantia de vitória |
| ENC-03 | Grupo avançado em estrada segura | Inimigos comuns não ganham atributos artificialmente gigantescos |
| ENC-04 | Região com NPC único já eliminado | Diretor não cria duplicata sem acontecimento válido de retorno |
| ENC-05 | Cronologia/facção alterada por campanha | Candidatos a encontro refletem o estado confirmado |
| ENC-06 | Reload e retry após resposta `UNCERTAIN` | Sem spawn ou loot duplicado |
| ENC-07 | Dois clientes e host | Criaturas, mortes, recompensas e estado convergem depois de confirmação |
| ENC-08 | Modo Original e Living World | Separação de estado e regras |
| ENC-09 | Falha de LLM ou rede | Seleção e execução mecânica normal continuam |
| ENC-10 | Encontro extremo perto de área pública | Cap de densidade, cooldown e estabilidade medidos sob load |
| ENC-11 | Criatura importada de IWD/NWN | Estatísticas/efeitos verificados no BG2:EE antes de liberação |
| ENC-12 | Turnos opcionais indisponíveis | Diretor opera no RTwP sem depender de TBC |

## Itens que não foram decididos

- Quais regiões e bestiários serão curados primeiro.
- Algoritmo/métrica de poder efetivo do grupo e coeficientes finais.
- Spawn aleatório por tempo ou passos, frequência e formas de aviso ao jogador.
- Relação entre CR/importações, loot e XP; política de prevenção de farming.
- Parâmetros e limites máximos/mínimos por região.
- Política de geração de áreas, quests e masmorras (DEC-010, próxima decisão).

## Integração com DEC-069/C — Discovery v6.5

DEC-069 distingue etapas de viagem de encontros reais: o diretor pode propor uma oportunidade regional, mas não produzir combate/spawn/ferimentos fora de cena por inferência; política específica de incidentes segue DEC-070.

**Status:** política arquitetural, não implementada; testes/POCs reais pendentes. Referência: `docs/decisions/ADR-0064-viagens-hierarquicas-e-presenca-mecanica-verificada-de-npcs.md` e `docs/69-itinerarios-regioes-tempo-e-presenca-mecanica-de-npcs.md`.

## Integração com DEC-070/C — Discovery v6.6

DEC-070 formaliza geração de incidentes em rotas como proposta, com LOW somente narrativo sob allowlist, MEDIUM condicionado a gates e HIGH fail-closed. O diretor regional não pode transformar perigo de estrada em combate vencido ou spawn confirmado.

**Status:** apenas desenho arquitetural; referência: `docs/decisions/ADR-0065-incidentes-de-viagem-por-risco-e-confirmacao-segura.md` e `docs/70-incidentes-de-viagem-classificacao-por-risco-e-resolucao-segura.md`. Testes/POCs não executados.

## Integração DEC-071/C — encontro local condicionado (Discovery v6.7)

Encontros propostos por DEC-005-E podem receber DEC-071 apenas quando origem, party e área são elegíveis e a engine confirmou capabilities de evento local por build. O diretor não materializa atores nem resolve incidentes HIGH sozinho; exclusividade offscreen/local por `incident_id`.

**Referências:** ADR-0066, `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md`. Implementação e POCs pendentes; decisões DEC-060–070 preservadas.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

O diretor DEC-005-E pode propor composição DEC-072 usando catálogo e parâmetros curados, sem presumir presença física; integridade de área/quests/scripts e capacidade por build precedem handoff DEC-071.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.

## Integração DEC-073/C — pós-encontro e cleanup seguro (Discovery v6.9)

Diretor de encontros propõe encerramento e recursos, mas não define que uma remoção foi executada; integridade mecânica pelo host.

**Referências:** `docs/decisions/ADR-0068-propriedade-e-persistencia-seletiva-pos-encontro-com-limpeza-segura.md`, `docs/73-ciclo-de-vida-pos-encontro-ownership-efeitos-e-limpeza-segura.md` (**50 testes candidatos NÃO EXECUTADOS**). DEC-060–072, incluindo separação física anual, preservadas; não há capacidade BG2:EE/EEex/multiplayer demonstrada.

## Integração DEC-084/C — Discovery v8.0

Diretor regional não materializa perseguidores apenas porque foi criada uma hipótese de retaliação; ambiente, ecologia, risco, host e capability condicionam encontros.

**Referências:** `docs/decisions/ADR-0079-protecao-ativa-contextual-contra-ameacas-e-retaliacoes-a-fontes.md`, `docs/84-protecao-ativa-de-testemunhas-avaliacao-de-ameacas-abrigo-escolta-e-reconciliacao.md`; DEC-060–083 preservadas, lore fisicamente anual. **72 testes candidatos T084-* NÃO EXECUTADOS; nenhuma capability BG2:EE/EEex/multiplayer comprovada.**

## Integração DEC-089/C — verificação de informes (Discovery v8.5)

Diretor de encontros não agenda emboscada por rumor sem evidência/competência/risco; informes inconclusivos podem motivar investigação narrativa, não spawn automático.

**Precedência:** decisões DEC-060–088 preservadas; fato canônico e relatório privado nunca são confundidos. Arquitetura ainda não implementada; 84 testes candidatos não executados. Não presumir POCs BG2:EE/EEex nem autoridade epistemológica da LLM.

## Integração DEC-091/C — Discovery v8.7

Encounter director pode receber proposta validada, mas encontro real exige templates/capability e confirmação host; um observador não cria combate por rumor.

**Estado:** política de planejamento aprovada somente como arquitetura; sem execução de testes, bridge funcional ou capacidade BG2:EE/EEex demonstrada. ADR-0086/documento 91; decisões DEC-060–090 preservadas.

## Integração DEC-092/C — monitoramento e replanejamento (Discovery v8.8)

Mudança de época/conteúdo para replanejamento exige Knowledge Pack pinado e data real do evento; não antecipar informações do futuro.

**Estado:** política arquitetural aprovada; testes de host/EEex/multiplayer e mecanismos de pausa/cancelamento não executados. DEC-060–091/ADRs predecessores preservados.

## Integração DEC-095/C — Discovery v9.1; matriz DEC-096 somente proposta

Regras de encontro dependentes de evento histórico seriam propostas DEC-096 após fase/região/risco e só materializadas via templates/capabilities; a matriz nunca gera spawns automaticamente.

**Estado:** DEC-095/C aprovada apenas como arquitetura; 96 testes T095-* candidatos NÃO EXECUTADOS. **DEC-096 EM ABERTO**, sua matriz histórica é proposta técnica sem execução no jogo. DEC-060–094 e ADRs anteriores preservados.

## Integração DEC-096/C — Discovery v9.2

DEC-096/C não atribui ao PC atual o papel de protagonista histórico nem dispara flags/quest originais por coincidência temporal. Baseline/campaign overlay isolados.

**Contrato vigente:** ADR-0091 e doc. 96 consolidado; **aprovado apenas como arquitetura**, 100 testes T096-* candidatos NÃO EXECUTADOS. As DEC-060–095 e ADRs anteriores permanecem preservados.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

NPCs, encontros e recursos que compõem o cenário precisam preservar ownership por instância e quotas; critério narrativo não autoriza despawn.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Ano-base 1369 DR e fontes oficiais não podem ser alterados por estados internos secretos de quests.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração transversal — DEC-103/C (2026-11-07)

**Integração DEC-103/C (Discovery v9.9; ADR-0098):** o marco de quest reconciliado (DEC-102) gera apenas **propostas** por rulesets curados, não altera NPC, spawn, inventário, recursos ou script. Exigir autorização, ownership DEC-099, build/capability, limites/riscos, reserva e receipts do Action Gateway para efeitos mecânicos; `DISPATCHED/UNCERTAIN` não autoriza repetição. Ledger/outbox e dedup por ocorrência/branch/lineage; reentrada, save/load e operações concorrentes não duplicam resultados. Transmissão de notícia é canal separado com prova de entrega. Ver doc. 103. **POCs reais pendentes.**
