from flask import Flask, render_template, request, redirect, url_for
from database import conectar

app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/livros", methods=["GET", "POST"])
def livros():

    if request.method == "POST":

        titulo = request.form["titulo"]
        autor = request.form["autor"]
        editora = request.form["editora"]
        ano_publicacao = request.form["ano_publicacao"]
        categoria = request.form["categoria"]
        isbn = request.form["isbn"]
        quantidade = request.form["quantidade"]

        banco = conectar()
        cursor = banco.cursor()

        sql = """
            INSERT INTO livro
            (titulo, autor, editora, ano_publicacao, categoria, isbn, quantidade)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            titulo,
            autor,
            editora,
            ano_publicacao,
            categoria,
            isbn,
            quantidade
        )

        cursor.execute(sql, valores)
        banco.commit()

        cursor.close()
        banco.close()

        return redirect(url_for("livros"))

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute("SELECT * FROM livro")
    livros = cursor.fetchall()

    cursor.close()
    banco.close()

    return render_template("livros.html", livros=livros)

@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]

        banco = conectar()
        cursor = banco.cursor()

        sql = """
            INSERT INTO usuario
            (nome, email, telefone)
            VALUES (%s, %s, %s)
        """

        valores = (
            nome,
            email,
            telefone
        )

        cursor.execute(sql, valores)
        banco.commit()

        cursor.close()
        banco.close()

        return redirect(url_for("usuarios"))

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuario")
    usuarios = cursor.fetchall()

    cursor.close()
    banco.close()

    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/emprestimos", methods=["GET", "POST"])
def emprestimos():

    if request.method == "POST":

        id_usuario = request.form["id_usuario"]
        id_livro = request.form["id_livro"]
        data_emprestimo = request.form["data_emprestimo"]
        data_devolucao_prevista = request.form["data_devolucao_prevista"]

        banco = conectar()
        cursor = banco.cursor()

        cursor.execute(
            "SELECT quantidade FROM livro WHERE id_livro = %s",
            (id_livro,)
        )

        livro = cursor.fetchone()

        if livro[0] <= 0:
            cursor.close()
            banco.close()
            return "Este livro não possui exemplares disponíveis."


        sql = """
            INSERT INTO emprestimo
            (id_usuario, id_livro, data_emprestimo,
             data_devolucao_prevista, status)
            VALUES (%s, %s, %s, %s, %s)
        """

        valores = (
            id_usuario,
            id_livro,
            data_emprestimo,
            data_devolucao_prevista,
            "Emprestado"
        )

        cursor.execute(sql, valores)

        cursor.execute(
        "UPDATE livro SET quantidade = quantidade - 1 WHERE id_livro = %s",
        (id_livro,)
    )
        banco.commit()

        cursor.close()
        banco.close()

        return redirect(url_for("emprestimos"))

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuario")
    usuarios = cursor.fetchall()

    cursor.execute("SELECT * FROM livro")
    livros = cursor.fetchall()

    cursor.execute("""
    SELECT
        emprestimo.id_emprestimo,
        usuario.nome AS nome_usuario,
        livro.titulo AS titulo_livro,
        emprestimo.data_emprestimo,
        emprestimo.data_devolucao_prevista,
        emprestimo.data_devolucao,
        emprestimo.status
    FROM emprestimo
    INNER JOIN usuario
        ON emprestimo.id_usuario = usuario.id_usuario
    INNER JOIN livro
        ON emprestimo.id_livro = livro.id_livro
""")

    emprestimos = cursor.fetchall()

    cursor.close()
    banco.close()

    return render_template(
    "emprestimos.html",
    usuarios=usuarios,
    livros=livros,
    emprestimos=emprestimos
    )

@app.route("/devolver/<int:id>")
def devolver(id):

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute(
        """
        UPDATE emprestimo
        SET data_devolucao = CURDATE(),
            status = 'Devolvido'
        WHERE id_emprestimo = %s
        """,
        (id,)
    )

    cursor.execute(
        """
        UPDATE livro
        SET quantidade = quantidade + 1
        WHERE id_livro = (
            SELECT id_livro
            FROM emprestimo
            WHERE id_emprestimo = %s
        )
        """,
        (id,)
    )

    banco.commit()

    cursor.close()
    banco.close()

    return redirect(url_for("emprestimos"))

@app.route("/editar_usuario/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        telefone = request.form["telefone"]

        sql = """
            UPDATE usuario
            SET nome = %s,
                email = %s,
                telefone = %s
            WHERE id_usuario = %s
        """

        valores = (
            nome,
            email,
            telefone,
            id
        )

        cursor.execute(sql, valores)
        banco.commit()

        cursor.close()
        banco.close()

        return redirect(url_for("usuarios"))

    cursor.execute(
        "SELECT * FROM usuario WHERE id_usuario = %s",
        (id,)
    )

    usuario = cursor.fetchone()

    cursor.close()
    banco.close()

    return render_template("editar_usuario.html", usuario=usuario)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    if request.method == "POST":

        titulo = request.form["titulo"]
        autor = request.form["autor"]
        editora = request.form["editora"]
        ano_publicacao = request.form["ano_publicacao"]
        categoria = request.form["categoria"]
        isbn = request.form["isbn"]
        quantidade = request.form["quantidade"]

        sql = """
            UPDATE livro
            SET titulo = %s,
                autor = %s,
                editora = %s,
                ano_publicacao = %s,
                categoria = %s,
                isbn = %s,
                quantidade = %s
            WHERE id_livro = %s
        """

        valores = (
            titulo,
            autor,
            editora,
            ano_publicacao,
            categoria,
            isbn,
            quantidade,
            id
        )

        cursor.execute(sql, valores)
        banco.commit()

        cursor.close()
        banco.close()

        return redirect(url_for("livros"))

    cursor.execute(
        "SELECT * FROM livro WHERE id_livro = %s",
        (id,)
    )

    livro = cursor.fetchone()

    cursor.close()
    banco.close()

    return render_template("editar.html", livro=livro)

@app.route("/excluir/<int:id>")
def excluir(id):

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute(
        "DELETE FROM livro WHERE id_livro = %s",
        (id,)
    )

    banco.commit()

    cursor.close()
    banco.close()

    return redirect(url_for("livros"))

@app.route("/excluir_usuario/<int:id>")
def excluir_usuario(id):

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute(
        "DELETE FROM usuario WHERE id_usuario = %s",
        (id,)
    )

    banco.commit()

    cursor.close()
    banco.close()

    return redirect(url_for("usuarios"))

if __name__ == "__main__":
    app.run(debug=False)