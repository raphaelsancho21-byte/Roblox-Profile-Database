# RobloxDB V2.4.1 — Interactive Profile Workspace

Interface interativa estilo Codex/Claude Code com animação de entrada, pesquisa de perfis Roblox e ficha visual em HTML. Inclui navegação por servidores públicos, favoritos, gerenciador de ocorrências locais, histórico, comparação, exportações e diagnóstico de API.

> O RobloxDB **não rastreia usuários por servidores**, não revela dados privados e não contorna as configurações de privacidade. Listagens de servidores não mostram identidade dos participantes. A entrada em partidas está sujeita às permissões oficiais do Roblox.

## Instalar no Windows (Python 3.10+)

```powershell
py -m pip install --user --upgrade --force-reinstall https://github.com/raphaelsancho21-byte/Roblox-Profile-Database/archive/refs/heads/main.zip
robloxdb
```

Se `robloxdb` não for reconhecido:

```powershell
$script = py -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
& "$script\robloxdb.exe"
```

Para adicionar ao PATH só nesta sessão: `$env:Path += ";$script"`.

## Comandos

| Comando | Ação |
|---|---|
| `4lurcx` ou `/user 4lurcx` | Consultar usuário pelo username exato (não DisplayName) |
| `/user 1` | Consultar pelo UserId |
| `/game 4924922222` | Consultar jogo pelo **PlaceId real**, URL ou `u:UniverseId` |
| `/servers 2` | Mostrar até duas páginas de servidores públicos |
| `/available` | Mostrar apenas servidores com vaga (da consulta pública) |
| `/open` | Abrir ficha HTML com avatar, capas de jogos, imagens de itens e indicador de presença |\n| `/presence` | Atualizar presença do último usuário consultado |
| `/join` | Solicitar entrada pelo Roblox, sujeito à privacidade |
| `/profile` | Abrir página oficial do perfil |
| `/save user` | Favoritar último usuário |
| `/save game` | Favoritar último jogo |
| `/save server` | Favoritar o primeiro servidor retornado |
| `/favorites` | Listar favoritos locais |
| `/unsave user 1` | Remover um favorito |
| `/case` | Criar ocorrência manual (username, jogo, descrição e evidência) |
| `/cases` | Listar ocorrências |
| `/close ID` | Encerrar uma ocorrência |
| `/history` | Histórico local |
| `/compare USER1 USER2` | Comparar dois perfis |
| `/export json` | Exportar JSON do último perfil |
| `/export csv` | Exportar CSV do último perfil |
| `/export html` | Abrir ficha HTML animada |
| `/export pdf` | Gerar relatório PDF |
| `/diagnose` | Diagnóstico de APIs |
| `/animations off` | Desligar animação de abertura |
| `/animations on` | Ligar animação de abertura |
| `/clear`, `/help`, `/exit` | Navegação |

O menu mostra a listagem completa com `/help`.

## Interface HTML V2

A ficha visual tem tema escuro, animação de aparição, navegação por seções, avatar, estatísticas, miniaturas de jogos favoritos/criados e itens equipados quando públicos. Para usuários sem itens ou jogos públicos, informa indisponibilidade; não inventa dados.

## O que precisa saber

- **Pesquisa de jogos por nome** ainda depende de endpoints de busca que mudam ou exigem autenticação. Atualmente `/game` recebe PlaceId ou URL de jogo.
- **Server Explorer** lista informações públicas: ocupação, capacidade, ping, FPS e ID de instância (quando oferecido). Não há varredura de jogadores por servidor.
- **Server favorites** guardam o ID de uma instância pública que pode expirar.
- **Join player** usa a tentativa de entrada do cliente oficial, nunca promete sucesso ou servidor exato.
- **Inventário**: miniaturas dos itens equipados; itens não públicos e inventário completo não são acessados.
- **PDF** usa reportlab, instalado automaticamente, e não depende de Word.
- **Histórico e ocorrências** ficam armazenados localmente, não sincronizados em servidores externos.
- A busca exata usa POST usernames/users e pode falhar em bloqueios de rede ou indisponibilidade temporária da API.

## Dados locais

`%USERPROFILE%\.robloxdb\`
- `profiles\`: capturas JSON
- `cards\`: fichas HTML
- `reports\`: relatórios CSV/PDF
- `cases\`: ocorrências
- `history.json`: consultas
- `favorites.json`: favoritos
- `settings.json`: preferências

## Executar testes locais

```powershell
py -m compileall -q .
```

Licença MIT. Projeto independente e não afiliado à Roblox Corporation. Use de forma legítima, com respeito à privacidade e aos limites de requisições.


## Presence — status público

RobloxDB consulta `POST https://presence.roblox.com/v1/presence/users` para um único usuário pesquisado. Apresenta os estados **Offline (0)**, **Online (1)**, **Jogando (2)**, **No Studio (3)** ou **Indisponível (4, erros e restrições)**. A consulta é pontual, não monitora o usuário continuamente e não tenta identificar o jogo ou servidor quando ocultos. A privacidade pode fazer a API mostrar uma pessoa como offline mesmo que ela esteja ativa. O comando `/presence` permite uma atualização manual. A ficha HTML é regenerada ao usar `/open`.


## Account Manager (cadastro manual e recuperação)

