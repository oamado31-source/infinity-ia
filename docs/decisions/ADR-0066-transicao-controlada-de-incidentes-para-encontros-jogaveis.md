# ADR-0066 — Transição controlada de incidentes fora de cena para encontros jogáveis

- **Decisão:** DEC-071 — **opção C**, escolhida expressamente pelo idealizador em 2026-11-06.
- **Estado:** **APROVADA como desenho de arquitetura no Discovery v6.7**, ainda **NÃO IMPLEMENTADA**. Nenhuma capacidade de spawn, alterações de script, eventos locais, sincronização de clientes ou POC BG2:EE/EEex foi comprovada.
- **Especificação de Discovery:** `docs/71-transicao-de-incidentes-offscreen-para-encontros-locais-validacao-e-handoff.md` (**46 testes candidatos T071-01..46, nenhum executado**).
- **Preservação exigida:** DEC-060 a DEC-070 e respectivos ADR-0055 a ADR-0065 continuam **inalterados**; DEC-005-E/011/012/027/033/050/051/052/053/056 continuam aplicáveis.

## Problema

DEC-069 permite itinerários e DEC-070 permite incidentes fora de cena sob risco. Quando a party se aproxima, um incidente ainda aberto poderia ser oferecido como situação jogável, mas somente se a área e os recursos realmente existirem na build e se houver uma integração validada com o host. Sem controle de concorrência, a simulação distante pode resolver o mesmo incidente enquanto um cliente o presencia, e a IA pode confundir texto dramático com combate, item, morte ou quest confirmados.

## Alternativas consideradas

- **A — Somente narrativa:** rejeitada por impedir que eventos emergentes se tornem interações locais mesmo quando houver suporte demonstrado.
- **B — Materialização automática de qualquer incidente:** rejeitada por presumir suporte de engine, criar riscos de duplicação de NPCs/combates, conflitos com scripts existentes e efeitos mecânicos sem receipts.
- **C — Transferência seletiva, previamente compatibilizada e confirmada:** **APROVADA**.

## Regras vinculantes

