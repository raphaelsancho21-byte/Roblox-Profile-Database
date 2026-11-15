# Roblox Profile Database

Coletor de **informações públicas** de perfis Roblox em JSON. Sem senhas, e-mails, cookies, sessões ou scraping de páginas privadas.

## Dados

- Perfil: `id`, `name`, `displayName`, descrição, criação e badge (quando disponíveis).
- Contagens: amigos, seguidores e seguindo.
- Jogos criados e jogos favoritos públicos (primeira página, máximo de 50).
- IDs de itens atualmente equipados, visibilidade do inventário e histórico público de usernames (quando disponibilizados).
- Timestamp de cada coleta. Valores indisponíveis ficam `null`, nunca são inventados.

> **Limitações:** As APIs e permissões do Roblox mudam. Algumas listas completas exigem autenticação ou não são públicas. Este projeto não contorna essas restrições. O catálogo completo de itens comprados não é coletado nesta versão. Contagens podem não estar disponíveis para todas as contas.

## Executar (Python 3.10+)

```bash
python src/main.py --username Roblox
# ou
python src/main.py --id 1
```

Os resultados vão para `data/profiles/USER_ID.json`. Não há bibliotecas a instalar.

## GitHub Actions

Na aba **Actions**, execute **Atualizar perfil Roblox**, informando um UserId. O workflow publica o JSON diretamente na branch padrão quando tiver permissão de escrita.

## Uso responsável

Consulte apenas perfis específicos, com propósito legítimo. Respeite restrições de privacidade, limites de requisição e pedidos apropriados de remoção. Evite varrer usuários em massa, cruzar dados para identificar pessoas ou publicar perfis de menores em escala. Este projeto não é afiliado à Roblox Corporation.

## API oficial

Documentação: https://create.roblox.com/docs/cloud/reference/features/users

Licença: MIT.
