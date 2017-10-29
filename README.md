# mal_recommender
Recommendation system for MAL.

The 'similarity' score of 2 MAL users is based on the euclidean distance of two particular show ratings which both users have rated. 
similarity\_score = (1 / (1 + euclidean\_(i, j))) # where 'i' and 'j' represent show ratings AND (0 <= similarity\_score <= 1)
