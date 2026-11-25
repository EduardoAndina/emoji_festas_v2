import re
from datetime import date, datetime
from database.banco import Banco
from models.entidades import CalendarioSalao, Funcionario

PREPOSICOES_NOME = {"da", "das", "de", "do", "dos", "e"}


def formatar_nome_pessoa(nome: str) -> str:
    partes = [p for p in re.sub(r"\s+", " ", nome.strip()).split(" ") if p]
    resultado = []
    for idx, parte in enumerate(partes):
        minuscula = parte.lower()
        if idx > 0 and minuscula in PREPOSICOES_NOME:
            resultado.append(minuscula)
        else:
            resultado.append("-".join(sub.capitalize() for sub in minuscula.split("-")))
    return " ".join(resultado)


def validar_e_formatar_nome(nome: str) -> tuple[bool, str]:
    limpo = re.sub(r"\s+", " ", nome.strip())
    if len(limpo) < 2:
        return False, "O nome deve ter pelo menos 2 caracteres."
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ\s\-']+", limpo):
        return False, "O nome deve conter apenas letras (sem numeros ou simbolos)."
    return True, formatar_nome_pessoa(limpo)


def validar_e_formatar_celular(celular: str) -> tuple[bool, str]:
    digitos = re.sub(r"\D", "", celular)
    if len(digitos) not in (10, 11):
        return False, "Celular/telefone invalido! Informe DDD + numero com 10 ou 11 digitos (ex: 51980623155)."
    if len(digitos) == 11 and digitos[2] != "9":
        return False, "Celular de 11 digitos deve comecar com 9 apos o DDD (ex: 51980623155)."
    if len(set(digitos)) == 1:
        return False, "Numero de telefone invalido (digitos repetidos)."
    if len(digitos) == 11:
        formatado = f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    else:
        formatado = f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return True, formatado


def validar_e_formatar_cpf(cpf: str) -> tuple[bool, str]:
    digitos = re.sub(r"\D", "", cpf)
    if len(digitos) != 11:
        return False, "CPF invalido! Deve conter exatamente 11 digitos numericos."
    if len(set(digitos)) == 1:
        return False, "CPF invalido (todos os digitos iguais)."
    soma1 = sum(int(digitos[i]) * (10 - i) for i in range(9))
    dv1 = (soma1 * 10) % 11
    dv1 = 0 if dv1 == 10 else dv1
    if dv1 != int(digitos[9]):
        return False, "CPF invalido! Primeiro digito verificador nao confere."
    soma2 = sum(int(digitos[i]) * (11 - i) for i in range(10))
    dv2 = (soma2 * 10) % 11
    dv2 = 0 if dv2 == 10 else dv2
    if dv2 != int(digitos[10]):
        return False, "CPF invalido! Segundo digito verificador nao confere."
    formatado = f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    return True, formatado


def validar_data_festa(data_str: str) -> tuple[bool, str]:
    limpa = data_str.strip()
    try:
        dt = date.fromisoformat(limpa)
    except ValueError:
        return False, "Data invalida! Use o formato AAAA-MM-DD (ex: 2026-12-20) com dia e mes reais."
    if dt < date.today():
        return False, "A data da festa nao pode ser no passado."
    return True, dt.isoformat()


def validar_hora_festa(hora_str: str) -> tuple[bool, str]:
    limpa = hora_str.strip()
    if not re.fullmatch(r"\d{2}:\d{2}", limpa):
        return False, "Horario invalido! Use o formato HH:MM (ex: 14:00)."
    try:
        hr = datetime.strptime(limpa, "%H:%M").time()
    except ValueError:
        return False, "Horario invalido! Informe horas entre 00:00 e 23:59."
    return True, hr.strftime("%H:%M")


def _perguntar_tentar_novamente(mensagem_erro: str) -> bool:
    print(f"Erro: {mensagem_erro}")
    while True:
        resp = input("Deseja tentar cadastrar/digitar novamente? (s/n): ").strip().lower()
        if resp in ("s", "sim"):
            return True
        if resp in ("n", "nao", "não"):
            return False
        print("Digite 's' para sim ou 'n' para nao.")


