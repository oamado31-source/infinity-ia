# ADR-0011 — Persistência híbrida e integração da cronologia de Forgotten Realms

- **Decisão associada:** DEC-008
- **Estado:** **APROVADA — opção C, com adendo obrigatório de cronologia oficial**
- **Data de aprovação:** 2026-11-06
- **Domínio:** persistência, event log, snapshots, lore histórica, conhecimento e consequências narrativas
- **Fonte da decisão:** escolha expressa do idealizador nesta conversa.
- **Relações:** DEC-011 / ADR-0007 (autoridade mecânica e narrativa); DEC-014 / ADR-0008 (regras primeiro); DEC-019 (segredos); DEC-020 (revisões); DEC-021 (simulação por níveis); DEC-022 (relógio híbrido); **DEC-009 ainda aberta** (política de canon e desvios da história oficial).

## Contexto

O Living World deve preservar o que aconteceu em dezenas de sessões, incluindo relações entre NPCs e jogadores, estados de regiões, resultados de missões e consequências duradouras. O mundo também deverá reagir a acontecimentos datados da história de Forgotten Realms: mortes relevantes, sucessões, guerras, crises políticas, ataques ou transformações regionais. Uma notícia pode produzir diálogos, rumores, novas missões, alterações de relações entre facções e do nível de instabilidade de uma região.

A integração de mapas de Baldur's Gate, Icewind Dale e adaptações de Neverwinter Nights não implica que todas as campanhas originais coexistam no mesmo ano. O Living World terá **sua própria época/calendário por campanha**, vinculado à cronologia lore em DR. Datas, locais e fontes deverão ser verificáveis.

## Decisão aprovada

1. **Persistência híbrida:** guardar (i) estado materializado de consulta rápida e snapshots recuperáveis e (ii) um histórico durável de eventos relevantes com origem, causalidade, identificação e versão. A implementação exata do banco permanece para SPECS técnicas; SQLite é candidato, não escolha fixada.
2. **Eventos de cronologia Forgotten Realms como entrada de primeira classe:** manter um catálogo versionado de acontecimentos do lore, rastreáveis a referências documentadas. O relógio da campanha e a relevância regional determinam quando podem influenciar o mundo. Não antecipar no mundo do jogo acontecimentos futuros.
3. **Separar quatro conceitos:** (a) `LoreEvent` — descrição fundamentada de fato histórico atribuído a uma fonte; (b) `WorldEvent` — acontecimento confirmado naquela campanha; (c) `EventProposal` — previsão/criação sugerida pela IA; (d) `WorldProjection` — estado derivado e rapidamente consultável. Fonte histórica não é automaticamente ação mecânica executada no jogo.
4. **Repercussões situadas no mundo:** efeitos como rumores, diálogos, tarefas, variação de tensão regional ou ações de facções devem respeitar data, geografia, causalidade, conhecimento individual dos NPCs, estado do grupo, histórias dos personagens e salvaguardas das decisões anteriores. O fato de a IA ter acesso ao catálogo não autoriza cada NPC a conhecer instantaneamente o evento.
5. **Código primeiro:** ativação por data, pré-condições, chegada de notícias, idempotência, atualizações numéricas e regras de facção são preferencialmente determinísticas. LLM local só entra sob demanda para produzir variações narrativas, diálogos ou ganchos não resolvidos por regras/templates. LLM não confirma mortes, altera saves ou executa Lua arbitrário.
6. **Autoridade preservada:** o host BG2:EE confirma o estado mecânico. Efeitos derivados do lore sobre spawn, inventário, combate, NPCs ou áreas só viram fatos mecânicos após validação e confirmação conforme DEC-011; o catálogo não ordena execução unilateral.
7. **Conflitos e linhas alternativas:** conservar proveniência e sinalizar discordâncias entre fontes, datas aproximadas, campanhas originais e ações dos jogadores. **Não** aprovar nesta decisão se todo evento oficial é obrigatório/imutável, se o mundo pode divergir, nem como resolver conflito de canon; essas políticas integram a próxima **DEC-009**.
8. **Modos isolados:** apenas Living World usa a persistência narrativa; saves e andamento do modo Original não podem ser alterados.
9. **Dados e direitos:** manter metadados, referências e resumos próprios minimamente necessários; não distribuir acervos integrais de livros protegidos ou recursos proprietários como parte do pacote de código sem autorização aplicável.

