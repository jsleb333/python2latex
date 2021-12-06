from python2latex import Template, Table, Plot

filepath = './examples/templating an existing file'
template = Template(filename='already_existing_file', filepath=filepath)

table = Table((4,3))
table[1:,0:] = [[i for _ in range(3)] for i in range(3)]
table[0] = 'Title'
table[0].add_rule()
table.caption = 'Here is a table caption.'

template.anchors['some_table'] = table

plot = Plot(plot_name='some_plot', plot_path=filepath)
plot.add_plot(list(range(10)), list(range(10)), 'red')
plot.caption = 'Here is a figure caption.'

template.anchors['some_figure'] = plot

template.render()
