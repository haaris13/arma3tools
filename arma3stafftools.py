"""
===============================================================================
Filename        : arma3stafftools.py
Author          : alharis thess / Pacific Island
Date            : 2025-05-24
Description     : 
    Arma 3 .rpt log file analyzer, comma checker
    - Modern dark-themed GUI built with customtkinter.
    - Load .rpt files, filter errors by keywords,
      and display errors with line numbers.
    - Export detected errors to a .txt file.
    
License         : No licence man do what you want !
Dependencies    : customtkinter (pip install customtkinter), tkinter (standard)
Usage           : python arma3_log_analyzer.py
===============================================================================
Change Log:
 2025-05-24  - Initial version with GUI and basic error analysis.
===============================================================================
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import os
import re

# === MENU PRINCIPAL ===
def launch_menu():
    menu = tk.Tk()
    menu.title("Outils Arma 3 - alharis thess")
    menu.geometry("400x200")
    menu.configure(bg="#1e1e1e")

    def lancer_analyse_rpt():
        menu.withdraw()
        launch_rpt_analyzer(menu)

    def lancer_verificateur_hpp():
        menu.withdraw()
        launch_hpp_checker(menu)

    btn1 = tk.Button(menu, text="Analyser un fichier .rpt", command=lancer_analyse_rpt,
                     font=("Segoe UI", 12), bg="#007acc", fg="white", padx=10, pady=10)
    btn1.pack(pady=20)

    btn2 = tk.Button(menu, text="Vérifier un fichier .hpp", command=lancer_verificateur_hpp,
                     font=("Segoe UI", 12), bg="#007acc", fg="white", padx=10, pady=10)
    btn2.pack(pady=10)

    menu.mainloop()

# === OUTIL 1 : Analyser .RPT ===
def launch_rpt_analyzer(menu_root):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Logs Arma 3 - alharis thess")
    app.geometry("950x700")

    chemin_fichier_global = None
    erreurs_globales = []
    filtres_disponibles = ["error", "warning", "missing", "undefined", "invalid", "failed"]
    filtres_vars = {}

    def analyser_rpt(fichier_rpt, filtres_actifs):
        erreurs = []
        try:
            with open(fichier_rpt, 'r', encoding='utf-8', errors='ignore') as fichier:
                for i, ligne in enumerate(fichier, start=1):
                    for mot in filtres_actifs:
                        if mot.lower() in ligne.lower():
                            erreurs.append((i, ligne.strip()))
                            break
            return erreurs
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")
        return []

    def afficher_erreurs():
        nonlocal erreurs_globales
        if not chemin_fichier_global:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné.")
            return
        filtres_actifs = [mot for mot, var in filtres_vars.items() if var.get()]
        erreurs = analyser_rpt(chemin_fichier_global, filtres_actifs)
        erreurs_globales = erreurs

        zone_texte.configure(state="normal")
        zone_texte.delete("0.0", "end")
        if erreurs:
            zone_texte.insert("end", "=== Erreurs trouvées ===\n\n")
            for ligne_num, erreur in erreurs:
                zone_texte.insert("end", f"Ligne {ligne_num}: {erreur}\n")
        else:
            zone_texte.insert("end", "Aucune erreur trouvée.")
        zone_texte.configure(state="disabled")

    def ouvrir_fichier():
        nonlocal chemin_fichier_global
        fichier = filedialog.askopenfilename(filetypes=[("Fichiers RPT", "*.rpt")])
        if fichier:
            chemin_fichier_global = fichier
            afficher_erreurs()

    def exporter_erreurs():
        if not erreurs_globales:
            messagebox.showinfo("Info", "Aucune erreur à exporter.")
            return
        fichier = filedialog.asksaveasfilename(defaultextension=".txt")
        if fichier:
            try:
                with open(fichier, "w", encoding="utf-8") as f:
                    f.write("=== Erreurs ===\n\n")
                    for ligne_num, erreur in erreurs_globales:
                        f.write(f"Ligne {ligne_num}: {erreur}\n")
                messagebox.showinfo("Succès", f"Erreurs exportées dans : {fichier}")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def retour_menu():
        app.destroy()
        menu_root.deiconify()

    frame_boutons = ctk.CTkFrame(app)
    frame_boutons.pack(pady=10)

    ctk.CTkButton(frame_boutons, text="📂 Ouvrir .RPT", command=ouvrir_fichier).pack(side="left", padx=10)
    ctk.CTkButton(frame_boutons, text="💾 Exporter", command=exporter_erreurs).pack(side="left", padx=10)
    ctk.CTkButton(frame_boutons, text="⬅ Retour", command=retour_menu).pack(side="left", padx=10)

    ctk.CTkLabel(app, text="Filtres d'erreurs :", font=ctk.CTkFont(size=14, weight="bold")).pack()
    filtre_frame = ctk.CTkFrame(app)
    filtre_frame.pack(pady=5)

    for mot in filtres_disponibles:
        var = ctk.BooleanVar(value=True)
        filtres_vars[mot] = var
        cb = ctk.CTkCheckBox(filtre_frame, text=mot, variable=var, command=afficher_erreurs)
        cb.pack(side="left", padx=5)

    zone_texte = ctk.CTkTextbox(app, width=900, height=500, font=("Consolas", 11))
    zone_texte.pack(padx=20, pady=20)
    zone_texte.configure(state="disabled")
    app.protocol("WM_DELETE_WINDOW", retour_menu)
    app.mainloop()

# === OUTIL 2 : Vérification .HPP ===
def launch_hpp_checker(menu_root):
    root = tk.Tk()
    root.title("Vérificateur .hpp - alharis thess")
    root.geometry("900x650")
    root.configure(bg="#1e1e1e")

    checker = DarkSyntaxCheckerApp(root)
    
    def retour_menu():
        root.destroy()
        menu_root.deiconify()

    tk.Button(root, text="⬅ Retour", command=retour_menu,
              font=("Segoe UI", 10), bg="#007acc", fg="white").pack(pady=5)
    root.protocol("WM_DELETE_WINDOW", retour_menu)

    root.mainloop()

# === CLASSE HPP ===
class DarkSyntaxCheckerApp:
    def __init__(self, root):
        self.root = root
        self.text = tk.Text(root, wrap="none", font=("Consolas", 12), bg="#1e1e1e", fg="white")
        self.text.pack(fill="both", expand=True)

        self.file_path = ""
        self.error_lines = set()

        frame = tk.Frame(root, bg="#1e1e1e")
        frame.pack(fill="x")

        tk.Button(frame, text="📂 Charger .hpp", command=self.load_file, bg="#007acc", fg="white").pack(side="left", padx=5, pady=5)
        tk.Button(frame, text="🔁 Re-vérifier", command=self.recheck, bg="#007acc", fg="white").pack(side="left", padx=5, pady=5)
        tk.Button(frame, text="🛠 Corriger", command=self.auto_fix, bg="#007acc", fg="white").pack(side="left", padx=5, pady=5)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Fichiers .hpp", "*.hpp")])
        if not path:
            return
        self.file_path = path
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, content)
        self.recheck()

    def recheck(self):
        content = self.text.get("1.0", tk.END)
        self.text.tag_remove("error", "1.0", tk.END)
        self.text.tag_config("error", foreground="red")

        errors = self.check_syntax(content)
        for line, _, _ in errors:
            index = f"{line}.0"
            self.text.tag_add("error", index, f"{line}.end")

        if not errors:
            messagebox.showinfo("👌 Nickel", "Aucune erreur détectée.")
        else:
            msg = "\n".join([f"Ligne {line}: {desc}" for line, desc, _ in errors])
            messagebox.showerror("Erreurs détectées", msg)

    def check_syntax(self, content):
        errors = []
        if content.count("{") != content.count("}"):
            errors.append((1, "Accolades déséquilibrées", "{"))

        pattern = r"stock\[\]\s*=\s*\{([\s\S]*?)\};"
        for match in re.finditer(pattern, content):
            start = match.start()
            block = match.group(1)
            lines = block.splitlines()
            start_line = content[:start].count("\n") + 1

            for i, line in enumerate(lines):
                line_no = start_line + i + 1
                line_strip = re.sub(r"//.*", "", line).strip()
                if i < len(lines) - 1 and line_strip and not line_strip.endswith(","):
                    errors.append((line_no, f"Virgule manquante après : {line_strip}", line_strip))
                elif i == len(lines) - 1 and line_strip.endswith(","):
                    errors.append((line_no, f"Virgule en trop à la fin : {line_strip}", line_strip))
        return errors

    def auto_fix(self):
        if not self.file_path:
            messagebox.showwarning("Erreur", "Aucun fichier à corriger.")
            return
        content = self.text.get("1.0", tk.END)
        fixed = self.fix_commas(content)
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(fixed)
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", fixed)
        self.recheck()
        messagebox.showinfo("✅ Corrigé", "Fichier corrigé et sauvegardé.")

    def fix_commas(self, content):
        def fix_block(block):
            lines = block.strip().splitlines()
            result = []
            for i, line in enumerate(lines):
                clean = re.sub(r"//.*", "", line).strip()
                if i < len(lines) - 1 and clean and not clean.endswith(","):
                    line = line.rstrip() + ","
                elif i == len(lines) - 1 and clean.endswith(","):
                    line = line.rstrip().rstrip(",")
                result.append(line)
            return "\n".join(result)

        return re.sub(r"(stock\[\]\s*=\s*\{)([\s\S]*?)(\};)",
                      lambda m: m.group(1) + "\n" + fix_block(m.group(2)) + "\n" + m.group(3),
                      content)

# === LANCEMENT ===
if __name__ == "__main__":
    launch_menu()
