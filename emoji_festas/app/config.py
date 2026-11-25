import os
from pathlib import Path

# Diretorio raiz do projeto (um nivel acima de app/)
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_FILE = Path(os.environ.get("EMOJIFESTAS_DB_PATH", ROOT_DIR / "emojifestas.db"))
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

DURACAO_BASE = 4  # horas incluidas em toda festa
VALOR_HORA_EXTRA = 200.0
