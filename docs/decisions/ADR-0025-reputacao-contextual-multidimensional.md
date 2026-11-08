# ADR-0025 — Reputação contextual e multidimensional

- **ID da decisão:** DEC-030
- **Status:** **APROVADA — opção B**
- **Data:** 2026-11-06
- **Escopo:** Living World; reputação de indivíduos e grupos observada por NPCs, facções e regiões.
- **Fonte:** escolha expressa do idealizador do Infinity AI nesta conversa.
- **Dependências principais:** DEC-004/019/020 (histórico e segredos), DEC-008/009 (persistência e canon), DEC-011 (autoridade mecânica), DEC-014 (código primeiro), DEC-021/022 (simulação e tempo), DEC-027 (risco), DEC-028 (acesso ao conhecimento), DEC-029 (propagação).

## Contexto

A reputação global existente em BG2:EE não representa toda a complexidade social pretendida para Forgotten Realms. Personagens, facções e regiões podem ter avaliações contraditórias sobre a mesma pessoa ou grupo. Além disso, a reputação depende das informações conhecidas ou acreditadas pelo observador — não da onisciência do orquestrador.

### Alternativas consideradas

- **A — Reputação global clássica:** rejeitada como única camada; mantém compatibilidade, mas não comporta diferenças por observador e região.
- **B — Reputação contextual por NPC, facção e região:** **aprovada**.
- **C — Reputação completamente decidida por LLMs:** rejeitada como árbitro; risco de incoerência, vazamento de segredos e custo de inferência.

## Decisão

1. **Reputação multidimensional:** o modelo deverá suportar, no mínimo conceitualmente, diferenças entre **fama/notoriedade**, **confiança**, **temor**, **hostilidade** e **prestígio/respeito**. Esses termos são *categorias narrativas*, não escalas numéricas, pesos ou fórmulas aprovados. Fama não implica aceitação, temor não implica hostilidade, e respeito não equivale à confiança.
2. **Escopo dos avaliados e dos avaliadores:** distinguir a reputação de um **personagem individual**, **grupo**, e eventualmente identidade pública/persona, perante um **NPC específico**, **facção/organização**, ou **região/localidade**. Não propagar automaticamente a avaliação de um NPC para toda a cidade ou facção.
3. **Conhecimento legítimo e crenças:** modificar a percepção de um observador somente a partir de testemunhos, experiências, notícias/rumores ou outras fontes legitimamente adquiridas conforme DEC-028/029. Uma crença pode ser equivocada; a reputação pode sofrer consequências sociais de rumor falso **sem reescrever a verdade histórica**.
4. **Proveniência e causalidade:** qualquer mudança relevante deve referenciar evento/alegação, fonte de conhecimento, versão da regra, data da campanha, destinatário e contexto, com possibilidade de auditoria e reconstrução por log/snapshot (DEC-008).
5. **Separação da reputação nativa:** preservar a reputação global e as regras mecânicas de BG2:EE como baseline. A reputação contextual é inicialmente uma **camada externa narrativa**. Nenhum espelhamento automático dos escores narrativos para a variável de reputação do jogo, preços, reações mecânicas ou flags de quest sem SPEC, teste técnico e confirmação do host (DEC-011/012).
6. **Cálculo código primeiro:** regras determinísticas/tabelas/estados tratam agregações, eventos e atualizações; um LLM local, quando acionado, poderá elaborar a expressão verbal de avaliações já calculadas e autorizadas, sem atribuir conhecimento ou mudar valores por improvisação.
7. **Tempo e atividade:** avaliações e rumores podem mudar com o tempo do mundo autorizado. Para milhares de NPCs, usar projeções, agrupamento e processamento por atividade ACTIVE/NEAR/DISTANT/DORMANT; não manter LLM ou recálculo de reputação por NPC a cada tick.
8. **Privacidade e identidades:** informações do histórico secreto não aumentam hostilidade/reputação pública por estarem no banco. Identidade oculta, disfarces, alegações de autoria e responsabilização individual/grupal exigem evidência e regras específicas; **não presumir que todo grupo é culpado por ações individuais**.
9. **Influência social limitada:** tendências da facção ou reputação regional podem influenciar membros/locais quando houver filiação, informação e políticas válidas; não impor uma opinião uniforme a todos os NPCs.
10. **Revisão de impressões:** receber evidência contrária, desmentido, mudança de alianças ou retcon autorizado pode alterar percepções futuras, mas não apagar o que um NPC historicamente acreditou sem política específica de correção/reconstrução.
11. **Riscos e bloqueios:** reputação pode influenciar propostas de diálogos, oportunidades e reações narrativas, sujeitas a conhecimento e risco. Prisões, ataques, perda de itens, efeitos de facção e outras consequências mecânicas precisam de gateway/autorização e confirmação do host. Consequências históricas irreversíveis permanecem HIGH até política especial DEC-027.
12. **Modos e campanhas isolados:** reputação narrativa do Living World não contamina a campanha Original ou outras campanhas; multiplayer deve observar o estado autoritativo compartilhado e não calcular versões incompatíveis por cliente.

