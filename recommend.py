import math


def euclidean_similarity(user1, user2):
    """
    Calculates the euclidean distance for two users. 
    """
    intersection_of_rated_shows = [item for item in data[user1] if item in data[user2]]
    ratings = [(data[user1][item], data[user2][item]) for item in intersection_of_rated_shows]
    distance = [pow(rate[0] - rate[1], 2) for rate in ratings]

    return 1 / (1 + sum(distance))


def pearson_similarity(user1, user2):
    """
    Calculates the Pearson correlation coefficient 
    between two users. This measures the linear dependence
    for two variables; in this use case, the rankings of
    intersected shows between two users. 
    :param user1  Mapping of username to ratings for the first user. 
    :param user2  Mapping of username to ratings for the second user. 
    """
    intersection_of_rated_shows = [item for item in data[user1] if item in data[user2]]
    length = len(intersection_of_rated_shows)

    s1 = sum([data[user1][item] for item in intersection_of_rated_shows])
    s2 = sum([data[user2][item] for item in intersection_of_rated_shows])

    ss1 = sum([pow(data[user1][item], 2) for item in intersection_of_rated_shows])
    ss2 = sum([pow(data[user2][item], 2) for item in intersection_of_rated_shows])

    ps = sum([data[user1][item] * data[user2][item] for item in intersection_of_rated_shows])

    num = length * ps - (s1 * s2)

    den = math.sqrt((length * ss1 - math.pow(s1, 2)) * (length * ss2 - math.pow(s2, 2)))

    return (num / den) if den != 0 else 0


def recommend(person, bound, similarity=pearson_similarity):
    scores = [(similarity(person, other), other) for other in data if other != person]

    scores.sort()
    scores.reverse()
    scores = scores[0:bound]

    print scores

    recommendations = {}

    for sim, other in scores:
        ranked = data[other]

        for item in ranked:
            if item not in data[person]:
                weight = sim * ranked[item]

                if item in recommendations:
                    s, weights = recommendations[item]
                    recommendations[item] = (s + sim, weights + [weight])
                else:
                    recommendations[item] = (sim, [weight])

    for r in recommendations:
        sim, item = recommendations[r]
        recommendations[r] = sum(item) / sim

    return recommendations
