import json
from pathlib import Path
import re

DATA_PATH = Path("contacts.json")
EXPORT_PATH = Path("contacts_export.txt")

TEL_PAT = re.compile(r"^\d{7,15}$")
MAIL_PAT = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


def run():
    # Load state
    if DATA_PATH.exists():
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            db = {"next_id": 1001, "groups": ["General"], "contacts": {}}
    else:
        db = {"next_id": 1001, "groups": ["General"], "contacts": {}}

    while True:
        print("\n--- CONTACTS ---")
        print("1: Add  | 2: View All | 3: Search | 4: Edit")
        print("5: Fav  | 6: Delete   | 7: Export | 8: Quit")
        
        opt = input("select> ").strip()

        if opt == "8":
            break

        if opt == "1":
            nm = input("Name: ").strip()
            if not nm:
                print("Name required.")
                continue

            ph = input("Phone: ").strip()
            if not TEL_PAT.match(ph):
                print("Invalid phone format.")
                continue

            if any(c["phone"] == ph for c in db["contacts"].values()):
                print("Number already exists.")
                continue

            em = input("Email (optional): ").strip()
            if em and not MAIL_PAT.match(em):
                print("Bad email. Skipping field.")
                em = ""

            print("\nGroups: " + ", ".join(db["groups"]))
            grp = input("Group name (leave blank for General): ").strip() or "General"
            if grp not in db["groups"]:
                db["groups"].append(grp)

            addr = input("Address: ").strip()
            note = input("Note: ").strip()

            cid = str(db["next_id"])
            db["next_id"] += 1
            db["contacts"][cid] = {
                "name": nm, "phone": ph, "email": em, 
                "group": grp, "address": addr, "note": note, "fav": False
            }
            
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
            print(f"Added ID: {cid}")

        elif opt == "2":
            if not db["contacts"]:
                print("No records found.")
                continue
            for k, v in db["contacts"].items():
                tag = "★" if v.get("fav") else " "
                print(f"[{tag}] {k} -> {v['name']} | {v['phone']} | {v.get('group')} | {v.get('email') or 'no email'}")

        elif opt == "3":
            q = input("Query: ").strip().lower()
            if not q:
                continue
            res = [
                (k, v) for k, v in db["contacts"].items()
                if q in v["name"].lower() or q in v["phone"] or q in v.get("group", "").lower()
            ]
            if not res:
                print("No matches.")
            for k, v in res:
                print(f"[{k}] {v['name']} - {v['phone']} ({v.get('group')})")

        elif opt == "4":
            target = input("Target ID: ").strip()
            if target not in db["contacts"]:
                print("ID not found.")
                continue

            row = db["contacts"][target]
            row["name"] = input(f"Name [{row['name']}]: ").strip() or row["name"]
            
            p = input(f"Phone [{row['phone']}]: ").strip()
            if p and TEL_PAT.match(p):
                row["phone"] = p

            e = input(f"Email [{row['email']}]: ").strip()
            if e and MAIL_PAT.match(e):
                row["email"] = e

            row["address"] = input(f"Address [{row['address']}]: ").strip() or row["address"]
            row["note"] = input(f"Note [{row['note']}]: ").strip() or row["note"]

            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
            print("Saved changes.")

        elif opt == "5":
            target = input("ID: ").strip()
            if target in db["contacts"]:
                db["contacts"][target]["fav"] = not db["contacts"][target].get("fav", False)
                with open(DATA_PATH, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
                print("Toggled favorite.")

        elif opt == "6":
            target = input("ID to purge: ").strip()
            if target in db["contacts"]:
                del db["contacts"][target]
                with open(DATA_PATH, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
                print("Removed.")

        elif opt == "7":
            try:
                with open(EXPORT_PATH, "w", encoding="utf-8") as f:
                    f.write("ID,Name,Phone,Group,Email\n")
                    for k, v in db["contacts"].items():
                        f.write(f"{k},{v['name']},{v['phone']},{v['group']},{v['email']}\n")
                print(f"Exported to {EXPORT_PATH}")
            except Exception as e:
                print(f"Export failed: {e}")


if __name__ == "__main__":
    run()