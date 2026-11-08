# ADR-0048 — Checkpoints coordenados e reconciliação segura entre save mecânico e memória narrativa

- **Decisão:** DEC-053 — manter estados de campanha recuperáveis quando o save do host BG2:EE e o estado persistente externo do Infinity AI evoluírem em ritmos diferentes.
- **Escolha expressa:** **C — checkpoints coordenados com reconciliação segura**.
- **Estado:** **APROVADA** pelo idealizador em 2026-11-06.
- **Versão:** Infinity AI Discovery **v4.9**.
- **Fase:** Discovery/SDD; não há integração de salvamento, captura atômica, restauração ou ensaio multiplayer executado.
- **Relacionada a:** DEC-001/003/004 (campanha e modos), DEC-008 (snapshots + event log), DEC-011 (host confirma mecânica), DEC-012 (gateway e idempotência), DEC-018 (operação e recuperação, ainda aberta), DEC-021/022 (simulação/catch-up), DEC-027/034 (eventos HIGH), DEC-028/041 (ACL/segredos), DEC-045/046 (controle de PCs), DEC-050/051/052 (scripts, builds e migrações).
- **Desenho técnico complementar:** `docs/53-checkpoints-coordenados-recuperacao-e-consistencia-da-campanha.md`.

## Contexto

BG2:EE controla personagens, inventário, combate, flags e a continuidade mecânica; o Infinity AI mantém histórico narrativo, facções, conhecimento, reputação, objetivos e eventos confirmados. O save do jogo e o banco externo **não compartilham uma transação atômica comprovada**. Crashes, timeout, desconexões, cópia incompleta, autosaves e carregamento de saves anteriores podem produzir duas versões do mesmo mundo. Nenhuma fonte deve fingir autoridade sobre a outra.

## Decisão aprovada

1. **Par de estado vinculado:** cada checkpoint **publicado e verificado** associa um save mecânico identificável e íntegro a uma revisão do estado narrativo, watermark do event log, build/manifesto, relógio, revisão de políticas e identidade da campanha/modo. Cada cópia conserva proveniência e escopos de acesso.
2. **Coordenação sem presumir atomicidade:** propor uma janela segura de quiescência, sem novas mutações enquanto se captura o par; realizar save pelo procedimento efetivamente suportado (manual ou automatizado após POC), observar seu término, copiar e verificar hash; capturar snapshot/log na revisão compatível. Publicar **somente depois** de validar ambas as partes e sua associação. Caso pause/quiescência não sejam demonstráveis, **não rotular como checkpoint coerente**.
3. **Manifesto e estado de publicação:** checkpoint candidato permanece `PREPARING`/`CAPTURED`/`VERIFYING`, nunca elegível para recuperação até `VERIFIED`/`PUBLISHED` com provas suficientes. Um save isolado ou snapshot isolado não se converte implicitamente em checkpoint utilizável.
4. **Autoridades preservadas:** host é autoridade para efeitos mecânicos observados e Infinity AI para fatos narrativos confirmados com evidência; o LLM não escolhe estado vencedor nem fabrica resultado de ação. Divergências são comparadas por IDs, revisões, receipts e fatos comprováveis.
5. **Recuperação conservadora:** após crash/reload, identificar build, campanha, save e revisão; verificar hash, identidade do snapshot e watermark; escolher **somente par coerente comprovado** e reconciliar a fila de ações pendentes. Não restaurar automaticamente narrativo mais recente sobre save antigo nem afirmar que evento narrado ocorreu mecanicamente.
6. **`UNCERTAIN` e não duplicação:** operações enviadas ao host sem confirmação suficiente ficam pendentes; antes de qualquer retry, obter observação confiável ou intervenção autorizada. IDs idempotentes e receipts impedem pagamento/recompensa, morte, spawn ou alteração de quest executados duas vezes.
7. **Rewind e ramificação:** carregar save anterior pode criar divergência com eventos narrativos posteriores. Não apagar silenciosamente um log confirmado nem transformar automaticamente esses eventos em fatos do passado recuperado. Preservar a auditoria da linha original e estabelecer ramo/epoch de recuperação ou reconciliação autorizada, sem cruzar conhecimento de futuros alternativos.
8. **Privacidade e isolamento:** checkpoints do modo Original e Living World, campanhas e jogadores permanecem isolados. Segredos, históricos e identidades exigem ACL, minimização de logs e proteção de backups; clientes não são autoridade para declarar par recuperado.
9. **Multiplayer:** verificar estado do host após save/load, redistribuição de personagens e reconexão; avaliar no mínimo host e dois clientes nas POCs. Estado narrativo só avança para eventos mecânicos confirmados.
10. **Falha fechada:** corrupção, ausência de qualquer metade, build divergente, autorização insuficiente ou diferença não conciliável levam a `BLOCKED`/`QUARANTINED`/`MANUAL_REVIEW` conforme futura SPEC; manter cópias prévias intactas, sem replay destrutivo.
11. **Compatibilidade com a DEC-052:** migração só pode utilizar par certificado no build A e produzir novo par certificado no build B em ambiente isolado; rollback por restauração de cópias coerentes e testadas, jamais por promessa de undo entre motor e banco.
12. **Registro auditável:** trilha inclui origem de cada artefato, hash, versões, revisão, escopo de campanha, decisões, verificações e eventos incertos, sem expor segredos em relatórios globais.

## Limites de escopo e definições adiadas

- **Não aprova** save programático, interceptação de autosaves, transação distribuída/2PC real com BG2:EE, restauração de flags por IA, suporte EEex multiplayer, alteração direta de saves, reconstrução universal a partir de logs, retorno automático de qualquer checkpoint, nem exclusão silenciosa de histórico.
- **DEC-018 permanece aberta** para política operacional: cadência, retenção, armazenamento, testes periódicos de restauração, observabilidade, cópias externas e resposta a incidentes.
- **DEC-013/015 permanecem abertas:** matriz real de compatibilidade e critérios de aceitação POCs; nomes de estados e esquema dos registros são **candidatos** até SPEC.
- Recuperação de campanha não é igual a desfazer efeitos mecânicos de ações que já chegaram ao host; revisões alternativas requerem salvamento/prova própria.

## Consequências

- **Benefícios:** menor risco de save e memória contarem histórias divergentes; auditoria de ramificações; detecção de corrupção e repetição de operações; migrações mais seguras.
- **Custos:** janelas de checkpoint, armazenamento extra, monitoramento, revisão de operações incertas, testes com vários clientes e possíveis bloqueios de retomada.
- **Preferência explícita:** é melhor interromper uma retomada duvidosa do que fabricar sucesso ou corromper uma campanha de longo prazo.

## Critérios candidatos de aceitação para SPECS/POCs

1. Capturar save e revisão externa com o mesmo `campaign_id`, `mode`, `build_id` e epoch; validar hash e watermark antes de publicar.
2. Interromper gravação depois de salvar só uma metade; candidato permanece não publicável e checkpoint anterior continua recuperável.
3. Confirmar que evento `UNCERTAIN` não é reexecutado cegamente após crash, reconexão ou mudança de build.
4. Carregar save antigo e detectar memória narrativa posterior, com isolamento de ramo e sem revelação de fatos do futuro descartado.
5. Ensaiar recuperação de par anterior em cópias; validar host e dois clientes após save/load, sem sobrescrever dados originais.
6. Alterar arquivo, build ou log e demonstrar bloqueio por integridade/identidade.

**Próxima discussão sugerida:** **DEC-054 — política operacional de backup, retenção e recuperação verificável**, aprofundando a DEC-018 sem alterar a arquitetura de checkpoint agora aprovada.
