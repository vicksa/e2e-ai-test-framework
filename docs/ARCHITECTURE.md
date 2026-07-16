# Arquitetura

```
src/e2e_ai/
├── scenario.py     # parser: texto (grammar de linha por ação) -> list[Step]
├── codegen.py      # Step[] -> código Python de teste Playwright/pytest
├── llm_backend.py  # opcional: normaliza prosa livre para a grammar via LLM
└── cli.py          # `e2e-ai generate <arquivo> --out <arquivo> --name <nome>`

examples/
├── app.py               # app Flask mínima (login) usada como alvo real dos testes
└── login_scenario.txt   # cenário de exemplo em linguagem natural

generated_tests/
└── test_login.py   # saída de exemplo do codegen, versionada para referência

tests/
├── test_scenario.py    # testes do parser
├── test_codegen.py      # testes do gerador de código
└── test_llm_backend.py  # testes do fallback sem API key

conftest.py          # sobe o app Flask de exemplo em thread de fundo antes dos testes
```

## Fluxo

1. Um cenário é escrito em uma gramática simples e explícita, uma ação por
   linha (`Visit "url"`, `Fill in "campo" com "valor"`, `Click "alvo"`,
   `Expect to see "texto"`, `Expect the url to contain "texto"`).
2. `scenario.parse()` transforma o texto em uma lista de `Step` tipados.
3. `codegen.generate_test_file()` transforma os `Step`s em um arquivo de
   teste Python real usando a API síncrona do Playwright e o plugin
   `pytest-playwright` (fixture `page`).
4. O arquivo gerado é executável como qualquer teste pytest normal —
   `conftest.py` sobe uma app Flask de demonstração para os testes terem
   um alvo real, mas em um cenário de uso real o `BASE_URL` apontaria para
   o ambiente de staging/produção da aplicação sob teste.

## Por que gramática fixa em vez de NLP livre por padrão

Um parser determinístico é rápido, não tem custo de API, e falha de forma
previsível (erro claro de linha) quando o cenário não está no formato
esperado — importante para confiabilidade em CI. `llm_backend.py` oferece
uma camada opcional que reescreve prosa livre para essa gramática antes do
parse, para quem quiser descrever cenários em linguagem mais solta; ela é
puramente aditiva e cai para "sem alteração" quando `ANTHROPIC_API_KEY` não
está configurada, então o pipeline nunca depende de uma API externa para
funcionar.

## Limitações conhecidas

- A gramática cobre ações comuns de formulário/navegação/asserção de texto
  — fluxos mais complexos (upload de arquivo, drag-and-drop, iframes)
  precisariam de novas ações em `scenario.py` e `codegen.py`.
- `page.get_by_label` e `page.get_by_role("button", name=...)` assumem que
  a aplicação sob teste usa `<label>` associado corretamente e texto
  acessível nos botões — é uma boa prática de acessibilidade, mas nem toda
  aplicação segue isso; nesse caso os seletores gerados podem precisar de
  ajuste manual.
