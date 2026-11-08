# ADR-0045 — Conciliação híbrida de roteiros originais e eventos dinâmicos

- **Decisão:** DEC-050 — precedência e reconciliação de conteúdo nativo de BG2:EE e mods com propostas do Infinity AI.
- **Escolha expressa:** **C — conciliação híbrida, com proteção de scripts e divergências causais validadas.**
- **Estado:** **APROVADA** pelo idealizador em 2026-11-06.
- **Versão:** Infinity AI Discovery **v4.6**.
- **Fase:** SDD/Discovery. Decisão arquitetural aprovada; não corresponde a SPEC final, código, mod ou integração verificada.
- **Dependências:** DEC-003/004/008/009/010/011/012/014/019/020/021/022/024/025/026/027/028/030/034/039/040/041/047/048/049.
- **Desenho:** `docs/50-conciliacao-de-scripts-quests-romances-e-eventos-dinamicos.md`.

## Contexto

BG2:EE traz diálogos, estados de missões, romances, banters, scripts de NPCs e pré-condições de participação no grupo, além de recursos instalados por mods em builds variadas. A DEC-049 permite que um companheiro cuja saída *foi confirmada* tenha vida externa e eventual reencontro. Isso introduz riscos de colisão com conteúdo esperado pelo jogo: remover ou transportar alguém ainda necessário a uma missão, exibir um romance fora de contexto, avançar uma quest por texto sem atualizar flags, duplicar NPCs ou disparar duas vezes uma ação.

Nenhuma integração em particular com EEex, variáveis do motor, WeiDU, EET ou multiplayer é presumida como testada ou viável apenas por aprovar esta política.

## Decisão vinculante

1. **Baseline original protegido:** a instalação concreta de BG2:EE e dos mods ativos, com versões e ordem de instalação, fornece a linha base de conteúdo narrativo e mecânico. Scripts originais não são substituídos por texto de IA. O modo Original permanece isolado.
2. **Propostas são propostas:** acontecimentos inventados pelo Personal Story Director, simulador de facções, autonomia de NPCs ou LLM devem entrar como propostas tipadas e identificadas, não como fatos ou comandos diretos. Conteúdo gerado não tem precedência sobre estado do host.
3. **Inventário e titularidade dos marcos:** antes de afetar quest, romance, banter, disponibilidade de NPC, posição, inventário ou evento canônico, consultar as dependências de conteúdo *efetivamente identificadas* para o build e as observações confiáveis disponíveis. Estados não observáveis devem ser marcados `UNKNOWN`, não inferidos de narrativa.
4. **Conciliação determinística:** um reconciliador baseado em regras, dependências, riscos, cronologia, causalidade e estado confirmado selecionará entre `ALLOW`, `ADAPT`, `DEFER`, `BLOCK` e `DIVERGENCE_REVIEW`; LLM poderá sugerir reformulação narrativa, nunca autorizar mutações.
5. **Reservas de cenas e pré-condições:** eventos originais com flags, pré-condições e etapas verificáveis devem ser protegidos contra deslocamento, romance concorrente, conversão de lealdade, remoção de companion ou inserção de cena incompatível. A reserva é tão precisa quanto a evidência do build, jamais suposta completa.
6. **Adaptação sem retcon:** preferir conteúdo complementar compatível, realocação temporal válida ou mudança de forma narrativa que não exija alterar estados do motor. Adiar uma proposta não a transforma em fato; mudanças em missões existentes só por caminho validado.
7. **Divergências legítimas possíveis:** eventos de jogadores confirmados podem gerar ramificações alternativas, mas somente quando causalidade, consentimento, política de risco (especialmente HIGH/cânone) e capacidade técnica demonstrada autorizarem. Se não houver rota técnica para compatibilizar o estado, bloquear a mutação e oferecer fallback narrativo explícito, sem alegar branch implementado.
8. **Autoridade e gateway:** efeitos mecânicos dependem de comando tipado em allowlist, preflight, controle de risco/consentimento, idempotency key, receipt de host e pós-condição observável. A IA nunca executa Lua/shell/código arbitrário no motor.
9. **Incerteza e concorrência:** se flags, sessão, NPC ou quest estiverem em estado desconhecido ou `UNCERTAIN`, impedir commit, reconciliar host/snapshot e não reexecutar cegamente. Revisões de estado evitam que duas fontes alterem o mesmo marco.
10. **NPC canônico e vida pós-party:** `projected_location` ou novo vínculo de facção não equivale à posição física; o NPC não pode simultaneamente cumprir arco nativo incompatível e aparecer em outra região. Reencontros e re-recrutamento exigem presença, script e party-state comprováveis.
11. **Cânone, época, conhecimento e consentimento:** validar ano DR, identidade, origem e aliases, relações existentes, DLC/mods, segredos e ACL de conhecimento antes da redação e exposição. Preservar autoria dos PCs e efeitos de romances/relacionamentos a partir de fatos existentes; não forçar decisões de jogadores ausentes.
12. **Observabilidade e reprodutibilidade:** gravar proposta, dependências, avaliação, versão do manifesto do build, flags efetivamente observadas, aprovação, host receipt, decisão e fallback para auditoria e testes; persistir em saves/snapshots compatíveis e impedir replay duplo.
13. **Escalonamento:** o primeiro POC limita-se a BG2:EE limpo, inspeção read-only e casos seguros isolados; EET, IWD, NWNForBG e demais mods exigem matrizes e regressões independentes. Nenhum hook é anunciado como suportado antes de dois clientes + save/load quando aplicável.

