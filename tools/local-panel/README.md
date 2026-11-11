# Infinity AI — Painel local de desenvolvimento

Interface de operações do Infinity AI no navegador, com **Python 3.11+ e biblioteca padrão**. Não instala Node.js, Flask, Docker nem serviços externos.

## Primeira execução no macOS

Na pasta do repositório:

~~~bash
python3 tools/local-panel/server.py
~~~

O navegador abre automaticamente em **http://127.0.0.1:8766**. Deixe a janela do Terminal que iniciou o painel aberta. Depois disso, os comandos comuns podem ser disparados pelos botões.

Opcional: para abrir com duplo clique pelo Finder, faça uma única vez:

~~~bash
chmod +x INICIAR_PAINEL.command
~~~

Depois use o arquivo INICIAR_PAINEL.command na raiz do repositório. Para usar outra porta: python3 tools/local-panel/server.py --port 8767.

## Recursos

| Área | Função |
| --- | --- |
| Repositório | Estado local, branch, commit, alterações locais, busca de atualizações |
| Branches | Trocar de branch remota conhecida, criar rastreamento local |
| Atualizar | Pull fast-forward only; sincronização = fetch + pull |
| Ambiente | Criar .venv se necessário e instalar requirements-test.txt no ambiente isolado |
| Testes | Identidade, suíte Python, cronologia, compilação, ADRs e arquivos públicos |
| Validação completa | Executar todas as verificações em sequência, parando na primeira falha |
| Laboratório | Iniciar/parar dialogue_service.py em campanha lab-* e banco isolado |
| Pin | Executar pin_canon_pack.py após observação com tempo válido, com confirmação |
| Logs | Acompanhar a saída dos testes e do serviço e copiar logs |

## Configurar o laboratório

Em **Laboratório**:

1. Informe um nome de campanha começando com lab- (por padrão, lab-s1f).
2. Informe o caminho absoluto do manifesto P2 JSON da instalação do jogo.
3. Informe host/IP da VM, usuário e, se necessário, o caminho da chave SSH. Alternativamente, se o Terminal que inicia o painel já possui INFINITY_LAB_SSH, essa configuração será herdada.
4. Escolha o modelo local Ollama (padrão: qwen3:8b) e clique em **Salvar configuração**.
5. Com o BG2:EE no save de laboratório, clique **Iniciar serviço de diálogo**.
6. Quando o console registrar uma observação válida com tempo de jogo, clique **Registrar pin canônico** e confirme; observe o resultado NOT_PINNED -> MATCH.
7. Faça as perguntas no jogo e acompanhe os logs pela aba **BG2:EE / Serviço**.

A campanha lab-s1f usa o banco ~/.infinity-ai/campaigns/lab-s1f.sqlite3; o painel nunca seleciona lab-s1 ou lab-s1e automaticamente. O token do overlay é preservado entre reinicializações do serviço, quando já existe um arquivo de configuração gerado. Não use duas instâncias do serviço na mesma porta.

## Arquivos locais e segurança

- Configurações: ~/.infinity-ai/local-panel/config.json (permissão 0600).
- Logs: ~/.infinity-ai/local-panel/logs/ (fora do repositório).
- Token do overlay e configuração de acesso: ~/.infinity-ai/local-panel/lab-NOME-overlay.json.
- Banco de cada campanha: ~/.infinity-ai/campaigns/lab-NOME.sqlite3.

O servidor **só escuta 127.0.0.1**, exige token de sessão para a API, rejeita Host/Origin de terceiros, não habilita CORS, não aceita comandos de Terminal arbitrários nem usa shell=True. Toda execução é limitada a ações permitidas, com um único job por vez e logs próprios. Operações Git que modificam a cópia são bloqueadas quando há alterações locais ou serviço de diálogo em execução. O painel nunca executa push, merge, reset, rebase, checkout forçado ou exclusão de arquivos.

O pin e o serviço mexem **somente no banco de laboratório e nas rotas já previstas pelos scripts existentes**. Continuam válidas as restrições dos adaptadores EEex; o painel não autoriza alterar saves reais. A conexão SSH usa chave local; seu conteúdo não é enviado ao navegador.

**Atenção:** ferramenta local de desenvolvimento, não um painel hospedável na internet. Não faça proxy, redirecionamento de porta ou exposição pela LAN. Os registros de serviço podem conter respostas e nomes de NPCs; não publique a pasta de logs.

## Solução de problemas

- **Porta 8766 ocupada:** inicie com --port 8767.
- **Python/venv ausente:** o botão **Preparar ambiente** instala as dependências de testes.
- **Git diz que há mudanças locais:** consulte o status e trate as alterações manualmente; o painel não descarta nada.
- **Não há observação para o pin:** carregue um save válido, inicie o serviço e aguarde um registro no console.
- **SSH indisponível:** confira a VM e a configuração SSH antes de iniciar.
- **Manifesto não corresponde à instalação:** não avance com o teste; revise a cópia de jogo e seu inventário.
- **Serviço encerrado:** examine a aba de logs do laboratório.
- **Interromper o painel:** pressione Ctrl+C no Terminal que iniciou o servidor; o serviço gerenciado também será interrompido.

O código dos botões está na lista de ações permitidas de tools/local-panel/server.py e a interface está em tools/local-panel/static/. Testes de segurança: tests/test_local_panel.py.
