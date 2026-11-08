# Publicação e governança do Infinity AI no GitHub

**Repositório canônico:** [oamado31-source/infinity-ia](https://github.com/oamado31-source/infinity-ia), público.  
**Baseline:** Discovery SDD v11.0 integrado na `main` pelo PR #3.  
**Política:** não fazer push direto para `main`; criar branches e Pull Requests.

## Estado do licenciamento

A decisão **ADR-0112** aprovou `Apache-2.0` para os materiais originais
elegíveis do Infinity AI. Consulte `LICENSE`, `NOTICE` e
[`licensing.md`](licensing.md). O antigo `LICENSE-PENDING.md` foi retirado
porque descrevia uma pendência já resolvida.

Não distribuir binários, saves, scripts, mods, dados nem assets originais de
BG2:EE/EEex ou outras ferramentas de terceiros sem direitos e revisão específica.
A licença do código próprio não muda os termos de GemRB, EEex, WeiDU ou dos jogos.

## Fluxo de alterações

1. Atualizar `main` localmente e criar uma branch por alteração.
2. Vincular mudanças funcionais à SPEC, REQ e ADR/CR apropriados; **não editar
   ADRs históricos ratificados**.
3. Abrir Pull Request com motivação, escopo, testes, riscos e rollback.
4. Aguardar `tests` no GitHub Actions e revisão conforme `protect-main`.
5. Integrar pelo método permitido no repositório; verificar CI pós-merge.
6. Preservar backups e conferir a ausência de material sensível e de terceiros.

Para atualizações futuras, não reutilizar o script de importação inicial
para sobrescrever a `main` ou reabrir o PR #3, já encerrado.

## Verificações de publicação

- A `main` deve continuar protegida e exigir o status check `tests`.
- A verificação automatizada de extensões e arquivos proibidos é básica e
  **não substitui auditoria humana de origem, licença e dados sensíveis**.
- Novas dependências exigem inventário de versão, licença e obrigações.
- Alterações de workflow GitHub Actions devem ser revisadas com atenção a
  permissões, segredos e execução em PRs externos.
- As integrações reais Windows + EEex + dois clientes continuam sujeitas
  às evidências e gates descritos nas SPECs.
