# RobloxDB CLI V0.3 — Interface interativa

CLI para pesquisar informações **públicas** de perfis Roblox, com uma interface de terminal inspirada em ferramentas como Codex e Claude Code. Nenhuma senha, e-mail, cookie ou sessão é solicitado.

## Instalar / atualizar (Windows PowerShell ou CMD)

Requer Python 3.10+.

```powershell
py -m pip install --user --upgrade --force-reinstall https://github.com/raphaelsancho21-byte/Roblox-Profile-Database/archive/refs/heads/main.zip
```

Depois execute:

```powershell
robloxdb
```

Se `robloxdb` não for reconhecido, descubra o executável e rode diretamente pelo PowerShell:

```powershell
$script = py -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
& "$script\robloxdb.exe"
```

Para usar `robloxdb` sem caminho no PowerShell atual:

```powershell
$env:Path += ";$script"
robloxdb
```

## Comandos da interface

- Digite um username (ex.: `4lurcx`) ou UserId (ex.: `1`) para consultar.
- `/search nome` — outra consulta.
- `/open` — abrir a ficha HTML da última conta pesquisada.
- `/profile` — abrir o perfil no site do Roblox.
- `/json` — exibir caminho para o JSON gerado.
- `/clear` — limpar terminal.
- `/help` — ver ajuda.
- `/exit` — sair.

Também é possível iniciar já com uma pesquisa:

```powershell
robloxdb 4lurcx
```

Modo clássico sem interface (exportação direta):

```powershell
robloxdb --terminal 1
robloxdb --no-open 1
```

## Armazenamento

Dados JSON: `%USERPROFILE%\.robloxdb\profiles\USER_ID.json`  
Fichas HTML: `%USERPROFILE%\.robloxdb\cards\USER_ID.html`

## Dados consultados

Nome, DisplayName, UserId, descrição, data de criação, contagem de amigos/seguidores/seguindo, jogos favoritos e criados, IDs de itens equipados, visibilidade do inventário e usernames antigos, apenas quando as APIs públicas permitirem. A coleta de jogos consulta até 50 resultados por categoria; este número **não** representa necessariamente o total. Campos indisponíveis são mostrados como tal.

Algumas APIs podem mudar, limitar requisições ou exigir autenticação; nenhum bloqueio de privacidade é contornado. A interface Rich é instalada automaticamente pelo pip.

## Workflow no GitHub

A aba Actions inclui o workflow **Atualizar perfil Roblox** para consultar um UserId específico e salvar o JSON no repositório.

Este projeto não é afiliado à Roblox Corporation. Use-o de forma responsável, sem criar varreduras massivas ou perfis invasivos. Licença MIT.
