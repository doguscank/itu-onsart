import pydot
import database as db
from database import CourseType

def draw_graph(term):
	g = pydot.Dot(graph_type = 'digraph')

	for c in term.courses:
		types = [CourseType.NORMAL, CourseType.ITB, CourseType.MT, CourseType.TM, CourseType.TB, CourseType.SNT]
		colors = ["cadetblue1", "chartreuse", "goldenrod1", "goldenrod1", "goldenrod1", "chartreuse"]
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
		
		if c.req is not None:
			for r in c.req:
				if r in term.course_names:
					g.add_edge(pydot.Edge(pydot.Node(r), pydot.Node(c.name)))
	
	g.write_png("outputs/{}.png".format(term.program_code))