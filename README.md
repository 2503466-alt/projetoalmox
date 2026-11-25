# Almoxarifado Fácil — Python

Sistema web acadêmico feito com Python, Flask, SQLite, HTML e CSS.

## Recursos
- Cadastro e pesquisa de produtos.
- Estoque inicial e estoque mínimo.
- Entradas e saídas de materiais.
- Bloqueio de saída maior que o saldo disponível.
- Alerta visual de estoque baixo.
- Histórico das movimentações.
- Exportação do estoque em CSV, compatível com Excel.

## Executar localmente
1. Instale Python 3.10 ou superior.
2. Abra o terminal nesta pasta.
3. Execute `pip install -r requirements.txt`.
4. Execute `python app.py`.
5. Acesse `http://127.0.0.1:5000`.

O banco SQLite é criado automaticamente.

## Publicar na internet
O projeto está preparado para um host Python como Render. Envie os arquivos para um repositório GitHub e crie um serviço Web:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

O endereço público será gerado pela plataforma após o deploy. Não consigo publicar na sua conta sem acesso/autorização. Esta versão usa SQLite local; para hospedagem persistente, configure disco persistente ou PostgreSQL. Troque `app.secret_key` antes de publicar.

## Linguagens
- Python: lógica, validações e movimentações.
- Flask: servidor web e rotas.
- SQLite: banco de dados.
- HTML: estrutura das páginas.
- CSS: aparência e responsividade.
- Jinja2: exibição dos dados nas páginas.
