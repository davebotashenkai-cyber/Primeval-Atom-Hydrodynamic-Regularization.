"""
push_to_github.py
=================
Script utilitario para sincronizar automáticamente los archivos actualizados
al repositorio de GitHub mediante la API REST de GitHub (sin necesidad de git.exe).

Uso:
  python push_to_github.py TU_GITHUB_TOKEN
"""

import sys
import os
import base64
import json
import urllib.request
import urllib.error

REPO_OWNER = "davebotashenkai-cyber"
REPO_NAME  = "Primeval-Atom-Hydrodynamic-Regularization."
BRANCH     = "main"

FILES_TO_UPLOAD = [
    "README.md",
    "simulation.py",
    "zepto_matrix.py",
    "primeval_atom_simulator.py",
    "fourier_breakdown_solver.py",
    "reflexive_causal_dominance.py",
    "param_card.dat",
    "run_card.dat",
    "simulation_report.md"
]

def upload_file(token, filename):
    if not os.path.exists(filename):
        print(f"[-] Archivo no encontrado: {filename}")
        return False

    with open(filename, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")

    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filename}"
    
    # 1. Obtener el SHA actual si el archivo ya existe
    sha = None
    req = urllib.request.Request(api_url, headers={
        "Authorization": f"token {token}",
        "User-Agent": "Antigravity-Sync"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sha = data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"[-] Error consultando {filename}: {e}")
            return False

    # 2. Preparar el payload de subida / actualización
    payload = {
        "message": f"Update {filename} (v2.1: regularized suite & collider phenomenology)",
        "content": content_b64,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    put_data = json.dumps(payload).encode("utf-8")
    put_req = urllib.request.Request(api_url, data=put_data, method="PUT", headers={
        "Authorization": f"token {token}",
        "User-Agent": "Antigravity-Sync",
        "Content-Type": "application/json"
    })

    try:
        with urllib.request.urlopen(put_req) as resp:
            print(f"[+] Sincronizado correctamente: {filename}")
            return True
    except urllib.error.HTTPError as e:
        print(f"[-] Error subiendo {filename}: {e.read().decode('utf-8')[:200]}")
        return False

def main():
    if len(sys.argv) < 2:
        print("\nUso: python push_to_github.py <GITHUB_PERSONAL_ACCESS_TOKEN>")
        print("Si prefieres no usar un token, puedes arrastrar los archivos directamente")
        print(f"a la web: https://github.com/{REPO_OWNER}/{REPO_NAME}\n")
        return

    token = sys.argv[1].strip()
    print(f"Sincronizando {len(FILES_TO_UPLOAD)} archivos a {REPO_OWNER}/{REPO_NAME}...")
    for f in FILES_TO_UPLOAD:
        upload_file(token, f)
    print("\nProceso de sincronizacion completado.")

if __name__ == "__main__":
    main()
