import pytest

from e2e_ai.scenario import ScenarioParseError, parse


def test_parse_full_scenario():
    scenario = '''
    Visit "/login"
    Fill in "Username" with "victoria"
    Fill in "Password" with "secret123"
    Click "Login"
    Expect to see "Welcome, victoria"
    '''
    steps = parse(scenario)
    assert [s.action for s in steps] == ["visit", "fill", "fill", "click", "expect_text"]
    assert steps[0].args == {"url": "/login"}
    assert steps[1].args == {"field": "Username", "value": "victoria"}
    assert steps[3].args == {"target": "Login"}
    assert steps[4].args == {"text": "Welcome, victoria"}


def test_parse_ignores_blank_lines_and_comments():
    scenario = '''
    # this is a comment

    Visit "/login"

    '''
    steps = parse(scenario)
    assert len(steps) == 1


def test_parse_expect_url():
    steps = parse('Expect the url to contain "/dashboard"')
    assert steps[0].action == "expect_url"
    assert steps[0].args == {"url": "/dashboard"}


def test_parse_raises_on_unknown_line():
    with pytest.raises(ScenarioParseError):
        parse("do something magical")


def test_parse_raises_on_empty_scenario():
    with pytest.raises(ScenarioParseError):
        parse("   \n  # only a comment\n")


def test_parse_accepts_single_quotes():
    steps = parse("Click 'Submit'")
    assert steps[0].args == {"target": "Submit"}
