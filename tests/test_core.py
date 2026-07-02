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

from RoyalAnalyzer.app.collectors.royal_dom_parser import parse_last_roll, parse_royal_dice_html


def test_parse_supplied_royal_dom_snippet():
    html = '''<div class="sc-zOxLx cgJbZr"><div class="sc-jxYSNo gDtmG"><div class="sc-erPUmh BKmw"><div color="Red" class="sc-iRTMaw hhTurn"><div class="sc-eKrodz laUure" style="grid-area: 1 / 1;"></div><div class="sc-eKrodz laUure" style="grid-area: 1 / 3;"></div><div class="sc-eKrodz laUure" style="grid-area: 3 / 1;"></div><div class="sc-eKrodz laUure" style="grid-area: 3 / 3;"></div></div><div color="Blue" class="sc-iRTMaw hoviMl"><div class="sc-eKrodz laUure" style="grid-area: 2 / 2;"></div></div></div></div></div>'''
    dice = parse_royal_dice_html(html)
    assert [die.value for die in dice] == [4, 1]
    assert [die.color for die in dice] == ["Red", "Blue"]


def test_parse_last_roll_from_history_level():
    die = lambda color, pips: f'<div color="{color}">' + ''.join('<div style="grid-area: 1 / 1;"></div>' for _ in range(pips)) + '</div>'
    html = '<section>' + ''.join(die('Red' if value % 2 else 'Blue', value) for value in [1, 2, 3, 4, 5]) + '</section>'
    assert parse_last_roll(html) == (1, 2, 3, 4, 5)
