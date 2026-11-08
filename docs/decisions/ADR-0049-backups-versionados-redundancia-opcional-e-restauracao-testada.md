# ADR-0049 — Backups versionados, redundância opcional e restauração verificada

- **Decisão:** DEC-054 — como proteger operacionalmente as campanhas persistentes contra falha de armazenamento, corrupção, exclusão acidental e erro humano.
- **Escolha expressa:** **C — backups automáticos versionados, redundância opcional e recuperação testada**.
- **Estado:** **APROVADA** pelo idealizador em 2026-11-06.
- **Versão:** Infinity AI Discovery **v5.0**.
- **Fase:** Discovery/SDD. Política arquitetural, **não há backup nem recuperação executados no BG2:EE**.
- **Relacionada a:** DEC-001/004 (isolamento de campanhas/modos), DEC-008 (event log e snapshots), DEC-011/012 (autoridade e gateway), DEC-018 (operação geral, permanece aberta), DEC-022 (tempo), DEC-028/041 (segredos/ACL), DEC-043 (legado), DEC-050/051/052 (conteúdo, build e migração), DEC-053 (checkpoint coordenado).
- **Detalhamento:** `docs/54-backups-versionados-retencao-e-ensaios-de-restauracao.md`.

## Contexto

Um checkpoint verificado pela DEC-053 une save do host BG2:EE e revisão da memória narrativa com identidade, hashes, build, ramo, eventos e evidências. Essa coerência não protege contra falha do mesmo disco, exclusão, corrupção posterior ou impossibilidade de leitura em uma nova instalação. A campanha necessita de política de **retenção, armazenamento, verificação, recuperação e segurança**, mas sem alegar atomicidade ou suporte de save automático não comprovados no motor.

## Decisão aprovada

1. **Origem verificável:** executar backup apenas de **conjuntos íntegros e elegíveis** segundo a DEC-053; copiar o par `save mecânico + snapshot/revisão/event-log` e **manifesto, políticas, build e identificadores necessários à reconstrução**, com consistência e vínculo verificáveis. Um arquivo isolado não será promovido a backup recuperável de campanha.
2. **Automação condicionada à integração:** quando a integração for demonstrada, automatizar backup **de checkpoints publicados**, com intervalos/eventos configuráveis (p.ex. após checkpoint válido, fim de sessão e antes de atualização). Não pressupor acesso programático a save BG2:EE, nem fabricar checkpoints por mera cópia em momento arbitrário.
3. **Histórico versionado e retenção configurável:** manter versões históricas com rotação por idade, quantidade e espaço; considerar marcos selecionados e cópias pré-migração como **pinadas**. A política exata, limites de uso, prazos e critérios quantitativos ficam para SPECS.
4. **Proteção da última recuperação viável:** limpeza/garbage collection deve verificar referências e integridade. **Nunca apagar automaticamente a única cópia recuperável conhecida**, nem remover par dependente de logs, manifestos, chave ou build. Falta de espaço torna o serviço `DEGRADED`/`FAILED`, não autoriza eliminação silenciosa da proteção.
5. **Redundância opcional e independente:** fornecer capacidade de cópia em destino distinto do armazenamento principal — disco externo, NAS ou armazenamento remoto **com adesão explícita do anfitrião**, sem impor nuvem, cobrança ou upload oculto. Cópias no mesmo disco não contam como independentes; cópia remota deverá ser criptografada e ter política de acesso configurada.
6. **Privacidade e controle de acesso:** permitir somente operadores autorizados; isolar campanhas, modo Original/Living World, jogadores e ramos; proteger segredos e material pessoal por ACL, criptografia quando aplicável, minimização de índices/logs e remoção segura conforme capacidades do meio. Guardar chaves separadamente do material cifrado quando praticável; perda de chave torna a restauração impossível, mesmo com hashes válidos.
7. **Integridade e disponibilidade não equivalem a recuperação:** conferir checksums, completude, manifesto e vínculos de armazenamento após cópia; realizar **ensaios regulares de restauração em ambiente isolado**, avaliando continuidade do banco e, nos gates de integração, carregamento/progressão de saves no mesmo build e sincronização host + dois clientes. Hash igual não prova save jogável, quest funcional ou restore real.
8. **Restauração controlada e não destrutiva:** apresentar pontos elegíveis ao anfitrião; ensaiar recuperação usando cópias, com autorização para restaurar na campanha ativa. Preservar o estado anterior quando possível e a trilha de auditoria; não misturar metade do backup A com metade do backup B, nem avançar relógio ou reaplicar mutações `UNCERTAIN` sem conciliação.
9. **Migração de builds:** antes de uma migração DEC-052, preservar checkpoint verificado e backup íntegro da **build A**, incluindo condições para reinstalação autorizada; backups da build B não substituem a reserva de rollback até a validação funcional e aprovação explícita. Não prometer redistribuição legal de arquivos de mods/jogo.
10. **Estados operacionais auditáveis:** registrar tentativas, falhas, cópias, idade do último ponto recuperável, testes de restore e alertas, com dados minimizados; se não houver redundância independente, declarar proteção **local apenas** e risco de falha de dispositivo. Falha recorrente de backup exige visibilidade e ação; não relatar sucesso não comprovado.
11. **Privacidade em ramos temporais:** restauração de save antigo não injeta automaticamente informações secretas, reputações ou eventos posteriores no ramo recuperado (DEC-028/053).
12. **Segurança contra exclusão/corrupção em massa:** isolamento de privilégios e, quando suportado pelo destino, proteção de versões contra sobrescrita/ransomware e política de exclusão com revisão para cópias pinadas; não prometer imutabilidade em qualquer mídia.

