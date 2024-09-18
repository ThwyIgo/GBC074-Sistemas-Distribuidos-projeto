# Intruções de compilação
Assume-se que o ambiente tenha suporte a POSIX sh, siga o FHS, ferramentas equivalentes a coreutils e o Python 3.11 ou superior estejam instalados.  
Basta executar: `./compile.sh`  
Há instruções extras no arquivo de script para debug.  

# Execução
ATENÇÃO: Os scripts que executam os clientes e servidores usam a versão
instalada do projeto no virtualenv do Python, portanto execute `./compile.sh`
para atualizar o código que será executado.  
Enquanto o projeto está em desenvolvimento, é recomendado instalá-lo de forma
editável. Isso pode ser feito com o comando `./compile.sh dev`, assim, as
alterações no código fonte serão refletidas diretamente no projeto instalado e
os scripts de execução poderão ser utilizados com uma menor margem para erros.  
É necessário iniciar o mosquitto manualmente antes de executar os scripts,
exceto o compile.sh.  

# JSONs utilizados
Foi utilizado um campo "remetente" para que um servidor possa identificar uma mensagem que ele mesmo pulicou e assim não fazer operações repetidas.  
Para sincronização de Usuários entre servidores de cadastro:  
```json
{
    "remetente": int,
    "cpf": string,
    "nome": string,
    "bloqueado": bool
}
```
Para sincronização de Livros entre servidores de cadastro:  
```json
{
    "remetente": int,
    "isbn": string,
    "titulo": string,
    "autor": string,
    "total": int
}
```