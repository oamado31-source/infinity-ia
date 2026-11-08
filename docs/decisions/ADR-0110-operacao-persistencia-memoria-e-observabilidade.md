# ADR-0110 — SQLite local, logs append-only, memória delimitada, rollback e LAN privada

**Estado:** APROVADA COMO POLÍTICA / ESCOPO em 2026-11-07, com base no questionário Q01–Q28 ratificado pelo idealizador.  
**Decisões:** DEC-018 / Q08=B, Q10=B, Q15=B, Q17=B, Q24=B, Q25=B, Q26=B. **Baseline:** Discovery v10.6 → SDD v11.0.  
**Referências anteriores:** DEC-001/008/011/018/021/022/028/053–059/064–074; Q08, Q10, Q15, Q17, Q24–Q26.  
**Gate:** documentação é política aprovada, **não uma capability comprovada no BG2:EE/EEex**.

## Contexto e alternativas

O questionário consolidado registrou escolhas explícitas para evitar bloqueio indefinido do Discovery. A opção escolhida não elimina mecanismos de segurança nem substitui ADRs anteriores: ela restringe a estratégia de implementação do MVP e da V1.

## Decisão vinculante

1. Estado local SQLite (com schema e migrations) + event log append-only, snapshots/epoch/branch/campaign separados, backups e rollback ensaiado.
2. Logs estruturados minimizados, action IDs/receipt IDs, replay sintético e trilhas de auditoria sem expor textos privados/segredos de NPCs.
3. Memória por NPC/PC: fatos tipados, sumários com proveniência, ACL, janelas temporais e recuperação sob demanda; sem colocar toda a história num prompt.
4. Simulação ACTIVE/NEAR agregada e DISTANT/DORMANT com orçamento; não simular cada NPC continuamente.
5. Servidor de sessão e modelos hospedados na máquina local do usuário, com jogadores pela rede privada/LAN ou VPN autenticada, sem exposição pública de portas.
6. Admin mostra proposta, evidências permitidas, autorização, ação, recibo e divergências; nenhum log de segredos distribuído a jogadores. 

## Consequências

- Requisitos nas SPECs devem citar este ADR e a pergunta de origem, com critério de aceite observável.
- Recursos mecânicos dependem de capability verificada na build do host, consentimento, idempotência e recibos; caso contrário `UNKNOWN` ou `BLOCKED_CAPABILITY`.
- Qualquer modificação material desta política deverá criar um ADR novo, mantendo este arquivo inalterado.
- Testes unitários sintéticos nunca serão descritos como validação de bridge, jogo ou multiplayer real.
