#!/usr/bin/env python3.11
# -*- utf-8 -*-
"""
Générer les instructions LaTeX pour le menu de la Planck
"""

import configparser
import pathlib

import pandas

# Pour gérer la feuille de calcul Google
# https://stackoverflow.com/questions/3287651/download-a-spreadsheet-from-google-drive-workspace-using-python
import csv
import gspread # https://github.com/burnash/gspread

from oauth2client.service_account import ServiceAccountCredentials


def initialiser_configuration():
    'Cherche un fichier de configuration à différents endroits, et en crée un au besoin.'
    par_défaut = [pathlib.Path('~/.config/menu_planck/menu_planck.config').expanduser(),
                  pathlib.Path('menu_planck.config')]
    
    for nom in par_défaut:
        if nom.exists():
            return nom
    
    nom = par_défaut[0]
    for chemin in nom.parents:
        if not chemin.exists():
            chemin.mkdir()
    
    configuration = configparser.ConfigParser()
    
    print('Configuration de base. Pour bien comprendre les paramètres, assurez-vous d\'avoir lu `Readme.md` avant de procéder.')
    continuer = input('Continuer? [o|n]') == 'o'
    
    print('Il faut obtenir une clé de service en format JSON, pour utiliser l\'API de Google et télécharger automatiquement le menu. Procéder à l\'adresse https://console.developers.google.com/apis/credentials/serviceaccountkey .')
    clé_de_service = pathlib.Path(input('Fichier JSON de clé de service:'))
    with clé_de_service.open('r', encoding='utf-8') as fichier_initial:
        clé = fichier_initial.read()
    
    chemin_clé = nom.parent / clé_de_service.name
    with chemin_clé.open('w', encoding='utf-8') as fichier_final:
        fichier_final.write(clé)
    
    configuration.add_section('google')
    configuration['google']['credentials'] = str(chemin_clé)
    
    print('Il faut aussi l\'adresse du tableur Google.')
    adresse = input('Adresse du document:')
    
    # Lien typique
    # https://docs.google.com/spreadsheets/d/1ZHSPzywfGYVS4Y6xGfwe3T9-VhZQrgsfcKQnPx0lcvE/edit?usp=sharing
    docid = adresse.split('://', 1)[1].split('/', 4)[3]
    
    configuration.add_section('document')
    configuration['document']['id'] = docid
    
    feuille = input('Nom de la feuille de calcul:')
    configuration['document']['feuille'] = feuille
    
    with nom.open('w', encoding='utf-8') as fichier_final:
        configuration.write(fichier_final)
    
    print(f'La configuration a été écrite à {nom}')
    
    return nom


def télécharger_inventaire(config: dict[dict]) -> pandas.DataFrame:
    # Tiré de https://stackoverflow.com/a/18296318
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(config['google']['credentials'], scope)
    docid = config['document']['id']
    
    client = gspread.authorize(credentials)
    tableur = client.open_by_key(docid)
    feuille = tableur.worksheet(config['document']['feuille'])
    produits = pandas.DataFrame(feuille.get_all_records())
    produits.loc[:, 'unit'] = r'\$'
    
    return produits

def ajouter_avertissements(produits: pandas.DataFrame) -> pandas.DataFrame:
    # https://www.quebec.ca/sante/alimentation/allergies-alimentaires/allergenes-differentes-appellations/
    avertissements = {'lait': r'\emoji{glass-of-milk}',  #'🥛',
                    'noix': r'\emoji{peanuts}',  #'🥜',
                    'gluten': r'\emoji{sheaf-of-rice}',  #'🌾',
                    'moutarde': r'\moutarde',  #'⚠️',
                    'sésame': r'\sesame',  #'⚠️',
                    'oeufs': r'\emoji{egg}',  #'🥚',
                    'poisson': r'\emoji{fish}',  #'🐟',
                    'soja': r'\soja',  #'⚠️',
                    'sulfites': r'\sulfites',  #'⚠️',
                    'végé': r'\emoji{seedling}',  #'🌱',
                    'autres': r'\emoji{warning}'}  #'⚠️'

    for avertissement, symbole in avertissements.items():
        if avertissement == 'autres':
            produits.loc[:, avertissement] = produits.loc[:, avertissement]\
                .fillna(False)\
                .map(bool)\
                .astype(bool)\
                .map(lambda x: symbole if x else '')
        else:
            produits.loc[:, avertissement] = produits.loc[:, avertissement]\
                .replace('', 0)\
                .fillna(0)\
                .map(int)\
                .astype(bool)\
                .map(lambda x: symbole if x else '')
    
    # Condenser les avertissements
    produits.loc[:, 'avertissements'] = produits.loc[:, list(avertissements.keys())]\
        .apply(lambda x: ''.join(x), axis=1)
        
    return produits

def condenser(produits: pandas.DataFrame) -> dict[pandas.DataFrame]:
    subs = {cat: produits.loc[produits.cat == cat, ['prod', 'prix', 'unit', 'avertissements']]
        for cat in produits.cat.unique()}
    
    return subs

def ajouter_café(catégories: dict[pandas.DataFrame]) -> dict[pandas.DataFrame]:
    café = catégories['Café']
    équations = {'Espresso': r'$\bra{\text{\emoji{coffee}}}$',
                'Double': r'$\bra{\text{\emoji{coffee}\emoji{coffee}}}$',
                'Allongé': r'$\bra{\text{\emoji{coffee}\emoji{coffee}}}$',
                'Latte': r'$\bra{\ket{\emoji{glass-of-milk}}}$',
                'Capuccino': r'$\ket{\text{\emoji{chocolate}}}$'}
    café.loc[:, 'prod'] = café.loc[:, 'prod'].map(lambda x: équations[x] if x in équations else x)
    
    return catégories

def afficher_catégories(subs: dict[pandas.DataFrame]):
    for cat, sub in subs.items():
        sub = sub.set_index('prod')\
                .loc[:, ['prix', 'unit', 'avertissements']]
                
    
        print(r'\section*{', cat, '}')
        print(sub.to_latex(column_format='lSll',
                        bold_rows=True,
                        header=False,
                        index_names=False,
                        escape=False))
        print(r'\switchcolumn')

def main():
    config = configparser.ConfigParser()
    
    nom_config = initialiser_configuration()
    config.read(nom_config)
    
    produits = télécharger_inventaire(config)
    produits = ajouter_avertissements(produits)
    catégories = condenser(produits)
    catégories = ajouter_café(catégories)
    afficher_catégories(catégories)


if __name__ == '__main__':
    main()