## Consequências

**Benefícios:** menor exposição à perda de progresso, rollback de migrações mais prudente, histórico recuperável em múltiplos pontos e transparência sobre falhas. **Custos e trade-offs:** uso de disco, manutenção de cópias, verificação de chaves, possibilidade de atrasos de salvamento, testes periódicos e segurança operacional. Não é garantia de zero perda de dados.

## Fora do escopo aprovado / pendente de SPECS

- Não aprova serviço de nuvem obrigatório, sincronização externa automática sem consentimento, serviço pago, captura de save em qualquer instante, auto-reparo irrestrito, restauração atômica, rollback garantido de mods, indisponibilidade zero, nem recuperação de dados sem chave criptográfica.
- **DEC-018 permanece aberta** para observabilidade geral, diagnóstico, trilhas operacionais e resposta a incidentes; DEC-055 propõe esse próximo tema.
- Cadência, número de gerações, RPO/RTO, quotas, algoritmos de compactação, layout de diretórios e criptografia local serão especificados por perfis após capacidades e riscos reais serem medidos.
- A viabilidade das ações automáticas e de restauração no BG2:EE/EEex multiplayer segue não comprovada.

## Critérios candidatos de aceitação

1. Backup de par certificado preserva identificadores/hashes, watermark e todos os artefatos necessários, sem mistura de builds/modos/ramos.
2. Backup de metade ou cópia truncada fica não recuperável; cópia anterior verificada continua intacta.
3. Rotação respeita versões pinadas, dependências, última cópia íntegra e falha por espaço, sem exclusões destrutivas.
4. Redundância externa só ocorre com consentimento; ausência do destino torna o estado degradado e notifica, sem declarações falsas.
5. Restauração de ensaio usa ambiente isolado e confirma continuidade do estado narrativo; no POC, save/reload e progressão com host + dois clientes.
6. Restore de build incompatível, histórico de outro ramo, segredo sem autorização ou chave ausente é bloqueado e auditado.

**Próxima discussão:** DEC-055 — observabilidade e resposta a incidentes: que eventos monitorar, como alertar e quais ações seguras automatizar sem ultrapassar a autoridade do anfitrião.
