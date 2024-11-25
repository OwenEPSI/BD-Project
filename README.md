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

# Requête spécifique pour le tournoi n°5
def get_tournoi_5_results(conn):
    query = """
        SELECT  t_club.nom_club AS nom_du_club,
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

    print("\n=== Résultats du tournoi n°5 ===")
    results = get_tournoi_5_results(conn)
    if results:
        print("Club | Équipe")
        for row in results:
            print(f"{row[0]} | {row[1]}")
    else:
        print("Aucun résultat trouvé.")
    
    # Fermer la connexion
    conn.close()

if __name__ == "__main__":
    main()
