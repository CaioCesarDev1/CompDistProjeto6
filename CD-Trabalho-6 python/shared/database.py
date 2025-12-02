"""
Configuração do banco de dados PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from shared.models import Base
import os
from dotenv import load_dotenv
import urllib.parse
import sys

# Workaround para problema de encoding do psycopg2 no Windows
# Limpa variáveis de ambiente problemáticas antes de conectar
if sys.platform == 'win32':
    # Salva e limpa variáveis que podem causar problemas de encoding
    _env_backup = {}
    problematic_vars = ['PATH', 'TEMP', 'TMP', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA']
    for var in problematic_vars:
        if var in os.environ:
            try:
                # Tenta codificar/decodificar para verificar se está OK
                os.environ[var].encode('utf-8').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                # Se houver problema, salva e limpa temporariamente
                _env_backup[var] = os.environ[var]
                # Não remove, apenas garante que está em UTF-8
                try:
                    os.environ[var] = os.environ[var].encode('latin1').decode('utf-8', errors='ignore')
                except:
                    pass

load_dotenv()

# Configuração do banco de dados usando parâmetros separados
# Isso evita problemas de codificação com URLs
DB_USER = os.getenv('DB_USER', 'streaming_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'streaming_pass')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5433'))
DB_NAME = os.getenv('DB_NAME', 'streaming_db')

# Constrói a URL de forma segura, garantindo que todos os componentes são strings ASCII
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Cria engine usando psycopg2 com parâmetros nomeados para evitar problemas de encoding
# Isso contorna o bug do psycopg2 com caminhos que contêm caracteres especiais
from sqlalchemy.engine.url import URL

database_url = URL.create(
    drivername='postgresql',
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

engine = create_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=20,  # Aumenta o pool de conexões
    max_overflow=40,  # Aumenta o overflow
    pool_recycle=3600,  # Recicla conexões após 1 hora
    connect_args={
        'client_encoding': 'utf8'
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Retorna uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

