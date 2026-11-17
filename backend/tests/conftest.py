"""Configuração do pytest: garante que o pacote backend seja importável."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
