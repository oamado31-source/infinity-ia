# ADR-0052 — Topologia modular local-first com execução distribuída opcional

- **Decisão de produto:** DEC-057 — localização de serviços do Infinity AI durante uma sessão cooperativa.
- **Escolha expressa pelo idealizador:** **C — serviços desacoplados, executáveis no computador anfitrião ou opcionalmente em nós da rede local**.
- **Estado:** **APROVADA em 2026-11-06**, como arquitetura; implementação condicionada a SPECS/POCs.
- **Pacote:** Infinity AI Discovery **v5.3**.
- **Detalhamento:** `docs/57-topologia-local-first-servicos-desacoplados-e-nos-lan.md`.
- **Dependências:** DEC-001/002/003 (coop privado, Windows inicial, BG2:EE limpo), DEC-006 (modelos/hardware/consentimento de nuvem, **aberta**), DEC-011 (host mecânico e persistência narrativa), DEC-012 (Action Gateway), DEC-014 (regras primeiro/IA sob demanda), DEC-018 (operações, **aberta**), DEC-021/022/032 (simulação e relógio), DEC-028/041/046 (segredos e agência), DEC-051/052 (manifestos e migração), DEC-053/054 (checkpoints/backups), DEC-055 (World Health Monitor), DEC-056 (Resource & Performance Director), DEC-015 (gates técnicos, **aberta**).

## Problema

O mesmo computador que hospeda BG2:EE pode precisar executar inferência de linguagem, indexação, simulação regional e banco narrativo. Tais cargas disputam CPU, GPU/VRAM, memória, disco e rede com o jogo e multiplayer. Obrigar uma segunda máquina inviabilizaria parte dos grupos; obrigar colocação única limitaria escalabilidade. Separar fisicamente processos, contudo, não altera quem pode confirmar efeitos, cria novas fronteiras de confiança e expõe falhas de transporte.

## Decisão aprovada — invariantes

1. **Local-first e modo de máquina única viável como objetivo:** admitir topologia `SINGLE_HOST` com BG2:EE no Windows e serviços Infinity AI em processo(s) local(is) isolados/sidecar. Não exigir servidor dedicado, nuvem, internet nem conexão de terceiros para a campanha local pretendida. O funcionamento efetivo deve ser medido/testado; não prometer que qualquer hardware suportará toda a carga.
2. **Distribuição opcional:** admitir `LAN_OPTIONAL` com execução de cargas de IA, simulação e outros workers em um ou mais nós LAN que o anfitrião explicitamente configurar. A decisão fixa a **capacidade de distribuição**, não um protocolo, runtime, sistema operacional remoto, balanceador ou quantidade de nós.
3. **Autoridade inalterada:** BG2:EE host continua autoridade do estado mecânico (DEC-011); o serviço narrativo só consolida fatos com evidências. Nenhum nó LAN recebe poderes diretos de alteração do motor. Todas as mutações passam pelo Action Gateway tipado, autorização/riscos, confirmação e receipt do host. Modelo LLM nunca executa comandos arbitrários.
4. **Direção de dependências:** nós remotos podem fazer inferências e cálculos de proposta, sempre com contexto limitado e retornos de esquema validável. Dados recebidos são **não confiáveis até validação**. Não transferir segredos, tokens, saves ou snapshots completos por conveniência; usar ACL antes da recuperação e minimização de payload da DEC-028.
5. **Serviços com estado:** a memória persistente e o event log ficam preferencialmente junto à autoridade da campanha, em implantação inicial controlada pelo host. Executá-los na LAN é **possibilidade arquitetural condicionada** a provas próprias de latência, durabilidade, isolamento, confirmação e recuperação; não significa que sejam seguros para migração automática.
6. **Identidade e sessão:** cada job/resultado possui `campaign_id`, `mode`, `build_fingerprint`, `branch_id`, revisão, autorização, papel do nó e identificadores de requisição/resultado. Uma resposta de outra campanha, ramo, época, versão ou usuário é rejeitada. Só hosts/serviços explicitamente autorizados podem estabelecer vínculos. Pareamento, transporte, criptografia e revogação detalhados serão discutidos na **DEC-058** e testados; não assumir segurança da LAN.
7. **Falhas e partições:** perder conectividade com um nó não equivale a falha mecânica do BG2:EE, nem autoriza repetição de ações com status `UNCERTAIN`. Suspender capacidades dependentes, revogar tarefas obsoletas e oferecer fallback **somente se validado**. Não criar segundo host/leader por eleição automática. A sessão clássica pode prosseguir se sua independência for realmente comprovada.
8. **Performance/consistência:** RPD da DEC-056 aplica budgets e prioridades por tarefa/nó, sem prometer quotas de GPU/latência não medidas. Lotes distantes podem ser adiados; receipts, eventos críticos, checkpoints e controle de risco não podem ser descartados. Migrar execução de worker não muda relógio do mundo nem aplica automaticamente eventos pendentes.
9. **Privacidade:** operação local e LAN privada por padrão, sem exposição de portas à internet, descoberta pública, telemetry upload ou API remota sem consentimento. Exportação do conteúdo secreto de PCs/NPCs requer política de dados e permissão prévia; nós LAN não herdam todos os privilégios do anfitrião.
10. **Implantação gradual e reversível:** testar primeiro BG2:EE Windows limpo com sidecar observacional/read-only; depois orquestração local e um worker externo LAN sem mutação; finalmente testes de perda de rede, retorno, privacidade, descompasso de revisões, host + dois clientes, save/restore e carga. EET/IWD/NWN dependem dos gates da DEC-003/013/015.

