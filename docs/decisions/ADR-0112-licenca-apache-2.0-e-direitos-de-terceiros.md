# ADR-0112 — Licença Apache-2.0 para materiais originais e proteção de direitos externos

**Estado:** APROVADA (decisão explícita do mantenedor, 2026-11-08).  
**Origem:** encerramento da pendência administrativa registrada em ADR-0111 e
Constitution v1.0, item 8.  
**Escopo:** licenciamento e governança de publicação; não valida capacidades de BG2:EE,
EEex ou multiplayer.

## Contexto

O Infinity AI publica documentação SDD, código sintético e contratos de interfaces
independentes do jogo. A baseline v11.0 foi inicialmente publicada sem licença
expressa, indicada em `LICENSE-PENDING.md`. A escolha precisava facilitar a
colaboração sem transferir direitos sobre motores, mods ou propriedade intelectual
de jogos de terceiros.

## Decisão

1. Adotar a **Apache License, Version 2.0** (`Apache-2.0`) para o código próprio,
   documentação original, scripts, testes e fixtures sintéticas do Infinity AI,
   exclusivamente na medida em que seus titulares tenham direitos para licenciá-los.
2. Publicar o texto integral em `LICENSE`, incluir `NOTICE`, atualizar o
   `pyproject.toml` e as orientações de contribuição.
3. Excluir da concessão de direitos obras, marcas, conteúdos e softwares de
   terceiros. BG2:EE, Forgotten Realms, EEex, GemRB e outros projetos continuam
   sujeitos a licenças e permissões próprias. Não venderizar arquivos do jogo.
4. Exigir inventário e revisão de licença/proveniência antes de incorporar
   dependências, especialmente código de terceiros com copyleft ou obrigações
   adicionais de redistribuição.
5. Integrar a decisão pelo procedimento normal: branch, PR, revisão e check
   `tests` antes de merge na `main`.

## Consequências e rastreabilidade

- A pendência de licença do software próprio descrita no ADR-0111, item 5, e
  na Constitution v1.0, item 8, fica **resolvida por esta nova decisão**;
  a referência ao estado anterior permanece no registro histórico imutável.
- A decisão **não altera** a estratégia de repositório independente versus
  fork além do que já está publicado, nem valida uma bridge ou jogo executável.
- Arquivos originais sob Apache-2.0 podem receber melhorias sob os termos da
  própria licença; isso não confere direitos de marca nem autorizações sobre
  assets de terceiros.
- Mudança futura desta política requer novo ADR/CR, sem reescrever os
  registros históricos.

## Plano de mudança / rollback

- Mudança: adicionar `LICENSE`, `NOTICE` e política de terceiros; atualizar
  README, README-SDD, CONTRIBUTING, metadados e publicação; retirar aviso
  operacional `LICENSE-PENDING.md`.
- Validação: verificar texto integral Apache-2.0, metadata SPDX, preservação
  dos ADRs históricos, ausência de arquivos protegidos e CI `tests`.
- Rollback técnico: reverter o commit mediante novo PR, se necessário.
  **A revogação de licenças já concedidas para cópias anteriores não decorre
  automaticamente de uma reversão futura**; consultar assessoria jurídica
  antes de qualquer tentativa de relicenciamento ou mudança retroativa.
