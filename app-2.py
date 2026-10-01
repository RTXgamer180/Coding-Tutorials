import os
import sys
import json
import time
import sqlite3
import subprocess
import tempfile
import threading
from pathlib import Path

from flask import Flask, request, jsonify, render_template_string


# ============================================================
# APP CONFIG
# ============================================================

app = Flask(__name__)

# No artificial application code-size limit.
# Real server/browser/memory limits still apply.
app.config["MAX_CONTENT_LENGTH"] = None

PORT = int(os.environ.get("PORT", "5000"))
HOST = "0.0.0.0"

PYTHON_TIMEOUT = 60
SQL_TIMEOUT = 30
PIP_TIMEOUT = 180

DB_FILE = os.environ.get(
    "NEON_DB",
    os.path.join(tempfile.gettempdir(), "neon_programming_hub.db")
)


# ============================================================
# DATABASE
# ============================================================

def init_db():
    conn = sqlite3.connect(DB_FILE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS playgrounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            language TEXT NOT NULL,
            code TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ============================================================
# TRANSLATIONS
# ============================================================

TRANSLATIONS = {
    "en": {
        "brand": "NEON PROGRAMMING HUB",
        "subtitle": "Code. Experiment. Build.",
        "run": "▶ Run",
        "clear": "Clear",
        "copy": "Copy",
        "examples": "Examples",
        "playgrounds": "Playgrounds",
        "packages": "Packages",
        "install": "Install Package",
        "language": "Language",
        "output": "Output",
        "python": "Python",
        "html": "HTML",
        "css": "CSS",
        "javascript": "JavaScript",
        "sql": "SQL",
        "new_playground": "New Playground",
        "save": "Save",
        "delete": "Delete",
        "package_name": "Package name",
        "package_help": "Install any package available from PyPI.",
        "ready": "Ready.",
        "running": "Running...",
        "saved": "Saved.",
        "deleted": "Deleted.",
        "loading": "Loading...",
        "error": "Error",
        "welcome": "Welcome to Neon Programming Hub!",
        "example_loaded": "Example loaded.",
        "no_code": "No code entered.",
        "select_language": "Select a language",
        "name": "Name",
    },

    "de": {
        "brand": "NEON PROGRAMMING HUB",
        "subtitle": "Programmieren. Experimentieren. Bauen.",
        "run": "▶ Ausführen",
        "clear": "Leeren",
        "copy": "Kopieren",
        "examples": "Beispiele",
        "playgrounds": "Playgrounds",
        "packages": "Pakete",
        "install": "Paket installieren",
        "language": "Sprache",
        "output": "Ausgabe",
        "python": "Python",
        "html": "HTML",
        "css": "CSS",
        "javascript": "JavaScript",
        "sql": "SQL",
        "new_playground": "Neuer Playground",
        "save": "Speichern",
        "delete": "Löschen",
        "package_name": "Paketname",
        "package_help": "Installiere beliebige Pakete, die auf PyPI verfügbar sind.",
        "ready": "Bereit.",
        "running": "Wird ausgeführt...",
        "saved": "Gespeichert.",
        "deleted": "Gelöscht.",
        "loading": "Lädt...",
        "error": "Fehler",
        "welcome": "Willkommen beim Neon Programming Hub!",
        "example_loaded": "Beispiel geladen.",
        "no_code": "Kein Code eingegeben.",
        "select_language": "Sprache auswählen",
        "name": "Name",
    }
}


# ============================================================
# EXAMPLES
# ============================================================

EXAMPLES = {

    "python": [

        {
            "name": "Hello World",
            "code": """print("Hello, world!")
"""
        },

        {
            "name": "Calculator",
            "code": """a = 25
b = 7

print("Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)
"""
        },

        {
            "name": "Loops",
            "code": """for number in range(1, 11):
    print("Number:", number)
"""
        },

        {
            "name": "Lists",
            "code": """players = [
    "Raphael",
    "Alex",
    "Steve",
    "Notch"
]

for player in players:
    print(player)
"""
        },

        {
            "name": "Functions",
            "code": """def greet(name):
    return f"Hello, {name}!"

print(greet("Raphael"))
"""
        },

        {
            "name": "Dictionary",
            "code": """player = {
    "name": "Raphael",
    "level": 42,
    "coins": 1337
}

print(player["name"])
print(player["level"])
print(player["coins"])
"""
        },

        {
            "name": "Random Numbers",
            "code": """import random

number = random.randint(1, 100)

print("Random number:", number)
"""
        },

        {
            "name": "Date & Time",
            "code": """from datetime import datetime

now = datetime.now()

print("Current time:")
print(now)
"""
        },

        {
            "name": "JSON",
            "code": """import json

data = {
    "player": "Raphael",
    "level": 50,
    "online": True
}

text = json.dumps(data, indent=2)

print(text)
"""
        },

        {
            "name": "Classes",
            "code": """class Player:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def info(self):
        print(self.name, "is level", self.level)


player = Player("Raphael", 100)

player.info()
"""
        },

        {
            "name": "File Example",
            "code": """from pathlib import Path

file = Path("example.txt")

file.write_text(
    "Hello from Neon Programming Hub!"
)

print(file.read_text())
"""
        },

        {
            "name": "HTTP Request",
            "code": """import requests

response = requests.get(
    "https://example.com",
    timeout=10
)

print("Status:", response.status_code)
print(response.text[:500])
"""
        },

        {
            "name": "NumPy",
            "code": """import numpy as np

numbers = np.array([1, 2, 3, 4, 5])

print(numbers)
print("Mean:", numbers.mean())
print("Sum:", numbers.sum())
"""
        },

        {
            "name": "Rich Terminal",
            "code": """from rich.console import Console

console = Console()

console.print(
    "[bold cyan]NEON PROGRAMMING HUB[/bold cyan]"
)

console.print(
    "[green]Everything works![/green]"
)
"""
        }
    ],

    "html": [

        {
            "name": "Basic HTML",
            "code": """<!DOCTYPE html>
<html>
<head>
    <title>Neon Page</title>
</head>

<body>

<h1>Hello World!</h1>

<p>Welcome to my website.</p>

</body>
</html>
"""
        },

        {
            "name": "Button",
            "code": """<!DOCTYPE html>
<html>

<body>

<button onclick="alert('Hello!')">
    Click me
</button>

</body>
</html>
"""
        },

        {
            "name": "Card",
            "code": """<div class="card">

    <h1>Neon Card</h1>

    <p>
        This is a simple HTML card.
    </p>

    <button>
        Open
    </button>

</div>
"""
        },

        {
            "name": "Video",
            "code": """<!DOCTYPE html>
<html>

<body>

<h1>Video Player</h1>

<video controls width="700">
    <source src="video.mp4" type="video/mp4">
</video>

</body>
</html>
"""
        }
    ],

    "css": [

        {
            "name": "Neon Button",
            "code": """.button {
    background: #080808;
    color: #00ffff;

    border: 2px solid #00ffff;

    padding: 15px 30px;

    border-radius: 12px;

    box-shadow:
        0 0 10px #00ffff;

    cursor: pointer;
}
"""
        },

        {
            "name": "Neon Card",
            "code": """.card {
    background: #101018;

    border: 1px solid #8a2be2;

    border-radius: 20px;

    padding: 25px;

    box-shadow:
        0 0 25px rgba(138,43,226,0.5);
}
"""
        },

        {
            "name": "Animation",
            "code": """@keyframes pulse {

    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }

    100% {
        transform: scale(1);
    }
}

.pulse {
    animation: pulse 2s infinite;
}
"""
        }
    ],

    "javascript": [

        {
            "name": "Hello",
            "code": """console.log("Hello from JavaScript!");
"""
        },

        {
            "name": "Counter",
            "code": """let counter = 0;

counter++;

console.log("Counter:", counter);
"""
        },

        {
            "name": "Function",
            "code": """function greet(name) {
    return `Hello, ${name}!`;
}

console.log(greet("Raphael"));
"""
        },

        {
            "name": "Array",
            "code": """const players = [
    "Steve",
    "Alex",
    "Raphael"
];

players.forEach(player => {
    console.log(player);
});
"""
        }
    ],

    "sql": [

        {
            "name": "Create Table",
            "code": """CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    name TEXT,
    level INTEGER
);

INSERT INTO players
(name, level)
VALUES
('Raphael', 42);

SELECT * FROM players;
"""
        },

        {
            "name": "Multiple Players",
            "code": """CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    name TEXT,
    level INTEGER
);

INSERT INTO players
(name, level)
VALUES
('Steve', 20),
('Alex', 35),
('Raphael', 100);

SELECT *
FROM players
ORDER BY level DESC;
"""
        },

        {
            "name": "WHERE",
            "code": """CREATE TABLE players (
    name TEXT,
    level INTEGER
);

INSERT INTO players VALUES
('Steve', 10),
('Alex', 50),
('Raphael', 100);

SELECT *
FROM players
WHERE level >= 50;
"""
        }
    ]
}


# ============================================================
# DEFAULT PLAYGROUNDS
# ============================================================

DEFAULT_PLAYGROUNDS = [
    {
        "name": "Python Playground",
        "language": "python",
        "code": EXAMPLES["python"][0]["code"]
    },
    {
        "name": "HTML Playground",
        "language": "html",
        "code": EXAMPLES["html"][0]["code"]
    },
    {
        "name": "CSS Playground",
        "language": "css",
        "code": EXAMPLES["css"][0]["code"]
    },
    {
        "name": "JavaScript Playground",
        "language": "javascript",
        "code": EXAMPLES["javascript"][0]["code"]
    },
    {
        "name": "SQL Playground",
        "language": "sql",
        "code": EXAMPLES["sql"][0]["code"]
    }
]


# ============================================================
# HELPERS
# ============================================================

def execute_python(code):
    if not code.strip():
        return {
            "success": False,
            "output": "No code entered."
        }

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as file:

            file.write(code)
            temp_path = file.name

        started = time.time()

        result = subprocess.run(
            [sys.executable, temp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=PYTHON_TIMEOUT,
            cwd=tempfile.gettempdir()
        )

        elapsed = time.time() - started

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "returncode": result.returncode,
            "time": round(elapsed, 3)
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "Execution timed out."
        }

    except Exception as exc:
        return {
            "success": False,
            "output": str(exc)
        }

    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except Exception:
                pass


def execute_sql(code):
    if not code.strip():
        return {
            "success": False,
            "output": "No SQL entered."
        }

    conn = None

    try:
        conn = sqlite3.connect(":memory:")

        cursor = conn.cursor()

        cursor.executescript(code)

        rows = cursor.fetchall()

        if cursor.description:
            columns = [
                description[0]
                for description in cursor.description
            ]

            output = json.dumps(
                {
                    "columns": columns,
                    "rows": rows
                },
                indent=2,
                default=str
            )
        else:
            output = f"SQL executed successfully. Rows affected: {cursor.rowcount}"

        return {
            "success": True,
            "output": output
        }

    except Exception as exc:
        return {
            "success": False,
            "output": str(exc)
        }

    finally:
        if conn:
            conn.close()


def install_package(package):
    package = package.strip()

    if not package:
        return {
            "success": False,
            "output": "Please enter a package name."
        }

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                package
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=PIP_TIMEOUT
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "Package installation timed out."
        }

    except Exception as exc:
        return {
            "success": False,
            "output": str(exc)
        }