## Exemplo aprovado como intenção, não conteúdo criado

Uma equipe impede um ataque a comerciantes de Athkatla. Comerciantes que presenciaram ou souberam legitimamente podem aumentar confiança; uma facção criminosa informada pode aumentar hostilidade; moradores de Neverwinter sem informação não alteram percepção. Um rumor falso pode gerar suspeita local, mas não muda o fato confirmado. O nome e as regras mecânicas de qualquer NPC/facção real serão determinados por dados verificados na implantação.

## Consequências

**Benefícios:** mundo social coerente com fatos e rumores; facções/indivíduos com visões distintas; narrativa emergente sem LLM contínuo; rastreabilidade; compatibilidade do motor preservada.

**Custos:** novas projeções e índices de percepção; vinculação aos canais de rumor; manutenção de provenance/identidades; regras para esquecimento, reparação e conflitos; testes de desempenho e sincronização multiplayer.

**Riscos:** vazamento de segredo por reputação implícita; rumor tratado como fato; avaliação global instantânea; má atribuição de culpa ao grupo; manipulação/farm de reputação; conflitos após reload; converter reputação externa em mecânica BG2 sem validação.

## O que NÃO foi decidido

- Escalas numéricas, limites, pesos, agregação, taxa de decaimento e fórmulas de reputação; classificação moral/alinhamento.
- Implementação de sistema comercial, alteração de preços, recrutamento ou reações automáticas no BG2:EE/EEex.
- Transmissão instantânea de reputação por região ou associação automática de identidades secretas.
- Conjunto de objetivos e recursos próprios das facções: tópico da **DEC-031**.
- Implementação, compatibilidade multiplayer, banco, UI, e testes reais do jogo: permanecem pendentes de SPECS/POCs.

## Critérios de aceitação candidatos (não são SPECS)

1. O mesmo grupo apresenta percepções diferentes perante dois NPCs/facções conforme fontes e interesses.
2. Um NPC sem acesso à notícia não atualiza sua reputação do grupo automaticamente.
3. A fama pode aumentar sem aumentar confiança; temor pode aumentar sem aumentar respeito.
4. O mesmo observador separa opinião sobre membro do grupo e coletivo salvo evidência de atribuição.
5. Um rumor falso influencia crença/percepção sem modificar fatos confirmados de campanha.
6. Históricos secretos não alteram reputação pública sem descoberta legitimada e política de divulgação.
7. NPCs de mesma facção podem discordar; agregação regional não sobrescreve registros individuais.
8. Modo Original preserva o escore nativo e não herda a camada de reputação narrativa.
9. Mutação mecânica solicitada por reputação exige gateway, confirmação do host e risco aprovado.
10. Após salvar/carregar e replay, não há alterações duplicadas; versões e causas permanecem auditáveis.
11. Regiões distantes e NPCs dormentes não requerem LLM por tick para atualizar reputação.
12. Dois clientes multiplayer não divergem sobre o estado persistente autoritativo da campanha; gate técnico continua pendente.

## Rastreabilidade

- Desenho de dados e de testes candidato: `../29-reputacao-contextual-percepcoes-e-faccoes.md`.
- Mapa consolidado: `../02-mapa-de-decisoes.md`.
- Próxima entrevista: **DEC-031 — objetivos, alianças e autonomia operacional das facções**.
