# Evidência P1 — loader EEex no laboratório Windows 11 ARM64 (2026-11-08)

**Gate:** P1 (ADR-0108, `docs/architecture/testing.md`: "loader inicializa sem falhas na build"). **Resultado:** APROVADO **no laboratório ARM64/VM** do CR-2026-001 (ainda PROPOSED). Não vale como P1 em Windows x86-64 nativo.
**Pré-requisito:** P0 aprovado no mesmo laboratório (`P0-2026-11-08-laboratorio-arm64.md`).
**Executado por:** Claude Code via SSH (download, verificação, instalação, coleta) e mantenedor (passos de jogo).

## Componentes

| Item | Valor |
|---|---|
| Ambiente | Windows 11 Pro 10.0.26100, ARM64, VMware Fusion em Mac Apple Silicon |
| Jogo | BG2:EE Steam 2.7.3.0, `Baldur.exe` x64 sha256 `b51093a4…14d57` (inalterado pela instalação) |
| EEex | v1.3.1 (release oficial `Bubb13/EEex`, 2026-10-07), `eeex-v1.3.1.zip` sha256 `9c8104bd63fe7e7dfff889d89ab2d98e158b6e552846370a924ed7eacea4ecf3` (confere com o digest publicado) |
| Instalador | `Setup-EEex.exe` (WeiDU 251, sem assinatura Authenticode; integridade pelo hash do zip) |
| Componentes | preset "Minimal": `#0` Quick Menu Core e `#1` EEex (sem módulos de jogabilidade, sem LuaJIT) |
| Runtime | Visual C++ 2015-2022 x64 v14.42.34438 (já presente) |
| Cópia | `C:\InfinityLab\BG2EE-P1`, criada da instalação Steam limpa; a cópia P0 ficou intacta |

## Identidade após instalação

- `build_fingerprint`: `sha256:c05b2b973695b622de21a4ada502e862f1ec079c09f53c184cfe7dc2de10d94e` (muda em relação ao P0 porque o coletor inclui as DLLs da raiz, e o EEex adiciona 7)
- `modpack_hash`: `sha256:ff31e6bb43b5c3a9270d66b32e3ce2bacb6d40817bf1b43a2b4ef0641b7265fc` (25 arquivos em `override/`, `WeiDU.log`, marcadores EEex)
- Iguais antes e depois da sessão de jogo.

## Passos e resultados

| # | Passo | Comando / ação | Resultado | Verificação |
|---|---|---|---|---|
| 1 | Baixar e conferir o EEex | `gh release download v1.3.1 -R Bubb13/EEex -p eeex-v1.3.1.zip`; `shasum -a 256` no Mac e `Get-FileHash` na VM | hash confere com o digest do release | ferramenta |
| 2 | Cópia P1 | robocopy da instalação Steam | ok | ferramenta |
| 3 | 1ª tentativa de instalação | `Setup-EEex.exe --language 0 --force-install-list 0 1 --no-exit-pause --skip-at-view` | **travou**: sem `weidu.conf`, o WeiDU repete a pergunta do idioma do jogo e o log cresceu até 893 MB; processo encerrado, nada instalado | ferramenta |
| 4 | Instalação | idem + `--use-lang pt_BR` (idioma configurado no `Baldur.lua`), stdin vazio e limite de 5 min | `SUCCESSFULLY INSTALLED` #0 e #1; `WeiDU.log` registra os dois | ferramenta |
| 5 | Abrir pelo loader | duplo clique em `InfinityLoader.exe` da cópia P1 | `InfinityLoader.exe` (P1) iniciou `Baldur.exe` (P1) como filho 2 s depois | ferramenta (processos) |
| 6 | Injeção | módulos do processo `Baldur.exe` | `EEex.dll`, `InfinityLoaderDLL.dll`, `InfinityLoaderCommon.dll`, `InfinityLoaderUtil.dll`, `LuaBindings.dll`, `LuaBindingsCore.dll`, `LuaProvider.dll` carregados | ferramenta |
| 7 | Sem falhas | pasta `InfinityLoader_Crash` e `*.dmp` | ausentes | ferramenta |
| 8 | EEex ativo no jogo | menu de opções do EEex visível; carregar o save P0, jogar ~1 min | ok | relato |
| 9 | Save P1 | slot `INFINITY-P1-DESCARTAVEL` | gravado às 16:51:41; o save P0 ficou intocado (16:23:00) | ferramenta + relato |
| 10 | Encerramento | sair pelo menu | processos encerrados, sem crash | ferramenta |
| 11 | Regressão P0 | hash de todos os arquivos da cópia P0 vs. Steam | 2.324 arquivos, 0 diferenças | ferramenta |

## Achados

1. **O loader do EEex funciona sob emulação x64 do Windows on ARM** nesta build (2.7.3.0) e versão (v1.3.1). Isso não estava documentado pelo EEex, que só cita Windows nativo.
2. **O loader escreve na pasta do jogo na primeira execução:** `InfinityLoader.db`, `InfinityLoader.ini` e `EEex_scripts/extra_pattern_dbs/v2.7.3.0.db`. Esses arquivos não entram no `build_fingerprint` nem no `modpack_hash` atuais; avaliar no P2 se devem entrar como estado de runtime separado.
3. **WeiDU sem `weidu.conf` não termina em modo não interativo:** sempre passar `--use-lang`. Documentado em `tools/windows-lab/README.md`.
4. **Saves com EEex:** o release do EEex avisa que versões antigas do Near Infinity podem corromper saves com dados do EEex. Saves P1 não devem ser editados nem reaproveitados no P0.

## Limitações

- Não mede desempenho, estabilidade em sessões longas nem combate sob emulação.
- Nenhuma API do EEex foi chamada pelo Infinity AI; P2 (bridge read-only allowlisted) continua NÃO EXECUTADO.
- Nenhum teste multiplayer (P4).

## O que não foi publicado

Manifestos brutos, saves, arquivos do jogo e do EEex ficam fora do repositório; só hashes, versões e comandos acima.
