# e2e-ai-test-framework

Framework de testes E2E (Playwright + Pytest) com **geração de cenários de
teste a partir de descrições em linguagem natural**, com um backend LLM
opcional para normalizar prosa livre antes de gerar o código do teste.

## Por que isso importa

Escrever testes E2E manualmente é repetitivo: cada fluxo (login, checkout,
cadastro) vira dezenas de linhas de seletores e asserções. Este framework
deixa você descrever o fluxo como uma sequência de passos simples e gera o
arquivo de teste Playwright/pytest automaticamente — reduzindo o
boilerplate e tornando os cenários legíveis por qualquer pessoa do time
(QA, PM, dev), não só por quem escreve os testes.

## Instalação

```bash
pip install -e ".[dev]"
playwright install --with-deps chromium
```

## Uso

Escreva um cenário como este (`examples/login_scenario.txt`):

```
Visit "/login"
Fill in "Username" with "victoria"
Fill in "Password" with "secret123"
Click "Login"
Expect to see "Welcome, victoria"
```

Gere o teste:

```bash
e2e-ai generate examples/login_scenario.txt --out generated_tests/test_login.py --name login
```

Isso gera:

```python
def test_login(page: Page) -> None:
    page.goto(BASE_URL + "/login")
    page.get_by_label("Username").fill("victoria")
    page.get_by_label("Password").fill("secret123")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("Welcome, victoria")).to_be_visible()
```

E roda como qualquer teste pytest:

```bash
pytest generated_tests/test_login.py
```

## Rodando a demo completa

Este repositório inclui uma mini aplicação Flask (`examples/app.py`) usada
como alvo real do teste gerado acima — não é preciso configurar nada, o
`conftest.py` sobe essa aplicação automaticamente antes da suíte rodar:

```bash
pytest
```

## Geração assistida por LLM (opcional)

Para descrever o cenário em prosa livre em vez da gramática fixa:

```bash
export ANTHROPIC_API_KEY=sk-...
e2e-ai generate scenario_em_prosa.txt --out generated_tests/test_x.py --name x --llm
```

Sem a variável de ambiente configurada, `--llm` simplesmente é ignorado e o
texto é interpretado diretamente pela gramática fixa — o framework nunca
depende de uma API externa para funcionar.

## Arquitetura

Veja [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) para o detalhamento de
cada módulo e o racional de design.

## Testes

```bash
pytest --cov=e2e_ai --cov-report=term-missing
```

## Licença

MIT
