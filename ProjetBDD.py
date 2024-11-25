import sqlite3
from tkinter import *

import mysql.connector
from tkinter import messagebox

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",         # Ou l'adresse IP de votre serveur MySQL
            user="root",  # Votre nom d'utilisateur MySQL
            password="votre_mot_de_passe",  # Votre mot de passe MySQL
            database="TOURNOI"        # Nom de la base de données
        )

        if conn.is_connected():
            print("Connexion réussie à la base de données")
            return conn
        else:
            print("Impossible de se connecter à la base de données")
            return None

    except mysql.connector.Error as err:
        messagebox.showerror("Erreur", f"Erreur de connexion : {err}")
        return None


# Fonction pour exécuter les requêtes
def execute_query(query):
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        display_result(result)
    except Exception as e:
        display_result([("Erreur", str(e))])

# Afficher les résultats dans la zone de texte
def display_result(result):
    result_display.delete("1.0", END)
    if result:
        for row in result:
            result_display.insert(END, f"{row}\n")
    else:
        result_display.insert(END, "Aucun résultat trouvé.\n")

# Requêtes spécifiques
def lister_joueurs_par_club():
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
    execute_query(query)

def compter_joueurs_club_1():
    query = """
    SELECT COUNT(id_joueur) AS nombre_joueurs
    FROM tj_joueur_club
    WHERE id_club = 1;
    """
    execute_query(query)

def lister_equipes_tournoi_5():
    query = """
    SELECT t_equipe.id_equipe, t_equipe.nom_equipe
    FROM t_equipe
    JOIN tj_inscription ON t_equipe.id_equipe = tj_inscription.id_equipe
    JOIN t_tournoi ON tj_inscription.id_tournoi = t_tournoi.id_tournoi
    WHERE t_tournoi.edition_tournoi = 5;
    """
    execute_query(query)

def calculer_total_buts_tournoi_5():
    query = """
    SELECT SUM(t_match.but_equipe1 + t_match.but_equipe2) AS total_buts
    FROM t_match
    JOIN t_tournoi ON t_match.id_tournoi = t_tournoi.id_tournoi
    WHERE t_tournoi.edition_tournoi = 5;
    """
    execute_query(query)

def classement_final_tournoi_5():
    query = """
    SELECT 
        t_club.nom_club AS nom_du_club,
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
    execute_query(query)

# Requête 6 : Met à jour les points et les scores d'un match
def afficher_points_match():
    def confirmer_score():
        try:
            # Récupérer les données saisies
            id_match = int(id_match_var.get())
            but_equipe1 = int(but_equipe1_var.get())
            but_equipe2 = int(but_equipe2_var.get())

            # Requête SQL pour calculer les points en fonction des scores saisis
            select_query = """
            SELECT 
                t_match.id_match,
                t_equipe1.nom_equipe AS equipe1,
                t_equipe2.nom_equipe AS equipe2,
                t_match.but_equipe1,
                t_match.but_equipe2,
                CASE 
                    WHEN t_match.but_equipe1 > t_match.but_equipe2 THEN 3
                    WHEN t_match.but_equipe1 = t_match.but_equipe2 THEN 1
                    ELSE 0
                END AS points_equipe1,
                CASE 
                    WHEN t_match.but_equipe2 > t_match.but_equipe1 THEN 3
                    WHEN t_match.but_equipe1 = t_match.but_equipe2 THEN 1
                    ELSE 0
                END AS points_equipe2
            FROM t_match
            JOIN t_equipe t_equipe1 ON t_match.id_equipe = t_equipe1.id_equipe
            JOIN t_equipe t_equipe2 ON t_match.id_equipe2 = t_equipe2.id_equipe
            WHERE t_match.id_match = ?;
            """

            # Exécution de la requête
            cursor.execute(select_query, (id_match,))
            result = cursor.fetchone()

            # Vérification du résultat
            if result:
                messagebox.showinfo(
                    "Résultat des points",
                    f"Match ID : {result['id_match']}\n"
                    f"Équipe 1 ({result['equipe1']}) : {result['points_equipe1']} points\n"
                    f"Équipe 2 ({result['equipe2']}) : {result['points_equipe2']} points"
                )
            else:
                messagebox.showwarning(
                    "Aucun résultat",
                    f"Aucun match trouvé avec l'ID {id_match}."
                )

            popup.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides pour les scores et l'ID.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # Création du pop-up pour entrer les informations
    popup = Toplevel(root)
    popup.title("Saisir le score d'un match")
    popup.geometry("400x300")

    Label(popup, text="ID du match :").pack(pady=5)
    id_match_var = StringVar()
    Entry(popup, textvariable=id_match_var).pack(pady=5)

    Label(popup, text="Buts Équipe 1 :").pack(pady=5)
    but_equipe1_var = StringVar()
    Entry(popup, textvariable=but_equipe1_var).pack(pady=5)

    Label(popup, text="Buts Équipe 2 :").pack(pady=5)
    but_equipe2_var = StringVar()
    Entry(popup, textvariable=but_equipe2_var).pack(pady=5)

    # Boutons du pop-up
    Button(popup, text="Confirmer", command=confirmer_score, bg="green", fg="white").pack(pady=10)
    Button(popup, text="Annuler", command=popup.destroy, bg="red", fg="white").pack(pady=10)


def club_du_joueur_2():
    query = """
    SELECT t_club.nom_club, tj_joueur_club.date_joueur_rejoin_club, tj_joueur_club.date_joueur_quitte_club
    FROM tj_joueur_club 
    JOIN t_club ON tj_joueur_club.id_club = t_club.id_club 
    WHERE tj_joueur_club.id_joueur = 2;
    """
    execute_query(query)

# Réduire la fenêtre
def minimize_window():
    root.iconify()

# Fermer l'application
def close_app():
    conn.close()
    root.destroy()

# Connexion à la base de données SQLite
conn = sqlite3.connect("TOURNOI.db")
cursor = conn.cursor()

# Interface graphique avec Tkinter
root = Tk()
root.title("Requêtes Tournoi")
root.geometry("800x600")

# Widgets
title_label = Label(root, text="Interface de requêtes SQL : TOURNOI", font=("Arial", 16))
title_label.pack(pady=10)

# Boutons pour les requêtes
Button(root, text="Lister joueurs par club", command=lister_joueurs_par_club, width=30).pack(pady=5)
Button(root, text="Compter joueurs club n°1", command=compter_joueurs_club_1, width=30).pack(pady=5)
Button(root, text="Lister équipes tournoi 5", command=lister_equipes_tournoi_5, width=30).pack(pady=5)
Button(root, text="Calculer buts tournoi 5", command=calculer_total_buts_tournoi_5, width=30).pack(pady=5)
Button(root, text="Classement tournoi 5", command=classement_final_tournoi_5, width=30).pack(pady=5)
Button(root, text="Saisir le score et afficher les points", command=afficher_points_match, width=30).pack(pady=5)
Button(root, text="Club joueur n°2", command=club_du_joueur_2, width=30).pack(pady=5)

# Zone d'affichage des résultats
result_display = Text(root, height=20, width=80, wrap="word", font=("Arial", 12))
result_display.pack(pady=10)

scroll = Scrollbar(root, command=result_display.yview)
result_display.config(yscrollcommand=scroll.set)
scroll.pack(side="right", fill="y")

# Lancer l'application
root.mainloop()
