# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This file is part of a program that is used to solve some partial differential
# equations. The program has been developed for the course Scientific Computing
# in the master Computational Science at the UvA february/march 2019.
#
# This part contains the code for the diffusion grid. It's most important
# properties are it's width and height (the diffusion grid is always a square)
# and the diffusion constant. It contains code for all the different methods that
# are used to solve the diffusion equation, including the analytic method.
#
# You can't run this class on its own, but it is used in all the other diffusion
# files.
# Romy Meester & Natasja Wezel
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import numpy as np
import math
import pandas
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import copy
import time

import seaborn as sns
sns.set()

class DiffusionGrid():
    """ This is a class that contains the diffusion coefficient and dimensions for
        the diffusion grid. It also contains the diffusion grid itself."""

    def __init__(self, gridsize, eta):
        self.height = gridsize
        self.width = gridsize
        self.eta = eta

        self.step = 0

        # this is needed for the time independent methods
        self.converged = False
        self.reached_boundaries = False

        self.object_size = 1

        # this is needed for the aggregation
        self.candidates = []
        self.object = []

        self.initialize()

    def initialize(self):
        """" Initalize grid """
        self.grid = np.zeros((self.width, self.height))

        # initialize with concentrations from analytic solutions
        y = self.analytic_solution()

        # initialize top with concentration 1
        for j in range(0, self.height):
            for i in range(0, self.width):
                self.grid[j][i] = y[j]

        self.object_grid = [[0 for col in range(self.width)] for row in range(self.height)]

        # initalize object_grid with a seed
        self.object_grid[0][int(self.width / 2)] = 1

        # initialize candidate list
        self.candidates.append((int(self.width / 2), 1))
        self.candidates.append((int(self.width / 2) - 1, 0))
        self.candidates.append((int(self.width / 2) + 1, 0))

    def add_object(self):
        """ Refresh the grid (this is for the finding of the optimum omega). """
        self.grid = np.zeros((self.width, self.height))

        for j in range(self.width):
            self.grid[self.height - 1][j] = 1

        # # iterate over grid, first row is always concentration 1, last row always 0
        # for i in range(self.height):
        #     # iterate over columns, first and last are periodic boundaries
        #     for j in range(self.width):
        #
        #         # check if there's an object at this grid point
        #         if self.object_grid[i][j] == 1:
        #             self.grid[i][j] = 0


    def analytic_solution(self):
        """ This function contains a function to calculate the analytic solution
            for the diffusion equation. """

        # TODO what is this M lol
        M = 10
        x = np.linspace(0.,1.,self.width)

        # make a list with zeros
        y = [0]*len(x)
        t = 1
        D = 1
        for j,xj in enumerate(x):
            for i in range(0,M):
                # add each time
                y[j] += math.erfc((1-xj+2*i)/(2*np.sqrt(D*t))) - math.erfc((1+xj+2*i)/(2*np.sqrt(D*t)))

        return y

    def set_omega(self, w):
        """ Set the weight of omega for the SOR diffusion method. """
        self.w = w

    def next_step(self):
        """ Compute concentration in each grid point according to the right
            method. """

        if not self.converged:
            self.next_step_sor()
        else:
            self.check_aggregation()

        self.step += 1

    def next_step_sor(self):
        """ Compute concentration in each grid point with the succesive over
            relaxation method. This method converges only if the weight is between
            zero and two. For weight smaller then 1, the method is called under
            relaxation. For w = 1 we recover the Gauss-Seidel iteration.
            The updates can be performed in place. """

        # biggest difference that can happen is 1
        max_delta = 0

        # iterate over grid, first row is always concentration 1, last row always 0
        for i in range(1, self.height - 1):
            # iterate over columns, first and last are periodic boundaries
            for j in range(self.width):
                previous = self.grid[i][j]

                # check if there's an object at this grid point
                if not self.object_grid[i][j] == 1:
                    if j == 0:
                        self.grid[i][j] = self.w/4 *\
                                            (self.grid[i + 1][j]\
                                            + self.grid[i - 1][j]\
                                            + self.grid[i][j + 1]\
                                            + self.grid[i][self.width - 1])\
                                            + (1 - self.w) * self.grid[i][j]
                    else:
                        self.grid[i][j] = self.w/4 *\
                                            (self.grid[i + 1][j]\
                                            + self.grid[i - 1][j]\
                                            + self.grid[i][(j + 1) % self.width]\
                                            + self.grid[i][j - 1])\
                                            + (1 - self.w) * self.grid[i][j]

                delta = abs(self.grid[i][j] - previous)

                if delta > max_delta:
                    max_delta = delta

        print(self.step, max_delta, self.object_size)

        if max_delta < 10**-5:
            self.converged = True
            print(self.step, "CONVERGED!")

    def check_aggregation(self):
        """ Check if the candidates around the object aggregate or not. """

        # calculate total concentration of candidates
        denominator = self.candidates_concentration()

        new_candidates = []

        for coord in self.candidates:
            x = coord[0]
            y = coord[1]

            concentration = self.grid[y][x]

            # check if it aggregates
            if not denominator == 0 and np.random.random() <= (concentration**self.eta)/denominator:
                print(self.step, "AGGREGATIONNNNNNNNNN", x,y)
                # add to object, make it a sink
                self.object_grid[y][x] = 1
                self.grid[y][x] = 0

                # append these coordinates to object list
                self.object.append((x,y))

                if x == 0 or x == self.width - 1 or y == self.height - 1:
                    self.reached_boundaries = True

                # remove from candidates
                self.candidates.remove(coord)

                # add new candidates if not at boundaries and if not already in there
                new_candidates.extend([(x + 1,y),(x - 1, y),(x, y + 1),(x, y - 1)])

                self.object_size += 1

        for new_coord in new_candidates:
            if not new_coord in self.candidates\
                    and not new_coord in self.object\
                    and new_coord[0] <= self.width - 1\
                    and new_coord[0] >= 0\
                    and new_coord[1] <= self.height -1\
                    and new_coord[1] >= 0:

                self.candidates.append(new_coord)

        self.converged = False

    def candidates_concentration(self):
        """ Calculates total concentration of all candidates together. """

        concentration = 0

        for coord in self.candidates:
            plus = self.grid[coord[1]][coord[0]]
            if self.grid[coord[1]][coord[0]] < 0:
                plus = 0
            concentration = concentration + plus**self.eta

        return concentration
