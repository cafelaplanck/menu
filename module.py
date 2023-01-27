#!/usr/bin/env python3.11
# -*- utf-8 -*-
"""
Générer les instructions LaTeX pour le menu de la Planck
"""

import configparser

import pandas

# Pour gérer la feuille de calcul Google
# https://stackoverflow.com/questions/3287651/download-a-spreadsheet-from-google-drive-workspace-using-python
import csv
import gspread # https://github.com/burnash/gspread

from oauth2client.service_account import ServiceAccountCredentials


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
    config.read('menu.config')
    
    produits = télécharger_inventaire(config)
    produits = ajouter_avertissements(produits)
    catégories = condenser(produits)
    catégories = ajouter_café(catégories)
    afficher_catégories(catégories)


if __name__ == '__main__':
    main()
