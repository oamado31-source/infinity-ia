# SPEC-010 — Inventário Geográfico Multijogo e de Áreas Externas

**Projeto:** Infinity AI · **Versão:** 1.1 (proposta para aprovação) · **Data:** 17/11/2026  
**Estado:** PROPOSTA. Registrada no repositório em 2026-11-17, a pedido do mantenedor ("registrar essa nova SPEC"). Implementação, instalação ou integração só com as decisões do §11 e uma CR própria (ADR-0111).  
**Natureza:** diretriz de inventário e validação; **não** autoriza integração, redistribuição nem geração de novas áreas  
**Alvo de execução:** BG2:EE / EEex; EET e outras engines mediante testes separados  
**Cronologia-piloto:** 1369 DR; outras datas tratadas como variantes, não importadas automaticamente.

## 1. Objetivo e resultado esperado

Estabelecer um **registro geográfico único, rastreável e reproduzível** dos mapas que o Infinity AI poderia utilizar **sem criar cenários novos**. O inventário deve abranger (a) jogos-base e expansões do escopo do projeto, (b) conversões e ports e (c) mods comunitários. A saída deve responder, por **região → localidade → subárea → arquivo**, onde o mapa existe, que tipo de espaço representa, se é novo ou repetido, de onde veio, qual a época representada e o que falta para sua utilização.

**Não objetivos:** criar mapas, instalar mods na instalação principal, prometer compatibilidade, copiar recursos proprietários para GitHub, distribuir artes de terceiros ou assumir que a existência de um arquivo `.ARE` implica área inédita e jogável.

## 2. Escopo de cobertura e unidade de contagem

### 2.1 Conjunto-base a deduplicar

- **Baldur's Gate:** jogo original / Enhanced Edition e Tales of the Sword Coast.
- **Siege of Dragonspear** e material adicional compatível com a linha BG1/SoD.
- **Baldur's Gate II:** Shadows of Amn e Throne of Bhaal / Enhanced Edition.
- **Icewind Dale:** jogo original, Heart of Winter e Trials of the Luremaster / Enhanced Edition.
- **Icewind Dale II** (tratado como fonte própria, com diferenças de engine).
- **Neverwinter Nights:** campanha original, Shadows of Undrentide e Hordes of the Underdark; por não utilizar a Infinity Engine, seus mapas originais são referências até que exista uma conversão específica comprovada.
- **EET e ports**: não são automaticamente 'novas áreas'; registrar a representação e a compatibilidade de cada recurso.

### 2.2 Granularidade

**Região:** porção geográfica de Faerûn (ex.: Cormyr). **Localidade:** cidade, vila, ruína, fortaleza, ilha ou complexo (ex.: Suzail). **Subárea:** mapa efetivamente carregável (ex.: distrito, esgoto, interior, andar de dungeon). **Recurso:** arquivos de suporte à subárea, identificados por `resref`, caminho e hash. Uma localidade pode conter dezenas de subáreas; uma subárea pode ter variantes dia/noite e dependências.

Os números de `.ARE` nas tabelas são **contagens brutas da árvore do repositório**, não contagens de localidades, mapas inéditos, recursos distribuíveis ou integrações concluídas. A soma bruta de 1.434 arquivos dos 13 repositórios auditados é **somente um indicador de volume a classificar**.

## 3. Regras normativas de classificação

**Evidência de disponibilidade (dimensões independentes):**

- `DISCOVERED`: anúncio ou repositório identificado.
- `SOURCE_VISIBLE`: recursos/arquivos localizados na árvore.
- `DOWNLOAD_VERIFIED`: release ou pacote acessível localizado.
- `ASSET_PARSED`: ARE/WED/TIS/PVRZ, referências e nomes inspecionados.
- `INSTALLED_TESTED`: instalação isolada e testes executados.
- `RIGHTS_CLEARED`: direitos e escopo de permissão verificados.
- `INTEGRATION_APPROVED`: decisão formal e testes concluídos para um pacote/versionamento específico.

Nenhuma dimensão implica as outras. Uma beta pública pode ser testável e **não** reutilizável em outro projeto. Uma área anunciada, como as de BG2 Rebirth, deve aparecer como `ANNOUNCED_ONLY` enquanto não houver pacote ou arquivos examinados.