## Evidência e fontes de referência

- *The Grand History of the Realms* (Wizards of the Coast, 2007; Ed Greenwood e Brian R. James) é uma referência histórica relevante; conferir material e trechos em cópias obtidas legitimamente.
- Forgotten Realms Wiki, política comunitária de canon: https://forgottenrealms.fandom.com/wiki/Forgotten_Realms_Wiki:Canon — reconhece divergências e hierarquias de fontes; a própria wiki não constitui uma autoridade oficial que elimine todas as contradições.
- Visão cronológica de jogos (referência secundária): https://forgottenrealms.fandom.com/wiki/List_of_video_games_in_chronological_order — BG1 em 1368 DR, BG2 em 1369 DR, NWN em 1372 DR (pode haver eventos com datas mais específicas ou arcos que cruzem anos).
- Referência ao calendário/DR: https://www.realmshelps.net/faerun/lore/life/time.shtml (material de referência não substitui fonte primária).

## Consequências

### Benefícios
- Mundo reage a eventos históricos e produz consequências persistentes entre visitas.
- Mantém rastreabilidade da origem dos acontecimentos e dos motivos de cada efeito.
- Permite reprocessamento controlado e diagnóstico, além de isolamento entre campanhas.

### Custos e riscos
- Versões, fontes e cronologias divergem. Um mapa de NWN importado para o BG não pode importar indiscriminadamente o estado histórico da campanha NWN.
- Falta de data exata (`ano`, `mês`, `dia`, `intervalo`, `data disputada`) exige critérios de ativação que ainda serão definidos.
- Eventos oficiais de grandes consequências podem conflitar com decisões dos jogadores; não efetuar retcons automáticos nem alterações irreversíveis fora de cena por padrão.
- Eventos conhecidos pela IA podem gerar spoilers se vazarem para diálogo ou missão antes de notícias chegarem ao NPC.
- Risco de duplicar consequências ao recalcular o catch-up; exigir chaves idempotentes de ativação por campanha, evento e fase de repercussão.

## Gates e aceitação provisórios

A decisão é de arquitetura, não de implementação. Para aprovação das futuras SPECS/POCs deverá ser demonstrado:

- Registro de um `LoreEvent` com fonte, precisão temporal, locais afetados e ID único sem impactar imediatamente o save.
- Em uma campanha **antes** da data autorizada, NPCs não tratam o evento como já ocorrido e não recebem spoilers indevidos.
- Ao cruzar a data, a mesma ocorrência histórica é ativada **uma vez** na campanha, com repercussões válidas e rastreáveis.
- Em região afastada, um rumor não chega ao NPC antes da propagação prevista; dois NPCs podem ter níveis diferentes de conhecimento.
- Com retorno ao save, a mesma notícia não duplica uma missão ou entrega recompensa novamente.
- Se a IA sugerir mudança mecânica sem confirmação do host, a consequência correspondente fica pendente, sem registrar sucesso.
- Com duas campanhas em épocas diferentes, a timeline de uma não contamina a outra.
- Divergências em lore são registradas como conflitos a resolver e não modificam silenciosamente fatos confirmados.

## Questões deliberadamente não decididas (DEC-009 e SPECS)

1. Quais fontes/edições prevalecem quando livros, jogos e materiais posteriores discordam?
2. Em que grau um acontecimento oficial é fixo, condicional ou adaptável às ações dos jogadores?
3. Qual o ano inicial e a precisão do calendário de cada Living World?
4. Qual o comportamento quando uma fonte traz apenas o ano ou uma faixa aproximada?
5. Como definir velocidades de propagação de notícias, raio de impacto e limites de instabilidade?
6. Qual estrutura de persistência/banco, serialização, migrações, backups e retenção utilizar (DEC-018)?
7. Como a época do Living World se relaciona às campanhas/mods importados e à data dos seus NPCs?

**Próxima discussão:** DEC-009 — política de canon, divergência e consequências da cronologia oficial.
