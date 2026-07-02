from RoyalAnalyzer.app.core.models import Combination, Roll, detect_combination
from RoyalAnalyzer.app.predictors.ensemble import VotingEnsemble
from RoyalAnalyzer.app.statistics.metrics import frequencies, shannon_entropy, transition_matrix


def test_detect_combination_strengths():
    assert detect_combination((6, 6, 6, 6, 6)) == Combination.PENTA
    assert detect_combination((1, 2, 3, 4, 5)) == Combination.SERIES
    assert detect_combination((2, 2, 2, 3, 3)) == Combination.HET


def test_statistics_and_ensemble_prediction():
    rolls = [Roll((1, 2, 3, 4, 5), chosen_dice=1), Roll((2, 2, 3, 4, 5), chosen_dice=2)]
    assert frequencies(rolls)[1] == 1
    assert shannon_entropy(rolls) == 1.0
    matrix = transition_matrix(rolls)
    assert len(matrix) == 6
    assert all(len(row) == 6 for row in matrix)
    model = VotingEnsemble()
    model.fit(rolls)
    prediction = model.predict(rolls)
    assert set(prediction) == {1, 2, 3, 4, 5, 6}
    assert round(sum(prediction.values()), 6) == 1.0