**Papel da área:** `BASE_GAME`, `EXPANSION`, `PORT_OF_BASE`, `NEW_MOD_AREA`, `MODIFIED_BASE`, `VARIANT`, `REFERENCE_ONLY`, `UNKNOWN`. **Tipo:** `CITY`, `DISTRICT`, `VILLAGE`, `KEEP`, `CASTLE`, `DUNGEON`, `CAVE`, `SEWER`, `FOREST`, `WILDERNESS`, `RUINS`, `TEMPLE`, `INTERIOR`, `ISLAND`, `UNDERDARK`, `PLANE`, `OTHER`. **Cobertura:** `COMPLETE`, `PARTIAL`, `UNMAPPED`, `UNVERIFIED`. A classificação deve aceitar múltiplos tipos e conexões por área.

**Regra de honestidade:** um nome citado no README não comprova um arquivo específico; um `.ARE` sem nome não comprova uma cidade; `resref` igual entre mods pode ser colisão, e `resref` diferente pode representar a mesma arte. Não atribuir coordenadas, nomes, lore ou números de andares por inferência sem evidência.

## 4. Fontes e rastreabilidade

### 4.1 Fontes primárias e fontes de descoberta

O inventário deve distinguir **fontes primárias**, que comprovam a existência e o conteúdo de um mod (repositório do autor, release, instalador, arquivos e documentação oficial), de **fontes de descoberta**, que apenas apontam para possíveis projetos (guias comunitários, coleções Steam, listas de mods, fóruns e wikis). Uma fonte de descoberta nunca comprova, isoladamente, disponibilidade, conteúdo de arquivos, compatibilidade ou permissão de reutilização.

Guias comunitários devem ser tratados como índices de referências. Cada link extraído deve gerar um candidato independente no registro de fontes, ser normalizado para seu repositório/página canônica e passar pelo mesmo processo de validação dos demais projetos. Registrar também a data de consulta e, quando disponível, a versão/data do guia. Páginas removidas, ocultas ou inacessíveis podem ser usadas somente quando houver conteúdo verificável preservado; não inferir o conteúdo ausente a partir do título.

**Caso inicial — guia Steam `Yosharian's BG2 Builds/Modding`:** a página Steam `https://steamcommunity.com/sharedfiles/filedetails/?id=3546634271` foi identificada como fonte de descoberta, mas aparece removida/incompatível na consulta realizada. As referências que puderam ser identificadas incluem Loretakers, Black Hearts, BP-BGT Worldmap, EEex, IETME e Sword Coast Stratagems. O guia não é um pacote de mapas e não deve ser contado como fonte de áreas. Loretakers já consta no inventário; Black Hearts deve ser cadastrado como candidato pendente de auditoria. BP-BGT Worldmap e EEex são ferramentas/infraestrutura, não áreas exploráveis; IETME é ferramenta de edição; Sword Coast Stratagems é mod de regras/encontros, não fonte de novas áreas, salvo evidência posterior em contrário.

Para cada entrada, armazenar URL canônica, commit/tag, data da coleta, arquivo e trecho que sustentam a classificação, hashes dos recursos e, quando possível, evidência de instalação. Priorizar README, instaladores WeiDU (`.tp2`), listas de áreas, `worldmap`, `TLK`, arquivos `.ARE/.WED/.TIS/.PVRZ`, documentação e releases. Anúncios e fóruns são evidência de intenção/descrição, não de recurso instalado.

**Direitos:** acesso público, código-fonte disponível, licença de código, licença da arte e autorização para distribuição são questões separadas. Não tratar GitHub público como open source. Recursos derivados de jogos comerciais exigem análise própria; projetos que reutilizam arte de terceiros devem ser marcados `THIRD_PARTY_RISK`. O catálogo pode guardar metadados e hashes sem redistribuir os recursos.

## 5. Contrato de dados mínimo

