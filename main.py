import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import date, datetime
import sqlite3


# ///TODO///
# mit ttk schön machen
# Datenbank für installation vorbereiten, init durch dieses script
# Restliche Funktionen ready machen
# exportieren und abfeuern


def format_dt( db_string ):
	if db_string is None:
		return "-"
	dt = datetime.strptime( db_string, "%Y-%m-%d %H:%M:%S" )
	return dt.strftime( "%d.%m.%Y %H:%M" )


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


def Projekt_Anlegen():
	def refresh_listbox():
		lbox.delete( 0, tk.END )
		projekte_liste2 = sql_select( "SELECT name FROM projekte;" )
		for projekte2 in projekte_liste2:
			lbox.insert( tk.END, projekte2 )

	def ANLEGEN( name2 ):
		if name_var != "":
			sql_str = "INSERT INTO projekte (name) VALUES ( '" + name2 + "');"
			sql_commit( sql_str )
			entrys_projekt_anlegen[ 0 ].delete( 0, tk.END )
			refresh_listbox()

	def LOESCHEN( projekte_liste3 ):
		auswahl = lbox.curselection()
		if auswahl != ():

			auswahl = auswahl[ 0 ]
			name_projekt = projekte_liste3[ auswahl ]
			name_projekt = name_projekt[ 0 ]
			### Frag nicht warum aber es funktioniert ###
			answer = messagebox.askyesno( "SIE LÖSCHEN PROJEKT " + name_projekt + "!",
			                              "Wollen sie wirklich das Projekt " + name_projekt + " wirklich löschen?" )
			projekt_anlegen.focus_set()
			if answer:
				sql_str = "DELETE FROM projekte WHERE name = '" + name_projekt + "';"
				sql_commit( sql_str )
				refresh_listbox()

		else:
			messagebox.showinfo( "Löschen nicht möglich", "Bitte wähle ein Projekt aus" )
			projekt_anlegen.focus_set()

	projekt_anlegen = tk.Toplevel()
	projekt_anlegen.title( "Stempeluhr - Projekt anlegen" )
	projekt_anlegen.geometry( "400x400" )
	projekt_anlegen.resizable( False, False )
	projekt_anlegen.configure( bg = "black" )
	projekt_anlegen.iconbitmap( "src/sanduhr.ico" )

	name_var = tk.StringVar()
	projekte_liste = sql_select( "SELECT name FROM projekte;" )

	lbox = tk.Listbox( projekt_anlegen )
	for projekte in projekte_liste:
		lbox.insert( tk.END, projekte )

	name = tk.Entry( projekt_anlegen, textvariable = name_var )
	name.focus_set()
	entrys_projekt_anlegen = [ name ]

	zurueck = tk.Button( projekt_anlegen, text = "Zurück", command = lambda: projekt_anlegen.destroy() )
	anlegen = tk.Button( projekt_anlegen, text = "Anlegen", command = lambda: ANLEGEN( name_var.get() ) )
	loeschen = tk.Button( projekt_anlegen, text = "Ausgewähltes Projekt Löschen",
	                      command = lambda: LOESCHEN( projekte_liste ) )
	buttons_projekt_anlegen = [ zurueck, anlegen, loeschen ]

	for button in buttons_projekt_anlegen:
		button.pack( pady = 10 )
	for entry in entrys_projekt_anlegen:
		entry.pack( pady = 10 )
	lbox.pack( pady = 10 )


