# ADR-0006 — Integração progressiva do motor e conteúdos

- **DEC associada:** DEC-003
- **Estado:** **APROVADA — opção A (motor mínimo, provas de integração, expansão incremental)**
- **Data de aprovação:** 2026-11-06
- **Domínio:** estratégia de instalação, testes de compatibilidade, integração externa e expansão de conteúdo
- **Fundamentação:** escolha explícita do idealizador no Discovery do Infinity AI.
- **Relações:** DEC-001/ADR-0001; DEC-002/ADR-0005; DEC-004/ADR-0002; DEC-013 e DEC-015 ainda pendentes.

## Contexto

O Infinity AI pretende utilizar BG2:EE como motor visual inicial, com integração externa de IA, e futuramente agregar mapas e recursos de EET, Icewind Dale e NWNForBG. Modificações, extensões e ferramentas da comunidade apresentam dependências de versão e ordem de instalação que podem se contradizer. O EEex Remote Console foi documentado para operações experimentais, **não demonstrou ainda sincronização multiplayer neste projeto**.

Montar de início o pacote completo dificultaria determinar qual componente causou falhas, corrompeu referências ou afetou saves. Precisamos de baselines restauráveis e gates objetivos por estágio.

## Decisão aprovada

1. O **primeiro baseline técnico** será BG2:EE **limpo, sem mods**, instalado em uma **cópia dedicada a testes no Windows nativo** (DEC-002). As instalações pessoais e saves originais permanecem intactos.
2. Validado o baseline, testar o **EEex compatível com a versão do jogo**, sem assumir de antemão combinação de builds. Em seguida, validar uma **bridge externa isolada** por ações inicialmente **somente de leitura**.
3. Executar POCs de **ação controlada offline**, reversão e **dois clientes multiplayer** antes de declarar integrações de eventos dinâmicos aptas ao modo cooperativo. Não autorizar Lua arbitrário vindo de LLM.
4. Após esse gate, preparar **uma nova build isolada** de EET com fontes legítimas e os mods exigidos. Repetir smoke/regressão, incluindo entrada/saída de áreas, interações, combate, save/reload e sincronização entre clientes.
5. Expandir **progressivamente por incrementos verificáveis de conteúdo** (IWD1-EET, IWD2-EET, NWNForBG e integrações de mapa, conforme disponibilidade/compatibilidade), registrando o efeito de cada inclusão.
6. **Integração progressiva não significa instalar cada mod por último sobre a mesma pasta já finalizada.** Montar cada combinação a partir de fontes limpas/snapshots conforme sua **ordem de instalação documentada**; `EET_End` e outros componentes finais devem permanecer na posição exigida pela combinação utilizada. Recriar a build do zero quando a ordem assim exigir.
7. Cada estágio terá um **manifesto de versões, origem, hashes quando aplicável, lista e ordem de mods**, evidências de testes, saves descartáveis e procedimento de rollback. Uma build com falha **não substitui** o baseline anterior.
8. Aumentar conteúdo do mundo **não implica automaticamente** suporte a mundo aberto irrestrito ou a múltiplos grupos independentes; esses recursos seguem sob decisões e testes próprios.
9. Esta ADR define a **sequência de validação**, não declara que ferramentas já foram instaladas, executadas ou que todas as combinações são compatíveis. Nenhum código de produção é autorizado antes das SPECS pertinentes.

## Etapas e gates candidatos (a converter em SPECS)

| Gate | Build / capacidade | Evidência mínima a obter | Bloqueia se… |
|---|---|---|---|
| G0 | BG2:EE puro, Windows | inicia, navega área, combate mínimo, cria/carrega save | instalação não reproduzível ou altera saves pessoais |
| G1 | EEex compatível, sem bridge | launcher correto, logs, sessão de jogo estável | versão incompatível ou crash |
| G2 | Bridge externa somente leitura | consulta de estado permitida e resposta registrada; nenhum Lua livre de IA | execução fora da allowlist ou erros de protocolo |
| G3 | Ação controlada offline | alteração permitida e observável, validação de limites, rollback | estado inconsistente ou sem reversão |
| G4 | Dois clientes multiplayer | ação autorizada refletida de modo consistente em ambos, teste de reconexão/save quando aplicável | divergência ou duplicação de eventos |
| G5 | EET em build própria | instalação/reprodução, mapas, diálogos, combate, save/load e regressão dos gates pertinentes | regressão e incompatibilidade persistente |
| G6+ | Inclusões IWD/NWN por combinação | baselines e testes repetidos por incremento; mapa de dependências | conflito em instalação, área, recurso ou multiplayer |

**Observação de desenho:** os gates G0–G6+ são critérios preliminares para a futura DEC-015. A sequência de *montagem dos arquivos dos mods* será definida por documentação de versões (DEC-013) e pode diferir da sequência de *evolução dos testes* acima.

## Consequências

**Benefícios:** falhas rastreáveis; segurança de saves; menor custo de depuração; possibilidade de avaliar o risco real de cada integração; isolamento do maior risco técnico (bridge multiplayer) antes da explosão de conteúdo.

**Custos:** mais builds e testes repetidos, maior consumo de espaço e manutenção do manifesto; possível necessidade de reconstruir cada combinação limpa; conteúdos adicionais chegarão mais tarde.

## Alternativas não escolhidas

- **B — EET primeiro:** evita repetir parte da integração com conteúdo, mas combina complexidade de mods com as incertezas de EEex/bridge logo na primeira prova.
- **C — Todos os conteúdos primeiro:** disponibiliza um mundo amplo mais cedo, mas torna incompatibilidades e regressões muito mais difíceis de isolar.

## Pendências e condições de revisão

- **DEC-013:** versões exatas de BG2:EE, EEex, bridge, EET, IWD1/IWD2 e NWNForBG, além de instalador/ordem e rollback.
- **DEC-011:** autoridade sobre eventos do jogo, persistência e sincronização multiplayer.
- **DEC-012:** segurança de IPC, permissões, allowlists, validação e auditoria das ações.
- **DEC-015:** transformar gates preliminares em critérios mensuráveis e automatizáveis.
- **DEC-007/016:** decidir UI/diálogos dinâmicos; atualmente não demonstrados no multiplayer.
- Caso a POC multiplayer seja inviável, reavaliar a bridge ou estratégia de integração antes de avançar ao conteúdo EET; **não** reclassificar uma falha como capacidade já implementada.

## Referências técnicas para preparação de teste

- EEex: https://github.com/Bubb13/EEex
- EEex Remote Console: https://github.com/Chrizhermann/eeex-remote-console
- EET: https://github.com/Gibberlings3/EET
- IWD1-EET: https://github.com/The-Gate-Project/IWD1_EET
- IWD2-EET: https://github.com/The-Gate-Project/IWD2_EET
- NWNForBG: https://github.com/abalabokhin/NWNForBG

As referências documentam componentes; **não constituem validação de interoperabilidade deste conjunto**.
