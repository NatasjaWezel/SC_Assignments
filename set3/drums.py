# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This file is part of a program that is used to solve the wave equations.
# The program has been developed for the course Scientific Computing
# in the master Computational Science at the UvA february/march 2019.
#
# Romy Meester & Natasja Wezel
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy as np
import scipy as sp
import random
from scipy import linalg
from scipy.sparse import linalg as linalg2

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from Drum import Drum

from mpl_toolkits import mplot3d
import math
import seaborn as sns
sns.set()

def main():
    L = 1
    # amount of discretization steps
    N = 21 * L
    # N = 5

    # shape can be "Square", "Rectangle" or "Circle"
    shape = "Circle"

    circle = False

    if shape == "Square":
        width = N
        height = N
        M = make_square_matrix(L, N)

    elif shape == "Rectangle":
        width = N
        height = 2 * N
        M = make_rectangle_matrix(L, N, height)

    elif shape == "Circle":
        width = N
        height = N
        M, circle = make_circle_matrix(L, N)

    # find eigenvalues and eigenvectors of the matrix
    eigenvalues, eigenvectors = find_eigenvalues(M)

    # sort from low to high
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[idx, :]

    # plot the 10 first modes
    eigenmodes = find_eigenmodes(eigenvectors, eigenvalues, shape, width, height)
    # graph_surfaces(eigenmodes, L, width, height, shape)

    # make animation
    show_animation(eigenmodes, shape, circle)

def find_eigenvalues(M):
    """ Calculate the eigenvalues and corresponding eigenvectors
    of the matrix M. """
    # eigenvalues, eigenvectors = linalg.eig(M)
    # eigenvalues, eigenvectors = linalg2.eigs(M, k=2500)
    # print(eigenvalues, len(eigenvalues))

    eigenvalues, eigenvectors = linalg.eig(M)

    eigenvectors = eigenvectors.T
    eigenvalues = eigenvalues.real

    return eigenvalues, eigenvectors

def graph_surfaces(eigenmodes, L, width, height, shape):
    """ Makes an 2D and 3D plot of the drum. """

    x = np.linspace(0, L, width)
    y = np.linspace(0, 2*L, height)

    X, Y = np.meshgrid(x, y)

    for i, eigenvalue in enumerate(eigenmodes):
        plt.figure()
        plt.grid(False)

        plt.title("$\lambda$: " + str(eigenvalue))
        plt.imshow(eigenmodes[eigenvalue], cmap='viridis', origin="lower", vmin=-0.05, vmax=0.05)
        plt.colorbar()
        plt.savefig("results/drum" + str(abs(eigenvalue.real)) + "_" + str(i) + ".png", dpi=150)
        plt.close()

        plt.title("$\lambda$: " + str(eigenvalue.real))
        ax = plt.axes(projection='3d')


        ax.set_xlim(0,2)
        ax.set_ylim(0,2)


        ax.plot_surface(X, Y, eigenmodes[eigenvalue], rstride=1, cstride=1, cmap='viridis', edgecolor='none')
        plt.savefig("results/drum" + str(abs(eigenvalue.real)) + "_" + str(i) + "_3D.png", dpi=150)
        plt.close()

def find_eigenmodes(eigenvectors, eigenvalues, shape, width, height):
    """ Finds eigenmodes that belong with the smallest eigenvalues. """

    eigenmodes = {}

    for i in range(10):
        # plot first .. frequencies
        eigenvalue = eigenvalues[i]
        eigenvector = eigenvectors[i]

        if not eigenvalue == 0.0:
            # matrix = np.reshape(eigenvector.real, (height, width), order='F')
            matrix = np.reshape(eigenvector.real, (height, width))

            eigenmodes[eigenvalue] = matrix

    return eigenmodes

