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

Primeiro execute `db-server.sh`; depois `bib-server.sh` e `cad-server.sh`; e por último, `bib-client.sh` e `cad-client.sh`.  
Caso os scripts sejam executados sem argumentos, intruções sobre seu uso serão impressas.  
O arquivo `teste.sh` já inicia todos os servidores automaticamente. Ele pode servir como exemplo de uso.  

# Uso dos programas
Há um vídeo neste repositório exemplificando como os programas funcionam.

# Funcionalidades não implementadas
A funcionalidade do usuário ser liberado automaticamente quando faz uma devolução, não foi feita. Caso essa funcionalidade
fosse implementada, a função LiberaUsuarios seria inútil, pois não haveria possibilidade de um usuário estar bloqueado
"injustamente", ou seja, LiberaUsuarios sempre retornaria que 0 usuários foram liberados.

# Banco de dados
Os arquivos do banco de dados estão hardcoded para serem salvos no diretório /tmp/db. Certifique-se de que o programa tenha
permissão de escrita nele.