# ADR-0111 — Constitution versionada, SPECs numeradas e change requests rastreáveis

**Estado:** APROVADA COMO POLÍTICA / ESCOPO em 2026-11-07, com base no questionário Q01–Q28 ratificado pelo idealizador.  
**Decisões:** DEC-111 / Q12=B. **Baseline:** Discovery v10.6 → SDD v11.0.  
**Referências anteriores:** DEC-003/011/013/015/018/111; Q12=B e decisão de governança pública solicitada pelo usuário.  
**Gate:** documentação é política aprovada, **não uma capability comprovada no BG2:EE/EEex**.

## Contexto e alternativas

O questionário consolidado registrou escolhas explícitas para evitar bloqueio indefinido do Discovery. A opção escolhida não elimina mecanismos de segurança nem substitui ADRs anteriores: ela restringe a estratégia de implementação do MVP e da V1.

## Decisão vinculante

1. Constitution, Domain, Architecture, Templates, Features, Skills e ADRs são o contrato do projeto.
2. Toda feature exige `spec.md`, `plan.md`, `tasks.md`, requisitos `REQ-*`, evidências de risco, e testes vinculados, com baseline e status explícitos.
3. Mudança importante requer `CR-*` com motivação, diff, impacto em ADR/SPEC/schema, plano de migração e aprovação; decisão antiga não é reescrita.
4. Branches de trabalho, PRs com revisão, testes e proteção de main. Contribuições externas em forks, sem permissões diretas ao repo canônico.
5. Licença open-source e estratégia definitiva `repo independente vs fork` são **decisões separadas ainda pendentes**; código e docs podem ser preparados sem publicar assets protegidos. 

## Consequências

- Requisitos nas SPECs devem citar este ADR e a pergunta de origem, com critério de aceite observável.
- Recursos mecânicos dependem de capability verificada na build do host, consentimento, idempotência e recibos; caso contrário `UNKNOWN` ou `BLOCKED_CAPABILITY`.
- Qualquer modificação material desta política deverá criar um ADR novo, mantendo este arquivo inalterado.
- Testes unitários sintéticos nunca serão descritos como validação de bridge, jogo ou multiplayer real.