def _ler_int(
    mensagem: str,
    permitir_vazio: bool = False,
    padrao: int | None = None,
    minimo: int | None = None,
    maximo: int | None = None,
) -> int | None:
    while True:
        entrada = input(mensagem).strip()
        if not entrada and permitir_vazio:
            return padrao
        try:
            valor = int(entrada)
            if minimo is not None and valor < minimo:
                print(f"O valor deve ser maior ou igual a {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"O valor deve ser menor ou igual a {maximo}.")
                continue
            return valor
        except ValueError:
            print("Entrada invalida! Digite um numero inteiro.")


def _ler_float(mensagem: str, minimo: float | None = None) -> float:
    while True:
        entrada = input(mensagem).strip().replace(",", ".")
        try:
            valor = float(entrada)
            if minimo is not None and valor < minimo:
                print(f"O valor deve ser maior ou igual a {minimo:.2f}.")
                continue
            return valor
        except ValueError:
            print("Entrada invalida! Digite um valor numerico (ex: 250.00).")


class SistemaCLI:
    def __init__(self, db: Banco):
        self.db = db
        self.usuario_logado: Funcionario | None = None

    def login(self) -> bool:
        print("=" * 44)
        print("      EMOJIFESTAS - LOGIN DO SISTEMA      ")
        print("=" * 44)
        print("(Dica: marina / 1234 [Proprietaria] ou lucas / 1234 [Atendente])")
        for tentativa in range(3):
            usuario = input("Usuario: ")
            senha = input("Senha: ")
            func = self.db.autenticar(usuario, senha)
            if func:
                self.usuario_logado = func
                print(f"\nBem-vindo(a), {func.nome} ({func.perfil.capitalize()})!")
                return True
            print(f"Credenciais invalidas ({2 - tentativa} tentativa(s) restante(s)).")
        return False

    def executar(self):
        if not self.login():
            print("Numero maximo de tentativas excedido. Encerrando.")
            return

        while True:
            print("\n" + "=" * 44)
            print("       EMOJIFESTAS - MENU PRINCIPAL       ")
            print("=" * 44)
            print("1. Listar Espacos (Saloes), Combos e Extras")
            print("2. Listar Clientes")
            print("3. Cadastrar Novo Cliente")
            print("4. Agendar Festa (com verificacao de agenda)")
            print("5. Listar Agendamentos (Festas)")
            print("6. Ver Calendario Mensal por Espaco")
            print("7. Registrar / Consultar Pagamentos")
            if self.usuario_logado and self.usuario_logado.eh_proprietaria():
                print("8. [Proprietaria] Cadastrar Novo Espaco")
                print("9. [Proprietaria] Cancelar Festa")
            print("0. Sair")
            print()
            opcao = input("Escolha uma opcao: ").strip()

            if opcao == "1":
                self._exibir_catalogo()
            elif opcao == "2":
                self._listar_clientes()
            elif opcao == "3":
                self._cadastrar_cliente()
            elif opcao == "4":
                self._agendar_festa()
            elif opcao == "5":
                self._listar_festas()
            elif opcao == "6":
                self._ver_calendario_espaco()
            elif opcao == "7":
                self._gerenciar_pagamentos()
            elif opcao == "8" and self.usuario_logado and self.usuario_logado.eh_proprietaria():
                self._cadastrar_salao()
            elif opcao == "9" and self.usuario_logado and self.usuario_logado.eh_proprietaria():
                self._cancelar_festa()
            elif opcao == "0":
                print("Saindo do sistema... Ate logo!")
                break
            else:
                print("Opcao invalida ou sem permissao de acesso.")

    def _exibir_catalogo(self):
        print("\n--- ESPACOS EMOJIFESTAS ---")
        saloes = self.db.listar_saloes()
        if not saloes:
            print("Nenhum espaco cadastrado.")
        else:
            for s in saloes:
                print(f"[{s.id}] {s.nome} | Capacidade: ate {s.capacidade} convidados | Acrescimo: R$ {s.acrescimo:,.2f}")
                if s.endereco:
                    print(f"    Endereco: {s.endereco}")
                if s.diferencial:
                    print(f"    Diferencial: {s.diferencial}")
                if s.estrutura:
                    print(f"    Estrutura: {s.estrutura}")

        print("\n--- COMBOS ---")
        combos = self.db.listar_combos()
        if not combos:
            print("Nenhum combo cadastrado.")
        else:
            for c in combos:
                print(f"[{c.id}] {c.nome} - R$ {c.preco:,.2f} ({c.descricao})")

        print("\n--- EXTRAS ---")
        extras = self.db.listar_extras()
        if not extras:
            print("Nenhum extra cadastrado.")
        else:
            for e in extras:
                print(f"[{e.id}] {e.nome} - R$ {e.preco:,.2f}")
        input("\nPressione Enter para voltar ao menu...")

    def _listar_clientes(self):
        print("\n--- CLIENTES CADASTRADOS ---")
        clientes = self.db.listar_clientes()
        if not clientes:
            print("Nenhum cliente cadastrado.")
            input("\nPressione Enter para voltar ao menu...")
            return
        for c in clientes:
            print(f"[{c.id}] {c.nome} | Contato: {c.contato} | Doc: {c.documento}")
        input("\nPressione Enter para voltar ao menu...")

    def _cadastrar_cliente(self):
        while True:
            print("\n--- NOVO CLIENTE ---")
            nome_raw = input("Nome completo: ")
            ok_nome, nome_ou_erro = validar_e_formatar_nome(nome_raw)
            if not ok_nome:
                if _perguntar_tentar_novamente(nome_ou_erro):
                    continue
                print("Cadastro cancelado.")
                return

            contato_raw = input("Celular com DDD (ex: 51980623155): ")
            ok_cel, cel_ou_erro = validar_e_formatar_celular(contato_raw)
            if not ok_cel:
                if _perguntar_tentar_novamente(cel_ou_erro):
                    continue
                print("Cadastro cancelado.")
                return

            doc_raw = input("CPF (apenas numeros ou 000.000.000-00): ")
            ok_cpf, cpf_ou_erro = validar_e_formatar_cpf(doc_raw)
            if not ok_cpf:
                if _perguntar_tentar_novamente(cpf_ou_erro):
                    continue
                print("Cadastro cancelado.")
                return

            try:
                cid = self.db.cadastrar_cliente(nome_ou_erro, cel_ou_erro, cpf_ou_erro)
                print(f"Cliente '{nome_ou_erro}' cadastrado com sucesso! ID: {cid}")
                return
            except ValueError as err:
                if not _perguntar_tentar_novamente(str(err)):
                    print("Cadastro cancelado.")
                    return

    def _mostrar_calendario_salao(self, salao_id: int, ano: int, mes: int):
        salao = self.db.salao(salao_id)
        if not salao:
            return
        festas_mes = self.db.listar_festas_por_salao_e_mes(salao_id, ano, mes)
        cal = CalendarioSalao(salao, ano, mes, festas_mes)
        print()
        print(cal())
        if cal.festas_mes:
            print(f"Horarios ja ocupados em {salao.nome} ({cal.nome_mes}/{ano}):")
            for f in cal.festas_mes:
                cli = self.db.cliente(f.cliente_id)
                print(
                    f"  - Dia {f.data.split('-')[2]} ({f.data}): {f.inicio} as {f.hora_fim_str()} "
                    f"[Festa #{f.id} - {cli.nome if cli else 'Cliente'}]"
                )
        else:
            print(f"Nenhuma reserva em {salao.nome} para {cal.nome_mes}/{ano}. Todos os dias livres!")

    def _ver_calendario_espaco(self):
        saloes = self.db.listar_saloes()
        if not saloes:
            print("\nNenhum espaco cadastrado.")
            return

        print("\n--- CALENDARIO POR ESPACO ---")
        ids_saloes = {s.id for s in saloes}
        for s in saloes:
            print(f"[{s.id}] {s.nome} (ate {s.capacidade} convidados)")

        salao_id = _ler_int("Escolha o ID do Espaco: ", minimo=1)
        assert salao_id is not None
        if salao_id not in ids_saloes:
            print("Espaco nao encontrado.")
            return

        hoje = date.today()
        ano = _ler_int(
            f"Ano (Enter para {hoje.year}): ", permitir_vazio=True, padrao=hoje.year, minimo=2020, maximo=2100
        )
        mes = _ler_int(
            f"Numero do mes [1 a 12] (Enter para {hoje.month}): ",
            permitir_vazio=True,
            padrao=hoje.month,
            minimo=1,
            maximo=12,
        )
        assert ano is not None and mes is not None
        self._mostrar_calendario_salao(salao_id, ano, mes)
        input("\nPressione Enter para voltar ao menu...")

    def _agendar_festa(self):
        while True:
            print("\n--- NOVO AGENDAMENTO ---")
            saloes = self.db.listar_saloes()
            if not saloes:
                print("Nenhum espaco cadastrado.")
                return
            ids_saloes = {s.id for s in saloes}
            for s in saloes:
                print(f"[{s.id}] {s.nome} | Ate {s.capacidade} convidados | Acrescimo: R$ {s.acrescimo:,.2f}")
            salao_id = _ler_int("ID do Espaco: ", minimo=1)
            assert salao_id is not None
            if salao_id not in ids_saloes:
                if _perguntar_tentar_novamente("ID de espaco inexistente!"):
                    continue
                return

            clientes = self.db.listar_clientes()
            if not clientes:
                print("Nenhum cliente cadastrado. Cadastre um cliente primeiro.")
                return
            ids_clientes = {c.id for c in clientes}
            for c in clientes:
                print(f"[{c.id}] {c.nome} ({c.documento})")
            cliente_id = _ler_int("ID do Cliente: ", minimo=1)
            assert cliente_id is not None
            if cliente_id not in ids_clientes:
                if _perguntar_tentar_novamente("ID de cliente inexistente!"):
                    continue
                return

            data_raw = input("Data (AAAA-MM-DD): ")
            ok_data, data_ou_erro = validar_data_festa(data_raw)
            if not ok_data:
                if _perguntar_tentar_novamente(data_ou_erro):
                    continue
                return

            # Mostra o calendario do espaco no mes escolhido antes de pedir o horario
            dt_escolhida = date.fromisoformat(data_ou_erro)
            self._mostrar_calendario_salao(salao_id, dt_escolhida.year, dt_escolhida.month)

            inicio_raw = input("\nHorario de Inicio (HH:MM): ")
            ok_hora, hora_ou_erro = validar_hora_festa(inicio_raw)
            if not ok_hora:
                if _perguntar_tentar_novamente(hora_ou_erro):
                    continue
                return

            combos = self.db.listar_combos()
            ids_combos = {cb.id for cb in combos}
            for cb in combos:
                print(f"[{cb.id}] {cb.nome} (R$ {cb.preco:,.2f})")
            combo_id = _ler_int(
                "ID do Combo (ou Enter para nenhum): ", permitir_vazio=True, padrao=None, minimo=1
            )
            if combo_id is not None and combo_id not in ids_combos:
                if _perguntar_tentar_novamente("ID de combo inexistente!"):
                    continue
                return

            horas_extra = _ler_int(
                "Horas extras (Enter para 0): ", permitir_vazio=True, padrao=0, minimo=0
            )
            assert horas_extra is not None

            extras = self.db.listar_extras()
            ids_extras = {ext.id for ext in extras}
            print("Extras disponiveis:")
            for ext in extras:
                print(f"[{ext.id}] {ext.nome} (R$ {ext.preco:,.2f})")

            extras_ids: list[int] = []
            extras_ok = True
            while True:
                extras_input = input(
                    "IDs dos extras separados por virgula (ex: 1,3) ou Enter para nenhum: "
                ).strip()
                if not extras_input:
                    extras_ids = []
                    break
                try:
                    candidatos = [int(x.strip()) for x in extras_input.split(",") if x.strip()]
                    invalidos = [eid for eid in candidatos if eid not in ids_extras]
                    if invalidos:
                        print(f"Extra(s) inexistente(s): {invalidos}")
                        extras_ok = False
                        break
                    extras_ids = candidatos
                    break
                except ValueError:
                    print("Digite apenas numeros separados por virgula (ex: 1,3).")

            if not extras_ok:
                if _perguntar_tentar_novamente("Um ou mais extras informados nao existem."):
                    continue
                return

            obs = input("Observacoes: ").strip()

            sucesso, mensagem = self.db.agendar_festa(
                salao_id, cliente_id, data_ou_erro, hora_ou_erro, combo_id, extras_ids, horas_extra, obs
            )
            print(mensagem)
            if sucesso:
                return
            if not _perguntar_tentar_novamente("Nao foi possivel concluir o agendamento."):
                return

    def _listar_festas(self):
        print("\n--- LISTA DE FESTAS AGENDADAS ---")
        festas = self.db.listar_festas()
        if not festas:
            print("Nenhuma festa agendada.")
            input("\nPressione Enter para voltar ao menu...")
            return

        for f in festas:
            cliente = self.db.cliente(f.cliente_id)
            salao = self.db.salao(f.salao_id)
            pago = self.db.total_pago(f.id)
            saldo = max(0.0, round(f.total - pago, 2))
            status_pgto = "QUITADA" if saldo == 0 else f"Falta R$ {saldo:,.2f}"
            print(
                f"Festa #{f.id} | {salao.nome if salao else 'N/A'} | "
                f"Cliente: {cliente.nome if cliente else 'N/A'} | "
                f"Data: {f.data} ({f.inicio} as {f.hora_fim_str()}) | "
                f"Total: R$ {f.total:,.2f} | Pago: R$ {pago:,.2f} ({status_pgto})"
            )
        input("\nPressione Enter para voltar ao menu...")

    def _gerenciar_pagamentos(self):
        festas = self.db.listar_festas()
        if not festas:
            print("\nNenhuma festa agendada para gerenciar pagamentos.")
            return

        self._listar_festas()
        festa_id = _ler_int("\nInforme o ID da Festa: ", minimo=1)
        assert festa_id is not None
        festa = self.db.festa(festa_id)
        if not festa:
            print("Festa nao encontrada.")
            return

        pagamentos = self.db.listar_pagamentos(festa_id)
        print(f"\n--- HISTORICO DE PAGAMENTOS (Festa #{festa.id}) ---")
        if not pagamentos:
            print("Nenhum pagamento registrado ainda.")
        else:
            for p in pagamentos:
                print(f"[{p.id}] {p.data} - {p.tipo}: R$ {p.valor:,.2f}")

        pago = self.db.total_pago(festa_id)
        saldo = round(festa.total - pago, 2)
        print(
            f"Total da festa: R$ {festa.total:,.2f} | "
            f"Total pago: R$ {pago:,.2f} | Saldo devedor: R$ {saldo:,.2f}"
        )

        if saldo <= 0:
            print("Esta festa ja esta totalmente quitada.")
            return

        while True:
            registrar = input("Deseja registrar um novo pagamento agora? (s/n): ").strip().lower()
            if registrar in ("n", "nao", "não"):
                return
            if registrar not in ("s", "sim"):
                print("Digite 's' para sim ou 'n' para nao.")
                continue
            valor = _ler_float("Valor do pagamento (R$): ", minimo=0.01)
            tipo = input("Tipo (Sinal / Parcela / Quitacao): ").strip() or "Parcela"
            ok, msg = self.db.registrar_pagamento(festa_id, valor, tipo)
            print(msg)
            if ok:
                return
            if not _perguntar_tentar_novamente("Pagamento nao registrado."):
                return

    def _cadastrar_salao(self):
        while True:
            print("\n--- CADASTRAR NOVO ESPACO ---")
            nome_raw = input("Nome do espaco (ex: Espaco 4 - Garden): ").strip()
            if len(nome_raw) < 2:
                if _perguntar_tentar_novamente("O nome do espaco deve ter pelo menos 2 caracteres."):
                    continue
                return
            capacidade = _ler_int("Capacidade maxima de convidados: ", minimo=1)
            acrescimo = _ler_float("Acrescimo no valor (R$): ", minimo=0.0)
            endereco = input("Endereco (opcional): ").strip()
            diferencial = input("Diferencial (opcional): ").strip()
            estrutura = input("Estrutura (opcional): ").strip()
            assert capacidade is not None
            try:
                sid = self.db.criar_salao(
                    nome_raw, capacidade, acrescimo, endereco, diferencial, estrutura
                )
                print(f"Espaco '{nome_raw}' cadastrado com sucesso! ID: {sid}")
                return
            except ValueError as err:
                if not _perguntar_tentar_novamente(str(err)):
                    return

    def _cancelar_festa(self):
        festas = self.db.listar_festas()
        if not festas:
            print("\nNenhuma festa agendada para cancelar.")
            return
        self._listar_festas()
        festa_id = _ler_int("\nID da Festa para cancelar (ou 0 para voltar): ", minimo=0)
        assert festa_id is not None
        if festa_id == 0:
            return
        _, msg = self.db.cancelar_festa(festa_id)
        print(msg)
