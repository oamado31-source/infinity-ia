# Architecture — Repositório público, governança e publicação

**Decisão do usuário:** repositório GitHub **público**, com contribuições externas aceitas. Contribuidores sem acesso de escrita no repositório canônico; usar forks + branches + pull requests.

**Estratégia de publicação materializada:** repositório independente e público https://github.com/oamado31-source/infinity-ia; EEex/WeiDU referenciados externamente; GemRB como referência ou investigação. Decisões técnicas futuras de motor permanecem sujeitas a ADR.

## Administração real obrigatória no GitHub
1. Usar `oamado31-source/infinity-ia` público, idealmente com licença escolhida e documentação sanitizada, sem dados do jogo.
2. `Settings > Branches / Rulesets`: proteger `main` contra alterações diretas, exclusões e force pushes; exigir PR, CI, conversa resolvida, reviews e **não permitir bypass** conforme controles disponíveis no plano.
3. Não conceder `Write/Maintain/Admin` a contribuidores externos; forks e PRs dispensam permissão de escrita no upstream.
4. `CODEOWNERS` sugere revisores; não impede mudanças **sem regras de proteção e revisão efetiva**.
5. Workflows de PR usar `pull_request` com `permissions: contents: read`, jamais `pull_request_target` que execute código externo com secrets.
6. PR que edita `docs/decisions/ADR-*.md` aprovado deve ser rejeitado; criar ADR novo para supersessão, sem apagar antigo.
7. Nunca publicar tokens, saves, WeiDU logs privados, copyrighted game assets, mapas originais protegidos, vozes gravadas sem permissão, modelos não licenciados.
8. Contribuições aprovadas entram na `main` somente após revisão; histórico Git preserva versões, mas proprietários/admins ainda podem alterar configurações ou apagar repo — backups independentes são necessários.

## Estado remoto
Repositório remoto verificado e regras `protect-main` ativas (PR, review, CODEOWNERS, bloqueios de force-push e exclusão). Exigir o status check `tests` somente após primeiro CI do PR #3. Bypass administrativo condicionado a pull requests.