## Política operacional básica

| Situação | Decisão padrão |
|---|---|
| Evento novo, puramente narrativo, sem conflito conhecido e fatos autorizados | `ALLOW`, sujeito às regras, fonte e ACL |
| Proposta colide com cena/flag/romance/quest confirmado | `ADAPT` se preservar invariantes; senão `DEFER`/`BLOCK` |
| Dependência nativa de alto impacto não observada | `BLOCK` da mutação; investigar o build, não presumir ausência de conflito |
| Jogadores causam desvio histórico verificável | `DIVERGENCE_REVIEW` sob DEC-009/026/027/034 e POC do efeito |
| Recebimento mecânico desconhecido ou timeout | `UNCERTAIN` → reconciliação; não marcar evento como aplicado |
| Mod/versão/ordem do build mudou | invalidar garantias anteriores, refazer inventário, regressões e gates |

## Trade-offs

- **Versus A — prioridade absoluta do roteiro:** manter invariantes não exige congelar narrativas; extensões compatíveis e bifurcações causais validadas enriquecem a experiência.
- **Versus B — prioridade automática do Living World:** uma narrativa desejável não justifica quebrar quests, romances, saves ou efeitos no multiplayer.
- **Opção C:** é mais complexa, exige catálogo/inventário e validação por build, mas mantém liberdade causal sem tratar o motor como ficção editável.

## Invariantes

- `GENERATED_PROPOSAL != CANON_EVENT != ENGINE_FACT`.
- `SCRIPT_FLAG_UNKNOWN != FLAG_FALSE`.
- `NPC_OFFSCREEN_LOCATION != HOST_CONFIRMED_LOCATION`.
- `NARRATIVE_BRANCH != MECHANICAL_BRANCH_IMPLEMENTED`.
- `HOST_RECEIPT_REQUIRED` para qualquer mutação do motor.
- `UNCERTAIN => NO_RETRY_WITHOUT_RECONCILIATION`.
- `HIGH_CANON_EVENT => SPECIAL_AUTHORIZATION`, sem exceção implícita por protagonismo do NPC.
- `BUILD_CHANGED => REVALIDATE_CONTENT_MANIFEST`.
- `ORIGINAL_MODE != LIVING_WORLD_MODE`.

## Não decidido nesta ADR

- Ferramentas definitivas de inspeção de diálogos/scripts/flags, cobertura de recursos e política de atualização do catálogo por mod (assunto candidato da **DEC-051**).
- Quais romances, quests ou banters serão suportados por branches; formatos exatos de patches, hooks e APIs; detalhes de prioridade quando dois mods colidirem.
- Semântica do conjunto completo de flags para cada build, estratégia de rollback mecânico, restrições do multiplayer, UI de aprovação e comportamento de recuperação a cada erro; todos pendem de SPEC/POC.
- Regras de conteúdo adulto/romance específicas, além das salvaguardas de agência e conhecimento já aprovadas.

## Gates / critérios candidatos

1. Fingerprint reproduzível da instalação e inventário *read-only* dos recursos relevantes, começando por um companion com quest/romance no BG2:EE limpo.
2. Casos de teste de conflitos de flags, indisponibilidade de NPC, progressão de quest, evento paralelo e proposta sem evidência; `UNKNOWN` deve bloquear mutações inseguras.
3. POC de diálogo/adiamento sem efeitos e POC de operação tipada segura, em cópia isolada, com receipt do host.
4. Regressão de comportamento original de missões/romances e testes save/load, 2 clientes, sincronização, reconexão e repetição idempotente.
5. Repetir a matriz por mod/build; erro de inventário ou mudança de versão bloqueia integração, não força adaptação de conteúdo.

**Status de engenharia:** nenhuma dessas capacidades foi demonstrada nesta aprovação; a decisão documenta critérios para a futura SPEC.
