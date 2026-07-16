from e2e_ai.codegen import generate_test_file, generate_test_function
from e2e_ai.scenario import parse


def test_generate_test_function_renders_all_step_types():
    scenario = '''
    Visit "/login"
    Fill in "Username" with "victoria"
    Click "Login"
    Expect to see "Welcome, victoria"
    Expect the url to contain "/dashboard"
    '''
    steps = parse(scenario)
    code = generate_test_function("login", steps)

    assert "def test_login(page: Page) -> None:" in code
    assert 'page.goto(BASE_URL + "/login")' in code
    assert 'page.get_by_label("Username").fill("victoria")' in code
    assert 'page.get_by_role("button", name="Login").click()' in code
    assert 'expect(page.get_by_text("Welcome, victoria")).to_be_visible()' in code
    assert 'expect(page).to_have_url(BASE_URL + "/dashboard")' in code


def test_generate_test_file_includes_header_and_imports():
    steps = parse('Visit "/login"')
    code = generate_test_file("smoke", steps)

    assert "from playwright.sync_api import Page, expect" in code
    assert "BASE_URL = os.environ.get" in code
    assert code.strip().endswith('page.goto(BASE_URL + "/login")')


def test_generated_code_is_valid_python():
    steps = parse('Visit "/login"\nClick "Login"')
    code = generate_test_file("valid", steps)
    compile(code, "<generated>", "exec")
