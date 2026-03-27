# -*- coding: utf-8 -*-
import os
import subprocess
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

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

def build_context():
    modules = get_active_modules()
    lines = []
    lines.append("=" * 60)
    lines.append("IDENTITY & MESSAGING ENGINE - AKTIVE MODULE")
    lines.append("=" * 60)
    lines.append("")
    for m in modules:
        lines.append(f"# {m['name']}")
        lines.append(m['inhalt'])
        lines.append("")
        lines.append("-" * 60)
        lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    context = build_context()
    print(context)
    subprocess.run("clip", input=context.encode("utf-8"), check=True)
    print("\nModule in Zwischenablage kopiert - bereit zum Einfuegen in Claude.")
