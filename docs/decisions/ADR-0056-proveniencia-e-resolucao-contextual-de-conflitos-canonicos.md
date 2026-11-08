# ADR-0056 — Proveniência de fontes e resolução contextual de conflitos canônicos

- **Decisão:** **DEC-061**, opção **C**, escolhida pelo idealizador em **2026-11-06**.
- **Status:** **APROVADA como política arquitetural de Discovery**, ainda sem implementação/POC.
- **Pacote:** Infinity AI Discovery **v5.7**.
- **Documento técnico:** `docs/61-governanca-de-fontes-conflitos-e-curadoria-por-periodo.md`.
- **Dependências e precedência:** DEC-060/C (ADR-0055, inclusive adendo de diretórios físicos anuais), DEC-008/009/022/023 (cronologia/ramo), DEC-028/029 (ACL e conhecimento), DEC-031 (facções), DEC-059 (roteamento) e DEC-015 (gates, aberta).

## Contexto

A separação física do conhecimento por ano DR impede a busca indiscriminada entre épocas, mas **não** resolve discrepâncias entre fontes pertinentes ao **mesmo ano**, nem diferenças entre voz de narrador, rumor, retcon editorial, tradução, precisão de data, material de jogo e mudanças legítimas da campanha. Atribuir automaticamente prioridade ao livro mais recente ou permitir que um LLM sintetize versões incompatíveis pode fabricar um cânone inexistente.

## Alternativas consideradas

- **A — hierarquia fixa de fontes:** fácil de automatizar, porém perde contexto temporal/editorial e pode sobrepor fatos de validade diferente.
- **B — consolidação automática por IA:** oferece cobertura aparente, porém a fluência não é evidência de correção e pode encobrir contradições.
- **C — manter fontes/versionamentos, analisar contexto e submeter conflitos importantes à curadoria:** **APROVADA**.

## Decisão e invariantes

1. **Preservar o isolamento físico da DEC-060.** Cada alegação canônica integra a partição física de seu **ano DR pertinente** (`knowledge/periods/<ano>-DR/{categoria}/`). O ano confirmado do mundo determina a busca primária. Anos anteriores são abertos somente por necessidade/continuidade e validade verificada; **anos futuros nunca viram fatos consumados** por busca transversal. Esta ADR não propõe um corpus monolítico.
2. **Alegação não equivale a fato resolvido.** Registrar separadamente alegações individuais de fontes, conjuntos de conflito e eventuais resoluções curatoriais. A existência de um texto em um arquivo não atesta verdade, conhecimento do NPC, autorização de publicação ou ocorrência na campanha.
3. **Proveniência obrigatória nas futuras entradas.** Metadados candidatos incluem `claim_id`, `entity_id`, atributo/alegação, `source_id` verificável e localização na obra, tipo/edição/versão, data editorial real se conhecida, época DR e precisão, região, perspectiva do narrador, estado epistêmico, resumo próprio, validade e licença/escopo de uso. Campos desconhecidos permanecem `UNKNOWN`, não são inventados.
4. **Detectar e classificar discrepâncias sem criar consenso.** Considerar: fatos complementares, diferenças legítimas entre datas/locais, informação narrada por personagem ou boato, variantes editoriais/retcons, interpretações concorrentes e **contradição irresolvida**. Um LLM pode sugerir hipóteses com evidências, mas não homologar o cânone sozinho.
5. **Resolução curada, contextual e auditável.** Quando a evidência permitir, associar a um conflito uma decisão justificada, escopo exato (época, região, edição/build e/ou ramo), referências consultadas, responsável pela curadoria, revisão e alternativas preservadas. **Não há precedência global cega** do material mais recente; qualquer preferência editorial exigirá regra explícita e fundamentada para seu contexto.
6. **Conflito não resolvido é estado legítimo.** Respostas factuais assertivas e mudanças persistentes de maior impacto ficam em `DEFER/ESCALATE` ou são substituídas por fala segura e não específica. Uma opinião/rumor pode ser representada como crença atribuída, desde que ACL, aprendizagem e proveniência a autorizem. Não apresentar alternativas divergentes como conhecimento onisciente.
7. **Alterações da campanha não corrigem nem reescrevem o cânone.** Divergências causais de jogadores são registradas nos overlays por `campaign_id/branch_id/ano/revision`, depois de eventos confirmados. A resolução canônica de base continua versionada e somente-leitura durante a partida.
8. **Consulta e publicação em duas etapas.** O resolvedor filtra partição, vigência, fonte, escopo, edição/instalação, estado de curadoria e ACL **antes do prompt**; DEC-060 revalida alegações antes de publicar ou gerar efeito. Resultado de fonte não confiável ou prompt injection jamais dá instruções ao sistema.
9. **Invalidação de versões e rastreabilidade.** Revisões curatoriais/novas fontes devem invalidar caches ou projeções afetadas e produzir auditoria com ID do conflito e revisão da partição. Não retconar diálogos, saves, histórico de PCs ou consequências já confirmadas sem política/autorização específica.
10. **Privacidade, licença e segurança.** Guardar referências bibliográficas/identificadores e resumos originais necessários à curadoria; não copiar automaticamente livros/assets proprietários para o pacote. Acesso a fonte não é permissão de distribuição nem licença para reprodução. Nós LAN recebem apenas conteúdo filtrado e autorizado.

## Consequências

**Benefícios:** decisões explicáveis, versões concorrentes preservadas, melhor consistência por ano, personagens com conhecimento limitado, suporte a expansão progressiva de lore e possibilidade de revisão editorial futura sem apagar evidências.

**Custos:** trabalho de curadoria, metadados, versionamento, estados de conflito/indeterminação, cobertura inicial parcial, possíveis respostas adiadas e cache/indexação complexos. A política não garante que fontes estejam corretas nem que se possa catalogar todo Forgotten Realms.

## Critérios de aceite candidatos (não executados)

- Duas fontes incompatíveis em 1369 DR permanecem separadas com `source_id`; não gerar terceira versão inventada.
- Mudança de liderança entre 1368 e 1369 DR não é falsamente classificada como contradição se intervalos justificarem a diferença.
- Alegação exclusiva de 1370 DR não é recuperada como fato de 1369 DR.
- Retcon/editorial e rumor de NPC não se tornam fato confirmado por simples priorização temporal.
- Conflito `UNRESOLVED` bloqueia fato assertivo de alto impacto; revisão curada registra justificativa e versão e preserva divergência.
- Mudança causal da campanha não modifica arquivos canônicos nem vaza para outro ramo ou personagem sem autorização.
- Worker LAN recebe somente alegações filtradas; metadados/índices não expõem segredos ou conteúdos de anos não permitidos.
- Testes do documento 61 e DEC-015/POCs ainda devem verificar falsos positivos, custo e latência.

## Limites e próxima discussão

- **DEC-006, DEC-013, DEC-015 e DEC-018 permanecem abertas.** Sem modelos, bancos de lore preenchidos, parser de documentos, esquema definitivo, importador, pipeline de curadoria ou BG2:EE/EEex multiplayer testados.
- **DEC-062 (aberta):** como receber novas obras/fontes e promover conteúdo às partições anuais por fluxo de ingestão, revisão e publicação, sem importar material protegido ou misturar épocas.
