# ADR-0053 — Descoberta assistida, pareamento autorizado e canais protegidos na LAN

- **Decisão de produto:** DEC-058 — segurança de nós e comunicação LAN do Infinity AI.
- **Escolha expressa pelo idealizador:** **C — descoberta assistida, pareamento aprovado pelo anfitrião e comunicação protegida entre nós**.
- **Estado:** **APROVADA em 2026-11-06**, como política arquitetural; **nenhum protocolo, serviço ou controle foi implementado/testado**.
- **Pacote:** Infinity AI Discovery **v5.4**.
- **Detalhamento:** `docs/58-descoberta-pareamento-identidade-e-seguranca-lan.md`.
- **Dependências:** DEC-001/002/003/011 (modelo coop e autoridade mecânica), DEC-012 (Action Gateway), DEC-014/028 (IA regras-primeiro e ACL de conhecimento), DEC-019/041/046 (segredos e titularidade), DEC-027/034 (risco e cânone), DEC-053/054/055 (checkpoints, backup, incidentes), DEC-056/057 (filas e topologia). DEC-006/013/015/018 continuam abertas.

## Contexto

A DEC-057 permite que cargas não autoritativas (inferência e simulação por lotes) sejam executadas na mesma máquina do host ou, opcionalmente, em computadores da LAN. Pertencer à rede local não é prova de confiança: anúncios falsos, interceptação de tráfego, nós comprometidos, resultados adulterados, replay, compartilhamento indevido de histórias secretas e revogação incompleta podem comprometer a campanha. A topologia `SINGLE_HOST` não deve depender de descoberta de rede.

## Decisão e invariantes

1. **Descoberta não confere confiança.** A descoberta de nós é *assistida*, opt-in, limitada à LAN configurada e tratada como dado não confiável. Encontrar um endereço ou nome de serviço não estabelece identidade nem concede tarefas, dados ou privilégios.
2. **Pareamento explícito.** Cada novo nó deve ter a identidade verificada por mecanismo apropriado e ser **aprovado expressamente pelo anfitrião**, em um fluxo que evita aceitar o primeiro anúncio da rede sem verificação. A forma do código de confirmação ou canal fora de banda permanece para SPECS e testes de segurança.
3. **Identidade durável e vinculada.** O vínculo do nó usa identidade criptograficamente verificável, distinta de IP/hostname, com registro de origem e estado da autorização. Mudança de chave, substituição do nó ou suspeita de comprometimento exige revalidação; não confiar silenciosamente em identidade nova.
4. **Canal protegido.** Comunicação entre host e nó pareado deve autenticar os pares e proteger confidencialidade e integridade do transporte. Rejeitar degradação automática para comunicação em texto claro ou não autenticada. Seleção de protocolo, versões, cifra, bibliotecas e ciclo de vida das chaves só em SPECS/POCs; mTLS é uma *candidata*, não decisão já implementada.
5. **Mínimo privilégio e consentimento.** Autorizar separadamente por nó, campanha/modo, serviço/tipo de job, escopo de dados, validade e limites de uso. Por padrão, o nó apenas **recebe tarefas de cálculo e devolve propostas**, sem escrever diretamente em saves, estado mecânico, event log ou Action Gateway mutativo. O anfitrião poderá revogar a autorização.
6. **Privacidade antes de enviar.** Aplicar ACL da DEC-028 e minimização do contexto **antes** do despacho, inclusive para histórico privado dos PCs, rumores e segredos dos NPCs. Não enviar snapshots integrais, tokens administrativos, chave de pareamento ou dados de outras campanhas por conveniência. Logs, cache, diagnósticos e pré-visualizações não podem vazar dados de acesso restrito.
7. **Revogação efetiva do acesso futuro.** Revogar ou suspender nó deve bloquear **novos despachos e resultados ainda não aceitos**, invalidar autorizações/tokens ativos na medida compatível com o protocolo e registrar decisão. Resultados antigos, tardios ou associados à época de permissão anterior são rejeitados/isolados, respeitando idempotência e auditoria. **Não** alegar que revogação apaga dados já entregues ou impede que nó comprometido os tenha copiado.
8. **Resultados não são autoridade.** Respostas são propostas não confiáveis até validação de identidade, autorização, esquema, revisão, `campaign_id`, `mode`, `build_fingerprint`, `branch_id`, `session_id`, `permission_epoch` e contexto. IA/nó não assume decisões dos jogadores, controle do host, nem envia comandos arbitrários diretamente ao motor.
9. **Sem rede pública por padrão.** Não habilitar descoberta fora do escopo local, port forwarding, exposição direta à internet, telemetria externa ou APIs cloud sem outra decisão/consentimento. LAN não é garantia absoluta de isolamento; regras de firewall/escuta são tema técnico a validar.
10. **Falhas seguram a fronteira.** Perda de conectividade, erro de autenticação, certificado expirado, suspeita de spoofing ou resposta inconsistente levam a contenção e modo degradado seguro da DEC-055, sem replay cego de ações `UNCERTAIN` nem failover da autoridade mecânica.
11. **Topologia de uma máquina preservada.** A implantação `SINGLE_HOST` continua funcional sem descoberta LAN ou pareamento remoto; a política de autenticação interna/IPC fica para SPECS.
12. **Privacidade operacional.** Credenciais/chaves não aparecem em logs, telas para outros jogadores ou arquivos de diagnóstico; recuperação/rotação de credenciais exige processo explícito. A auditoria registra quem autorizou, qual nó, qual escopo e quando, sem guardar segredos do conteúdo.

