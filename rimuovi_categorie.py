#!/usr/bin/env python3
"""
Rimuovi categorie dal DB Paprika 3.
RIMUOVI = set(current) - set(proposed) per ogni ricetta, desunto da recipe_category_editor.html
"""
import sqlite3, os

DB = os.path.expanduser(
    "~/Library/Group Containers/72KVKW69K8.com.hindsightlabs.paprika.mac.v3"
    "/Data/Database/Paprika.sqlite"
)

# RIMUOVI[pk] = lista categorie da rimuovere (nomi esatti come nel DB)
RIMUOVI = {
    682:  ["Messinese"],
    677:  ["Messinese"],
    648:  ["Messinese"],
    716:  ["Aiutacuochi", "Ricette base"],
    711:  ["Aiutacuochi", "Ricette base"],
    715:  ["Aiutacuochi", "Ricette base"],
    713:  ["Aiutacuochi", "Ricette base"],
    717:  ["Aiutacuochi", "Ricette base"],
    712:  ["Aiutacuochi", "Ricette base"],
    714:  ["Aiutacuochi", "Ricette base"],
    651:  ["Messinese"],
    676:  ["Messinese"],
    647:  ["Messinese"],
    649:  ["Messinese"],
    674:  ["Messinese"],
    734:  ["Ricette base"],
    732:  ["Ricette base"],
    777:  ["Ricette base"],
    778:  ["Ricette base"],
    733:  ["Ricette base"],
    773:  ["Ricette base"],
    759:  ["30 minuti"],
    721:  ["Ricette base"],
    903:  ["Pizze, focacce & co."],
    901:  ["Pizze, focacce & co."],
    900:  ["Pizze, focacce & co."],
    646:  ["Messinese"],
    882:  ["Pizze, focacce & co."],
    891:  ["Pizze, focacce & co."],
    749:  ["30 minuti"],
    761:  ["30 minuti"],
    653:  ["Messinese"],
    762:  ["30 minuti"],
    888:  ["Pizze, focacce & co."],
    887:  ["Impasti per pizze, focacce & co."],
    678:  ["Messinese"],
    670:  ["Messinese"],
    675:  ["Messinese"],
    645:  ["Messinese"],
    755:  ["30 minuti"],
    681:  ["Messinese", "Ricette base"],
    744:  ["30 minuti"],
    661:  ["Messinese"],
    654:  ["Messinese"],
    662:  ["Messinese", "Pasqua"],
    655:  ["Messinese"],
    658:  ["Messinese"],
    766:  ["30 minuti"],
    760:  ["30 minuti"],
    753:  ["30 minuti"],
    671:  ["Messinese"],
    660:  ["Messinese"],
    656:  ["Messinese"],
    751:  ["30 minuti"],
    740:  ["Messinese"],
    741:  ["Messinese"],
    657:  ["Messinese"],
    863:  ["Pizze, focacce & co."],
    865:  ["Pizze, focacce & co."],
    861:  ["Impasti per pizze, focacce & co."],
    864:  ["Impasti per pizze, focacce & co."],
    862:  ["Pizze, focacce & co."],
    866:  ["Pizze, focacce & co."],
    893:  ["Pizze, focacce & co."],
    897:  ["Pizze, focacce & co."],
    894:  ["Pizze, focacce & co."],
    892:  ["Impasti per pizze, focacce & co."],
    895:  ["Impasti per pizze, focacce & co."],
    896:  ["Pizze, focacce & co."],
    813:  ["Pizze, focacce & co."],
    913:  ["Pizze, focacce & co."],
    917:  ["Pizze, focacce & co."],
    871:  ["Pizze, focacce & co."],
    922:  ["Pizze, focacce & co."],
    870:  ["Pizze, focacce & co."],
    852:  ["Impasti per pizze, focacce & co."],
    880:  ["Impasti per pizze, focacce & co."],
    867:  ["Impasti per pizze, focacce & co."],
    869:  ["Impasti per pizze, focacce & co."],
    868:  ["Impasti per pizze, focacce & co."],
    905:  ["Pizze, focacce & co."],
    915:  ["Pizze, focacce & co."],
    923:  ["Pizze, focacce & co."],
    912:  ["Pizze, focacce & co."],
    872:  ["Pizze, focacce & co."],
    916:  ["Pizze, focacce & co."],
    921:  ["Pizze, focacce & co."],
    914:  ["Pizze, focacce & co."],
    909:  ["Pizze, focacce & co."],
    910:  ["Pizze, focacce & co."],
    877:  ["Pizze, focacce & co."],
    873:  ["Impasti per pizze, focacce & co."],
    875:  ["Pizze, focacce & co."],
    874:  ["Pizze, focacce & co."],
    879:  ["Pizze, focacce & co."],
    876:  ["Pizze, focacce & co."],
    878:  ["Pizze, focacce & co."],
    743:  ["30 minuti"],
    663:  ["Messinese"],
    695:  ["Messinese"],
    756:  ["30 minuti"],
    683:  ["Messinese"],
    689:  ["Ricette base"],
    699:  ["Ricette base"],
    763:  ["30 minuti"],
    679:  ["Messinese"],
    719:  ["Ricette base"],
    757:  ["Ricette base"],
    758:  ["Ricette base"],
    779:  ["Ricette base"],
    703:  ["Ricette base"],
    672:  ["Messinese"],
    680:  ["Messinese"],
    904:  ["Impasti per pizze, focacce & co."],
    883:  ["Impasti per pizze, focacce & co."],
    889:  ["Impasti per pizze, focacce & co."],
    709:  ["Aiutacuochi", "Ricette base"],
    710:  ["Aiutacuochi", "Ricette base"],
    706:  ["Aiutacuochi", "Ricette base"],
    707:  ["Aiutacuochi", "Ricette base"],
    708:  ["Aiutacuochi", "Ricette base"],
    659:  ["Messinese"],
    754:  ["30 minuti"],
    650:  ["Messinese"],
    702:  ["Ricette base"],
    765:  ["Ricette base"],
    752:  ["30 minuti"],
    750:  ["30 minuti"],
    884:  ["Impasti per pizze, focacce & co."],
    885:  ["Pizze, focacce & co."],
    748:  ["30 minuti"],
    764:  ["30 minuti"],
    747:  ["30 minuti"],
}

