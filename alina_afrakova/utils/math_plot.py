import os
import re
import numpy as np
import matplotlib.pyplot as plt

from utils.math_solver import MathSolver


class MathPlot:
    def __init__(self) -> None:
        self.clear_plot()

    def clear_plot(self):
        self.fig = None
        
    def plot(self, expression: str, solver: MathSolver, path: str = 'plot.png') -> None:
        if not '=' in expression: return 'ERROR'
        y, expression = map(str.strip, expression.split('='))

        x = re.search('[a-zA-Z]', expression)
        if not x: return 'ERROR'
        x = expression[x.start() : x.end()]
        expression = solver.solve(expression, return_str=False)

        xs = np.range(-20, 20.1, 0.1)
        ys = []
        for x_value in xs:
            try:
                ys.append(expression.subs(x, x_value))
            except Exception as exc:
                return 'ERROR'

        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=(15, 15))

        self.ax.scatter(xs, ys, '-.', label=f'{y} = {str(expression)}')

        xmin, xmax, ymin, ymax = -20, 20, -20, 20

        self.ax.set(xlim=(xmin-1, xmax+1), ylim=(ymin-1, ymax+1), aspect='equal')

        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['left'].set_position('zero')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        self.ax.set_xlabel(x, size=14, labelpad=-24, x=1.03)
        self.ax.set_ylabel(y, size=14, labelpad=-21, y=1.02, rotation=0)

        x_ticks = np.arange(xmin, xmax+1, 1)
        y_ticks = np.arange(ymin, ymax+1, 1)
        self.ax.set_xticks(x_ticks[x_ticks != 0])
        self.ax.set_yticks(y_ticks[y_ticks != 0])
        self.ax.set_xticks(np.arange(xmin, xmax+1, 0.5), minor=True)
        self.ax.set_yticks(np.arange(ymin, ymax+1, 0.5), minor=True)

        self.ax.grid(which='both', color='grey', linewidth=1, linestyle='-', alpha=0.2)
        self.ax.legend(loc='upper right')

        arrow_fmt = dict(markersize=4, color='black', clip_on=False)
        self.ax.plot((1), (0), marker='>', transform=self.ax.get_yaxis_transform(), **arrow_fmt)
        self.ax.plot((0), (1), marker='^', transform=self.ax.get_xaxis_transform(), **arrow_fmt)

        path = os.path.join(os.path.dirname(__file__), path)
        self.fig.savefig(path, dpi=300)

        return path
