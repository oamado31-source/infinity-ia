# ADR-0032 — Consequências progressivas e validadas da mudança de alinhamento

- **Decisão:** DEC-037 — efeitos mecânicos de alterações de alinhamento.
- **Estado:** **APROVADA — opção B**.
- **Data:** 2026-11-06.
- **Decisor:** idealizador do Infinity AI, aprovação expressa nesta conversa.
- **Escopo:** personagens dos jogadores no **Living World**; personagens clássicos e NPCs não recebem alterações mecânicas por esta aprovação.
- **Vínculos:** DEC-035/ADR-0030 (alinhamento mutável), DEC-036/ADR-0031 (avaliação contextual), DEC-005-R/ADR-0018 (AD&D 2e e módulos), DEC-005-T (turnos opcionais com POCs), DEC-011 (host autoritativo), DEC-012 (Action Gateway), DEC-030 (reputação independente), DEC-008 (persistência), DEC-020 (versionamento), DEC-027/034 (riscos e cânone).

## Contexto

O sistema narrativo aprovado pode reconhecer que um personagem evoluiu de Lawful Good para outra orientação. Entretanto, em BG2:EE uma alteração efetiva do campo de alinhamento pode afetar restrições de classes/kits, habilidades, magias, equipamentos, scripts e condições especiais como **fallen**, conforme regras aplicáveis a cada classe. Os efeitos reais devem ser investigados em instalação controlada: não presumir que uma escrita arbitrária no atributo tenha todos os efeitos corretos ou possa ser revertida sem risco.

Precisamos permitir consequências reais de escolhas éticas e morais, mas sem punir por tendências ainda incertas, corromper saves, perder sincronismo multiplayer ou permitir que o modelo generativo edite diretamente a mecânica.

## Decisão

1. **Opção B aprovada — consequências progressivas, explícitas e validadas.** O sistema acompanha a tendência moral/ética pelas regras da DEC-036; somente uma **transição confirmada** pode iniciar a avaliação de consequências mecânicas. Tendência narrativa, mudança consolidada e execução física no host são estados diferentes.
2. **Política mecânica vinculada à campanha:** antes de jogar, a campanha deve informar de forma compreensível que transições podem afetar classes, poderes, restrições, magias e itens, quando o módulo estiver disponível. Perfil e versão de regra ficam presos à campanha/save; trocar políticas exige procedimento de migração/consentimento, nunca atualização silenciosa.
3. **Sem imunidade a consequências:** a gradação oferece contexto, estabilidade e aviso, **não** uma opção livre de cancelar penalidades legítimas depois de ações deliberadas. O caminho de redenção e eventual recuperação de poderes fica para a DEC-038/SPECS e deve respeitar as regras/meios permitidos da campanha.
4. **Motor e gateway:** apenas ações mecânicas em allowlist, validadas pelo Action Gateway e confirmadas pelo host, podem alterar atributos ou estados de classe. LLM não decide perda de habilidade, não grava alinhamento no BG2:EE e não modifica classe/kit/inventário.
5. **Classificação de impacto por dependência:** examinar a classe/kit, possíveis códigos religiosos/juramentos, seleção de magias, efeitos ativos, itens com restrição de alinhamento, diálogos e regras de mod aplicáveis. Não aplicar automaticamente a mesma consequência a todas as classes ou a todo o grupo.
6. **Avisos proporcionais:** quando um personagem se aproxima de uma transição relevante, o usuário pode receber indicação clara, adequada à informação de que seu personagem dispõe, sem revelar segredos de outros NPCs nem metaconhecimento. Aviso não constitui efeito mecânico nem garantia de que uma mudança será bloqueada.
7. **Gates técnicos obrigatórios:** antes de qualquer escrita no motor, demonstrar em instalação de teste BG2:EE/EEex e multiplayer: leitura do alinhamento, mudança validada e efeitos da classe, persistência, retorno ao save, diferenças de versão de mod, cooperação com host e rollback/reconciliação. Até aprovação da SPEC/POC, **somente projeção narrativa é permitida**; o estado mecânico fica `PENDING_TECH_VALIDATION` ou equivalente.
8. **Ambiguidade e concorrência:** avaliações `NEEDS_REVIEW` não podem gerar sanção mecânica; resultados `UNCERTAIN` da bridge não podem ser interpretados como sucesso nem repetidos cegamente. Toda mudança física precisa de receipt do host, ação idempotente e conciliação com o save ativo.
9. **Separação de reputação e histórico:** alinhamento não é reputação e não se altera por acusação falsa ou rumor; nunca expor ao NPC/player não autorizado a causa privada de uma avaliação. Ações dos demais jogadores não alteram as habilidades de terceiros sem causalidade comprovada.
10. **Preservação do modo Original:** o módulo do Living World não muda o comportamento das campanhas/saves Original ou qualquer personagem em campanha não autorizada.

