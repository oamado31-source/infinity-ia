# Architecture — Visão executável e limites

## Topologia alvo (etapa 1 em single player; clientes na etapa 2, ADR-0113)

```
BG2:EE Windows (host + 2 clientes)
          │
       EEex (dependência externa, instalação do usuário)
          │ ONLY allowlisted observations, when proven
  Game bridge/adapters (Lua candidate; fail-closed)
          │ typed envelopes + authenticated session
  Infinity AI backend (Python candidate)
          ├── SQLite/event log/snapshots
          ├── Domain rules + capability registry
          ├── NPC memory/knowledge ACL
          ├── Local LLM router (no host mutations)
          └── Dialog overlay (text baseline)
                   ├── player microphone push-to-talk → local STT (optional)
                   └── NPC reply text → local TTS (optional)
```

**Candidatos de tecnologia** (não capacidades de jogo comprovadas): Python 3.12 para backend, stdlib primeiro, SQLite com migração, typed JSON contracts; Lua no adaptador EEex; frontend overlay externo em tecnologia a decidir após POC Windows. C++ apenas se necessidade/benchmark validado.

## Regras de integração
- BG2:EE é software instalado legalmente pelo jogador, fora do repo.
- Não acoplar a interface do host ao protocolo interno de GemRB ou ao executável da Beamdog.
- Cada adaptador implementa contrato comum e anuncia capability por fingerprint; sem fingerprint válido, retornar UNKNOWN/BLOCKED_CAPABILITY.
- Mods e engines alternativos entram como adaptadores novos, não alteração de núcleo.
- Primeiro teste prova BG2 vanilla → EEex → leitura allowlisted em single player (etapa 1); host + 2 clientes na etapa 2 (ADR-0113).
- Nenhuma função de áudio confere permissão de Action Gateway ou altera quest original.

## Desenho evolutivo
Adaptadores experimentais de GemRB podem residir em repositórios separados sob condições de licença; importação de código GPL requer avaliação de distribuição e arquitetura. Sem commit de binários de jogos.
