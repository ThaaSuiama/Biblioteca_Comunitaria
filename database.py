import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(override=True)


def conectar():
    banco = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_disabled=False
    )
    return banco


conexao = conectar()

print("Conexão com o banco realizada com sucesso!")

conexao.close()