Use `/accounts` no CLI. Selecione de 1 a 5 cadastros e escolha usernames aleatórios ou manuais. O programa abre a página oficial do Roblox, gera uma senha local opcional, mostrada uma única vez e nunca armazenada, e aguarda você concluir o cadastro. Caso não consiga abrir o site ou surja uma etapa que exige ação humana, escolha **tentar**, **manual** ou **pular**. Escolha **concluido** apenas quando tiver terminado o cadastro e conseguir entrar; a conclusão é confirmada manualmente e não verificada pelo software. O RobloxDB salva apenas usernames e estado local em `~/.robloxdb/account_manager.json`, nunca senhas. Use data de nascimento verdadeira. Não automatiza CAPTCHA, envio de cadastros ou criação em massa e não envia credenciais a webhooks do Discord.


## V2.2 — Preenchimento assistido e notificações seguras

O comando `/accounts` agora oferece as opções `preencher`, `tentar`, `manual`, `concluido` e `pular`.

- `preencher` tenta abrir **Chrome, Edge ou Brave** usando Playwright e completar **somente** username e senha sugeridos. É um preenchimento de melhor esforço: o Roblox pode alterar campos ou bloquear automação; não há garantia de funcionamento.
- **Data de nascimento verdadeira, CAPTCHA, verificações e envio do formulário continuam manuais**. O aplicativo não cria contas sozinho.
- `tentar` tenta reabrir o navegador e preencher novamente, `manual` permite completar diretamente na página oficial, `pular` mantém a conta pendente.
- `concluido` só marca uma conta como confirmada após sua confirmação explícita.
- O programa **não envia nem armazena senhas**. Guarde-as em um gerenciador de senhas pessoal; elas aparecem uma vez no terminal durante o assistente.

### Notificação opcional do Discord (sem senha)

**Revogue URLs de webhook publicadas em chats ou repositórios** e gere uma nova. No PowerShell atual, configure um webhook novo **sem incluí-lo no código público**:

```powershell
$env:ROBLOXDB_DISCORD_WEBHOOK = Read-Host "Cole o webhook NOVO do Discord"
robloxdb
```

A mensagem enviada só contém o username e a confirmação manual de cadastro. Nenhum token, senha, cookie ou data de nascimento é enviado. O webhook permanece apenas na variável do terminal atual.

Se Playwright não conseguir iniciar o browser, instale ou use Chrome, Edge ou Brave e finalize o cadastro manualmente. Não automatizamos soluções de CAPTCHA nem etapas de segurança.


### Correção: ordem dos campos no cadastro

O assistente solicita no terminal uma **data de nascimento verdadeira** em `DD/MM/AAAA`, válida, e tenta selecionar **mês, dia e ano primeiro** na página de cadastro do Roblox; somente depois preenche username e senha. A data não é salva no histórico e não é enviada ao webhook. Se os seletores da página mudarem, o aplicativo avisa e permite concluir manualmente. CAPTCHA, verificações e envio final permanecem sob controle do usuário.


## V2.3 — Atualizador e correção de preenchimento

Para atualizar sem colar o comando longo: `robloxdb --update`. O atualizador usa pip e baixa a branch main. Feche outras instâncias do RobloxDB e execute novamente após atualizar.

O assistente `/accounts` agora abre diretamente a página de cadastro `https://www.roblox.com/pt?p=reg`, aguarda o formulário e indica quais campos (mês, dia, ano, username e senha) foram preenchidos. Se o Roblox alterar o layout, bloquear a automação ou pedir login, conclua manualmente. CAPTCHA, verificações e envio final continuam sob controle do usuário. Não envie senhas a webhooks.


## V2.4 — Cadastros em janelas independentes

O comando `/accounts` prepara de 1 a 5 inscrições numa única execução. O programa solicita a **data de nascimento verdadeira** de cada conta e gera username e senha. Guarde as senhas antes de confirmar a abertura das janelas. O navegador usa **contextos isolados** para não compartilhar cookies entre contas; a interface pode criar janelas separadas em vez de abas da mesma sessão.

Cada formulário é aberto e preenchido (data primeiro, username e senha depois). Quando todos os cinco campos estão prontos e o botão de cadastro está habilitado, o assistente tenta **clicar uma única vez em Cadastrar**. O clique não garante criação: CAPTCHA, verificação adicional, limitação da plataforma e revisão final dependem do usuário. Nunca tenta forçar botões desabilitados, contornar desafios ou repetir cadastros indefinidamente.

As janelas permanecem abertas enquanto você verifica cada cadastro. No terminal, use `concluido` apenas depois de conseguir acessar a conta, `tentar` para preencher/enviar novamente somente quando solicitado por você, `manual` para terminar na janela aberta ou `pular` para deixar pendente.

**Não envia senhas ou datas de nascimento ao Discord.** Notificações opcionais de conclusão manual contêm apenas username. A confirmação do CLI não verifica independentemente a criação da conta.


## V2.4.1 — Correção de fluxo de CAPTCHA

O Account Manager não clica mais automaticamente em Cadastrar. Ele prepara o formulário e deixa o usuário enviar e resolver a verificação na página oficial. A opção `tentar` não recarrega automaticamente uma página que poderia conter um CAPTCHA em andamento. Isso evita invalidar acidentalmente a etapa atual, mas **não garante** que o Roblox aceitará o cadastro. Se o próprio site disser "Tente novamente" após completar um CAPTCHA, a validação está sob controle do Roblox; experimente realizar o cadastro manualmente em um navegador normal e consulte o suporte oficial se persistir.
