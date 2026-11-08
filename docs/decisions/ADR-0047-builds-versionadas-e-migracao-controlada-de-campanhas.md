# ADR-0047 — Instalações versionadas e migração controlada de campanhas persistentes

- **Decisão:** DEC-052 — como evoluir BG2:EE, EEex, EET e outros mods durante uma campanha persistente sem corromper saves, quests ou histórico narrativo.
- **Escolha expressa:** **C — builds versionadas com migração controlada, testes, backups e autorização do anfitrião**.
- **Estado:** **APROVADA** pelo idealizador em 2026-11-06.
- **Versão:** Infinity AI Discovery **v4.8**.
- **Fase:** arquitetura SDD/Discovery; não há instalador, migrador, restauração ou compatibilidade do motor demonstrados.
- **Relacionada a:** DEC-001/003 (coop privado e ordem de instalação); DEC-008/011 (persistência/autoridade); DEC-012/027/034 (gateway e eventos críticos); DEC-013 (matriz técnica aberta); DEC-018 (recuperação aberta); DEC-021/022 (catch-up/tempo); DEC-050/051 (reconciliação e inventário por build).
- **Desenho complementar:** `docs/52-migracao-controlada-de-builds-e-campanhas-persistentes.md`.

## Contexto

Uma campanha Living World depende simultaneamente de arquivos instalados, ordem/versionamento de mods, saves mecânicos do BG2:EE, registros de eventos e snapshots narrativos, catálogo de conteúdos, permissões e condições das quests. Atualizações podem adicionar, renomear ou sobrescrever scripts, recursos, IDs, diálogos e condições. Um save que carrega aparentemente não prova que continua apto a completar missões, nem que dois clientes compartilham o mesmo estado. A DEC-051 diagnostica o conteúdo instalado; **não autoriza a migração**.

## Decisão aprovada

1. **Pin imutável por campanha:** toda campanha ativa referencia o identificador/fingerprint de uma build de referência, incluindo jogo, mods, ordem e artefatos comprováveis. Mudanças de instalação não alteram silenciosamente o estado ativo.
2. **Novas builds isoladas:** preparar alterações em cópia/ambiente de teste separado, sem sobrescrever a instalação, saves ou dados narrativos originais. Registrar dependências, origem, hashes e diferenças por ferramentas read-only da DEC-051.
3. **Ponto de recuperação anterior à migração:** preservar cópia íntegra e verificável dos saves do host, estado narrativo/event log, manifestos, política de campanha, configurações relevantes e versão dos esquemas. Relacionar os artefatos por `campaign_id`, `source_build_id` e um identificador de checkpoint. Não presumir operação atômica entre jogo e banco de dados.
4. **Plano e avaliação explícitos:** construir diff de conteúdo e migrações de esquema/identidade para o que tiver suporte; marcar dependências `UNKNOWN`, `CONFLICTED` ou não mapeadas como bloqueantes. Reavaliar quests, diálogos, romances, NPCs, variáveis e interações relevantes da DEC-050.
5. **Ensaiar em cópias, não em produção:** testar carregamento, salvamento, recuperação, progressão de quests, áreas, inventários, status de personagens, consistência do log narrativo, persistência de segredos, host e no mínimo dois clientes conectados; repetir em save/load e reconexão conforme houver capacidade demonstrada.
6. **Transição deliberada do anfitrião:** só publicar a nova build como referência ativa após evidências suficientes, nenhuma inconsistência bloqueante, autorização explícita do anfitrião e confirmação dos estados esperados. Troca de build invalida permissões e evidências específicas da build anterior até nova certificação. IA não aprova a migração.
7. **Falha fechada e conservação:** se a validação falhar, não migrar. A campanha continua na build anterior, com seus dados intactos. Restaurar a cópia coerente preservada se um teste ou tentativa controlada causar dano; não afirmar que desinstalar mod ou reverter bytes automaticamente reverte estados de quests/saves.
8. **Registros auditáveis:** manter histórico de tentativa, motivos de aprovação/bloqueio, comparativo de manifests, resultados de testes, identidade do autorizador, snapshots e estado do processo. Não reexecutar cegamente operação `UNCERTAIN`.
9. **Segurança e direitos:** não redistribuir ativos proprietários de jogos/mods; limitar coleta de caminhos privados e segredos de PCs; proteger backups com permissões adequadas.
10. **Escopo técnico progressivo:** validar inicialmente BG2:EE limpo no Windows; tratar EEex/EET/IWD/NWNForBG como casos independentes que exigem sua própria matriz e provas. Nem toda atualização, especialmente remoção/reordenação de mods, será migrável.

## Fronteiras e escolhas adiadas

- **Não aprova** hot update durante sessão, migrador automático universal, manutenção de campanha em qualquer versão, remoção arbitrária de mods, sincronização garantida de EEex ou modpacks, rollback atômico entre dois sistemas nem modificação direta de save de produção.
- **DEC-013 permanece aberta:** formatos específicos de manifesto, versões validadas, ordem final dos mods e matriz real de compatibilidade não foram determinados.
- **DEC-018 permanece aberta:** frequência/retenção/consistência dos checkpoints e política operacional de recuperação ainda dependem de uma decisão posterior (DEC-053 proposta).
- **DEC-008/011 preservadas:** host confirma estado mecânico; Infinity AI preserva log narrativo, com reconciliação explícita em vez de inferir sucesso de uma instalação.

## Consequências

- Benefícios: reduz risco de perder campanhas extensas; permite aproveitar melhorias quando migração for demonstravelmente segura; viabiliza diagnóstico de regressões por build.
- Custos: armazenamento para builds e backups, testes por modpack, manutenção de mapas de compatibilidade, documentação de casos não migráveis.
- Falha esperada: uma campanha pode permanecer indefinidamente em build antiga quando não houver evidências suficientes para transição. Isso é correto e preferível à corrupção silenciosa.

## Gates candidatos para SPECS/POCs

1. Reproduzir fingerprint da instalação limpa e detectar mudança de um mod na ordem/configuração.
2. Criar backup auditável e restaurar uma cópia com hash íntegro; provar que original foi preservado.
3. Carregar, salvar e continuar quest no build de origem antes do ensaio de migração.
4. Ensaiar atualização em ambiente isolado, sem alterar instalação/saves de origem.
5. Verificar mapa de conteúdos/schemas, dependências desconhecidas e regressões funcionais.
6. Verificar a mesma campanha em host e dois clientes, com save/load e reconexão.
7. Forçar incompatibilidade e comprovar bloqueio da promoção, manutenção do baseline e logs.
8. Testar falha/timeout e recuperação de par coerente entre save e banco narrativo, sem replay cego.

**Próxima discussão sugerida:** DEC-053 — checkpoint coerente e recuperação coordenada do save mecânico com o estado narrativo externo, aprofundando a DEC-018.
