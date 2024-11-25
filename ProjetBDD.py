import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# Connexion à la base de données MySQL
conn = mysql.connector.connect(
    host="localhost",     # ou l'adresse IP du serveur de base de données
    user="root",
    password="Nassim123",
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
        display_result([f"Erreur : {e}"])

# Afficher les résultats dans une Treeview (tableau)
def display_result(result):
    # Vider la table avant d'afficher de nouveaux résultats
    for row in result_table.get_children():
        result_table.delete(row)
    
    if result:
        # Dynamique : récupérer les colonnes à partir du résultat
        columns = [desc[0] for desc in cursor.description]  # Récupère les noms de colonnes
        result_table["columns"] = columns  # Mettre à jour les colonnes de la Treeview
        for col in columns:
            result_table.heading(col, text=col, anchor="w")
            result_table.column(col, width=150, anchor="w")
        
        # Ajouter les résultats dans la table
        for row in result:
            result_table.insert("", "end", values=row)
    else:
        messagebox.showinfo("Résultat", "Aucun résultat trouvé.")

# Requête pour lister les joueurs par club
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
    SELECT t_joueur.nom_joueur,t_club.nom_club, tj_joueur_club.date_joueur_rejoin_club, tj_joueur_club.date_joueur_quitte_club
    FROM tj_joueur_club 
    JOIN t_club ON tj_joueur_club.id_club = t_club.id_club 
    JOIN t_joueur ON tj_joueur_club.id_club = t_joueur.id_joueur
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
root.geometry("900x700")
root.configure(bg="#f4f6f8")

style = ttk.Style()
style.configure("Treeview",
                font=("Helvetica", 11),
                rowheight=25,
                fieldbackground="#f4f6f8",
                background="#ffffff",
                foreground="#333333")


# Widgets
title_label = Label(root, text="Interface de requêtes SQL : TOURNOI", font=("Arial", 16))
title_label.pack(pady=10)

# Frame pour les boutons
button_frame = Frame(root, bg="#f4f6f8")
button_frame.pack(side="top", pady=20)

Button(root, text="Lister joueurs par club", command=lister_joueurs_par_club, width=30, height=2, bg="#0078D4", fg="white", font=("Helvetica", 12), relief="flat", cursor="hand2").pack(pady=10)
Button(root, text="Compter joueurs club n°1", command=compter_joueurs_club_1, width=30, height=2, bg="#0078D4", fg="white", font=("Helvetica", 12), relief="flat", cursor="hand2").pack(pady=10)
Button(root, text="Lister équipes tournoi 5", command=lister_equipes_tournoi_5, width=30, height=2, bg="#0078D4", fg="white", font=("Helvetica", 12), relief="flat", cursor="hand2").pack(pady=10)
Button(root, text="Calculer buts tournoi 5", command=calculer_total_buts_tournoi_5, width=30, height=2, bg="#0078D4", fg="white", font=("Helvetica", 12), relief="flat", cursor="hand2").pack(pady=10)
Button(root, text="Classement tournoi 5", command=classement_final_tournoi_5, width=30, height=2, bg="#0078D4", fg="white", font=("Helvetica", 12), relief="flat", cursor="hand2").pack(pady=10)
Button(root, text="Afficher points d'un match", command=enregistrer_resultat_match, width=30, height=2, bg="#0078D4", fg="white", font=("Helvetica", 12), relief="flat", cursor="hand2").pack(pady=10)
Button(root, text="Club du joueur 2", command=club_du_joueur_2, width=30, height=2, bg="#0078D4", fg="white", font=("Helvetica", 12), relief="flat", cursor="hand2").pack(pady=10)
# Table pour afficher les résultats
result_table = ttk.Treeview(root, show="headings", height=10)
result_table.pack(pady=10)

# Zone de défilement pour la table
scroll = Scrollbar(root, command=result_table.yview)
result_table.config(yscrollcommand=scroll.set)
scroll.pack(side="right", fill="y")

# Lancer l'application
root.mainloop()