## Alternativas avaliadas

- **A — Todos os serviços no computador anfitrião:** implantação simples, mas não escalável sem redesenho e com maior contenção de hardware.
- **B — Servidor dedicado obrigatório:** separa recursos, mas impõe infraestrutura e falhas de rede desnecessárias à adoção inicial.
- **C — Modular local-first com distribuição opcional (**aprovada**):** permite máquina única e LAN, com complexidade adicional de identidade, transportes e recuperação administrada em SPECS.

## Consequências

**Benefícios:** instalabilidade para grupos pequenos, possibilidade de aproveitar segunda máquina/GPU, isolamento dos workloads, reaproveitamento dos contratos de jobs e monitoração, liberdade para trabalhar sem internet. 

**Custos:** introduz descoberta de nós, identificação de sessão, autenticação, proteção de dados no trânsito, monitoramento por nó, políticas de desconexão e testes de deployment. Isolamento lógico não comprova isolamento de memória/processos no Windows. Local-first não garante desempenho suficiente no computador do usuário.

## Gates e evidências necessários antes de implementação

1. Comparar `SINGLE_HOST` sob BG2:EE host + dois clientes com LLM/simulação sem violar integridade ou causar degradação não aceitável, definindo métricas após benchmark.
2. Executar worker de inferência **somente leitura** em LAN, com retorno de proposta validado e nenhum caminho direto de escrita no motor.
3. Desconectar nó em diferentes pontos (antes/depois de iniciar job, após enviar resultado, durante checkpoint) sem duplicar efeito, perder receipt ou promover job incerto a confirmado.
4. Rejeitar resposta cruzada de campanha/modo/build/ramo/revisão; validar ACL antes de disponibilizar contexto a nó remoto.
5. Medir latência, throughput, CPU/GPU, fila, impacto em FPS/sincronização, atraso e comportamento de fallback; sondas ausentes = `UNKNOWN`.
6. Validar restauração coerente e tratamento de memória distribuída **antes** de aprovar tal colocação; não supor transações entre hosts e bancos de dados.
7. Confirmar, em provas de rede e consentimento, como prevenir conexões LAN não autorizadas; segurança concreta permanece pendente da DEC-058.

**Situação:** apenas a **arquitetura** foi aprovada. Sem código implantado, serviço de LAN executado, contrato de rede testado, métricas de hardware ou suporte comprovado para EEex multiplayer. **Próxima decisão proposta:** DEC-058 — pareamento e proteção das conexões entre anfitrião e nós LAN opcionais.
