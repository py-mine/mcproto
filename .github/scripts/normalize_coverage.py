from __future__ import annotations

import sqlite3

connection = sqlite3.connect(".coverage")

# Normalize windows paths
connection.execute("UPDATE file SET path = REPLACE(path, '\\', '/')")

connection.commit()
connection.close()
