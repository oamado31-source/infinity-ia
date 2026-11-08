# ADR-0038 — Mortalidade configurável, ressurreição e legado persistente

- **Decisão:** DEC-043 — morte, ressurreição e permanência dos personagens de jogadores (PCs).
- **Status:** **APROVADA — opção C**.
- **Aprovação:** 2026-11-06, escolha expressa do idealizador do Infinity AI.
- **Fase:** Discovery (não é SPEC aprovada nem funcionalidade implementada).
- **Versão do pacote:** Discovery v3.9.
- **Rastreabilidade:** DEC-001/003/004/005-R/008/009/011/012/014/019/020/021/022/025/027/028/029/030/034–042; ADR-0037; documento técnico `43-mortalidade-ressurreicao-e-legado-de-personagens.md`.

## Contexto

Morte e ressurreição fazem parte da experiência de BG2:EE, mas no Living World cada PC acumula relações, histórico autoral, reputação contextual, alinhamento, promessas e arcos pessoais. A decisão anterior DEC-042 aprovou permissões PvP configuráveis, sem equiparar permissão para duelo com morte permanente. É preciso equilibrar gravidade das consequências com a variedade de grupos e as limitações técnicas da Infinity Engine.

A **opção C** prevalece sobre políticas uniformes de morte sempre definitiva ou recuperação garantida.

## Decisão vinculante

1. **Mortalidade por campanha:** cada campanha Living World define, antes de expor jogadores a riscos graves, uma política clara de mortalidade e retorno. O ponto de partida é o comportamento nativo de BG2:EE/AD&D 2e; perfis alternativos são opt-in, versionados e condicionados a compatibilidade comprovada. Nenhuma campanha recebe permissões mais rigorosas por mudança silenciosa de perfil.
2. **Autoridade mecânica:** a morte, condição de retorno, aplicação de magia, consumo de recursos e restauração do controle do PC são fatos **mecânicos** cuja confirmação pertence ao host BG2:EE. O Infinity AI não mata, revive, converte ou remove um PC do save apenas por narrativa de LLM ou por projeção externa.
3. **Separação de estados:** não confundir derrota, inconsciência, morte mecanicamente comprovada, disponibilidade potencial de ressurreição, retorno efetivamente executado, morte definitiva conforme política, e resultado incerto. Estados e transições específicos são **candidatos a SPEC**, não uma promessa de interceptação do engine.
4. **Ressurreição sob condições:** retorno depende das regras e recursos válidos da campanha (magias, restrições de classe, custos, condições do corpo, local, tempo e decisões humanas quando aplicáveis), dos conteúdos/mods instalados e do aceite/resultado do host. Não prometer acesso universal nem ressurreição por texto da IA.
5. **Morte definitiva possível:** quando suportada, a morte pode encerrar a participação daquele PC, de acordo com condições conhecidas da campanha e efeitos comprovados. A decisão não torna obrigatório o permadeath em todos os grupos. A maneira de bloquear ou fazer cumprir modalidades alternativas é gate técnico crítico, especialmente em multiplayer.
6. **Regra PvP independente:** consentimento para ataques ou duelos **não** concede permissão implícita para eliminação permanente, perda de personagem, roubo de inventário ou alterações irreversíveis. A categoria de permadeath PvP exige a proteção específica de DEC-042, a política vigente e confirmação/consentimento apropriados dos participantes afetados. Anfitrião e LLM não consentem em nome de outro jogador.
7. **Legado persistente:** fatos *confirmados* sobre conquistas, sacrifícios, relações, obrigações, objetos, reputação e efeitos sobre facções permanecem na história da campanha quando um PC morre definitivamente. O sistema pode usar o legado para alimentar rumores, memoriais, quests ou reações de NPCs sem alegar que toda consequência será física ou imediata no BG2:EE.
8. **Conhecimento e privacidade:** morte não torna público todo o histórico secreto, diários privados, motivações ou fatos só conhecidos por agentes específicos. Informações e repercussões continuam sob DEC-019/020/028/029, com fonte, tempo, região e controle de acesso.
9. **Redenção, alinhamento e reputação:** morte/ressurreição não reescrevem a trajetória moral nem apagam efeitos legítimos; reputações e relações continuam contextuais. Consequências religiosas, limitações de retorno e transformações de classe dependem de regras específicas e validação de compatibilidade.
10. **Presença e agência:** nenhum diretor narrativo escolhe sacrifício, ressurreição, sucessão ou ações póstumas em nome de PC ausente. A simulação offscreen não pode declarar a morte mecânica de um PC sem evidência do host. Decisões de terceiros sobre recuperação do corpo/recur­sos exigem políticas e ações próprias, não consentimento fictício do falecido.
11. **Consistência e idempotência:** morte, retorno, inventário e consequências legadas são correlacionados por IDs, eventos e receipts; `UNCERTAIN` impede retry cego. Após reconectar ou restaurar saves, reconciliar com fingerprints e eventos do host antes de concluir morte definitiva, devolver equipamento ou ressuscitar novamente.
12. **Integridade do cânone:** impacto sobre NPCs canônicos, entidades históricas e grandes arcos segue DEC-034 e a política de risco; a morte de um PC não autoriza colapso automático de reinos nem retcons de Forgotten Realms.
13. **Modo Original isolado:** nenhum perfil alternativo, legado externo ou política de ressurreição do Living World afeta saves e regras do modo Original.
14. **Sem promessa de compatibilidade:** BG2:EE, EEex, multiplayer, mods, personagem protagonista, recursos de ressurreição e estados como morte irreversível exigem POCs específicos. Uma política que não puder ser imposta com segurança não deve ser anunciada como protegida.

