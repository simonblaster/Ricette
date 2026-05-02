#!/usr/bin/env python3
"""Aggiunge 50 Kalò di Ciro Salvo a menu_pizzerie.json."""

import json, os

BASE = os.path.expanduser("~/Documents/Claude/Projects/Ricette")
DB   = os.path.join(BASE, "menu_pizzerie.json")

FONTE = "Ciro Salvo — 50 Kalò, Londra"

nuova_pizzeria = {
    "nome": "50 Kalò",
    "citta": "Londra",
    "maestro": "Ciro Salvo",
    "stile": "Napoletana",
    "note_menu": "Menu della sede londinese di 50 Kalò di Ciro Salvo (marzo 2026). Impasto napoletano con pomodoro San Marzano DOP Casa Marrazzo e olio EVO Colline Salernitane come fil rouge.",
    "pizze": [
        # ── LE PIZZE ──────────────────────────────────────────────────────
        {
            "nome": "Marinara",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "aglio", "origano", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["vegetariana", "vegana", "senza-mozzarella", "classica"],
            "note": ""
        },
        {
            "nome": "Marinara Rinforzata",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "alici del Mediterraneo", "olive taggiasche nere", "capperi", "aglio", "origano", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["senza-mozzarella", "pesce"],
            "note": ""
        },
        {
            "nome": "Cosacca",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "Parmigiano DOP 24 mesi", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["vegetariana", "senza-mozzarella", "classica"],
            "note": ""
        },
        {
            "nome": "Margherita",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "fior di latte", "Parmigiano DOP 24 mesi", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["vegetariana", "classica"],
            "note": ""
        },
        {
            "nome": "Margherita con Bufala",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "mozzarella di bufala", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["vegetariana", "classica"],
            "note": ""
        },
        {
            "nome": "Pomodorini e Scaglie di Parmigiano",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodorini freschi", "fior di latte", "Parmigiano DOP 24 mesi a scaglie", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["vegetariana"],
            "note": ""
        },
        {
            "nome": "Margherita Scarpariello",
            "categoria": "Le Pizze",
            "ingredienti": ["salsa di pomodorini alla scarpariello", "fior di latte", "Parmigiano DOP 24 mesi", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["vegetariana", "new"],
            "note": ""
        },
        {
            "nome": "Cacio e Pepe",
            "categoria": "Le Pizze",
            "ingredienti": ["mozzarella di bufala", "Pecorino Fiore Sardo DOP", "pepe nero", "stracciatella pugliese", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": ["vegetariana"],
            "note": ""
        },
        {
            "nome": "La Mia Provola e Pepe",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "provola affumicata", "pepe nero", "Pecorino Fiore Sardo DOP", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["vegetariana", "new"],
            "note": ""
        },
        {
            "nome": "Quattro Formaggi",
            "categoria": "Le Pizze",
            "ingredienti": ["fior di latte", "formaggio di capra in botti di vino", "formaggio vaccino stagionato in paglia", "chips di Parmigiano DOP 24 mesi", "fonduta Selva Blue", "pomodorini confit", "basilico"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": ["vegetariana", "new"],
            "note": ""
        },
        {
            "nome": "Prosciutto Cotto e Parmigiano",
            "categoria": "Le Pizze",
            "ingredienti": ["base bianca", "fior di latte", "prosciutto cotto", "Parmigiano DOP 24 mesi", "olio EVO Colline Salernitane"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": [],
            "note": ""
        },
        {
            "nome": "Del Monaco DOP",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "fior di latte", "salame Napoli", "Provolone del Monaco DOP a scaglie", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": [],
            "note": ""
        },
        {
            "nome": "Diavola",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "salame piccante morbido", "fior di latte", "Parmigiano DOP 24 mesi", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["piccante"],
            "note": ""
        },
        {
            "nome": "Nduja e Stracciata",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "'nduja", "stracciatella pugliese", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["piccante"],
            "note": ""
        },
        {
            "nome": "Bufala e Fiocco",
            "categoria": "Le Pizze",
            "ingredienti": ["base bianca", "mozzarella di bufala", "prosciutto di Parma 24 mesi", "olio EVO Colline Salernitane"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": [],
            "note": ""
        },
        {
            "nome": "Bianca Prosciutto e Funghi Cardoncelli",
            "categoria": "Le Pizze",
            "ingredienti": ["base bianca", "fior di latte", "prosciutto cotto", "funghi cardoncelli saltati", "olio EVO Colline Salernitane"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": [],
            "note": ""
        },
        {
            "nome": "Capricciosa",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodoro San Marzano DOP", "fior di latte", "salame Napoli", "carciofi al forno", "funghi cardoncelli saltati", "Parmigiano DOP 24 mesi", "Pecorino", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["classica"],
            "note": ""
        },
        {
            "nome": "Salsicce e Patate",
            "categoria": "Le Pizze",
            "ingredienti": ["base bianca", "fior di latte", "salsiccia fresca italiana", "patate al forno"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": [],
            "note": ""
        },
        {
            "nome": "Salsiccia e Friarielli",
            "categoria": "Le Pizze",
            "ingredienti": ["base bianca", "fior di latte", "salsiccia fresca italiana", "friarielli", "olio EVO Colline Salernitane"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": ["napoletana"],
            "note": ""
        },
        {
            "nome": "Tonno e Cipolla",
            "categoria": "Le Pizze",
            "ingredienti": ["pomodorini freschi", "filetti di tonno del Mediterraneo", "fior di latte", "cipolla rossa", "olio EVO Colline Salernitane"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["pesce"],
            "note": ""
        },
        {
            "nome": "Carciofi e Bresaola",
            "categoria": "Le Pizze",
            "ingredienti": ["base bianca", "fior di latte", "cuori di carciofo al forno", "bresaola Black Angus", "Parmigiano DOP 24 mesi a scaglie", "olio EVO Colline Salernitane"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": [],
            "note": ""
        },
        {
            "nome": "Genovese",
            "categoria": "Le Pizze",
            "ingredienti": ["base bianca", "ragù di manzo e cipolle alla genovese", "fior di latte", "Parmigiano DOP 24 mesi", "basilico"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": ["new", "napoletana"],
            "note": ""
        },
        # ── LE MIE PIZZE VEGETALI ─────────────────────────────────────────
        {
            "nome": "Ortolana",
            "categoria": "Le Mie Pizze Vegetali",
            "ingredienti": ["crema di melanzane fritte", "fior di latte", "peperoni freschi saltati", "zucchine fritte a dadini", "funghi cardoncelli saltati"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": ["vegetariana", "new"],
            "note": ""
        },
        {
            "nome": "Parmigiana di Melanzane",
            "categoria": "Le Mie Pizze Vegetali",
            "ingredienti": ["pomodoro San Marzano DOP", "melanzane fritte", "provola affumicata", "Parmigiano DOP 24 mesi a scaglie", "olio EVO Colline Salernitane", "basilico"],
            "tipo": "rossa",
            "fonte": FONTE,
            "tags": ["vegetariana"],
            "note": ""
        },
        {
            "nome": "Nerano",
            "categoria": "Le Mie Pizze Vegetali",
            "ingredienti": ["crema di zucchine", "fior di latte", "zucchine fritte a dadini", "Provolone del Monaco DOP", "olio EVO Colline Salernitane", "menta"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": ["vegetariana"],
            "note": ""
        },
        {
            "nome": "Peperoni e Provola",
            "categoria": "Le Mie Pizze Vegetali",
            "ingredienti": ["peperoni freschi saltati", "provola affumicata", "olive taggiasche nere", "capperi", "Pecorino Fiore Sardo DOP"],
            "tipo": "bianca",
            "fonte": FONTE,
            "tags": ["vegetariana", "new"],
            "note": ""
        },
        # ── PIZZE FRITTE ──────────────────────────────────────────────────
        {
            "nome": "Montanara",
            "categoria": "Pizze Fritte",
            "ingredienti": ["salsa di pomodoro San Marzano DOP", "Parmigiano DOP 24 mesi", "basilico"],
            "tipo": "fritta",
            "fonte": FONTE,
            "tags": ["vegetariana", "classica"],
            "note": ""
        },
        {
            "nome": "Ripieno Fritto Classico",
            "categoria": "Pizze Fritte",
            "ingredienti": ["ricotta", "provola affumicata", "cicoli di Mugnano del Cardinale", "pepe nero"],
            "tipo": "fritta",
            "fonte": FONTE,
            "tags": ["classica", "napoletana"],
            "note": ""
        },
    ]
}

# Carica DB, aggiungi pizzeria, salva
with open(DB) as f:
    db = json.load(f)

# Rimuovi eventuale duplicato
db['pizzerie'] = [p for p in db['pizzerie'] if p['nome'] != '50 Kalò']
db['pizzerie'].append(nuova_pizzeria)

with open(DB, 'w') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

totale = sum(len(p['pizze']) for p in db['pizzerie'])
print(f"✅ Aggiunta: 50 Kalò — {len(nuova_pizzeria['pizze'])} pizze")
print(f"   Pizzerie totali: {len(db['pizzerie'])}")
print(f"   Pizze totali: {totale}")
