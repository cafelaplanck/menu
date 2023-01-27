# Générer automatiquement le menu de la Planck

Ce programme génère le menu de la Planck automatiquement, à partir de l'inventaire en ligne de la Planck.
Le programme est disponible sur Github, au https://github.com/cafelaplanck/menu.git .

## Prérequis
- Un [environnement](https://docs.python.org/3/library/venv.html) [Python 3.10+](https://www.python.org/downloads/) situé à `~/env/planck`
- Une installation [TeXLive](https://tug.org/texlive/) à jour

### Choses qui facilite le travail
- Une ligne de commande `shell`
- L'éditeur TeXWorks ou TeXShop, qui permettent de facilement configurer les scripts de compilation

## Autorisations pour télécharger la feuille de calcul
Pour pouvoir télécharger automatiquement la feuille de calcul, il faut obtenir un fichier JSON d'authentification à la page https://console.developers.google.com/apis/credentials/serviceaccountkey . Spécifiquement, il faut:

1. Se connecter au https://console.developers.google.com/apis/credentials/serviceaccountkey
2. Créer un projet «Planck»
3. Créer un compte «Planck» dans le projet
4. Créer une clé de service dans le compte, et la télécharger.
5. Changer la valeur de `[google] credentials` dans le fichier de configuration `menu.config` .
6. Spécifiquement activer l'API Google SHeets pour le projet.

## Configuration

### Fichier de configuration
À la première exécution, le programme vous guidera dans la configuration. Un document de configuration sera créé dans le dossier `~/.config/menu_planck`.

### Polices de caractères
Les polices de caractère dans le fichier suivant sont nécessaires: https://drive.google.com/drive/folders/1lvF58KR9Gv161QGD-_1RA-ZZVsnX1Ax_?usp=share_link . Le fichier est à accès contrôlé à cause des licenses des polices. Elles peuvent aussi être obtenues ou paramétrées dans `preambule.tex`.

## Exécuter le programme
Sur Linux, UNIX, MacOS ou les dérivés, il suffit d'exécuter `source Planck.engine modele-affiche.tex` pour recompiler le PDF. Le programme

1. Compile `modele-affiche.tex` une première fois,
2. Exécute PythonTeX (voir `module.py`)
3. Et recompile `modele-affiche.tex` une seconde fois, avec le contenu généré automatiquement.

Le programme `module.py` télécharge automatiquement la version à jour du menu à partir du Google Drive de la Planck, d'où l'importance de bien obtenir les autorisations de téléchargement de la feuille de calcul.

## Pour forcer la compilation
Exécuter le script `nettoyer.zsh`, qui efface les fichiers de sortie et auxiliaires de LaTeX et Python.
