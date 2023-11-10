from datetime import datetime


class Carteira():
    def __init__(self, df):
        self.df = df
        self.data = datetime.now()

    def to_dict(self):
        # Retorna um dicionário com os campos e seus valores
        return {
            'df': self.df,
            'data': self.data
        }
