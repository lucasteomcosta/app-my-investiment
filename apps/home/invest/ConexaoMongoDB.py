import pymongo

class ConexaoMongoDB:
    def __init__(self):
        self.nome_banco = 'investment'
        self.cliente = None

    def conectar(self):
        try:
            #Cria uma conexão com o MongoDB
            self.cliente = pymongo.MongoClient('mongodb+srv://admin:hHsd3LJ5sqM0aWNL@cluster0.bgsphsj.mongodb.net/?retryWrites=true&w=majority')

           # Seleciona ou cria um banco de dados
            banco_de_dados = self.cliente[self.nome_banco]

            # Retorna a conexão e o banco de dados
            return self.cliente, banco_de_dados
        except Exception as e:
            print(f"Erro ao conectar ao MongoDB: {e}")
            return None, None

    def desconectar(self):
        if self.cliente:
            self.cliente.close()
            print("Conexão com o MongoDB fechada.")