```yaml
area_record_id: string
source:
  project: string
  repository_url: string | null
  release_url: string | null
  version: string | null
  commit: string | null
  collected_at: ISO8601
  evidence: [string]
rights:
  code_license: string | UNKNOWN
  asset_license: string | UNKNOWN
  asset_provenance: [string]
  permission_status: OPEN_LICENSE | PERMISSION_GRANTED | RESTRICTED | UNKNOWN | THIRD_PARTY_RISK
geography:
  region_id: string | UNKNOWN
  locality_id: string | UNKNOWN
  locality_name: string | UNKNOWN
  subarea_name: string | UNKNOWN
  canonicality: CANON | MOD_ADDITION | ADAPTATION | UNKNOWN
  era_start_dr: integer | null
  era_end_dr: integer | null
  geometry_reference: string | null
area:
  resref: string | UNKNOWN
  type: [CITY, DISTRICT, VILLAGE, KEEP, CASTLE, DUNGEON, CAVE, SEWER, FOREST, WILDERNESS, RUINS, TEMPLE, INTERIOR, ISLAND, UNDERDARK, PLANE, OTHER]
  role: BASE_GAME | EXPANSION | PORT_OF_BASE | NEW_MOD_AREA | MODIFIED_BASE | VARIANT | REFERENCE_ONLY | UNKNOWN
  file_paths: {are: string | null, wed: string | null, tis: [string], pvrz: [string], wmp: [string]}
  hashes: {sha256: [string]}
  links_to: [string]
validation:
  evidence_status: [DISCOVERED, SOURCE_VISIBLE, DOWNLOAD_VERIFIED, ASSET_PARSED, INSTALLED_TESTED, RIGHTS_CLEARED, INTEGRATION_APPROVED]
  compatibility: UNTESTED | PASSED | FAILED | CONFLICT
  base_overlap: NONE | EXACT | DERIVED | POSSIBLE | UNKNOWN
  notes: string
```

Os valores `UNKNOWN`/`null` devem ser preservados em vez de preenchidos por conjectura. A classificação de uma região como 'coberta' exige pelo menos uma subárea identificada e documentada; 'cobertura completa' requer um critério específico de escopo, não mera presença de um mapa.

## 6. Requisitos verificáveis

- **REQ-AREA-001 — Fontes-base:** inventariar separadamente os jogos e expansões do §2, suas instalações/versões e seus recursos; não contabilizar ports como expansão geográfica líquida.
- **REQ-AREA-002 — Fontes externas:** catalogar repositórios, releases, arquivos, autores, versões, dependências e direitos sem incorporar binários ao repositório do Infinity AI.
- **REQ-AREA-003 — Extração:** coletar `resref`, `.ARE`, `.WED`, `.TIS`, `.PVRZ`, `.WMP`, textos e metadados de instaladores, com hash e proveniência.
- **REQ-AREA-004 — Geografia:** vincular `resref → subárea → localidade → região → período`, preservando incertezas e evidências.
- **REQ-AREA-005 — Tipologia:** diferenciar cidades, distritos, vilas, fortalezas/keeps, castelos, masmorras, cavernas, esgotos, ruínas, florestas, exteriores e interiores.
- **REQ-AREA-006 — Deduplicação:** detectar igualdade exata, variantes e adaptações; não deduplicar exclusivamente pelo nome ou `resref`.
- **REQ-AREA-007 — Direitos:** registrar permissões de código e assets separadamente; impedir promoção para reutilização quando a situação jurídica não estiver clara.
- **REQ-AREA-008 — Cronologia:** manter mapas e eventos em camadas separadas; nunca importar automaticamente estado de quests/NPCs de outra época para 1369 DR.
- **REQ-AREA-009 — Compatibilidade:** executar instalação e testes somente em cópia isolada, verificando carregamento, transições, portas, pathfinding, gráficos, save/load e reversibilidade.
- **REQ-AREA-010 — Relatórios:** gerar visão por região/localidade/subárea, fonte, tipo, disponibilidade, direitos, compatibilidade e sobreposição com base.
- **REQ-AREA-011 — Cobertura líquida:** calcular separadamente `arquivos_brutos`, `subareas_identificadas`, `subareas_unicas`, `subareas_adicionais_ao_escopo_base`, `subareas_tecnicamente_validadas` e `subareas_com_direitos_liberados`.
- **REQ-AREA-012 — Evidência:** qualquer contagem, nome ou afirmação de inclusão deve apontar para fonte/arquivo/versão; não promover anúncios a mapas disponíveis.
- **REQ-AREA-013 — Governança:** alterações de integração e geração de áreas exigem decisão e escopo próprios, sem modificar main diretamente.
- **REQ-AREA-014 — Reprodutibilidade:** armazenar snapshots do inventário, hashes e datas para que mudanças nos projetos externos não alterem silenciosamente o catálogo.
- **REQ-AREA-015 — Guias e coleções como descoberta:** registrar guias comunitários, coleções Steam, índices de mods e listas de fóruns como fontes de descoberta, mantendo explícita a distinção em relação às fontes primárias.
- **REQ-AREA-016 — Extração de referências:** extrair e normalizar links de projetos citados em guias; criar um registro candidato por projeto, preservar a URL de origem e evitar duplicatas por URL canônica, proprietário/repositório e identidade do mod.
- **REQ-AREA-017 — Revalidação de candidatos:** verificar individualmente a existência do projeto, disponibilidade atual, release/download, conteúdo geográfico, arquivos de área, dependências, compatibilidade e direitos. Um link em guia não promove automaticamente o projeto a `SOURCE_VISIBLE`, `DOWNLOAD_VERIFIED` ou `RIGHTS_CLEARED`.
- **REQ-AREA-018 — Classificação funcional de referências:** classificar cada referência descoberta como `AREA_CONTENT`, `WORLD_MAP_INFRASTRUCTURE`, `ENGINE_EXTENSION`, `MODDING_TOOL`, `RULES_OR_AI_MOD`, `DOCUMENTATION` ou `UNKNOWN`, para evitar contabilizar ferramentas e mods de regras como cobertura geográfica.

