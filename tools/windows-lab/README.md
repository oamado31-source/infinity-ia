# Windows lab — roteiro do gate P0

Ferramentas para coletar evidência no Windows sem escrever na instalação do jogo. Contexto: ADR-0005, ADR-0108, SPEC-001 e, para Windows on ARM em VM, CR-2026-001.

## 1. Preparar a cópia dedicada

1. Instale o BG2:EE da sua conta legítima (Steam, GOG ou Beamdog) **sem mods**.
2. Faça uma cópia dedicada da pasta do jogo para os testes (ADR-0005 item 5); nunca use a instalação ou os saves do dia a dia.
3. Não instale EEex ainda: o P0 é o jogo limpo.

## 2. Coletar o manifesto (somente leitura)

No PowerShell do Windows, na pasta deste arquivo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File p0-collect-manifest.ps1 -GameRoot 'C:\InfinityLab\BG2EE' -OutFile p0-manifest.json
```

Sem `-GameRoot`, o coletor procura instalações Steam/GOG/Beamdog e usa a primeira encontrada. Ele grava só o JSON, com caminhos relativos à raiz do jogo e sem usuário ou nome da máquina.

## 3. Avaliar

```bash
python scripts/p0_assess_manifest.py p0-manifest.json
```

`MANIFEST_OK` é condição necessária, não o P0. Achados `REVIEW` (VM, ARM64, override) devem constar no relatório; `BLOCK` impede seguir.

## 4. Teste base manual (completa o P0)

**Dependência de sistema:** o jogo precisa do runtime OpenAL. O Steam o instala na primeira vez que o jogo é aberto pela loja; abrindo direto pela cópia antes disso, o Windows acusa `OpenAL32.dll não foi encontrado`. O instalador vem com o jogo (`oalinst.exe`, assinado pela Creative Labs). Num PowerShell de administrador:

```powershell
Get-AuthenticodeSignature 'C:\InfinityLab\BG2EE-P0\oalinst.exe'   # Status deve ser Valid
Start-Process 'C:\InfinityLab\BG2EE-P0\oalinst.exe' -ArgumentList '/s' -Wait
```

Ele instala em `System32`/`SysWOW64`, fora da pasta do jogo, então o `build_fingerprint` não muda. Registre a versão instalada no relatório (no laboratório de 2026-11-08: 6.14.0357.24).

1. Abra o jogo pela cópia dedicada, inicie um jogo novo, ande até sair da primeira área.
2. Salve num slot com nome `INFINITY-P0-DESCARTAVEL`, feche e recarregue o save.
3. Registre: data, SHA do commit, `build_fingerprint`, `modpack_hash`, ambiente e resultado.

## 5. Gate P1 — loader EEex (cópia separada)

Nunca instale o EEex na cópia P0: crie outra cópia a partir da instalação limpa (ex.: `C:\InfinityLab\BG2EE-P1`).

1. Baixe o zip do release oficial (`https://github.com/Bubb13/EEex/releases`) e confira o sha256 com o digest publicado no release.
2. Extraia e copie `EEex\` e `Setup-EEex.exe` para a raiz da cópia P1 (os arquivos de macOS do zip não são necessários).
3. Instale o preset "Minimal" sem interação, na raiz da cópia. **Passe `--use-lang`** com o idioma do jogo (veja `Language` em `Documentos\Baldur's Gate II - Enhanced Edition\Baldur.lua`); sem `weidu.conf` o WeiDU repete a pergunta do idioma para sempre:

   ```powershell
   .\Setup-EEex.exe --use-lang pt_BR --language 0 --force-install-list 0 1 --no-exit-pause --skip-at-view --log setup-EEex.debug
   ```