def make_square_matrix(L, N):
    """ This is a function that makes the matrix of a square. """
    dimension = N**2
    M = np.zeros((dimension, dimension))
    dx = (L/N)

    outer_diagonal = N
    inner_diagonal = 1

    for i in range(dimension):
        try:
            M[outer_diagonal, i] = 1 * (1/dx**2)
            M[i, outer_diagonal] = 1 * (1/dx**2)
        except IndexError:
            pass

        try:
            if not inner_diagonal % N == 0:
                M[inner_diagonal, i] = 1 * (1/dx**2)
                M[i, inner_diagonal] = 1 * (1/dx**2)
        except IndexError:
            pass

        outer_diagonal += 1
        inner_diagonal += 1

    np.fill_diagonal(M, -4 * (1/dx**2))

    return M

def make_rectangle_matrix(L, N, height):
    """ This is a function that makes the matrix of a rectangle. """
    dimension = N * height
    M = np.zeros((dimension, dimension))
    dx = (L/N)

    # TODO: This can't be right, there's two L here ... different amount
    # of discretization steps in the two directions (I think?)

    outer_diagonal = N
    inner_diagonal = 1

    for i in range(dimension):
        try:
            M[outer_diagonal, i] = 1 * (1/dx**2)
            M[i, outer_diagonal] = 1 * (1/dx**2)
        except IndexError:
            pass

        try:
            if not inner_diagonal % N == 0:
                M[inner_diagonal, i] = 1 * (1/dx**2)
                M[i, inner_diagonal] = 1 * (1/dx**2)
        except IndexError:
            pass

        outer_diagonal += 1
        inner_diagonal += 1

    np.fill_diagonal(M, -4 * (1/dx**2))

    return M

def make_circle_matrix(L,N):
    R = N/2
    radius = L/2

    circle = np.zeros((N,N))

    # iterate over matrix, check if distance is < radius, if yes, it's a 1
    x, y = math.floor(N/2), math.floor(N/2)

    for i, row in enumerate(circle):
        for j, column in enumerate(row):
            distance = (math.sqrt(abs(i - x)**2 + abs(j - y)**2))/N

            if distance < radius:
                circle[i, j] = 1
                
    print(circle)
    M = make_square_matrix(L, N)

    # step over matrix, check if it's a one in the circle
    for i in range(len(M)):
        row = math.floor(i/N)
        column = i % N

        # if this point does not belong to the circle, change the values in the matrix row to 0
        if circle[row, column] == 0:
            for j in range(len(M)):
                if not i == j:
                    M[i, j] = 0
    print(M)
    return M, circle

def show_animation(eigenmodes, shape, circle):
    dt = 0.001
    tmax = 0.2
    timesteps = math.ceil(tmax/dt)

    # this needs to be global for the animation
    global current_state, fig, ax
    hoi = 1
    for eigenvalue in eigenmodes:
        # initiate image
        if not hoi == 0:
            current_state = Drum(eigenmodes[eigenvalue], eigenvalue, shape)

            if shape == "Circle":
                current_state.set_circle(circle)
        hoi = 0

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    plt.title("Vibration of eigenmode with $\lambda$: " + str(current_state.eigenvalue.real) + " timestep: " + str(current_state.timestep))
    ax.plot_surface(current_state.X, current_state.Y, current_state.state, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
    ax.set_xlim(0,20)
    ax.set_ylim(0,20)
    ax.set_zlim(-0.1,0.1)
    # animation
    anim = animation.FuncAnimation(fig, animate, frames=timesteps, interval=1, repeat=False)
    plt.show()

def animate(i):
    """ Calculate next state and set that for the animation. """
    ax.clear()
    ax.set_zlim(-0.1,0.1)

    current_state.next_step()

    plt.title("Vibration of eigenmode with $\lambda$: " + str(current_state.eigenvalue.real) + " timestep: " + str(current_state.timestep))
    ax.plot_surface(current_state.X, current_state.Y, current_state.state, rstride=1, cstride=1, cmap='viridis', edgecolor='none')

    return plt,

if __name__ == '__main__':
    main()
