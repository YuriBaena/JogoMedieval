from random import randint
import time


def cria_mapa():
    mapa = []

    with open("arquivos/localizacao/mapa.txt", "r") as mp:
        mapa_atual = mp.readline().strip()

    with open(f"arquivos/mapas/{mapa_atual}.txt", "r") as mp:
        linhas = mp.readlines()
        if mapa_atual == "0":
            linhas = linhas[1:]

    for i in range(5):
        linha = []
        for j in range(5):
            a = linhas[i * 5 + j].strip()
            linha.append(a)
        mapa.append(linha)

    with open("arquivos/localizacao/posicao.txt", "r") as pos:
        posicao = pos.readline().strip()
        x, y = map(int, posicao.split(','))

    return mapa, (x, y)


def imprime_mapa(mapa, posicao):
    print("\nLocais do Castelo:\n")

    x, y = posicao
    tamanho_colunas = []

    # Adiciona "웃" na posição correta
    mapa_com_icone = [linha[:] for linha in mapa]  # Copia o mapa original
    mapa_com_icone[x][y] = "웃"

    for coluna in range(5):
        comprimentos_coluna = []
        for linha in range(5):
            comprimentos_coluna.append(len(mapa_com_icone[linha][coluna]))
        tamanho_colunas.append(max(comprimentos_coluna))

    print("_" * (sum(tamanho_colunas) + 8))
    for linha in range(5):
        for coluna in range(5):
            lugar = mapa_com_icone[linha][coluna]
            print("{:<{}}".format(lugar, tamanho_colunas[coluna]), end="  ")
        print()
    print("_" * (sum(tamanho_colunas) + 8))


def movimenta():
    with open("arquivos/localizacao/posicao.txt", "r") as pos:
        posicao = pos.readline().strip()
        x, y = map(int, posicao.split(','))

    lugares, _ = cria_mapa()

    while True:
        destino = input("Onde deseja ir (Norte/Sul/Leste/Oeste): ").lower().strip()
        if destino != "" and destino in "nslo":
            break

    if destino[0] == "n" and x > 0:
        x -= 1
    elif destino[0] == "s" and x < len(lugares) - 1:
        x += 1
    elif destino[0] == "l" and y < len(lugares[0]) - 1:
        y += 1
    elif destino[0] == "o" and y > 0:
        y -= 1
    else:
        print("Movimento não é possível.")
        return False

    with open("arquivos/localizacao/posicao.txt", "w") as pos:
        pos.write(f"{x},{y}")

    return True


def mostra_inventario():
    print()
    vidas = []
    danos = []
    utilizaveis = []
    with open("arquivos/interacoes/inventario.txt", "r") as inv:
        vida = inv.readline().strip()
        print("Vida:", vida)
        dano = inv.readline().strip()
        print("Dano:", dano)
        print("Itens:")
        itens = inv.readlines()
        print()
        print("#@*(Itens que tem 💥 ou ❤️ nao podem ser usados em combate)*@#")
        print()
        for item in itens:
            if "❤️" in item:
                vidas.append(f"-{item.strip()}")
            elif "💥" in item:
                danos.append(f"-{item.strip()}")
            else:
                utilizaveis.append(f"-{item.strip()}")

        for i in utilizaveis:
            print(i)


def descreve_lugar():
    with open("arquivos/localizacao/mapa.txt", "r") as mapa_file:
        k = int(mapa_file.readline().strip())

    with open("arquivos/interacoes/descrica.txt", "r") as desc:
        for i, linha in enumerate(desc):
            if i == k:
                lugar, descricao = linha.strip().split(":")
                print("Você está na", lugar + ":", descricao)
                return
        else:
            print("Não foi encontrada uma descrição para a posição atual.")


def menu():
    while True:
        print()
        print("[1] Movimentar\n"
              "[2] Interagir\n"
              "[3] Inventário\n"
              "[4] Entrar/Sair da sala\n"
              "[5] Sair do Jogo")

        fazer = input("O que deseja fazer: ").strip()

        if fazer == "5":
            sair_ou_continuar = input("Deseja sair do jogo (S/N)? ").strip().lower()
            if sair_ou_continuar == "s":
                reseta()
                sair()
            elif sair_ou_continuar == "n":
                return  # Retorna ao jogo
            else:
                print("Opção inválida, por favor, escolha S ou N.")
        elif fazer.isdigit() and 1 <= int(fazer) <= 4:
            fazer = int(fazer)
            if fazer == 1:
                if movimenta():
                    mapa, posicao = cria_mapa()
                    imprime_mapa(mapa, posicao)
                    descreve_lugar()
            elif fazer == 2:
                interagir()
            elif fazer == 3:
                mostra_inventario()
            elif fazer == 4:
                with open("arquivos/localizacao/mapa.txt", "r") as mp:
                    if mp.read().strip() == "0":
                        entrar_sala()
                    else:
                        sair_sala()
        else:
            print("Opção inválida, por favor, escolha uma opção de 1 a 5.")


