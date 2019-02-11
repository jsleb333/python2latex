from py2tex import TexEnvironment
import csv
from datetime import datetime as dt


class Plot(TexEnvironment):
    """

    """
    def __init__(self, *X_Y, plot_name=None, width=r'.8\textwidth', height=r'.45\textwidth', grid=True, marks=False, lines=True, axis_y='left', axis_x='bottom', position='h!', as_float_env=True, **axis_kwoptions):
        """
        Args:

        """
        self.as_float_env = as_float_env
        super().__init__('figure', options=position, label_pos='bottom')
        if self.as_float_env:
            self.body.append(r'\centering')
        else:
            self.head, self.tail = '', ''
        self.add_package('tikz')
        self.add_package('pgfplots')
        self.add_package('pgfplotstable')

        self.tikzpicture = TexEnvironment('tikzpicture')
        self.add_text(self.tikzpicture)

        if grid is True:
            grid = 'major'
        elif grid is False:
            grid = 'none'

        options = ('grid style={dashed,gray!50}',
                    f'axis y line*={axis_y}',
                    f'axis x line*={axis_x}',
                    'axis line style={-latex}')
        self.axis = TexEnvironment('axis', options=options, width=width, height=height, grid=grid, **axis_kwoptions)
        self.tikzpicture.add_text(self.axis)
        if not marks:
            self.axis.options += ('no marks',)

        self.plot_name = plot_name or f"plot-{dt.now().strftime(r'%Y-%m-%d %Hh%Mm%Ss')}"
        self.caption = ''

        iter_X_Y = iter(X_Y)
        self.plots = []
        for x, y in zip(iter_X_Y, iter_X_Y):
            self.add_plot(x, y)
        if len(X_Y) % 2 != 0: # Copies matplotlib.pyplot.plot() behavior
            self.add_plot(np.arange(len(X_Y[-1])), X_Y[-1])

        if not marks:
            mark_size = '0pt'
        elif isinstance(marks, str):
            mark_size = marks
        else:
            mark_size = '2pt'

        if not lines:
            line_width = '0pt'
        elif isinstance(lines, str):
            line_width = lines
        else:
            line_width = '1.5pt'

        self.default_plot_kwoptions = {'line width':line_width,
                                       'mark size':mark_size,
                                       }

    def add_plot(self, X, Y, *options, **kwoptions):
        options = tuple(opt.replace('_', ' ') for opt in options)
        kwoptions = {key.replace('_', ' '):value for key, value in kwoptions.items()}
        kwoptions.update({k:v for k, v in self.default_plot_kwoptions.items() if k not in kwoptions})
        self.plots.append((X, Y, options, kwoptions))

    def build_plots(self):
        for i, (X, Y, options, kwoptions) in enumerate(self.plots):
            options = ', '.join(options)
            kwoptions = ', '.join('='.join((k, v)) for k, v in kwoptions.items())
            if options and kwoptions:
                options += ', '
            self.axis.add_text(f"\\addplot+[{options+kwoptions}] table[x=x{i}, y=y{i}, col sep=comma]{{{self.plot_name+'.csv'}}};")

    def save_to_csv(self):
        with open(self.plot_name + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)

            titles = [coor for i in range(len(self.plots)) for coor in (f'x{i}', f'y{i}')]
            writer.writerow(titles)
            X_Y = [x_y for x, y, *_ in self.plots for x_y in (x, y)]
            for row in zip(*X_Y):
                writer.writerow(row)

    def build(self):
        self.save_to_csv()
        self.build_plots()

        if self.caption and self.as_float_env:
            self.body.append(f"\caption{{{self.caption}}}")
        return super().build()


if __name__ == '__main__':
    from py2tex import Document
    import numpy as np

    doc = Document('Plot_test', doc_type='article')
    sec = doc.new_section('Testing plots')
    sec.add_text("This section tests plots.")

    X = np.linspace(0,6,100)
    Y1 = np.sin(X)
    Y2 = np.cos(X)
    plot = sec.new(Plot(plot_name='plot_test'))
    plot.caption = 'Plot of the sine and cosine functions.'

    plot.add_plot(X, Y1, 'blue')
    plot.add_plot(X, Y2, 'orange')

    doc.build()

    # import matplotlib.pyplot as plt
    # plt.plot(X, Y1, X, Y2)
    # plt.show()
