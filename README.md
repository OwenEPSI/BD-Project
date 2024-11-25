# BD-Project
import mysql.connector

# Fonction pour établir la connexion à la base de données
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="votre_utilisateur",  # Remplacez par votre utilisateur MySQL
            password="votre_mot_de_passe",  # Remplacez par votre mot de passe MySQL
            database="votre_base_de_donnees"  # Remplacez par le nom de votre base
        )
        print("Connexion réussie à la base de données.")
        return conn
    except mysql.connector.Error as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

# Fonction pour exécuter une requête SQL
def execute_query(conn, query, params=()):
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return None

# Requête : Liste des joueurs par club
def get_joueurs_par_club(conn):
    query = """
        SELECT 
            t_club.nom_club, 
            t_joueur.nom_joueur, 
            t_joueur.prenom_joueur
        FROM 
            t_joueur
        JOIN 
            tj_joueur_equipe ON t_joueur.id_joueur = tj_joueur_equipe.id_joueur
        JOIN 
            t_equipe ON tj_joueur_equipe.id_equipe = t_equipe.id_equipe
        JOIN 
            t_club ON t_equipe.id_club = t_club.id_club
        ORDER BY 
            t_club.nom_club, t_joueur.nom_joueur, t_joueur.prenom_joueur;
    """
    return execute_query(conn, query)

# Requête : Nombre de joueurs dans le club n°1
def get_nombre_joueurs_club_1(conn):
    query = """
        SELECT COUNT(id_joueur) AS nombre_joueurs
        FROM tj_joueur_club
        WHERE id_club = 1;
    """
    return execute_query(conn, query)

# Requête : Équipes participant à la 5ème édition du tournoi
def get_equipes_tournoi_5(conn):
    query = """
        SELECT t_equipe.id_equipe, t_equipe.nom_equipe
        FROM t_equipe
        JOIN tj_inscription ON t_equipe.id_equipe = tj_inscription.id_equipe
        JOIN t_tournoi ON tj_inscription.id_tournoi = t_tournoi.id_tournoi
        WHERE t_tournoi.edition_tournoi = 5;
    """
    return execute_query(conn, query)

# Requête : Total des buts dans le tournoi n°5
def get_total_buts_tournoi_5(conn):
    query = """
        SELECT SUM(t_match.but_equipe1 + t_match.but_equipe2) AS total_buts
        FROM t_match
        JOIN t_tournoi ON t_match.id_tournoi = t_tournoi.id_tournoi
        WHERE t_tournoi.edition_tournoi = 5;
    """
    return execute_query(conn, query)

# Requête : Résultats du tournoi n°5 (classement des équipes)
def get_tournoi_5_results(conn):
    query = """
        SELECT t_club.nom_club AS nom_du_club,
            t_equipe.nom_equipe AS nom_de_l_equipe,
            SUM(CASE 
                WHEN t_match.id_equipe = t_equipe.id_equipe THEN point_equipe1 
                WHEN t_match.id_equipe2 = t_equipe.id_equipe THEN point_equipe2 
                ELSE 0 
            END) AS total_points,
            SUM(CASE 
                WHEN t_match.id_equipe = t_equipe.id_equipe THEN but_equipe1 
                WHEN t_match.id_equipe2 = t_equipe.id_equipe THEN but_equipe2 
                ELSE 0 
            END) AS total_buts
        FROM t_equipe
        JOIN t_club ON t_equipe.id_club = t_club.id_club
        LEFT JOIN t_match ON t_equipe.id_equipe IN (t_match.id_equipe, t_match.id_equipe2)
        JOIN t_tournoi ON t_match.id_tournoi = t_tournoi.id_tournoi
        WHERE t_tournoi.edition_tournoi = 5 
        GROUP BY t_club.nom_club, t_equipe.nom_equipe
        ORDER BY total_points DESC, total_buts DESC;
    """
    return execute_query(conn, query)

# Fonction principale
def main():
    conn = connect_to_db()
    if not conn:
        return

    # Requête 1 : Liste des joueurs par club
    print("\n=== Liste des joueurs par club ===")
    results = get_joueurs_par_club(conn)
    if results:
        for row in results:
            print(f"Club : {row[0]}, Joueur : {row[1]} {row[2]}")
    else:
        print("Aucun résultat trouvé.")

    # Requête 2 : Nombre de joueurs dans le club n°1
    print("\n=== Nombre de joueurs dans le club n°1 ===")
    results = get_nombre_joueurs_club_1(conn)
    if results:
        print(f"Nombre de joueurs : {results[0][0]}")
    else:
        print("Aucun résultat trouvé.")

    # Requête 3 : Équipes participant à la 5ème édition du tournoi
    print("\n=== Équipes participant à la 5ème édition du tournoi ===")
    results = get_equipes_tournoi_5(conn)
    if results:
        for row in results:
            print(f"Équipe ID : {row[0]}, Nom : {row[1]}")
    else:
        print("Aucun résultat trouvé.")

    # Requête 4 : Total des buts dans le tournoi n°5
    print("\n=== Total des buts dans le tournoi n°5 ===")
    results = get_total_buts_tournoi_5(conn)
    if results and results[0][0] is not None:
        print(f"Total des buts : {results[0][0]}")
    else:
        print("Aucun but trouvé.")

    # Requête 5 : Résultats du tournoi n°5
    print("\n=== Résultats du tournoi n°5 ===")
    results = get_tournoi_5_results(conn)
    if results:
        for row in results:
            print(f"Club : {row[0]}, Équipe : {row[1]}, Points : {row[2]}, Buts : {row[3]}")
    else:
        print("Aucun résultat trouvé.")

    # Fermer la connexion
    conn.close()

if __name__ == "__main__":
    main()