def interagir():
    mapa, posicao = cria_mapa()

    tem = False

    with open("arquivos/localizacao/mapa.txt", "r") as mp:
        numero1 = mp.read().strip()

    if numero1 != "0":

        x = posicao[0]
        y = posicao[1]

        with (open("arquivos/interacoes/itens.txt", "r") as opcoes):
            with open("arquivos/personagens/personagens.txt", "r") as personagem:
                for i, j in zip(opcoes.readlines(), personagem.readlines()):
                    numero2, objetos = i.split(":")
                    resto = j.split(":")[1]
                    nome, seu, oferece, precisa, vida_inimigo = resto.split("-")
                    precisa1 = precisa.split("(")[0]
                    dica = precisa.split("(")[1]

                    if numero1 == numero2:
                        if mapa[x][y] == nome.strip():
                            tem = True
                            verifica2 = verifica_inventario(precisa1)
                            if not verifica2[0] and seu.strip().lower() == "amigo":
                                interage_amigo(nome, seu, precisa1)
                                ajuda(dica, precisa1)
                            elif verifica2[0] and seu.strip().lower() == "amigo":
                                '''Se voce tem o item necessario, recebe algo do amigo'''
                                if not verifica_inventario(oferece[:-3])[0]:
                                    adiciona_ao_inventario(oferece, "")
                                else:
                                    print("Voce ja possui esse item no inventario")
                            elif not verifica2[0] and seu.strip().lower() == "inimigo":
                                interage_inimigo(nome, seu, oferece, vida_inimigo, precisa1)
                                ajuda(dica, precisa1)
                            elif verifica2[0] and seu.strip().lower() == "inimigo":
                                lutar(nome, vida_inimigo)

                        cada = objetos.split(",")

                        for i in cada:
                            lugar, item, desc = i.split("-")

                            if mapa[x][y] == lugar.strip():
                                tem = True
                                verifica1 = verifica_inventario(item)
                                if not verifica1[0]:
                                    adiciona_ao_inventario(item, desc)
                                    atualiza_vida(desc)
                                    atualiza_dano(desc)
                                else:
                                    print("Voce ja possui esse item no inventario")

        if not tem:
            print("Nesse exato local nao possui nada para interagir")

    else:
        print("Nao possui nada no Salao Geral para interagir")


def verifica_inventario(item):
    with open("arquivos/interacoes/inventario.txt", "r") as inv:
        for linha in inv.readlines():
            a = linha.split(":")[0].strip().lower()
            if item.strip().lower() in a:
                com = [True, a]
                return com
    return [False, None]


def ajuda(dica, item):
    while True:
        quer = input("Deseja ter uma dica de onde procurar esse item (S/N): ").lower()
        if quer in "sn":
            break

    numero = ''.join([char for char in dica if char.isdigit()])
    numero = int(numero)

    if quer in "Ss":
        with open("arquivos/mapas/0.txt", "r") as mapa:
            sala = mapa.readlines()[numero]
        print(f"Voce pode encontrar o item {item} -> {sala}")


def atualiza_vida(descricao):
    coracoes_adicionais = descricao.count("❤️")
    if coracoes_adicionais > 0:
        with open("arquivos/interacoes/inventario.txt", "r") as inv:
            linhas = inv.readlines()
            vida = linhas[0].strip()
        nova_vida = vida + (" ❤️" * coracoes_adicionais)
        linhas[0] = nova_vida + "\n"
        with open("arquivos/interacoes/inventario.txt", "w") as inv:
            inv.writelines(linhas)
        print(f"Vida atualizada: {nova_vida}")
    else:
        pass


