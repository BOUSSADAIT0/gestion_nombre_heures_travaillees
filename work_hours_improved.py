import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import locale
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

# Configurer la locale française
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'fra_fra')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except:
            pass

class WorkHoursApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calcul des Heures Travaillées")
        self.root.geometry("1200x800")
        
        # Variables pour le thème
        self.is_dark_mode = tk.BooleanVar(value=False)
        self.theme_colors = {
            'light': {
                'bg': "#f0f0f0",
                'fg': "#333333",
                'accent': "#4a7a8c",
                'button': "#4a7a8c",
                'button_fg': "white",
                'error': "#d9534f",
                'success': "#28a745"
            },
            'dark': {
                'bg': "#2b2b2b",
                'fg': "#ffffff",
                'accent': "#5c9eb3",
                'button': "#5c9eb3",
                'button_fg': "white",
                'error': "#e74c3c",
                'success': "#2ecc71"
            }
        }
        
        # Variables pour les catégories et taux
        self.categories = ["Travail normal", "Travail de nuit", "Heures supplémentaires", "Week-end"]
        self.category_rates = {cat: 0.0 for cat in self.categories}
        self.current_category = tk.StringVar(value=self.categories[0])
        self.hourly_rate = tk.DoubleVar(value=0.0)  # Tarif horaire par défaut
        
        # Variables pour les pauses
        self.has_break = tk.BooleanVar(value=False)
        self.break_start_hour = tk.StringVar()
        self.break_start_min = tk.StringVar()
        self.break_end_hour = tk.StringVar()
        self.break_end_min = tk.StringVar()
        
        # Variables existantes
        self.is_night_shift = tk.BooleanVar(value=False)
        self.current_id = 0
        self.entries = []
        self.editing_id = None
        
        # Création de l'interface
        self.create_interface()
        
        # Configuration des raccourcis clavier
        self.setup_shortcuts()
        
        # Charger les données sauvegardées
        self.load_data()
        
    def get_theme_color(self, color_key):
        theme = 'dark' if self.is_dark_mode.get() else 'light'
        return self.theme_colors[theme][color_key]
        
    def create_interface(self):
        # Frame principal avec thème
        self.main_frame = tk.Frame(self.root, bg=self.get_theme_color('bg'))
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Barre d'outils
        self.create_toolbar()
        
        # Contenu principal
        self.create_main_content()
        
        # Barre de progression
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Afficher/masquer les champs de pause après la création de l'interface
        self.toggle_break_fields()
        
    def create_toolbar(self):
        toolbar = tk.Frame(self.main_frame, bg=self.get_theme_color('bg'))
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Bouton thème
        theme_btn = tk.Button(toolbar, text="🌓 Thème", command=self.toggle_theme,
                            bg=self.get_theme_color('button'), fg=self.get_theme_color('button_fg'))
        theme_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton statistiques
        stats_btn = tk.Button(toolbar, text="📊 Statistiques", command=self.show_statistics,
                            bg=self.get_theme_color('button'), fg=self.get_theme_color('button_fg'))
        stats_btn.pack(side=tk.LEFT, padx=5)
        
        # Configuration des catégories
        category_btn = tk.Button(toolbar, text="📋 Catégories", command=self.show_category_settings,
                               bg=self.get_theme_color('button'), fg=self.get_theme_color('button_fg'))
        category_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour vérifier les durées
        verify_btn = tk.Button(toolbar, text="🔍 Vérifier les durées",
                             command=self.check_all_durations,
                             bg=self.get_theme_color('button'),
                             fg=self.get_theme_color('button_fg'))
        verify_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour vider le tableau
        clear_btn = tk.Button(toolbar, text="🗑️ Vider le tableau",
                            command=self.clear_all_entries,
                            bg=self.get_theme_color('button'),
                            fg=self.get_theme_color('button_fg'))
        clear_btn.pack(side=tk.LEFT, padx=5)
        
    def create_main_content(self):
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet principal (Saisie)
        main_tab = tk.Frame(self.notebook, bg=self.get_theme_color('bg'))
        self.notebook.add(main_tab, text="Saisie des heures")
        
        # Onglet statistiques
        stats_tab = tk.Frame(self.notebook, bg=self.get_theme_color('bg'))
        self.notebook.add(stats_tab, text="Statistiques")
        
        # Configuration des widgets dans l'onglet principal
        self.setup_main_tab(main_tab)
        
        # Configuration des widgets dans l'onglet statistiques
        self.setup_stats_tab(stats_tab)
        
        # Sélectionner l'onglet Saisie par défaut
        self.notebook.select(0)
        
    def setup_main_tab(self, parent):
        # Frame pour les contrôles
        controls_frame = tk.Frame(parent, bg=self.get_theme_color('bg'))
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Bouton pour ajouter une entrée
        add_btn = tk.Button(controls_frame, text="➕ Nouvelle entrée",
                          command=self.add_entry,
                          bg=self.get_theme_color('button'),
                          fg=self.get_theme_color('button_fg'))
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour modifier une entrée
        edit_btn = tk.Button(controls_frame, text="✏️ Modifier",
                           command=self.edit_selected,
                           bg=self.get_theme_color('button'),
                           fg=self.get_theme_color('button_fg'))
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour supprimer une entrée
        delete_btn = tk.Button(controls_frame, text="🗑️ Supprimer",
                             command=self.delete_selected,
                             bg=self.get_theme_color('button'),
                             fg=self.get_theme_color('button_fg'))
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour exporter
        export_btn = tk.Button(controls_frame, text="📤 Exporter",
                             command=self.show_export_options,
                             bg=self.get_theme_color('button'),
                             fg=self.get_theme_color('button_fg'))
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour vérifier les durées
        verify_btn = tk.Button(controls_frame, text="🔍 Vérifier les durées",
                             command=self.check_all_durations,
                             bg=self.get_theme_color('button'),
                             fg=self.get_theme_color('button_fg'))
        verify_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour vider le tableau
        clear_btn = tk.Button(controls_frame, text="🗑️ Vider le tableau",
                            command=self.clear_all_entries,
                            bg=self.get_theme_color('button'),
                            fg=self.get_theme_color('button_fg'))
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame pour les totaux
        totals_frame = tk.LabelFrame(parent, text="Résumé",
                                   bg=self.get_theme_color('bg'),
                                   fg=self.get_theme_color('fg'))
        totals_frame.pack(fill=tk.X, pady=5)
        
        # Frame pour le tarif horaire
        rate_frame = tk.Frame(totals_frame, bg=self.get_theme_color('bg'))
        rate_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(rate_frame, text="Tarif horaire:",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT)
        
        rate_entry = tk.Entry(rate_frame, textvariable=self.hourly_rate,
                            width=8,
                            bg=self.get_theme_color('bg'),
                            fg=self.get_theme_color('fg'))
        rate_entry.pack(side=tk.LEFT, padx=5)
        
        # Ajouter un événement de changement sur le tarif horaire
        self.hourly_rate.trace_add("write", lambda *args: self.on_rate_change())
        
        tk.Label(rate_frame, text="€/h",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT)
        
        # Labels pour les totaux
        self.total_hours_label = tk.Label(totals_frame,
                                        text="Total des heures: 0.00",
                                        bg=self.get_theme_color('bg'),
                                        fg=self.get_theme_color('fg'))
        self.total_hours_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.total_amount_label = tk.Label(totals_frame,
                                         text="Total des gains: 0.00 €",
                                         bg=self.get_theme_color('bg'),
                                         fg=self.get_theme_color('fg'))
        self.total_amount_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Mettre à jour les totaux
        self.update_totals()
        
        # Frame pour le tableau des entrées
        entries_frame = tk.Frame(parent, bg=self.get_theme_color('bg'))
        entries_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Création du tableau
        columns = ('id', 'date', 'début', 'pause_début', 'pause_fin', 'fin', 'durée', 'catégorie', 'montant')
        self.tree = ttk.Treeview(entries_frame, columns=columns, show='headings')
        
        # Configuration des colonnes
        self.tree.heading('id', text='ID')
        self.tree.heading('date', text='Date')
        self.tree.heading('début', text='Heure début')
        self.tree.heading('pause_début', text='Début pause')
        self.tree.heading('pause_fin', text='Fin pause')
        self.tree.heading('fin', text='Heure fin')
        self.tree.heading('durée', text='Durée (h)')
        self.tree.heading('catégorie', text='Catégorie')
        self.tree.heading('montant', text='Montant (€)')
        
        # Ajuster la largeur des colonnes
        self.tree.column('id', width=50)
        self.tree.column('date', width=100)
        self.tree.column('début', width=80)
        self.tree.column('pause_début', width=80)
        self.tree.column('pause_fin', width=80)
        self.tree.column('fin', width=80)
        self.tree.column('durée', width=80)
        self.tree.column('catégorie', width=120)
        self.tree.column('montant', width=100)
        
        # Ajouter une barre de défilement
        scrollbar = ttk.Scrollbar(entries_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Placer le tableau et la barre de défilement
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Charger les entrées existantes
        self.refresh_entries()
        
        # Frame pour les champs de pause
        self.break_fields_frame = tk.LabelFrame(entries_frame, text="Pause",
                                              bg=self.get_theme_color('bg'),
                                              fg=self.get_theme_color('fg'))
        self.break_fields_frame.pack(fill=tk.X, pady=10)
        
        # Checkbox pour activer la pause
        break_check = tk.Checkbutton(self.break_fields_frame, text="Activer la pause",
                                   variable=self.has_break,
                                   command=lambda: self.toggle_break_fields(self.break_fields_frame),
                                   bg=self.get_theme_color('bg'),
                                   fg=self.get_theme_color('fg'),
                                   selectcolor=self.get_theme_color('bg'),
                                   activebackground=self.get_theme_color('bg'),
                                   activeforeground=self.get_theme_color('fg'))
        break_check.pack(side=tk.LEFT, padx=5)
        
        # Frame pour les champs de pause
        self.break_fields_frame.pack(fill=tk.X, pady=5)
        
        # Heure de début de pause
        tk.Label(self.break_fields_frame, text="Début pause:",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT, padx=5)
        
        self.break_start_hour_combo = ttk.Combobox(self.break_fields_frame,
                                                  values=[f"{i:02}" for i in range(24)],
                                                  textvariable=self.break_start_hour,
                                                  width=3, state="readonly")
        self.break_start_hour_combo.pack(side=tk.LEFT, padx=2)
        
        tk.Label(self.break_fields_frame, text=":",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT)
        
        self.break_start_min_combo = ttk.Combobox(self.break_fields_frame,
                                                 values=[f"{i:02}" for i in range(0, 60, 5)],
                                                 textvariable=self.break_start_min,
                                                 width=3, state="readonly")
        self.break_start_min_combo.pack(side=tk.LEFT, padx=2)
        
        # Heure de fin de pause
        tk.Label(self.break_fields_frame, text="Fin pause:",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT, padx=5)
        
        self.break_end_hour_combo = ttk.Combobox(self.break_fields_frame,
                                               values=[f"{i:02}" for i in range(24)],
                                               textvariable=self.break_end_hour,
                                               width=3, state="readonly")
        self.break_end_hour_combo.pack(side=tk.LEFT, padx=2)
        
        tk.Label(self.break_fields_frame, text=":",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT)
        
        self.break_end_min_combo = ttk.Combobox(self.break_fields_frame,
                                              values=[f"{i:02}" for i in range(0, 60, 5)],
                                              textvariable=self.break_end_min,
                                              width=3, state="readonly")
        self.break_end_min_combo.pack(side=tk.LEFT, padx=2)
        
        # Cacher les champs de pause par défaut ou les afficher selon l'état initial
        if self.has_break.get():
            self.break_fields_frame.pack(fill=tk.X, pady=5)
        else:
            self.break_fields_frame.pack_forget()

    def setup_stats_tab(self, parent):
        # Création du graphique
        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_shortcuts(self):
        self.root.bind('<Control-s>', lambda e: self.save_data())
        self.root.bind('<Control-n>', lambda e: self.add_entry())
        self.root.bind('<Control-d>', lambda e: self.delete_selected())
        self.root.bind('<Control-e>', lambda e: self.show_export_options())
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        
    def toggle_theme(self):
        self.is_dark_mode.set(not self.is_dark_mode.get())
        self.update_theme()
        
    def update_theme(self):
        theme = 'dark' if self.is_dark_mode.get() else 'light'
        colors = self.theme_colors[theme]
        
        def update_widget(widget):
            # Mise à jour des widgets de base
            if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                widget.configure(bg=colors['bg'])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=colors['bg'], fg=colors['fg'])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=colors['button'], fg=colors['button_fg'])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=colors['bg'], fg=colors['fg'], insertbackground=colors['fg'])
            elif isinstance(widget, ttk.Combobox):
                style = ttk.Style()
                style.configure('TCombobox', 
                              fieldbackground=colors['bg'],
                              background=colors['bg'],
                              foreground=colors['fg'],
                              arrowcolor=colors['fg'])
            elif isinstance(widget, ttk.Notebook):
                style = ttk.Style()
                style.configure('TNotebook', background=colors['bg'])
                style.configure('TNotebook.Tab', 
                              background=colors['bg'],
                              foreground=colors['fg'],
                              padding=[10, 2])
            elif isinstance(widget, ttk.Progressbar):
                style = ttk.Style()
                style.configure('Horizontal.TProgressbar',
                              background=colors['accent'],
                              troughcolor=colors['bg'])
            
            # Mise à jour récursive des widgets enfants
            for child in widget.winfo_children():
                update_widget(child)
        
        # Mise à jour de la fenêtre principale
        self.root.configure(bg=colors['bg'])
        
        # Mise à jour de tous les widgets
        update_widget(self.main_frame)
        
        # Mise à jour des styles ttk
        style = ttk.Style()
        style.configure('.',
                      background=colors['bg'],
                      foreground=colors['fg'],
                      fieldbackground=colors['bg'])
        
        # Mise à jour des graphiques
        if hasattr(self, 'fig'):
            self.fig.set_facecolor(colors['bg'])
            for ax in self.fig.axes:
                ax.set_facecolor(colors['bg'])
                ax.tick_params(colors=colors['fg'])
                ax.xaxis.label.set_color(colors['fg'])
                ax.yaxis.label.set_color(colors['fg'])
                ax.title.set_color(colors['fg'])
                for spine in ax.spines.values():
                    spine.set_color(colors['fg'])
            self.canvas.draw()
                
    def toggle_break_fields(self, frame=None):
        """Affiche ou cache les champs de pause"""
        if frame is None:
            frame = self.break_fields_frame
            
        if hasattr(self, 'has_break') and self.has_break.get():
            frame.pack(fill=tk.X, pady=5)
        else:
            frame.pack_forget()
            
    def verify_duration(self, start_date, start_time, end_date, end_time):
        """Vérifie et corrige la durée entre deux dates/heures"""
        print(f"Attempting to verify duration with: start_date={start_date}, start_time={start_time}, end_date={end_date}, end_time={end_time}")
        try:
            # Convertir en objets datetime
            start = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            end = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
            
            # Vérifier si la date de fin est avant la date de début
            if end < start:
                return False, "La date/heure de fin est antérieure à la date/heure de début"
            
            # Calculer la durée brute
            duration = (end - start).total_seconds() / 3600
            
            # Vérifier si la durée est raisonnable (moins de 24h)
            if duration > 24:
                return False, "La durée ne peut pas dépasser 24 heures"
            
            # Vérifier si la durée est positive
            if duration <= 0:
                return False, "La durée doit être supérieure à 0"
            
            return True, duration
            
        except ValueError as e:
            print(f"verify_duration ValueError: {e}")
            return False, f"Format de date/heure invalide: {str(e)}"
        except Exception as e:
            print(f"verify_duration Exception: {e}")
            return False, f"Erreur lors de la vérification: {str(e)}"

    def calculate_duration(self, entry):
        """Calcule la durée de travail en tenant compte des pauses"""
        try:
            # Convertir les dates et heures en objets datetime
            start = datetime.strptime(f"{entry['start_date']} {entry['start_time']}", "%Y-%m-%d %H:%M")
            end = datetime.strptime(f"{entry['end_date']} {entry['end_time']}", "%Y-%m-%d %H:%M")
            
            # Vérifier si la date de fin est avant la date de début
            if end < start:
                print(f"Erreur: Date de fin antérieure à la date de début pour l'entrée {entry['id']}")
                return 0.0
            
            # Calculer la durée totale en heures
            duration = (end - start).total_seconds() / 3600
            
            # Vérifier si la durée est raisonnable (moins de 24h)
            if duration > 24:
                print(f"Attention: Durée supérieure à 24h pour l'entrée {entry['id']}")
                return 0.0
            
            # Soustraire les pauses si elles sont activées pour cette entrée
            if entry.get('has_break', False):
                try:
                    # Créer les objets datetime pour le début et la fin de la pause
                    break_start = datetime.strptime(
                        f"{entry['start_date']} {entry['break_start_hour']}:{entry['break_start_min']}",
                        "%Y-%m-%d %H:%M"
                    )
                    break_end = datetime.strptime(
                        f"{entry['start_date']} {entry['break_end_hour']}:{entry['break_end_min']}",
                        "%Y-%m-%d %H:%M"
                    )
                    
                    # Vérifier si la pause est dans la période de travail
                    if break_start < end and break_end > start:
                        # Ajuster les heures de pause si nécessaire
                        if break_start < start:
                            break_start = start
                        if break_end > end:
                            break_end = end
                            
                        # Calculer la durée de la pause
                        break_duration = (break_end - break_start).total_seconds() / 3600
                        
                        # Vérifier que la pause ne dépasse pas la durée totale
                        if break_duration > duration:
                            print(f"Attention: Pause plus longue que la durée totale pour l'entrée {entry['id']}")
                            break_duration = duration
                        
                        duration -= break_duration
                        
                        # Vérifier que la durée finale est positive
                        if duration < 0:
                            print(f"Attention: Durée négative après pause pour l'entrée {entry['id']}")
                            duration = 0.0
                            
                except (ValueError, KeyError) as e:
                    print(f"Erreur lors du calcul de la pause: {e}")
                    pass  # Si les heures de pause ne sont pas valides, ignorer
            
            # Arrondir à 2 décimales
            return round(duration, 2)
            
        except Exception as e:
            print(f"Erreur lors du calcul de la durée: {e}")
            return 0.0

    def on_rate_change(self):
        """Méthode appelée quand le tarif horaire change"""
        try:
            # Vérifier que le tarif est un nombre valide
            rate = float(self.hourly_rate.get())
            if rate < 0:
                self.hourly_rate.set(0)
                rate = 0
        except ValueError:
            self.hourly_rate.set(0)
            rate = 0
        
        # Mettre à jour l'affichage
        self.refresh_entries()
        self.update_totals()
        
        # Sauvegarder les données
        self.save_data()

    def save_data(self):
        # Convertir les données en format sérialisable
        data = {
            'entries': self.entries,
            'categories': self.categories,
            'category_rates': self.category_rates,
            'has_break': self.has_break.get(),
            'break_start_hour': self.break_start_hour.get(),
            'break_start_min': self.break_start_min.get(),
            'break_end_hour': self.break_end_hour.get(),
            'break_end_min': self.break_end_min.get(),
            'hourly_rate': self.hourly_rate.get()  # Sauvegarder le tarif horaire
        }
        
        try:
            with open('work_hours_data.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")
            
    def load_data(self):
        try:
            with open('work_hours_data.json', 'r') as f:
                data = json.load(f)
                self.entries = data.get('entries', [])
                self.categories = data.get('categories', self.categories)
                self.category_rates = data.get('category_rates', {cat: 0.0 for cat in self.categories})
                
                # Charger les données de pause
                self.has_break.set(data.get('has_break', False))
                self.break_start_hour.set(data.get('break_start_hour', ''))
                self.break_start_min.set(data.get('break_start_min', ''))
                self.break_end_hour.set(data.get('break_end_hour', ''))
                self.break_end_min.set(data.get('break_end_min', ''))
                
                # Charger le tarif horaire
                self.hourly_rate.set(data.get('hourly_rate', 0.0))
                
                # Réorganiser les IDs au chargement
                self.reorganize_ids()
                
                # Rafraîchir l'affichage
                self.refresh_entries()
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement : {str(e)}")

    def show_statistics(self):
        # Effacer les graphiques existants
        for ax in self.fig.axes:
            ax.clear()
        
        # Créer deux sous-graphiques
        ax1 = self.fig.add_subplot(211)
        ax2 = self.fig.add_subplot(212)
        
        # Préparer les données
        dates = []
        hours = []
        earnings = []
        
        for entry in self.entries:
            date = datetime.strptime(entry['start_date'], "%Y-%m-%d")
            duration = self.calculate_duration(entry)
            rate = self.category_rates.get(entry.get('category', self.categories[0]), 0.0)
            
            dates.append(date)
            hours.append(duration)
            earnings.append(duration * rate)
        
        # Graphique des heures travaillées
        ax1.plot(dates, hours, 'b-', marker='o')
        ax1.set_title('Heures travaillées par jour')
        ax1.set_ylabel('Heures')
        ax1.grid(True)
        
        # Graphique des gains
        ax2.plot(dates, earnings, 'g-', marker='o')
        ax2.set_title('Gains par jour')
        ax2.set_ylabel('Euros')
        ax2.grid(True)
        
        # Ajuster la mise en page
        self.fig.tight_layout()
        self.canvas.draw()
        
        # Afficher l'onglet des statistiques
        self.notebook.select(1)  # Index 1 correspond à l'onglet Statistiques

    def show_category_settings(self):
        # Créer une nouvelle fenêtre pour les paramètres des catégories
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configuration des catégories")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.get_theme_color('bg'))
        
        # Frame pour la liste des catégories
        categories_frame = tk.Frame(settings_window, bg=self.get_theme_color('bg'))
        categories_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dictionnaire pour stocker les variables temporaires
        temp_rates = {}
        
        # Liste des catégories
        for i, category in enumerate(self.categories):
            frame = tk.Frame(categories_frame, bg=self.get_theme_color('bg'))
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(frame, text=category, bg=self.get_theme_color('bg'),
                    fg=self.get_theme_color('fg')).pack(side=tk.LEFT)
            
            rate_var = tk.StringVar(value=str(self.category_rates.get(category, 0.0)))
            rate_entry = tk.Entry(frame, textvariable=rate_var, width=10,
                                bg=self.get_theme_color('bg'),
                                fg=self.get_theme_color('fg'))
            rate_entry.pack(side=tk.RIGHT)
            
            # Sauvegarder la référence à la variable
            temp_rates[category] = rate_var
        
        # Bouton de sauvegarde
        save_btn = tk.Button(settings_window, text="Sauvegarder",
                           command=lambda: self.save_category_settings(settings_window, temp_rates),
                           bg=self.get_theme_color('button'),
                           fg=self.get_theme_color('button_fg'))
        save_btn.pack(pady=10)

    def save_category_settings(self, window, temp_rates):
        # Mettre à jour les taux des catégories
        new_rates = {}
        for category, rate_var in temp_rates.items():
            try:
                new_rates[category] = float(rate_var.get())
            except ValueError:
                messagebox.showerror("Erreur", f"Le taux pour {category} n'est pas un nombre valide")
                return
        
        # Mettre à jour les taux
        self.category_rates = new_rates
        
        # Sauvegarder les données
        self.save_data()
        
        # Rafraîchir l'affichage
        self.refresh_entries()
        
        # Fermer la fenêtre
        window.destroy()

    def get_suggested_times(self):
        """Retourne les dates et heures suggérées basées sur les entrées récentes"""
        if not self.entries:
            today = datetime.now()
            return today.strftime("%Y-%m-%d"), "09:00", today.strftime("%Y-%m-%d"), "17:00"
            
        # Trier les entrées par date décroissante
        sorted_entries = sorted(self.entries, 
                              key=lambda x: datetime.strptime(f"{x['start_date']} {x['start_time']}", "%Y-%m-%d %H:%M"),
                              reverse=True)
        
        # Prendre la dernière entrée
        last_entry = sorted_entries[0]
        last_date = datetime.strptime(last_entry['start_date'], "%Y-%m-%d")
        
        # Suggérer la date suivante
        suggested_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Calculer la moyenne des heures de début et de fin des 5 dernières entrées
        start_times = []
        end_times = []
        
        for entry in sorted_entries[:5]:
            start = datetime.strptime(entry['start_time'], "%H:%M")
            end = datetime.strptime(entry['end_time'], "%H:%M")
            start_times.append(start)
            end_times.append(end)
        
        # Calculer la moyenne
        avg_start = sum((t.hour * 60 + t.minute for t in start_times), 0) / len(start_times)
        avg_end = sum((t.hour * 60 + t.minute for t in end_times), 0) / len(end_times)
        
        # Convertir en format HH:MM
        suggested_start = f"{int(avg_start // 60):02d}:{int(avg_start % 60):02d}"
        suggested_end = f"{int(avg_end // 60):02d}:{int(avg_end % 60):02d}"
        
        return suggested_date, suggested_start, suggested_date, suggested_end

    def add_entry(self):
        # Créer une nouvelle fenêtre pour ajouter une entrée
        entry_window = tk.Toplevel(self.root)
        entry_window.title("Nouvelle entrée")
        entry_window.geometry("400x500")  # Augmenté la hauteur pour les nouveaux champs
        entry_window.configure(bg=self.get_theme_color('bg'))
        
        # Obtenir les dates et heures suggérées
        suggested_start_date, suggested_start_time, suggested_end_date, suggested_end_time = self.get_suggested_times()
        
        # Variables pour les champs
        start_date = tk.StringVar(value=suggested_start_date)
        start_time = tk.StringVar(value=suggested_start_time)
        end_date = tk.StringVar(value=suggested_end_date)
        end_time = tk.StringVar(value=suggested_end_time)
        has_break = tk.BooleanVar(value=False)
        break_start_hour = tk.StringVar()
        break_start_min = tk.StringVar()
        break_end_hour = tk.StringVar()
        break_end_min = tk.StringVar()
        
        # Frame pour les champs
        fields_frame = tk.Frame(entry_window, bg=self.get_theme_color('bg'))
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Champs de date et heure
        tk.Label(fields_frame, text="Date de début:", bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(anchor=tk.W)
        start_date_entry = tk.Entry(fields_frame, textvariable=start_date,
                                  bg=self.get_theme_color('bg'),
                                  fg=self.get_theme_color('fg'))
        start_date_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(fields_frame, text="Heure de début:", bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(anchor=tk.W)
        start_time_entry = tk.Entry(fields_frame, textvariable=start_time,
                                  bg=self.get_theme_color('bg'),
                                  fg=self.get_theme_color('fg'))
        start_time_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(fields_frame, text="Date de fin:", bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(anchor=tk.W)
        end_date_entry = tk.Entry(fields_frame, textvariable=end_date,
                                bg=self.get_theme_color('bg'),
                                fg=self.get_theme_color('fg'))
        end_date_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(fields_frame, text="Heure de fin:", bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(anchor=tk.W)
        end_time_entry = tk.Entry(fields_frame, textvariable=end_time,
                                bg=self.get_theme_color('bg'),
                                fg=self.get_theme_color('fg'))
        end_time_entry.pack(fill=tk.X, pady=5)
        
        # Frame pour la pause
        break_frame = tk.LabelFrame(fields_frame, text="Pause",
                                  bg=self.get_theme_color('bg'),
                                  fg=self.get_theme_color('fg'))
        break_frame.pack(fill=tk.X, pady=10)
        
        # Checkbox pour activer la pause
        break_check = tk.Checkbutton(break_frame, text="Activer la pause",
                                   variable=has_break,
                                   command=lambda: self.toggle_break_fields(break_fields_frame),
                                   bg=self.get_theme_color('bg'),
                                   fg=self.get_theme_color('fg'),
                                   selectcolor=self.get_theme_color('bg'),
                                   activebackground=self.get_theme_color('bg'),
                                   activeforeground=self.get_theme_color('fg'))
        break_check.pack(side=tk.LEFT, padx=5)
        
        # Frame pour les champs de pause
        break_fields_frame = tk.Frame(break_frame, bg=self.get_theme_color('bg'))
        break_fields_frame.pack(fill=tk.X, pady=5)
        
        # Heure de début de pause
        tk.Label(break_fields_frame, text="Début pause:",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT, padx=5)
        
        break_start_hour_combo = ttk.Combobox(break_fields_frame,
                                            values=[f"{i:02}" for i in range(24)],
                                            textvariable=break_start_hour,
                                            width=3, state="readonly")
        break_start_hour_combo.pack(side=tk.LEFT, padx=2)
        
        tk.Label(break_fields_frame, text=":",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT)
        
        break_start_min_combo = ttk.Combobox(break_fields_frame,
                                           values=[f"{i:02}" for i in range(0, 60, 5)],
                                           textvariable=break_start_min,
                                           width=3, state="readonly")
        break_start_min_combo.pack(side=tk.LEFT, padx=2)
        
        # Heure de fin de pause
        tk.Label(break_fields_frame, text="Fin pause:",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT, padx=5)
        
        break_end_hour_combo = ttk.Combobox(break_fields_frame,
                                          values=[f"{i:02}" for i in range(24)],
                                          textvariable=break_end_hour,
                                          width=3, state="readonly")
        break_end_hour_combo.pack(side=tk.LEFT, padx=2)
        
        tk.Label(break_fields_frame, text=":",
                bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(side=tk.LEFT)
        
        break_end_min_combo = ttk.Combobox(break_fields_frame,
                                         values=[f"{i:02}" for i in range(0, 60, 5)],
                                         textvariable=break_end_min,
                                         width=3, state="readonly")
        break_end_min_combo.pack(side=tk.LEFT, padx=2)
        
        # Cacher les champs de pause par défaut ou les afficher selon l'état initial
        if self.has_break.get():
            self.break_fields_frame.pack(fill=tk.X, pady=5)
        else:
            self.break_fields_frame.pack_forget()
        
        # Bouton de sauvegarde
        save_btn = tk.Button(entry_window, text="Ajouter",
                           command=lambda: self.save_entry(entry_window, start_date.get(),
                                                         start_time.get(), end_date.get(),
                                                         end_time.get(), has_break.get(),
                                                         break_start_hour.get(),
                                                         break_start_min.get(),
                                                         break_end_hour.get(),
                                                         break_end_min.get()),
                           bg=self.get_theme_color('button'),
                           fg=self.get_theme_color('button_fg'))
        save_btn.pack(pady=10)
        
        # Mettre le focus sur le champ de l'heure de début
        start_time_entry.focus_set()

    def save_entry(self, window, start_date, start_time, end_date, end_time,
                  has_break, break_start_hour, break_start_min, break_end_hour, break_end_min):
        print(f"Attempting to save entry with: start_date={start_date}, start_time={start_time}, end_date={end_date}, end_time={end_time}, has_break={has_break}, break_start_hour={break_start_hour}, break_start_min={break_start_min}, break_end_hour={break_end_hour}, break_end_min={break_end_min}")
        try:
            # Vérifier la durée avant de sauvegarder
            is_valid, result = self.verify_duration(start_date, start_time, end_date, end_time)
            if not is_valid:
                messagebox.showerror("Erreur", result)
                return
            
            # Créer la nouvelle entrée
            entry = {
                'id': self.current_id,
                'start_date': start_date,
                'start_time': start_time,
                'end_date': end_date,
                'end_time': end_time,
                'category': self.current_category.get(),
                'has_break': has_break,
                'break_start_hour': break_start_hour,
                'break_start_min': break_start_min,
                'break_end_hour': break_end_hour,
                'break_end_min': break_end_min
            }
            
            # Ajouter l'entrée à la liste
            self.entries.append(entry)
            self.current_id += 1
            
            # Réorganiser les IDs après l'ajout
            self.reorganize_ids()
            
            # Sauvegarder les données
            self.save_data()
            
            # Fermer la fenêtre
            window.destroy()
            
            # Mettre à jour les statistiques
            self.show_statistics()
            
            return True, result
            
        except ValueError as e:
            print(f"verify_duration ValueError: {e}")
            return False, f"Format de date/heure invalide: {str(e)}"
        except Exception as e:
            print(f"verify_duration Exception: {e}")
            return False, f"Erreur lors de la vérification: {str(e)}"

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Attention", "Veuillez sélectionner une entrée à supprimer")
            return
            
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer les entrées sélectionnées ?"):
            # Récupérer les IDs des entrées sélectionnées
            selected_ids = [int(self.tree.item(item)['values'][0]) for item in selected_items]
            
            # Supprimer les entrées de la liste
            self.entries = [entry for entry in self.entries if entry['id'] not in selected_ids]
            
            # Réorganiser les IDs après la suppression
            self.reorganize_ids()
            
            # Sauvegarder les données
            self.save_data()
            
            # Rafraîchir l'affichage
            self.refresh_entries()
            
            # Mettre à jour les statistiques
            self.show_statistics()

    def show_export_options(self):
        """Affiche les options d'export avec sélection des colonnes"""
        export_window = tk.Toplevel(self.root)
        export_window.title("Options d'export")
        export_window.geometry("400x500")
        export_window.configure(bg=self.get_theme_color('bg'))
        
        # Frame pour les colonnes
        columns_frame = tk.LabelFrame(export_window, text="Colonnes à exporter",
                                    bg=self.get_theme_color('bg'),
                                    fg=self.get_theme_color('fg'))
        columns_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Variables pour les colonnes
        columns_vars = {
            'ID': tk.BooleanVar(value=True),
            'Date': tk.BooleanVar(value=True),
            'Heure début': tk.BooleanVar(value=True),
            'Début pause': tk.BooleanVar(value=True),
            'Fin pause': tk.BooleanVar(value=True),
            'Heure fin': tk.BooleanVar(value=True),
            'Durée': tk.BooleanVar(value=True),
            'Catégorie': tk.BooleanVar(value=False),
            'Montant': tk.BooleanVar(value=False)
        }
        
        # Créer les checkboxes pour chaque colonne
        for col, var in columns_vars.items():
            tk.Checkbutton(columns_frame, text=col, variable=var,
                          bg=self.get_theme_color('bg'),
                          fg=self.get_theme_color('fg'),
                          selectcolor=self.get_theme_color('bg'),
                          activebackground=self.get_theme_color('bg'),
                          activeforeground=self.get_theme_color('fg')).pack(anchor=tk.W, padx=5, pady=2)
        
        # Frame pour les boutons
        buttons_frame = tk.Frame(export_window, bg=self.get_theme_color('bg'))
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Boutons d'export
        tk.Button(buttons_frame, text="Exporter en PDF",
                 command=lambda: self.export_pdf(columns_vars),
                 bg=self.get_theme_color('button'),
                 fg=self.get_theme_color('button_fg')).pack(fill=tk.X, pady=5)
        
        tk.Button(buttons_frame, text="Exporter en PNG",
                 command=lambda: self.export_png(columns_vars),
                 bg=self.get_theme_color('button'),
                 fg=self.get_theme_color('button_fg')).pack(fill=tk.X, pady=5)

    def export_pdf(self, columns_vars):
        """Exporte les données en PDF avec les colonnes sélectionnées"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Demander le nom du fichier
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Exporter en PDF"
            )
            
            if not filename:
                return
            
            # Créer le document
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30
            )
            elements.append(Paragraph("Rapport des heures travaillées", title_style))
            elements.append(Spacer(1, 20))
            
            # Préparer les données du tableau
            headers = []
            for col, var in columns_vars.items():
                if var.get():
                    headers.append(col)
            
            data = [headers]
            total_hours = 0.0
            total_amount = 0.0
            
            for entry in self.entries:
                duration = self.calculate_duration(entry)
                amount = duration * self.hourly_rate.get()
                total_hours += duration
                total_amount += amount
                
                row = []
                for col, var in columns_vars.items():
                    if var.get():
                        if col == 'ID':
                            row.append(str(entry['id']))
                        elif col == 'Date':
                            row.append(entry['start_date'])
                        elif col == 'Heure début':
                            row.append(entry['start_time'])
                        elif col == 'Début pause':
                            row.append(f"{entry.get('break_start_hour', '')}:{entry.get('break_start_min', '')}" if entry.get('has_break') else '')
                        elif col == 'Fin pause':
                            row.append(f"{entry.get('break_end_hour', '')}:{entry.get('break_end_min', '')}" if entry.get('has_break') else '')
                        elif col == 'Heure fin':
                            row.append(entry['end_time'])
                        elif col == 'Durée':
                            row.append(f"{duration:.2f}")
                        elif col == 'Catégorie':
                            row.append(entry.get('category', ''))
                        elif col == 'Montant':
                            row.append(f"{amount:.2f} €")
                data.append(row)
            
            # Ajouter les totaux
            totals = [''] * len(headers)
            if 'Durée' in headers:
                totals[headers.index('Durée')] = f"{total_hours:.2f}"
            if 'Montant' in headers:
                totals[headers.index('Montant')] = f"{total_amount:.2f} €"
            data.append(totals)
            
            # Créer le tableau
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
            
            # Générer le PDF
            doc.build(elements)
            
            messagebox.showinfo("Succès", "Export PDF réussi !")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export PDF : {str(e)}")

    def export_png(self, columns_vars):
        """Exporte les données en image PNG avec les colonnes sélectionnées"""
        try:
            # Demander le nom du fichier
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                title="Exporter en PNG"
            )
            
            if not filename:
                return
            
            # Créer une nouvelle figure
            fig = Figure(figsize=(12, 8))
            ax = fig.add_subplot(111)
            
            # Cacher les axes
            ax.axis('off')
            
            # Préparer les données
            headers = []
            for col, var in columns_vars.items():
                if var.get():
                    headers.append(col)
            
            data = [headers]
            total_hours = 0.0
            total_amount = 0.0
            
            for entry in self.entries:
                duration = self.calculate_duration(entry)
                amount = duration * self.hourly_rate.get()
                total_hours += duration
                total_amount += amount
                
                row = []
                for col, var in columns_vars.items():
                    if var.get():
                        if col == 'ID':
                            row.append(str(entry['id']))
                        elif col == 'Date':
                            row.append(entry['start_date'])
                        elif col == 'Heure début':
                            row.append(entry['start_time'])
                        elif col == 'Début pause':
                            row.append(f"{entry.get('break_start_hour', '')}:{entry.get('break_start_min', '')}" if entry.get('has_break') else '')
                        elif col == 'Fin pause':
                            row.append(f"{entry.get('break_end_hour', '')}:{entry.get('break_end_min', '')}" if entry.get('has_break') else '')
                        elif col == 'Heure fin':
                            row.append(entry['end_time'])
                        elif col == 'Durée':
                            row.append(f"{duration:.2f}")
                        elif col == 'Catégorie':
                            row.append(entry.get('category', ''))
                        elif col == 'Montant':
                            row.append(f"{amount:.2f} €")
                data.append(row)
            
            # Ajouter les totaux
            totals = [''] * len(headers)
            if 'Durée' in headers:
                totals[headers.index('Durée')] = f"{total_hours:.2f}"
            if 'Montant' in headers:
                totals[headers.index('Montant')] = f"{total_amount:.2f} €"
            data.append(totals)
            
            # Créer le tableau
            table = ax.table(cellText=data,
                           loc='center',
                           cellLoc='center',
                           colWidths=[0.1] * len(headers))
            
            # Styliser le tableau
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1.2, 1.5)
            
            # Ajouter un titre
            ax.set_title("Rapport des heures travaillées", pad=20)
            
            # Sauvegarder l'image
            fig.savefig(filename, bbox_inches='tight', dpi=300)
            
            messagebox.showinfo("Succès", "Export PNG réussi !")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export PNG : {str(e)}")

    def update_totals(self):
        """Met à jour l'affichage des totaux"""
        total_hours = 0.0
        total_amount = 0.0
        
        for entry in self.entries:
            duration = self.calculate_duration(entry)
            total_hours += duration
            total_amount += duration * self.hourly_rate.get()
        
        self.total_hours_label.config(text=f"Total des heures: {total_hours:.2f}")
        self.total_amount_label.config(text=f"Total des gains: {total_amount:.2f} €")

    def refresh_entries(self):
        """Rafraîchit l'affichage des entrées dans le tableau"""
        # Effacer toutes les entrées existantes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ajouter les entrées au tableau
        for entry in self.entries:
            try:
                duration = self.calculate_duration(entry)
                amount = duration * self.hourly_rate.get()
                
                self.tree.insert('', tk.END, values=(
                    entry['id'],
                    entry['start_date'],
                    entry['start_time'],
                    f"{entry.get('break_start_hour', '')}:{entry.get('break_start_min', '')}" if entry.get('has_break') else '',
                    f"{entry.get('break_end_hour', '')}:{entry.get('break_end_min', '')}" if entry.get('has_break') else '',
                    entry['end_time'],
                    f"{duration:.2f}",
                    entry.get('category', self.categories[0]),
                    f"{amount:.2f}"
                ))
            except Exception as e:
                print(f"Erreur lors de l'affichage de l'entrée {entry['id']}: {e}")
        
        # Mettre à jour les totaux
        self.update_totals()

    def edit_selected(self):
        """Modifie l'entrée sélectionnée"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Attention", "Veuillez sélectionner une entrée à modifier")
            return
            
        if len(selected_items) > 1:
            messagebox.showwarning("Attention", "Veuillez sélectionner une seule entrée à modifier")
            return
            
        # Récupérer l'ID de l'entrée sélectionnée
        selected_id = int(self.tree.item(selected_items[0])['values'][0])
        
        # Trouver l'entrée correspondante
        entry = next((e for e in self.entries if e['id'] == selected_id), None)
        if not entry:
            messagebox.showerror("Erreur", "Entrée non trouvée")
            return
            
        # Créer une nouvelle fenêtre pour modifier l'entrée
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Modifier l'entrée")
        edit_window.geometry("400x400")
        edit_window.configure(bg=self.get_theme_color('bg'))
        
        # Variables pour les champs
        start_date = tk.StringVar(value=entry['start_date'])
        start_time = tk.StringVar(value=entry['start_time'])
        end_date = tk.StringVar(value=entry['end_date'])
        end_time = tk.StringVar(value=entry['end_time'])
        category = tk.StringVar(value=entry.get('category', self.categories[0]))
        
        # Frame pour les champs
        fields_frame = tk.Frame(edit_window, bg=self.get_theme_color('bg'))
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Champs de date et heure
        tk.Label(fields_frame, text="Date de début:", bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(anchor=tk.W)
        start_date_entry = tk.Entry(fields_frame, textvariable=start_date,
                                  bg=self.get_theme_color('bg'),
                                  fg=self.get_theme_color('fg'))
        start_date_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(fields_frame, text="Heure de début:", bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(anchor=tk.W)
        start_time_entry = tk.Entry(fields_frame, textvariable=start_time,
                                  bg=self.get_theme_color('bg'),
                                  fg=self.get_theme_color('fg'))
        start_time_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(fields_frame, text="Date de fin:", bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(anchor=tk.W)
        end_date_entry = tk.Entry(fields_frame, textvariable=end_date,
                                bg=self.get_theme_color('bg'),
                                fg=self.get_theme_color('fg'))
        end_date_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(fields_frame, text="Heure de fin:", bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(anchor=tk.W)
        end_time_entry = tk.Entry(fields_frame, textvariable=end_time,
                                bg=self.get_theme_color('bg'),
                                fg=self.get_theme_color('fg'))
        end_time_entry.pack(fill=tk.X, pady=5)
        
        # Catégorie
        tk.Label(fields_frame, text="Catégorie:", bg=self.get_theme_color('bg'),
                fg=self.get_theme_color('fg')).pack(anchor=tk.W)
        category_combo = ttk.Combobox(fields_frame, textvariable=category,
                                    values=self.categories, state="readonly")
        category_combo.pack(fill=tk.X, pady=5)
        
        # Bouton de sauvegarde
        save_btn = tk.Button(edit_window, text="Enregistrer",
                           command=lambda: self.save_edit(edit_window, entry, start_date.get(),
                                                        start_time.get(), end_date.get(),
                                                        end_time.get(), category.get()),
                           bg=self.get_theme_color('button'),
                           fg=self.get_theme_color('button_fg'))
        save_btn.pack(pady=10)
        
        # Mettre le focus sur le champ de l'heure de début
        start_time_entry.focus_set()

    def save_edit(self, window, entry, start_date, start_time, end_date, end_time, category):
        """Sauvegarde les modifications d'une entrée"""
        try:
            # Vérifier la durée avant de sauvegarder
            is_valid, result = self.verify_duration(start_date, start_time, end_date, end_time)
            if not is_valid:
                messagebox.showerror("Erreur", result)
                return
            
            # Mettre à jour l'entrée
            entry['start_date'] = start_date
            entry['start_time'] = start_time
            entry['end_date'] = end_date
            entry['end_time'] = end_time
            entry['category'] = category
            
            # Réorganiser les IDs après la modification
            self.reorganize_ids()
            
            # Sauvegarder les données
            self.save_data()
            
            # Fermer la fenêtre
            window.destroy()
            
            # Rafraîchir l'affichage
            self.refresh_entries()
            
            # Mettre à jour les statistiques
            self.show_statistics()
            
        except ValueError:
            messagebox.showerror("Erreur", "Format de date ou d'heure invalide")

    def reorganize_ids(self):
        """Réorganise les IDs des entrées pour s'assurer qu'ils sont séquentiels"""
        try:
            # Trier les entrées par date et heure de début
            sorted_entries = sorted(self.entries, 
                                  key=lambda x: datetime.strptime(f"{x['start_date']} {x['start_time']}", "%Y-%m-%d %H:%M"))
            
            # Réassigner les IDs
            for i, entry in enumerate(sorted_entries):
                entry['id'] = i
            
            # Mettre à jour l'ID courant
            self.current_id = len(sorted_entries)
            
            # Sauvegarder les modifications
            self.save_data()
            
            # Rafraîchir l'affichage
            self.refresh_entries()
            
            return True
        except Exception as e:
            print(f"Erreur lors de la réorganisation des IDs: {e}")
            return False

    def check_all_durations(self):
        """Vérifie toutes les durées et affiche un rapport détaillé"""
        issues = []
        total_duration = 0.0
        
        for entry in self.entries:
            try:
                # Calculer la durée brute
                start = datetime.strptime(f"{entry['start_date']} {entry['start_time']}", "%Y-%m-%d %H:%M")
                end = datetime.strptime(f"{entry['end_date']} {entry['end_time']}", "%Y-%m-%d %H:%M")
                raw_duration = (end - start).total_seconds() / 3600
                
                # Calculer la durée avec pauses
                final_duration = self.calculate_duration(entry)
                
                # Vérifier les problèmes potentiels
                if raw_duration <= 0:
                    issues.append(f"Entrée {entry['id']}: Durée brute invalide ({raw_duration:.2f}h)")
                elif raw_duration > 24:
                    issues.append(f"Entrée {entry['id']}: Durée brute supérieure à 24h ({raw_duration:.2f}h)")
                elif final_duration <= 0:
                    issues.append(f"Entrée {entry['id']}: Durée finale nulle ou négative ({final_duration:.2f}h)")
                elif abs(final_duration - raw_duration) > 2:  # Si la différence est supérieure à 2h
                    issues.append(f"Entrée {entry['id']}: Grande différence entre durée brute ({raw_duration:.2f}h) et finale ({final_duration:.2f}h)")
                
                total_duration += final_duration
                
            except Exception as e:
                issues.append(f"Entrée {entry['id']}: Erreur lors de la vérification - {str(e)}")
        
        # Préparer le message
        message = f"Total des heures: {total_duration:.2f}h\n\n"
        
        if issues:
            message += "Problèmes détectés:\n\n" + "\n".join(issues)
            messagebox.showwarning("Vérification des durées", message)
        else:
            message += "Aucun problème détecté dans les durées."
            messagebox.showinfo("Vérification des durées", message)

    def clear_all_entries(self):
        """Vide toutes les entrées du tableau après confirmation"""
        if not self.entries:
            messagebox.showinfo("Information", "Le tableau est déjà vide")
            return
            
        if messagebox.askyesno("Confirmation", 
                              "Êtes-vous sûr de vouloir supprimer toutes les entrées ?\nCette action est irréversible."):
            # Vider la liste des entrées
            self.entries = []
            self.current_id = 0
            
            # Sauvegarder les données
            self.save_data()
            
            # Rafraîchir l'affichage
            self.refresh_entries()
            
            # Mettre à jour les statistiques
            self.show_statistics()
            
            messagebox.showinfo("Succès", "Toutes les entrées ont été supprimées")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkHoursApp(root)
    root.mainloop()