## 7. Fluxo de execução e critérios de aceite

1. **Descoberta:** localizar projeto, fonte canônica, versão, download e licença; marcar pendências.
2. **Inventário estático:** enumerar recursos, arquivos WeiDU, dependências e referências de worldmap.
3. **Extração semântica:** interpretar nomes e relações entre `ARE/WED/TIS/PVRZ/WMP/TLK`, com evidência por subárea.
4. **Confronto com a base:** deduplicar BG/SoD/BG2/IWD/IWD2/NWN e seus ports; marcar variantes.
5. **Verificação de direitos:** separar consulta, uso local, adaptação e redistribuição; obter autorizações quando necessárias.
6. **Laboratório isolado:** testar compatibilidade com BG2:EE/EEex e, quando aplicável, EET.
7. **Relatórios e aprovação:** produzir matriz por localidade e lista de lacunas, sem realizar importação automática.

**Aceite do inventário v1:** (a) toda fonte auditada tem URL e versão/snapshot; (b) cada `.ARE` encontrado tem registro ou justificativa explícita de exclusão; (c) áreas não nomeadas permanecem `UNKNOWN`; (d) o relatório separa áreas-base, ports e adições; (e) nenhum asset de terceiros é redistribuído; (f) nenhum recurso é declarado integrado sem testes e autorização.

## 8. Cenários de validação

- **VAL-AREA-13:** um guia Steam removido é registrado como fonte de descoberta, sem ser tratado como pacote instalável ou fonte primária.
- **VAL-AREA-14:** um mod citado por guia (ex.: Black Hearts) vira candidato separado e só entra na cobertura após auditoria de repositório, release, arquivos, geografia e direitos.
- **VAL-AREA-15:** ferramentas (EEex, IETME), infraestrutura de mapa-múndi (BP-BGT Worldmap) e mods de regras (Sword Coast Stratagems) são classificados por função e não somados como novas áreas jogáveis.

- **T-AREA-01:** duas versões do mesmo `.ARE` geram duas entradas de proveniência e uma relação de variante, sem inflar localidades.
- **T-AREA-02:** colisão de `resref` entre mods é sinalizada, não mesclada.
- **T-AREA-03:** área de IWD1_EET já existente em IWD não aumenta cobertura líquida.
- **T-AREA-04:** área anunciada do Rebirth permanece indisponível até identificação do arquivo.
- **T-AREA-05:** `.ARE` presente sem `.WED` ou recursos obrigatórios fica incompleto e não aprovado.
- **T-AREA-06:** arquivo com arte de terceiro sem autorização não é promovido para reutilização.
- **T-AREA-07:** mapa de 1371 DR pode ser referência espacial, mas não importa eventos de 1371 DR para 1369 DR.
- **T-AREA-08:** cidade com um distrito conhecido é classificada como cobertura parcial, não completa.
- **T-AREA-09:** mapa-múndi `.WMP` não é contado como área explorável.
- **T-AREA-10:** instalação em laboratório não altera os arquivos originais nem o branch protegido.
- **T-AREA-11:** relatório lista dungeons e keeps individualmente, e não apenas as cidades que os contêm.
- **T-AREA-12:** atualização de release não substitui silenciosamente o snapshot anterior.

## 9. Integração arquitetural e governança

A SPEC-010 é uma **fonte de metadados**, não o próprio banco de conhecimento dos NPCs. Ela alimentará catálogo de lugares, worldmap e conexões geográficas; SPECs de conhecimento/memória consultarão apenas localidades validadas conforme seu escopo e época. O mapa visual, a verdade canônica e a crença individual de um NPC são entidades diferentes. Respeitar ADR-0012 e governança de alterações da ADR-0111, com CR, `plan.md`, `tasks.md`, testes e PR quando a implementação for aprovada. A criação automática de novas áreas será objeto de especificação/decisão posterior, não desta SPEC: é a SPEC-014 (proposta aprovada em 2026-11-27), que usa este inventário como catálogo de fontes.

