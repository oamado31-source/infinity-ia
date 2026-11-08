# Infinity AI — Spec-Driven Development (SDD)

Projeto público independente do motor original Infinity Engine. Repositório canônico: https://github.com/oamado31-source/infinity-ia. Integração via adaptadores BG2:EE/EEex; forks de motores podem ser usados apenas em provas separadas.

## Navegação
- `docs/domain/context.md`, `docs/domain/glossary.md` — regras de produto e termos.
- `docs/architecture/constitution.md`, `context.md`, `security.md`, `coding_style.md`, `testing.md` — guardrails.
- `docs/decisions/ADR-*.md` — 105 ADRs históricos imutáveis, mais ADRs novos do questionário.
- `specs/*/{spec,plan,tasks}.md` — features incrementais.
- `templates/`, `skills/`, `features/` — autoria, agentes de revisão e roadmap.
- `.github/`, `CONTRIBUTING.md`, `SECURITY.md` — contribuições públicas via forks/PRs.

## Status técnico
Arquitetura aprovada e código sintético; nenhuma bridge real Windows+EEex+2 clientes provada. Voz push-to-talk com STT/TTS é requisito aprovado **para fase posterior à UI texto funcional**.

## Não distribuir
Conteúdo protegido da Beamdog/Wizards, saves e mods de terceiros sem licença, credenciais, microfone/vozes privados. O software e a documentação originais elegíveis são licenciados sob **Apache-2.0**; consulte [`LICENSE`](LICENSE), [`NOTICE`](NOTICE) e [`docs/architecture/licensing.md`](docs/architecture/licensing.md). Direitos de terceiros permanecem excluídos.

## Primeiro ciclo
Read-only bridge e manifesto → host e dois clientes → SQLite/event memory → NPC dialogue texto → voz opcional. Leia `docs/architecture/roadmap.md`.

## Publicação

Leia [`docs/architecture/publishing.md`](docs/architecture/publishing.md). O repositório público https://github.com/oamado31-source/infinity-ia já foi criado. O ruleset `protect-main` está ativo e exige o status check `tests` para integração por Pull Request.