## Perfis candidatos, não impostos

| Perfil ilustrativo | Intenção | Observação técnica |
|---|---|---|
| `classic_rules` | Manter morte/retorno conforme as regras efetivas da build BG2:EE | Regras exatas devem ser inventariadas; engine é fonte mecânica |
| `recoverable_campaign` | Campanha mais permissiva, com possibilidades de recuperação sob condições narrativas/mecânicas | **Não** garante retorno em todos os casos; precisar validar cada mecanismo |
| `lasting_consequences` | Maior peso para morte definitiva, com memória e legado persistentes | Permadeath, protagonista/game-over e integridade de save requerem POCs |

Nomes dos perfis são propostas para SPECS, não configuração já existente. Cada política terá versão e informação acessível aos jogadores.

## Invariantes

- Evento narrativo (`LEGACY_RECORDED`) não é uma alteração mecânica (`ENGINE_DEATH_CONFIRMED`/`ENGINE_RETURN_CONFIRMED`).
- O sistema não cria *clones* nem duplicação de itens, experiência ou recompensas ao reviver/carregar save.
- A morte não libera segredos privados indiscriminadamente nem transfere titularidade do PC.
- Os participantes não perdem seu direito de escolha por terem recusado PvP, quests ou redenção.
- Duelo consensual ≠ consentimento para morte permanente.
- A possibilidade de construir um novo personagem e os critérios de herança de bens/conhecimento/participação ainda **não estão decididos**: DEC-044.

## Gates candidatos e riscos

1. Testar morte/retorno em BG2:EE limpo (host e dois clientes) antes de ativar ponte narrativa que requeira mutações.
2. Distinguir derrota, morte retornável, morte não retornável e *game-over* do protagonista quando aplicável; não assumir o resultado de mods.
3. Verificar funcionamento de magias e recursos de ressurreição em cada build e classe/kit sem simular efeito irrealizável.
4. Conferir persistência de inventário, corpos, efeitos de área, loot, experiência, composição da party e save/load.
5. Falhas de confirmação e desconexões mantêm estado `UNCERTAIN`, sem reconciliação automática inventada.
6. Manter memórias, rumores e reputação conforme quem realmente viu/soube da morte e ressurreição.
7. Falha na interceptação de uma perda irreversível impede oferecer proteções como garantidas.
8. Testar segregação total entre modo Original e Living World e isolamentos entre campanhas.
9. Testar consentimento específico em PvP fatal, inclusive dano indireto e jogadores ausentes.
10. Testar políticas de recuperação mais permissivas apenas se seus hooks puderem ser demonstrados no motor real.

## Pendências para SPECS / próxima DEC

- Parametrização por campanha, defaults e alterações de política durante jogo.
- Matriz real de classes/magias/itens/mods e consequências de morte/resurreição.
- UX e recuperação quando o jogo força *game-over* ou impossibilita retorno físico.
- Quantificação de recursos, custos, limitações de nível, efeitos em companheiros e tempos.
- **DEC-044 (aberta):** substituição de PCs, continuidade do grupo, possível herança e conhecimento legítimo de um novo personagem após aposentadoria ou morte definitiva.

**Conclusão:** aprovada a política narrativa e de governança; nenhuma funcionalidade de mortalidade alternativa, ressurreição ou legado mecânico foi implementada.
