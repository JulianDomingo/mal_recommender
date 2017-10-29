import math


def euclidean_similarity(user1, user2):
    common_ranked_items = [itm for itm in data[user1] if itm in data[user2]]
    rankings = [(data[user1][itm], data[user2][itm]) for itm in common_ranked_items]
    distance = [pow(rank[0] - rank[1], 2) for rank in rankings]

    return 1 / (1 + sum(distance))


def pearson_similarity(user1, user2):
    common_ranked_items = [itm for itm in data[user1] if itm in data[user2]]

    n = len(common_ranked_items)

    s1 = sum([data[user1][item] for item in common_ranked_items])
    s2 = sum([data[user2][item] for item in common_ranked_items])

    ss1 = sum([pow(data[user1][item], 2) for item in common_ranked_items])
    ss2 = sum([pow(data[user2][item], 2) for item in common_ranked_items])

    ps = sum([data[user1][item] * data[user2][item] for item in common_ranked_items])

    num = n * ps - (s1 * s2)

    den = math.sqrt((n * ss1 - math.pow(s1, 2)) * (n * ss2 - math.pow(s2, 2)))

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

        for itm in ranked:
            if itm not in data[person]:
                weight = sim * ranked[itm]

                if itm in recommendations:
                    s, weights = recommendations[itm]
                    recommendations[itm] = (s + sim, weights + [weight])
                else:
                    recommendations[itm] = (sim, [weight])

    for r in recommendations:
        sim, item = recommendations[r]
        recommendations[r] = sum(item) / sim

    return recommendations
