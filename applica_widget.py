#!/usr/bin/env python3
import sqlite3, os

DB = os.path.expanduser(
    "~/Library/Group Containers/72KVKW69K8.com.hindsightlabs.paprika.mac.v3"
    "/Data/Database/Paprika.sqlite"
)

RIMUOVI = [
    (704, "Lento e Brasato"), (716, "Vegano"), (716, "Vegetariano"),
    (674, "Arrosto"), (810, "Lento e Brasato"),
    (903, "Impasti per pizze, focacce & co."), (901, "Impasti per pizze, focacce & co."),
    (900, "Impasti per pizze, focacce & co."), (646, "Impasti per pizze, focacce & co."),
    (881, "Impasti per pizze, focacce & co."), (890, "Impasti per pizze, focacce & co."),
    (882, "Impasti per pizze, focacce & co."), (891, "Impasti per pizze, focacce & co."),
    (675, "Pesce"), (742, "Maiale"), (661, "Maiale"), (662, "Pesce"), (655, "Pesce"),
    (893, "Maiale"), (877, "Maiale"), (879, "Maiale"), (876, "Maiale"), (878, "Maiale"),
    (913, "Vegetariano"), (923, "Vegetariano"), (921, "Maiale"), (872, "Vegetariano"),
    (914, "Vegetariano"), (813, "Pizze, focacce & co."), (663, "Maiale"),
    (794, "Secondo"), (796, "Secondo"), (679, "Manzo"), (758, "Pesce"), (685, "Vegetariano"),
]

AGGIUNGI = [
    (652, "Piatto unico"), (717, "Verdure"), (714, "Verdure"), (647, "Verdure"),
    (649, "Verdure"), (783, "Formaggio"), (771, "Verdure"), (786, "Verdure"),
    (725, "Formaggio"), (792, "Alla griglia & BBQ"), (789, "Al forno"),
    (646, "Pizze, focacce & co."), (881, "Pizze, focacce & co."), (890, "Pizze, focacce & co."),
    (793, "Aiutacuochi"), (772, "Formaggio"), (653, "Piatto unico"), (653, "Secondo"),
    (696, "Messinese"), (670, "Manzo"), (670, "Verdure"), (675, "Formaggio"), (675, "Verdure"),
    (645, "Formaggio"), (645, "Verdure"), (742, "Affettati"), (742, "Pollo"),
    (746, "Vegano"), (745, "Vegano"), (681, "Formaggio"), (744, "Alla griglia & BBQ"),
    (744, "Cotto o saltato in padella"), (728, "Natale"), (661, "Affettati"), (661, "Verdure"),
    (654, "Verdure"), (662, "Verdure"), (662, "Vegetariano"), (662, "Vegano"),
    (655, "Vegetariano"), (655, "Vegano"), (774, "Ricette base"), (775, "Ricette base"),
    (766, "Patate"), (760, "Patate"), (753, "Patate"), (736, "Patate"), (788, "Patate"),
    (701, "Patate"), (701, "Verdure"), (671, "Verdure"), (660, "Verdure"),
    (698, "Piatto unico"), (740, "Fritto"), (741, "Al forno"), (741, "Natale"),
    (657, "Natale"), (657, "Vegetariano"), (893, "Affettati"), (893, "Verdure"),
    (893, "Formaggio"), (894, "Verdure"), (894, "Formaggio"), (896, "Formaggio"),
    (877, "Formaggio"), (877, "Verdure"), (877, "Affettati"), (877, "Funghi"),
    (875, "Formaggio"), (879, "Affettati"), (879, "Formaggio"), (876, "Affettati"),
    (876, "Funghi"), (876, "Formaggio"), (876, "Verdure"), (878, "Affettati"),
    (878, "Formaggio"), (863, "Formaggio"), (865, "Formaggio"), (865, "Affettati"),
    (862, "Formaggio"), (866, "Verdure"), (913, "Affettati"), (922, "Formaggio"),
    (923, "Affettati"), (923, "Formaggio"), (921, "Affettati"), (921, "Formaggio"),
    (870, "Patate"), (870, "Affettati"), (905, "Formaggio"), (915, "Formaggio"),
    (912, "Patate"), (872, "Affettati"), (872, "Verdure"), (916, "Formaggio"),
    (914, "Affettati"), (914, "Formaggio"), (910, "Formaggio"), (910, "Verdure"),
    (813, "Impasti per pizze, focacce & co."), (718, "Lento e Brasato"),
    (718, "Verdure"), (718, "Funghi"), (663, "Formaggio"), (663, "Affettati"),
    (790, "Patate"), (790, "Contorno"), (756, "Contorno"), (756, "Verdure"),
    (794, "Sughi per primi"), (794, "Ricette base"), (800, "Piatto unico"),
    (697, "Manzo"), (727, "Verdure"), (687, "Alla griglia & BBQ"),
    (679, "Verdure"), (679, "Vitello"), (719, "Aiutacuochi"),
    (758, "Salse, sughi e intingoli vari"), (757, "Salse, sughi e intingoli vari"),
    (779, "Salse, sughi e intingoli vari"), (703, "Salse, sughi e intingoli vari"),
    (703, "Natale"), (680, "Verdure"), (808, "Impasti per pizze, focacce & co."),
    (729, "Formaggio"), (730, "Verdure"), (809, "Sughi per primi"),
    (754, "Verdure"), (754, "Vegetariano"), (735, "Natale"), (811, "Pasqua"),
    (811, "Verdure"), (664, "Verdure"), (885, "Formaggio"), (798, "Colazione"),
    (748, "Verdure"), (666, "Verdure"), (764, "Dolce"), (694, "Verdure"),
    (693, "Manzo"), (693, "Verdure"),
]

con = sqlite3.connect(DB)
cur = con.cursor()

cur.execute("SELECT Z_PK, ZNAME FROM ZRECIPECATEGORY")
cat_map = {name: pk for pk, name in cur.fetchall()}

removed = skipped_r = added = skipped_a = 0
missing_cats = set()

for recipe_pk, cat_name in RIMUOVI:
    cat_pk = cat_map.get(cat_name)
    if cat_pk is None:
        missing_cats.add(cat_name); skipped_r += 1; continue
    cur.execute("DELETE FROM Z_12CATEGORIES WHERE Z_12RECIPES=? AND Z_13CATEGORIES=?", (recipe_pk, cat_pk))
    if cur.rowcount > 0:
        removed += 1
        print(f"  REM pk={recipe_pk:4d} -{cat_name}")
    else:
        skipped_r += 1

for recipe_pk, cat_name in AGGIUNGI:
    cat_pk = cat_map.get(cat_name)
    if cat_pk is None:
        missing_cats.add(cat_name); skipped_a += 1; continue
    cur.execute("SELECT 1 FROM Z_12CATEGORIES WHERE Z_12RECIPES=? AND Z_13CATEGORIES=?", (recipe_pk, cat_pk))
    if cur.fetchone():
        skipped_a += 1; continue
    cur.execute("INSERT INTO Z_12CATEGORIES (Z_12RECIPES, Z_13CATEGORIES) VALUES (?, ?)", (recipe_pk, cat_pk))
    added += 1
    print(f"  ADD pk={recipe_pk:4d} +{cat_name}")

con.commit()
con.close()

print(f"\n=== RISULTATO ===")
print(f"Rimossi: {removed}  (saltati: {skipped_r})")
print(f"Aggiunti: {added}  (saltati: {skipped_a})")
if missing_cats:
    print(f"Categorie non trovate nel DB: {missing_cats}")
