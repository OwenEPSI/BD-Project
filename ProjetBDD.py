import mysql.connector
from tkinter import *
from tkinter import messagebox

# Connexion MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nassim123",  # Assurez-vous de mettre à jour le mot de passe ici
    database="coupe_amitie"
)

cursor = conn.cursor()

# Fonction pour exécuter les requêtes
def execute_query(query):
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        display_result(result)
    except Exception as e:
        display_result([f"Erreur MySQL : {e}"])

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
    ORDER BY total_points , total_buts ;
    """
    execute_query(query)

# Requête 6 : Met à jour les points et les scores d'un match
def enregistrer_resultat_match():
    def confirmer_score():
        try:
            # Récupérer les données saisies
            id_match = int(id_match_var.get().strip())
            but_equipe1 = int(but_equipe1_var.get().strip())
            but_equipe2 = int(but_equipe2_var.get().strip())

            # Calculer les points pour chaque équipe
            if but_equipe1 > but_equipe2:
                point_equipe1 = 3
                point_equipe2 = 0
            elif but_equipe1 < but_equipe2:
                point_equipe1 = 0
                point_equipe2 = 3
            else:
                point_equipe1 = 1
                point_equipe2 = 1

            # Mettre à jour les scores et les points dans la base de données
            update_query = """
            UPDATE t_match
            SET 
                but_equipe1 = %s,
                but_equipe2 = %s,
                point_equipe1 = %s,
                point_equipe2 = %s
            WHERE id_match = %s;
            """

            # Exécution de la mise à jour
            cursor.execute(update_query, (but_equipe1, but_equipe2, point_equipe1, point_equipe2, id_match))
            conn.commit()

            # Afficher un message de confirmation
            messagebox.showinfo(
                "Résultat du match",
                f"Match ID : {id_match}\n"
                f"Équipe 1 : {but_equipe1} buts, {point_equipe1} points\n"
                f"Équipe 2 : {but_equipe2} buts, {point_equipe2} points"
            )
            popup.destroy()

        except ValueError:
            messagebox.showerror("Erreur", "Les valeurs saisies doivent être des entiers.")
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

# Interface graphique avec Tkinter
root = Tk()
root.title("Requêtes Tournoi")
root.geometry("800x600")

# Widgets
title_label = Label(root, text="Interface de requêtes SQL : TOURNOI", font=("Arial", 16))
title_label.pack(pady=10)

# Boutons pour les requêtes
button_frame = Frame(root)
button_frame.pack(side="top", pady=10)

Button(root, text="Lister joueurs par club", command=lister_joueurs_par_club, width=30).pack(pady=5)
Button(root, text="Compter joueurs club n°1", command=compter_joueurs_club_1, width=30).pack(pady=5)
Button(root, text="Lister équipes tournoi 5", command=lister_equipes_tournoi_5, width=30).pack(pady=5)
Button(root, text="Calculer buts tournoi 5", command=calculer_total_buts_tournoi_5, width=30).pack(pady=5)
Button(root, text="Classement final tournoi 5", command=classement_final_tournoi_5, width=30).pack(pady=5)
Button(root, text="Afficher points d'un match", command=enregistrer_resultat_match, width=30).pack(pady=5)
Button(root, text="Club du joueur 2", command=club_du_joueur_2, width=30).pack(pady=5)

# Zone d'affichage des résultats
result_display = Text(root, width=100, height=15)
result_display.pack(pady=10)

# Fenêtre avec des boutons pour minimiser et fermer
bottom_frame = Frame(root)
bottom_frame.pack(side="bottom", pady=10)

Button(bottom_frame, text="Minimiser", command=minimize_window).pack(side="left", padx=10)
Button(bottom_frame, text="Quitter", command=close_app).pack(side="left", padx=10)

# Lancer l'application
root.mainloop()

# Ne pas oublier de fermer la connexion à la base de données
conn.close()
