# ADR-0039 — Entrada contextual de novos personagens, progressão equilibrada e herança legítima

- **Decisão:** DEC-044 — sucessão de personagens e continuidade do grupo no Living World.
- **Status:** **APROVADA — opção C**.
- **Aprovação:** 2026-11-06, escolha expressa do idealizador do Infinity AI.
- **Fase:** Discovery / SDD, não é SPEC aprovada nem funcionalidade implementada.
- **Versão do pacote:** Discovery v4.0.
- **Rastreabilidade:** DEC-001/003/004/005-R/008/011/012/019/020/022/028/029/030/034/035–043; ADR-0038; desenho `44-entrada-de-personagens-sucessao-e-heranca-legitima.md`.

## Contexto

Na DEC-043 foi aprovada a morte/ressurreição configurável com legado persistente. O jogador de um personagem falecido definitivamente, aposentado ou afastado deve poder continuar a campanha com outra identidade **sem herdar automaticamente a biografia, o conhecimento, os itens e a posição social de seu antigo PC**. Ao mesmo tempo, não é desejável impor um personagem mecanicamente incapaz de participar de uma party avançada. BG2:EE não teve testada sua capacidade de introduzir e trocar PCs no fluxo real de multiplayer, especialmente após game-over do protagonista.

Alternativas avaliadas: **A**, novo PC independente com criação estritamente inicial, pouco ajustado ao grupo; **B**, sucessão automática de níveis, bens e relações, que desvaloriza o legado e produz transferências não autorizadas; **C**, integração contextual, progressão de entrada equilibrada e transferências condicionadas a causas e regras legítimas. **C foi escolhida.**

## Decisão vinculante

1. **Identidade própria:** cada PC sucessor/recém-chegado terá identidade estável, histórico autoral, alinhamento inicial conforme regras, crenças, reputação individual e relações próprias. O fato de ser controlado pelo mesmo jogador não o torna o PC antigo e não compartilha identidade diegética, conhecimento ou obrigações automaticamente.
2. **Âmbitos de entrada:** a política vale para substituição após morte definitiva, aposentadoria voluntária, abandono consentido de PC, entrada de participante novo e reintegração de jogadores na campanha, sem declarar que esses eventos compartilhem um mesmo mecanismo do engine.
3. **Narrativa contextual:** o Personal Story Director propõe ganchos de apresentação plausíveis por período, região, facção, conflitos e conhecimento já existente, usando o Cooperative Story Director para evitar cenas que retirem agência de outros PCs. O jogador controla escolhas e identidade do novo PC; a IA não inventa parentescos, pertencimentos, segredos ou atos pregressos que contrariem o histórico aprovado.
4. **Progressão equilibrada, não herança de XP:** a campanha poderá adotar critérios versionados de nível/faixa de experiência, equipamentos iniciais, recursos e limitações compatíveis com sua party, com tetos antiabuso. Não existe obrigação de começar no nível 1 **nem** transferência automática de XP do falecido. Regras quantitativas e perfis são pendências de SPECS.
5. **Inventário e espólio:** itens têm localização, titularidade, restrições, histórico e estado mecânico próprios. Um sucessor só recebe bens por entrega confirmada, espólio válido, doação, compra, saque ou outra causa autorizada pelas regras; nenhum pacote de herança é criado por renomear um personagem. Direitos de terceiros e regras de saque/PvP DEC-042 continuam em vigor.
6. **Conhecimento separado:** jogador humano pode lembrar eventos da campanha, mas conhecimento do **novo PC** depende de observação, ensino, documentos, rumores ou outra fonte legítima, submetida a ACL DEC-028 e propagação DEC-029. Logs e prompts não copiam segredos de PCs antigos para os novos só porque o controlador é o mesmo.
7. **Reputação e relações:** reputação contextual, alinhamento, dívidas, juramentos, inimigos e laços do antigo PC permanecem ligados a ele. Um novo personagem pode adquirir consequências relacionais justificadas — por exemplo, se for reconhecido como herdeiro ou aliado — mas **não** recebe automaticamente métricas, memória ou status social. A reputação nativa do BG2:EE não será modificada por inferência narrativa.
8. **Legado preservado:** morte definitiva/aposentadoria não apagam ações e histórias confirmadas do PC anterior. A sucessão não é retcon, não cria desfechos secretos arbitrários e não transfere automaticamente quests. O PSD poderá criar histórias *relacionadas* ao legado, desde que haja fonte/causa e autorização apropriadas.
9. **Titularidade e consentimento:** o novo jogador controla a ficha e o histórico do PC novo; não recebe autorização de editar ou retirar pertences de outros PCs. O anfitrião administra a política de entrada, sem falar ou decidir por jogadores. Um evento de herança pode exigir acordo ou ação de terceiros, não um consentimento presumido por vínculo de conta.
10. **Host e gateway:** criação/importação, inclusão/exclusão em party, XP, inventário, nível, transferências e distribuição de controle entre clientes são mudanças mecânicas sujeitas ao Action Gateway, permissão, capacidade comprovada e recibo do host. Nenhuma delas é realizada por LLM, texto narrativo ou edição direta não validada do save.
11. **Sucessão não é ressurreição:** retorno do PC antigo, restauração de save, reentrada de novo personagem e morte definitiva são processos distintos, com identidades e correlações próprias; reconciliar antes de confirmar estados mutuamente incompatíveis. Não duplicar itens, XP, personagem, slots ou quests.
12. **Limites de disponibilidade:** não assumir que BG2:EE/EEex permite hot-swap de PC, players drop-in, mudança do protagonista, mudança de dono de slot ou recuperação após game-over. Recursos não testados devem permanecer como objetivos condicionados a POCs com host e dois clientes, inclusive save/load. Se inviáveis, propor procedimentos compatíveis (ex.: entrada em ponto seguro validado), sem declarar automação existente.
13. **Regras e cânone:** criação respeita espécies, classes/kits, alinhamentos e regras efetivamente suportados pela build, período e mundo curado. Novos parentescos históricos, heranças de figuras canônicas ou títulos críticos não são aceitos sem curadoria e DEC-034.
14. **Segurança por campanha:** novas identidades ficam vinculadas a campanha, controlador autenticado e versão de política; vazamentos entre modo Original, campanhas ou personagens são proibidos. Em `UNCERTAIN`, congelar a ação crítica e reconciliar; nenhum retry cego que gere personagens/itens duplicados.
15. **Ausências não equivalem a substituição:** desconexão temporária não autoriza o sistema a declarar aposentadoria, permadeath ou criar um substituto. Regras de continuidade em sessão quando um jogador sai ou cai a conexão ficam para **DEC-045**.

