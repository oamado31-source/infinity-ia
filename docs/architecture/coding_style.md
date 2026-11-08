# Architecture — Coding style

- **Python proposto:** 3.12+, tipagem de domínio, `dataclass(frozen=True)` para DTOs, enum para estados; lógica pura para regras antes de I/O.
- **Lua/EEex:** adaptador mínimo, allowlist por build; nenhum hook inferido sem POC, nenhuma atualização de quest via logging ou UI.
- Arquivos com encoding UTF-8, paths relativos, funções pequenas e nomes em `snake_case` no Python.
- Separar `domain/`, `application/`, `adapters/` e `infrastructure/`; imports de domínio não dependem de runtime EEex.
- Contratos JSON com `schema_version`, `campaign_id`, `branch_id`, `host_epoch`, `build_fingerprint`, `observation_id`, `timestamp` e `visibility` quando aplicável.
- Nenhuma função interpreta `UNKNOWN` como `False`, nem duplica receipt; tratamento explícito de erros.
- Mudanças que impactem comportamento começam em SPEC + teste; PR inclui referência REQ/ADR, evidência e plano de rollback.
- Nunca publicar caminhos absolutos do usuário, secrets, credenciais, logs de conversa, dumps binários ou saves.
