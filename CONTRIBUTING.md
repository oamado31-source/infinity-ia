# Contribuindo com Infinity AI

Obrigado por contribuir. O repositório canônico será público, mas **contribuições externas são propostas, não alterações diretas**.

1. Faça um fork para sua conta e crie uma branch com o desenvolvimento.
2. Leia Constitution, Domain, Architecture e a SPEC relevante antes de programar.
3. Abra Pull Request com REQ/SPEC/ADR, critérios de aceite, testes, riscos, licença e rollback.
4. Não altere nem apague ADR já aprovado; mudança arquitetural requer novo ADR/CR.
5. Não inclua arquivos originais de BG2:EE, mods de terceiros sem autorização, saves, credenciais, crash dumps, dados de players, imagens/vozes protegidas.
6. Nunca dependa de CI com acesso a secrets para PR externo. Mudança de workflow exige revisão do mantenedor.
7. Uma PR não é aceita automaticamente. Mantenedor decide merge após CI e revisão humana.

## Licença e origem das contribuições

O material original do Infinity AI licenciado pelo projeto utiliza a [Apache License, Version 2.0](LICENSE) (`Apache-2.0`); leia também o [NOTICE](NOTICE) e a [política sobre direitos de terceiros](docs/architecture/licensing.md).

Ao submeter intencionalmente uma contribuição para inclusão no projeto, ela é oferecida sob os termos da seção 5 da Apache-2.0, salvo declaração explícita em contrário aceita pelo mantenedor. Você mantém os direitos sobre sua contribuição; **envie somente conteúdo próprio ou com autorização e licença compatíveis**. Não copie código de GemRB, EEex, mods ou outros projetos apenas por serem públicos. Identifique dependências, licenças, atribuições e alterações relevantes no PR.

Novos arquivos-fonte originais devem preferencialmente conter `SPDX-License-Identifier: Apache-2.0`. Contribuições com ativos proprietários, segredos ou dados privados não serão aceitas.
