import csv

from random import seed
from random import randint
from random import random


class GeneticAlgorithm:
    """ Knapsack problem genetic algorithm:
    - chromosome - a binary string,
    - gene       - each bit of binary size,
    - fixed population size,
    - elite selection,
    - single point crossover,
    - gene-wise mutation.

    Knapsack problem - given a set of items, each with a volume and a value,
    determine the subset of this items to include in a collection so that the
    total volume is less than or equal to a given knapsack capacity and the
    total value is as large as possible.

    Knapsack equation: sum(value[i] * x[i]) <= capacity, where i - id of and
    an item in a set, x[i] = 1 if item i is included into the collection and
    x[i] = 0 if it is not. """

    RANDOM_SEED = 1975

    # Genetic algorithm parameters

    POPULATION_SIZE = 20
    POPULATIONS_LIMIT = 100
    CHROMOSOME_MUTATION_PROBABILITY = 0.3
    GENE_MUTATION_PROBABILITY = 0.1
    CHROMOSOME_SIZE = None

    # Knapsack problem parameters

    KNAPSACK_CAPACITY = 50
    ITEMS_SET_FILE = 'res/items.csv'

    # Before adding offspring to resulting population we will save it to a
    # separate list to perform mutation
    offspring_list = list()
    population = list()
    # A sorted by name list of items to put into a knapsack
    # (element = (name, volume, value))
    items_list = list()

    def __init__(self):
        seed(self.RANDOM_SEED)  # random.seed()
        self.load_items_set()
        self.create_starting_population()

        for i in range(self.POPULATIONS_LIMIT):
            self.panmixia_selection()
            self.population_crossover()
            self.mutate_population()
            self.create_new_population()

    def __str__(self):
        pass

    # Knapsack problem functions

    def load_items_set(self):
        """ Read data from res/items.csv and load it into items list. Each
        element of the list is a tuple that represents some item from file
        and consists of 3 elements: name, volume and value. """
        with open(self.ITEMS_SET_FILE, newline='') as csv_file:
            file_reader = csv.reader(csv_file, delimiter=',')

            for row in file_reader:
                item = (row[0], int(row[1]), int(row[2]))
                self.items_list.append(item)

        # Sort items list by name
        self.items_list = sorted(self.items_list, key=lambda x: x[0])
        self.CHROMOSOME_SIZE = len(self.items_list)

        return None

    def count_total_value(self, chromosome):
        """ Count a total value of items, that are marked as 1. """
        total_value = 0

        for i in range(self.CHROMOSOME_SIZE):
            mask = 1 << (self.CHROMOSOME_SIZE - i - 1)
            if mask & chromosome:
                total_value += self.items_list[i][2]

        return total_value

    def count_total_capacity(self, chromosome):
        """ Count a total capacity of items, that are marked as 1. """
        total_capacity = 0

        for i in range(self.CHROMOSOME_SIZE):
            mask = 1 << (self.CHROMOSOME_SIZE - i - 1)
            if mask & chromosome:
                total_capacity += self.items_list[i][1]

        return total_capacity

    def chromosome_to_collection(self, chromosome):
        """ Present a chromosome as a collection of items. """
        collection = list()

        for i in range(self.CHROMOSOME_SIZE):
            mask = 1 << (self.CHROMOSOME_SIZE - i - 1)
            if mask & chromosome:
                collection.append(self.items_list[i])

        return collection

    # Population initialization functions

    def create_individual(self):
        """ Each individual consists of one chromosome, that is represented
        by a binary string of CHROMOSOME_SIZE length. """
        chromosome = 0

        for i in range(self.CHROMOSOME_SIZE):
            chromosome = (chromosome << 1) + randint(0, 1)

        return chromosome

    def create_starting_population(self):
        for i in range(self.POPULATION_SIZE):
            self.population.append(self.create_individual())

        return None

    # Selection and breeding functions

    def panmixia_selection(self):
        """ Select individuals for breeding. """
        first_parent = self.population[
            randint(0, self.POPULATION_SIZE - 1)]
        second_parent = self.population[
            randint(0, self.POPULATION_SIZE - 1)]
        breeding_pair = [first_parent, second_parent]
        return breeding_pair

    def single_point_crossover(self, breeding_pair):
        # TODO: change
        """ Two individuals crossover.
        We exclude 0th and second last bit of each chromosome from list of
        possible crossover points to avoid the situations when children
        chromosomes are fully identical to their parents chromosomes. """
        first_parent = breeding_pair[0]
        second_parent = breeding_pair[1]

        # TODO: Create a "global" variable for 2 ** CHROMOSOME_SIZE instead
        #       of max_value.
        max_value = 2 ** self.CHROMOSOME_SIZE

        crossover_point = randint(1, self.CHROMOSOME_SIZE-2)
        binary_mask = max_value - 2 ** crossover_point

        first_child = first_parent & binary_mask + \
            second_parent & (max_value - binary_mask - 1)
        second_child = second_parent & binary_mask + \
            first_parent & (max_value - binary_mask - 1)

        offspring = (first_child, second_child)
        return offspring

    def population_crossover(self):
        """ Perform crossover for all selected individuals. """
        for i in range(self.POPULATION_SIZE):
            breeding_pair = self.panmixia_selection()

            if breeding_pair[0] != breeding_pair[1]:
                offspring = self.single_point_crossover(breeding_pair)
                self.offspring_list.append(offspring[0])
                self.offspring_list.append(offspring[1])

    # Mutation functions

    def mutate_chromosome(self, chromosome):
        gene_mutation_probabilities = (random() for i in range(self.CHROMOSOME_SIZE))
        inverting_mask = 0

        for probability in gene_mutation_probabilities:
            if probability < self.GENE_MUTATION_PROBABILITY:
                inverting_mask = (inverting_mask << 1) + 1
            else:
                inverting_mask = inverting_mask << 1

        mutated_chromosome = chromosome ^ inverting_mask
        return mutated_chromosome

    def mutate_population(self):
        for individual in self.offspring_list:
            if random() < self.CHROMOSOME_MUTATION_PROBABILITY:
                self.population.append(self.mutate_chromosome(individual))
            else:
                self.population.append(individual)

        self.offspring_list = []

    # Selection to new population functions

    def evaluate_fitness(self, individual):
        capacity = self.count_total_capacity(individual)
        value = self.count_total_value(individual)
        fitness = value if capacity <= self.KNAPSACK_CAPACITY else -value
        return fitness

    def create_new_population(self):
        """ Elite selection method. Sort and select n best. """
        fitness_list = list()

        for individual in self.population:
            fitness = self.evaluate_fitness(individual)
            fitness_list.append(fitness)

        # Sort population by fitness DESC
        new_population = sorted(list(zip(fitness_list, self.population)),
                                key=lambda f: f[0], reverse=True)
        self.population = []
        # In next population pass POPULATION_SIZE most fit individuals
        for i in range(self.POPULATION_SIZE):
            self.population.append(new_population[i][1])
