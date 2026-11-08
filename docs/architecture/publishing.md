# Publicar o Infinity AI no GitHub (após validação)

**Repositório canônico:** `oamado31-source/infinity-ia`, público. Já existe; importação no PR #3 `bootstrap/sdd-v11`. Não fazer push direto para `main`.

## Antes de publicar

1. Confirmar estratégia (novo repositório independente recomendado; não forkar GemRB ou EEex como base da V1).
2. Escolher licença SPDX adequada ao código próprio (`LICENSE-PENDING.md`); analisar dependências GPL e EEex antes de usar código desses projetos.
3. Inspecionar o histórico das 105 ADRs, docs e fixtures para qualquer material privado, senhas, tokens, dados de terceiros ou conteúdo de jogo protegido. O script básico não substitui revisão humana.
4. Usar apenas fontes próprias: não enviar diretório do jogo, saves, áudio gravado, logs reais ou executáveis do EEex.

## Publicação via Git local

O repositório já existe e tem `main` protegida. **NÃO execute os comandos abaixo que inicializam outro repositório ou enviam para `main`**; use `IMPORTAR_INFINITY_AI.command` para atualizar o PR #3. Os comandos a seguir são mantidos como referência histórica, não instrução atual:

```bash
git init -b main
git add .
git commit -m "chore: bootstrap Infinity AI SDD with validated ADR baseline"
git remote add origin https://github.com/oamado31-source/infinity-ia.git
git push -u origin main
```

Não executar esses comandos se ainda existir material sensível ou não houver licença/autorizações para a publicação.

## Configuração obrigatória no GitHub

- Settings → Branches / Rulesets → proteger `main`: PR obrigatório, revisão humana e status checks; não permitir deletar nem force push, evitar bypass conforme plano e permissões.
- Usar `CODEOWNERS` para pedir revisão (não é regra de proteção por si só).
- Não conceder acesso Write/Maintain/Admin para colaboradores ocasionais; forks e PRs permitem contribuição sem essa permissão.
- Ativar private vulnerability reporting, GitHub Actions CI e revisão de dependências.
- Fazer snapshot externo assinado/versionado do ZIP e reter cópias de backups de acordo com política do projeto.

## Critério de sucesso

Verificar remotamente visibility=PUBLIC, branch default=main, proteções efetivas, CI concluído, ADRs intactos, licença explícita e ausência de assets/segredos.
