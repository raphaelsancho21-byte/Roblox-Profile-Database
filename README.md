# Roblox Profile Database — CLI V0.2

Pesquise informações **públicas** de contas Roblox pelo Windows CMD e abra uma ficha visual no navegador, sem senhas, e-mails, cookies ou login.

## Instalação no Windows

Requer Python 3.10 ou superior. Verifique no CMD com `py --version`.

Cole no CMD:

```cmd
py -m pip install --user https://github.com/raphaelsancho21-byte/Roblox-Profile-Database/archive/refs/heads/main.zip
```

Feche e reabra o CMD. Pesquise:

```cmd
robloxdb Roblox
robloxdb 1
robloxdb
robloxdb --terminal Roblox
robloxdb --no-open 1
```

Se o Windows não reconhecer `robloxdb`, execute sem depender do PATH:

```cmd
py -m pip show roblox-profile-database-cli
```

O instalador pode informar a pasta `Scripts` que precisa estar no PATH. Como alternativa, execute o arquivo `robloxdb_cli.py` diretamente a partir de uma cópia do repositório: `py robloxdb_cli.py 1`.

## Onde ficam os dados?

- JSON: `%USERPROFILE%\.robloxdb\profiles\USER_ID.json`
- Ficha HTML: `%USERPROFILE%\.robloxdb\cards\USER_ID.html`

As fichas HTML são locais; imagens de avatar exigem internet.

## Dados

Nome, DisplayName, UserId, descrição, data de criação, contagens de amigos/seguidores/seguindo, jogos favoritos e criados públicos, IDs de itens equipados, visibilidade do inventário, nomes anteriores públicos quando disponíveis e data de consulta. Listas de jogos são limitadas a 50 itens na versão inicial; contagens e dados podem vir indisponíveis em função de alterações nas APIs ou privacidade.

## Coletor standalone

```cmd
py src/main.py --username Roblox
py src/main.py --id 1
```

## GitHub Actions

Na aba Actions, execute **Atualizar perfil Roblox**, com um UserId. A automação gera JSON público na pasta `data/profiles`.

**Privacidade:** nunca contornar bloqueios de API, não coletar dados privados nem criar bancos massivos de usuários. Não afiliado à Roblox Corporation.

Licença: MIT. Sem dependências Python em tempo de execução.
