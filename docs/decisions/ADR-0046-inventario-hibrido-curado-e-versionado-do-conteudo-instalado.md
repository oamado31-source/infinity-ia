# ADR-0046 — Inventário híbrido, curado e versionado do conteúdo instalado

- **Decisão:** DEC-051 — como identificar e manter o catálogo de recursos, scripts, missões, diálogos, romances e dependências na instalação concreta do jogo e seus mods.
- **Escolha expressa:** **C — inventário automatizado com curadoria e validação por build**.
- **Estado:** **APROVADA** pelo idealizador em 2026-11-06.
- **Versão:** Infinity AI Discovery **v4.7**.
- **Fase:** arquitetura SDD/Discovery, não especificação final nem implementação verificada.
- **Complementa:** DEC-003 (BG2:EE limpo antes de mods), DEC-011 (host mecânico), DEC-012 (Action Gateway), DEC-008/009 (persistência e cronologia), DEC-014 (regras antes do modelo), DEC-024/025/034 (eventos canônicos e autorização), DEC-028 (conhecimento e segredos), DEC-049 (NPCs independentes), DEC-050 (reconciliador de scripts e eventos).
- **Desenho detalhado:** `docs/51-inventario-hibrido-de-conteudo-por-build-e-proveniencia.md`.

## Contexto

A DEC-050 permite histórias alternativas somente se o Infinity AI não romper missões, romances ou scripts existentes. Entretanto, BG2:EE, EET e combinações com outros mods podem conter recursos distintos, substituições de arquivos e conflitos introduzidos pela ordem de instalação. Uma lista genérica de conteúdo de Forgotten Realms não descreve com fidelidade os recursos realmente instalados, muito menos seus estados durante uma sessão. Também não é seguro inferir que a ausência de um recurso identificado equivale à inexistência de uma dependência.

## Decisão aprovada

1. **Fingerprint por instalação/build:** registrar identificadores do jogo, edições/versões quando detectáveis, configuração relevante, ordem de instalação dos mods quando documentável, evidências de arquivos e hashes adequados, data de captura e identificador estável do manifesto. Usar fontes de metadados disponíveis; nenhum formato específico está garantido nesta fase.
2. **Descoberta automatizada somente de leitura:** propor varredura de recursos instalados de missão, script, diálogo, criatura, área e configuração, conforme ferramentas/formats suportados e posteriormente verificados; nunca modificar a instalação no processo de inventariar.
3. **Catálogo curado e rastreável:** relacionar recursos identificados a entidades, quests, diálogos, romances e dependências, com nomes/aliases, fonte, atribuição a jogo/mod, época, estado de revisão, alcance de cobertura e evidências. Distinguir extração de interpretação humana.
4. **Separar recursos estáticos de estado vivo:** um arquivo instalado pode indicar a existência de scripts ou condições, mas não confirma o valor corrente de flags, etapas de quests, personagens vivos ou romances ativos. Estado runtime exige leitura autorizada e POC próprios, reconciliada com o host.
5. **Qualidade explícita do conhecimento:** cada afirmação deve indicar `VERIFIED`, `OBSERVED`, `INFERRED`, `UNKNOWN` ou `CONFLICTED` (valores candidatos para SPECS). Recurso ausente em uma varredura incompleta permanece `UNKNOWN`, não `ABSENT`. Afirmar ausência exige cobertura comprovada da fonte e do build relevante.
6. **Gates por build, não permissão universal:** a cobertura e os testes de uma instalação não autorizam automaticamente outra. Mudança detectada de versão, ordem de mods, recursos relevantes ou manifesto invalida as aprovações dependentes até reavaliação.
7. **Reconciliador e gateway:** propostas dinâmicas incluem build/manifesto, evidências de estado/versão e dependências relevantes. O reconciliador da DEC-050 aplica `ALLOW`, `ADAPT`, `DEFER`, `BLOCK` ou `DIVERGENCE_REVIEW`; operações mecânicas continuam sujeitas ao gateway, risco, autorização e confirmação do host.
8. **Escopo progressivo:** iniciar pelo BG2:EE limpo; adicionar EEex/bridge read-only e testes; ampliar depois para EET/IWD/NWNForBG e outros mods com manifestos independentes e sua ordem de instalação correta. Não é promessa de compatibilidade ou cobertura integral.
9. **Segurança e distribuição:** registrar identificadores e evidências suficientes para reproduzir resultados sem incluir, por padrão, conteúdos proprietários do jogo ou arquivos de mods redistribuídos no pacote Discovery. Não publicar segredos de campanhas, saves ou dados privados em inventários de diagnóstico.

## Consequências

- Positiva: reduz divergências acidentais de quests e torna verificável por que uma proposta pode ou não ser aplicada a um build.
- Positiva: reutiliza classificações curadas entre instalações apenas quando as evidências de compatibilidade correspondem.
- Custo: manutenção de extratores, referências por formato, catálogos, revisões e testes de regressão por build.
- Risco: um inventário estático não captura ordem de execução, condições ocultas ou runtime; tratar toda interpretação como hipótese até validação.
- Risco: falsos positivos/negativos, recursos sobrescritos, TLK/ID/aliases ambíguos e modificações feitas após a captura. Preflight conservador e logs obrigatórios.

## Fora do escopo / não presumir

- Extração completa automática de semântica de scripts, compreensão de quests via LLM, leitura confiável de flags vivas ou compatibilidade de ferramentas em qualquer build.
- Modificar o conteúdo instalado, manipular scripts, instalar mods, executar ações do motor ou aprovar divergências canônicas nesta fase.
- Aprovar migrações de campanhas/saves entre builds alterados: assunto específico para **DEC-052**.

## Gates candidatos

1. Identificar fingerprint de duas cópias de BG2:EE com e sem uma alteração deliberada; distinguir mudança real de variação de metadados irrelevantes.
2. Inventariar recursos da instalação limpa em modo leitura e mapear uma missão/companheiro conhecido com evidências verificáveis, inclusive dependências não resolvidas.
3. Testar inconsistências de ordem de mods, sobrescritas, aliases, recursos desconhecidos, scans parciais e manifestos desatualizados: mutações com dependências desconhecidas devem ser bloqueadas.
4. Comparar catálogo e estados observados apenas por mecanismos suportados; nunca deduzir estado runtime com base exclusiva em arquivos estáticos.
5. Testar gate de reconciliação e gateway em cópia isolada com host, dois clientes, save/load e logs; repetir para novos builds/mods conforme capacidade demonstrada.

**Próximo tema aberto:** DEC-052 — congelamento da instalação por campanha e migrações controladas quando versões ou mods mudarem.