# ============================================================
# API ROUTES
# ============================================================

@app.get("/health")
def health():
    return jsonify({
        "status": "online",
        "service": "Neon Programming Hub"
    })


@app.get("/")
def index():
    return render_template_string(HTML)


@app.post("/api/python/run")
def api_python_run():
    data = request.get_json(silent=True) or {}

    code = data.get("code", "")

    return jsonify(
        execute_python(code)
    )


@app.post("/api/python/install")
def api_python_install():
    data = request.get_json(silent=True) or {}

    package = data.get("package", "")

    return jsonify(
        install_package(package)
    )


@app.post("/api/sql/run")
def api_sql_run():
    data = request.get_json(silent=True) or {}

    code = data.get("code", "")

    return jsonify(
        execute_sql(code)
    )


@app.get("/api/examples")
def api_examples():
    return jsonify(EXAMPLES)


@app.get("/api/playgrounds")
def api_playgrounds():

    conn = sqlite3.connect(DB_FILE)

    rows = conn.execute("""
        SELECT id, name, language, code, created_at
        FROM playgrounds
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "language": row[2],
            "code": row[3],
            "created_at": row[4]
        })

    return jsonify(result)


@app.post("/api/playgrounds")
def api_create_playground():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "Untitled Playground")
    language = data.get("language", "python")
    code = data.get("code", "")

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.execute("""
        INSERT INTO playgrounds
        (name, language, code, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        language,
        code,
        time.time()
    ))

    conn.commit()

    playground_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "success": True,
        "id": playground_id
    })


