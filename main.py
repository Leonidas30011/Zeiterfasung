import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import date, datetime
from tkinter import ttk
import sqlite3
import traceback
from pathlib import Path
import subprocess
import sys


def log_exception( exc: BaseException ):
	log = Path( __file__ ).with_name( "error.log" )
	log.write_text( traceback.format_exc(), encoding = "utf-8" )


try:
	# --- ab hier kommt dein restlicher Code ---

	def apply_ttk_dark_theme( root ):
		style = ttk.Style( root )
		style.theme_use( "clam" )

		# Palette
		bg = "#0f1115"  # App Hintergrund
		panel = "#171a21"  # Card Hintergrund
		fg = "#e6e6e6"
		muted = "#b7bcc8"
		accent = "#4c8bf5"
		border = "#2a2f3a"
		entry_bg = "#0b0d12"
		hover = "#1d2330"
		pressed = "#111520"

		root.configure( bg = bg )

		# Für tk Widgets
		root.option_add( "*Entry.background", entry_bg )
		root.option_add( "*Entry.foreground", fg )
		root.option_add( "*Entry.insertBackground", fg )

		root.option_add( "*Spinbox.background", entry_bg )
		root.option_add( "*Spinbox.foreground", fg )
		root.option_add( "*Spinbox.insertBackground", fg )

		# Global
		style.configure( ".", font = ("Segoe UI", 10), foreground = fg )

		# Frames
		style.configure( "TFrame", background = bg )
		style.configure( "Card.TFrame", background = panel, relief = "solid", borderwidth = 1 )

		# Labels:
		# Default Label ohne "falschen" Hintergrund -> bg = bg
		style.configure( "TLabel", background = bg, foreground = fg )
		# Labels die auf Cards liegen -> bg = panel
		style.configure( "Card.TLabel", background = panel, foreground = fg )
		style.configure( "Muted.Card.TLabel", background = panel, foreground = muted )

		# Titel auf Cards
		style.configure( "CardTitle.TLabel", background = panel, foreground = fg, font = ("Segoe UI", 12, "bold") )

		# Buttons
		style.configure( "TButton", background = panel, foreground = fg, padding = (10, 6) )
		style.map( "TButton",
		           background = [ ("active", hover), ("pressed", pressed) ],
		           foreground = [ ("disabled", "#777") ] )

		style.configure( "Accent.TButton", background = accent, foreground = "#ffffff", padding = (10, 6) )
		style.map( "Accent.TButton",
		           background = [ ("active", "#3a78e0"), ("pressed", "#2f61b8") ] )

		# Entry
		style.configure( "TEntry",
		                 fieldbackground = entry_bg,
		                 foreground = fg,
		                 insertcolor = fg )

		# Combobox
		style.configure( "TCombobox",
		                 fieldbackground = entry_bg,
		                 foreground = fg,
		                 background = panel )

		style.map( "TCombobox",
		           fieldbackground = [ ("readonly", entry_bg), ("!readonly", entry_bg) ],
		           foreground = [ ("readonly", fg), ("!readonly", fg) ],
		           background = [ ("readonly", entry_bg), ("!readonly", entry_bg) ],
		           selectbackground = [ ("readonly", hover) ],
		           selectforeground = [ ("readonly", fg) ] )

		# Dropdown Listbox (Win11)
		root.option_add( "*TCombobox*Listbox.background", entry_bg )
		root.option_add( "*TCombobox*Listbox.foreground", fg )
		root.option_add( "*TCombobox*Listbox.selectBackground", hover )
		root.option_add( "*TCombobox*Listbox.selectForeground", fg )
		root.option_add( "*TCombobox*Listbox.borderWidth", 0 )
		root.option_add( "*TCombobox*Listbox.highlightThickness", 0 )

		# Menüs (OptionMenu / tk.Menu)
		root.option_add( "*Menu.background", panel )
		root.option_add( "*Menu.foreground", fg )
		root.option_add( "*Menu.activeBackground", hover )
		root.option_add( "*Menu.activeForeground", fg )

		return style


	def format_dt( db_string ):
		if db_string is None:
			return "-"
		dt = datetime.strptime( db_string, "%Y-%m-%d %H:%M:%S" )
		return dt.strftime( "%d.%m.%Y %H:%M" )


	def init_db():
		db_dir = Path( "datenbank" )
		db_dir.mkdir( parents = True, exist_ok = True )  # Ordner sicherstellen

		db_path = db_dir / "Zeiterfassung.db"
		sql_path = db_dir / "init.sql"

		with sql_path.open( "r", encoding = "utf-8" ) as f:
			ddl = f.read()

		conn = sqlite3.connect( str( db_path ) )
		try:
			conn.execute( "PRAGMA foreign_keys = ON;" )
			conn.executescript( ddl )
			conn.commit()
		finally:
			conn.close()


	def sql_commit( sql ):
		verbindung = sqlite3.connect( "datenbank/Zeiterfassung.db" )
		zeiger = verbindung.cursor()
		zeiger.execute( sql )
		verbindung.commit()
		verbindung.close()


	def sql_commit2( sql, params = () ):
		conn = sqlite3.connect( "datenbank/Zeiterfassung.db" )
		cur = conn.cursor()
		cur.execute( sql, params )
		conn.commit()
		conn.close()


	def sql_select( sql ):
		verbindung = sqlite3.connect( "datenbank/Zeiterfassung.db" )
		zeiger = verbindung.cursor()
		zeiger.execute( sql )
		ergebnis = zeiger.fetchall()
		return ergebnis


	def sql_select2( sql, params = () ):
		conn = sqlite3.connect( "datenbank/Zeiterfassung.db" )
		cur = conn.cursor()
		cur.execute( sql, params )
		ergebnis = cur.fetchall()
		return ergebnis


	def Auswertung():
		subprocess.run( [ sys.executable, "auswertung.pyw" ] )



	def Projekt_Anlegen():
		def refresh_listbox():
			lbox.delete( 0, tk.END )
			projekte_liste2 = sql_select( "SELECT name FROM projekte;" )
			for (name,) in projekte_liste2:
				lbox.insert( tk.END, name )

		def ANLEGEN( name2 ):
			name2 = name2.strip()
			if name2 != "":
				sql_str = "INSERT INTO projekte (name) VALUES (?);"
				sql_commit2( sql_str, (name2,) )
				name_var.set( "" )
				refresh_listbox()
			else:
				messagebox.showinfo( "Anlegen nicht möglich", "Bitte gib einen Namen ein." )
				entry_name.focus_set()

		def LOESCHEN():
			auswahl = lbox.curselection()
			if auswahl:
				idx = auswahl[ 0 ]
				name_projekt = lbox.get( idx )
				answer = messagebox.askyesno(
					f"SIE LÖSCHEN PROJEKT {name_projekt}!",
					f"Wollen Sie das Projekt '{name_projekt}' wirklich löschen?"
				)
				if answer:
					sql_commit2( "DELETE FROM projekte WHERE name = ?;", (name_projekt,) )
					refresh_listbox()
					win.focus_force()
			else:
				messagebox.showinfo( "Löschen nicht möglich", "Bitte wähle ein Projekt aus" )

		win = tk.Toplevel()
		win.title( "Stempeluhr - Projekt anlegen" )
		win.geometry( "420x420" )
		win.resizable( False, False )
		win.iconbitmap( "src/sanduhr.ico" )
		win.configure( bg = "#0f1115" )

		outer = ttk.Frame( win, style = "Card.TFrame" )
		outer.pack( fill = "both", expand = True, padx = 12, pady = 12 )

		title = ttk.Label( outer, text = "Projekt anlegen", style = "CardTitle.TLabel" )
		title.grid( row = 0, column = 0, columnspan = 2, sticky = "w", pady = (0, 10) )

		# Eingabe
		ttk.Label( outer, text = "Projektname:", style = "CardTitle.TLabel" ).grid( row = 1, column = 0, sticky = "w",
		                                                                            padx = (0, 8), pady = 6 )
		name_var = tk.StringVar()
		entry_name = ttk.Entry( outer, textvariable = name_var )
		entry_name.grid( row = 1, column = 1, sticky = "ew", pady = 6 )

		# Buttons
		btn_frame = ttk.Frame( outer )
		btn_frame.grid( row = 2, column = 0, columnspan = 2, sticky = "ew", pady = (6, 10) )
		btn_frame.columnconfigure( 0, weight = 1, uniform = "pbtn" )
		btn_frame.columnconfigure( 1, weight = 1, uniform = "pbtn" )

		ttk.Button( btn_frame, text = "Anlegen", style = "Accent.TButton",
		            command = lambda: ANLEGEN( name_var.get() ) ).grid(
			row = 0, column = 0, sticky = "ew", padx = (0, 6)
		)
		ttk.Button( btn_frame, text = "Ausgewähltes Projekt löschen", command = LOESCHEN ).grid(
			row = 0, column = 1, sticky = "ew", padx = (6, 0)
		)

		# Listbox
		ttk.Label( outer, text = "Vorhandene Projekte:", style = "CardTitle.TLabel" ).grid( row = 3, column = 0,
		                                                                                    columnspan = 2,
		                                                                                    sticky = "w",
		                                                                                    pady = (6, 6) )

		list_frame = ttk.Frame( outer, style = "Card.TFrame" )
		list_frame.grid( row = 4, column = 0, columnspan = 2, sticky = "nsew" )

		scroll = tk.Scrollbar( list_frame )
		scroll.pack( side = "right", fill = "y" )

		lbox = tk.Listbox(
			list_frame,
			bg = "#0b0d12",
			fg = "#e6e6e6",
			selectbackground = "#1d2330",
			selectforeground = "#e6e6e6",
			highlightthickness = 1,
			highlightbackground = "#2a2f3a",
			relief = "flat",
			yscrollcommand = scroll.set
		)
		lbox.pack( side = "left", fill = "both", expand = True, padx = 8, pady = 8 )
		scroll.config( command = lbox.yview )

		# Back Button
		ttk.Button( outer, text = "Zurück", command = win.destroy ).grid( row = 5, column = 0, columnspan = 2,
		                                                                  sticky = "ew", pady = (10, 0) )

		outer.columnconfigure( 1, weight = 1 )
		outer.rowconfigure( 4, weight = 1 )

		refresh_listbox()
		entry_name.focus_set()


	def Person_Anlegen():
		def refresh_listbox():
			lbox.delete( 0, tk.END )
			projekte_liste2 = sql_select( "SELECT  id, name, role, art FROM personen;" )
			for x in projekte_liste2:
				id, person, role, art = x

				text = (
					f"{id:<2} | "
					f"Name: {person:<16} | "
					f"Rolle: {role or '-':<8} | "
					f"Art: {art or '-':<8} | "
				)

				lbox.insert( tk.END, text )

		def ANLEGEN( name, role, art ):
			name = name.strip()
			if name != "":
				sql_str = "INSERT INTO personen (name, role, art) VALUES (?, ?, ?);"
				sql_commit2( sql_str, (name, role, art,) )
				name_var.set( "" )
				role_var.set( "" )
				art_var.set( "" )
				refresh_listbox()
			else:
				messagebox.showinfo( "Anlegen nicht möglich", "Bitte gib einen Namen ein." )
				entry_name.focus_set()

		def LOESCHEN():
			auswahl = lbox.curselection()
			if auswahl:
				idx = auswahl
				inhalt_box = lbox.get( idx )
				id_var = inhalt_box[ 0 ]
				((name_var,),) = sql_select2( "SELECT name FROM personen WHERE id = ?;", (id_var,) )
				answer = messagebox.askyesno(
					f"SIE LÖSCHEN PERSON {name_var}!",
					f"Wollen Sie die Person '{name_var}' wirklich löschen?"
				)
				if answer:
					sql_commit2( "DELETE FROM personen WHERE id = ?;", (id_var,) )
					refresh_listbox()

			else:
				messagebox.showinfo( "Löschen nicht möglich", "Bitte wähle eine Person aus" )
			win.focus_force()

		win = tk.Toplevel()
		win.title( "Stempeluhr - Person anlegen" )
		win.geometry( "420x500" )
		win.resizable( False, False )
		win.iconbitmap( "src/sanduhr.ico" )
		win.configure( bg = "#0f1115" )

		outer = ttk.Frame( win, style = "Card.TFrame" )
		outer.pack( fill = "both", expand = True, padx = 12, pady = 12 )

		title = ttk.Label( outer, text = "Person anlegen", style = "CardTitle.TLabel" )
		title.grid( row = 0, column = 0, columnspan = 2, sticky = "w", pady = (0, 10) )

		# Eingabe Name
		ttk.Label( outer, text = "Name der Person:", style = "CardTitle.TLabel" ).grid( row = 1, column = 0,
		                                                                                sticky = "w",
		                                                                                padx = (0, 8), pady = 6 )
		name_var = tk.StringVar()
		entry_name = ttk.Entry( outer, textvariable = name_var )
		entry_name.grid( row = 1, column = 1, sticky = "ew", pady = 6 )

		# Eingabe Rolle
		roles = ('Chef', 'DEVELOPER', 'TESTER', 'Büro', 'Andere')
		ttk.Label( outer, text = "Rolle der Person:", style = "CardTitle.TLabel" ).grid( row = 2, column = 0,
		                                                                                 sticky = "w",
		                                                                                 padx = (0, 8), pady = 6 )
		role_var = tk.StringVar()
		entry_name = ttk.Combobox( outer, textvariable = role_var, values = roles, state = "readonly" )
		entry_name.grid( row = 2, column = 1, sticky = "ew", pady = 6 )

		# Eingabe Art
		arts = ('Ja', 'Vollzeit', 'Teilzeit', 'Mini-Job', 'Extern')
		ttk.Label( outer, text = "Einstellungs Art:", style = "CardTitle.TLabel" ).grid( row = 3, column = 0,
		                                                                                 sticky = "w",
		                                                                                 padx = (0, 8), pady = 6 )
		art_var = tk.StringVar()
		entry_name = ttk.Combobox( outer, textvariable = art_var, values = arts, state = "readonly" )
		entry_name.grid( row = 3, column = 1, sticky = "ew", pady = 6 )

		# Buttons
		btn_frame = ttk.Frame( outer )
		btn_frame.grid( row = 6, column = 0, columnspan = 2, sticky = "ew", pady = (6, 10) )
		btn_frame.columnconfigure( 0, weight = 1, uniform = "pbtn" )
		btn_frame.columnconfigure( 1, weight = 1, uniform = "pbtn" )

		ttk.Button( btn_frame, text = "Anlegen", style = "Accent.TButton",
		            command = lambda: ANLEGEN( name_var.get(), role_var.get(), art_var.get() ) ).grid(
			row = 0, column = 0, sticky = "ew", padx = (0, 6)
		)
		ttk.Button( btn_frame, text = "Ausgewählte Person löschen", command = LOESCHEN ).grid(
			row = 0, column = 1, sticky = "ew", padx = (6, 0)
		)

		# Listbox
		ttk.Label( outer, text = "Vorhandene Personen:", style = "CardTitle.TLabel" ).grid( row = 4, column = 0,

		                                                                                    sticky = "w",
		                                                                                    pady = (6, 6) )

		list_frame = ttk.Frame( outer, style = "Card.TFrame" )
		list_frame.grid( row = 5, column = 0, columnspan = 2, sticky = "nsew" )

		scroll = tk.Scrollbar( list_frame )
		scroll.pack( side = "right", fill = "y" )

		lbox = tk.Listbox(
			list_frame,
			bg = "#0b0d12",
			fg = "#e6e6e6",
			selectbackground = "#1d2330",
			selectforeground = "#e6e6e6",
			highlightthickness = 1,
			highlightbackground = "#2a2f3a",
			relief = "flat",
			yscrollcommand = scroll.set
		)
		lbox.pack( side = "left", fill = "both", expand = True, padx = 8, pady = 8 )
		scroll.config( command = lbox.yview )

		# Back Button
		ttk.Button( outer, text = "Zurück", command = win.destroy ).grid( row = 7, column = 0, columnspan = 2,
		                                                                  sticky = "ew", pady = (10, 0) )

		outer.columnconfigure( 1, weight = 1 )
		outer.rowconfigure( 4, weight = 1 )

		refresh_listbox()
		entry_name.focus_set()


	def Zeit_Nachtraeglich_erfassen( voreinstellung ):
		buchung_id = voreinstellung if voreinstellung != "" else None

		win = tk.Toplevel()
		win.title( "Stempeluhr - Buchung ändern" if buchung_id else "Stempeluhr - Zeit nachträglich erfassen" )
		win.geometry( "460x332" )
		win.resizable( False, False )
		win.iconbitmap( "src/sanduhr.ico" )
		win.configure( bg = "#0f1115" )

		outer = ttk.Frame( win, style = "Card.TFrame" )
		outer.pack( fill = "both", expand = True, padx = 12, pady = 12 )

		ttk.Label(
			outer,
			text = "Buchung ändern" if buchung_id else "Zeit nachträglich erfassen",
			style = "CardTitle.TLabel"
		).grid( row = 0, column = 0, columnspan = 2, sticky = "w", pady = (0, 12) )

		# --- Defaults laden ---
		if buchung_id:
			sql = """
                  select buchungen.id, p.name, p2.name, einstempelzeit, ausstempelzeit
                  from buchungen
                           left join personen p on buchungen.person_id = p.id
                           left join projekte p2 on buchungen.projekt_id = p2.id
                  where buchungen.id = ?; \
			      """
			rows = sql_select2( sql, (buchung_id,) )
			if not rows:
				messagebox.showerror( "Fehler", "Buchung existiert nicht mehr" )
				win.destroy()
				return None

			_, person_def, projekt_def, start_def, ende_def = rows[ 0 ]
			dt_in = datetime.strptime( start_def, "%Y-%m-%d %H:%M:%S" )
			dt_out = datetime.strptime( ende_def, "%Y-%m-%d %H:%M:%S" )

			in_date_def = dt_in.date()
			in_h_def = dt_in.strftime( "%H" )
			in_m_def = dt_in.strftime( "%M" )

			out_date_def = dt_out.date()
			out_h_def = dt_out.strftime( "%H" )
			out_m_def = dt_out.strftime( "%M" )
		else:
			person_def = ""
			projekt_def = ""
			in_date_def = date.today()
			in_h_def = ""
			in_m_def = ""
			out_date_def = date.today()
			out_h_def = ""
			out_m_def = ""

		# --- Datenquellen ---
		projekte = [ row[ 0 ] for row in sql_select( "SELECT name FROM projekte;" ) ]
		personen = [ row[ 0 ] for row in sql_select( "SELECT name FROM personen;" ) ]

		# --- Projekt ---
		ttk.Label( outer, text = "Projekt:", style = "CardTitle.TLabel" ).grid( row = 1, column = 0, sticky = "w",
		                                                                        padx = (0, 8), pady = 6 )
		var_projekt = tk.StringVar( value = projekt_def )
		cb_projekt = ttk.Combobox( outer, textvariable = var_projekt, values = projekte, state = "readonly" )
		cb_projekt.grid( row = 1, column = 1, sticky = "ew", pady = 6 )

		# --- Person ---
		ttk.Label( outer, text = "Person:", style = "CardTitle.TLabel" ).grid( row = 2, column = 0, sticky = "w",
		                                                                       padx = (0, 8), pady = 6 )
		var_person = tk.StringVar( value = person_def )
		cb_person = ttk.Combobox( outer, textvariable = var_person, values = personen, state = "readonly" )
		cb_person.grid( row = 2, column = 1, sticky = "ew", pady = 6 )

		# --- Von Datum ---
		ttk.Label( outer, text = "Von Datum:", style = "CardTitle.TLabel" ).grid( row = 3, column = 0, sticky = "w",
		                                                                          padx = (0, 8), pady = 6 )
		in_cal = DateEntry( outer, width = 14, background = "black", foreground = "white", date_pattern = "dd.mm.yyyy" )
		in_cal.set_date( in_date_def )
		in_cal.grid( row = 3, column = 1, sticky = "w", pady = 6 )

		# --- Von Zeit ---
		ttk.Label( outer, text = "Von Zeit:", style = "CardTitle.TLabel" ).grid( row = 4, column = 0, sticky = "w",
		                                                                         padx = (0, 8), pady = 6 )
		time_in_frame = ttk.Frame( outer )
		time_in_frame.grid( row = 4, column = 1, sticky = "w", pady = 6 )

		stunden = [ f"{h:02d}" for h in range( 24 ) ]
		minuten = [ f"{m:02d}" for m in range( 0, 60, 5 ) ]

		in_time_h = tk.StringVar( value = in_h_def )
		in_time_m = tk.StringVar( value = in_m_def )

		cb_in_h = ttk.Combobox( time_in_frame, textvariable = in_time_h, values = stunden, width = 5,
		                        state = "readonly" )
		cb_in_m = ttk.Combobox( time_in_frame, textvariable = in_time_m, values = minuten, width = 5,
		                        state = "readonly" )
		cb_in_h.grid( row = 0, column = 0, padx = (0, 8) )
		cb_in_m.grid( row = 0, column = 1 )

		# --- Bis Datum ---
		ttk.Label( outer, text = "Bis Datum:", style = "CardTitle.TLabel" ).grid( row = 5, column = 0, sticky = "w",
		                                                                          padx = (0, 8), pady = 6 )
		out_cal = DateEntry( outer, width = 14, background = "darkblue", foreground = "white",
		                     date_pattern = "dd.mm.yyyy" )
		out_cal.set_date( out_date_def )
		out_cal.grid( row = 5, column = 1, sticky = "w", pady = 6 )

		# --- Bis Zeit ---
		ttk.Label( outer, text = "Bis Zeit:", style = "CardTitle.TLabel" ).grid( row = 6, column = 0, sticky = "w",
		                                                                         padx = (0, 8), pady = 6 )
		time_out_frame = ttk.Frame( outer )
		time_out_frame.grid( row = 6, column = 1, sticky = "w", pady = 6 )

		out_time_h = tk.StringVar( value = out_h_def )
		out_time_m = tk.StringVar( value = out_m_def )

		cb_out_h = ttk.Combobox( time_out_frame, textvariable = out_time_h, values = stunden, width = 5,
		                         state = "readonly" )
		cb_out_m = ttk.Combobox( time_out_frame, textvariable = out_time_m, values = minuten, width = 5,
		                         state = "readonly" )
		cb_out_h.grid( row = 0, column = 0, padx = (0, 8) )
		cb_out_m.grid( row = 0, column = 1 )

		def reset_form():
			var_projekt.set( "" )
			var_person.set( "" )
			in_time_h.set( "" )
			in_time_m.set( "" )
			out_time_h.set( "" )
			out_time_m.set( "" )
			in_cal.set_date( date.today() )
			out_cal.set_date( date.today() )
			win.focus_force()

		def Buchen():
			projekt_name = var_projekt.get()
			person_name = var_person.get()

			if projekt_name == "" or person_name == "" or in_time_h.get() == "" or in_time_m.get() == "" or out_time_h.get() == "" or out_time_m.get() == "":
				messagebox.showinfo( "Buchen nicht möglich!", "Buchen nicht möglich, fülle alle Felder aus!" )
				return

			in_complete = f"{in_cal.get_date()} {int( in_time_h.get() ):02d}:{int( in_time_m.get() ):02d}:00"
			out_complete = f"{out_cal.get_date()} {int( out_time_h.get() ):02d}:{int( out_time_m.get() ):02d}:00"

			in_date_str = in_cal.get_date().strftime( "%d.%m.%Y" )
			out_date_str = out_cal.get_date().strftime( "%d.%m.%Y" )
			in_time_str = f"{int( in_time_h.get() ):02d}:{int( in_time_m.get() ):02d}"
			out_time_str = f"{int( out_time_h.get() ):02d}:{int( out_time_m.get() ):02d}"

			answer = messagebox.askyesno(
				f"Wirklich buchen für {projekt_name}?",
				f"Projekt: {projekt_name}\n\n"
				f"Person: {person_name}\n"
				f"Von:\n"
				f"  {in_date_str}  um  {in_time_str}\n\n"
				f"Bis:\n"
				f"  {out_date_str}  um  {out_time_str}\n\n"
				f"Möchten Sie diese Buchung speichern?"
			)
			if not answer:
				return

			if buchung_id is None:
				sql = """
                      INSERT INTO buchungen (projekt_id, person_id, einstempelzeit, ausstempelzeit)
                      VALUES ((SELECT id FROM projekte WHERE name = ?),
                              (SELECT id FROM personen WHERE name = ?),
                              ?,
                              ?); \
				      """
				params = (projekt_name, person_name, in_complete, out_complete)
			else:
				sql = """
                      UPDATE buchungen
                      SET projekt_id     = (SELECT id FROM projekte WHERE name = ?),
                          person_id      = (SELECT id FROM personen WHERE name = ?),
                          einstempelzeit = ?,
                          ausstempelzeit = ?
                      WHERE id = ?; \
				      """
				params = (projekt_name, person_name, in_complete, out_complete, buchung_id)

			sql_commit2( sql, params )

			if buchung_id is None:
				reset_form()
			else:
				win.destroy()

		# Buttons
		btn_frame = ttk.Frame( outer )
		btn_frame.grid( row = 7, column = 0, columnspan = 2, sticky = "ew", pady = (14, 0) )
		btn_frame.columnconfigure( 0, weight = 1, uniform = "zbtn" )
		btn_frame.columnconfigure( 1, weight = 1, uniform = "zbtn" )

		button_text = "Änderungen speichern" if buchung_id else "Zeit buchen"
		ttk.Button( btn_frame, text = button_text, style = "Accent.TButton", command = Buchen ).grid(
			row = 0, column = 0, sticky = "ew", padx = (0, 6)
		)
		ttk.Button( btn_frame, text = "Zurück", command = win.destroy ).grid(
			row = 0, column = 1, sticky = "ew", padx = (6, 0)
		)

		outer.columnconfigure( 1, weight = 1 )
		return win


	def Einstempeln():
		def Buchen():
			projekt_name = var_projekt.get()
			person_name = var_person.get()

			if projekt_name == "" or person_name == "":
				messagebox.showinfo( "Einstempeln nicht möglich", "Bitte Projekt und Person auswählen." )
				return

			now = datetime.now().replace( microsecond = 0 )
			sql = """
                  INSERT INTO buchungen (projekt_id, person_id, einstempelzeit, ausstempelzeit)
                  VALUES ((SELECT id FROM projekte WHERE name = ?),
                          (SELECT id FROM personen WHERE name = ?),
                          ?,
                          ?); \
			      """
			params = (projekt_name, person_name, now, "9999-12-31 23:59:59")

			sql_commit2( sql, params )
			refresh_buchungen_liste()
			win.destroy()
			root.focus_force()

		win = tk.Toplevel()
		win.title( "Stempeluhr - Einstempeln" )
		win.geometry( "420x184" )
		win.resizable( False, False )
		win.iconbitmap( "src/sanduhr.ico" )
		win.configure( bg = "#0f1115" )

		outer = ttk.Frame( win, style = "Card.TFrame" )
		outer.pack( fill = "both", expand = True, padx = 12, pady = 12 )

		ttk.Label( outer, text = "Einstempeln", style = "CardTitle.TLabel" ).grid( row = 0, column = 0, columnspan = 2,
		                                                                           sticky = "w", pady = (0, 12) )

		projekte = [ row[ 0 ] for row in sql_select( "SELECT name FROM projekte;" ) ]
		personen = [ row[ 0 ] for row in sql_select( "SELECT name FROM personen;" ) ]

		ttk.Label( outer, text = "Projekt:", style = "CardTitle.TLabel" ).grid( row = 1, column = 0, sticky = "w",
		                                                                        padx = (0, 8), pady = 6 )
		var_projekt = tk.StringVar()
		cb_projekt = ttk.Combobox( outer, textvariable = var_projekt, values = projekte, state = "readonly" )
		cb_projekt.grid( row = 1, column = 1, sticky = "ew", pady = 6 )

		ttk.Label( outer, text = "Person:", style = "CardTitle.TLabel" ).grid( row = 2, column = 0, sticky = "w",
		                                                                       padx = (0, 8), pady = 6 )
		var_person = tk.StringVar()
		cb_person = ttk.Combobox( outer, textvariable = var_person, values = personen, state = "readonly" )
		cb_person.grid( row = 2, column = 1, sticky = "ew", pady = 6 )

		btn_frame = ttk.Frame( outer )
		btn_frame.grid( row = 3, column = 0, columnspan = 2, sticky = "ew", pady = (14, 0) )
		btn_frame.columnconfigure( 0, weight = 1, uniform = "ebtn" )
		btn_frame.columnconfigure( 1, weight = 1, uniform = "ebtn" )

		ttk.Button( btn_frame, text = "Einstempeln", style = "Accent.TButton", command = Buchen ).grid(
			row = 0, column = 0, sticky = "ew", padx = (0, 6)
		)
		ttk.Button( btn_frame, text = "Zurück", command = win.destroy ).grid(
			row = 0, column = 1, sticky = "ew", padx = (6, 0)
		)

		outer.columnconfigure( 1, weight = 1 )
		return win


	def Ausstempeln():
		def Buchen():
			selected_label = var_unbeendete.get()
			if selected_label not in label_to_row:
				messagebox.showinfo( "Ausstempeln", "Bitte wähle eine offene Buchung aus." )
				return

			id_, person, projekt, start, ende = label_to_row[ selected_label ]
			now = datetime.now().replace( microsecond = 0 )

			sql = "UPDATE buchungen SET ausstempelzeit = ? WHERE id = ?;"
			sql_commit2( sql, (now, id_) )

			refresh_buchungen_liste()
			win.destroy()
			root.focus_force()

		win = tk.Toplevel()
		win.title( "Stempeluhr - Ausstempeln" )
		win.geometry( "520x147" )
		win.resizable( False, False )
		win.iconbitmap( "src/sanduhr.ico" )
		win.configure( bg = "#0f1115" )

		outer = ttk.Frame( win, style = "Card.TFrame" )
		outer.pack( fill = "both", expand = True, padx = 12, pady = 12 )

		ttk.Label( outer, text = "Ausstempeln", style = "CardTitle.TLabel" ).grid( row = 0, column = 0, columnspan = 2,
		                                                                           sticky = "w", pady = (0, 12) )

		sql = """
              select buchungen.id, p.name, p2.name, einstempelzeit, ausstempelzeit
              from buchungen
                       left join personen p on buchungen.person_id = p.id
                       left join projekte p2 on buchungen.projekt_id = p2.id
              where ausstempelzeit = ?; \
		      """
		rows = sql_select2( sql, ("9999-12-31 23:59:59",) )

		options = [ ]
		label_to_row = { }

		for (id_, person, projekt, start, ende) in rows:
			start_str = format_dt( start )
			label = f"#{id_:<3} | {person} | {projekt or '-'} | Start: {start_str}"
			options.append( label )
			label_to_row[ label ] = (id_, person, projekt, start, ende)

		ttk.Label( outer, text = "Offene Buchung:", style = "CardTitle.TLabel" ).grid( row = 1, column = 0,
		                                                                               sticky = "w",
		                                                                               padx = (0, 8), pady = 6 )
		var_unbeendete = tk.StringVar()

		cb_offen = ttk.Combobox( outer, textvariable = var_unbeendete, values = options, state = "readonly" )
		cb_offen.grid( row = 1, column = 1, sticky = "ew", pady = 6 )

		if options:
			var_unbeendete.set( options[ 0 ] )
		else:
			var_unbeendete.set( "" )
			cb_offen.configure( state = "disabled" )

		btn_frame = ttk.Frame( outer )
		btn_frame.grid( row = 2, column = 0, columnspan = 2, sticky = "ew", pady = (14, 0) )
		btn_frame.columnconfigure( 0, weight = 1, uniform = "abtn" )
		btn_frame.columnconfigure( 1, weight = 1, uniform = "abtn" )

		btn_a = ttk.Button( btn_frame, text = "Ausstempeln", style = "Accent.TButton", command = Buchen )
		btn_a.grid( row = 0, column = 0, sticky = "ew", padx = (0, 6) )

		if not options:
			btn_a.configure( state = "disabled" )

		ttk.Button( btn_frame, text = "Zurück", command = win.destroy ).grid(
			row = 0, column = 1, sticky = "ew", padx = (6, 0)
		)

		outer.columnconfigure( 1, weight = 1 )
		return win


	if __name__ == "__main__":
		buchungen_liste = [ ]


	def open_einstempeln():
		win = Einstempeln()
		root.wait_window( win )
		refresh_buchungen_liste()


	def refresh_buchungen_liste():
		global buchungen_liste
		lbox.delete( 0, "end" )
		buchungen_liste = sql_select( """
                                      select buchungen.id, p.name, p2.name, einstempelzeit, ausstempelzeit
                                      from buchungen
                                               left join personen p on buchungen.person_id = p.id
                                               left join projekte p2 on buchungen.projekt_id = p2.id""" )

		for buchung in buchungen_liste:
			id_, person, projekt, start, ende = buchung

			start_str = format_dt( start )
			ende_str = format_dt( ende )
			if ende_str == '31.12.9999 23:59':
				ende_str = 'offen'

			text = (

				f"Person: {person:<10} | "
				f"Projekt: {projekt or '-':<8} | "
				f"{start_str} → {ende_str}"
			)

			lbox.insert( tk.END, text )
		return root


	def loeschen():
		auswahl = lbox.curselection()
		if auswahl != ():

			auswahl = auswahl[ 0 ]
			buchung = buchungen_liste[ auswahl ]
			buchung_id = buchung[ 0 ]

			answer = messagebox.askyesno( "Sie Löschen eine Buchung",
			                              "Wollen sie wirklich die Buchung löschen?" )
			projekt_anlegen.focus_set()
			if answer:
				sql_str = "DELETE FROM buchungen WHERE id =  ? ;"

				sql_commit2( sql_str, (buchung_id,) )
				refresh_buchungen_liste()
				root.focus_force()

		else:
			messagebox.showinfo( "Löschen nicht Möglich", "Bitte wähle eine Buchung aus" )


	def bearbeiten():
		auswahl = lbox.curselection()
		if auswahl != ():

			auswahl = auswahl[ 0 ]
			buchung = buchungen_liste[ auswahl ]
			buchung_id = buchung[ 0 ]
			win = Zeit_Nachtraeglich_erfassen( buchung_id )
			root.wait_window( win )
			win = refresh_buchungen_liste()
			root.wait_window( win )
			root.focus_force()

		else:
			messagebox.showinfo( "Bearbeiten nicht Möglich", "Bitte wähle eine Buchung aus" )


	init_db()
	root = tk.Tk()
	style = apply_ttk_dark_theme( root )

	root.title( "Stempeluhr" )

	root.geometry( "600x400" )
	root.resizable( False, False )

	root.iconbitmap( "src/sanduhr.ico" )

	top_frame = ttk.Frame( root, style = "Card.TFrame" )
	top_frame.pack( fill = "x", padx = 10, pady = 10 )

	list_frame = ttk.Frame( root, style = "Card.TFrame" )
	list_frame.pack( fill = "both", expand = True, padx = 10, pady = 5 )

	bottom_frame = ttk.Frame( root, style = "Card.TFrame" )
	bottom_frame.pack( fill = "x", padx = 10, pady = 10 )

	top_frame.columnconfigure( 0, weight = 1, uniform = "buttons" )
	top_frame.columnconfigure( 1, weight = 1, uniform = "buttons" )
	bottom_frame.columnconfigure( 0, weight = 1, uniform = "buttons2" )
	bottom_frame.columnconfigure( 1, weight = 1, uniform = "buttons2" )

	lbox = tk.Listbox(
		list_frame,
		height = 5,
		width = 80,
		bg = "#0b0d12",
		fg = "#e6e6e6",
		selectbackground = "#1d2330",
		selectforeground = "#e6e6e6",
		highlightthickness = 1,
		highlightbackground = "#2a2f3a",
		relief = "flat"
	)
	lbox.config( font = ("Consolas", 9) )
	lbox.pack( fill = "both", expand = True, padx = 8, pady = 8 )

	refresh_buchungen_liste()

	projekt_anlegen = ttk.Button( top_frame, text = "Projekt anlegen", command = Projekt_Anlegen )
	person_anlegen = ttk.Button( top_frame, text = "Person anlegen", command = Person_Anlegen )
	zeit_nachtraeglich_erfassen = ttk.Button( top_frame, text = "Zeit Nachträglich erfassen",
	                                          command = lambda: Zeit_Nachtraeglich_erfassen( "" ) )
	auswertung = ttk.Button( top_frame, text = "Auswertung", command = Auswertung )
	einstempeln = ttk.Button( top_frame, text = "Einstempeln", command = open_einstempeln )
	ausstempeln = ttk.Button( top_frame, text = "Ausstempeln", command = Ausstempeln )

	bearbeiten_button = ttk.Button( bottom_frame, text = "Ausgewählte Buchung Bearbeiten", command = bearbeiten )
	loeschen_button = ttk.Button( bottom_frame, text = "Ausgewählte Buchung Löschen", command = loeschen )
	aktualisieren_button = ttk.Button( bottom_frame, text = "Aktualisieren", command = refresh_buchungen_liste )

	projekt_anlegen.grid( row = 0, column = 0, padx = 5, pady = 5, sticky = "ew" )
	person_anlegen.grid( row = 0, column = 1, padx = 5, pady = 5, sticky = "ew" )
	zeit_nachtraeglich_erfassen.grid( row = 1, column = 0, padx = 5, pady = 5, sticky = "ew" )
	auswertung.grid( row = 1, column = 1, padx = 5, pady = 5, sticky = "ew" )
	einstempeln.grid( row = 2, column = 0, padx = 5, pady = 5, sticky = "ew" )
	ausstempeln.grid( row = 2, column = 1, padx = 5, pady = 5, sticky = "ew" )

	bearbeiten_button.grid( row = 0, column = 0, padx = 5, pady = 5, sticky = "ew" )
	loeschen_button.grid( row = 0, column = 1, padx = 5, pady = 5, sticky = "ew" )
	aktualisieren_button.grid( row = 0, column = 2, columnspan = 2, padx = 5, pady = 5, sticky = "ew" )

	refresh_buchungen_liste()
	root.mainloop()

	pass
except Exception as e:
	log_exception( e )
	raise
