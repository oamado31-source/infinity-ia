# Evidência S1c — inventário de áreas da instalação e pacote 1369 DR (single player, 2026-11-09)

**Gate:** S1 (etapa 1, ADR-0113), parte "c": SPEC-005 (REQ-CANON-001/002/004). **Resultado:** infraestrutura, inventário real e **primeiro lote de curadoria (6 entradas conferidas pelo mantenedor) APROVADOS no laboratório ARM64/VM** (CR-2026-001). Single player.
**Executado por:** Claude Code via SSH (leitura da cópia `BG2EE-P1`, gravação local no Mac).

## Inventário real

| Item | Valor |
|---|---|
| Build | `sha256:c05b2b97…` (BG2:EE 2.7.3.0 + EEex Minimal + probe; mesma de S1a/S1b) |
| Idioma | `pt_BR` (`lang/pt_BR/dialog.tlk` da instalação) |
| Áreas na build | **423** (recursos ARE da KEY + `override/*.are`) |
| No mapa-múndi | **45**, em dois mapas (números 0 e 2), todas com nome no jogo |
| `AR0602` (masmorra) | fora do mapa-múndi → **sem nome do jogo**; continua com a curadoria provisória |
| Exemplos | `AR0300`, `AR0700`, `AR1000` com nomes de distrito em pt_BR (lidos do jogo, não reproduzidos no repo) |
| Tempo | ~30 s, só leituras parciais por SSH (KEY inteira, tabela do BIF, WMP, entradas e strings necessárias do TLK) |
| Destino | `~/.infinity-ai/knowledge/install-c05b2b973695b622/areas.pt_BR.json` (Mac, fora do repo) |

Nenhum arquivo do jogo foi salvo no Mac: as fatias ficam em memória e só o inventário derivado é gravado. O extrator recusa caminhos dentro do repositório e `tests/test_gamedata.py` falha se algum inventário for commitado.

**Primeira tentativa:** a leitura em lote estourou o limite de linha de comando do Windows (~8 KB) ao resolver os textos; o transporte passou a enviar os pedidos pela entrada padrão do SSH (`lab_ssh.run_ps(..., stdin=...)`). KEY, BIF e WMP já haviam sido lidos corretamente na primeira tentativa.

## Diálogo

O serviço de diálogo carregou os 45 nomes do inventário (`nomes de area do jogo (inventario local): 45`). Precedência verificada: nome do jogo (S0) → curadoria provisória → "um lugar que você não sabe nomear". Como o grupo está na masmorra (sem nome no jogo), a fala ainda usa o nome provisório até a party sair para uma área do mapa-múndi.

## Pacote 1369 DR — ponto de partida (antes da curadoria)

- `knowledge/periods/1369-DR/manifest.json` começou como `coverage_status = PARTIAL`, `IN_CURATION` (hoje `FIRST_BATCH_CHECKED`).
- `region:athkatla` e `region:amn` começaram como esqueletos `RESEARCH_ONLY` ligados a áreas da build; conferidos no lote abaixo.
- `knowledge/sources/`: *Lands of Intrigue*, *Grand History of the Realms*, *FR Campaign Setting 3e* (ambientado em 1372 DR), manual do BG2 (dados bibliográficos `TO_CONFIRM`), dados do jogo (`CONFIRMED`).
- Gate sobre o pacote real: Athkatla com áreas na build → `WEAK_SOURCE` (ainda `RESEARCH_ONLY`); sem áreas na build → `UNMAPPED_REGION`; ano 1370 → `WRONG_YEAR`.

## Primeiro lote de curadoria (livros do mantenedor)

Livros em PDF numa pasta privada fora do repositório; lidos por extração de texto, com página impressa anotada. O PDF do *FR Campaign Setting 3e* abre com 0 páginas (arquivo corrompido) e ficou de fora.

| Entrada | Status | Fontes |
|---|---|---|
| `event:bg2-campaign-year` | `CAMPAIGN_CANON` | manual do BG2, seção "The Role of Years" (PDF p. 34); *Grand History* pp. 148–149 |
| `region:athkatla` | `SOURCE_CHECKED` | manual "Athkatla" (PDF p. 27); *Lands of Intrigue* Livro Dois, p. 7; dados do jogo |
| `region:amn` | `SOURCE_CHECKED` | *Lands of Intrigue* Livro Dois, p. 2; manual "Amn" (PDF p. 26); dados do jogo |
| `org:council-of-six` | `SOURCE_CHECKED` | manual (PDF p. 27); *Lands of Intrigue* Livro Dois, p. 7 |
| `org:shadow-thieves` | `SOURCE_CHECKED` | manual (PDF pp. 27–28); *Lands of Intrigue* Livro Três, p. 17 |
| `org:cowled-wizards` | `SOURCE_CHECKED` | manual (PDF p. 28); *Lands of Intrigue* Livro Três, p. 8 |

**Conflito resolvido pelo mantenedor:** o manual trata 1369 DR como o ano corrente; o *Grand History* põe a trama de Irenicus em 1368 DR. Decisão de 2026-11-09: a campanha adota 1369 DR (manual), alinhada ao ADR-0013; a divergência fica documentada na própria entrada.

**Achado de datação:** o "presente" do *Lands of Intrigue* é 1370 DR ("Amn of Today", Livro Dois, p. 23), embora suas tabelas mercantis valham até o fim de 1369 (Livro Dois, p. 14). As entradas que o citam têm validade explícita 1369–1370; sem isso o gate recusa (`SETTING_YEAR_MISMATCH`), como para o FR3e (1372 DR).

**Gate com o inventário real (423 áreas):** as 6 entradas → `CANON_OK`. **Pin:** `KnowledgePackPinned` gravado no banco de laboratório (revisão `sha256:e1f09733…`, 6 entradas); `check_pin` passou de `NOT_PINNED` a `MATCH`.

Os resumos são texto nosso (≤ 280 caracteres), sem citações; nenhum trecho, imagem ou mapa dos livros está no repositório.

## Pendências

Próximos lotes (marcos de 1369 DR do *Grand History*, famílias e casas mercantis do *Lands of Intrigue*), confirmação bibliográfica das obras (edição/ISBN), cópia legível do FR3e, regra de conhecimento comum regional para NPCs (ADR-0059), REQ-CANON-003 e segunda região; Windows nativo.
