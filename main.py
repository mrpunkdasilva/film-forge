import pandas as pd
import streamlit as st
import os
import hashlib
import numpy as np
from scipy.linalg import svd


# Caminhos dos arquivos
data_dir = 'data'
users_file = os.path.join(data_dir, 'users.csv')
ratings_file = os.path.join(data_dir, 'user_ratings.csv')
movies_file = os.path.join(data_dir, 'movies.csv')
forum_file = os.path.join(data_dir, 'forum_messages.csv')

# Criar diretório de dados se não existir
os.makedirs(data_dir, exist_ok=True)

# Criar arquivos vazios se não existirem
if not os.path.exists(users_file):
    pd.DataFrame(columns=["username", "password"]).to_csv(users_file, index=False)
if not os.path.exists(ratings_file):
    pd.DataFrame(columns=["username", "movieId", "rating"]).to_csv(ratings_file, index=False)
if not os.path.exists(forum_file):
    pd.DataFrame(columns=["username", "message"]).to_csv(forum_file, index=False)


# Carregar dados
movies_df = pd.read_csv(movies_file)
ratings_df = pd.read_csv(ratings_file)
forum_df = pd.read_csv(forum_file)

# Criar dicionário de filmes
movies_dict = dict(zip(movies_df['movieId'], movies_df['title']))
movie_id_to_index = {movie_id: idx for idx, movie_id in enumerate(movies_dict.keys())}

# Função para hash de senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Função para carregar usuários
def load_users():
    return pd.read_csv(users_file)

# Registrar usuário
def register_user(username, password):
    users_df = load_users()
    if username in users_df["username"].values:
        return False
    hashed_password = hash_password(password)
    new_user = pd.DataFrame([[username, hashed_password]], columns=["username", "password"])
    new_user.to_csv(users_file, mode='a', header=False, index=False)
    return True

# Verificar credenciais
def check_credentials(username, password):
    users_df = load_users()
    hashed_password = hash_password(password)
    return any((users_df["username"] == username) & (users_df["password"] == hashed_password))

# Função para carregar avaliações
def load_user_ratings():
    return pd.read_csv(ratings_file)

# Salvar avaliação
def save_user_rating(username, movie_id, rating):
    user_ratings_df = load_user_ratings()
    new_rating = pd.DataFrame([[username, movie_id, rating]], columns=["username", "movieId", "rating"])
    user_ratings_df = pd.concat([user_ratings_df, new_rating], ignore_index=True)
    user_ratings_df.to_csv(ratings_file, index=False)

# Salvar mensagem no fórum
def save_forum_message(username, message):
    forum_df = pd.read_csv(forum_file)
    new_message = pd.DataFrame([[username, message]], columns=["username", "message"])
    forum_df = pd.concat([forum_df, new_message], ignore_index=True)
    forum_df.to_csv(forum_file, index=False)

# Interface de Login
st.title("FilmForge")

# Variável para controlar o login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")

    # Tentar logar
    if st.sidebar.button("Entrar"):
        if check_credentials(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.sidebar.success(f"Bem-vindo, {username}!")
        else:
            st.sidebar.error("Usuário ou senha incorretos")

    # Registrar novo usuário
    if st.sidebar.button("Registrar"):
        if register_user(username, password):
            st.sidebar.success("Usuário registrado com sucesso!")
        else:
            st.sidebar.error("Usuário já existe!")

    st.stop()  # Impede que o conteúdo após a tela de login seja carregado até o login ser feito.

# Quando o usuário estiver logado, continuar com a navegação
username = st.session_state['username']
st.sidebar.success(f"Bem-vindo, {username}!")

# Navegação
st.sidebar.title("Navegação")
page = st.sidebar.radio("Escolha uma opção", ["Recomendações", "Avaliar Filmes", "Histórico", "Fórum"])

# Criar matriz de avaliações
n_movies = len(movie_id_to_index)
R = np.full((1, n_movies), np.nan)
for _, row in ratings_df.iterrows():
    if row['movieId'] in movie_id_to_index:
        movie_index = movie_id_to_index[row['movieId']]
        R[0, movie_index] = row['rating']

# Preencher valores faltantes
movie_means = np.nanmean(R, axis=0)
R_filled = np.where(np.isnan(R), movie_means, R)

# Verificar e tratar NaNs ou Infs na matriz R_filled
if np.any(np.isnan(R_filled)) or np.any(np.isinf(R_filled)):
    # Substituindo NaNs e Infs por zeros ou pela média (como preferir)
    R_filled = np.nan_to_num(R_filled, nan=0.0, posinf=0.0, neginf=0.0)

# Aplicar SVD
U, sigma, Vt = svd(R_filled, full_matrices=False)
sigma = np.diag(sigma)
R_predicted = np.dot(np.dot(U, sigma), Vt)

# Função de recomendação
def recommend_movies(R_predicted, movies_dict, movie_id_to_index, n_recommendations=5):
    user_ratings = R_predicted[0]
    top_movie_indices = np.argsort(user_ratings)[::-1][:n_recommendations]
    index_to_movie_id = {idx: movie_id for movie_id, idx in movie_id_to_index.items()}
    return [(index_to_movie_id[movie_idx], movies_dict[index_to_movie_id[movie_idx]]) for movie_idx in top_movie_indices if movie_idx in index_to_movie_id]

# Interface principal
if page == "Recomendações":
    st.subheader(f"Recomendações para {username}")
    recommended_movies = recommend_movies(R_predicted, movies_dict, movie_id_to_index)
    for movie_id, movie_name in recommended_movies:
        st.write(f"🎬 {movie_name} (ID: {movie_id})")

elif page == "Avaliar Filmes":
    st.subheader("Avalie um Filme")
    selected_movie = st.selectbox("Escolha um filme", list(movies_dict.keys()), format_func=lambda x: movies_dict[x])
    rating = st.slider("Nota (0.5 a 5.0)", 0.5, 5.0, step=0.5)

    if st.button("Salvar Avaliação"):
        save_user_rating(username, selected_movie, rating)
        st.success("Avaliação salva com sucesso!")

elif page == "Histórico":
    st.subheader("Suas Avaliações")
    user_ratings_df = load_user_ratings()
    user_history = user_ratings_df[user_ratings_df["username"] == username]
    if user_history.empty:
        st.info("Você ainda não avaliou nenhum filme.")
    else:
        st.table(user_history)

elif page == "Fórum":
    st.subheader("Fórum")
    st.write("Aqui você pode ver as mensagens de outros usuários e postar a sua.")

    # Exibir mensagens do fórum
    if forum_df.empty:
        st.info("Ainda não há mensagens no fórum.")
    else:
        for idx, row in forum_df.iterrows():
            st.write(f"**{row['username']}**: {row['message']}")

    # Enviar nova mensagem
    new_message = st.text_area("Poste uma nova mensagem:")
    if st.button("Postar"):
        if new_message:
            save_forum_message(username, new_message)
            st.success("Mensagem postada com sucesso!")
        else:
            st.warning("Digite uma mensagem antes de postar.")