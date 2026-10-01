import os
import sys
import json
import time
import sqlite3
import subprocess
import tempfile

from flask import Flask, request, jsonify, render_template_string


# ============================================================
# APP CONFIG
# ============================================================

app = Flask(__name__)

# No artificial application code-size limit.
# Real browser/server/memory limits still apply.
app.config["MAX_CONTENT_LENGTH"] = None

PORT = int(os.environ.get("PORT", "5000"))
HOST = "0.0.0.0"

PYTHON_TIMEOUT = 60
PIP_TIMEOUT = 180

DB_FILE = os.environ.get(
    "NEON_DB",
    os.path.join(
        tempfile.gettempdir(),
        "neon_programming_hub.db"
    )
)


# ============================================================
# DATABASE
# ============================================================

def get_db():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = get_db()

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
        "workspace": "Workspace",
        "editor": "Editor",
        "examples": "Examples",
        "playgrounds": "Playgrounds",
        "packages": "Packages",
        "run": "▶ Run",
        "clear": "🗑 Clear",
        "copy": "📋 Copy",
        "code": "Code",
        "output": "Output",
        "console": "Console",
        "ready": "Ready.",
        "running": "Running...",
        "finished": "Finished.",
        "error": "Error.",
        "copied": "Copied.",
        "example_loaded": "Example loaded.",
        "no_code": "No code entered.",
        "load": "Load Example",
        "load_playground": "Open",
        "delete": "Delete",
        "new_playground": "➕ New Playground",
        "save": "Save",
        "package_name": "Package name",
        "install": "📦 Install",
        "package_help": "Install packages directly from PyPI.",
        "ready_packages": "Ready.",
        "loading": "Loading...",
        "no_playgrounds": "No saved playgrounds yet.",
        "playground_name": "Playground name:",
        "saved": "Saved.",
        "deleted": "Deleted.",
        "language": "Language",
        "description": "Ready-to-use code example.",
        "html_preview": "HTML Preview",
        "css_preview": "CSS Preview",
        "javascript_output": "JavaScript output",
        "python": "Python",
        "html": "HTML",
        "css": "CSS",
        "javascript": "JavaScript",
        "sql": "SQL",
        "json": "JSON",
        "bash": "Bash",
        "markdown": "Markdown",
    },

    "de": {
        "brand": "NEON PROGRAMMING HUB",
        "subtitle": "Programmieren. Experimentieren. Bauen.",
        "workspace": "Arbeitsbereich",
        "editor": "Editor",
        "examples": "Beispiele",
        "playgrounds": "Playgrounds",
        "packages": "Pakete",
        "run": "▶ Ausführen",
        "clear": "🗑 Leeren",
        "copy": "📋 Kopieren",
        "code": "Code",
        "output": "Ausgabe",
        "console": "Konsole",
        "ready": "Bereit.",
        "running": "Wird ausgeführt...",
        "finished": "Fertig.",
        "error": "Fehler.",
        "copied": "Kopiert.",
        "example_loaded": "Beispiel geladen.",
        "no_code": "Kein Code eingegeben.",
        "load": "Beispiel laden",
        "load_playground": "Öffnen",
        "delete": "Löschen",
        "new_playground": "➕ Neuer Playground",
        "save": "Speichern",
        "package_name": "Paketname",
        "install": "📦 Installieren",
        "package_help": "Pakete direkt von PyPI installieren.",
        "ready_packages": "Bereit.",
        "loading": "Lädt...",
        "no_playgrounds": "Noch keine gespeicherten Playgrounds.",
        "playground_name": "Name des Playgrounds:",
        "saved": "Gespeichert.",
        "deleted": "Gelöscht.",
        "language": "Sprache",
        "description": "Fertiges Code-Beispiel.",
        "html_preview": "HTML-Vorschau",
        "css_preview": "CSS-Vorschau",
        "javascript_output": "JavaScript-Ausgabe",
        "python": "Python",
        "html": "HTML",
        "css": "CSS",
        "javascript": "JavaScript",
        "sql": "SQL",
        "json": "JSON",
        "bash": "Bash",
        "markdown": "Markdown",
    }
}


