from flask import Flask, render_template, request
import os

app = Flask(__name__)

def contains_backdoor_patterns(line):
    import re
    patterns = [
        r"\b(system|exec|passthru|popen|fopen|eval)\s*\(",
        r"\b(os\.system|subprocess\.run|subprocess\.call)\s*\(",
        r"\bimport\s+subprocess\b",
        r"\bimport\s+os\b",
        r"\bexec\(\s*('|\"|\'\'|\"\"\")(.*?)(\'|\"|\'\'|\"\"\")\)",
        r"\bgetattr\(\s*\w+,\s*(\".*?\"|'.*?')\s*\)",
    ]
    return any(re.search(pattern, line) for pattern in patterns)

def scan_file_for_backdoors(file_storage):
    findings = []
    try:
        file_content = file_storage.stream.read().decode('utf-8')
        lines = file_content.split('\n')
        
        for line_number, line in enumerate(lines, start=1):
            stripped_line = line.strip()

            if contains_backdoor_patterns(stripped_line):
                findings.append(f"Potential backdoor found in {file_storage.filename} at line {line_number}: {line.strip()}")

    except Exception as e:
        findings.append(f"Error scanning {file_storage.filename}: {e}")
    return findings

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    results = []
    for file_storage in request.files.getlist('folder'):
        results.extend(scan_file_for_backdoors(file_storage))

    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
