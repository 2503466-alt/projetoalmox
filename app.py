from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3, csv, io
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mude-esta-chave-antes-de-publicar"
DB = Path(__file__).with_name("almoxarifado.db")

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS produtos(
        id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL, categoria TEXT DEFAULT '', unidade TEXT DEFAULT 'UN',
        quantidade INTEGER NOT NULL DEFAULT 0, minimo INTEGER NOT NULL DEFAULT 0)""")
        c.execute("""CREATE TABLE IF NOT EXISTS movimentos(
        id INTEGER PRIMARY KEY AUTOINCREMENT, produto_id INTEGER NOT NULL,
        tipo TEXT NOT NULL, quantidade INTEGER NOT NULL, observacao TEXT DEFAULT '',
        data TEXT NOT NULL, FOREIGN KEY(produto_id) REFERENCES produtos(id))""")

@app.route("/")
def home():
    with db() as c:
        nprod = c.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        nun = c.execute("SELECT COALESCE(SUM(quantidade),0) FROM produtos").fetchone()[0]
        baixo = c.execute("SELECT COUNT(*) FROM produtos WHERE quantidade<=minimo").fetchone()[0]
        produtos = c.execute("SELECT * FROM produtos ORDER BY nome LIMIT 10").fetchall()
        movs = c.execute("""SELECT m.*,p.nome produto FROM movimentos m
        JOIN produtos p ON p.id=m.produto_id ORDER BY m.id DESC LIMIT 6""").fetchall()
    return render_template("home.html", nprod=nprod, nun=nun, baixo=baixo, produtos=produtos, movs=movs)

@app.route("/produtos", methods=["GET","POST"])
def produtos():
    if request.method == "POST":
        try:
            vals = (request.form["codigo"].strip(), request.form["nome"].strip(),
                    request.form.get("categoria","").strip(), request.form.get("unidade","UN"),
                    int(request.form.get("quantidade",0)), int(request.form.get("minimo",0)))
            if not vals[0] or not vals[1] or vals[4] < 0 or vals[5] < 0: raise ValueError
            with db() as c:
                c.execute("INSERT INTO produtos(codigo,nome,categoria,unidade,quantidade,minimo) VALUES(?,?,?,?,?,?)", vals)
            flash("Produto cadastrado com sucesso!","ok")
        except sqlite3.IntegrityError:
            flash("Este código já está cadastrado.","err")
        except (ValueError, KeyError):
            flash("Confira os campos e as quantidades informadas.","err")
        return redirect(url_for("produtos"))
    q = request.args.get("q","").strip()
    with db() as c:
        ps = c.execute("""SELECT * FROM produtos WHERE codigo LIKE ? OR nome LIKE ? OR categoria LIKE ? ORDER BY nome""",
                       (f"%{q}%",f"%{q}%",f"%{q}%")).fetchall()
    return render_template("produtos.html", produtos=ps, q=q)

@app.route("/movimentos", methods=["GET","POST"])
def movimentos():
    if request.method == "POST":
        try:
            pid, tipo, qtd = int(request.form["produto_id"]), request.form["tipo"], int(request.form["quantidade"])
            obs = request.form.get("observacao","").strip()
            if tipo not in ("Entrada","Saída") or qtd <= 0: raise ValueError
            with db() as c:
                p = c.execute("SELECT * FROM produtos WHERE id=?", (pid,)).fetchone()
                if p is None: raise ValueError
                saldo = p["quantidade"] + qtd if tipo == "Entrada" else p["quantidade"] - qtd
                if saldo < 0:
                    flash("Saldo insuficiente: a saída não foi registrada.","err")
                    return redirect(url_for("movimentos"))
                c.execute("UPDATE produtos SET quantidade=? WHERE id=?", (saldo,pid))
                c.execute("INSERT INTO movimentos(produto_id,tipo,quantidade,observacao,data) VALUES(?,?,?,?,?)",
                          (pid,tipo,qtd,obs,datetime.now().strftime("%d/%m/%Y %H:%M")))
            flash(f"{tipo} registrada com sucesso!","ok")
        except (ValueError,KeyError):
            flash("Preencha os dados corretamente.","err")
        return redirect(url_for("movimentos"))
    with db() as c:
        ps = c.execute("SELECT * FROM produtos ORDER BY nome").fetchall()
        hs = c.execute("""SELECT m.*,p.codigo,p.nome produto FROM movimentos m
        JOIN produtos p ON p.id=m.produto_id ORDER BY m.id DESC LIMIT 100""").fetchall()
    return render_template("movimentos.html", produtos=ps, historico=hs)

@app.route("/excluir/<int:pid>", methods=["POST"])
def excluir(pid):
    with db() as c:
        count = c.execute("SELECT COUNT(*) FROM movimentos WHERE produto_id=?", (pid,)).fetchone()[0]
        if count: flash("Produto com histórico de movimentações não pode ser excluído.","err")
        else:
            c.execute("DELETE FROM produtos WHERE id=?", (pid,))
            flash("Produto excluído.","ok")
    return redirect(url_for("produtos"))

@app.route("/estoque.csv")
def exportar():
    with db() as c:
        rows = c.execute("SELECT codigo,nome,categoria,unidade,quantidade,minimo FROM produtos ORDER BY nome").fetchall()
    out=io.StringIO(); w=csv.writer(out,delimiter=";")
    w.writerow(["Código","Produto","Categoria","Unidade","Saldo","Estoque mínimo"])
    for r in rows: w.writerow(list(r))
    return Response("\\ufeff"+out.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition":"attachment; filename=relatorio_estoque.csv"})

init_db()
if __name__ == "__main__":
    app.run(debug=True)