# ============================================================
# EXAMPLES
# ============================================================

EXAMPLES = {

    # --------------------------------------------------------
    # PYTHON
    # --------------------------------------------------------

    "python": [

        {
            "name": "Hello World",
            "code": '''print("Hello, world!")'''
        },

        {
            "name": "Calculator",
            "code": '''a = 25
b = 7

print("Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)
'''
        },

        {
            "name": "Loops",
            "code": '''for number in range(1, 11):
    print("Number:", number)
'''
        },

        {
            "name": "Lists",
            "code": '''players = [
    "Raphael",
    "Alex",
    "Steve",
    "Notch"
]

for player in players:
    print(player)
'''
        },

        {
            "name": "Functions",
            "code": '''def greet(name):
    return f"Hello, {name}!"

print(greet("Raphael"))
'''
        },

        {
            "name": "Dictionary",
            "code": '''player = {
    "name": "Raphael",
    "level": 42,
    "coins": 1337
}

print(player["name"])
print(player["level"])
print(player["coins"])
'''
        },

        {
            "name": "Random Numbers",
            "code": '''import random

number = random.randint(1, 100)

print("Random number:", number)
'''
        },

        {
            "name": "Date & Time",
            "code": '''from datetime import datetime

now = datetime.now()

print("Current time:")
print(now)
'''
        },

        {
            "name": "JSON",
            "code": '''import json

data = {
    "player": "Raphael",
    "level": 50,
    "online": True
}

print(json.dumps(data, indent=2))
'''
        },

        {
            "name": "Classes",
            "code": '''class Player:
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def info(self):
        print(self.name, "is level", self.level)


player = Player("Raphael", 100)

player.info()
'''
        },

        {
            "name": "Exception Handling",
            "code": '''try:
    number = int("hello")
except ValueError:
    print("That is not a number!")
'''
        },

        {
            "name": "Comprehension",
            "code": '''numbers = [1, 2, 3, 4, 5]

squares = [
    number * number
    for number in numbers
]

print(squares)
'''
        },

        {
            "name": "Counter",
            "code": '''from collections import Counter

items = [
    "apple",
    "banana",
    "apple",
    "orange",
    "banana",
    "apple"
]

counter = Counter(items)

print(counter)
'''
        },

        {
            "name": "HTTP Request",
            "code": '''import requests

response = requests.get(
    "https://example.com",
    timeout=10
)

print("Status:", response.status_code)
print(response.text[:500])
'''
        },

        {
            "name": "NumPy",
            "code": '''import numpy as np

numbers = np.array([
    1, 2, 3, 4, 5
])

print(numbers)
print("Mean:", numbers.mean())
print("Sum:", numbers.sum())
'''
        },

        {
            "name": "Rich",
            "code": '''from rich.console import Console

console = Console()

console.print(
    "[bold cyan]NEON PROGRAMMING HUB[/bold cyan]"
)

console.print(
    "[green]Everything works![/green]"
)
'''
        },

        {
            "name": "Mini Game",
            "code": '''import random

secret = random.randint(1, 10)

print("I picked a number from 1 to 10.")

guess = 5

print("Your guess:", guess)

if guess == secret:
    print("You won!")
else:
    print("The number was:", secret)
'''
        },

        {
            "name": "Fibonacci",
            "code": '''a = 0
b = 1

for _ in range(10):
    print(a)
    a, b = b, a + b
'''
        },

        {
            "name": "Prime Numbers",
            "code": '''for number in range(2, 50):

    prime = True

    for divisor in range(2, number):
        if number % divisor == 0:
            prime = False
            break

    if prime:
        print(number)
'''
        },

        {
            "name": "Pathlib",
            "code": '''from pathlib import Path

folder = Path("neon_test")

folder.mkdir(
    exist_ok=True
)

print("Folder:", folder)
print("Exists:", folder.exists())
'''
        }
    ],


    # --------------------------------------------------------
    # HTML
    # --------------------------------------------------------

    "html": [

        {
            "name": "Basic HTML",
            "code": '''<!DOCTYPE html>
<html>
<head>
    <title>Neon Page</title>
</head>

<body>

<h1>Hello World!</h1>

<p>Welcome to my website.</p>

</body>
</html>
'''
        },

        {
            "name": "Button",
            "code": '''<!DOCTYPE html>
<html>

<body>

<button onclick="alert('Hello!')">
    Click me
</button>

</body>
</html>
'''
        },

        {
            "name": "Card",
            "code": '''<div class="card">

    <h1>Neon Card</h1>

    <p>
        This is a simple HTML card.
    </p>

    <button>
        Open
    </button>

</div>
'''
        },

        {
            "name": "Form",
            "code": '''<!DOCTYPE html>
<html>

<body>

<h1>Login</h1>

<form>

    <input
        type="text"
        placeholder="Username"
    >

    <br><br>

    <input
        type="password"
        placeholder="Password"
    >

    <br><br>

    <button>
        Login
    </button>

</form>

</body>
</html>
'''
        },

        {
            "name": "Image",
            "code": '''<!DOCTYPE html>
<html>

<body>

<h1>Image Example</h1>

<img
    src="https://placehold.co/600x300"
    alt="Example image"
>

</body>
</html>
'''
        },

        {
            "name": "Video",
            "code": '''<!DOCTYPE html>
<html>

<body>

<h1>Video Player</h1>

<video controls width="700">

    <source
        src="video.mp4"
        type="video/mp4"
    >

</video>

</body>
</html>
'''
        },

        {
            "name": "Navigation",
            "code": '''<!DOCTYPE html>
<html>

<body>

<nav>

    <a href="#">Home</a>
    <a href="#">Projects</a>
    <a href="#">About</a>
    <a href="#">Contact</a>

</nav>

</body>
</html>
'''
        },

        {
            "name": "Canvas",
            "code": '''<!DOCTYPE html>
<html>

<body>

<canvas
    id="canvas"
    width="600"
    height="300">
</canvas>

<script>

const canvas =
    document.getElementById("canvas");

const ctx =
    canvas.getContext("2d");

ctx.fillRect(
    50,
    50,
    200,
    100
);

</script>

</body>
</html>
'''
        }
    ],


    # --------------------------------------------------------
    # CSS
    # --------------------------------------------------------

    "css": [

        {
            "name": "Neon Button",
            "code": '''.button {
    background: #080808;
    color: #00ffff;

    border: 2px solid #00ffff;

    padding: 15px 30px;

    border-radius: 12px;

    box-shadow:
        0 0 10px #00ffff;

    cursor: pointer;
}
'''
        },

        {
            "name": "Neon Card",
            "code": '''.card {
    background: #101018;

    border: 1px solid #8a2be2;

    border-radius: 20px;

    padding: 25px;

    box-shadow:
        0 0 25px
        rgba(138,43,226,0.5);
}
'''
        },

        {
            "name": "Animation",
            "code": '''@keyframes pulse {

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
    animation:
        pulse 2s infinite;
}
'''
        },

        {
            "name": "Gradient",
            "code": '''body {
    background:
        linear-gradient(
            135deg,
            #050509,
            #201040,
            #001f2b
        );

    color: white;
}
'''
        },

        {
            "name": "Grid",
            "code": '''.grid {
    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(200px, 1fr)
        );

    gap: 20px;
}
'''
        },

        {
            "name": "Glass",
            "code": '''.glass {
    background:
        rgba(255,255,255,0.08);

    backdrop-filter:
        blur(15px);

    border:
        1px solid
        rgba(255,255,255,0.15);

    border-radius: 20px;
}
'''
        }
    ],


    # --------------------------------------------------------
    # JAVASCRIPT
    # --------------------------------------------------------

    "javascript": [

        {
            "name": "Hello",
            "code": '''console.log(
    "Hello from JavaScript!"
);'''
        },

        {
            "name": "Counter",
            "code": '''let counter = 0;

counter++;

console.log(
    "Counter:",
    counter
);'''
        },

        {
            "name": "Function",
            "code": '''function greet(name) {
    return `Hello, ${name}!`;
}

console.log(
    greet("Raphael")
);'''
        },

        {
            "name": "Array",
            "code": '''const players = [
    "Steve",
    "Alex",
    "Raphael"
];

players.forEach(player => {
    console.log(player);
});'''
        },

        {
            "name": "Object",
            "code": '''const player = {
    name: "Raphael",
    level: 100,
    online: true
};

console.log(player);'''
        },

        {
            "name": "Random Number",
            "code": '''const number =
    Math.floor(
        Math.random() * 100
    ) + 1;

console.log(
    "Random:",
    number
);'''
        },

        {
            "name": "Timer",
            "code": '''console.log("Starting...");

setTimeout(() => {

    console.log(
        "Finished!"
    );

}, 1000);'''
        },

        {
            "name": "Map",
            "code": '''const numbers = [
    1, 2, 3, 4, 5
];

const doubled =
    numbers.map(
        number => number * 2
    );

console.log(doubled);'''
        }
    ],


    # --------------------------------------------------------
    # SQL
    # --------------------------------------------------------

    "sql": [

        {
            "name": "Create Table",
            "code": '''CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    name TEXT,
    level INTEGER
);

INSERT INTO players
(name, level)
VALUES
('Raphael', 42);

SELECT * FROM players;
'''
        },

        {
            "name": "Multiple Players",
            "code": '''CREATE TABLE players (
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
'''
        },

        {
            "name": "WHERE",
            "code": '''CREATE TABLE players (
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
'''
        },

        {
            "name": "COUNT",
            "code": '''CREATE TABLE players (
    name TEXT,
    level INTEGER
);

INSERT INTO players VALUES
('Steve', 10),
('Alex', 50),
('Raphael', 100);

SELECT COUNT(*) AS total
FROM players;
'''
        },

        {
            "name": "GROUP BY",
            "code": '''CREATE TABLE players (
    name TEXT,
    team TEXT
);

INSERT INTO players VALUES
('Steve', 'Red'),
('Alex', 'Blue'),
('Raphael', 'Red'),
('Notch', 'Blue');

SELECT
    team,
    COUNT(*) AS players
FROM players
GROUP BY team;
'''
        }
    ],


    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    "json": [

        {
            "name": "Player",
            "code": '''{
    "name": "Raphael",
    "level": 100,
    "online": true
}'''
        },

        {
            "name": "Server",
            "code": '''{
    "server": "Neon SMP",
    "online": true,
    "players": 42,
    "max_players": 100
}'''
        },

        {
            "name": "Settings",
            "code": '''{
    "theme": "neon",
    "language": "de",
    "notifications": true,
    "fullscreen": false
}'''
        }
    ],


    # --------------------------------------------------------
    # BASH
    # --------------------------------------------------------

    "bash": [

        {
            "name": "Hello",
            "code": '''echo "Hello from Bash!"'''
        },

        {
            "name": "Variables",
            "code": '''NAME="Raphael"

echo "Hello $NAME!"'''
        },

        {
            "name": "Loop",
            "code": '''for number in 1 2 3 4 5
do
    echo "Number: $number"
done'''
        },

        {
            "name": "System",
            "code": '''echo "System information:"
uname -a'''
        }
    ],


    # --------------------------------------------------------
    # MARKDOWN
    # --------------------------------------------------------

    "markdown": [

        {
            "name": "README",
            "code": '''# Neon Project

Welcome to my project!

## Features

- Fast
- Simple
- Open
- Neon

## Installation

Run the project and enjoy!'''
        },

        {
            "name": "Table",
            "code": '''# Players

| Name | Level |
|------|------:|
| Steve | 20 |
| Alex | 35 |
| Raphael | 100 |'''
        },

        {
            "name": "Checklist",
            "code": '''# TODO

- [x] Create project
- [x] Add editor
- [ ] Add more examples
- [ ] Publish project'''
        }
    ]
}


