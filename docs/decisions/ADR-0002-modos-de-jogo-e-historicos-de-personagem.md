# ADR-0002 — Modos de jogo separados e histórico dos personagens como motor narrativo

- **Decisão relacionada:** DEC-004
- **Estado:** APROVADA
- **Data:** 2026-11-05
- **Responsável:** idealizador do projeto
- **Origem:** opção **C** escolhida com adendo explícito sobre histórias criadas por cada jogador.
- **Fase atual:** discovery (não equivale a validação técnica).

## Contexto

O projeto reutilizará, quando tecnicamente viável, recursos de BG2:EE/EET e adaptações compatíveis de Icewind Dale e NWN. Busca-se preservar a experiência das campanhas originais e, em paralelo, criar um modo aberto orientado por IA em que cidades, áreas, NPCs e eventos possam mudar entre visitas. Cada personagem jogador terá seu próprio histórico de vida, que deve influenciar os acontecimentos da campanha cooperativa.

## Alternativas consideradas para os modos

- **A — Campanhas originais enriquecidas por IA:** aproveita narrativas prontas, mas amplia o risco de conflitos com scripts do enredo original.
- **B — Apenas mundo aberto:** evita parte desses conflitos, porém abandona a experiência original como modo de jogo.
- **C — Modos separados, Original e Living World:** selecionada para separar progressão, estado e intervenções narrativas.

## Decisão aprovada

1. O projeto deverá oferecer, como **objetivo de produto**, dois modos de jogo: **Original** (campanhas clássicas preservadas, com isolamento de progressão) e **Living World** (exploração livre e geração assistida por IA). A forma de expor os modos (launcher, perfis, instalações separadas) permanece sujeita à viabilidade técnica.
2. Os modos terão **saves e estados narrativos separados**; eventos gerados no Living World não poderão alterar automaticamente a progressão das campanhas originais.
3. **Cada jogador deverá criar um histórico próprio para seu personagem**, registrado de forma persistente e associado à identidade correta do personagem/campanha.
4. O histórico **não será apenas descritivo**: servirá como fonte de motivações, vínculos, conflitos, inimigos, lugares de origem, promessas, objetivos e outros *ganchos narrativos* que a IA poderá utilizar para criar eventos, encontros, diálogos e missões contextualizados.
5. A IA deverá relacionar esses ganchos às condições atuais do mundo e às consequências de escolhas dos jogadores, evitando acontecimentos contraditórios ou repetitivos.
6. Ganchos de personagens diferentes podem produzir acontecimentos individuais ou entrelaçados que afetem a campanha cooperativa. O sistema não deve assumir que todos os NPCs conhecem os segredos ou a história completa de um personagem.
7. Resultados e alterações de mundo deverão ser **propostos, validados por regras e confirmados na fonte autoritativa de estado**; textos de jogadores e respostas do modelo não podem executar comandos livremente no motor.
8. **A implementação fica condicionada às provas de compatibilidade** BG2:EE/EET/EEex/mods/multiplayer. A aprovação é de comportamento desejado, não de suporte já existente no jogo.

## Exemplo representativo

- Jogadora A cria uma personagem que **fugiu de uma ordem de cultistas**. O sistema extrai o gancho de perseguição, mantendo secretas as informações que os cultistas não poderiam ter aprendido.
- Jogador B cria um personagem que **jurou vingança contra uma pessoa específica**. O sistema cria oportunidades progressivas de investigação, pistas, encontros e escolhas, sem obrigar o jogador a cumprir a vingança.
- Ao explorar uma estrada, o diretor narrativo pode selecionar um dos ganchos para compor um encontro com perseguidores; em outra visita, um informante pode revelar uma pista sobre o alvo da vingança.
- Após a sessão, as decisões são registradas para que o mundo responda de forma coerente na próxima visita.

## Consequências arquiteturais

- Separar `mode_id`, `campaign_id`, `player_id`, `character_id`, `world_state_id` e identificadores de eventos; não compartilhar saves entre modos por acidente.
- Armazenar **texto original do histórico** e **ganchos estruturados extraídos** com fonte, status, escopo de visibilidade e revisão/versionamento. Distinção essencial: *alegação no histórico do personagem* não implica *fato mundial confirmado*.
- Definir categorias mínimas de gancho: origem, pessoas, grupos/facções, dívidas, inimigos, promessas, perdas, objetivos, medos e segredos (lista inicial, extensível).
- Criar um diretor narrativo que considere simultaneamente história de cada personagem, grupo, localização, progressão, recursos válidos do jogo, diversidade de acontecimentos e consequências anteriores.
- Controlar a frequência da focalização narrativa por personagem, sem prometer igualdade matemática em toda sessão. Evitar que um histórico monopolize todos os encontros.
- Proteger fronteiras de conhecimento: IA, narrador, NPC e jogadores não necessariamente conhecem as mesmas informações.
- Tratar histórico inserido pelo jogador como **entrada não confiável**: não executar instruções embutidas, comandos Lua, pedidos de arquivos, URLs ou alterações administrativas.
- Prever degradação segura quando a IA estiver indisponível: regras e conteúdo convencional continuam, sem corromper o estado do mundo.

## Limites do que foi aprovado

- **Aprovado:** dois modos separados; histórico individual obrigatório; histórico impulsiona eventos e missões no Living World; narrativa contextual e persistente; preservação de isolamento entre modos.
- **Ainda não aprovado:** padrão de visibilidade de segredos; forma de revisar histórias; autonomia para eventos sensíveis/irreversíveis; frequência de eventos; interface de edição; cronologia/canon; provedor de IA; tecnologia definitiva do bridge.

## Requisitos e critérios candidatos (não são SPECS aprovadas)

- **CAND-MODE-001:** cada modo tem namespace de estado separado; reiniciar ou alterar o Living World não modifica save/capítulo/quest do modo Original.
- **CAND-CHAR-001:** cada personagem deve ter histórico registrado para ser considerado apto à geração narrativa baseada em origem.
- **CAND-CHAR-002:** o sistema identifica pelo menos um gancho utilizável no histórico e permite que sua interpretação seja revisada antes de passar a orientar o mundo (interface de revisão ainda por decidir).
- **CAND-NARR-001:** eventos propostos registram a qual personagem, gancho, localização e fatos de mundo estão relacionados; nenhum evento é aplicado sem verificação de pré-condições.
- **CAND-KNOW-001:** um NPC não revela um segredo do personagem sem um caminho de conhecimento registrado e autorizado.
- **CAND-COOP-001:** dois personagens com histórias distintas podem originar acontecimentos diferentes na mesma campanha sem misturar suas identidades/memórias.
- **CAND-PERSIST-001:** após salvar, encerrar e reabrir, histórias, ganchos relevantes e consequências continuam coerentes.

## Riscos e dependências

- **R-009:** contradição entre histórico do jogador e lore/canon/mundo persistido.
- **R-010:** vazamento de informação entre personagem, NPCs e membros da equipe; a política de visibilidade está pendente.
- **R-011:** agente narrativo privilegiar injustamente um personagem ou impor acontecimentos excessivos.
- **R-012:** entrada maliciosa no histórico influenciar o agente ou tentar acionar comandos do bridge.
- **Dependências:** DEC-001, DEC-008, DEC-009, DEC-011, DEC-014, DEC-019, testes de compatibilidade do motor.

## Próxima decisão relacionada

**DEC-019 — Política de conhecimento e visibilidade do histórico dos personagens**: público, privado ou híbrido? Não foi respondida nesta rodada.