4. Abra sempre pelo `InfinityLoader.exe` (abrir pelo `Baldur.exe` com EEex instalado trava o jogo). Se não abrir, atualize o Visual C++ Redistributable x64.
5. Confirme que `EEex.dll` e `InfinityLoaderDLL.dll` estão carregados no processo `Baldur.exe` e que não surgiu `InfinityLoader_Crash\`. Saves feitos com EEex vão em slot próprio (`INFINITY-P1-DESCARTAVEL`), nunca por cima do save P0.

## 6. Gate P2 — bridge read-only pelo log do EEex

Na cópia P1 (com EEex), instale o probe conforme `tools/eeex-probe/README.md` e colete o manifesto de referência (ele passa a incluir os 2 arquivos do probe no `modpack_hash`). Com a VM acessível por SSH:

```bash
export INFINITY_LAB_SSH='ssh -i ~/.ssh/<chave> -o IdentitiesOnly=yes -o BatchMode=yes -l "<usuario>" <ip-da-vm>'
python tools/windows-lab/p2_lab_session.py --pinned-manifest <p2-manifest.json> --out <sessao.jsonl> --duration 600
```

Roteiro no jogo: menu principal → carregar save → (trocar de área) → salvar em `INFINITY-P2-DESCARTAVEL` → recarregar → fechar. Esperado: `UNKNOWN` no menu, `OBSERVED` no mapa, `EPOCH_MISMATCH` no reload seguido de reconexão, `ADAPTER_UNAVAILABLE`/`UNKNOWN` com o jogo fechado; requisições de escrita, campo fora da allowlist e ACL errada sempre recusadas. O relógio da VM é local (UTC−3 no laboratório); os envelopes usam UTC.

## 7. S1a — persistência e memória de companheiros (single player)

Com o probe atualizado (3 campos) na cópia com EEex e o manifesto de referência coletado:

```bash
export INFINITY_LAB_SSH='ssh -i ~/.ssh/<chave> -o IdentitiesOnly=yes -o BatchMode=yes -l "<usuario>" <ip-da-vm>'
python tools/windows-lab/s1_record_session.py --pinned-manifest <manifesto.json> --duration 900
```

O banco fica em `~/.infinity-ai/campaigns/lab-s1.sqlite3` (fora do repo) e o backup em `~/.infinity-ai/campaigns/backups/`. Rodar de novo continua o mesmo banco sem duplicar. Para provar a divisão de ramos é preciso **mudar algo depois do save** (área ou grupo) e então recarregar o save; um reload sem mudança gravada depois do save continua no mesmo ramo, por projeto.

## 8. S1b — diálogo por texto com overlay (single player)

No Mac (Ollama com `qwen3:8b` rodando):

```bash
export INFINITY_LAB_SSH='ssh -i ~/.ssh/<chave> -o IdentitiesOnly=yes -o BatchMode=yes -l "<usuario>" <ip-da-vm>'
python tools/windows-lab/dialogue_service.py --pinned-manifest <manifesto.json> --config-out <fora-do-repo>/overlay.json
```

Copie `overlay.json` (URL + token) para `%LOCALAPPDATA%\InfinityAI\overlay.json` na VM e `tools/windows-overlay/` para a VM; abra `Start-InfinityOverlay.cmd` na sessão do jogador. Programas com janela iniciados pelo SSH não aparecem na área de trabalho; para abrir pelo SSH, use uma tarefa agendada de uso único com `LogonType Interactive` e apague-a em seguida. **Abra o jogo uma vez só**: duas instâncias disputam o `InfinityLoader.log` e a segunda não escreve nele. `--reuse-token` mantém o overlay funcionando após reiniciar o serviço; `--ollama-url` permite simular o modelo fora do ar sem parar o Ollama.


## Anexo — ADR-0119: conhecimento relacional (S1f, isolado)

A validação desta mudança usa a campanha **`lab-s1f`** e um banco próprio, sem reutilizar registros da `lab-s1e` nem o banco padrão `lab-s1.sqlite3`. Execute os comandos na máquina que mantém o banco do laboratório, a partir da raiz do repositório:

```bash
python tools/windows-lab/pin_canon_pack.py --campaign lab-s1f --db ~/.infinity-ai/campaigns/lab-s1f.sqlite3 --year 1369
python tools/windows-lab/dialogue_service.py --pinned-manifest <manifesto.json> --config-out <fora-do-repo>/overlay-s1f.json --campaign lab-s1f --world-seed lab-s1f --db ~/.infinity-ai/campaigns/lab-s1f.sqlite3
```

O primeiro comando cria/atualiza explicitamente o pin do pacote canônico 1369 DR no ramo ativo de `lab-s1f`; não altera o pin de outras campanhas. O segundo serviço deve usar exatamente a mesma campanha e o mesmo banco. Se o banco S1f já existir em outro caminho, passe esse caminho nos dois comandos.

Roteiro mínimo:
1. Bernard, com afiliação `place:copper-coronet:STAFF`: deve reconhecer Lehtinan como proprietário e explicar sua própria função operacional.
2. Um NPC sem afiliação, mesmo presente em AR0406: deve conhecer a propriedade pública local, mas não a relação operacional restrita.
3. Um frequentador com curadoria explícita `place:copper-coronet:REGULAR`: deve receber a relação operacional restrita.
4. Se houver ouvintes na party, confirmar que INQUIRY pode propagar a relação pública efetivamente dita, mas nunca a relação RESTRICTED.

Registre o SHA do commit, a revisão do pacote, o ramo/campanha e os resultados. Não suba o banco, saves, inventário local do jogo ou arquivos extraídos.

## 9. Onde guardar a evidência

O manifesto bruto fica fora do repositório (contém hashes da sua instalação, nada sensível, mas também nada que precise ser público). No relatório da PR, cite apenas fingerprint, modpack hash, versões, ambiente e resultado. **Nunca** suba saves, `chitin.key`, `.tlk`, `.bif` ou capturas com conteúdo do jogo.

## Anexo — S1c: inventário de áreas da instalação (SPEC-005)

```bash
export INFINITY_LAB_SSH='ssh -i ~/.ssh/<chave> -o IdentitiesOnly=yes -o BatchMode=yes -l "<usuario>" <ip-da-vm>'
python tools/windows-lab/build_area_inventory.py --language pt_BR
```

Lê fatias de `chitin.key`, do BIF com o mapa-múndi e do `dialog.tlk` da cópia na VM para a memória e grava só o inventário derivado em `~/.infinity-ai/knowledge/install-<fingerprint>/` (fora do repo). O serviço de diálogo carrega esses nomes ao iniciar (`--language`).

## Anexo — SPEC-006: diálogo de primeiro contato com pessoas comuns (protótipo)

A API de laboratório agora reconhece `POST /v1/encounter-dialogue` com `Authorization: Bearer <token>` e JSON `{"contact_event_id":"ev-...", "text":"Bom dia"}`. O servidor só aceita **evento já gravado** do tipo `NpcDialogueStarted`, visível no ramo atual e com cena coincidente com a área observada. Não há rota para fabricar perfis/observações pelo overlay. Os campos de ator, papel social, identidade e prova precisam vir de um **adaptador de jogo confiável**, ainda não implementado.

Este endpoint é infraestrutura experimental, **não habilita cliques em NPCs comuns do BG2:EE**. O overlay atual continua limitado aos companheiros. O probe EEex atual vê área, tempo e party: primeiro é necessário verificar tecnicamente a observação do clique em qualquer personagem (inclusive figurantes sem diálogo nativo), respeitando diálogos roteirizados. Sem observação o serviço bloqueia, e NPCs canônicos não são randomizados. A semente de criação pode ser fixada por `--world-seed`, que deve permanecer estável por campanha; perfis verificados já persistidos não são regenerados.

## Anexo — ADR-0116: perguntar a habitantes na caixa do jogo

1. Inventário de habitantes (fora do repositório): `python tools/windows-lab/build_area_inventory.py --residents`.
2. Copiar a caixa para a VM: `python tools/windows-lab/talk_poc.py --deploy` e reabrir o jogo.
3. Serviço numa campanha nova: `dialogue_service.py ... --campaign lab-s1e --db ~/.infinity-ai/campaigns/lab-s1e.sqlite3 [--world-seed <semente>]`. Depois, pin: `pin_canon_pack.py --campaign lab-s1e --db ...`.
4. No jogo, F9 sobre a pessoa. O console do serviço mostra `caixa pedido=... perfil=... status=... entradas=[...] ouvintes=[...]` e, quando houver, `conhecimento comum adquirido ... base=INQUIRY`.