## 10. Inventário inicial de fontes e cobertura

O material abaixo é **baseline de auditoria** e não equivale a aprovação de uso. Mantém as contagens e evidências de 17/11/2026 para orientar o inventário por arquivo.

## A. Inventário de repositórios com contagem observada

| Projeto | `.ARE` na árvore | Evidência de distribuição | Cobertura geográfica e tipos documentados | Situação para Infinity AI |
|---|---:|---|---|---|
| [NWNForBG](https://github.com/abalabokhin/NWNForBG) | 368 | GitHub público; tag 1.00 (31/12/2025), sem arquivo de release confirmado nesta auditoria | Neverwinter e campanha NWN original; cidade, distritos, arredores, florestas, masmorras, interiores e outras áreas da adaptação; classificação exata por resref pendente | R1; alta utilidade, mas README alerta sobre arte de outros jogos: auditoria de direitos obrigatória |
| [IWD1_EET](https://github.com/The-Gate-Project/IWD1_EET) | 174 | GitHub público; README com ordem de instalação; projeto beta | Easthaven, Kuldahar, Vale of Shadows, Dragon's Eye, Severed Hand, Dorn's Deep, Wyrm's Tooth; Heart of Winter/Trials of the Luremaster no escopo declarado; cidades, vales, cavernas, fortalezas e dungeons | R1; assets derivados dos jogos, requer propriedade legítima e verificação de direitos |
| [IWD2_EET](https://github.com/The-Gate-Project/IWD2_EET) | 115 | GitHub público; README com ordem de instalação; beta | Targos, Shaengarne, Horde Fortress, Fell Wood, Black Raven Monastery, Dragon's Eye, Kuldahar; cidade, fortalezas, bosques, mosteiro, dungeons | R1; validar compatibilidade e diferenças de IWD2 |
| [Silverrealms](https://github.com/AciferBG/Silverrealms) | 114 | **Release v0.910, 16/11/2026**, ZIP beta alemã | Underdark; **Iltkazar**, cidade anã com vários distritos; cavernas, construções e masmorras; >100 áreas anunciado | R1+R2; **todos os direitos reservados** |
| [Region of Terror](https://github.com/Spellhold-Studios/Region-of-Terror) | 164 | Repositório público; README com instruções de download | Norte/áreas associadas a Drizzt, **Bremen, Maribur, Spirit Soaring**; quatro novas cidades/vilas segundo autor; exteriores, cidades, interiores, dungeons | R1; >160 áreas anunciado, origem/qualidade dos recursos deve ser avaliada |
| [The Darkest Day](https://github.com/Spellhold-Studios/The-Darkest-Day) | 161 | Repositório público; edição EE requer integração TDDz | **Riatavin, Eshpurta**, Amn e localidades associadas; cidade, interiores, áreas rurais e dungeons | R1; `.ARE` podem incluir patches de áreas existentes; não assumir 161 novas |
| [Check the Bodies](https://github.com/Spellhold-Studios/Check-the-Bodies) | 129 | **Release v3.0** (15/12/2024) com ZIP | **Hlondeth** e outras áreas; README informa **160 áreas no conjunto, 15 novas e uma cidade**; cidades, interiores, missões e dungeons | R1+R2; **129 arquivos não significam 129 áreas novas** |
| [Shadows over Soubar](https://github.com/Spellhold-Studios/Shadows-over-Soubar) | 95 | Repositório público; README com download e instalação | **Soubar**, conexões à região de Trademeet, áreas rurais, cidades/interiores e missões; README diz mais de 100 áreas novas ou alteradas | R1; distinguir modificações das áreas base |
| [Call of the Lost Goddess](https://github.com/AciferBG/Call-of-the-Lost-Goddess) | 46 | **Release v3.3, 17/10/2026**, ZIP | **Goldspires** (distrito urbano), áreas de aventura, interiores e dungeons; **45 cenários 3D novos + 1 adaptação de IWD** | R1+R2; todos os direitos reservados |
| [Poisoned Pathways](https://github.com/AciferBG/Poisoned-Pathways) | 31 | **Release v1.8, 17/10/2026**, ZIP | **Vila florestal** e **ruína élfica assombrada**, outros mapas de aventura; ligação à trama de Renfeld/Athkatla | R1+R2; localização exata da vila/ruína e direitos pendentes |
| [Throne of the Mad God](https://github.com/AciferBG/Throne-of-the-Mad-God) | 16 | **Release v2.6, 17/10/2026**, ZIP | **Troll Mountains**, norte de Amn; complexo anão subterrâneo, dungeons, acessos | R1+R2; 16 áreas novas anunciadas; todos os direitos reservados |
| [Dark Tidings](https://github.com/AciferBG/Dark-Tidings) | 14 | **Release v3.2, 18/09/2026**, ZIP | **Ilha de Irphong**, **Sea Tower**, litoral e instalações de aventura; parte do distrito portuário de Athkatla é área base | R1+R2; todos os direitos reservados |
| [Loretakers](https://github.com/AciferBG/Loretakers) | 7 | **Release v3.0, 17/10/2026**, ZIP | **Baldur's Gate**, masmorra sob a cidade, acesso pelo santuário de Oghma; dungeon e interiores | R1+R2; todos os direitos reservados |
| [BP-BGT Worldmap](https://github.com/Spellhold-Studios/BP-BGT-Worldmap) | 0 | Repositório público; mapas-múndi, scripts, imagens e instalador | **Mapa-múndi**, ligações e ícones; **não** representa conjunto de cenários exploráveis `.ARE` | R1 para sistema geográfico, não somar como áreas |

**Subtotal bruto dos 13 repositórios com `.ARE`: 1.434 arquivos.** É um teto de inventário bruto, **não** uma quantidade de áreas adicionais integráveis; parte se sobrepõe a jogos originais, contém adaptações ou depende de terceiros. Repositórios históricos duplicados/forks não foram somados duas vezes.

## B. Projetos com cobertura anunciada, sem inventário binário nesta auditoria

| Projeto | Locais e tipos anunciados | Acesso confirmado | Pendência |
|---|---|---|---|
| [BG2 Rebirth](https://www.bg2rebirthmod.com/bg2rebirthmod/) / [anúncio](https://www.gibberlings3.net/forums/topic/40754-announcing-baldurs-gate-2-rebirth-tc-mod-for-ee/) | **Cormyr, 1371 DR:** Suzail (9 áreas de superfície + 9 esgotos), Castle Crag, Castle High Horn, Eveningstar, Wheloon, Waymoot, Immersea, Dhedluk, Tyrluk, Collinwood, Crownpost, Knightswood, Yeoman's Bridge, Espar, Mouth of Gargoyles, Minroe, Moonever, Blustich, Bogbrook, Monksblade, Battlerise, Kirinwood, Junirill, Ghars, Hultail, Thunderstone; mundo navegável, vilas, cidades, castelos, esgotos | Site/anúncio público | **Nenhum pacote instalável verificado**; não contar no total de arquivos disponíveis; conversão total, requer negociação com autor |
| Secret of Bone Hill | Bone Hill e entorno; vila, ruínas e dungeons | Índice Spellhold | Localizar release, contar `.ARE`, origem geográfica e licença |
| Northern Tales of the Sword Coast | Costa da Espada, novas áreas e quests | Índice Spellhold | Identificar repositório canônico e `.ARE` |
| Dark Side of the Sword Coast | Costa da Espada, novos locais e áreas alteradas | Índice Spellhold | Inventário e versão EET |
| Fishing for Trouble | Vila, áreas rurais, dungeons | Índice Spellhold | Localização geográfica precisa e contagem |
| Trials of the Luremaster para BG | Castle Maluradek e dungeons de IWD | Índice Spellhold | Evitar duplicidade com IWD1_EET |
| The Darkest Day z | Compatibilização EE de TDD | Índice Spellhold | Não somar como novo pacote independente sem verificar assets |
| Mods menores: Balduran's Seatower, Athkatlan Grounds | Baldur's Gate, Athkatla, áreas de aventura | Diretório Sigil-IE | Inventariar separadamente, contar `.ARE` e direitos |
| [Black Hearts](https://github.com/11jo/Black-Hearts) | **Candidato: contagem não verificada** | Repositório público identificado por guia comunitário; confirmar árvore, releases e licença na auditoria | Conteúdo adicional associado a BG1/SoD; Beregost é indicado como ponto de início. Tipos e quantidade de áreas inéditas ainda não confirmados por inspeção dos recursos | `DISCOVERED`; não somar a cobertura até confirmar `.ARE`, áreas, dependências, compatibilidade e direitos |

## C. Matriz geográfica preliminar por local e tipo

| Região | Localidade | Projeto-fonte | Tipos de mapas potencialmente adicionados | Grau de evidência |
|---|---|---|---|---|
| Cormyr | Suzail | BG2 Rebirth | 9 áreas urbanas + 9 esgotos | Anúncio do autor; não disponível |
| Cormyr | Castle Crag; Castle High Horn | BG2 Rebirth | Castelos, interiores e possíveis acessos | Anúncio; número de subáreas desconhecido |
| Cormyr | Eveningstar, Wheloon, Waymoot, Immersea, Dhedluk, Tyrluk, Collinwood, Crownpost, Knightswood, Yeoman's Bridge, Espar, Mouth of Gargoyles, Minroe, Moonever, Blustich, Bogbrook, Monksblade, Battlerise, Kirinwood, Junirill, Ghars, Hultail, Thunderstone | BG2 Rebirth | Vilas/cidades e entorno; número por local desconhecido | Anúncio; não disponível |
| Norte da Costa da Espada | Neverwinter e arredores; Port Llast, Luskan e outras regiões da campanha NWN | NWNForBG | Distritos, interiores, florestas, cavernas, fortalezas e dungeons | `.ARE` presentes; associação individual pendente |
| Icewind Dale | Easthaven, Kuldahar, Vale of Shadows, Dragon's Eye, Severed Hand, Dorn's Deep, Wyrm's Tooth, Lonelywood, Burial Isle, Gloomfrost, Castle Maluradek | IWD1_EET | Vilas, floresta, vale, ruínas, fortalezas, cavernas, castelo e dungeons | `.ARE` presentes; delimitar base/expansões |
| Icewind Dale / Spine of the World | Targos, Shaengarne, Horde Fortress, Fell Wood, Black Raven Monastery, Dragon's Eye, Kuldahar | IWD2_EET | Cidade, forte, floresta, mosteiro e dungeons | `.ARE` presentes; localização por ID pendente |
| Underdark sob Lands of Intrigue | **Iltkazar** | Silverrealms | Cidade anã com distritos, cavernas, interiores e dungeons | Beta pública; 114 `.ARE` |
| Norte de Amn | **Troll Mountains** | Throne of the Mad God | Complexo anão, masmorras e áreas de acesso | Release; 16 `.ARE` |
| Costa de Amn | **Irphong / Sea Tower** | Dark Tidings | Ilha, torre/farol, interiores, encontros costeiros | Release; 14 `.ARE` |
| Amn / novo distrito | **Goldspires** | Call of the Lost Goddess | Distrito urbano, interiores, dungeons, locais de aventura | Release; 46 `.ARE` |
| Amn / arredores de Athkatla | **Vila florestal e ruína élfica** (nomes e localização a confirmar) | Poisoned Pathways | Vila, floresta, ruínas, dungeons | Release; 31 `.ARE` |
| Baldur's Gate | **Masmorra sob a cidade / Oghma's Shrine** | Loretakers | Dungeon, passagens, interiores | Release; 7 `.ARE` |
| Vilhon Reach | **Hlondeth** | Check the Bodies | Cidade e interiores | Release; README declara 15 áreas novas no mod |
| Amn | **Riatavin; Eshpurta** | The Darkest Day | Cidades, interiores e arredores | Repositório; `.ARE` não classificados |
| Região de Soubar | **Soubar** | Shadows over Soubar | Cidade, áreas rurais, interiores, aventuras | Repositório; `.ARE` não classificados |
| Norte / Icewind Dale | **Bremen; Maribur; Spirit Soaring** | Region of Terror | Vila/cidade, exterior de edifício, interiores, dungeons | Repositório; origem e sobreposição pendentes |

**Atenção:** `IWD1_EET` e `IWD2_EET` são adaptações de materiais **já previstos no escopo base** do Infinity AI; não somá-los como expansão geográfica líquida. A mesma cautela vale para `NWNForBG`. A expansão líquida é a soma de locais ou subáreas *não existentes* na base e *compatíveis*, após deduplicação por localidade, `resref`, geometria e origem de recursos.


## D. Fontes comunitárias de descoberta e candidatos derivados

### D.1 Guia Steam consultado

- **Título identificado:** `Yosharian's BG2 Builds/Modding`.
- **URL:** https://steamcommunity.com/sharedfiles/filedetails/?id=3546634271
- **Papel no inventário:** `DISCOVERY_SOURCE`; não contém, por si só, um pacote de mapas do Infinity AI.
- **Estado observado:** a página aparece removida/incompatível na consulta. Tratar referências preservadas ou já identificadas como pistas; não presumir que o conteúdo integral permaneça acessível.
- **Referências extraídas para classificação:** Loretakers, Black Hearts, BP-BGT Worldmap, EEex, IETME e Sword Coast Stratagems.

| Referência | Classe | Tratamento na SPEC-010 | Situação no inventário |
|---|---|---|---|
| [Loretakers](https://github.com/AciferBG/Loretakers) | `AREA_CONTENT` | Já inventariado; relacionar a referência Steam como descoberta adicional, sem duplicar contagem | 7 `.ARE` na auditoria anterior; direitos reservados, autorização necessária |
| [Black Hearts](https://github.com/11jo/Black-Hearts) | `AREA_CONTENT_CANDIDATE` | Criar registro candidato e inspecionar repositório, releases, instalador e recursos | Não contar áreas até identificar e classificar os arquivos e localidades |
| [BP-BGT Worldmap](https://github.com/SpellholdStudios/BP-BGT-Worldmap) | `WORLD_MAP_INFRASTRUCTURE` | Catalogar como infraestrutura de navegação e integração geográfica | Não somar como áreas `.ARE` exploráveis |
| [EEex](https://github.com/BGforgeNet/EEex) | `ENGINE_EXTENSION` | Registrar como dependência/ferramenta de engine quando aplicável | Não é conteúdo geográfico |
| IETME | `MODDING_TOOL` | Registrar na lista de ferramentas de edição e avaliar apenas se necessário | Não é conteúdo geográfico |
| [Sword Coast Stratagems](https://github.com/Gibberlings3/SwordCoastStratagems) | `RULES_OR_AI_MOD` | Registrar como referência de regras/IA e compatibilidade de mods | Não contar como novas áreas sem evidência de recursos geográficos |

### D.1.1 Ferramentas de criação de áreas (acrescentadas em 2026-11-27, SPEC-014)

Classe `MODDING_TOOL`: não são conteúdo geográfico e não somam cobertura. O uso de cada uma está na SPEC-014, §4.

| Ferramenta | Versão e licença (consulta de 2026-11-27) | Função |
|---|---|---|
| [MapSmithEE](https://github.com/sad0/MapSmithEE) | 0.2.6, prévia; CC BY-NC-SA 4.0 (o README estende a licença ao que é feito com ele) | monta uma área (`ARE`, `TIS`/`PVRZ`, `WED`, mapas de busca, altura e luz) a partir de uma cena 3D renderizada no Blender; só referência e ferramenta do mantenedor |
| [Near Infinity](https://github.com/Argent77/NearInfinity) | ativo; LGPL-2.1 | navegador e editor de recursos do motor |
| DLTCEP | versão não conferida | editor antigo de recursos do motor (projeto GemRB) |

### D.2 Procedimento para novos guias e coleções

1. Capturar URL, título, autor/publicador, data de publicação/atualização e estado de acesso.
2. Extrair todos os links e nomes de mods, preservando o contexto em que foram mencionados.
3. Normalizar URLs e deduplicar projetos já registrados.
4. Classificar cada referência por função; separar conteúdo de áreas, infraestrutura, ferramenta, extensão de engine, mod de regras e documentação.
5. Verificar fonte primária, versão, release, instalador, arquivos e licença.
6. Somente após a inspeção dos recursos atribuir localidade, subárea, tipo e contagem geográfica.
7. Registrar referências quebradas/removidas como `UNAVAILABLE_AT_CHECK` sem apagar a trilha de proveniência.

## 11. Próximas decisões pendentes

1. Confirmar o número `SPEC-010` e o namespace de requisitos no repositório atual antes da abertura de PR.
2. Aprovar o escopo do primeiro inventário (BG2:EE + mods com releases, ou todos os jogos-base de uma vez).
3. Definir o formato físico do catálogo (JSON/SQLite) e convenção de IDs geográficos.
4. Decidir quais projetos merecem solicitação de autorização aos autores; **BG2 Rebirth** permanece apenas como referência anunciada.
5. Só após a auditoria de compatibilidade e direitos avaliar uma proposta separada para instalação e integração.

**Estado final deste documento:** SPEC registrada como **proposta de diretriz** (versão 1.1). A versão 1.1 acrescenta descoberta sistemática por guias comunitários e o candidato Black Hearts, sem promover referências não verificadas a cobertura disponível. Nenhum repositório, mod ou instalação foi modificado.
