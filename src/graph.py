import pydot
import database as db
from database import CourseType

def draw_graph(term, dmajor_term = None):
	g = pydot.Dot(graph_type = 'digraph', concentrate = True, pack = True, label = "{} {}".format(term.program_code, term.name), labelloc = 't')
	
	"""
	legend = pydot.Cluster(label = 'Lejant')
	l1 = legend.add_node(pydot.Node('Zorunlu', shape = 'box'))
	l2 = legend.add_node(pydot.Node('Secmeli', shape = 'ellipse'))
	l3 = legend.add_node(pydot.Node('NORMAL', style = 'filled', fillcolor = 'cadetblue1', fontcolor = 'white', pos = '0!,0!'))
	l4 = legend.add_node(pydot.Node('MT', style = 'filled', fillcolor = 'crimson', fontcolor = 'white'))
	l5 = legend.add_node(pydot.Node('TM', style = 'filled', fillcolor = 'gold3', fontcolor = 'white'))
	l6 = legend.add_node(pydot.Node('TB', style = 'filled', fillcolor = 'darkgreen', fontcolor = 'white'))

	g.add_subgraph(legend)
	"""

	if dmajor_term is None:
		courses = term.courses
		course_names = term.course_names
	else:
		courses = term.courses
		if dmajor_term.courses is not None:
			courses.extend(dmajor_term.courses)

		course_names = [c.name for c in courses]

	for c in courses:
		types = [CourseType.NORMAL, CourseType.ITB, CourseType.MT, CourseType.TM, CourseType.TB, CourseType.SNT]
		colors = ["cadetblue1", "chartreuse", "crimson", "gold3", "darkgreen", "chartreuse"]
		shapes = ["box", "ellipse"]

		selected_shape = None
		selected_color = None

		if c.compulsary:
			selected_shape = shapes[0]
		else:
			selected_shape = shapes[1]

		for i in range(len(types)):
			if c.course_type == types[i]:
				selected_color = colors[i]

		g.add_node(pydot.Node(c.name, style = 'filled', shape = selected_shape, fillcolor = selected_color, fontcolor = 'white'))
		
		#print(c.name, c.req)

		if c.req is not None:
			for r in c.req:
				if r in course_names:
					g.add_edge(pydot.Edge(pydot.Node(r), pydot.Node(c.name)))

	if term.has_snt:
		g.add_node(pydot.Node('SNT', style = 'filled', shape = 'box', fillcolor = 'chartreuse', fontcolor = 'white'))

	if term.itb_count != 0:
		for i in range(term.itb_count - 1):
			g.add_node(pydot.Node("ITB {}".format(i + 1), style = 'filled', shape = 'box', fillcolor = 'chartreuse', fontcolor = 'white'))
	
	if dmajor_term is None:
		g.write_png("outputs/{}.png".format(term.program_code))
	else:
		g.write_png("outputs/{}.png".format(dmajor_term.program_name))

if __name__ == '__main__':
	g1 = pydot.Dot(graph_type = 'digraph', pack = True)
	g = pydot.Subgraph(graph_type = 'digraph', pack = True)
	c = pydot.Subgraph(label = 'foo', labelloc = 't', color = 'black', shape = 'box')
	c.add_node(pydot.Node('foo1'))

	for i in range(20):
		g.add_edge(pydot.Edge(pydot.Node(str(i)), pydot.Node(str(i % 4))))

	g1.add_subgraph(c)
	g1.add_subgraph(g)

	g1.write_png('deneme1.png')