# ============================================================
# LANGUAGE LABELS
# ============================================================

LANGUAGE_LABELS = {
    "python": "Python",
    "html": "HTML",
    "css": "CSS",
    "javascript": "JavaScript",
    "sql": "SQL",
    "json": "JSON",
    "bash": "Bash",
    "markdown": "Markdown"
}


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
            [
                sys.executable,
                temp_path
            ],
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
            "output": (
                "Execution timed out after "
                f"{PYTHON_TIMEOUT} seconds."
            )
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

            output = (
                "SQL executed successfully."
            )

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
            "output": (
                "Package installation timed out."
            )
        }

    except Exception as exc:

        return {
            "success": False,
            "output": str(exc)
        }


# ============================================================
# API
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

    data = request.get_json(
        silent=True
    ) or {}

    return jsonify(
        execute_python(
            data.get("code", "")
        )
    )


@app.post("/api/python/install")
def api_python_install():

    data = request.get_json(
        silent=True
    ) or {}

    return jsonify(
        install_package(
            data.get("package", "")
        )
    )


@app.post("/api/sql/run")
def api_sql_run():

    data = request.get_json(
        silent=True
    ) or {}

    return jsonify(
        execute_sql(
            data.get("code", "")
        )
    )


@app.get("/api/examples")
def api_examples():

    return jsonify(EXAMPLES)


