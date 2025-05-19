import sys
import os

# Adicionar o diretório atual ao path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

from src.main import app as application
