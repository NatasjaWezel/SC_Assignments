import math
import matplotlib.pyplot as plt
import numpy as np
import copy

def main():
    print("start")
    x = np.linspace(0,1,100)
    dx = 1/len(x)
    c = 0.001
    dt = 0.001

    y_min_1 = 0.9 * wave_function(x)
    y0 = wave_function(x)

    plt.plot(x,y0)
    plt.plot(x,y_min_1)



    for t in range(1, 500,100):
        print("timestep: " , t)

        y1 = next_step(c, x,  y_min_1, y0, dx, dt)

        y_min_1 = copy.copy(y0)
        y0 = copy.copy(y1)

        plt.plot(x, y1)
    plt.show()

def next_step(c, x_linspace, y_min_1, y_0, dx, dt):
    y_1 = []

    for i in range(len(x_linspace)):
        x = x_linspace[i]
        if x is 0 or i is len(x_linspace) - 1:
            y = 0
            y_1.append(y)
        else:
            y = c**2 * dt**2/dx**2\
                * (wave_function(x_linspace[i + 1]) + wave_function(x_linspace[i - 1]))\
                - y_min_1[i] + 2 * y_0[i]

            y_1.append(y)

    return y_1

def wave_function(x):
    # return np.sin(2 * math.pi * x)
    return np.sin(5 * math.pi * x)

if __name__ == '__main__':
    main()