@app.delete("/api/playgrounds/<int:playground_id>")
def api_delete_playground(playground_id):

    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        "DELETE FROM playgrounds WHERE id = ?",
        (playground_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


# ============================================================
# HTML
# ============================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>Neon Programming Hub</title>

<style>

* {
    box-sizing: border-box;
}

:root {
    --bg: #050509;
    --panel: #0c0c14;
    --panel2: #11111c;
    --border: #272738;
    --cyan: #00ffff;
    --purple: #9d4edd;
    --text: #f5f5ff;
    --muted: #888899;
    --green: #35ff8a;
    --red: #ff4f70;
}

body {
    margin: 0;
    background:
        radial-gradient(
            circle at top left,
            rgba(157, 78, 221, 0.18),
            transparent 35%
        ),
        radial-gradient(
            circle at bottom right,
            rgba(0, 255, 255, 0.10),
            transparent 35%
        ),
        var(--bg);

    color: var(--text);

    font-family:
        Inter,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    min-height: 100vh;
}

header {
    position: sticky;
    top: 0;
    z-index: 50;

    backdrop-filter: blur(18px);

    background:
        rgba(5, 5, 9, 0.82);

    border-bottom:
        1px solid var(--border);

    padding: 16px 20px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 15px;
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-icon {
    width: 44px;
    height: 44px;

    border-radius: 13px;

    display: grid;
    place-items: center;

    background:
        linear-gradient(
            135deg,
            var(--purple),
            var(--cyan)
        );

    color: #000;

    font-weight: 1000;

    box-shadow:
        0 0 25px rgba(0,255,255,.25);
}

.logo h1 {
    font-size: 17px;
    margin: 0;
}

.logo span {
    color: var(--muted);
    font-size: 12px;
}

.header-controls {
    display: flex;
    gap: 8px;
    align-items: center;
}

select,
input,
button {
    font: inherit;
}

select,
input {
    background: var(--panel2);
    color: var(--text);

    border: 1px solid var(--border);

    border-radius: 10px;

    padding: 10px 12px;

    outline: none;
}

select:focus,
input:focus {
    border-color: var(--cyan);

    box-shadow:
        0 0 0 2px rgba(0,255,255,.08);
}

button {
    border: 1px solid var(--border);

    background: var(--panel2);

    color: var(--text);

    border-radius: 10px;

    padding: 10px 14px;

    cursor: pointer;

    transition:
        transform .15s,
        border-color .15s,
        background .15s;
}

button:hover {
    transform: translateY(-1px);

    border-color: var(--cyan);

    background: #171722;
}

button.primary {
    background:
        linear-gradient(
            135deg,
            rgba(0,255,255,.20),
            rgba(157,78,221,.20)
        );

    border-color: var(--cyan);
}

button.danger {
    border-color: var(--red);
}

.app {
    display: grid;

    grid-template-columns:
        250px
        minmax(0, 1fr);

    min-height:
        calc(100vh - 77px);
}

.sidebar {
    border-right:
        1px solid var(--border);

    padding: 18px;

    background:
        rgba(10,10,16,.65);
}

.sidebar-section {
    margin-bottom: 24px;
}

.sidebar-title {
    color: var(--muted);

    font-size: 11px;

    text-transform: uppercase;

    letter-spacing: 1.4px;

    margin-bottom: 8px;
}

.nav-button {
    width: 100%;

    text-align: left;

    margin-bottom: 6px;
}

.nav-button.active {
    border-color: var(--cyan);

    background:
        rgba(0,255,255,.08);
}

main {
    min-width: 0;

    padding: 20px;
}

.topbar {
    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 15px;

    margin-bottom: 15px;

    flex-wrap: wrap;
}

.title h2 {
    margin: 0 0 4px;

    font-size: 24px;
}

.title p {
    margin: 0;

    color: var(--muted);
}

.actions {
    display: flex;

    gap: 8px;

    flex-wrap: wrap;
}

.editor-layout {
    display: grid;

    grid-template-columns:
        minmax(0, 1fr)
        minmax(280px, 36%);

    gap: 15px;
}

.panel {
    background:
        rgba(12,12,20,.88);

    border:
        1px solid var(--border);

    border-radius: 16px;

    overflow: hidden;

    box-shadow:
        0 20px 60px rgba(0,0,0,.22);
}

.panel-header {
    min-height: 48px;

    padding: 10px 13px;

    border-bottom:
        1px solid var(--border);

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 10px;
}

.panel-header strong {
    font-size: 13px;
}

.editor-wrap {
    height:
        calc(100vh - 225px);

    min-height: 420px;
}

textarea {
    width: 100%;
    height: 100%;

    resize: none;

    border: 0;
    outline: none;

    padding: 18px;

    background:
        #07070d;

    color:
        #e9e9ff;

    font-family:
        "JetBrains Mono",
        "Fira Code",
        Consolas,
        monospace;

    font-size: 14px;

    line-height: 1.6;

    tab-size: 4;
}

.output {
    height:
        calc(100vh - 225px);

    min-height: 420px;

    overflow: auto;

    padding: 18px;

    background:
        #050507;

    font-family:
        "JetBrains Mono",
        Consolas,
        monospace;

    white-space: pre-wrap;

    word-break: break-word;

    color:
        #d8d8e8;
}

.output.success {
    color: var(--green);
}

.output.error {
    color: var(--red);
}

.example-grid {
    display: grid;

    grid-template-columns:
        repeat(auto-fill, minmax(220px, 1fr));

    gap: 12px;

    padding: 15px;
}

.example-card {
    border:
        1px solid var(--border);

    border-radius: 14px;

    padding: 15px;

    background:
        rgba(255,255,255,.02);
}

.example-card h3 {
    margin:
        0 0 7px;

    font-size: 14px;
}

.example-card p {
    color: var(--muted);

    font-size: 12px;

    min-height: 35px;
}

.example-card button {
    width: 100%;
}

.package-box {
    padding: 15px;
}

.package-row {
    display: flex;

    gap: 8px;
}

.package-row input {
    flex: 1;
}

.package-output {
    margin-top: 12px;

    padding: 12px;

    min-height: 80px;

    background: #050507;

    border:
        1px solid var(--border);

    border-radius: 10px;

    white-space: pre-wrap;

    font-family: monospace;

    font-size: 12px;
}

.playground-list {
    padding: 15px;

    display: grid;

    gap: 10px;
}

.playground {
    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 10px;

    padding: 12px;

    background:
        rgba(255,255,255,.025);

    border:
        1px solid var(--border);

    border-radius: 12px;
}

.playground-info strong {
    display: block;
}

.playground-info span {
    color: var(--muted);

    font-size: 12px;
}

.playground-actions {
    display: flex;

    gap: 6px;
}

.status {
    color: var(--muted);

    font-size: 12px;
}

.badge {
    padding: 4px 8px;

    border-radius: 999px;

    border:
        1px solid var(--border);

    font-size: 11px;

    color: var(--cyan);
}

.empty {
    padding: 30px;

    text-align: center;

    color: var(--muted);
}

@media(max-width: 900px) {

    .app {
        grid-template-columns: 1fr;
    }

    .sidebar {
        border-right: 0;

        border-bottom:
            1px solid var(--border);

        display: flex;

        gap: 8px;

        overflow-x: auto;
    }

    .sidebar-section {
        min-width: 180px;

        margin: 0;
    }

    .editor-layout {
        grid-template-columns: 1fr;
    }

    .editor-wrap,
    .output {
        height: 500px;
    }
}

</style>

</head>

<body>

<header>

    <div class="logo">

        <div class="logo-icon">
            &lt;/&gt;
        </div>

        <div>
            <h1 id="brand">
                NEON PROGRAMMING HUB
            </h1>

            <span id="subtitle">
                Code. Experiment. Build.
            </span>
        </div>

    </div>

    <div class="header-controls">

        <select id="languageSelect"
                onchange="changeUILanguage()">

            <option value="en">
                🇬🇧 English
            </option>

            <option value="de">
                🇩🇪 Deutsch
            </option>

        </select>

    </div>

</header>


<div class="app">

<aside class="sidebar">

    <div class="sidebar-section">

        <div class="sidebar-title">
            Workspace
        </div>

        <button
            class="nav-button active"
            onclick="showPage('editor')"
            id="navEditor">
            💻 Editor
        </button>

        <button
            class="nav-button"
            onclick="showPage('examples')"
            id="navExamples">
            📚 Examples
        </button>

        <button
            class="nav-button"
            onclick="showPage('playgrounds')"
            id="navPlaygrounds">
            🧪 Playgrounds
        </button>

        <button
            class="nav-button"
            onclick="showPage('packages')"
            id="navPackages">
            📦 Packages
        </button>

    </div>

</aside>


<main>

<!-- ======================================================
     EDITOR
====================================================== -->

<section id="page-editor">

    <div class="topbar">

        <div class="title">

            <h2 id="editorTitle">
                Python Playground
            </h2>

            <p id="status">
                Ready.
            </p>

        </div>

        <div class="actions">

            <select id="language"
                    onchange="changeLanguage()">

                <option value="python">
                    Python
                </option>

                <option value="html">
                    HTML
                </option>

                <option value="css">
                    CSS
                </option>

                <option value="javascript">
                    JavaScript
                </option>

                <option value="sql">
                    SQL
                </option>

            </select>

            <button onclick="clearEditor()">
                🗑 Clear
            </button>

            <button onclick="copyCode()">
                📋 Copy
            </button>

            <button
                class="primary"
                onclick="runCode()">

                ▶ Run

            </button>

        </div>

    </div>


    <div class="editor-layout">

        <div class="panel">

            <div class="panel-header">

                <strong>
                    Code
                </strong>

                <span class="badge"
                      id="languageBadge">
                    Python
                </span>

            </div>

            <div class="editor-wrap">

                <textarea
                    id="editor"
                    spellcheck="false"></textarea>

            </div>

        </div>


        <div class="panel">

            <div class="panel-header">

                <strong id="outputTitle">
                    Output
                </strong>

                <span class="status">
                    Console
                </span>

            </div>

            <div
                id="output"
                class="output">

                Ready.

            </div>

        </div>

    </div>

</section>


<!-- ======================================================
     EXAMPLES
====================================================== -->

<section id="page-examples"
         style="display:none;">

    <div class="topbar">

        <div class="title">

            <h2 id="examplesTitle">
                Examples
            </h2>

            <p>
                Ready-to-use code examples.
            </p>

        </div>

        <select
            id="exampleLanguage"
            onchange="renderExamples()">

            <option value="python">
                Python
            </option>

            <option value="html">
                HTML
            </option>

            <option value="css">
                CSS
            </option>

            <option value="javascript">
                JavaScript
            </option>

            <option value="sql">
                SQL
            </option>

        </select>

    </div>


    <div class="panel">

        <div
            id="exampleGrid"
            class="example-grid">
        </div>

    </div>

</section>


<!-- ======================================================
     PLAYGROUNDS
====================================================== -->

<section id="page-playgrounds"
         style="display:none;">

    <div class="topbar">

        <div class="title">

            <h2>
                Playgrounds
            </h2>

            <p>
                Save your own coding projects.
            </p>

        </div>

        <button
            class="primary"
            onclick="newPlayground()">

            ➕ New Playground

        </button>

    </div>


    <div class="panel">

        <div
            id="playgroundList"
            class="playground-list">

            Loading...

        </div>

    </div>

</section>


<!-- ======================================================
     PACKAGES
====================================================== -->

<section id="page-packages"
         style="display:none;">

    <div class="topbar">

        <div class="title">

            <h2>
                Packages
            </h2>

            <p>
                Install packages from PyPI.
            </p>

        </div>

    </div>


    <div class="panel">

        <div class="package-box">

            <div class="sidebar-title">
                Package name
            </div>

            <div class="package-row">

                <input
                    id="packageInput"
                    placeholder="requests">

                <button
                    class="primary"
                    onclick="installPackage()">

                    📦 Install

                </button>

            </div>

            <p class="status">
                Any package available on PyPI can be entered.
                Examples: requests, flask, rich, numpy, pillow
            </p>

            <div
                id="packageOutput"
                class="package-output">

                Ready.

            </div>

        </div>

    </div>

</section>

</main>

</div>


<script>

const examples = """ + json.dumps(EXAMPLES) + r""";

const translations = """ + json.dumps(TRANSLATIONS) + r""";

let currentUILanguage = "en";

let currentLanguage = "python";


// ========================================================
// LANGUAGE
// ========================================================

function changeUILanguage() {

    currentUILanguage =
        document.getElementById(
            "languageSelect"
        ).value;

    const t =
        translations[currentUILanguage];

    document.getElementById("brand").textContent =
        t.brand;

    document.getElementById("subtitle").textContent =
        t.subtitle;

    document.getElementById("outputTitle").textContent =
        t.output;

    document.getElementById("status").textContent =
        t.ready;

    document.querySelectorAll(
        "button"
    ).forEach(button => {

        const text =
            button.textContent.trim();

        if (text.includes("Run") ||
            text.includes("Ausführen")) {

            button.textContent =
                t.run;

        }

    });

}


// ========================================================
// PAGE NAVIGATION
// ========================================================

function showPage(page) {

    const pages = [
        "editor",
        "examples",
        "playgrounds",
        "packages"
    ];

    pages.forEach(name => {

        const element =
            document.getElementById(
                "page-" + name
            );

        if (element) {
            element.style.display =
                name === page
                    ? "block"
                    : "none";
        }

    });

    if (page === "examples") {
        renderExamples();
    }

    if (page === "playgrounds") {
        loadPlaygrounds();
    }

}


// ========================================================
// LANGUAGE / EDITOR
// ========================================================

function changeLanguage() {

    currentLanguage =
        document.getElementById(
            "language"
        ).value;

    document.getElementById(
        "languageBadge"
    ).textContent =
        currentLanguage;

    document.getElementById(
        "editorTitle"
    ).textContent =
        currentLanguage.charAt(0).toUpperCase()
        + currentLanguage.slice(1)
        + " Playground";

    const list =
        examples[currentLanguage];

    if (list && list.length > 0) {

        document.getElementById(
            "editor"
        ).value =
            list[0].code;

    }

    document.getElementById(
        "status"
    ).textContent =
        "Example loaded.";

}


// ========================================================
// EXAMPLES
// ========================================================

function renderExamples() {

    const language =
        document.getElementById(
            "exampleLanguage"
        ).value;

    const grid =
        document.getElementById(
            "exampleGrid"
        );

    grid.innerHTML = "";

    const list =
        examples[language] || [];

    list.forEach((example, index) => {

        const card =
            document.createElement(
                "div"
            );

        card.className =
            "example-card";

        const title =
            document.createElement(
                "h3"
            );

        title.textContent =
            example.name;

        const description =
            document.createElement(
                "p"
            );

        description.textContent =
            "Ready-to-use " +
            language +
            " example.";

        const button =
            document.createElement(
                "button"
            );

        button.textContent =
            "Load Example";

        button.onclick =
            function() {

                document.getElementById(
                    "language"
                ).value =
                    language;

                currentLanguage =
                    language;

                document.getElementById(
                    "languageBadge"
                ).textContent =
                    language;

                document.getElementById(
                    "editor"
                ).value =
                    example.code;

                showPage("editor");

            };

        card.appendChild(title);

        card.appendChild(description);

        card.appendChild(button);

        grid.appendChild(card);

    });

}


// ========================================================
// RUN
// ========================================================

async function runCode() {

    const code =
        document.getElementById(
            "editor"
        ).value;

    const output =
        document.getElementById(
            "output"
        );

    const status =
        document.getElementById(
            "status"
        );

    if (!code.trim()) {

        output.textContent =
            "No code entered.";

        output.className =
            "output error";

        return;

    }

    output.className =
        "output";

    output.textContent =
        "Running...";

    status.textContent =
        "Running...";


    try {

        let endpoint = null;

        if (currentLanguage === "python") {

            endpoint =
                "/api/python/run";

        } else if (
            currentLanguage === "sql"
        ) {

            endpoint =
                "/api/sql/run";

        } else {

            /*
             * HTML/CSS/JS aren't executed
             * on the server.
             *
             * We show the source in the
             * output panel instead.
             */

            output.textContent =
                code;

            status.textContent =
                "Ready.";

            return;

        }


        const response =
            await fetch(
                endpoint,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        code: code
                    })
                }
            );


        const data =
            await response.json();


        output.textContent =
            data.output ||
            "No output.";

        output.className =
            data.success
                ? "output success"
                : "output error";

        status.textContent =
            data.success
                ? "Finished."
                : "Error.";

    }

    catch (error) {

        output.textContent =
            String(error);

        output.className =
            "output error";

        status.textContent =
            "Error.";

    }

}


