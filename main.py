import numpy as np
import pandas as pd
from scipy.linalg import svd
import streamlit as st

# Carregar dados dos arquivos CSV
movies_df = pd.read_csv('data/movies.csv')  # Arquivo com informações dos filmes
ratings_df = pd.read_csv('data/ratings.csv')  # Arquivo com avaliações dos usuários

# Criar dicionários para mapear IDs para nomes
movies_dict = dict(zip(movies_df['movieId'], movies_df['title']))
users = ratings_df['userId'].unique()
users_dict = {user_id: f"Usuário {user_id}" for user_id in users}

# Criar um mapeamento de movieId para um índice sequencial
movie_id_to_index = {movie_id: idx for idx, movie_id in enumerate(movies_dict.keys())}

# Criar matriz de avaliações
n_users = len(users)
n_movies = len(movie_id_to_index)  # Corrigido para refletir apenas os filmes presentes nas avaliações
R = np.full((n_users, n_movies), np.nan)  # Matriz esparsa inicializada com NaN

# Preencher a matriz R com as avaliações
for _, row in ratings_df.iterrows():
    user_index = int(row['userId']) - 1  # IDs dos usuários começam em 1, ajustamos para índice 0
    movie_id = int(row['movieId'])

    if movie_id in movie_id_to_index:
        movie_index = movie_id_to_index[movie_id]

        # Verifica se os índices estão dentro dos limites da matriz
        if 0 <= user_index < n_users and 0 <= movie_index < n_movies:
            R[user_index, movie_index] = row['rating']
        else:
            print(f"Índices fora do limite -> user_index: {user_index}, movie_index: {movie_index}")

# Preencher valores faltantes com a média das avaliações de cada filme
movie_means = np.nanmean(R, axis=0)
movie_means = np.where(np.isnan(movie_means), 0, movie_means)  # Substituir NaN por 0
R_filled = np.where(np.isnan(R), movie_means, R)

# Garantir que não há mais NaN ou Inf
R_filled = np.nan_to_num(R_filled, nan=0.0, posinf=0.0, neginf=0.0)

# Verificar se a matriz está limpa antes de aplicar o SVD
if np.isnan(R_filled).any() or np.isinf(R_filled).any():
    print("Erro: Ainda há NaNs ou Infs na matriz!")
    print("Número de NaNs:", np.isnan(R_filled).sum())
    print("Número de Infs:", np.isinf(R_filled).sum())
else:
    # Aplicar SVD
    U, sigma, Vt = svd(R_filled, full_matrices=False)
    sigma = np.diag(sigma)

    # Reconstruir a matriz de previsões
    R_predicted = np.dot(np.dot(U, sigma), Vt)

    # Função de recomendação
    def recommend_movies(user_id, R_predicted, movies_dict, movie_id_to_index, n_recommendations=5):
        user_index = user_id - 1  # Ajuste para índice baseado em zero
        if user_index >= R_predicted.shape[0]:  # Verifica se o usuário existe
            print(f"Erro: usuário {user_id} não encontrado na matriz.")
            return []

        user_ratings = R_predicted[user_index]
        top_movie_indices = np.argsort(user_ratings)[::-1][:n_recommendations]

        # Reverter o índice para movieId original
        index_to_movie_id = {idx: movie_id for movie_id, idx in movie_id_to_index.items()}
        recommended_movies = [(index_to_movie_id[movie_idx], movies_dict[index_to_movie_id[movie_idx]])
                              for movie_idx in top_movie_indices if movie_idx in index_to_movie_id]

        return recommended_movies

    # Dashboard com Streamlit
    st.title("FilmForge")

    # Selecionar usuário
    user_id = st.selectbox("Selecione o usuário", list(users_dict.keys()), format_func=lambda x: users_dict[x])

    # Gerar recomendações
    recommended_movies = recommend_movies(user_id, R_predicted, movies_dict, movie_id_to_index)

    # Exibir recomendações
    st.write(f"Recomendações para {users_dict[user_id]}:")
    for movie_id, movie_name in recommended_movies:
        st.write(f"Filme: {movie_name} (ID: {movie_id})")