## Invariantes de design

- `PLAYER_ID != PC_ID`: continuidade do jogador humano não implica continuidade de identidade, conhecimento ou propriedades do personagem.
- `STORY_INTRODUCED != ENGINE_PARTY_MEMBER`: uma cena proposta não significa que o engine já adicionou o PC à party.
- `INHERITANCE_CLAIM != INVENTORY_TRANSFER_CONFIRMED`: reivindicar espólio não significa possuir o item.
- Nível de entrada depende de política legítima, não de cópia de XP de uma pessoa falecida.
- O legado histórico continua pertencendo à linha de eventos da campanha; novo personagem não apaga nem assume autoria de feitos antigos.
- Falhas de criação/transferência/party exigem reconciliação antes de publicar efeitos externos.

## Perfil conceitual de integração (para futuras SPECS)

| Aspecto | Princípio aprovado | Detalhe não escolhido |
|---|---|---|
| Protagonismo | Entrada diegética coerente, sem forçar missões | Locais/gatilhos e prioridades |
| Nível/recursos | Regra por campanha para compatibilidade do grupo | Faixa, teto, XP e orçamento de itens |
| Ficha/identidade | Histórico e atributos novos, owner autenticado | Processo de importação, race/class/kit |
| Espólio | Direito comprovado, transação autorizada | Leis locais e mecanismo de distribuição |
| Memória | ACL e proveniência, sem transferência por conta | Política de metaconhecimento e interface |
| Entrada no engine | Só após POC de host/multiplayer | Hot-join, party-slot, game-over, save workflow |
| História do PC anterior | Legado persistente com fatos preservados | Tratamento de arcos interrompidos |

## Gate de implementação

1. Demonstrar em **BG2:EE limpo**, host e dois clientes, a sequência factível de criação/importação, troca e inclusão de PC em partida em andamento.
2. Comprovar restrições de protagonista, número de slots, propriedade de PC, distribuição de controle, efeitos de game-over e persistência dos novos IDs.
3. Verificar classes, kits, experiência, equipamento inicial e limites reais por instalação/modlist (EET e outros somente após baseline).
4. Testar herança e transferências de inventário com host receipt, queda de conexão e reinício sem duplicações.
5. Testar sigilo de PCs antigos em prompts, memória, UI e logs de PCs sucessores e demais jogadores.
6. Verificar que novas personagens não herdam reputação, alinhamento ou quests por confusão de índices/slots.
7. Garantir que o modo Original e outras campanhas permaneçam isolados.
8. Quando o jogo não suportar entrada segura, não ofertar recurso como automático; definir fallback e linguagem de limitação.

## Pendente

- SPECS: regras de progressão, recursos, limites de recrutamento/troca, objetivos narrativos e gestão de espólio.
- POCs: BG2:EE/EEex, multiplayer, save/load, identidade e game-over.
- **DEC-045 (aberta):** política de ausências, desconexões e retomada de participação de um jogador sem violar agência ou colocar o PC em risco não consentido.

**Conclusão:** aprovada a arquitetura de sucessão contextual, sem promessas de troca automática de PCs no motor ou redistribuição automática de itens.