// ========================================================
// CLEAR
// ========================================================

function clearEditor() {

    document.getElementById(
        "editor"
    ).value = "";

    document.getElementById(
        "output"
    ).textContent =
        "Ready.";

    document.getElementById(
        "status"
    ).textContent =
        "Ready.";

}


// ========================================================
// COPY
// ========================================================

async function copyCode() {

    const code =
        document.getElementById(
            "editor"
        ).value;

    await navigator.clipboard.writeText(
        code
    );

    document.getElementById(
        "status"
    ).textContent =
        "Copied.";

}


// ========================================================
// PACKAGES
// ========================================================

async function installPackage() {

    const packageName =
        document.getElementById(
            "packageInput"
        ).value.trim();

    const output =
        document.getElementById(
            "packageOutput"
        );

    if (!packageName) {

        output.textContent =
            "Enter a package name.";

        return;

    }

    output.textContent =
        "Installing " +
        packageName +
        "...";


    try {

        const response =
            await fetch(
                "/api/python/install",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        package:
                            packageName
                    })
                }
            );


        const data =
            await response.json();

        output.textContent =
            data.output ||
            "Finished.";

    }

    catch (error) {

        output.textContent =
            String(error);

    }

}


// ========================================================
// PLAYGROUNDS
// ========================================================

