from flask import Flask, render_template_string, request, jsonify
import subprocess
import sys
import tempfile
import os
import sqlite3

app = Flask(__name__)

PYTHON_TIMEOUT = 50

# Packages that the web interface is allowed to install.
ALLOWED_PACKAGES = {
    "requests",
    "colorama",
    "rich",
    "numpy",
    "pillow",
}

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

html,
body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;

    font-family: Arial, sans-serif;
    color: white;

    background:
        radial-gradient(
            circle at 20% 20%,
            #7c3aed55,
            transparent 35%
        ),
        radial-gradient(
            circle at 80% 80%,
            #2563eb55,
            transparent 35%
        ),
        #050510;
}

.grid {
    position: fixed;
    inset: 0;

    background-image:
        linear-gradient(
            rgba(255,255,255,0.03) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,0.03) 1px,
            transparent 1px
        );

    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

.screen {
    position: fixed;
    inset: 0;

    width: 100%;
    height: 100%;

    display: none;

    z-index: 1;

    overflow-y: auto;
    overflow-x: hidden;

    padding: 15px;

    -webkit-overflow-scrolling: touch;
}

.screen.active {
    display: block;
    animation: screenIn 0.3s ease;
}

@keyframes screenIn {
    from {
        opacity: 0;
        transform: scale(0.97);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

.center {
    min-height: 100%;

    display: flex;
    justify-content: center;
    align-items: center;

    padding: 20px;
}

.card {
    width: min(850px, 100%);

    padding: 50px 25px;

    text-align: center;

    background: rgba(10, 10, 30, 0.84);

    border:
        1px solid
        rgba(180, 130, 255, 0.35);

    border-radius: 30px;

    box-shadow:
        0 0 50px
        rgba(120, 50, 255, 0.3);

    backdrop-filter: blur(15px);
}

.badge {
    display: inline-block;

    padding: 8px 16px;

    border-radius: 999px;

    background:
        rgba(130, 80, 255, 0.15);

    border:
        1px solid
        rgba(170, 120, 255, 0.4);

    color: #c4a7ff;

    font-size: 13px;

    margin-bottom: 20px;
}

h1 {
    margin: 0;

    font-size:
        clamp(50px, 12vw, 90px);

    letter-spacing: -4px;

    background:
        linear-gradient(
            90deg,
            white,
            #c084fc,
            #60a5fa,
            white
        );

    background-size: 300%;

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    animation: gradient 5s infinite;
}

@keyframes gradient {
    0% {
        background-position: 0%;
    }

    50% {
        background-position: 100%;
    }

    100% {
        background-position: 0%;
    }
}

h2 {
    margin: 0;

    font-size:
        clamp(40px, 9vw, 70px);

    background:
        linear-gradient(
            90deg,
            #60a5fa,
            #c084fc
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

p {
    color: #aaa9c5;

    font-size: 17px;

    line-height: 1.5;
}

.status {
    display: inline-block;

    margin-top: 20px;

    padding: 12px 20px;

    border-radius: 12px;

    background:
        rgba(0, 255, 150, 0.08);

    border:
        1px solid
        rgba(0, 255, 150, 0.25);

    color: #5dffb0;
}

.button {
    display: inline-block;

    margin-top: 20px;

    padding: 14px 22px;

    border: none;
    border-radius: 13px;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #2563eb
        );

    color: white;

    font-size: 15px;
    font-weight: bold;

    cursor: pointer;

    box-shadow:
        0 8px 25px
        rgba(80, 50, 255, 0.3);

    transition: 0.2s;

    -webkit-tap-highlight-color: transparent;
}

.button:active {
    transform: scale(0.96);
}

.hub {
    width: min(1100px, 100%);

    margin: auto;

    text-align: center;

    padding: 20px 0 50px;
}

.languages {
    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(155px, 1fr)
        );

    gap: 14px;

    margin-top: 25px;
}

.language {
    padding: 22px 12px;

    background:
        rgba(15, 15, 35, 0.85);

    border:
        1px solid
        rgba(255, 255, 255, 0.08);

    border-radius: 20px;

    cursor: pointer;

    transition: 0.2s;

    -webkit-tap-highlight-color: transparent;
}

.language:hover {
    transform: translateY(-4px);

    border-color:
        rgba(180, 130, 255, 0.4);

    box-shadow:
        0 10px 35px
        rgba(100, 50, 255, 0.18);
}

.language:active {
    transform: scale(0.96);
}

.language-icon {
    font-size: 40px;
    margin-bottom: 8px;
}

.language h3 {
    margin: 7px 0;
    font-size: 19px;
}

.language p {
    margin: 0;
    font-size: 13px;
    color: #88879e;
}

.tutorial {
    width: min(1000px, 100%);

    margin: auto;

    padding: 10px 0 60px;
}

.tutorial-header {
    text-align: center;
    margin-bottom: 25px;
}

.tutorial-icon {
    font-size: 65px;
}

.lesson {
    background:
        rgba(12, 12, 32, 0.92);

    border:
        1px solid
        rgba(180, 130, 255, 0.2);

    border-radius: 20px;

    padding: 22px;

    margin-bottom: 18px;

    text-align: left;
}

.lesson h3 {
    margin-top: 0;
    color: #c4a7ff;
    font-size: 22px;
}

.lesson p {
    font-size: 15px;
}

pre {
    background: #030308;

    border:
        1px solid
        rgba(255, 255, 255, 0.08);

    border-radius: 14px;

    padding: 16px;

    overflow-x: auto;

    color: #e8e5ff;

    font-family:
        Consolas,
        monospace;

    font-size: 14px;

    line-height: 1.6;
}

.terminal {
    background: #020205;

    border:
        1px solid
        rgba(255, 255, 255, 0.1);

    border-radius: 18px;

    overflow: hidden;

    margin-top: 15px;
}

.terminal-top {
    padding: 10px 14px;

    background: #11111b;

    display: flex;

    gap: 7px;

    align-items: center;
}

.term-dot {
    width: 11px;
    height: 11px;

    border-radius: 50%;

    background: #555;
}

.terminal-title {
    margin-left: 8px;

    color: #999;

    font-size: 13px;
}

.terminal-body {
    padding: 18px;

    min-height: 130px;

    font-family: Consolas, monospace;

    font-size: 14px;

    line-height: 1.6;

    white-space: pre-wrap;

    overflow-x: auto;

    color: #d9d5ff;
}

.editor {
    width: 100%;

    min-height: 220px;

    resize: vertical;

    background: #030308;

    color: #e8e5ff;

    border:
        1px solid
        rgba(255, 255, 255, 0.1);

    border-radius: 14px;

    padding: 16px;

    font-family: Consolas, monospace;

    font-size: 14px;

    line-height: 1.6;

    outline: none;
}

.editor:focus {
    border-color: #7c3aed;
}

.output {
    background: #020205;

    color: #d9d5ff;

    min-height: 100px;

    border:
        1px solid
        rgba(255, 255, 255, 0.1);

    border-radius: 14px;

    padding: 15px;

    font-family: Consolas, monospace;

    white-space: pre-wrap;

    overflow-x: auto;
}

.controls {
    display: flex;

    gap: 10px;

    flex-wrap: wrap;

    margin: 12px 0;
}

.input {
    flex: 1;

    min-width: 180px;

    padding: 13px;

    background: #080812;

    border:
        1px solid
        rgba(255, 255, 255, 0.1);

    border-radius: 10px;

    color: white;

    outline: none;
}

.small-button {
    padding: 12px 18px;

    border: none;

    border-radius: 10px;

    background: #27204b;

    color: white;

    cursor: pointer;

    font-weight: bold;
}

.packages {
    display: flex;

    flex-wrap: wrap;

    gap: 8px;

    margin-top: 12px;
}

.package {
    padding: 7px 11px;

    border-radius: 999px;

    background:
        rgba(124, 58, 237, 0.15);

    border:
        1px solid
        rgba(124, 58, 237, 0.3);

    color: #cdb8ff;

    font-size: 12px;
}

.preview {
    width: 100%;
    height: 300px;

    border:
        1px solid
        rgba(255, 255, 255, 0.1);

    border-radius: 14px;

    background: white;
}

@media (max-width: 600px) {

    .screen {
        padding: 10px;
    }

    .card {
        padding: 40px 18px;
    }

    .languages {
        grid-template-columns: 1fr 1fr;
    }

    .lesson {
        padding: 18px;
    }

    .tutorial {
        padding-top: 5px;
    }

}

@media (max-width: 360px) {

    .languages {
        grid-template-columns: 1fr;
    }

}

</style>

</head>


<body>

<div class="grid"></div>


<!-- ============================================================
     HOME
============================================================ -->

<div id="home" class="screen active">

<div class="center">

<div class="card">

<div class="badge">
🌐 LOCAL • FLASK • ONLINE
</div>

<h1>NEON</h1>

<p>
Your local programming laboratory.
Learn, experiment and build.
</p>

<div class="status">
🟢 SERVER ONLINE
</div>

<br>

<button
    class="button"
    onclick="showScreen('languages')"
>
🚀 Programming Academy
</button>

<br>

<button
    class="button"
    onclick="showScreen('python-test')"
>
🧪 Python Test Area
</button>

</div>

</div>

</div>


<!-- ============================================================
     LANGUAGES
============================================================ -->

<div id="languages" class="screen">

<div class="hub">

<div class="badge">
💻 PROGRAMMING ACADEMY
</div>

<h2>Languages</h2>

<p>
Choose a language to start learning.
</p>

<div class="languages">


<div class="language" onclick="showScreen('python')">
<div class="language-icon">🐍</div>
<h3>Python</h3>
<p>General programming</p>
</div>


<div class="language" onclick="showScreen('html')">
<div class="language-icon">🌐</div>
<h3>HTML</h3>
<p>Web structure</p>
</div>


<div class="language" onclick="showScreen('css')">
<div class="language-icon">🎨</div>
<h3>CSS</h3>
<p>Web design</p>
</div>


<div class="language" onclick="showScreen('javascript')">
<div class="language-icon">⚡</div>
<h3>JavaScript</h3>
<p>Web interaction</p>
</div>


<div class="language" onclick="showScreen('java')">
<div class="language-icon">☕</div>
<h3>Java</h3>
<p>Applications</p>
</div>


<div class="language" onclick="showScreen('c')">
<div class="language-icon">💻</div>
<h3>C</h3>
<p>Low-level programming</p>
</div>


<div class="language" onclick="showScreen('cpp')">
<div class="language-icon">🔷</div>
<h3>C++</h3>
<p>Games & applications</p>
</div>


<div class="language" onclick="showScreen('csharp')">
<div class="language-icon">🟣</div>
<h3>C#</h3>
<p>.NET & games</p>
</div>


<div class="language" onclick="showScreen('rust')">
<div class="language-icon">🦀</div>
<h3>Rust</h3>
<p>Fast & safe</p>
</div>


<div class="language" onclick="showScreen('php')">
<div class="language-icon">🐘</div>
<h3>PHP</h3>
<p>Web backend</p>
</div>


<div class="language" onclick="showScreen('ruby')">
<div class="language-icon">💎</div>
<h3>Ruby</h3>
<p>Readable programming</p>
</div>


<div class="language" onclick="showScreen('go')">
<div class="language-icon">🐹</div>
<h3>Go</h3>
<p>Backend development</p>
</div>


<div class="language" onclick="showScreen('kotlin')">
<div class="language-icon">🦫</div>
<h3>Kotlin</h3>
<p>Modern JVM</p>
</div>


<div class="language" onclick="showScreen('swift')">
<div class="language-icon">🐦</div>
<h3>Swift</h3>
<p>Apple development</p>
</div>


<div class="language" onclick="showScreen('sql')">
<div class="language-icon">🗄️</div>
<h3>SQL</h3>
<p>Databases</p>
</div>


</div>

<button
    class="button"
    onclick="showScreen('home')"
>
← Back Home
</button>

</div>

</div>


<!-- ============================================================
     PYTHON
============================================================ -->

<div id="python" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🐍</div>

<h2>Python</h2>

<p>
Learn Python from the basics.
</p>

</div>


<div class="lesson">

<h3>1. Hello World</h3>

<p>
The print function displays text.
</p>

<pre>print("Hello, World!")</pre>

</div>


<div class="lesson">

<h3>2. Variables</h3>

<pre>name = "Neon"
age = 15

print(name)
print(age)</pre>

</div>


<div class="lesson">

<h3>3. Conditions</h3>

<pre>age = 15

if age >= 18:
    print("Adult")
else:
    print("Not an adult")</pre>

</div>


<div class="lesson">

<h3>4. Loops</h3>

<pre>for number in range(5):
    print(number)</pre>

</div>


<div class="lesson">

<h3>💻 Python Tutorial Terminal</h3>

<div class="terminal">

<div class="terminal-top">

<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>

<span class="terminal-title">
Python
</span>

</div>

<div class="terminal-body">>>> print("Hello!")
Hello!

>>> 2 + 3
5

>>> name = "Neon"
>>> print(name)
Neon</div>

</div>

<button
    class="button"
    onclick="showScreen('python-test')"
>
🧪 Open Python Test Area
</button>

</div>


<button
    class="button"
    onclick="showScreen('languages')"
>
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     PYTHON TEST AREA
============================================================ -->

<div id="python-test" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🧪</div>

<h2>Python Test Area</h2>

<p>
Write Python and execute it using Pydroid's Python.
</p>

</div>


<div class="lesson">

<h3>🐍 Python Editor</h3>

<textarea
    id="pythonCode"
    class="editor"
    spellcheck="false"
>print("Hello from Neon!")

numbers = [1, 2, 3, 4, 5]

for number in numbers:
    print(number)</textarea>

<div class="controls">

<button
    class="small-button"
    onclick="runPython()"
>
▶ Run
</button>

<button
    class="small-button"
    onclick="clearPython()"
>
🗑 Clear
</button>

</div>

<h3>Output</h3>

<pre
    id="pythonOutput"
    class="output"
>Ready.</pre>

</div>


<div class="lesson">

<h3>📦 Install Python Library</h3>

<p>
Choose one of the supported libraries.
</p>

<div class="controls">

<input
    id="packageName"
    class="input"
    placeholder="Example: requests"
>

<button
    class="small-button"
    onclick="installPackage()"
>
📦 Install
</button>

</div>

<div class="packages">

<span class="package">requests</span>
<span class="package">colorama</span>
<span class="package">rich</span>
<span class="package">numpy</span>
<span class="package">pillow</span>

</div>

<pre
    id="packageOutput"
    class="output"
>Installer ready.</pre>

</div>


<div class="lesson">

<h3>⚠️ Local Execution</h3>

<p>
The Python editor runs code on the device where
this Flask server is running. Do not expose this
server to untrusted users.
</p>

</div>


<button
    class="button"
    onclick="showScreen('languages')"
>
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     HTML
============================================================ -->

<div id="html" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🌐</div>

<h2>HTML</h2>

<p>Build webpages.</p>

</div>


<div class="lesson">

<h3>Basic HTML</h3>

<pre>&lt;!DOCTYPE html&gt;

&lt;html&gt;

&lt;body&gt;

    &lt;h1&gt;Hello!&lt;/h1&gt;

    &lt;p&gt;
        My website!
    &lt;/p&gt;

&lt;/body&gt;

&lt;/html&gt;</pre>

</div>


<div class="lesson">

<h3>🌐 Live HTML Playground</h3>

<textarea
    id="htmlCode"
    class="editor"
    spellcheck="false"
>&lt;h1&gt;Hello Neon!&lt;/h1&gt;

&lt;p&gt;This is my website.&lt;/p&gt;

&lt;button&gt;Click Me&lt;/button&gt;</textarea>

<br>

<button
    class="small-button"
    onclick="runHTML()"
>
▶ Preview
</button>

<br><br>

<iframe
    id="htmlPreview"
    class="preview"
    sandbox
></iframe>

</div>


<div class="lesson">

<h3>💻 Tutorial Terminal</h3>

<div class="terminal">

<div class="terminal-top">

<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>

<span class="terminal-title">
HTML
</span>

</div>

<div class="terminal-body">$ html

HTML is interpreted by your browser.

Use the playground above
to experiment with HTML.</div>

</div>

</div>


<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     CSS
============================================================ -->

<div id="css" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🎨</div>

<h2>CSS</h2>

<p>Style your webpages.</p>

</div>


<div class="lesson">

<h3>Basic CSS</h3>

<pre>body {
    background: black;
    color: white;
}

h1 {
    font-size: 50px;
}</pre>

</div>


<div class="lesson">

<h3>🎨 Live CSS Playground</h3>

<textarea
    id="cssCode"
    class="editor"
    spellcheck="false">body {
    background: #101020;
    color: white;
    font-family: Arial;
    text-align: center;
}

h1 {
    color: #c084fc;
}

button {
    padding: 15px;
    border-radius: 10px;
}</textarea>

<br>

<button
    class="small-button"
    onclick="runCSS()"
>
▶ Preview
</button>

<br><br>

<iframe
    id="cssPreview"
    class="preview"
    sandbox
></iframe>

</div>


<div class="lesson">

<h3>💻 Tutorial Terminal</h3>

<div class="terminal">

<div class="terminal-top">

<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>

<span class="terminal-title">
CSS
</span>

</div>

<div class="terminal-body">$ css

CSS controls the appearance
of HTML elements.</div>

</div>

</div>


<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     JAVASCRIPT
============================================================ -->

<div id="javascript" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">⚡</div>

<h2>JavaScript</h2>

<p>Add logic and interaction.</p>

</div>


<div class="lesson">

<h3>Variables</h3>

<pre>let name = "Neon";

console.log(name);</pre>

</div>


<div class="lesson">

<h3>⚡ JavaScript Playground</h3>

<textarea
    id="jsCode"
    class="editor"
    spellcheck="false">let x = 10;
let y = 20;

console.log("Result:", x + y);</textarea>

<br>

<button
    class="small-button"
    onclick="runJS()"
>
▶ Run
</button>

<br><br>

<pre
    id="jsOutput"
    class="output"
>Ready.</pre>

</div>


<div class="lesson">

<h3>💻 Tutorial Terminal</h3>

<div class="terminal">

<div class="terminal-top">

<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>

<span class="terminal-title">
JavaScript
</span>

</div>

<div class="terminal-body">&gt; 5 + 5
10

&gt; console.log("Hello")
Hello</div>

</div>

</div>


<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     JAVA
============================================================ -->

<div id="java" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">☕</div>

<h2>Java</h2>

<p>Object-oriented programming.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>public class Main {

    public static void main(String[] args) {

        System.out.println("Hello, World!");

    }
}</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">Java</span>
</div>

<div class="terminal-body">$ javac Main.java
$ java Main

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     C
============================================================ -->

<div id="c" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">💻</div>

<h2>C</h2>

<p>Learn the foundations of programming.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>#include &lt;stdio.h&gt;

int main() {

    printf("Hello, World!");

    return 0;
}</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">C</span>
</div>

<div class="terminal-body">$ gcc main.c -o main
$ ./main

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     C++
============================================================ -->

<div id="cpp" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🔷</div>

<h2>C++</h2>

<p>Powerful application and game programming.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>#include &lt;iostream&gt;

int main() {

    std::cout &lt;&lt; "Hello, World!";

    return 0;
}</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">C++</span>
</div>

<div class="terminal-body">$ g++ main.cpp -o main
$ ./main

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     C#
============================================================ -->

<div id="csharp" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🟣</div>

<h2>C#</h2>

<p>.NET and game development.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>using System;

class Program {

    static void Main() {

        Console.WriteLine(
            "Hello, World!"
        );

    }
}</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">C#</span>
</div>

<div class="terminal-body">$ dotnet run

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     RUST
============================================================ -->

<div id="rust" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🦀</div>

<h2>Rust</h2>

<p>Fast and memory-safe programming.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>fn main() {

    println!("Hello, World!");

}</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">Rust</span>
</div>

<div class="terminal-body">$ rustc main.rs
$ ./main

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     PHP
============================================================ -->

<div id="php" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🐘</div>

<h2>PHP</h2>

<p>Server-side web programming.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>&lt;?php

echo "Hello, World!";

?&gt;</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">PHP</span>
</div>

<div class="terminal-body">$ php main.php

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     RUBY
============================================================ -->

<div id="ruby" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">💎</div>

<h2>Ruby</h2>

<p>Readable and expressive programming.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>puts "Hello, World!"</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">Ruby</span>
</div>

<div class="terminal-body">$ ruby main.rb

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     GO
============================================================ -->

<div id="go" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🐹</div>

<h2>Go</h2>

<p>Simple and fast backend programming.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>package main

import "fmt"

func main() {

    fmt.Println("Hello, World!")

}</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">Go</span>
</div>

<div class="terminal-body">$ go run main.go

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     KOTLIN
============================================================ -->

<div id="kotlin" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🦫</div>

<h2>Kotlin</h2>

<p>Modern JVM programming.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>fun main() {

    println("Hello, World!")

}</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">Kotlin</span>
</div>

<div class="terminal-body">$ kotlinc main.kt -include-runtime -d main.jar
$ java -jar main.jar

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     SWIFT
============================================================ -->

<div id="swift" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🐦</div>

<h2>Swift</h2>

<p>Apple platform programming.</p>

</div>

<div class="lesson">

<h3>Hello World</h3>

<pre>print("Hello, World!")</pre>

</div>

<div class="lesson">

<h3>💻 Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">Swift</span>
</div>

<div class="terminal-body">$ swift main.swift

Hello, World!</div>

</div>

</div>

<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<!-- ============================================================
     SQL
============================================================ -->

<div id="sql" class="screen">

<div class="tutorial">

<div class="tutorial-header">

<div class="tutorial-icon">🗄️</div>

<h2>SQL</h2>

<p>Learn databases and queries.</p>

</div>


<div class="lesson">

<h3>🗄️ SQLite Playground</h3>

<textarea
    id="sqlCode"
    class="editor"
    spellcheck="false">CREATE TABLE users (
    id INTEGER,
    name TEXT,
    age INTEGER
);

INSERT INTO users VALUES
(1, 'Alex', 15),
(2, 'Sam', 20);

SELECT * FROM users;</textarea>

<br>

<button
    class="small-button"
    onclick="runSQL()"
>
▶ Run SQL
</button>

<br><br>

<pre
    id="sqlOutput"
    class="output"
>Ready.</pre>

</div>


<div class="lesson">

<h3>💻 SQLite Terminal</h3>

<div class="terminal">

<div class="terminal-top">
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="term-dot"></span>
<span class="terminal-title">SQLite</span>
</div>

<div class="terminal-body">sqlite&gt; SELECT 1 + 1;

2</div>

</div>

</div>


<button class="button"
onclick="showScreen('languages')">
← Back to Languages
</button>

</div>

</div>


<script>

/* ============================================================
   SCREEN NAVIGATION
============================================================ */

function showScreen(id) {

    const screens =
        document.querySelectorAll(".screen");

    screens.forEach(function(screen) {
        screen.classList.remove("active");
    });

    const selected =
        document.getElementById(id);

    if (selected) {

        selected.classList.add("active");

        selected.scrollTop = 0;
    }
}


/* ============================================================
   PYTHON
============================================================ */

async function runPython() {

    const code =
        document.getElementById(
            "pythonCode"
        ).value;

    const output =
        document.getElementById(
            "pythonOutput"
        );

    output.textContent =
        "Running...";

    try {

        const response =
            await fetch(
                "/api/python/run",
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

        let text = "";

        if (data.stdout) {
            text += data.stdout;
        }

        if (data.stderr) {

            if (text) {
                text += "\n";
            }

            text += data.stderr;
        }

        if (!text) {
            text = "(no output)";
        }

        output.textContent = text;

    } catch (error) {

        output.textContent =
            "Connection error: " +
            error;

    }
}


function clearPython() {

    document.getElementById(
        "pythonCode"
    ).value = "";

    document.getElementById(
        "pythonOutput"
    ).textContent = "Ready.";
}


/* ============================================================
   PACKAGE INSTALLER
============================================================ */

async function installPackage() {

    const input =
        document.getElementById(
            "packageName"
        );

    const output =
        document.getElementById(
            "packageOutput"
        );

    const packageName =
        input.value.trim();

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
            data.error ||
            "Finished.";

    } catch (error) {

        output.textContent =
            "Connection error: " +
            error;
    }
}


/* ============================================================
   HTML
============================================================ */

function runHTML() {

    const code =
        document.getElementById(
            "htmlCode"
        ).value;

    document.getElementById(
        "htmlPreview"
    ).srcdoc = code;
}


/* ============================================================
   CSS
============================================================ */

function runCSS() {

    const css =
        document.getElementById(
            "cssCode"
        ).value;

    const html =
        "<!DOCTYPE html>" +
        "<html>" +
        "<head>" +
        "<style>" +
        css +
        "</style>" +
        "</head>" +
        "<body>" +
        "<h1>Neon CSS Playground</h1>" +
        "<p>Change the CSS and preview it.</p>" +
        "<button>Test Button</button>" +
        "</body>" +
        "</html>";

    document.getElementById(
        "cssPreview"
    ).srcdoc = html;
}


/* ============================================================
   JAVASCRIPT
============================================================ */

function runJS() {

    const code =
        document.getElementById(
            "jsCode"
        ).value;

    const output =
        document.getElementById(
            "jsOutput"
        );

    const lines = [];

    const originalLog =
        console.log;

    console.log = function() {

        const args =
            Array.from(arguments);

        lines.push(
            args.join(" ")
        );

        originalLog.apply(
            console,
            args
        );
    };

    try {

        const result =
            Function(code)();

        if (result !== undefined) {

            lines.push(
                String(result)
            );
        }

        output.textContent =
            lines.join("\n") ||
            "(no output)";

    } catch (error) {

        output.textContent =
            String(error);

    } finally {

        console.log =
            originalLog;
    }
}


/* ============================================================
   SQL
============================================================ */

async function runSQL() {

    const sql =
        document.getElementById(
            "sqlCode"
        ).value;

    const output =
        document.getElementById(
            "sqlOutput"
        );

    output.textContent =
        "Running...";

    try {

        const response =
            await fetch(
                "/api/sql/run",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            sql: sql
                        })
                }
            );

        const data =
            await response.json();

        output.textContent =
            data.output ||
            data.error ||
            "(no output)";

    } catch (error) {

        output.textContent =
            "Connection error: " +
            error;
    }
}

