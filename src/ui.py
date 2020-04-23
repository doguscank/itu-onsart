import database as db
import graph
from PyQt5.QtWidgets import QApplication, QLabel, QGridLayout, QAction, QWidget, QPushButton, QComboBox, QLineEdit, QMenuBar, QCheckBox, QDialog
from PyQt5.QtCore import pyqtSlot, Qt

class App(QWidget):
	def __init__(self):
		super().__init__()
		self.title = "On Sart Grafigi"
		self.db = db.Database()

		#Keep selected options
		self.selected_faculty = None
		self.selected_program = None
		self.selected_term = None
		self.selected_dmajor_faculty = None
		self.selected_dmajor_program = None
		self.selected_dmajor_term = None

		self.default_selection = 'Seciniz'

		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(200, 200, 200, 200)

		self.layout = QGridLayout()
		self.init_components()
		self.init_dmajor_components()
		self.setLayout(self.layout)
		self.show()

	def init_components(self):
		self.cbox_faculty = QComboBox(self)
		self.cbox_program = QComboBox(self)
		self.cbox_term = QComboBox(self)

		self.cbox_faculty_label = QLabel('Fakulte:')
		self.cbox_program_label = QLabel('Program:')
		self.cbox_term_label = QLabel('Donem:')

		#Add default option
		self.cbox_faculty.addItem(self.default_selection)
		self.cbox_program.addItem(self.default_selection)
		self.cbox_term.addItem(self.default_selection)

		self.btn_get = QPushButton('Programi Cek', self)
		self.btn_get.clicked.connect(lambda _: self.btn_get_pressed())

		#Update faculties from ITU system and show names in checkbox
		self.db.update_faculties()

		for faculty in self.db.faculties_list:
			self.cbox_faculty.addItem(faculty.name)

		self.cbox_faculty.activated[str].connect(lambda x: self.faculty_changed(x))
		self.cbox_program.activated[str].connect(lambda x: self.program_changed(x))
		self.cbox_term.activated[str].connect(lambda x: self.term_changed(x))

		self.dmajor_checkbox = QCheckBox('CAP programi dahil etmek istiyorum.', self)
		self.dmajor_checkbox.stateChanged.connect(lambda _: self.dmajor_check())

		self.layout.addWidget(self.cbox_faculty_label, 0, 0, 1, 5)
		self.layout.addWidget(self.cbox_faculty, 1, 0, 1, 5)
		self.layout.addWidget(self.cbox_program_label, 2, 0, 1, 5)
		self.layout.addWidget(self.cbox_program, 3, 0, 1, 5)
		self.layout.addWidget(self.cbox_term_label, 4, 0, 1, 5)
		self.layout.addWidget(self.cbox_term, 5, 0, 1, 5)
		self.layout.addWidget(self.dmajor_checkbox, 6, 0, 1, 5)
		self.layout.addWidget(self.btn_get, 15, 1, 1, 3)

	def init_dmajor_components(self):
		self.cbox_dmajor_faculty = QComboBox(self)
		self.cbox_dmajor_program = QComboBox(self)
		self.cbox_dmajor_term = QComboBox(self)

		self.cbox_dmajor_faculty.addItem(self.default_selection)
		self.cbox_dmajor_program.addItem(self.default_selection)
		self.cbox_dmajor_term.addItem(self.default_selection)

		self.db.update_dmajor_faculties()

		for faculty in self.db.dmajor_faculties:
			self.cbox_dmajor_faculty.addItem(faculty.name)

		self.cbox_dmajor_faculty.activated[str].connect(lambda x: self.dmajor_faculty_changed(x))
		self.cbox_dmajor_program.activated[str].connect(lambda x: self.dmajor_program_changed(x))
		self.cbox_dmajor_term.activated[str].connect(lambda x: self.dmajor_term_changed(x))

		self.cbox_dmajor_label = QLabel('CAP icin uygun secenekleri secin')
		self.cbox_dmajor_faculty_label = QLabel('Fakulte:')
		self.cbox_dmajor_program_label = QLabel('Program:')
		self.cbox_dmajor_term_label = QLabel('Donem:')

		self.layout.addWidget(self.cbox_dmajor_label, 7, 0, 1, 5)
		self.layout.addWidget(self.cbox_dmajor_faculty_label, 8, 0, 1, 5)
		self.layout.addWidget(self.cbox_dmajor_faculty, 9, 0, 1, 5)
		self.layout.addWidget(self.cbox_dmajor_program_label, 10, 0, 1, 5)
		self.layout.addWidget(self.cbox_dmajor_program, 11, 0, 1, 5)
		self.layout.addWidget(self.cbox_dmajor_term_label, 12, 0, 1, 5)
		self.layout.addWidget(self.cbox_dmajor_term, 13, 0, 1, 5)

		self.toggle_dmajor_components(False)

	def toggle_dmajor_components(self, toggle):
		widgets = [self.cbox_dmajor_label, self.cbox_dmajor_faculty_label, self.cbox_dmajor_program_label, self.cbox_dmajor_term_label, self.cbox_dmajor_faculty, self.cbox_dmajor_program, self.cbox_dmajor_term]
		for widget in widgets:
			widget.setEnabled(toggle)

		if not toggle:
			self.selected_dmajor_faculty = None
			self.selected_dmajor_program = None
			self.selected_dmajor_term = None

	def clear_options(self, cbox):
		cbox.clear() #Clear options of programs
		cbox.addItem(self.default_selection)

	def faculty_changed(self, faculty_name):
		if faculty_name != self.default_selection:
			self.clear_options(self.cbox_program) #Clear options
			for f in self.db.faculties_list:
				if f.name == faculty_name:
					self.selected_faculty = f
					self.db.update_programs(f)
					self.update_program_list(f)
					break

	def update_program_list(self, faculty):
		for p in faculty.programs:
			self.cbox_program.addItem(p.name)

	def program_changed(self, program_name):
		if program_name != self.default_selection:
			self.clear_options(self.cbox_term) #Clear options
			for p in self.selected_faculty.programs:
				if p.name == program_name:
					self.selected_program = p
					self.db.update_terms(p)
					self.update_term_list(p)
					break

	def update_term_list(self, program):
		for t in program.terms:
			self.cbox_term.addItem(t.name)

	def term_changed(self, term_name):
		if term_name != self.default_selection:
			for t in self.selected_program.terms:
				if t.name == term_name:
					self.selected_term = t
					break

	def dmajor_faculty_changed(self, faculty_name):
		if faculty_name != self.default_selection:
			self.clear_options(self.cbox_dmajor_program)
			for f in self.db.dmajor_faculties:
				if f.name == faculty_name:
					self.selected_dmajor_faculty = f
					self.db.update_dmajor_programs(f)
					self.update_dmajor_program_list(f)
					break

	def update_dmajor_program_list(self, faculty):
		for p in faculty.programs:
			self.cbox_dmajor_program.addItem(p.name)

	def dmajor_program_changed(self, program_name):
		if program_name != self.default_selection:
			self.clear_options(self.cbox_dmajor_term) #Clear options
			for p in self.selected_dmajor_faculty.programs:
				if p.name == program_name:
					self.selected_dmajor_program = p
					self.db.update_dmajor_terms(p)
					self.update_dmajor_term_list(p)
					break

	def update_dmajor_term_list(self, program):
		if program.has_terms:			
			for t in program.terms:
				self.cbox_dmajor_term.addItem(t.name)
				print(t.url)
		else:
			self.cbox_dmajor_term.addItem(program.name)

	def dmajor_term_changed(self, term_name):
		if term_name != self.default_selection:
			for t in self.selected_dmajor_program.terms:
				if t.name == term_name:
					self.selected_dmajor_term = t
					break

	@pyqtSlot()
	def btn_get_pressed(self):
		if (self.selected_faculty is not None) and (self.selected_program is not None) and (self.selected_term is not None):
			self.db.update_courses(self.selected_term)
			self.db.update_dmajor_courses(self.selected_dmajor_term)

			graph.draw_graph(self.selected_term, self.selected_dmajor_term)

	@pyqtSlot()
	def dmajor_check(self):
		if self.dmajor_checkbox.isChecked():
			self.toggle_dmajor_components(True)
		else:
			self.toggle_dmajor_components(False)