con = sqlite3.connect(DB)
cur = con.cursor()

# Carica mappa nome→pk per ZRECIPECATEGORY
cur.execute("SELECT Z_PK, ZNAME FROM ZRECIPECATEGORY")
cat_map = {row[1]: row[0] for row in cur.fetchall()}

removed = 0
skipped = 0
not_found_cat = set()
not_found_assoc = []

for recipe_pk, cats in RIMUOVI.items():
    for cat_name in cats:
        cat_pk = cat_map.get(cat_name)
        if cat_pk is None:
            not_found_cat.add(cat_name)
            skipped += 1
            continue
        cur.execute(
            "DELETE FROM Z_12CATEGORIES WHERE Z_12RECIPES=? AND Z_13CATEGORIES=?",
            (recipe_pk, cat_pk)
        )
        if cur.rowcount > 0:
            removed += 1
            print(f"  RIMOSSO  pk={recipe_pk:4d}  {cat_name}")
        else:
            not_found_assoc.append((recipe_pk, cat_name))
            skipped += 1

con.commit()
con.close()

print(f"\n=== RISULTATO ===")
print(f"Rimossi: {removed}")
print(f"Saltati (non trovati): {skipped}")
if not_found_cat:
    print(f"Categorie non trovate nel DB: {not_found_cat}")
if not_found_assoc:
    print(f"Associazioni già assenti ({len(not_found_assoc)}):")
    for pk, c in not_found_assoc:
        print(f"  pk={pk} {c}")
