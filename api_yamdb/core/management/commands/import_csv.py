from django.core.management.base import BaseCommand
import sqlite3
import pandas as pd
import os
import logging
from api_yamdb.settings import DICT_TABLE, CSV_DIR

FORMATTER = '%(asctime)s — %(levelname)s — %(message)s'

logging.basicConfig(
    level=logging.INFO,
    format=FORMATTER
)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        con = sqlite3.connect('db.sqlite3')
        for file_csv, table in DICT_TABLE.items():
            df = pd.read_csv(os.path.join(CSV_DIR, file_csv), delimiter=',')
            try:
                df.to_sql(table, con=con, if_exists='append', index=False)
                logging.info(f'Загружен файл {file_csv} в таблицу {table}')
            except sqlite3.IntegrityError as e:
                if 'not null' in e.args[0].lower():
                    logging.error(f'Данные содержат значения NULL {file_csv}')
                elif 'unique constraint' in e.args[0].lower():
                    logging.error('Вы пытаетесь загрузить данные с '
                                  f'одинаковыми ID в таблицу {table}. '
                                  'Убедитесь, что не произвели загрузку '
                                  'данных из файлов csc ранее.')
                else:
                    raise
        con.commit()
        con.close()