## Máquina de estados candidata (não implementada)

```text
CONFIRMED_EVENT -> CONTEXT_REVIEW -> ALIGNMENT_TREND
                                       |
                                 transition confirmed
                                       v
                               CONSEQUENCE_PREFLIGHT
                              /          |             \
                           SAFE       UNCERTAIN       UNSUPPORTED
                            |            |                 |
                     GATEWAY_REQUEST  RECONCILE          NARRATIVE_ONLY
                            |
                        HOST_RECEIPT
                         /        \
                    CONFIRMED     FAILED / UNCERTAIN
                        |               |
                  MECHANICAL_COMMIT   RECONCILE (no blind retry)
```

O estado `SAFE` significa somente que passou por validações; não é autorização humana implícita. A autorização final segue o perfil da campanha, o gateway e o tipo de risco.

## Exemplos hipotéticos, sem efeitos de engine aprovados

- Paladino que abandona os critérios da classe: a tendência narrativa é registrada; eventual perda de poderes ou status especial só é aplicada por módulo validado, conforme regras de BG2:EE.
- Clérigo cuja trajetória entra em conflito com exigências de fé: pode haver enredo, avisos e consequências **somente se** forem definidas por futura SPEC; não assumir que todos os clérigos possuem o mesmo bloqueio técnico.
- Item sujeito a restrição: verificar sua definição real/versão do mod antes de permitir, impedir uso ou alterar inventário. Nunca remover item ou poder silenciosamente por simples texto do LLM.
- Ato realizado em segredo: pode contribuir para o alinhamento; não altera automaticamente a reputação pública.

## Critérios de aceitação candidatos

| Teste | Critério |
|---|---|
| MECH-ALIGN-01 | Tendência moral ainda não consolidada não altera poderes ou campo de alinhamento no motor. |
| MECH-ALIGN-02 | Transição confirmada em classe sem restrição adicional preserva habilidades não afetadas. |
| MECH-ALIGN-03 | Paladino com transição incompatível recebe efeitos somente depois de validar regras e suporte efetivo, sem presumir manipulação de `fallen`. |
| MECH-ALIGN-04 | Mudança ética e moral separadas não troca atributos por rumores públicos. |
| MECH-ALIGN-05 | Ação sob coerção e caso ambíguo não produzem sanção mecânica enquanto não resolvidos. |
| MECH-ALIGN-06 | Aplicação de efeito em BG2:EE exige comando da allowlist e receipt do host. |
| MECH-ALIGN-07 | Save/reload/replay mantém alinhamento, perfil da campanha e efeito único sem duplicar perda ou retorno de poder. |
| MECH-ALIGN-08 | Dois clientes e host concordam sobre alteração ou bloqueiam a operação com divergência. |
| MECH-ALIGN-09 | Mod incompatível não recebe escrita presumida; só projeção externa e diagnóstico. |
| MECH-ALIGN-10 | Modo Original permanece intacto; outro personagem do grupo não herda consequências. |
| MECH-ALIGN-11 | Atribuição sem evidência/LLM injeta comando inválido: gateway rejeita. |
| MECH-ALIGN-12 | Falha de rede após comando não provoca repetição ou mudança duplicada. |
| MECH-ALIGN-13 | Aviso ao jogador não revela segredo de NPC ou outro personagem. |
| MECH-ALIGN-14 | Perfil de regras alterado após salvar não modifica os efeitos sem migração explícita. |
| MECH-ALIGN-15 | Evento HIGH que provoque mudança histórica segue DEC-034 independentemente da avaliação moral. |
| MECH-ALIGN-16 | Possível redenção não restaura poder automaticamente sem regra e confirmação da operação. |

## Decisões explicitamente não tomadas

- Não definimos **limiares numéricos, progressividade temporal, mensagens de interface, lista fechada de classes ou fórmulas** para efeitos.
- Não aprovamos automaticamente **reclassificação de paladino, ex-paladino, ranger, clérigo, kits, mudança de patrono, troca de classe**, redenção, respec ou reforma das restrições de AD&D 2e; esses temas terão SPECS e DEC-038 quando pertinente.
- Não comprovamos que EEex/bridge expõem todos os campos e mecanismos de atualização de regras em multiplayer.
- Não estabelecemos que um alinhamento narrativo recém-confirmado altera imediatamente o save. A mecânica poderá permanecer pendente até haver integração segura.

## Consequências

**Benefícios:** ações têm impacto narrativo e podem ter impacto mecânico consistente; previsibilidade de regra, proteção de saves e auditoria. **Custos:** mais contratos, testes de classes e kits, regras versionadas, tratamentos de estados pendentes e migrações. **Estado atual:** Discovery, sem código executado nem funcionalidade comprovada.

**Próxima decisão:** **DEC-038 — redenção, recuperação de poderes e reorientação de juramentos, patronos ou classes após mudanças de alinhamento.**