@app.get("/api/playgrounds")
def api_playgrounds():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            name,
            language,
            code,
            created_at
        FROM playgrounds
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify([
        {
            "id": row[0],
            "name": row[1],
            "language": row[2],
            "code": row[3],
            "created_at": row[4]
        }
        for row in rows
    ])


@app.post("/api/playgrounds")
def api_create_playground():

    data = request.get_json(
        silent=True
    ) or {}

    name = data.get(
        "name",
        "Untitled Playground"
    )

    language = data.get(
        "language",
        "python"
    )

    code = data.get(
        "code",
        ""
    )

    conn = get_db()

    cursor = conn.execute(
        """
        INSERT INTO playgrounds
        (name, language, code, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            language,
            code,
            time.time()
        )
    )

    conn.commit()

    playground_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "success": True,
        "id": playground_id
    })


@app.put("/api/playgrounds/<int:playground_id>")
def api_update_playground(
    playground_id
):

    data = request.get_json(
        silent=True
    ) or {}

    name = data.get("name")
    language = data.get("language")
    code = data.get("code")

    conn = get_db()

    conn.execute(
        """
        UPDATE playgrounds
        SET name = ?,
            language = ?,
            code = ?
        WHERE id = ?
        """,
        (
            name,
            language,
            code,
            playground_id
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


@app.delete(
    "/api/playgrounds/<int:playground_id>"
)
def api_delete_playground(
    playground_id
):

    conn = get_db()

    conn.execute(
        """
        DELETE FROM playgrounds
        WHERE id = ?
        """,
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
        0 0 25px
        rgba(0,255,255,.25);
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

    border:
        1px solid var(--border);

    border-radius: 10px;

    padding: 10px 12px;

    outline: none;
}

select:focus,
input:focus {
    border-color: var(--cyan);

    box-shadow:
        0 0 0 2px
        rgba(0,255,255,.08);
}

button {
    border:
        1px solid var(--border);

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
        0 20px 60px
        rgba(0,0,0,.22);
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

    background: #07070d;

    color: #e9e9ff;

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

    background: #050507;

    font-family:
        "JetBrains Mono",
        Consolas,
        monospace;

    white-space: pre-wrap;

    word-break: break-word;

    color: #d8d8e8;
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
        repeat(
            auto-fill,
            minmax(220px, 1fr)
        );

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

        <select
            id="languageSelect"
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

        <div
            class="sidebar-title"
            id="workspaceTitle">

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

            <select
                id="language"
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

                <option value="json">
                    JSON
                </option>

                <option value="bash">
                    Bash
                </option>

                <option value="markdown">
                    Markdown
                </option>

            </select>

            <button
                onclick="clearEditor()"
                id="clearButton">

                🗑 Clear

            </button>

            <button
                onclick="copyCode()"
                id="copyButton">

                📋 Copy

            </button>

            <button
                class="primary"
                onclick="runCode()"
                id="runButton">

                ▶ Run

            </button>

        </div>

    </div>


    <div class="editor-layout">

        <div class="panel">

            <div class="panel-header">

                <strong id="codeTitle">
                    Code
                </strong>

                <span
                    class="badge"
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

                <span
                    class="status"
                    id="consoleTitle">

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

<section
    id="page-examples"
    style="display:none;">

    <div class="topbar">

        <div class="title">

            <h2 id="examplesTitle">
                Examples
            </h2>

            <p id="examplesDescription">
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

            <option value="json">
                JSON
            </option>

            <option value="bash">
                Bash
            </option>

            <option value="markdown">
                Markdown
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

<section
    id="page-playgrounds"
    style="display:none;">

    <div class="topbar">

        <div class="title">

            <h2 id="playgroundsTitle">
                Playgrounds
            </h2>

            <p id="playgroundsDescription">
                Save your own coding projects.
            </p>

        </div>

        <button
            class="primary"
            onclick="newPlayground()"
            id="newPlaygroundButton">

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

<section
    id="page-packages"
    style="display:none;">

    <div class="topbar">

        <div class="title">

            <h2 id="packagesTitle">
                Packages
            </h2>

            <p id="packagesDescription">
                Install packages from PyPI.
            </p>

        </div>

    </div>


    <div class="panel">

        <div class="package-box">

            <div
                class="sidebar-title"
                id="packageNameLabel">

                Package name

            </div>

            <div class="package-row">

                <input
                    id="packageInput"
                    placeholder="requests">

                <button
                    class="primary"
                    onclick="installPackage()"
                    id="installButton">

                    📦 Install

                </button>

            </div>

            <p
                class="status"
                id="packageHelp">

                Install any package available
                from PyPI.

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

const examples =
""" + json.dumps(EXAMPLES) + r""";

const translations =
""" + json.dumps(TRANSLATIONS) + r""";

const languageLabels =
""" + json.dumps(LANGUAGE_LABELS) + r""";


let currentUILanguage = "en";

let currentLanguage = "python";


function t(key) {

    return (
        translations[currentUILanguage][key]
        ||
        translations.en[key]
        ||
        key
    );

}


function languageName(language) {

    const label =
        languageLabels[language];

    if (label) {
        return label;
    }

    return language;
}


// ========================================================
// UI LANGUAGE
// ========================================================

function changeUILanguage() {

    currentUILanguage =
        document.getElementById(
            "languageSelect"
        ).value;

    applyTranslations();

    renderExamples();

    updateEditorLanguage();

}


function applyTranslations() {

    document.getElementById(
        "brand"
    ).textContent =
        t("brand");

    document.getElementById(
        "subtitle"
    ).textContent =
        t("subtitle");

    document.getElementById(
        "workspaceTitle"
    ).textContent =
        t("workspace");

    document.getElementById(
        "navEditor"
    ).textContent =
        "💻 " + t("editor");

    document.getElementById(
        "navExamples"
    ).textContent =
        "📚 " + t("examples");

    document.getElementById(
        "navPlaygrounds"
    ).textContent =
        "🧪 " + t("playgrounds");

    document.getElementById(
        "navPackages"
    ).textContent =
        "📦 " + t("packages");

    document.getElementById(
        "clearButton"
    ).textContent =
        t("clear");

    document.getElementById(
        "copyButton"
    ).textContent =
        t("copy");

    document.getElementById(
        "runButton"
    ).textContent =
        t("run");

    document.getElementById(
        "codeTitle"
    ).textContent =
        t("code");

    document.getElementById(
        "outputTitle"
    ).textContent =
        t("output");

    document.getElementById(
        "consoleTitle"
    ).textContent =
        t("console");

    document.getElementById(
        "examplesTitle"
    ).textContent =
        t("examples");

    document.getElementById(
        "examplesDescription"
    ).textContent =
        t("description");

    document.getElementById(
        "playgroundsTitle"
    ).textContent =
        t("playgrounds");

    document.getElementById(
        "playgroundsDescription"
    ).textContent =
        currentUILanguage === "de"
            ? "Speichere deine eigenen Coding-Projekte."
            : "Save your own coding projects.";

    document.getElementById(
        "newPlaygroundButton"
    ).textContent =
        t("new_playground");

    document.getElementById(
        "packagesTitle"
    ).textContent =
        t("packages");

    document.getElementById(
        "packagesDescription"
    ).textContent =
        currentUILanguage === "de"
            ? "Installiere Python-Pakete von PyPI."
            : "Install Python packages from PyPI.";

    document.getElementById(
        "packageNameLabel"
    ).textContent =
        t("package_name");

    document.getElementById(
        "installButton"
    ).textContent =
        t("install");

    document.getElementById(
        "packageHelp"
    ).textContent =
        t("package_help");

}


// ========================================================
// NAVIGATION
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

        if (!element) {
            return;
        }

        element.style.display =
            name === page
                ? "block"
                : "none";

    });


    document.querySelectorAll(
        ".nav-button"
    ).forEach(button => {

        button.classList.remove(
            "active"
        );

    });


    const navMap = {
        editor: "navEditor",
        examples: "navExamples",
        playgrounds: "navPlaygrounds",
        packages: "navPackages"
    };


    const active =
        document.getElementById(
            navMap[page]
        );

    if (active) {
        active.classList.add(
            "active"
        );
    }


    if (page === "examples") {
        renderExamples();
    }


    if (page === "playgrounds") {
        loadPlaygrounds();
    }

}


// ========================================================
// EDITOR LANGUAGE
// ========================================================

function changeLanguage() {

    currentLanguage =
        document.getElementById(
            "language"
        ).value;

    updateEditorLanguage();


    const list =
        examples[currentLanguage];

    if (
        list &&
        list.length > 0
    ) {

        document.getElementById(
            "editor"
        ).value =
            list[0].code;

        document.getElementById(
            "status"
        ).textContent =
            t("example_loaded");

    }

}


function updateEditorLanguage() {

    const label =
        languageName(
            currentLanguage
        );

    document.getElementById(
        "languageBadge"
    ).textContent =
        label;

    document.getElementById(
        "editorTitle"
    ).textContent =
        label +
        " Playground";

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


    list.forEach(example => {

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
            t("description");


        const button =
            document.createElement(
                "button"
            );

        button.textContent =
            t("load");


        button.onclick =
            function() {

                document.getElementById(
                    "language"
                ).value =
                    language;

                currentLanguage =
                    language;

                updateEditorLanguage();

                document.getElementById(
                    "editor"
                ).value =
                    example.code;

                document.getElementById(
                    "status"
                ).textContent =
                    t("example_loaded");

                showPage(
                    "editor"
                );

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
            t("no_code");

        output.className =
            "output error";

        status.textContent =
            t("error");

        return;

    }


    output.className =
        "output";

    output.textContent =
        t("running");

    status.textContent =
        t("running");


    try {

        let endpoint = null;


        if (
            currentLanguage ===
            "python"
        ) {

            endpoint =
                "/api/python/run";

        }


        else if (
            currentLanguage ===
            "sql"
        ) {

            endpoint =
                "/api/sql/run";

        }


        else {

            /*
             * HTML, CSS, JavaScript,
             * JSON, Bash and Markdown
             * are shown directly in the
             * output panel.
             *
             * Python and SQL are executed
             * server-side.
             */

            if (
                currentLanguage ===
                "html"
            ) {

                const iframe =
                    document.createElement(
                        "iframe"
                    );

                iframe.style.width =
                    "100%";

                iframe.style.height =
                    "100%";

                iframe.style.border =
                    "0";

                iframe.srcdoc =
                    code;

                output.innerHTML =
                    "";

                output.appendChild(
                    iframe
                );

            }

            else {

                output.textContent =
                    code;

            }


            status.textContent =
                t("finished");

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

                    body:
                        JSON.stringify({
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
                ? t("finished")
                : t("error");

    }

    catch (error) {

        output.textContent =
            String(error);

        output.className =
            "output error";

        status.textContent =
            t("error");

    }

}


// ========================================================
// CLEAR
// ========================================================

function clearEditor() {

    document.getElementById(
        "editor"
    ).value =
        "";

    document.getElementById(
        "output"
    ).textContent =
        t("ready");

    document.getElementById(
        "output"
    ).className =
        "output";

    document.getElementById(
        "status"
    ).textContent =
        t("ready");

}


// ========================================================
// COPY
// ========================================================

async function copyCode() {

    const code =
        document.getElementById(
            "editor"
        ).value;

    try {

        await navigator.clipboard
            .writeText(code);

        document.getElementById(
            "status"
        ).textContent =
            t("copied");

    }

    catch (error) {

        document.getElementById(
            "status"
        ).textContent =
            String(error);

    }

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
            currentUILanguage === "de"
                ? "Bitte einen Paketnamen eingeben."
                : "Enter a package name.";

        return;

    }


    output.textContent =
        (
            currentUILanguage === "de"
                ? "Installiere "
                : "Installing "
        )
        +
        packageName
        +
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

                    body:
                        JSON.stringify({
                            package:
                                packageName
                        })
                }
            );


        const data =
            await response.json();

        output.textContent =
            data.output ||
            t("finished");

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
        t("loading");


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
                t("no_playgrounds");

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
                languageName(
                    item.language
                );


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
                t("load_playground");


            open.onclick =
                function() {

                    document.getElementById(
                        "language"
                    ).value =
                        item.language;

                    currentLanguage =
                        item.language;

                    updateEditorLanguage();

                    document.getElementById(
                        "editor"
                    ).value =
                        item.code;

                    document.getElementById(
                        "status"
                    ).textContent =
                        t("example_loaded");

                    showPage(
                        "editor"
                    );

                };


            const remove =
                document.createElement(
                    "button"
                );

            remove.textContent =
                t("delete");

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
            t("playground_name")
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

        const response =
            await fetch(
                "/api/playgrounds",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            name: name,
                            language: language,
                            code: code
                        })
                }
            );


        const data =
            await response.json();


        if (data.success) {

            showPage(
                "playgrounds"
            );

        }

    }

    catch (error) {

        alert(
            String(error)
        );

    }

}


// ========================================================
// DELETE PLAYGROUND
// ========================================================

async function deletePlayground(
    id
) {

    const question =
        currentUILanguage === "de"
            ? "Diesen Playground löschen?"
            : "Delete this playground?";


    if (!confirm(question)) {
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

        if (event.key !== "Tab") {
            return;
        }

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
);


// ========================================================
// STARTUP
// ========================================================

document.getElementById(
    "editor"
).value =
    examples.python[0].code;


applyTranslations();

renderExamples();

updateEditorLanguage();

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
    print(
        f"Server: http://{HOST}:{PORT}"
    )
    print("Render mode enabled.")
    print("No artificial code-size limit.")
    print("PyPI package installation enabled.")
    print("=" * 60)

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True
)
