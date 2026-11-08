# ADR-0012 — Canon principal com divergências controladas e matriz cronológica

- **Decisão:** DEC-009
- **Estado:** **APROVADA — opção C, com matriz transversal de jogos/expansões e acontecimentos de Forgotten Realms**
- **Data da decisão:** 2026-11-06
- **Fase:** Discovery; ainda não é uma SPEC de implementação.
- **Antecedentes:** DEC-004 (Original/Living World), DEC-008 (persistência híbrida e cronologia), DEC-011 (autoridade dividida), DEC-019/020 (segredos e retcons), DEC-021/022 (simulação e relógio).

## Contexto

O projeto pretende reaproveitar mapas, NPCs, monstros, itens e ambientação do ecossistema BG/EET, IWD e NWNForBG, sem impor que aventuras produzidas em séculos diferentes tenham ocorrido simultaneamente. A cronologia publicada de Forgotten Realms deve orientar a situação atual de regiões e personagens. A campanha pode divergir do histórico principal apenas por consequência causal comprovada das ações dos jogadores.

## Decisão vinculante

1. **Canon como linha de base**, não como trilho inescapável: acontecimentos históricos previstos ativam repercussões quando se tornam devidos no calendário da campanha, sujeitos à sua precisão temporal e à situação vigente.
2. **Divergências por causa confirmada**: uma intervenção de jogadores pode impedir, transformar ou precipitar um evento histórico. Registrar `CANON_BRANCH` ligado à causa, ao evento esperado e ao estado de jogo confirmado. Não substituir silenciosamente o canon nem registrar como ocorrido algo que não ocorreu.
3. **Matriz cronológica obrigatória** para jogos e expansões, cruzando época da obra original, recursos reutilizáveis, personagens/autoridades, eventos da linha histórica, diferenças por período, prioridade e fonte. Arte visual reutilizável **não** implica validade temporal de NPCs, diálogos, inventários ou missões.
4. **Analisar exceções, não refazer automaticamente todos os mapas**. O foco inicial é procurar anacronismos verificáveis: morte/vida, idade, cargos políticos, relações, facções, destruição/reconstrução, epidemias, guerras, estado de localidades, poderes divinos, questlines e viagens. O fato de uma cidade existir em dois anos não garante que seus estados sejam idênticos.
5. **Datas incertas permanecem incertas.** É proibido inventar mês/dia para evento com ano apenas, ou transformar hipótese de fã sobre datas de ToB em data oficial. Fontes contraditórias geram `SOURCE_CONFLICT` pendente de revisão.
6. **Continuidade separada por campanha.** `OfficialLoreEvent` é referência compartilhável; `CampaignEvent` e divergências pertencem a um `campaign_id`. A campanha Original mantém saves isolados da Living World.
7. **Repercussões por código primeiro**: `event -> conditions -> rules -> effects-proposed` com prioridades, cooldown, filtragem por região/rotas de notícias e status de conhecimento; LLM local apenas para texto aberto/diálogo contextual, nunca para modificar o banco ou o host diretamente.
8. **Aplicação mecânica somente após confirmação do host**, segundo DEC-011. Recusa, conflito, deduplicação e reconciliação não implicam retry cego.
9. **Fontes com rastreabilidade**: guardar obra/edição/página ou capítulo, URL de índice, confiança, precisão da data, canon-status e revisão. Obras de cenário, novelas e materiais oficiais devem ser buscados para confirmação; wikis/fóruns são índices secundários e não devem ser rotulados de fonte primária.
10. **A época inicial do Living World ainda NÃO foi escolhida.** A matriz apresenta 1372 DR como cenário ilustrativo, não como decisão aprovada. Aberta DEC-023.

## Escopo inicial da matriz

- IWD1 (1281 DR), Heart of Winter, Trials of the Luremaster, IWD2 (1312 DR).
- BG1 (1368 DR), Tales of the Sword Coast, Siege of Dragonspear (1368–1369 DR), BG2: Shadows of Amn (1369 DR; extensão até 1370 é controvertida), Throne of Bhaal (1369/1370 em fontes divergentes).
- NWN1 original, Shadows of Undrentide, Hordes of the Underdark (1372 DR).
- Módulos premium/adicionais de NWN: inventário separado com validação própria de cronologia, natureza oficial e disponibilidade da adaptação. **NWNForBG documenta o enredo de NWN original; não presumir que SoU/HotU foram adaptados por ele**.

## Consequências

**Positivas:** preservação de cenários e identidade visual, lore reativo, coerência histórica verificável, campanhas alternativas auditáveis, menor custo de adaptação que refazer tudo.

**Custos/riscos:** curadoria de fontes e datas; NPCs do IWD1 são de cerca de 91 anos antes de 1372 e não devem ser transplantados automaticamente; conflitos entre games/livros; world-state/quest flags dos mods não reconhecem as mudanças propostas; bibliotecas gráficas não equivalem a áreas importadas e testadas.

## Testes candidatos

- **CAND-CANON-001:** campanha em 1368 DR não recebe notícia consumada da morte de Azoun IV em 1371.
- **CAND-CANON-002:** campanha em 1372 DR inicia Cormyr com Azoun IV morto e Alusair regente, caso não haja ramo divergente validado.
- **CAND-CANON-003:** NPC de 1281 DR importado para 1372 não fica vivo automaticamente; resolver por revisão da entidade e classificação de longevidade/identidade.
- **CAND-CANON-004:** `Tarsakh 30, 1372 DR` para Wailing Death não vira efeito na cidade antes de data devida (respeitando data/escopo da fonte).
- **CAND-CANON-005:** campanha impede evento histórico com consequência confirmada: abre ramo causal e não aplica efeitos incompatíveis do canon.
- **CAND-CANON-006:** duas fontes datam ToB de forma diferente: manter conflito e bloqueio de ativação rígida até curadoria.
- **CAND-CANON-007:** repetir catch-up/salvar/carregar não duplica rumores, recompensas ou mudanças de facção.
- **CAND-CANON-008:** NPC distante só recebe notícia via canal de propagação e tempo estimado, sem acesso a lore futuro.
- **CAND-CANON-009:** ator canônico morto não aparece ativo por herança de arquivo de área sem justificativa/ramo explícito.
- **CAND-CANON-010:** nova build com IDs diferentes não atribui automaticamente identidade histórica a outro NPC.
- **CAND-CANON-011:** diálogo de expansão não incluída na adaptação não é anunciado como funcional.
- **CAND-CANON-012:** Original e Living World não compartilham efeitos históricos de campanha por engano.

## Artefatos relacionados

- `docs/13-matriz-cronologica-jogos-expansoes.md`: matriz dos conteúdos e datas.
- `docs/14-matriz-eventos-excecoes-repercussoes.md`: eventos e diferenças por período.
- `docs/15-politica-fontes-canon-curadoria.md`: fontes, graus de confiança, fluxo de revisão e schema candidato.
- `docs/12-persistencia-hibrida-e-cronologia-forgotten-realms.md`: persistência e ativação de eventos.

## Pendências explícitas

- DEC-023: ano/data inicial padrão e limites de escolha de época por campanha.
- Decidir regra de precedência quando fonte de cenário conflitar com um jogo ou romance, sem tratar a política editorial de uma wiki como lei oficial da WotC.
- Inspecionar fontes primárias de cada evento/expansão; extrair apenas resumos e metadados legais.
- Validar que recursos/áreas importados via EET/IWD/NWNForBG carregam em multiplayer com EEex e bridge, sem tratar lore como prova de viabilidade técnica.
