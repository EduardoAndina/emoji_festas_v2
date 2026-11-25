import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.banco import Banco
from ui.menu import SistemaCLI


def main():
    db = Banco()
    try:
        app = SistemaCLI(db)
        app.executar()
    finally:
        db.fechar()

if __name__ == "__main__":
    main()
