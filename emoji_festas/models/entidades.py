import calendar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from app.config import DURACAO_BASE, VALOR_HORA_EXTRA


@dataclass
class Funcionario:
    id: int
    nome: str
    usuario: str
    perfil: str  # "proprietaria" ou "atendente"
    ativo: bool = True

    def eh_proprietaria(self) -> bool:
        return self.perfil.strip().lower() == "proprietaria"


@dataclass
class Salao:
    id: int
    nome: str
    capacidade: int
    acrescimo: float
    endereco: str = ""
    diferencial: str = ""
    estrutura: str = ""


@dataclass
class Combo:
    id: int
    nome: str
    preco: float
    descricao: str = ""


@dataclass
class Extra:
    id: int
    nome: str
    preco: float


@dataclass
class Cliente:
    id: int
    nome: str
    contato: str
    documento: str


@dataclass
class Pagamento:
    id: int
    festa_id: int
    valor: float
    data: str
    tipo: str  # "Sinal", "Parcela", "Quitacao"


@dataclass
class Festa:
    id: int
    salao_id: int
    cliente_id: int
    data: str
    inicio: str
    combo_id: int | None
    horas_extra: int = 0
    total: float = 0.0
    obs: str = ""
    extras: list[int] = field(default_factory=list)

    @property
    def duracao(self) -> int:
        return DURACAO_BASE + self.horas_extra

    def intervalo(self) -> tuple[datetime, datetime]:
        ini = datetime.fromisoformat(f"{self.data}T{self.inicio}")
        return ini, ini + timedelta(hours=self.duracao)

    def hora_fim_str(self) -> str:
        _, fim = self.intervalo()
        return fim.strftime("%H:%M")

    def conflita_com(self, outra: "Festa") -> bool:
        if self.salao_id != outra.salao_id or self.id == outra.id:
            return False
        a1, a2 = self.intervalo()
        b1, b2 = outra.intervalo()
        return a1 < b2 and b1 < a2

    @staticmethod
    def calcular_orcamento(
        salao: Salao | None,
        combo: Combo | None,
        extras: list[Extra],
        horas_extra: int,
    ) -> float:
        total = (salao.acrescimo if salao else 0.0) + (horas_extra * VALOR_HORA_EXTRA)
        total += combo.preco if combo else 0.0
        total += sum(extra.preco for extra in extras)
        return round(total, 2)


class CalendarioSalao:
    """
    Representa o calendario mensal de um Salao especifico,
    destacando os dias que ja possuem festas agendadas.
    Inspirado na classe Mes vista em aula (POO).
    """

    NOMES_MESES = [
        "", "JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO",
        "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
    ]
    DIAS_SEMANA = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"]

    def __init__(self, salao: Salao, ano: int, numero_mes: int, festas_mes: list[Festa]):
        if not (1 <= numero_mes <= 12):
            raise ValueError("O numero do mes deve estar entre 1 e 12.")
        if ano < 2000:
            raise ValueError("Ano invalido para o calendario.")

        self.salao = salao
        self.ano = ano
        self.numero_mes = numero_mes
        self.festas_mes = sorted(festas_mes, key=lambda f: (f.data, f.inicio))
        self.nome_mes = self.NOMES_MESES[numero_mes]

        # calendar.monthrange retorna (dia_semana_segunda0, total_dias)
        primeiro_seg0, self.total_dias = calendar.monthrange(ano, numero_mes)
        # Converte para 0=Domingo .. 6=Sabado
        self.dia_inicio_semana = (primeiro_seg0 + 1) % 7

        self.dias_ocupados: dict[int, list[Festa]] = {}
        for f in self.festas_mes:
            dia = int(f.data.split("-")[2])
            self.dias_ocupados.setdefault(dia, []).append(f)

    def formatar_calendario(self) -> str:
        largura = 35  # 5 chars por coluna * 7 dias
        linhas = []
        linhas.append("=" * largura)
        linhas.append(f"{self.salao.nome.upper()} - {self.nome_mes}/{self.ano}".center(largura))
        linhas.append("-" * largura)
        linhas.append(" ".join(f"{dia:>4}" for dia in self.DIAS_SEMANA))
        linhas.append("-" * largura)

        grade = []
        for _ in range(self.dia_inicio_semana):
            grade.append("    ")

        for d in range(1, self.total_dias + 1):
            if d in self.dias_ocupados:
                grade.append(f"[{d:02d}]")
            else:
                grade.append(f" {d:02d} ")

        for i in range(0, len(grade), 7):
            linhas.append(" ".join(grade[i:i + 7]))

        linhas.append("=" * largura)
        linhas.append("Legenda: [DD] = Dia com reserva no salao")
        return "\n".join(linhas)

    def __call__(self) -> str:
        return self.formatar_calendario()

    def __str__(self) -> str:
        return self.formatar_calendario()
