# ADR-0017 — Combate por turnos opcional com validação técnica obrigatória

- **Identificador:** DEC-005-T (subdecisão da DEC-005)
- **Estado:** **APROVADA COMO OBJETIVO DE DESIGN; IMPLEMENTAÇÃO CONDICIONADA À PROVA DE VIABILIDADE**
- **Escolha do idealizador:** B — preservar RTwP clássico e oferecer turnos individuais opcionais, se tecnicamente viável.
- **Data:** 2026-11-06
- **Ámbito:** mecânica de combate; não redefine edição das regras, autoridade multiplayer ou motor oficial.
- **Relacionamentos:** DEC-001, DEC-003, DEC-011, DEC-014, DEC-015, DEC-013, DEC-005-R, DEC-005-E.

## Contexto

O Infinity AI exige coop multiplayer sobre BG2:EE, com integração progressiva de EET, IWD-EET e NWNForBG. Foi localizado o fork GemRB-TBC com um sistema alternável de turnos individuais, preservando regras AD&D 2e. Sua existência **não comprova** compatibilidade direta com o executável BG2:EE, EEex, EET ou multiplayer. A investigação de código identificou um gerenciador próprio integrado a diversos subsistemas do GemRB, além de dependências do motor e estado em memória.

## Decisão aprovada

1. Manter **RTwP original de BG2:EE como baseline funcional** para testes, regressão e para o modo clássico.
2. Objetivo de longo prazo: oferecer **modo opcional com turnos individuais reais**, selecionável pelo anfitrião para sessões compatíveis. Alternância em qualquer instante, inclusive com combate aberto, **não** está aprovada como requisito técnico sem ensaio de consistência.
3. **Não adotar GemRB-TBC como motor principal neste momento**: falta multiplayer, BG2:EE é experimental no GemRB e módulos baseados em EEex não executam como extensões desse motor.
4. GemRB-TBC é **referência verificável de código e lógica** para iniciativa, scheduler, fases de ataque, ações, movimentação, interrupções e interface; sua incorporação a BG2:EE não é plug-and-play e exigiria engenharia sobre a engine proprietária via EEex e/ou mudanças de código de motor aberto.
5. O combate por turnos não exige conversão para D&D 5e. **Edição base das regras permanece aberta** sob DEC-005-R; diretor determinístico de encontros permanece aberto sob DEC-005-E.
6. Toda versão de teste do combate precisa preservar autoridade mecânica do host, confirmação/reconciliação, saves separados, isolamento de sessão, sem LLM por ataque e sem execução arbitrária de comandos (ADRs 0006–0008).

## Evidências e limites

- Repositório: https://github.com/Dreamkins/gemrb-TBC (branch TBC). Documenta Enter para alternar o modo; Space para encerrar turno; iniciativa, movimento, ação principal e livre e ataques de oportunidade.
- Inspeção de API GitHub em 2026-11-06: diferença `master...TBC` do fork contém **199 commits à frente** e diversas alterações no core; arquivos adicionados `gemrb/core/TurnBasedCombatManager.cpp` (568 linhas) e `.h` (177 linhas). Mudanças relevantes em Actor, Game, GameControl, Actions, Map e outras unidades. Contagem descreve o diff do fork; **não** implica 199 commits exclusivamente sobre combate.
- Gerenciador usa `Actor*` e estruturas de iniciativa locais; não foi identificada, nessa inspeção dirigida, serialização multiplayer/saves do estado integral de turnos. Exige auditoria específica; **não afirmar ausência definitiva** sem teste/inspeção completa.
- GemRB oficial: https://gemrb.org/Features.html — sem multiplayer; BG2:EE experimental; https://gemrb.org/Modding.html — EEex/hooks não funcionam no motor GemRB; https://gemrb.org/Install — modificação de executável não é equivalente.
- EET: https://gibberlings3.github.io/Documentation/readmes/readme-EET.html — alvo BG2:EE e dependências de instalação.
- EEex: https://github.com/Bubb13/EEex — extender específico do executável Enhanced Edition.

## Portas de validação / critérios de aceitação futuros

| Gate | Prova | Resultado necessário |
|---|---|---|
| TBC-01 | Testar build GemRB-TBC isolado em Windows com cópia legítima compatível dos dados de BG2 original | Turnos, ações, movimentos, magias e alternância observados e registrados |
| TBC-02 | Inspecionar execução com BG2:EE e build/mods EET em ambientes isolados | Registro de funcionalidades e incompatibilidades; nenhum sucesso presumido |
| TBC-03 | Verificar serialização/restauração da ordem de iniciativa e efeitos durante turno | Save/load sem inconsistências observáveis |
| TBC-04 | Avaliar se EEex oferece hooks suficientes no BG2:EE para scheduler de host | Demonstração de bloquear ação fora da vez sem desalinhar clocks/efeitos |
| TBC-05 | Dois clientes BG2:EE — ordem, ações, pausa e salvamento | Host e cliente concordam em iniciativa e efeitos, inclusive após reconexão |
| TBC-06 | Regressões com IWD/NWNForBG, magia e scripts de tempo real | Sem bloqueio de progressão e rollback funcional |

## Condições de revisão arquitetural

- **Se BG2:EE + EEex passar TBC-04 e TBC-05**, projetar SPEC de turnos opcionais para o motor atual, usando o GemRB-TBC como referência de comportamento.
- **Se não passar**, manter RTwP (e opcionalmente UX de autopausa) e avaliar novo projeto específico para multiplayer GemRB ou motor 2D independente. Não sacrificar silenciosamente a DEC-001 para ganhar turnos.
- Provas de conceito TBC não justificam alterar a ordem de integração definida na DEC-003.

## Não decidido nesta ADR

Edição definitiva de D&D, CR/balanceamento, runtime de turno e save intermediário, alternância entre modos em meio ao combate, UI final e suporte ao multiplayer de EET/IWD/NWNForBG. São questões para SPECS e POCs.
