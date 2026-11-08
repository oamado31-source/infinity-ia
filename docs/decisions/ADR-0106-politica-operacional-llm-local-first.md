# ADR-0106 — Runtime de LLM local-first e exceção remota controlada

**Estado:** APROVADA COMO POLÍTICA / ESCOPO em 2026-11-07, com base no questionário Q01–Q28 ratificado pelo idealizador.  
**Decisões:** DEC-006 / Q06=B. **Baseline:** Discovery v10.6 → SDD v11.0.  
**Referências anteriores:** DEC-003/011/012/014/028/059; Q01, Q06.  
**Gate:** documentação é política aprovada, **não uma capability comprovada no BG2:EE/EEex**.

## Contexto e alternativas

O questionário consolidado registrou escolhas explícitas para evitar bloqueio indefinido do Discovery. A opção escolhida não elimina mecanismos de segurança nem substitui ADRs anteriores: ela restringe a estratégia de implementação do MVP e da V1.

## Decisão vinculante

1. Modelo local por padrão, orquestrador central e especialistas sob demanda; código determinístico antes da LLM (DEC-014).
2. Provedor remoto só com opt-in explícito por sessão e finalidade, filtro de contexto por ACL, dados mínimos, teto de gasto e opção de revogar.
3. Falha, limite de custo ou indisponibilidade gera fallback de texto/ação segura; jamais autoriza mutação no host.
4. Modelo/hardware/latência precisos ficam como parâmetros de benchmark da SPEC, não promessas de desempenho.
5. Q01=B: primeiro vertical slice inclui bridge read-only, dois clientes, memória NPC e **proposta narrativa sem spawn**. 

## Consequências

- Requisitos nas SPECs devem citar este ADR e a pergunta de origem, com critério de aceite observável.
- Recursos mecânicos dependem de capability verificada na build do host, consentimento, idempotência e recibos; caso contrário `UNKNOWN` ou `BLOCKED_CAPABILITY`.
- Qualquer modificação material desta política deverá criar um ADR novo, mantendo este arquivo inalterado.
- Testes unitários sintéticos nunca serão descritos como validação de bridge, jogo ou multiplayer real.
