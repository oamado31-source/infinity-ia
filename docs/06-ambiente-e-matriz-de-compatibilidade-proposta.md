# Ambiente e matriz de compatibilidade — proposta v0.6

**Estado:** rascunho técnico de Discovery; **não representa instalação executada, versões aprovadas nem SPEC final.**

## Decisão vinculante

DEC-002 / ADR-0005: **Windows nativo** como primeiro ambiente de execução e teste; os serviços de IA permanecem conceitualmente desacoplados da Infinity Engine.

## Ponto de atenção entre fontes

- A documentação de EET descreve instalação em BG2:EE limpo e recomenda `EET_End` **após os demais mods**.
- O EEex declara Windows nativo e compatibilidade distinta para motores 2.6 e 2.7; o instalador correto deve corresponder à versão real.
- O README do IWD1_EET propõe uma ordem envolvendo **EET → IWD1_EET → IWD2_EET → componentes iniciais NWNForBG → integrações finais → componente de campanha NWNForBG → EET_End**. Essa sequência é **referência inicial**, não uma garantia universal, e depende de componentes e outros mods escolhidos.
- A documentação do NWNForBG descreve componentes opcionais de mapas e campanha dedicada, inclusive observações de compatibilidade com outros mods; as escolhas e ordem serão registradas por instalação.
- A funcionalidade EEex Remote Console e sua sincronização em multiplayer precisam ser comprovadas em POC independente; não tratar um teste de single-player como validação de multiplayer.

## Matriz inicial a preencher no teste real

| Componente | Versão do ambiente | Estado | Prova exigida |
|---|---|---|---|
| Windows | A levantar | DEC-002: SO escolhido | Inventário e teste de execução |
| BG2:EE | A levantar | Motor candidato | Executar jogo base sem mods |
| BG:EE + SoD | A levantar | Dependência candidata de EET | Recursos de origem disponíveis e compatíveis |
| EEex | A levantar | Dependência candidata da bridge | Launcher correto e comandos inofensivos |
| EEex Remote Console | A levantar | Experimental | IPC local; depois validação com 2 clientes |
| EET | A levantar | Expansão candidata | Instalação e integridade de áreas/saves |
| IWD1_EET | A levantar | Expansão candidata | Áreas/recursos e regressões |
| IWD2_EET | A levantar | Expansão candidata | Áreas/recursos e regressões |
| NWNForBG | A levantar | Expansão candidata | Componentes adequados ao EET |
| Worldmap / integrações | A levantar | Opcional a decidir | Transições e conflitos de recursos |

## Protocolo de experimentação proposto — ainda depende da DEC-003

1. Registrar versões e hashes, e copiar instalações para sandbox local separada.
2. Criar baseline de execução e saves de teste.
3. Verificar cada extensão isoladamente e guardar logs/reprodutibilidade.
4. Repetir testes de entrada, transição de áreas, diálogos, combate e save/reload.
5. Antes de afirmar capacidade multiplayer, realizar testes com **dois clientes** e observação equivalente do estado.
6. Documentar rollback e critérios de bloqueio; se um mod quebrar a compatibilidade, não comprometer os baselines prévios.

## Decisão DEC-003 pendente

- **A. Prova mínima primeiro:** BG2:EE limpo → EEex/bridge → prova multiplayer → EET → IWD/NWN incremental.
- **B. Mundo-base integrado primeiro:** EET → prova de integração + IA → IWD/NWN incremental.
- **C. Pacote de regiões primeiro:** EET + IWD1/IWD2 + NWNForBG → prova de IA no conjunto.

A escolha A reduz variáveis simultâneas nos primeiros testes; B valida o mundo-base mais cedo; C dá conteúdo imediato, mas aumenta dificuldade para localizar falhas.

## Fontes