</script>

</body>

</html>
"""


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
def home():
    return render_template_string(HTML)


# ============================================================
# PYTHON EXECUTION API
# ============================================================

@app.route("/api/python/run", methods=["POST"])
def api_python_run():

    data = request.get_json(silent=True) or {}

    code = data.get("code", "")

    if not isinstance(code, str):
        return jsonify({
            "stdout": "",
            "stderr": "Invalid code."
        }), 400

    if len(code) > 20000:
        return jsonify({
            "stdout": "",
            "stderr": "Code is too large."
        }), 400

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

        result = subprocess.run(
            [
                sys.executable,
                temp_path
            ],
            capture_output=True,
            text=True,
            timeout=PYTHON_TIMEOUT
        )

        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr
        })

    except subprocess.TimeoutExpired:

        return jsonify({
            "stdout": "",
            "stderr":
                "Execution stopped: "
                "time limit exceeded."
        })

    except Exception as error:

        return jsonify({
            "stdout": "",
            "stderr":
                "Execution error: " +
                str(error)
        })

    finally:

        if temp_path is not None:

            try:
                os.remove(temp_path)

            except OSError:
                pass


# ============================================================
# PYTHON PACKAGE INSTALLER
# ============================================================

@app.route("/api/python/install", methods=["POST"])
def api_python_install():

    data = request.get_json(silent=True) or {}

    package = data.get("package", "")

    if not isinstance(package, str):

        return jsonify({
            "error": "Invalid package."
        }), 400

    package = package.strip().lower()

    if package not in ALLOWED_PACKAGES:

        allowed = "\n".join(
            sorted(ALLOWED_PACKAGES)
        )

        return jsonify({
            "error":
                "Package not allowed.\n\n"
                "Available packages:\n" +
                allowed
        }), 400

    try:

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                package
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        output = (
            result.stdout +
            "\n" +
            result.stderr
        )

        return jsonify({
            "output": output
        })

    except subprocess.TimeoutExpired:

        return jsonify({
            "error":
                "Package installation timed out."
        })

    except Exception as error:

        return jsonify({
            "error":
                str(error)
        })


# ============================================================
# SQLITE API
# ============================================================

@app.route("/api/sql/run", methods=["POST"])
def api_sql_run():

    data = request.get_json(silent=True) or {}

    sql = data.get("sql", "")

    if not isinstance(sql, str):

        return jsonify({
            "error": "Invalid SQL."
        }), 400

    if len(sql) > 20000:

        return jsonify({
            "error": "SQL is too large."
        }), 400

    connection = None

    try:

        connection = sqlite3.connect(":memory:")

        cursor = connection.cursor()

        statements = [
            statement.strip()
            for statement in sql.split(";")
            if statement.strip()
        ]

        output_lines = []

        for statement in statements:

            cursor.execute(statement)

            if cursor.description:

                columns = [
                    column[0]
                    for column in cursor.description
                ]

                output_lines.append(
                    " | ".join(columns)
                )

                output_lines.append(
                    "-" * 40
                )

                rows = cursor.fetchall()

                for row in rows:

                    output_lines.append(
                        " | ".join(
                            str(value)
                            for value in row
                        )
                    )

            else:

                output_lines.append("OK")

        return jsonify({
            "output":
                "\n".join(output_lines)
        })

    except Exception as error:

        return jsonify({
            "error":
                "SQL error: " +
                str(error)
        })

    finally:

        if connection is not None:
            connection.close()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("          NEON PROGRAMMING HUB")
    print("==========================================")
    print()
    print("Open:")
    print("http://127.0.0.1:5000")
    print()
    print("Features:")
    print("  - Programming tutorials")
    print("  - Python test area")
    print("  - Python execution")
    print("  - Python package installer")
    print("  - HTML playground")
    print("  - CSS playground")
    print("  - JavaScript playground")
    print("  - SQLite playground")
    print()
    print("Press CTRL+C to stop.")
    print("==========================================")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