## Fronteiras aprovadas e não decididas

**Aprovados:** fluxo conceitual `DISCOVERED_UNTRUSTED → PENDING_VERIFICATION → PAIRED_RESTRICTED → ACTIVE`, com `SUSPENDED/REVOKED/QUARANTINED` para problemas; autorização explícita, comunicação protegida, identidade verificável, mínimo privilégio, ACL pré-envio, revogação e validação de retornos.

**Não decididos:** algoritmo de descoberta, PKI/mTLS versus outras formas auditadas de autenticação, distribuição e armazenamento de chaves, número de nós, SO remoto, códigos de pareamento, UI, TTL, portas, algoritmo de criptografia, política de instalação de serviços, servidor de segredos e limites de dados. Esses detalhes exigem SPECS e provas técnicas. **Nenhuma criptografia ou proteção efetiva é alegada já estar funcionando.**

## Consequências

- **Benefícios:** distribuição LAN opcional com onboarding controlado, privilégio restrito, isolamento entre campanhas, preservação do host, revogação e proteção dos históricos pessoais.
- **Custos e riscos:** gestão de identidades/chaves, fricção no pareamento, superfície de ataque de rede, possível comprometimento de nós já autorizados, atrasos e falhas de revogação em trânsito, dependências de transporte e firewall.
- **Riscos remanescentes:** nó aprovado pode ser comprometido posteriormente e copiar dados que já recebeu; criptografia de transporte não prova execução correta do modelo nem elimina prompts adversariais; proteções granulares exigem análise de threat model e testes.

## Gates de aceitação candidatos

1. Worker LAN de leitura/cálculo, sem interface de mutação do BG2:EE, pareado em sessão explicitamente autorizada.
2. Descoberta de nó malicioso ou duplicado não permite envio de contexto, chave, save ou tarefa.
3. Tentativas de impersonação, man-in-the-middle, replay, downgrade de transporte, certificado/chave substituídos e escopo vencido falham fechadas e geram alertas minimizados.
4. ACL impede transmissão de segredos não relevantes; caches e logs não revelam informação privada.
5. Revogação bloqueia novos jobs e resultados antigos não podem alterar narrativa; job `UNCERTAIN` com efeito mecânico não pode ser repetido automaticamente.
6. Fallback single-host funciona sem LAN e a queda do worker não cria segundo host nem corrompe checkpoint.
7. Ensaiar host + dois clientes no BG2:EE limpo com EEex/bridge **somente quando os gates pré-requisitos permitirem**, sem supor compatibilidade mecânica existente.

**Situação atual:** exclusivamente decisão de Discovery. Nenhum serviço pareado, teste de criptografia, autenticação ou integração multiplayer foi executado. **Próxima proposta: DEC-059 — roteamento de tarefas/modelos de IA sob políticas de privacidade, capacidade e fallback**, em articulação com a DEC-006 ainda aberta.