- https://github.com/Bubb13/EEex/blob/master/README.md
- https://github.com/Gibberlings3/EET/blob/master/EET/readme-EET.html
- https://github.com/The-Gate-Project/IWD1_EET
- https://github.com/abalabokhin/NWNForBG
- https://github.com/orgs/The-Gate-Project/discussions/3

## Integração com DEC-051 — inventário de conteúdo validado por build (Discovery v4.7)

A DEC-051 aprovou captura de fingerprint/manifesto e recursos **read-only**, enriquecidos por curadoria e cobertura explícita (ADR-0046/doc. 51). A presença estática de arquivos não comprova flags/quests vivas. Propostas dependentes de conteúdo desconhecido ou build divergente devem ser bloqueadas/adiadas pelo reconciliador DEC-050; operações efetivas continuam sob gateway e confirmação do host. Regressões são específicas de instalação/ordem de mods; implementações e suporte multiplayer permanecem não comprovados.

## DEC-052 — Política de migração entre baselines (Discovery v4.8)

Uma campanha Living World deve permanecer vinculada à build e ao inventário de origem até que uma nova instalação isolada tenha **migração ensaiada** e **aprovada pelo anfitrião**. O fingerprint da DEC-051 e a matriz de versões da futura DEC-013 identificam condições necessárias, não suficientes. Exigir backup coordenado de saves do host + snapshots/log narrativo, diff de mods/recursos, revalidação de scripts/quests/romances e testes com host + dois clientes. Se falhar qualquer gate, manter baseline anterior; não tentar desmontar mods diretamente em save de produção. Ver ADR-0047/doc. 52. Ainda não há migração demonstrada.

## DEC-057 — Topologia de serviços (Discovery v5.3)

O primeiro baseline permanece **Windows nativo com BG2:EE limpo, processo(s) de serviço local(is) desacoplado(s)** e bridge inicialmente observacional. A opção aprovada permite um segundo nó **LAN opcional** para LLM e simulação; o suporte de qualquer SO/runtime nesse nó não está afirmado. Identidade do anfitrião e a confirmação mecânica continuam no BG2:EE host. O teste de capacidade inclui modo de máquina única, sidecar com host + dois clientes, depois worker LAN com dados sintéticos e partições. Não confundir EEex Remote Console com prova de IPC seguro, rede LAN ou multiplayer. Ver ADR-0052/documento 57; DEC-058 definirá pareamento/canal.

## Integração DEC-072/C — catálogo modular de encontros por build (Discovery v6.8)

Matriz de compatibilidade DEC-072 deve registrar para cada build/mod o hash, ordem e prova específica de uso de template/adapter. Asset PRESENT não comprova alteração runtime nem multiplayer.

**Referências:** `docs/decisions/ADR-0067-catalogo-modular-de-encontros-e-componentes-validados-por-build.md` e `docs/72-catalogo-modular-de-encontros-templates-componentes-e-gates-por-build.md` (**48 testes candidatos não executados**). Todas as DEC-060–071 preservadas; nenhum suporte de engine/EEex/multiplayer demonstrado.


## Integração DEC-099/C — proteção de ownership e compatibilidade (Discovery v9.5)

Matriz de compatibilidade por build: fingerprint de BG2:EE, EEex, bridge e manifest de mods/ordem/hash devem ser pinados antes de qualquer capability. Inventário estático não comprova write.

**Contrato vinculante de Discovery:** [`ADR-0094`](decisions/ADR-0094-ownership-por-instancia-compatibilidade-por-build-e-protecao-de-conteudo-original.md) e [`Documento técnico 99`](99-ownership-por-instancia-compatibilidade-por-build-arbitragem-e-reconciliacao.md). Origem, custódia, owner de instância e autoridade por campo são distintos; build/EEex/modpack precisa ser testado, em ausência de prova aplica-se bloqueio e reconciliação. **Nenhum hook BG2:EE/EEex foi testado.**


## Integração DEC-100/C — Observação mínima e antifuga de spoilers (Discovery v9.6)

