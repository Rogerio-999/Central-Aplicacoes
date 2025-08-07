# Copyright © 2025 Rogerio Gomes Pereira Junior 
# Todos os direitos reservados.

import json
import hashlib
import os
import random
import itertools
import string
import time
import re
import sys
from pathlib import Path

class CentralAplicacoes:
    def __init__(self):
        # Salva o arquivo na pasta Documentos do usuário (sempre tem permissão)
        documentos = Path.home() / "Documents"
        pasta_app = documentos / "CentralAplicacoes"
        
        # Cria a pasta se não existir
        pasta_app.mkdir(exist_ok=True)
        
        self.ARQUIVO_CREDENCIAIS = str(pasta_app / "credenciais.json")
        self.usuario_logado = None
    
    def criar_hash_senha(self, senha):
        """Cria um hash seguro da senha usando SHA-256"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def carregar_credenciais(self):
        """Carrega as credenciais do arquivo JSON"""
        if os.path.exists(self.ARQUIVO_CREDENCIAIS):
            try:
                with open(self.ARQUIVO_CREDENCIAIS, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erro ao carregar credenciais: {e}")
                print("Criando novo arquivo...")
                return {}
        else:
            return {}
    
    def salvar_credenciais(self, credenciais):
        """Salva as credenciais no arquivo JSON"""
        try:
            # Verifica se o diretório existe, se não, cria
            dir_arquivo = os.path.dirname(self.ARQUIVO_CREDENCIAIS)
            if dir_arquivo and not os.path.exists(dir_arquivo):
                os.makedirs(dir_arquivo)
            
            with open(self.ARQUIVO_CREDENCIAIS, 'w', encoding='utf-8') as arquivo:
                json.dump(credenciais, arquivo, indent=2, ensure_ascii=False)
            return True
        except PermissionError:
            print(f"ERRO: Sem permissão para escrever no arquivo de credenciais")
            print("Tente executar como administrador ou verificar as permissões.")
            return False
        except IOError as e:
            print(f"Erro ao salvar credenciais: {e}")
            return False
    
    def validar_senha(self, senha):
        """Valida se a senha atende aos critérios mínimos de segurança"""
        if len(senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."
        
        if not re.search(r'[A-Za-z]', senha):
            return False, "A senha deve conter pelo menos uma letra."
        
        if not re.search(r'\d', senha):
            return False, "A senha deve conter pelo menos um número."
        
        return True, "Senha válida."
    
    def validar_nome_usuario(self, nome):
        """Valida se o nome de usuário atende aos critérios"""
        if len(nome) < 3:
            return False, "O nome de usuário deve ter pelo menos 3 caracteres."
        
        if not re.match(r'^[a-zA-Z0-9_]+$', nome):
            return False, "O nome de usuário pode conter apenas letras, números e underscore."
        
        return True, "Nome de usuário válido."
    
    def cadastro(self):
        """Função para cadastrar novo usuário"""
        credenciais = self.carregar_credenciais()
        
        print("\n=== CADASTRO DE NOVO USUÁRIO ===")
        
        while True:
            nome = input("Escolha um nome de usuário: ").strip()
            
            valido, mensagem = self.validar_nome_usuario(nome)
            if not valido:
                print(f"Erro: {mensagem}")
                continue
            
            if nome.lower() in [user.lower() for user in credenciais.keys()]:
                print("Este nome de usuário já está em uso. Escolha outro.")
                continue
            
            break
        
        while True:
            senha = input("Escolha uma senha: ").strip()
            
            valido, mensagem = self.validar_senha(senha)
            if not valido:
                print(f"Erro: {mensagem}")
                continue
            
            senha2 = input("Confirme a senha: ").strip()
            
            if senha != senha2:
                print("As senhas não coincidem. Tente novamente.")
                continue
            
            break
        
        hash_senha = self.criar_hash_senha(senha)
        credenciais[nome] = {
            "senha": hash_senha,
            "data_criacao": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.salvar_credenciais(credenciais):
            print(f"\nCadastro realizado com sucesso para {nome}!")
            print("Agora você pode fazer login com sua conta.\n")
            return True
        else:
            print("Erro ao salvar o cadastro. Tente novamente.")
            return False
    
    def fazer_login(self, credenciais):
        """Realiza o processo de login"""
        if not credenciais:
            print("Nenhum usuário cadastrado. Faça um cadastro primeiro.")
            return self.login()
        
        tentativas = 3
        
        while tentativas > 0:
            nome = input("\nNome de usuário: ").strip()
            senha = input("Senha: ").strip()
            
            usuario_encontrado = None
            for user in credenciais.keys():
                if user.lower() == nome.lower():
                    usuario_encontrado = user
                    break
            
            if usuario_encontrado and credenciais[usuario_encontrado]["senha"] == self.criar_hash_senha(senha):
                print(f"\nBem-vindo(a), {usuario_encontrado}!")
                self.usuario_logado = usuario_encontrado
                return usuario_encontrado
            else:
                tentativas -= 1
                if tentativas > 0:
                    print(f"Credenciais incorretas. Você tem {tentativas} tentativa(s) restante(s).")
                else:
                    print("Número máximo de tentativas excedido.")
                    return self.login()
        
        return self.login()
    
    def login(self):
        """Função principal de login"""
        credenciais = self.carregar_credenciais()
        
        print("\n=== SISTEMA DE LOGIN ===")
        print("1 - Fazer Login")
        print("2 - Cadastrar novo usuário")
        print("3 - Sair")
        
        try:
            escolha = int(input("\nEscolha uma opção: "))
        except ValueError:
            print("Opção inválida. Digite um número.")
            return self.login()
        
        if escolha == 1:
            return self.fazer_login(credenciais)
        elif escolha == 2:
            if self.cadastro():
                return self.login()
            else:
                return self.login()
        elif escolha == 3:
            print("Saindo do sistema...")
            sys.exit(0)
        else:
            print("Opção inválida.")
            return self.login()
    
    def mostrar_usuarios_cadastrados(self):
        """Função auxiliar para mostrar usuários cadastrados"""
        credenciais = self.carregar_credenciais()
        if credenciais:
            print("\nUsuários cadastrados:")
            for i, (nome, info) in enumerate(credenciais.items(), 1):
                print(f"{i}. {nome} (cadastrado em: {info.get('data_criacao', 'N/A')})")
        else:
            print("Nenhum usuário cadastrado.")
    
    def calculadora(self):
        """Calculadora básica"""
        try:
            number1 = float(input("Digite o primeiro número: "))
            number2 = float(input("Digite o segundo número: "))
        except ValueError:
            print("Digite apenas números válidos!")
            return self.inicio()
        
        soma = number1 + number2
        subtracao = number1 - number2
        multiplicacao = number1 * number2
        divisao = number1 / number2 if number2 != 0 else "Impossível dividir por zero"
        restoDivisao = number1 % number2 if number2 != 0 else "Impossível dividir por zero"
        potenciacao = number1 ** number2
        
        print(f"\nO primeiro número é {'ímpar' if number1 % 2 != 0 else 'par'}")
        print(f"O segundo número é {'ímpar' if number2 % 2 != 0 else 'par'}")
        print(f"Soma: {soma}")
        print(f"Subtração: {subtracao}")
        print(f"Multiplicação: {multiplicacao}")
        print(f"Divisão: {divisao}")
        print(f"Resto da Divisão: {restoDivisao}")
        print(f"Potenciação: {potenciacao}")
        
        self.inicio()
    
    def jogo_adivinhacao(self):
        """Jogo de adivinhação de números"""
        numero_secreto = random.randint(1, 1000)
        tentativas = 0
        
        print("Bem vindo ao jogo da adivinhação!")
        print("Tente adivinhar um número entre 1 e 1000")
        
        while True:
            try:
                escolha = int(input("Digite seu palpite: "))
                tentativas += 1
                
                if escolha < numero_secreto:
                    print("Mais alto!")
                elif escolha > numero_secreto:
                    print("Mais baixo!")
                else:
                    print(f"Parabéns! Você acertou o número {numero_secreto} em {tentativas} tentativas!")
                    break
            except ValueError:
                print("Digite apenas números!")
        
        self.inicio()
    
    def media(self):
        """Calcula média de três notas"""
        try:
            nota1 = float(input("Digite a primeira nota: "))
            nota2 = float(input("Digite a segunda nota: "))
            nota3 = float(input("Digite a terceira nota: "))
        except ValueError:
            print("Digite apenas números válidos!")
            return self.inicio()
        
        media = (nota1 + nota2 + nota3) / 3
        
        if 6 <= media <= 10:
            print(f"Sua média é {media:.2f} - Você está aprovado!")
        else:
            print(f"Sua média é {media:.2f} - Você está reprovado!")
        
        self.inicio()
    
    def numero_impar_par(self):
        """Verifica se um número é par ou ímpar"""
        try:
            number = int(input("Digite um número inteiro: "))
        except ValueError:
            print("Digite apenas números inteiros!")
            return self.inicio()
        
        resultado = "ímpar" if number % 2 != 0 else "par"
        print(f"O número {number} é {resultado}")
        
        self.inicio()
    
    def numeros_loteria(self):
        """Gera números aleatórios para loteria"""
        print("Gerando 6 números da sorte para você:")
        numeros = set()
        
        while len(numeros) < 6:
            numero = random.randint(1, 60)
            numeros.add(numero)
        
        numeros_ordenados = sorted(list(numeros))
        print(f"Seus números da sorte são: {', '.join(map(str, numeros_ordenados))}")
        
        self.inicio()
    
    def quebrador_senhas(self):
        """Demonstração de força bruta (apenas para fins educacionais)"""
        print("AVISO: Esta função é apenas para fins educacionais!")
        print("Não use para quebrar senhas de outras pessoas.")
        
        senha_alvo = input("Digite a senha que você quer testar: ").strip()
        
        if len(senha_alvo) > 4:
            print("Para demonstração, teste apenas senhas de até 4 caracteres.")
            return self.inicio()
        
        caracteres = string.ascii_letters + string.digits
        tentativas = 0
        start_time = time.time()
        
        print("Iniciando teste de força bruta...")
        
        for tamanho in range(1, len(senha_alvo) + 1):
            for tentativa in itertools.product(caracteres, repeat=tamanho):
                tentativa_senha = ''.join(tentativa)
                tentativas += 1
                
                if tentativas % 1000 == 0:
                    print(f"Tentativa #{tentativas}: {tentativa_senha}")
                
                if tentativa_senha == senha_alvo:
                    end_time = time.time()
                    print(f"\nSenha encontrada: {tentativa_senha}")
                    print(f"Tentativas necessárias: {tentativas}")
                    print(f"Tempo decorrido: {end_time - start_time:.2f} segundos")
                    return self.inicio()
        
        self.inicio()
    
    def testador_senhas(self):
        """Testa a força de uma senha"""
        senha = input("Digite sua senha para testar: ")
        
        requisitos = {
            'comprimento': len(senha) >= 8,
            'maiuscula': bool(re.search(r'[A-Z]', senha)),
            'minuscula': bool(re.search(r'[a-z]', senha)),
            'numero': bool(re.search(r'\d', senha)),
            'especial': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', senha))
        }
        
        pontuacao = sum(requisitos.values())
        
        print(f"\nAnálise da senha:")
        print(f"Comprimento >= 8: {'SIM' if requisitos['comprimento'] else 'NÃO'}")
        print(f"Possui maiúscula: {'SIM' if requisitos['maiuscula'] else 'NÃO'}")
        print(f"Possui minúscula: {'SIM' if requisitos['minuscula'] else 'NÃO'}")
        print(f"Possui número: {'SIM' if requisitos['numero'] else 'NÃO'}")
        print(f"Possui caractere especial: {'SIM' if requisitos['especial'] else 'NÃO'}")
        
        if pontuacao == 5:
            forca = "Senha muito forte!"
        elif pontuacao >= 3:
            forca = "Senha forte!"
        elif pontuacao == 2:
            forca = "Senha fraca!"
        else:
            forca = "Senha muito fraca!"
        
        print(f"\nResultado: {forca}")
        
        self.inicio()
    
    def verificacao_vogais(self):
        """Conta vogais em uma frase"""
        sentenca = input("Digite uma frase: ")
        contador_vogais = 0
        
        for letra in sentenca.lower():
            if letra in 'aáãâeéêiíîoóõôuúû':
                contador_vogais += 1
        
        print(f"Total de vogais na frase: {contador_vogais}")
        
        self.inicio()
    
    def inicio(self):
        """Menu principal da aplicação"""
        print(f"\n=== CENTRAL DE APLICAÇÕES - Usuário: {self.usuario_logado} ===")
        print("1 - Sair da Central")
        print("2 - Calculadora")
        print("3 - Jogo de Adivinhação")
        print("4 - Média")
        print("5 - Número ímpar ou par")
        print("6 - Números para loteria")
        print("7 - Quebrador de senhas")
        print("8 - Testador de senhas")
        print("9 - Verificação de vogais")
        print("10 - Trocar de usuário")
        print("11 - Ver usuários cadastrados")
        
        try:
            escolha = int(input("\nEscolha uma opção: "))
        except ValueError:
            print("Digite apenas números!")
            return self.inicio()
        
        opcoes = {
            1: lambda: (print("Encerrando a Central..."), sys.exit(0)),
            2: lambda: (print("\nIniciando calculadora..."), self.calculadora()),
            3: lambda: (print("\nIniciando jogo de adivinhação..."), self.jogo_adivinhacao()),
            4: lambda: (print("\nCalculando média..."), self.media()),
            5: lambda: (print("\nVerificando par/ímpar..."), self.numero_impar_par()),
            6: lambda: (print("\nGerando números da sorte..."), self.numeros_loteria()),
            7: lambda: (print("\nIniciando quebrador de senhas..."), self.quebrador_senhas()),
            8: lambda: (print("\nTestando força da senha..."), self.testador_senhas()),
            9: lambda: (print("\nContando vogais..."), self.verificacao_vogais()),
            10: lambda: (print("\nTrocando de usuário..."), self.executar()),
            11: lambda: (self.mostrar_usuarios_cadastrados(), self.inicio())
        }
        
        if escolha in opcoes:
            opcoes[escolha]()
        else:
            print("Opção inválida!")
            self.inicio()
    
    def hello_world(self):
        """Animação de Hello World"""
        target = "Hello World"
        possible_characters = string.ascii_letters + " "
        result = [""] * len(target)
        
        for i in range(len(target)):
            while True:
                guess = random.choice(possible_characters)
                tentativa = "".join(result[:i]) + guess + "".join("_" for _ in range(i+1, len(target)))
                print(tentativa, end="\r")
                time.sleep(0.02)
                if guess == target[i]:
                    result[i] = guess
                    break
        print("".join(result))
    
    def executar(self):
        """Método principal para executar o programa"""
        print("Copyright © 2025 Rogerio Gomes Pereira Junior")
        print("Todos os direitos reservados.")
        print("Este código é protegido por leis de direitos autorais nacionais e internacionais.")
        print("É proibida sua reprodução, modificação, distribuição ou a aplicação de engenharia reversa sem autorização.\n")
        
        self.hello_world()
        usuario_logado = self.login()
        if usuario_logado:
            self.inicio()

# Execução do programa
if __name__ == "__main__":
    app = CentralAplicacoes()
    app.executar()