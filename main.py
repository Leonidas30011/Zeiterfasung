import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
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
		if name_var != "":
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
	def buchen(projekt_name, person_name, in_zeit_h,in_date, in_zeit_m, out_date, out_zeit_h, out_zeit_m):
		in_zeit = in_zeit_h + ":" + in_zeit_m
		out_zeit = out_zeit_h + ":" + out_zeit_m

		sql_str = "INSERT INTO buchungen (projekt_id, person_id, einstempelzeit, ausstempelzeit) VALUES ((select id from projekte where name = '" + projekt_name + "'), (SELECT id from personen where name = '" + person_name + "'),'2023-01-01 12:00:00','2023-01-02 12:00:00');"

		sql_commit(sql_str)

		pass

	zeit_nachtraeglich_erfassen = tk.Toplevel()
	zeit_nachtraeglich_erfassen.title( "Stempeluhr - Zeit nachträglich erfassen" )
	zeit_nachtraeglich_erfassen.geometry( "400x600" )
	zeit_nachtraeglich_erfassen.resizable( False, False )
	zeit_nachtraeglich_erfassen.configure( bg = "black" )
	zeit_nachtraeglich_erfassen.iconbitmap( "src/sanduhr.ico" )

	label_projekt_name = tk.Label(zeit_nachtraeglich_erfassen, text = "Projekt Name: ").pack( pady = 10 )
	var_projekt_name = tk.StringVar()
	entry_projekt_name = tk.OptionMenu( zeit_nachtraeglich_erfassen, var_projekt_name, "",*sql_select( "SELECT name FROM projekte;" ) ).pack( pady = 10 )

	label_person_name = tk.Label(zeit_nachtraeglich_erfassen, text = "Person Name: ").pack( pady = 10 )
	var_person_name = tk.StringVar()
	entry_projekt_name = tk.OptionMenu( zeit_nachtraeglich_erfassen, var_projekt_name, "",*sql_select( "SELECT name FROM personen;" )).pack( pady = 10 )

	cal = DateEntry( zeit_nachtraeglich_erfassen, width = 10, background = "black", foreground = "white" ).pack( pady = 10 )

	Stunden = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
	in_time_h = tk.Listbox( zeit_nachtraeglich_erfassen)
	in_time_h.insert( tk.END, *Stunden )
	Minuten = [0,5,10,15,20,25,30,35,40,45,50,55]
	in_time_m = tk.Listbox( zeit_nachtraeglich_erfassen)
	in_time_m.insert( tk.END, *Minuten )

	label_in_zeit_h = tk.Label(zeit_nachtraeglich_erfassen, text = "Stunden: ").pack( pady = 10 )
	in_zeit_h = tk.StringVar()
	in_zeit_m = tk.StringVar()
	entry_in_zeit_h = tk.Spinbox(zeit_nachtraeglich_erfassen, from_ =  0, to = 23, increment=1, textvariable = in_zeit_h).pack( pady = 10 )
	label_in_zeit_m = tk.Label( zeit_nachtraeglich_erfassen, text = "Minuten: " ).pack( pady = 10 )
	entry_in_zeit_m = tk.Spinbox( zeit_nachtraeglich_erfassen, from_ = 0, to = 60, increment = 1, textvariable = in_zeit_m).pack( pady = 10 )

	label_out_zeit_h = tk.Label( zeit_nachtraeglich_erfassen, text = "Stunden: " ).pack( pady = 10 )
	out_zeit_h = tk.StringVar()
	out_zeit_m = tk.StringVar()
	entry_out_zeit_h = tk.Spinbox( zeit_nachtraeglich_erfassen, from_ = 0, to = 23, increment = 1, textvariable = out_zeit_h ).pack( pady = 10 )
	label_out_zeit_m = tk.Label( zeit_nachtraeglich_erfassen, text = "Minuten: " ).pack( pady = 10 )
	entry_out_zeit_m = tk.Spinbox( zeit_nachtraeglich_erfassen, from_ = 0, to = 60, increment = 1, textvariable = out_zeit_m ).pack( pady = 10 )

	buchen = tk.Button(zeit_nachtraeglich_erfassen, text= "Zeit Buchen", command= lambda:buchen(var_projekt_name.get(), var_person_name.get(), in_zeit_h.get(), in_zeit_m.get(), out_zeit_h.get(), out_zeit_m.get()))

	zurueck = tk.Button( zeit_nachtraeglich_erfassen, text = "Zurück", command = lambda: zeit_nachtraeglich_erfassen.destroy() )

	buttons_zeit_nachtraeglich_erfassen = [ buchen, zurueck ]
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


