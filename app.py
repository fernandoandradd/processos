import streamlit as st
import sqlite3


# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('processos.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Função para criar a tabela de processos, se não existir
def create_process_table():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS processos (id INTEGER PRIMARY KEY, nome TEXT UNIQUE)')
    conn.commit()
    conn.close()

# Função para criar tabelas de tópicos para cada processo
def create_topic_table(processo_nome):
    conn = get_db_connection()
    conn.execute(f'CREATE TABLE IF NOT EXISTS "{processo_nome}" (id INTEGER PRIMARY KEY, topico TEXT, concluido BOOLEAN DEFAULT FALSE)')
    conn.commit()
    conn.close()

# Função para atualizar tabelas existentes com a coluna 'concluido'
def update_tables():
    conn = get_db_connection()
    processos = conn.execute('SELECT nome FROM processos').fetchall()
    for processo in processos:
        nome_processo = processo['nome']
        conn.execute(f'ALTER TABLE "{nome_processo}" ADD COLUMN concluido BOOLEAN DEFAULT FALSE')
    conn.commit()
    conn.close()

# Função para adicionar um novo processo
def add_processo(nome):
    conn = get_db_connection()
    conn.execute('INSERT INTO processos (nome) VALUES (?)', (nome,))
    conn.commit()
    conn.close()
    create_topic_table(nome)

# Função para adicionar um tópico a um processo
def add_topico(processo_nome, topico):
    conn = get_db_connection()
    conn.execute(f'INSERT INTO "{processo_nome}" (topico, concluido) VALUES (?, FALSE)', (topico,))
    conn.commit()
    conn.close()

# Função para atualizar o status de um tópico
def update_topico_status(processo_nome, topico_id, status):
    conn = get_db_connection()
    conn.execute(f'UPDATE "{processo_nome}" SET concluido = ? WHERE id = ?', (status, topico_id))
    conn.commit()
    conn.close()

# Função para recuperar todos os processos
def get_processos():
    conn = get_db_connection()
    processos = conn.execute('SELECT * FROM processos').fetchall()
    conn.close()
    return processos

# Função para recuperar tópicos de um processo
def get_topicos(processo_nome):
    conn = get_db_connection()
    topicos = conn.execute(f'SELECT * FROM "{processo_nome}"').fetchall()
    conn.close()
    return topicos

# Função para excluir um processo
def delete_processo(processo_nome):
    conn = get_db_connection()
    conn.execute(f'DROP TABLE IF EXISTS "{processo_nome}"')
    conn.execute('DELETE FROM processos WHERE nome = ?', (processo_nome,))
    conn.commit()
    conn.close()

# Função para excluir um tópico
def delete_topico(processo_nome, topico_id):
    conn = get_db_connection()
    conn.execute(f'DELETE FROM "{processo_nome}" WHERE id = ?', (topico_id,))
    conn.commit()
    conn.close()



# Chamada da função para atualizar as tabelas existentes
# (Descomente a linha abaixo e execute o script uma vez se estiver atualizando o banco de dados existente)
# update_tables()

# Criar tabela de processos
create_process_table()

# Interface Streamlit
st.title('Gerenciamento de Processos Empresariais')

# Adicionando novo processo
st.sidebar.title('Adicionar Novo Processo')
nome_processo = st.sidebar.text_input('Nome do Processo')
if st.sidebar.button('Adicionar Processo'):
    add_processo(nome_processo)

# Selecionar processo para adicionar tópicos
processos = get_processos()
processo_selecionado = st.selectbox('Escolha um Processo', [p['nome'] for p in processos])

# Adicionar tópicos ao processo selecionado
topico = st.text_input('Adicionar novo tópico ao processo')
if st.button(f'Adicionar tópico a {processo_selecionado}'):
    add_topico(processo_selecionado, topico)

# Exibindo tópicos do processo selecionado como checklist
st.header(f'Tópicos do Processo: {processo_selecionado}')
topicos = get_topicos(processo_selecionado)
for topico in topicos:
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        check = st.checkbox(topico['topico'], key=topico['id'], value=topico['concluido'])
        if check != topico['concluido']:
            update_topico_status(processo_selecionado, topico['id'], check)
    with col2:
        if st.button(f'Excluir {topico["id"]}', key=f'del_{topico["id"]}'):
            delete_topico(processo_selecionado, topico['id'])
            st.experimental_rerun()

# Opção para excluir um processo
processo_para_excluir = st.sidebar.selectbox('Escolha um Processo para Excluir', [p['nome'] for p in processos])
if st.sidebar.button(f'Excluir Processo {processo_para_excluir}'):
    delete_processo(processo_para_excluir)
    st.experimental_rerun()

# ... Restante do código ...
