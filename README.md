# RobloxDB V2.0 — Interactive Profile Workspace

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
| `/open` | Abrir ficha HTML com avatar, capas de jogos e imagens dos itens equipados |
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