def Zeit_Nachtraeglich_erfassen( voreinstellung ):
	buchung_id = voreinstellung if voreinstellung != "" else None

	def Buchen( projekt_name, person_name ):
		if projekt_name == "" or person_name == "" or in_time_h.get() == "" or in_time_m.get() == "" or out_time_h.get() == "" or out_time_m.get() == "":
			messagebox.showinfo( "Buchen nicht möglich!", "Buchen nicht möglich, fülle alle Felder aus!" )
		else:
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

			projekt_anlegen.focus_set()
			if answer:

				if buchung_id is None:
					# FALL 1: neue Buchung
					sql = """
                          INSERT INTO buchungen (projekt_id, person_id, einstempelzeit, ausstempelzeit)
                          VALUES ((SELECT id FROM projekte WHERE name = ?),
                                  (SELECT id FROM personen WHERE name = ?),
                                  ?,
                                  ?); \
					      """
					params = (projekt_name, person_name, in_complete, out_complete)
				else:
					# FALL 2: vorhandene Buchung ändern
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
					reset_form()  # NEU: Eingaben leeren
				else:
					zeit_nachtraeglich_erfassen.destroy()  # EDIT: Fenster zu

	def reset_form():
		# Dropdowns
		var_projekt_name.set( "" )
		var_person_name.set( "" )

		in_time_h.set( "" )
		in_time_m.set( "" )
		out_time_h.set( "" )
		out_time_m.set( "" )

		# Kalender auf heute setzen
		in_cal.set_date( date.today() )
		out_cal.set_date( date.today() )
		zeit_nachtraeglich_erfassen.focus_set()

	zeit_nachtraeglich_erfassen = tk.Toplevel()
	zeit_nachtraeglich_erfassen.title( "Stempeluhr - Zeit nachträglich erfassen" )
	zeit_nachtraeglich_erfassen.geometry( "400x600" )
	zeit_nachtraeglich_erfassen.resizable( False, False )
	zeit_nachtraeglich_erfassen.configure( bg = "black" )
	zeit_nachtraeglich_erfassen.iconbitmap( "src/sanduhr.ico" )

	if voreinstellung != "":
		zeit_nachtraeglich_erfassen.title( "Stempeluhr - Buchung ändern" )
		id_voreinstellung = voreinstellung
		sql = """
              select buchungen.id, p.name, p2.name, einstempelzeit, ausstempelzeit
              from buchungen
                       left join personen p on buchungen.person_id = p.id
                       left join projekte p2 on buchungen.projekt_id = p2.id
              where buchungen.id = ?; \
		      """
		rows = sql_select2( sql, (id_voreinstellung,) )

		if not rows:
			messagebox.showerror( "Fehler", "Buchung existiert nicht mehr" )
			return
		array = rows[ 0 ]  # erstes tupel
		print( array )

		name_projekt_voreinstellung = array[ 2 ]
		name_person_voreinstellung = array[ 1 ]

		dt = datetime.strptime( array[ 3 ], "%Y-%m-%d %H:%M:%S" )
		in_date_voreinstellung = dt.date()
		in_time_h_voreinstellung = dt.strftime( "%H" )
		in_time_m_voreinstellung = dt.strftime( "%M" )

		et = datetime.strptime( array[ 4 ], "%Y-%m-%d %H:%M:%S" )
		out_date_voreinstellung = et.date()
		out_time_h_voreinstellung = et.strftime( "%H" )
		out_time_m_voreinstellung = et.strftime( "%M" )


	else:
		name_projekt_voreinstellung = ""
		name_person_voreinstellung = ""
		in_date_voreinstellung = ""
		in_time_h_voreinstellung = ""
		in_time_m_voreinstellung = ""
		out_date_voreinstellung = ""
		out_time_h_voreinstellung = ""
		out_time_m_voreinstellung = ""

	label_projekt_name = tk.Label( zeit_nachtraeglich_erfassen, text = "Projekt Name: " )
	label_projekt_name.pack( pady = 10 )
	var_projekt_name = tk.StringVar( value = name_projekt_voreinstellung )
	values_projekt_name = [ row[ 0 ] for row in sql_select( "SELECT name FROM projekte;" ) ]
	entry_projekt_name = tk.OptionMenu( zeit_nachtraeglich_erfassen, var_projekt_name, *values_projekt_name )
	entry_projekt_name.pack( pady = 10 )

	label_person_name = tk.Label( zeit_nachtraeglich_erfassen, text = "Person Name: " )
	label_person_name.pack( pady = 10 )
	var_person_name = tk.StringVar( value = name_person_voreinstellung )
	values_person_name = [ row[ 0 ] for row in sql_select( "SELECT name FROM personen;" ) ]
	entry_person_name = tk.OptionMenu( zeit_nachtraeglich_erfassen, var_person_name, *values_person_name )
	entry_person_name.pack( pady = 10 )

	in_cal = DateEntry( zeit_nachtraeglich_erfassen, width = 14, background = "black", foreground = "white",
	                    date_pattern = 'dd.mm.yyyy' )
	in_cal.delete( 0, "end" )
	if voreinstellung != "":
		in_cal.set_date( in_date_voreinstellung )
	in_cal.pack( pady = 10 )

	Stunden = [ "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16",
	            "17", "18", "19", "20", "21", "22", "23" ]
	in_time_h = tk.StringVar( value = in_time_h_voreinstellung )
	menu_in_time_h = tk.OptionMenu( zeit_nachtraeglich_erfassen, in_time_h, *Stunden )

	Minuten = [ f"{m:02d}" for m in range( 0, 60, 5 ) ]
	in_time_m = tk.StringVar( value = in_time_m_voreinstellung )
	menu_in_time_m = tk.OptionMenu( zeit_nachtraeglich_erfassen, in_time_m, *Minuten )

	menu_in_time_h.pack( pady = 10 )
	menu_in_time_m.pack( pady = 10 )

	out_cal = DateEntry( zeit_nachtraeglich_erfassen, width = 12, background = "darkblue", foreground = "white",
	                     date_pattern = 'dd.mm.yyyy', )
	out_cal.delete( 0, "end" )
	if voreinstellung != "":
		out_cal.set_date( out_date_voreinstellung )
	out_cal.pack( pady = 10 )
	out_cal.pack( pady = 10 )
	out_time_h = tk.StringVar( value = out_time_h_voreinstellung )
	menu_out_time_h = tk.OptionMenu( zeit_nachtraeglich_erfassen, out_time_h, *Stunden )

	out_time_m = tk.StringVar( value = out_time_m_voreinstellung )
	menu_out_time_m = tk.OptionMenu( zeit_nachtraeglich_erfassen, out_time_m, *Minuten )

	menu_out_time_h.pack( pady = 10 )
	menu_out_time_m.pack( pady = 10 )

	button_text = "Änderungen speichern" if buchung_id else "Zeit buchen"

	buchen = tk.Button( zeit_nachtraeglich_erfassen, text = button_text,
	                    command = lambda: Buchen( var_projekt_name.get(), var_person_name.get() ) )

	zurueck = tk.Button( zeit_nachtraeglich_erfassen, text = "Zurück",
	                     command = lambda: zeit_nachtraeglich_erfassen.destroy() )

	buchen.pack( pady = 10 )
	zurueck.pack( pady = 10 )

	return zeit_nachtraeglich_erfassen