async function loadPlaygrounds() {

    const container =
        document.getElementById(
            "playgroundList"
        );

    container.textContent =
        "Loading...";


    try {

        const response =
            await fetch(
                "/api/playgrounds"
            );

        const list =
            await response.json();

        container.innerHTML = "";


        if (!list.length) {

            const empty =
                document.createElement(
                    "div"
                );

            empty.className =
                "empty";

            empty.textContent =
                "No saved playgrounds yet.";

            container.appendChild(
                empty
            );

            return;
        }


        list.forEach(item => {

            const row =
                document.createElement(
                    "div"
                );

            row.className =
                "playground";


            const info =
                document.createElement(
                    "div"
                );

            info.className =
                "playground-info";


            const strong =
                document.createElement(
                    "strong"
                );

            strong.textContent =
                item.name;


            const span =
                document.createElement(
                    "span"
                );

            span.textContent =
                item.language;


            info.appendChild(
                strong
            );

            info.appendChild(
                span
            );


            const actions =
                document.createElement(
                    "div"
                );

            actions.className =
                "playground-actions";


            const open =
                document.createElement(
                    "button"
                );

            open.textContent =
                "Open";

            open.onclick =
                function() {

                    document.getElementById(
                        "language"
                    ).value =
                        item.language;

                    currentLanguage =
                        item.language;

                    document.getElementById(
                        "languageBadge"
                    ).textContent =
                        item.language;

                    document.getElementById(
                        "editor"
                    ).value =
                        item.code;

                    showPage("editor");

                };


            const remove =
                document.createElement(
                    "button"
                );

            remove.textContent =
                "Delete";

            remove.className =
                "danger";

            remove.onclick =
                function() {

                    deletePlayground(
                        item.id
                    );

                };


            actions.appendChild(
                open
            );

            actions.appendChild(
                remove
            );


            row.appendChild(
                info
            );

            row.appendChild(
                actions
            );

            container.appendChild(
                row
            );

        });

    }

    catch (error) {

        container.textContent =
            String(error);

    }

}


