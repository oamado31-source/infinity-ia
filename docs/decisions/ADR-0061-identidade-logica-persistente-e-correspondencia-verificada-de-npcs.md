# ADR-0061 — Identidade lógica persistente e correspondência verificada de NPCs

- **Decisão:** DEC-066 — **opção C**, aprovada expressamente pelo idealizador em 2026-11-06.
- **Status:** APROVADA como diretriz de Discovery **v6.2**, **não implementada e não validada** em BG2:EE/EEex, nem em multiplayer.
- **Documento técnico associado:** `docs/66-identidade-persistente-correspondencia-e-reconciliacao-de-npcs.md`.
- **Preservação integral:** DEC-060/C–DEC-065/C e ADR-0055 a ADR-0060 **não foram alterados**; o cânone mantém diretórios físicos por ano DR, e as memórias permanecem no overlay de campanha/ramo.

## Contexto

O mesmo NPC narrativo pode ser observado em instâncias distintas da Infinity Engine após transição de área, save/load, recrutamento, reaparecimento ou migração de build. Em contrapartida, instâncias simultâneas, NPCs genéricos, duplicatas de script e homônimos podem compartilhar nomes, assets ou identificadores transitórios. Um erro de correspondência mistura memórias, segredos, reputação, arcos, flags narrativas e possíveis consequências mecânicas. **Nenhum identificador do motor foi verificado como estável ou globalmente único** neste projeto.

## Alternativas

- **A — Identificadores nativos diretos:** rejeitada como política exclusiva; somente poderão ser usados como evidência após POCs de estabilidade, escopo e reutilização.
- **B — Nome, aparência e localização:** rejeitada como prova suficiente; indícios heurísticos podem servir para triagem, jamais para vinculação autoritativa.
- **C — Identidade lógica persistente por campanha e correspondência verificada, bloqueando ambiguidades:** **APROVADA**.

## Decisão vinculante

1. **Identidade lógica e observação do motor separadas:** introduzir conceitualmente `NPCIdentity` (entidade narrativa persistente por campanha/ramo) e `EngineObservation` (instância observada, efêmera e vinculada a sessão/build/estado). Nomes, portraits, CRE/script names, posições e object IDs, se acessíveis, **não são identidades** por si sós.
2. **Escopo de isolamento:** cada identidade referencia campanha, branch, linhagem de branch, revisões de conteúdo/build e provas. Forks só herdam evidências existentes no ancestral confirmado até o ponto de divergência; novos eventos/alterações do ramo não se propagam ao ramo irmão. Uma entidade canônica pode ter referência de catálogo estável, **sem compartilhar automaticamente memória pessoal entre campanhas**.
3. **Correspondência verificável:** usar evidência positiva suficiente e compatível com o contexto: vínculo de save/observação confirmado, continuidade causal de transição, reserva de instância, evidência de quest/script inventariada na build, eventos de party, histórico e múltiplos sinais independentes. Definição de evidências e thresholds para SPECS/POCs; **não presumir hooks/IDs estáveis**.
4. **Estados explícitos:** `UNSEEN`, `CANDIDATE`, `VERIFIED`, `AMBIGUOUS`, `STALE`, `REVOKED`/`SUPERSEDED`. Apenas `VERIFIED` permite recuperar memória pessoal privada e promover ações dependentes da identidade. `CANDIDATE` não equivale a confirmação.
5. **Fail-closed em ambiguidades:** múltiplos candidatos, evidência conflitante, spawn duplicado, ID reciclado, restauração de snapshot incompatível, mudança de build ou perda de continuidade => `AMBIGUOUS`/`STALE`; bloquear associação automática de memórias, segredos, relacionamentos e compromissos. Pode-se oferecer diálogo genérico autorizado sem identidade pessoal, sem inventar reconhecimento.
6. **Merge/split e correção:** vinculações e desvinculações exigem operação auditável, políticas de risco e autorização compatível; nunca fundir dois NPCs por similaridade de embeddings/LLM. Corrigir associação inválida não reescreve diálogos, acontecimentos ou saves confirmados sem política própria e reconciliação.
7. **Tempo, mortes e instâncias:** morte, ressurreição, respawn, duplicata scriptada, substituição, transformação, teleporte e companion ausente são fenômenos distintos. A identidade não se extingue ou renasce automaticamente por despawn; continuidade deve ser provada para cada forma de reaparecimento, respeitando DEC-043/049/050.
8. **Autoridade e persistência:** registros de identificação usam evidências/receipts verificadas, com idempotência, branch/revision/knowledge-pack/build epoch e checkpoint DEC-053/054; workers LLM/LAN podem propor correspondências, mas não confirmá-las. `UNCERTAIN` da bridge não se converte em prova positiva.
9. **Privacidade e conhecimento:** ACL antes de pesquisar ou entregar memórias DEC-028/064/065, mesmo com correspondência `VERIFIED`. Novos fatos só entram na memória por aquisição legítima DEC-029/064. Identidade não dá onisciência nem acesso a segredos alheios.
10. **Cânone e conteúdos:** os registros de `NPCIdentity`/`EngineObservation` ficam no estado narrativo de campanha, **não em** `knowledge/periods/<ano>-DR/`. Cânone fisicamente segregado DEC-060, fontes e conflitos DEC-061, staging curado DEC-062 e pack fixado DEC-063 permanecem intactos; referências a NPC canônico são metadados e não uma base unificada de todas as épocas.
11. **Sem implementação presumida:** formatos de identificação, fontes de IDs, API EEex, algoritmos, thresholds, telas de revisão, capacidade de rastrear NPC genérico e compatibilidade multiplayer exigem SPECS e POCs. O ADR define princípios, não garante suporte de engine.

## Consequências

- **Benefícios:** reduzir transferência indevida de memórias, suportar reencontros e migração com prova, preservar personagens homônimos e NPCs genéricos sem confusão.
- **Custos:** índice de identidades por campanha/ramo, evidências e epochs, tratamento de incerteza, revisão de vínculos, invalidação de caches e testes de engine/rede.
- **Limites:** sem POC, NPCs poderão ficar `AMBIGUOUS` e usar somente interação limitada. Não sacrificar privacidade/consistência para prometer reconhecimento perfeito.

## Evidência e verificação

- Aprovação explícita da opção C nesta conversa, 2026-11-06.
- **34 testes candidatos** `T066-01` a `T066-34` no documento técnico, **todos não executados**.
- Relacionadas: DEC-008/011/012/021/022/028/029/043/049/050/051/052/053/054/055/056/057/058/059/060/061/062/063/064/065. DEC-006/007/013/015/017/018 continuam em aberto.

## Próxima decisão

**DEC-067 — política de individualização e persistência para NPCs genéricos, únicos e recorrentes.** Alternativas: A — identidade/memória integral de todos os NPCs observados; B — apenas NPCs únicos curados; C — hierarquia híbrida com promoção progressiva por interações/eventos relevantes, identificação comprovada, orçamento e proteção de fatos confirmados. DEC-067 não retrocede os gates de identidade da DEC-066.
