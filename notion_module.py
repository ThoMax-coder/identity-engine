import os
from notion_client import Client

NOTION_TOKEN = "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"
DATABASE_ID = "32b96ddc396380ff830ff91dfaf3a0b9"

notion = Client(auth=NOTION_TOKEN)

def get_active_modules():
    response = notion.databases.query(
        **{
            "database_id": DATABASE_ID,
            "filter": {
                "property": "Aktiv",
                "checkbox": {"equals": True}
            }
        }
    )
    modules = []
    for page in response["results"]:
        props = page["properties"]
        name = props["Name"]["title"][0]["text"]["content"] if props["Name"]["title"] else ""
        inhalt = props["Inhalt"]["rich_text"][0]["text"]["content"] if props["Inhalt"]["rich_text"] else ""
        modules.append({"name": name, "inhalt": inhalt})
    return modules

def print_module_context():
    modules = get_active_modules()
    print("\n" + "="*60)
    print("IDENTITY & MESSAGING ENGINE — AKTIVE MODULE")
    print("="*60 + "\n")
    for m in modules:
        print(f"# {m['name']}")
        print(m['inhalt'])
        print("\n" + "-"*60 + "\n")

if __name__ == "__main__":
    print_module_context()
