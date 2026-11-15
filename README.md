# RobloxDB V0.5 — CLI + Profile Explorer + Join Player

Pesquise perfis públicos do Roblox no terminal com uma interface inspirada em Codex/Claude Code e abra uma ficha visual no navegador com **avatar, ícones de jogos favoritos/criados e imagens dos itens equipados**.

O projeto usa endpoints públicos do Roblox, sem senha, e-mail, cookies, sessões ou login.

## Instalar / atualizar no Windows

Requer Python 3.10+ (o Python 3.13 também é compatível).

```powershell
py -m pip install --user --upgrade --force-reinstall https://github.com/raphaelsancho21-byte/Roblox-Profile-Database/archive/refs/heads/main.zip
robloxdb
```

Se o PowerShell disser que `robloxdb` não existe no PATH:

```powershell
$script = py -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
& "$script\robloxdb.exe"
```

## Interface

Digite `4lurcx` ou outro username exato, ou o UserId numérico.

- `/search NOME` — consultar usuário
- `/open` — abrir dashboard HTML com imagens
- `/profile` — abrir perfil no Roblox
- `/join` — tentar entrar na partida da última conta consultada (permissão controlada pelo Roblox)
- `/json` — mostrar JSON coletado
- `/clear`, `/help`, `/exit` — comandos do CLI

```powershell
robloxdb 4lurcx
robloxdb --terminal 1
robloxdb --no-open 1
```

A pesquisa por username utiliza o endpoint exato `POST /v1/usernames/users`. Nomes de exibição não são usernames: consulte pelo UserId quando houver ambiguidades.

## Dados e imagens

A ficha HTML exibe foto do avatar, estatísticas, lista de jogos favoritos/criados com ícones e itens atualmente equipados com miniaturas, se disponíveis. Imagens são resolvidas pelos endpoints públicos de thumbnails Roblox. Itens mostram o ID (nomes de catálogo não são consultados nesta versão).

O HTML é gerado em `%USERPROFILE%\.robloxdb\cards\USER_ID.html`, e os dados em `%USERPROFILE%\.robloxdb\profiles\USER_ID.json`.

Alguns jogos, imagens ou itens podem não aparecer porque o perfil é privado, a API está indisponível ou o Roblox não gerou a miniatura. Não coletamos inventário privado ou catálogo completo.

## GitHub Actions

O workflow **Atualizar perfil Roblox** recebe um UserId e salva uma captura JSON da consulta pública no repositório.

Licença MIT. Não afiliado à Roblox Corporation. Não use para varreduras massivas de contas ou agregação invasiva de dados.


## Entrar na partida do usuário

Depois de consultar alguém, digite `/join` ou clique no botão **Entrar na partida** da ficha HTML. O sistema abre `roblox://userId=USER_ID` usando o aplicativo oficial. O Roblox decidirá se a entrada está autorizada. **Não há rastreamento de localização, descoberta de servidores ocultos ou contorno de configurações de privacidade.** Se o jogador estiver offline ou impedir entradas, não será possível ingressar. Links profundos legados podem não funcionar em todas as versões do Roblox.
