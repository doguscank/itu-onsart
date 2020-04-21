from bs4 import BeautifulSoup
import urllib3
import os.path

class CourseType:
	NORMAL = 'NORMAL'
	ITB = 'ITB'
	MT = 'MT'
	TM = 'TM'
	TB = 'TB'
	SNT = 'SNT'

def get_type(course_type):
	types = [CourseType.NORMAL, CourseType.ITB, CourseType.MT, CourseType.TM, CourseType.TB, CourseType.SNT]
	for i in range(len(types)):
		if types[i] == course_type:
			return types[i]

	return 'NORMAL'

def fix_tr_chars(to_fix):
	table = to_fix.maketrans("İıÜüĞğÇçŞşÖö", "IiUuGgCcSsOo")
	fixed = to_fix.translate(table)
	return fixed

class Faculty:
	def __init__(self, code, name, programs = None):
		self.code = code
		self.name = name
		self.programs = programs #List

class Program:
	def __init__(self, code, name, terms = None):
		self.code = code
		self.name = name
		self.terms = terms

class Term:
	def __init__(self, name, program_code, url, courses):
		self.name = name
		self.program_code = program_code
		self.url = url
		self.courses = courses
		self.course_names = list()

class Course:
	def __init__(self, course_code, course_no, req = None, compulsary = True, course_type = CourseType.NORMAL):
		self.course_code = course_code
		self.course_no = course_no
		self.req = req #Prerequisites
		self.compulsary = compulsary
		self.course_type = course_type
		self.name = "{} {}".format(self.course_code, self.course_no)

class Database:
	def __init__(self):
		self.faculties_list = list()

		self.database_url = "http://www.sis.itu.edu.tr/tr/dersplan/index.php"
		self.program_url = "http://www.sis.itu.edu.tr/tr/dersplan/plan/"
		self.manager = urllib3.PoolManager(1) #Create pool manager to get data from URLs

	#Updates faculty programs
	#Does not update courses
	def update_faculties(self):
		html = self.manager.urlopen('GET', self.database_url) #Get HTML of given database URL
		soup = BeautifulSoup(html.data, 'lxml') #Export HTML data from object with given HTML parser

		for option in soup.find_all('option'):
			if option['value'] != '':
				code = option['value']
				fac_name = fix_tr_chars(option.text)

				new_faculty = Faculty(code, fac_name)
				self.faculties_list.append(new_faculty)

	def update_programs(self, faculty):
		programs = list()

		html = self.manager.urlopen('GET', "{}?fakulte={}".format(self.database_url, faculty.code))
		soup = BeautifulSoup(html.data, 'lxml')

		for option in soup.find('select', {'name':'subj'}).find_all('option'):
			if option['value'] != '':
				program_name = fix_tr_chars(option.text)
				new_program = Program(option['value'], program_name)
				programs.append(new_program)

		faculty.programs = programs

	#Updates whole terms in program if only program is given, does not assign courses to term
	#Updates courses of given term only if term is not None
	def update_terms(self, program = None, term = None):
		terms = list()

		terms_url = "{}{}".format(self.program_url, program.code)
		html = self.manager.urlopen('GET', terms_url)
		soup = BeautifulSoup(html.data, 'lxml')

		for href in soup.find_all('a', {'href':True})[2:]:
			course_url = "{}/{}".format(terms_url, href['href'])
			term_name = fix_tr_chars(href.text)

			if term is not None:
				if term.name == term_name:
					term = self.update_courses(term = term, course_url = course_url)
					terms.append(term)
					continue

			new_term = Term(term_name, program.code, course_url, None)
			terms.append(new_term)

		program.terms = terms
		return terms

	#Updates courses
	#If any term is given, assign courses to this term
	#If any courses list is given, append courses to this one
	#If any course url is given, use this url as data source
	def update_courses(self, term = None, course_url = None, courses = None, course_type = CourseType.NORMAL):
		if course_url is None:
			course_url = term.url

		if courses is None:
			courses = list()

		if term is None:
			program = course_url.split("/")[6]
		else:
			program = term.program_code

		html = self.manager.urlopen('GET', course_url)
		soup = BeautifulSoup(html.data, 'lxml')

		for table in soup.find_all('table', {'class':'plan'}):
			for course in table.find_all('tr')[1:]:
				a_list = course.find_all('a')
				href = a_list[0]['href']

				if href[0] != 'h':
					#This means this course has many options to choose
					if '(' in a_list[0].text:
						course_type = get_type(a_list[0].text.split("(")[1][:-1])
					else:
						course_type = CourseType.NORMAL

					courses = self.update_courses(term = term, course_url = "{}{}/{}".format(self.program_url, program, href), courses = courses, course_type = course_type)
					continue

				course_html = self.manager.urlopen('GET', href)
				course_soup = BeautifulSoup(course_html.data, 'lxml')

				info_tables = course_soup.find_all('table', {'class':'plan'})
				course_name = info_tables[0].find_all('tr')[1].find('td').text
				course_code, course_no = course_name.split(" ")

				if course_name in term.course_names: continue
				else: term.course_names.append(course_name)

				compulsary = True if a_list[-1].text == 'Z' else False

				req = info_tables[2].find_all('tr')[1].find_all('td')[1].text
				if req == "Yok/None": req = None

				new_course = Course(course_code, course_no, req, compulsary, course_type)
				courses.append(new_course)

		if term is not None:			
			term.courses = courses
			self.update_course_reqs(term)

		return courses

	#Updates prerequisitied courses
	def update_course_reqs(self, term):
		or_split = 'veya/or '
		min_split = ' MIN DD'

		if len(term.course_names) != 0:
			for c in term.courses:
				if c.req is not None: #Check if course has prerequisitied courses
					if or_split in c.req: #Check if the prerequisitied course is not single
						c.req = c.req.split(or_split)
					
						for i in range(len(c.req)):
							c.req[i] = c.req[i].split(min_split)[0]

							if '(' in c.req[i]:
								c.req[i] = c.req[i][1:]
							if ')' in c.req[i]:
								c.req[i] = c.req[i][:-1]