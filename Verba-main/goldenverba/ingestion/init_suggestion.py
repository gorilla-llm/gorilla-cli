import os
from wasabi import msg  # type: ignore[import]

from goldenverba.ingestion.util import setup_client

from dotenv import load_dotenv

load_dotenv()


def init_suggestion():
    msg.divider("Creating Suggestion class")

    client = setup_client()

    suggestion_schema = {
        "classes": [
            {
                "class": "Suggestion",
                "description": "List of possible prompts",
                "properties": [
                    {
                        "name": "suggestion",
                        "dataType": ["text"],
                        "description": "Query",
                    },
                ],
            }
        ]
    }

    if client.schema.exists("Suggestion"):
        user_input = input(
            "Suggestion class already exists, do you want to overwrite it? (y/n): "
        )
        if user_input.strip().lower() == "y":
            client.schema.delete_class("Suggestion")
            client.schema.create(suggestion_schema)
            msg.good("'Suggestion' schema created")
        else:
            msg.warn("Skipped deleting Suggestion schema, nothing changed")
    else:
        client.schema.create(suggestion_schema)
        msg.good("'Suggestion' schema created")

    if client._connection.embedded_db:
        msg.info("Stopping Weaviate Embedded")
        client._connection.embedded_db.stop()
    msg.info("Done")
