import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import sqlite3
import os

def sql_commit(sql):
	verbindung = sqlite3.connect( "datenbank/Zeiterfassung.db" )
	zeiger = verbindung.cursor()
	zeiger.execute( sql )
	verbindung.commit()
	verbindung.close()

def sql_select(sql):
	verbindung = sqlite3.connect( "datenbank/Zeiterfassung.db" )
	zeiger = verbindung.cursor()
	zeiger.execute( sql )
	ergebnis = zeiger.fetchall()
	return ergebnis

def Projekt_Anlegen():
	def refresh_listbox():
		lbox.delete(0, tk.END)
		projekte_liste2 = sql_select("SELECT name FROM projekte;")
		for projekte2 in projekte_liste2:
			lbox.insert(tk.END, projekte2)

	def ANLEGEN(name2):
		if name_var is not "":
			sql_str = "INSERT INTO projekte (name) VALUES ( '" + name2 + "');"
			sql_commit(sql_str)
			entrys_projekt_anlegen[0].delete(0, tk.END)
			refresh_listbox()

	def LOESCHEN(projekte_liste3):
		auswahl = lbox.curselection()
		if auswahl != ():

			auswahl = auswahl[ 0 ]
			name_projekt = projekte_liste3[ auswahl ]
			name_projekt = name_projekt[ 0 ]
			### Frag nicht warum aber es funktioniert ###
			answer = messagebox.askyesno("SIE LÖSCHEN PROJEKT " + name_projekt + "!", "Wollen sie wirklich das Projekt " + name_projekt + " wirklich löschen?")
			projekt_anlegen.focus_set()
			if answer:
				sql_str = "DELETE FROM projekte WHERE name = '" + name_projekt + "';"
				sql_commit(sql_str)
				refresh_listbox()

		else:
			messagebox.showinfo("Löschen nicht möglich", "Bitte wähle ein Projekt aus")
			projekt_anlegen.focus_set()

	projekt_anlegen = tk.Toplevel()
	projekt_anlegen.title( "Stempeluhr - Projekt anlegen" )
	projekt_anlegen.geometry( "400x400" )
	projekt_anlegen.resizable( False, False )
	projekt_anlegen.configure( bg = "black" )
	projekt_anlegen.iconbitmap( "src/sanduhr.ico" )

	name_var = tk.StringVar()
	projekte_liste = sql_select("SELECT name FROM projekte;")




	lbox = tk.Listbox(projekt_anlegen)
	for projekte in projekte_liste:
		lbox.insert(tk.END, projekte)


	name = tk.Entry(projekt_anlegen, textvariable = name_var)
	name.focus_set()
	entrys_projekt_anlegen = [name]

	zurueck = tk.Button( projekt_anlegen, text = "Zurück", command = lambda: projekt_anlegen.destroy() )
	anlegen = tk.Button( projekt_anlegen, text = "Anlegen", command = lambda: ANLEGEN(name_var.get()) )
	loeschen = tk.Button(projekt_anlegen, text = "Ausgewähltes Projekt Löschen", command = lambda: LOESCHEN(projekte_liste))
	buttons_projekt_anlegen = [ zurueck, anlegen, loeschen]

	for button in buttons_projekt_anlegen:
		button.pack(pady=10)
	for entry in entrys_projekt_anlegen:
		entry.pack(pady=10)
	lbox.pack( pady = 10 )

def Zeit_Nachtraeglich_erfassen():
	zeit_nachtraeglich_erfassen = tk.Toplevel()
	zeit_nachtraeglich_erfassen.title( "Stempeluhr - Zeit nachträglich erfassen" )
	zeit_nachtraeglich_erfassen.geometry( "400x400" )
	zeit_nachtraeglich_erfassen.resizable( False, False )
	zeit_nachtraeglich_erfassen.configure( bg = "black" )
	zeit_nachtraeglich_erfassen.iconbitmap( "src/sanduhr.ico" )

	zurueck = tk.Button( zeit_nachtraeglich_erfassen, text = "Zurück", command = lambda: zeit_nachtraeglich_erfassen.destroy() )

	buttons_zeit_nachtraeglich_erfassen = [ zurueck ]
	for button in buttons_zeit_nachtraeglich_erfassen:
		button.pack( pady = 10 )

def Einstempeln():
	einstempeln = tk.Toplevel()
	einstempeln.title( "Stempeluhr - Einstempeln" )
	einstempeln.geometry( "400x400" )
	einstempeln.resizable( False, False )
	einstempeln.configure( bg = "black" )
	einstempeln.iconbitmap( "src/sanduhr.ico" )

	zurueck = tk.Button( einstempeln, text = "Zurück", command = lambda: einstempeln.destroy() )

	buttons_einstempeln = [ zurueck ]
	for button in buttons_einstempeln:
		button.pack( pady = 10 )

def Ausstempeln():
	ausstempeln = tk.Toplevel()
	ausstempeln.title( "Stempeluhr - Ausstempeln" )
	ausstempeln.geometry( "400x400" )
	ausstempeln.resizable( False, False )
	ausstempeln.configure( bg = "black" )
	ausstempeln.iconbitmap( "src/sanduhr.ico" )

	zurueck = tk.Button( ausstempeln, text = "Zurück", command = lambda: ausstempeln.destroy() )

	buttons_ausstempeln = [ zurueck ]
	for button in buttons_ausstempeln:
		button.pack( pady = 10 )



if __name__ == "__main__":
	root = tk.Tk()
	root.title("Stempeluhr")
	root.geometry("400x400")
	root.resizable(False, False)
	root.configure(bg="black")
	root.iconbitmap("src/sanduhr.ico")



	projekt_anlegen = tk.Button(root, text="Projekt anlegen", command = Projekt_Anlegen)
	zeit_nachtraeglich_erfassen = tk.Button(root, text="Zeit Nachträglich erfassen", command = Zeit_Nachtraeglich_erfassen)
	einstempeln = tk.Button(root, text="Einstempeln", command = Einstempeln)
	ausstempeln = tk.Button(root, text="Ausstempeln", command = Ausstempeln)
	buttons_main = [projekt_anlegen, zeit_nachtraeglich_erfassen, einstempeln, ausstempeln]



	for button in buttons_main:
		button.pack(pady=10)



	root.mainloop()


