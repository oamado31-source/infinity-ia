# Roadmap orientado por SPECs e gates

**Ordem vigente:** ADR-0113 (single player primeiro, multiplayer na etapa 2), que substitui parcialmente a ordem do ADR-0108 sem alterá-lo.

## Etapa 1 — single player (primeiro marco jogável)

- `SPEC-001` bridge read-only e manifesto de build — P0, P1 e P2 aprovados no laboratório ARM64 (CR-2026-001).
- `SPEC-003` SQLite/event log, memória NPC mínima, save/load com épocas.
- `SPEC-004` UI overlay texto; voz push-to-talk STT/TTS local como incremento planejado.
- `SPEC-005` canon 1369 DR e mapas exploráveis do BG2:EE com fonte curada.

Critério de entrega (ADR-0113 item 2): observação segura, memória NPC persistente, save/load coerente, auditoria e zero efeito não autorizado numa instância single player. Contratos mantêm host, PC, campanha, branch e época (ADR-0113 item 4).

## Etapa 2 — multiplayer cooperativo

- `SPEC-002` autoridade host + clientes, consentimentos, receipts e épocas.
- Gate P4: P4a anfitrião + 1 cliente, depois P4b anfitrião + 2 clientes (ADR-0108), e repetição em máquinas distintas para afirmar suporte de rede real.
- Reavaliar o caminho de ações mecânicas compartilhadas: o EEex não suporta multiplayer para mudanças que não sejam só do cliente (Bubb13/EEex#37).

## Dependências críticas

P0 vanilla → P1 EEex → P2 bridge read-only → memória NPC e save/load (single player) → diálogo contextual (single player) → canon → **etapa 2:** P4 multiplayer read-only com save/load → ações com consentimento e receipts. P3 mutação de teste é trilha isolada (explorável em single player), nunca requisito de ler ou conversar.

## Seguinte (sem bloquear a etapa 1)
- Uma quest original mapeada semanticamente quando leitura permitida.
- Primeiro evento paralelo do usuário, somente proposta sem spawn até POC.
- Expansões EET/IWD/NWN e modos de combate alternativos após gates próprios.
- Economia/facções agregadas, escrow, justiça dinâmica e eventos críticos sob contratos existentes.


## Extensão proposta SPEC-006 — contato com qualquer habitante (Living World)

Após segurança da bridge/estabilização de tempo: POC read-only de seleção e tentativa de diálogo em pessoas comuns; emitir `NpcDialogueStarted` observado com prova de alvo/cena; provisionar persona/alinhamento no primeiro contato; manter personalidade de figurante somente no escopo do encontro até identidade `VERIFIED`; quando verificada, atribuir snapshot append-only por campanha/branch; responder via overlay local sem comprometer scripts/quests originais. A rota e o núcleo sintético já existem no PR da SPEC-006; **o hook in-game e o gate real ainda não**.
