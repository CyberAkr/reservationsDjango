# catalogue/utils.py
def admin_check(user):
    return user.is_staff  # Vérifie si l'utilisateur est un administrateur