def atualiza_dano(descricao):
    dano_adicionais = descricao.count("💥")
    if dano_adicionais > 0:
        with open("arquivos/interacoes/inventario.txt", "r") as inv:
            linhas = inv.readlines()
            dano = linhas[1].strip()  # Corrigido para ler a segunda linha
        novo_dano = dano + (" 💥" * dano_adicionais)
        linhas[1] = novo_dano + "\n"  # Corrigido para atualizar a segunda linha
        with open("arquivos/interacoes/inventario.txt", "w") as inv:
            inv.writelines(linhas)
        print(f"Dano atualizado: {novo_dano}")
    else:
        pass


def adiciona_ao_inventario(item, descricao):
    excessaoes = "👑📖🪄🌫🗝️✝🥀🎶🐎🔪🗺🔨️🖼🔑🏺🧩"
    if item[-1] not in excessaoes:
        with open("arquivos/interacoes/inventario.txt", "a") as inv:
            inv.write(f"{item}: {descricao.strip()}\n")
        print(f"Item adicionado ao inventário: {item}")
    else:
        if "👑" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Coroa Real: Atira raios poderosos pelos diamantes{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "📖" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Livro dos Feitiços: Amaldiçoa o oponente{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🪄" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Varinha Mágica: Faz loucuras{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🌫" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Gás de fumaça: Da dano ao oponente{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🗝️" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Chave Secreta: Abre um portal para outra dimensao para um monstro vir de la {item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "✝" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Cruz Sagrada: Um espirito do bem vem te proteger {item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🥀" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Flor de Gelo: Congela um membro do inimigo{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🎶" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Lira Mística: Desnorteia oponente{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🐎" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Cavalo Real: Treinado para te ajudar em combates{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🔪" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Facão do Chef: Ao ser lançada com um alvo em mente, ela seguira o alvo{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🗺" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(
                    f"Mapa Secreto: Se desenhado sobre ele criara os objetos desenhados nos lugares que foram desenhados em cima{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🔨" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(
                    f"Martelo de Guerra: Prende oponente por certo tempo para que voce possa causar-lhe dano{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "️🖼" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Pintura Enfeitiçada: Sai um desenho aleatorio do quadro para te ajudar a lutar{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🔑" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Chave do Tempo: Para o tempo por 10 segundos para conseguir atacar o inimigo{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🏺" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(
                    f"Relíquias Ancestrais: Cinzas viram o melhor lutador da Grecia antiga para te ajudar em combate{item}\n")
            print(f"Item adicionado ao inventário: {item}")
        elif "🧩" in item:
            with open("arquivos/interacoes/inventario.txt", "a") as inv:
                inv.write(f"Dica: {item}\n")
            print(f"{item}: Para salvar seus irmãos e rainha é necessário derrotar todos os inimigos do castelo!")


def remove_do_inventario(item):
    # Abre o arquivo de inventário para leitura
    with open("arquivos/interacoes/inventario.txt", "r") as inv:
        linhas = inv.readlines()

    # Remove o item especificado do inventário
    with open("arquivos/interacoes/inventario.txt", "w") as inv:
        # Escreve a primeira linha (vida) inalterada
        inv.write(linhas[0])
        # Escreve a segunda linha (dano) inalterada
        inv.write(linhas[1])

        # Escreve os itens restantes, exceto o item a ser removido
        for linha in linhas[2:]:
            nome_item, descricao = linha.strip().split(":")
            if nome_item.lower() != item.lower():
                inv.write(linha)


def interage_amigo(personagem, seu, precisa1):
    print()
    print(
        f"O {personagem} é seu {seu} e  precisa do {precisa1} (Ganhando algo em troca que talvez seja muito importante)")


def interage_inimigo(personagem, seu, oferece, vida, precisa1):
    print()
    print(f"O {personagem} é seu {seu} e {oferece.lower()} e tem {vida}")
    print(f"Mas para batalhar com ele voce precisa disso: {precisa1}")


def lutar(nome, inimigo_coracao):
    lutar = input("Deseja lutar agora (S/N): ")
    print()

    if lutar in "Ss":
        with open("arquivos/interacoes/inventario.txt", "r") as inv:
            itens = inv.readlines()
            minha_vida = itens[0].count("❤️")
            meu_dano = itens[1].count("💥")

            vida_inimigo = inimigo_coracao.count("❤️")

            time.sleep(1)
            print(f"Lutando: ", end="")
            time.sleep(0.5)
            print("Você", end="")
            time.sleep(1)
            print(" ⚔️ ", end="")
            time.sleep(1)
            print(f"{nome}")
            for i in range(5):
                print(".", end="")
                time.sleep(0.5)

            while True:

                tem = False

                with open("arquivos/interacoes/inventario.txt", "r") as inv:
                    a = inv.readlines()
                    for i in a:
                        if "🛡️" in i:
                            tem = True
                            break
                        elif "🗡️️👑📖🪄🌫️🗝️✝️🥀🎶🐎🔪🗺️🔨🖼️🔑🏺" in i:
                            tem = True
                            break

                print()
                print(f"Sua vida: {minha_vida * ' ❤️'} ({minha_vida})")
                print(f"Vida do {nome}: {vida_inimigo * ' ❤️'} ({vida_inimigo})")
                print()

                dano = dano_inimigo(vida_inimigo)

                if tem:
                    quer = input("Deseja usar algum item (S/N): ").lower()

                    if quer == "s":
                        usou = usar_item()

                        if usou:
                            if usou[0] == "Esquiva":
                                time.sleep(2)
                                print(f"{nome} tentou te acertar, mas errou miseravelmente")
                                print(f"Iria ter dado {dano} de dano")

                                if meu_dano > vida_inimigo:
                                    time.sleep(2)
                                    print()
                                    print(f"Voce derotou o {nome}")
                                    with open("arquivos/personagens/mortos.txt", "a") as morto:
                                        morto.write(nome)
                                    break
                                else:
                                    time.sleep(2)
                                    print(f"Voce deu {meu_dano} no {nome}")
                                    vida_inimigo -= meu_dano

                            elif usou[0] == "Dano":
                                meu_dano = usou[1]
                                time.sleep(2)
                                print(f"{nome} deu {dano} de dano em você")

                                if dano > minha_vida:
                                    time.sleep(2)
                                    print("Morreu")
                                    reseta()
                                    time.sleep(1)
                                    mapa, posicao = cria_mapa()
                                    imprime_mapa(mapa, posicao)
                                    descreve_lugar()
                                    break
                                else:
                                    if meu_dano > vida_inimigo:
                                        time.sleep(2)
                                        print()
                                        print(f"Voce derotou o {nome}")
                                        with open("arquivos/personagens/mortos.txt", "a") as morto:
                                            morto.write(nome)
                                        break
                                    else:
                                        minha_vida -= dano
                                        time.sleep(2)
                                        print(f"Voce deu {meu_dano} no {nome}")
                                        vida_inimigo -= meu_dano

                else:
                    print("Você não tem itens")
                    time.sleep(2)
                    print(f"{nome} deu {dano} de dano em você")
                    if dano > minha_vida:
                        time.sleep(2)
                        print("Morreu")
                        reseta()
                        time.sleep(1)
                        mapa, posicao = cria_mapa()
                        imprime_mapa(mapa, posicao)
                        descreve_lugar()
                        break
                    else:
                        if meu_dano > vida_inimigo:
                            time.sleep(2)
                            print()
                            print(f"Voce derotou o {nome}")
                            with open("arquivos/personagens/mortos.txt", "w") as morto:
                                morto.write(nome)
                            break
                        else:
                            minha_vida -= dano
                            time.sleep(2)
                            print(f"Voce deu {meu_dano} no {nome}")
                            vida_inimigo -= meu_dano


def usar_item():
    global com
    tem = False
    while not tem:
        mostra_inventario()
        print()
        qual = input("Qual item deseja usar: ")
        print()
        com = verifica_inventario(qual.lower().strip())
        tem = com[0]

        with open("arquivos/interacoes/inventario.txt", "r") as inv:
            for i in inv.readlines():
                if com[1] in i.split(":")[0].lower().strip():
                    item = i.split(":")[1]
                    break

    remove_do_inventario(com[1])

    if item.strip()[-2] in "🛡":
        lista = ["Esquiva"]
        return lista
    elif item.strip()[-2] in "🗡️👑📖🪄🌫️🗝️✝🥀🎶🐎🔪🗺️🔨🖼️🔑🏺":
        dano = randint(1, 5)
        lista = ["Dano", dano]
        return lista


def dano_inimigo(vida_inimigo):
    if vida_inimigo < 10:
        return randint(1, 7)
    elif 10 >= vida_inimigo >= 15:
        return randint(2, 12)
    else:
        return randint(3, 17)


def sair_sala():
    with open("arquivos/localizacao/posicao.txt", "r") as pos:
        x, y = map(int, pos.readline().strip().split(','))

    mapa_atual, _ = cria_mapa()

    if mapa_atual[x][y] != "Porta":
        print("Você não está na porta. Não pode sair da sala.")
        return

    with open("arquivos/localizacao/mapa.txt", "r") as mp:
        mapa_atual_num = int(mp.readline().strip())

    # Lê a posição anterior a partir do arquivo entrou.txt
    with open("arquivos/localizacao/entrou.txt", "r") as entrou:
        posicao_anterior = entrou.readline().strip()
        anterior_x, anterior_y = map(int, posicao_anterior.split(','))

    # Atualiza o mapa para o anterior e a posição do jogador
    with open("arquivos/localizacao/mapa.txt", "w") as mp:
        mp.write("0")
    with open("arquivos/localizacao/posicao.txt", "w") as pos:
        pos.write(f"{anterior_x},{anterior_y}")

    mapa, posicao = cria_mapa()
    imprime_mapa(mapa, posicao)
    descreve_lugar()


def entrar_sala():
    mapa_inicial, posicao1 = cria_mapa()
    x1, y1 = posicao1

    # Salva a posição atual no arquivo entrou.txt
    with open("arquivos/localizacao/entrou.txt", "w") as entrou:
        entrou.write(f"{x1},{y1}")

    alternado = (x1 * 5 + y1) + 1

    if alternado != 12:
        with open("arquivos/localizacao/mapa.txt", "w") as mapa_file:
            mapa_file.write(str(alternado))

        mapa_medio, posicao2 = cria_mapa()

        for i in range(5):
            for j in range(5):
                if mapa_medio[i][j] == "Porta":
                    with open("arquivos/localizacao/posicao.txt", "w") as pos:
                        pos.write(f"{i},{j}")
                    break
            else:
                continue
            break

        mapa, posicao = cria_mapa()
        imprime_mapa(mapa, posicao)
        descreve_lugar()
    else:
        print("Voce não pode sair antes de salvar a rainha e os seus irmãos")


def ganhou():
    inimigos = []
    mortos = []

    with open("arquivos/personagens/mortos.txt", "r") as abatidos:
        m = abatidos.readlines()

    with open("arquivos/personagens/personagens.txt", "r") as personagens:
        p = personagens.readlines()

    for i in p:

        nome = i.split("-")[0].split(":")[1].strip()
        seu = i.split("-")[1]

        if seu == "Inimigo":
            inimigos.append(nome)

    for i in m:
        morto = i.strip()
        mortos.append(morto)

    if len(mortos) == len(inimigos):
        print("Parabens voce ganhou!!!")
        print("Voce salvou seus irmaos e a rainha")
        # Mostra codigo asc de 3 guerreiros e 1 madame
        return True
    else:
        return False


def reseta():
    with open("arquivos/localizacao/posicao.txt", "w") as pos:
        pos.write("2,1")
    with open("arquivos/localizacao/mapa.txt", "w") as mapa:
        mapa.write("0")
    with open("arquivos/interacoes/inventario.txt", "w") as inv:
        inv.write("❤️ ❤️\n")
        inv.write("💥\n")
    with open("arquivos/personagens/mortos.txt", "w"):
        pass


def sair():
    print("Saindo do jogo. Até a próxima!")
    exit()


def jogo():
    with open("arquivos/localizacao/posicao.txt", "w") as pos:
        pos.write("2,1")

    print(
        "\nNo distante Reino de Eldoria, o Castelo da Rainha Raissa, um majestoso e antigo castelo, guarda muitos segredos.\n"
        "A Rainha Raissa, uma governante justa e poderosa, foi aprisionada por um mal antigo que despertou de um sono profundo. \n"
        "Você, um jovem herói, é chamado para explorar o castelo, resgatar seus irmãos Thiago e Yuri, e libertar a Rainha.\n"
        "Cada sala do castelo guarda perigos, enigmas e tesouros, mas também um guardião temível.\n"
        "Apenas os mais corajosos e sagazes poderão sobreviver e triunfar.\n")

    descreve_lugar()
    mapa, posicao = cria_mapa()
    imprime_mapa(mapa, posicao)
    print("\nSabendo que você está na entrada e só pode se movimentar nas direções: Norte, Sul, Leste e Oeste")

    while True:
        menu()


while True:
    jogar = input("Deseja Jogar (S/N): ").strip().lower()

    ganhou = ganhou()

    if jogar == "s" and not ganhou:
        jogo()
    elif jogar == "n" or ganhou:
        print("Obrigado por jogar meu jogo, tchau!")
        exit()
    else:
        print("Por favor, escolha S ou N.")
