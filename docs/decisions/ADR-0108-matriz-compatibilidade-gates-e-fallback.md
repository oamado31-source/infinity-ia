# ADR-0108 — Builds pinadas, POCs com gates e fallback sem falsas capabilities

**Estado:** APROVADA COMO POLÍTICA / ESCOPO em 2026-11-07, com base no questionário Q01–Q28 ratificado pelo idealizador.  
**Decisões:** DEC-013, DEC-015 / Q02=B, Q03=B, Q05=B, Q11=A, Q21=B, Q22=B, Q28=B. **Baseline:** Discovery v10.6 → SDD v11.0.  
**Referências anteriores:** DEC-002/003/005-T/011/012/050–054/099–102; Q02, Q03, Q05, Q11, Q21, Q22, Q28.  
**Gate:** documentação é política aprovada, **não uma capability comprovada no BG2:EE/EEex**.

## Contexto e alternativas

O questionário consolidado registrou escolhas explícitas para evitar bloqueio indefinido do Discovery. A opção escolhida não elimina mecanismos de segurança nem substitui ADRs anteriores: ela restringe a estratégia de implementação do MVP e da V1.

## Decisão vinculante

1. Plataforma inicial: BG2:EE Windows limpo; EEex separado; bridge read-only isolada; depois host e dois clientes coerentes inclusive save/load; hashes/build/modlist/manifesto fixados.
2. Gates P0 jogo vanilla → P1 EEex loader → P2 bridge allowlisted read-only → P3 mutação reversível **somente em save descartável e se autorizada** → P4 validação host+2 clientes e recuperação.
3. Sem EEex/bridge comprovada: desenvolver simulador e testes de contrato; **não migrar automaticamente** para GemRB, nem declarar integração operacional.
4. Expandir para EET/IWD/NWNForBG apenas após gate BG2:EE e regressão por pacote de mods; combate nativo como baseline, turnos opcionais trilha experimental separada.
5. Critérios de entrega: dois clientes, observação segura, memória NPC, save/load, auditoria, zero efeito não autorizado; pontos não comprovados permanecem bloqueados. 

## Consequências

- Requisitos nas SPECs devem citar este ADR e a pergunta de origem, com critério de aceite observável.
- Recursos mecânicos dependem de capability verificada na build do host, consentimento, idempotência e recibos; caso contrário `UNKNOWN` ou `BLOCKED_CAPABILITY`.
- Qualquer modificação material desta política deverá criar um ADR novo, mantendo este arquivo inalterado.
- Testes unitários sintéticos nunca serão descritos como validação de bridge, jogo ou multiplayer real.
