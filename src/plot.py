from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter


PLOT_VARIATION_ON_REGION = True

if PLOT_VARIATION_ON_REGION:
    fig = plt.figure(figsize=(8, 8))
    fig.suptitle('representation of the potential field', fontsize=17, fontweight='bold', y=0.98)
    fig.subplots_adjust(bottom=0.10, left=0.1, right=0.90, top=0.90)
    ax1 = fig.add_subplot(1, 1, 1, projection='3d')