Descoberta de capacidades do EEex deve verificar empiricamente se probes são realmente read-only; nunca assumir APIs não medidas.

**Contrato de Discovery:** [`ADR-0095`](decisions/ADR-0095-observacao-somente-leitura-allowlisted-de-quests-scripts-e-protecao-contra-spoilers.md) e [`Documento técnico 100`](100-observacao-read-only-quests-scripts-capabilities-acl-e-fronteiras-de-conhecimento.md). Toda leitura exige probe read-only **com POC por build**, allowlist, finalidade, audiência, cobertura e ACL; o estado bruto técnico não equivale a conhecimento narrativo nem a receipt do host. Falta de prova => `UNKNOWN` ou bloqueio, nunca LLM. **Nenhum hook BG2:EE/EEex foi testado.**


### Integração DEC-102/C (Discovery v9.8)

Mudanças de BG2:EE/EEex/bridge/modpack invalidam observação e reconciliação DEC-102 até recertificação. Ver `docs/102-reconciliacao-semantica-quests-host-overlay-epochs-provas-e-projecoes.md` e ADR-0097. **Arquitetura somente; POCs pendentes.**

### Integração DEC-105/C — Discovery v10.1

**Contrato vinculante:** ADR-0100 / doc. 105. Para capabilities de comunicação e observação por build, sem alegar hooks existentes, preservar uma fronteira verificável entre prova committed, conteúdo divulgado, transporte, entrega, percepção, conhecimento e opinião. **Nenhum broadcast global, aceitação obrigatória, vazamento de fonte ou escrita mecânica por LLM**; aplicar ACL por destinatário, canal/tempo DR, campanha/branch/epoch, outbox idempotente e gates próprios quando necessário. A DEC-105 é **arquitetural**, com T105-001..144 candidatos **NÃO EXECUTADOS** no jogo; exemplos em `examples/chronology/correction_diffusion_*` são sintéticos.

### Integração DEC-106/C — Discovery v10.2

**Contrato vinculante:** ADR-0101/doc. 106. Para matriz de compatibilidade BG2:EE e modpack por build, preservar prova de retificação curada, destinatários realmente expostos, crença falível, danos efetivamente comprovados, reputação por contexto e medidas voluntárias de reabilitação; a saída é **PROPOSTA**. Nunca broadcast global, perdão compulsório, apagamento de prejuízo, indenização fictícia, mudança de reputação do host ou concessão de ACL pela LLM. Proteger fontes e PCs, respeitar tempo DR, branch/epoch, CAS, ownership, Action Gateway e recibos para efeitos. **T106-001..148 candidatos NÃO EXECUTADOS no jogo**; código/fixture JSON somente sintéticos.

### Integração DEC-107/C — Direito de resposta e mediação voluntária

**ADR-0102 / doc.107 (Discovery v10.3).** Requerer legitimidade do principal, mandato de representantes e consentimento específico de PCs/partes; proteger prova e identidade por ACL/audiência antes de prompt ou log. Pedido não certifica autorização própria. Nenhuma operação mecânica sem ownership, risco e recibo do host. **DEC-060..106 e ADRs anteriores preservados; cenários T107-001..152 candidatos NÃO EXECUTADOS em BG2:EE/EEex.**

## Integração DEC-110/C — garantias e SDD (Discovery v10.6)

Novo gate escrow por build: read-only ownership, transferência em save descartável, host receipts, dois clientes e recuperação após save/load; ausência de capability → `BLOCKED_CAPABILITY`. Não declarar feature instalada.

**Referências:** ADR-0105; docs/110-custodia-garantias-escrow-ownership-recibos-e-liberacao-condicionada.md; questionário docs/111-questionario-consolidado-decisoes-para-specs-e-handoff-sdd.md. 176 testes de integração T110 candidatos ainda não executados. DEC-060–109 e ADRs anteriores preservados.