// ========================================================
// NEW PLAYGROUND
// ========================================================

async function newPlayground() {

    const name =
        prompt(
            "Playground name:"
        );

    if (!name) {
        return;
    }

    const language =
        document.getElementById(
            "language"
        ).value;

    const code =
        document.getElementById(
            "editor"
        ).value;


    try {

        await fetch(
            "/api/playgrounds",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    name: name,
                    language: language,
                    code: code
                })
            }
        );

        loadPlaygrounds();

    }

    catch (error) {

        alert(String(error));

    }

}


// ========================================================
// DELETE PLAYGROUND
// ========================================================

async function deletePlayground(id) {

    if (!confirm(
        "Delete this playground?"
    )) {
        return;
    }

    await fetch(
        "/api/playgrounds/" + id,
        {
            method: "DELETE"
        }
    );

    loadPlaygrounds();

}


// ========================================================
// TAB SUPPORT
// ========================================================

document.getElementById(
    "editor"
).addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Tab") {

            event.preventDefault();

            const start =
                this.selectionStart;

            const end =
                this.selectionEnd;

            this.value =
                this.value.substring(
                    0,
                    start
                )
                +
                "    "
                +
                this.value.substring(
                    end
                );

            this.selectionStart =
                this.selectionEnd =
                    start + 4;

        }

    }
);


// ========================================================
// STARTUP
// ========================================================

document.getElementById(
    "editor"
).value =
    examples.python[0].code;

renderExamples();

</script>

</body>
</html>
"""


# ============================================================
# RENDER START
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("NEON PROGRAMMING HUB")
    print("=" * 60)
    print(f"Server: http://0.0.0.0:{PORT}")
    print("Render mode enabled.")
    print("No artificial code-size limit enabled.")
    print("=" * 60)

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True
            )
