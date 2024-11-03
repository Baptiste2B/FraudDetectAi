# Guide de Déploiement pour FraudDetectAI

## Pré-requis

1. **Docker** :
   - Assurez-vous que Docker est installé et en cours d’exécution sur votre machine. [Télécharger Docker](https://www.docker.com/products/docker-desktop).

2. **Python 3.11** (si vous démarrez l'application sans Docker) :
   - [Télécharger Python 3.11](https://www.python.org/downloads/).
   - Assurez-vous que `uvicorn` est installé : `pip install uvicorn`.

3. **Variables d’Environnement** :
   Créez un fichier `.env` dans le répertoire racine du projet pour y stocker les variables d'environnement suivantes :
   ALLOWED_HOSTS=0.0.0.0,127.0.0.1

4. **Ajouter le répertoire GIT (GitHub)**:
   git clone https://github.com/username/repository-name.git
   cd repository-name

5. **Effectuer les tests unitaires** :
```bash
python manage.py test
```

## Commandes utiles pour Docker
1. 	•	Accéder au conteneur en cours d’exécution :
2.	•	Arrêter tous les conteneurs Docker :
3. 	•	Relancer l’application avec des modifications (si le code a changé) :
```bash
docker exec -it <container_id> /bin/bash
docker stop $(docker ps -q)
docker-compose up --build
```