def Einstempeln():
	def Buchen( projekt_name, person_name ):

		now = datetime.now().replace(microsecond=0)
		sql = """
              INSERT INTO buchungen (projekt_id, person_id, einstempelzeit, ausstempelzeit)
              VALUES ((SELECT id FROM projekte WHERE name = ?),
                      (SELECT id FROM personen WHERE name = ?),
                      ?, 
                      ? 
                      ); \
		      """
		params = (projekt_name, person_name, now, '9999-12-31 23:59:59' )

		sql_commit2( sql, params )
		refresh_buchungen_liste()  # <-- neu laden und anzeigen
		einstempeln.destroy()
		root.focus_force()


	einstempeln = tk.Toplevel()
	einstempeln.title( "Stempeluhr - Einstempeln" )
	einstempeln.geometry( "400x400" )
	einstempeln.resizable( False, False )
	einstempeln.configure( bg = "black" )
	einstempeln.iconbitmap( "src/sanduhr.ico" )



	label_projekt_name = tk.Label( einstempeln, text = "Projekt Name: " )
	label_projekt_name.pack( pady = 10 )
	var_projekt_name = tk.StringVar()
	values_projekt_name = [ row[ 0 ] for row in sql_select( "SELECT name FROM projekte;" ) ]
	entry_projekt_name = tk.OptionMenu( einstempeln, var_projekt_name, *values_projekt_name )
	entry_projekt_name.pack( pady = 10 )

	label_person_name = tk.Label( einstempeln, text = "Person Name: " )
	label_person_name.pack( pady = 10 )
	var_person_name = tk.StringVar( )
	values_person_name = [ row[ 0 ] for row in sql_select( "SELECT name FROM personen;" ) ]
	entry_person_name = tk.OptionMenu( einstempeln, var_person_name, *values_person_name )
	entry_person_name.pack( pady = 10 )

	buchen = tk.Button( einstempeln, text = "Einstempeln",
	                    command = lambda: Buchen( var_projekt_name.get(), var_person_name.get() ) )

	zurueck = tk.Button( einstempeln, text = "Zurück", command = lambda: einstempeln.destroy() )

	buchen.pack( pady = 10 )
	zurueck.pack( pady = 10 )

	return einstempeln

