import wx
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

def create_paraboloid_canvas(panel):
    figure = Figure(figsize=(6, 6))
    canvas = FigureCanvas(panel, -1, figure)
    ax = figure.add_subplot(111, projection='3d')
    
    x = np.linspace(-2, 2, 50)
    y = np.linspace(-2, 2, 50)
    X, Y = np.meshgrid(x, y)
    Z = X**2 - Y**2
    
    surface = ax.plot_surface(X, Y, Z, cmap='viridis')
    ax.set_axis_off()
    
    return canvas
