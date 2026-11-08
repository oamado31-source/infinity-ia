# ADR-0005 — Windows nativo como ambiente prioritário de execução e testes

- **DEC associada:** DEC-002
- **Estado:** **APROVADA — opção A (Windows nativo)**
- **Data de aprovação:** 2026-11-06
- **Domínio:** plataforma de execução, integração com Infinity Engine, ambiente de desenvolvimento e operações
- **Fundamentação:** escolha explícita do idealizador no planejamento do Infinity AI.
- **Âmbito:** primeiro protótipo técnico e testes de validação, com BG2:EE como candidato a motor.

## Contexto

O protótipo do Infinity AI pretende reaproveitar conteúdo de BG2:EE / EET, integrar ferramentas de modding e conectar componentes externos de IA, armazenamento e validação de eventos. A capacidade experimental depende de EEex e possivelmente EEex Remote Console, cujas compatibilidades variam por sistema operacional, versão do jogo e do próprio extender.

A documentação de EEex informa suporte **nativo completo no Windows**, **parcial no Linux via Proton/Wine** e **limitado no macOS via CrossOver**. Windows reduz uma categoria de incertezas iniciais, mas **não valida** automaticamente compatibilidade entre versões, mods ou sincronização multiplayer.

## Decisão aprovada

1. **Ambiente primário:** executar BG2:EE e os primeiros testes de integração (EEex e pontes compatíveis) em **Windows nativo**.
2. **Primeiro host de testes:** quando aplicável, o computador Windows poderá abrigar a sessão cooperativa e o controlador de integração; localização final dos serviços e topologia de rede ainda não foram escolhidas.
3. **Separação de responsabilidades:** motor do jogo, bridge de integração, controlador de ações, modelos de IA e persistência devem ser conceitualmente separados por contratos. O agente de IA não terá acesso direto a executáveis, arquivos de instalação ou comandos Lua arbitrários.
4. **Portabilidade futura:** documentar interfaces para permitir desenvolvimento de componentes independentes em outro SO, execução remota da IA e eventual suporte a Linux/macOS, sem exigir compatibilidade multiplataforma para concluir o primeiro marco.
5. **Isolamento de instalação:** testes devem ocorrer em **cópias dedicadas** dos jogos legítimos, sem sobrescrever saves ou instalações originais. Backups, rollback e manifesto de versão são obrigatórios antes de mutações.
6. **Versões fixadas:** não declarar versão específica do Windows, jogo, EEex, Remote Console ou distribuição como aprovada sem coleta de dados do ambiente e prova de compatibilidade. Fixar matriz e checksums quando a instalação real for escolhida (DEC-013).
7. **Capacidade multiplayer:** trabalhar inicialmente com o grupo cooperativo da DEC-001. Qualquer evento criado por integração externa precisa provar sincronização com dois clientes antes de ser declarado apto para multiplayer.
8. **Sem produção antecipada:** esta decisão não autoriza instalação, execução de testes reais nem início de código de produção antes dos respectivos gates e SPECS.

## Consequências

**Positivas:** menor risco inicial de incompatibilidade de EEex; depuração mais simples da integração nativa; instalação mais próxima do ambiente documentado das ferramentas; mantém a preferência visual pelo BG2:EE.

**Custos/restrições:** depender de uma máquina Windows nos testes; outros sistemas serão considerados portabilidades futuras; versões do jogo e mods podem permanecer conflitantes mesmo no Windows; separação IA/jogo exige contratos e validação de comunicação.

## Alternativas consideradas

- **B — macOS/CrossOver:** não selecionada para os primeiros testes devido ao suporte limitado de EEex. Desenvolvimento de documentos e serviços independentes no Mac continua permitido.
- **C — Linux/Proton ou Wine:** não selecionada como ambiente prioritário por introduzir uma camada extra de compatibilidade. Poderá ser reconsiderada após validação do MVP.

## Requisitos e gates candidatos (a detalhar em SPECS)

| ID | Teste ou exigência | Critério preliminar |
|---|---|---|
| CAND-ENV-001 | Inventário de ambiente | Registrar Windows (edição e versão), arquitetura, hardware, fonte do jogo e versões de BG2:EE e mods, sem segredos pessoais. |
| CAND-ENV-002 | Instalação isolada | Cópia de testes reproduzível, instalação original e saves existentes intactos. |
| CAND-ENV-003 | Baseline do jogo | Iniciar BG2:EE sem mods e abrir/criar um save de teste sem erro. |
| CAND-ENV-004 | EEex sozinho | Lançar pela ferramenta correta para a versão escolhida e confirmar funcionamento no ambiente fixado. |
| CAND-ENV-005 | Leitura inofensiva externa | Bridge consulta estado permitido sem modificação e registra resultado e versão. |
| CAND-ENV-006 | Segurança de comunicação | Agente só propõe ações estruturadas; controlador rejeita comandos fora da allowlist; não aceitar Lua diretamente do modelo. |
| CAND-ENV-007 | Teste multiplayer de integração | Dois clientes observam estado consistente de uma ação aprovada; falha impede avanço da feature multiplayer. |
| CAND-ENV-008 | Recuperação | Restaurar baseline ou snapshot após instalação malsucedida, sem afetar o modo Original. |

## Pendências explicitamente não decididas

- DEC-003 — estratégia de instalação e expansão: BG2:EE mínimo, EET primeiro ou pacote completo.
- DEC-006 — provedor e localização de modelos de IA.
- DEC-011 — autoridade e topologia multiplayer.
- DEC-012 — autenticação da bridge, permissões e isolamento operacional detalhado.
- DEC-013 — matriz exata de versões, gerenciador de mods e mecanismo de atualização/rollback.
- DEC-015 — plano de testes e gates definitivos.
- Dados da máquina Windows e cópias legais instaladas serão levantados no momento oportuno; não pressupor que já existam.

## Referências oficiais verificadas em 2026-11-06

- EEex README: https://github.com/Bubb13/EEex/blob/master/README.md
- EET documentação: https://github.com/Gibberlings3/EET/blob/master/EET/readme-EET.html
- IWD1_EET README (ordem indicativa dos mods): https://github.com/The-Gate-Project/IWD1_EET
- NWNForBG README (componentes e compatibilidade): https://github.com/abalabokhin/NWNForBG

## Relações

- **DEC-001/ADR-0001:** multiplayer cooperativo primeiro.
- **DEC-004/ADR-0002:** modos Original e Living World isolados.
- **DEC-019/ADR-0003:** proteção de segredos e conhecimento.
- **DEC-020/ADR-0004:** históricos versionados e fatos confirmados preservados.
- **DEC-002/ADR-0005:** ambiente de execução Windows — esta decisão.

**Próxima discussão:** DEC-003 — ordem das provas de conceito e integração do conteúdo EET, IWD e NWNForBG.
