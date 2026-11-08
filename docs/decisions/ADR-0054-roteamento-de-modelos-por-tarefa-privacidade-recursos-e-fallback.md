# ADR-0054 — Roteamento de modelos por tarefa, privacidade, recursos e fallback

- **Decisão de produto:** DEC-059 — roteamento de tarefas/modelos entre host e nós LAN.
- **Escolha expressa pelo idealizador:** **C — roteamento inteligente por tarefa, sensibilidade, complexidade, latência e recursos disponíveis**.
- **Estado:** **APROVADA em 2026-11-06**, como política arquitetural. Sem implementação ou benchmark executado.
- **Pacote:** Infinity AI Discovery **v5.5**.
- **Detalhamento:** `docs/59-roteador-de-modelos-politicas-de-privacidade-qualidade-e-fallback.md`.
- **Dependências:** DEC-006 (modelos/hardware/remoto e custos, **aberta**), DEC-011/012 (host e gateway), DEC-014 (regras primeiro), DEC-028/041 (conhecimento e agência), DEC-053/055/056 (checkpoints, incidentes e budgets), DEC-057/058 (topologia e nós pareados); DEC-015 (gates de teste, **aberta**).

## Contexto

A topologia local-first admite um host Windows e, facultativamente, trabalhadores de inferência/cálculo na LAN. Não é seguro selecionar um worker somente por velocidade, disponibilidade ou tamanho do modelo: o job pode conter segredos, exigir competências específicas ou estar associado a um ramo temporal, versão de build, revisão de memória ou autorização já revogada. Rodar um modelo grande para cada fala de NPC é custoso e contraria a orquestração por regras aprovada.

## Decisão e invariantes

1. **Um roteador lógico `AI Model Router` coordena apenas tarefas de inferência autorizadas.** Classifica a tarefa, a sensibilidade, o risco, a urgência e as capacidades validadas exigidas. A decisão operacional é determinística/auditável; o modelo não escolhe o destino para contornar permissões.
2. **Regras/código primeiro.** Quando regras determinísticas ou conteúdo já validado solucionam a tarefa, não chamar LLM. Simulação econômica/faccional em lote não passa por LLM por tick ou NPC.
3. **Privacidade e autorização são filtros eliminatórios, não pontuações compensáveis.** O contexto é reduzido por ACL **antes** do despacho. Somente workers `ACTIVE`, pareados, com canal autenticado e permissões atuais, podem receber dados de escopo permitido. Latência e GPU nunca autorizam vazamento.
4. **Seleção por adequação e orçamento.** Dentre destinos já elegíveis, escolher a classe de modelo e nó conforme tipo de tarefa (diálogo, análise contextual, proposta narrativa etc.), competências verificadas, qualidade mínima exigida, deadlines, recursos atuais, fila, estabilidade e política de campanha. No host único a política funciona sem LAN.
5. **Fallback exclusivamente seguro.** Se destino/modelo estiver indisponível, tentar um candidato **igualmente autorizado e capaz**, se existir; caso contrário, entregar conteúdo seguro já existente, declarar indisponibilidade ou deixar pendente, sem inventar fatos. **Não existe fallback implícito para nuvem ou API externa**: DEC-006 continua aberta e precisa de aprovação explícita para eventual uso remoto.
6. **Sem duplicação de efeitos.** O roteador envia cálculos sem efeitos autoritativos; idempotência, `job_id`, revisão, ramo, escopos, deadline e `permission_epoch` impedem respostas tardias/revogadas de produzirem mudanças. Se existir operação mutativa em `UNCERTAIN`, não reexecutar pelo fallback.
7. **Saída de modelo é proposta, não verdade ou comando.** Validar schema, integridade, escopo, proveniência, compatibilidade narrativa/canônica e políticas de risco antes de qualquer publicação; gateway/host determinam efeitos mecânicos. A qualidade e consistência da proposta precisam de critérios futuros (possível DEC-060).
8. **Separação de informação e poderes.** Worker não recebe token administrativo, save bruto, log completo ou acesso direto a banco/gateway; não atribui decisões a PCs, altera fatos confirmados ou conhecimento de NPCs.
9. **Observabilidade privada.** Registrar seleção, razões resumidas, modelo/worker/revisão, latência, erro, uso aproximado e fallback sem expor segredos em logs. O World Health Monitor reage a panes e o RPD aplica backpressure; métricas concretas serão aferidas, não presumidas.
10. **Isolamento de campanhas e revisões.** Todo job carrega `campaign_id`, `mode`, `branch_id`, `build_fingerprint`, `world_revision`, `permission_epoch` e minimização de escopo; resultados de versões antigas não são importados automaticamente após checkpoint/rewind/migração.

## Não decisões

- **Nenhum modelo específico**, runtime, GPU, VRAM, RAM mínima, tamanho de contexto, desempenho, custo, preço ou rota para serviços remotos foi escolhido. São temas da DEC-006 e de futuros benchmarks/POCs.
- Nenhuma API ou interface concreta de EEex/BG2:EE foi comprovada.
- Nenhuma classe de qualidade, regra de validação semântica ou verificador LLM foi implementado. A próxima discussão DEC-060 poderá definir a política de aceitação das respostas, complementando a DEC-015 ainda aberta.
- O roteador não cria agentes autônomos permanentes nem eleva permissões de nós LAN.

## Consequências

**Benefícios:** eficiência sem LLM por tick, menor vazamento de contexto, adaptação single-host/LAN, tolerância controlada a falhas e explicabilidade da escolha de modelo.

**Custos e riscos:** políticas de capability/privacidade, certificação de modelos, maior complexidade de agendamento, latência de rede, caches e artefatos temporários, falhas de classificação de sensibilidade e respostas inconsistentes entre modelos. O sigilo já enviado a um nó comprometido não pode ser revogado retroativamente.

## Gates candidatos

1. Tarefa determinística não chama IA; diálogos simples podem usar modelo menor apenas se sua capacidade for comprovada.
2. Histórico privado não atravessa nó/escopo não autorizado mesmo quando ele é mais rápido.
3. Nó desconectado ou revogado não recebe novo job; retorno tardio ou de ramo antigo é rejeitado.
4. Single-host funciona sem LAN; queda de worker usa somente fallback autorizado ou falha fechada.
5. Gateway/host não aceitam comandos livres de resposta de modelo; event log não duplica efeitos.
6. Metadados/logs sem segredos; benchmarks de qualidade, latência, consumo e dois clientes antes de metas de desempenho.

**Estado atual:** desenho de Discovery; **nenhum modelo foi selecionado, roteado ou avaliado**, nenhuma rede LAN ou bridge foi testada. **Próxima candidata: DEC-060 — validação e qualidade de respostas de IA antes de se tornarem conteúdo do Living World**.
