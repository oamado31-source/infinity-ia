# Plan — SPEC-004

1. Definir schemas e amostras sintéticas da feature; registrar status POC pendente.
2. Desenvolver função de domínio pura + unit tests de falhas e ACL.
3. Criar adaptador com interfaces e contrato, sem acoplar a recursos internos não observados do BG2:EE.
4. Aplicar gate da matriz P0–P4 quando relevante; recolher log redacted e hashes.
5. Atualizar rastreabilidade REQ→teste→evidência e abrir CR quando plano exigir novo comportamento.

**Riscos:** versão inválida, informação incompleta, vazamento de memória, consentimento implícito, save/load, multiplayer, direitos de ativos de terceiros.