1. **Incidente é a unidade causal:** conservar o mesmo `incident_id`, a identidade do NPC, `campaign_id`, `branch_id`, `itinerary_id`, segmento, janela do relógio, revisão do Knowledge Pack, checkpoint, risk class e proveniência de DEC-070. O encontro local é *representação ou handoff* do mesmo incidente, não um segundo evento independente.
2. **Oportunidade não é presença:** proximidade validada da party à região pode habilitar avaliação de um encontro, mas não prova que NPCs, objetos, diálogos ou combate estejam instanciados na área. A observação do host deve sustentar condição real; nenhuma suposição de API EEex.
3. **Compatibilidade por build:** verificar manifesto DEC-051, área real e carregável, mapa/recursos disponíveis, scripts/quests/romances protegidos DEC-050, assinaturas e capacidades já demonstradas em POC. Cidade do cânone não equivale a mapa disponível. Sem compatibilidade: apenas proposta narrativa ou incidente pendente.
4. **Identidade e privacidade:** NPC participante requer identidade verificada DEC-066; ambiguidades de CRE, GUID, homônimos, duplicatas ou entidade já presente bloqueiam associação e tentativa de criar instância; proteger conhecimento e segredos com ACL DEC-028/060–066.
5. **Coordenação exclusiva offscreen/local:** a promoção de um incidente exige uma **reserva durável e versionada de resolução**, sob autoridade do coordenador da campanha/host. Worker distante não pode concluir efeitos durante a reserva local. Transição é atômica quanto ao direito de resolver, não exige transação atômica com a engine (não pressuposta).
6. **Exclusão por revisão e fencing:** usar `incident_id`, `resolution_epoch`, `state_revision`, `checkpoint_epoch`, token de fencing e `idempotency_key`. Um único resolvedor autorizado avança a revisão por comparação-condicional. Expiração de lease não autoriza um segundo resolvedor a reaplicar efeitos sem reconciliação.
7. **Condições de handoff:** somente após verificação de horário, região, ramo, identidade, capabilities, risco e permissão; confirmação dos jogadores/host quando a política requer. Nenhum prompt de LLM cria autorização, spawn ou consentimento.
8. **Separar oferta de execução:** oferecer rumor, oportunidade de encontro ou marcador informativo é ação narrativa distinta de efetivamente instanciar atores ou disparar scripts. UI e gatilhos dependem de DEC-007/016, SPECS e POCs; opção C **não** afirma que haverá interface ou spawn funcional.
9. **Gateway tipado:** toda ação mecânica passa pela allowlist DEC-012 e compatibilidade por build/DEC-003/013/015; o host BG2:EE mantém exclusividade para estado mecânico DEC-011. Nada de comandos Lua/shell arbitrários, edição direta de save, spawn ou teleporte presumidos.
10. **Receipts e conclusão:** somente observações/recibos de host coerentes com a operação, sessão e revisão autorizam `ENGINE_CONFIRMED`; eventos narrativos LOW autorizados podem ser `NARRATIVE_COMMITTED` sem efeitos mecânicos. Texto LLM, logs de workers, clients e estimativas de combate nunca confirmam HP, inventário, XP, loot, morte ou quest.
11. **Sem dupla resolução:** após confirmação e commit único dos efeitos autorizados, marcar o incidente como resolvido e impedir o processamento offscreen ou nova apresentação mecânica da mesma ocorrência. Replays, reconexão e restores consultam o ledger antes de qualquer tentativa.
12. **Incerteza falha fechada:** crash, timeout, desconexão, save/load, alteração de build ou resultado de bridge `UNCERTAIN` suspendem novas ações; reconciliar host/checkpoint/idempotência antes de reiniciar ou devolver o incidente ao fluxo distante. Falha de handshake não implica que engine não aplicou operação.
13. **Cancelamento seguro:** se handoff for cancelado **antes de qualquer efeito mecânico**, poderá liberar a reserva ao processamento distante apenas após comprovar ausência de operação em voo e revalidar estado. Após efeito incerto ou confirmado, não há rollback imaginário nem reexecução automática.
14. **Risco proporcional:** classes LOW/MEDIUM/HIGH da DEC-027/070 continuam; uma cena visual inofensiva não autoriza combate, morte, captura, saque, reputação ou mudança de quest; impactos agregados elevam a classe de risco. Eventos canônicos protegidos continuam HIGH default-deny DEC-034.
15. **Multiplayer e consentimento:** host autentica eventos e determina o que está presente e confirmado. Clientes podem observar e escolher dentro da política DEC-041/042/046, mas não resolver mecanicamente nem inserir múltiplos eventos por reconexão. Nenhum jogador ausente perde agência por incidente automatizado.
16. **Cronologia/ramo:** viagem DEC-069, clock DEC-022, simulação DEC-021/068 e decisões DEC-060–063 devem concordar; encontros não poderão acontecer após o fato estar resolvido nem mover NPC instantaneamente para área incompatível. Bifurcação/restauração não transportam resultado entre branches.
17. **Diretor regional e conflitos:** DEC-005-E sugere encontros contextualizados; DEC-033 pode propor manifestação local de conflito estratégico, mas a elegibilidade e os gates permanecem idênticos. O encontro não substitui automaticamente a verdade regional ou resolve guerras em escala.
18. **Orçamento e degradação segura:** RPD DEC-056 define limites e filas; se recursos, capacidades ou sincronização faltarem, manter proposta pendente/representação narrativa validada. Nunca acelerar o relógio ou inventar resolução para reduzir fila.
19. **Auditoria mínima:** registrar transições, propostas rejeitadas, motivos de incompatibilidade, decisões de autorização, fencing, receipts, efeito confirmado e revisões, com redação de segredos. Checkpoints DEC-053/054 e Health Monitor DEC-055 monitoram órfãos e estados UNCERTAIN.
20. **Conteúdo histórico isolado:** nenhuma transição grava memórias e eventos no corpus canônico. DEC-060 mantém `knowledge/periods/<ano>-DR/` fisicamente dividido; DEC-061/062 curadoria e proveniência, DEC-063 Knowledge Packs fixados. Incidentes e consequências somente no overlay da campanha/ramo.

## Benefícios, custos e riscos assumidos

- **Benefício:** um encontro emergente pode ficar jogável quando isso é verificavelmente suportado, sem sacrificar integridade de campanha, autonomia nem host.
- **Custo:** reconciliador único por incidente, ledger e fencing duráveis, matriz de compatibilidade por build, gates de autorização e instrumentação de falhas.
- **Limitação:** alguns incidentes nunca poderão ser materializados localmente; nesses casos, manter narrativa autorizada ou pendência. Preferir experiência parcial honesta a efeitos inventados.

## Verificação pendente

A SPECS deverá definir estados finais, APIs e capabilities reais, estratégia transacional de ledger, critérios para a party estar suficientemente perto, escopos de consentimento, UI, conteúdo de encontro, receitas de rollback/restore, limites temporais e testes multiplayer. Documento 71 lista **46 testes candidatos, não executados**; até uma POC demonstrar um caminho seguro, **nenhuma funcionalidade de spawn, encounter, script ou ação mecânica local é prometida**.

## Próxima decisão — DEC-072 (em aberto)

**Política de composição dos encontros jogáveis por build:** A) apenas encontros nativos pré-existentes; B) montar scripts/atores dinamicamente em runtime; **C, recomendada)** catálogo de encontros/templates e adapters por build, previamente inventariados e testados, com preparação offline e geração expandida somente mediante validação/POCs. A DEC-071 aprova o *handoff*, não autoriza geração arbitrária de recursos de engine.
