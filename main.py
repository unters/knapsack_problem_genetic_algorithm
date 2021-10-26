from GeneticAlgorithm import GeneticAlgorithm


def main():
    ga = GeneticAlgorithm()
    resulting_population = ga.population.copy()
    fitness_list = list()

    for individual in resulting_population:
        fitness = ga.evaluate_fitness(individual)
        fitness_list.append(fitness)

    index, max_value = max(enumerate(fitness_list), key=lambda i_v: i_v[1])
    best_collection = resulting_population[index]
    capacity = ga.count_total_capacity(best_collection)
    value = ga.count_total_value(best_collection)

    print(best_collection, capacity, value, sep=' ')
    for item in ga.chromosome_to_collection(best_collection):
        print(item)

    return None


if __name__ == "__main__":
    main()