def Ausstempeln():
	def Buchen():
		selected_label = var_unbeendete_buchungen.get()
		if selected_label not in label_to_row:
			messagebox.showinfo( "Ausstempeln", "Bitte wähle eine offene Buchung aus." )
			return

		id_, person, projekt, start, ende = label_to_row[ selected_label ]

		now = datetime.now().replace( microsecond = 0 )

		sql = """
              UPDATE buchungen
              SET ausstempelzeit = ?
              WHERE id = ?; \
		      """
		sql_commit2( sql, (now, id_) )

		refresh_buchungen_liste()
		ausstempeln.destroy()
		root.focus_force()



	ausstempeln = tk.Toplevel()
	ausstempeln.title( "Stempeluhr - Einstempeln" )
	ausstempeln.geometry( "400x400" )
	ausstempeln.resizable( False, False )
	ausstempeln.configure( bg = "black" )
	ausstempeln.iconbitmap( "src/sanduhr.ico" )

	label_unbeendete_buchungen = tk.Label( ausstempeln, text = "Unbeendete Buchungen: " )
	label_unbeendete_buchungen.pack( pady = 10 )




	sql = """
              select buchungen.id, p.name, p2.name, einstempelzeit, ausstempelzeit
              from buchungen
                       left join personen p on buchungen.person_id = p.id
                       left join projekte p2 on buchungen.projekt_id = p2.id
              where ausstempelzeit = ?; \
		      """

	rows = sql_select2( sql, ('9999-12-31 23:59:59',) )
	# rows: [(id, person, projekt, start, ende), ...]
	options = [ ]
	label_to_row = { }

	for (id_, person, projekt, start, ende) in rows:
		start_str = format_dt( start )  # z.B. "03.02.2026 18:43"
		label = f"#{id_:<3} | {person} | {projekt or '-'} | Start: {start_str}"
		options.append( label )
		label_to_row[ label ] = (id_, person, projekt, start, ende)

	var_unbeendete_buchungen = tk.StringVar()

	if options:
		var_unbeendete_buchungen.set( options[ 0 ] )  # ersten Eintrag vorauswählen
	else:
		var_unbeendete_buchungen.set( "Keine offenen Buchungen" )



	entry_unbeendete_buchungen = tk.OptionMenu( ausstempeln, var_unbeendete_buchungen, *options )
	entry_unbeendete_buchungen.pack( pady = 10 )


	buchen = tk.Button( ausstempeln, text = "Ausstempeln",
	                    command = lambda: Buchen())

	zurueck = tk.Button( ausstempeln, text = "Zurück", command = lambda: ausstempeln.destroy() )

	buchen.pack( pady = 10 )
	zurueck.pack( pady = 10 )

	return ausstempeln

if __name__ == "__main__":
	buchungen_liste = [ ]

def open_einstempeln():
	win = Einstempeln()
	root.wait_window(win)
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
		if ende_str ==  '31.12.9999 23:59':
			ende_str = 'offen'



		text = (

			f"Person: {person:<10} | "
			f"Projekt: {projekt or '-':<8} | "
			f"{start_str} → {ende_str}"
		)

		lbox.insert( tk.END, text )


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

			sql_commit2( sql_str , (buchung_id,))
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
		refresh_buchungen_liste()
		root.focus_force()

	else:
		messagebox.showinfo( "Bearbeiten nicht Möglich", "Bitte wähle eine Buchung aus" )


root = tk.Tk()
root.title( "Stempeluhr" )

root.geometry( "600x400" )
root.resizable( False, False )
root.configure( bg = "black" )
root.iconbitmap( "src/sanduhr.ico" )

lbox = tk.Listbox( root, height = 5, width = 80 )
lbox.config( font = ("Courier New", 8) )

refresh_buchungen_liste()

projekt_anlegen = tk.Button( root, text = "Projekt anlegen", command = Projekt_Anlegen )
zeit_nachtraeglich_erfassen = tk.Button( root, text = "Zeit Nachträglich erfassen",
                                         command = lambda: Zeit_Nachtraeglich_erfassen( "" ) )
einstempeln = tk.Button( root, text = "Einstempeln", command = open_einstempeln)
ausstempeln = tk.Button( root, text = "Ausstempeln", command = Ausstempeln )
buttons_main = [ projekt_anlegen, zeit_nachtraeglich_erfassen, einstempeln, ausstempeln ]

bearbeiten_button = tk.Button( root, text = "Ausgewählte Buchung Bearbeiten", command = bearbeiten )

loeschen_button = tk.Button( root, text = "Ausgewählte Buchung Löschen", command = loeschen )

refresh_buchungen_liste()

for button in buttons_main:
	button.pack( pady = 10 )

lbox.pack( pady = 10 )
bearbeiten_button.pack( pady = 10 )
loeschen_button.pack( pady = 10 )

root.mainloop()
