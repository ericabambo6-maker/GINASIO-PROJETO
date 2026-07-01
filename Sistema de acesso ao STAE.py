# Sistema de acesso ao STAE
# Desenvolvido por: Érica Bambo
# Meta A: Captura de dados de quem entra
# Fase 1: Apresentação do Menu Inicial e Captura do Tipo de Utilizador

print("Bem-vindo ao Sistema de Acesso ao STAE!")
while True:
    # TEXTO ATUALIZADO AQUI: Adicionado o | [0]Sair para o guarda saber que existe
    try:
        tipo_usuario = int(input("\nTipo de utilizador: [1]Funcionario | [2]Estagiário | [3]Visitante | [0]Sair: ").strip())
    except ValueError:
        print("Opção inválida! Digite um número entre [0] e [3].")
        continue

    # Dados do funcionário
    # Nota técnica: O id_funcionario refere-se ao número único do Cartão de Acesso institucional.
    if tipo_usuario == 0:
        print("Encerrando o Sistema de Acesso ao STAE... Até logo!")
        break
    elif tipo_usuario == 1:
        nome_funcionario = input("Digite o nome do funcionario: ")
        id_funcionario = input("Digite o número único de identificação do funcionario: ")
        departamento = input("Digite o departamento do funcionario: ")
        print(f"O funcionário {nome_funcionario} com o ID {id_funcionario} do departamento {departamento} foi registrado com sucesso.")
    
    # Dados do estagiário
    # Nota técnica: O id_estagiario refere-se ao número único do Cartão de Acesso institucional.
    elif tipo_usuario == 2:
        nome_estagiario = input("Digite o nome do estagiário: ")
        id_estagiario = input("Digite o número único de identificação do estagiário: ")
        departamento = input("Digite o departamento do estagiário: ")
        print(f"O estagiário {nome_estagiario} com o ID {id_estagiario} do departamento {departamento} foi registrado com sucesso.")
    
    # Dados do visitante
    # Nota técnica: Como o visitante é externo, o ID aqui recolhido é o documento oficial (BI ou Passaporte).
    elif tipo_usuario == 3:
        nome_visitante = input("Digite o nome do visitante: ")
        # É familiar?
        familiar = input("É familiar de algum funcionario? [Sim/Não]: ")
        # Se sim
        if familiar.lower() == "sim":
            id_visitante = input("Digite o número do BI ou Passaporte do visitante: ")
            # Insere o Primeiro nome e apelido do funcionário que será visitado
            nome_funcionario = input("Digite o nome do funcionário que será visitado: ")
            print(f"O visitante {nome_visitante} é familiar do funcionário {nome_funcionario}.")
        # Se não
        else:
            motivo_visita = input("Digite o motivo da visita: ")
            departamento = input("Digite o departamento para onde o visitante se dirige: ")
            print(f"O visitante {nome_visitante} com o motivo de visita '{motivo_visita}' foi registrado para o departamento {departamento}.")
    else:
        # MENSAGEM DE ERRO ATUALIZADA AQUI: Incluído o [0]
        print("Opção inválida! Digite um número entre [0] e [3].")
