# Sugestões de Produto

API e interface web para cadastrar, comentar, votar e acompanhar sugestões de melhorias de um produto. A aplicação centraliza propostas, registra discussões e permite acompanhar o status de cada sugestão.

> **Estado do projeto:** em planejamento. Os modelos, as rotas e a estrutura descritos neste documento definem o escopo previsto. As instruções de instalação e execução serão adicionadas conforme os componentes estiverem disponíveis.

O plano detalhado, com cinco etapas e critérios de conclusão, está em [PLANO.md](PLANO.md).

## Funcionamento previsto

1. Uma pessoa cadastra uma sugestão com título, descrição e categoria.
2. A API Flask valida os dados e usa o SQLAlchemy para salvá-los no PostgreSQL.
3. A interface permite listar e filtrar sugestões, consultar detalhes, editar dados e acompanhar o status.
4. Cada sugestão pode receber comentários e votos. Um voto acrescenta uma unidade ao contador.
5. Quando solicitado, o backend consulta o Jev para sugerir uma categoria ou uma API de geração de texto para produzir um resumo. As operações são independentes; cada resultado é revisado antes de ser enviado no cadastro ou na edição.

A versão inicial prevê duas tabelas relacionadas e uma interface web para cadastro e acompanhamento. O contador de votos não identifica pessoas: chamadas repetidas contam novos votos. Autenticação, controle de um voto por pessoa, anexos e notificações ficam fora do escopo inicial.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python e Flask |
| Banco e modelos | PostgreSQL local, Flask-SQLAlchemy, SQLAlchemy e psycopg |
| Migrações | Flask-Migrate e Alembic |
| Configuração | Variáveis de ambiente e python-dotenv |
| Testes | pytest, cliente de testes do Flask, SQLite temporário e mocks da IA |
| Classificação por IA | TypeSafe AI, com System One/Jev, chamada pelo backend |
| Geração de resumo | API de geração de texto, com provedor a definir |
| Interface | React, TypeScript e Vite |
| Versionamento | Git/GitHub, branches, commits e pull requests |

O banco da aplicação será `sugestoes_produto`, com usuário `sugestoes_app` e variáveis `SUGESTOES_DB_*`. A chave `TYPESAFE_API_KEY` e a credencial do provedor de resumos ficarão apenas no backend, em configurações independentes. A suíte SQLite será isolada; as migrações também serão verificadas no PostgreSQL.

O Jev será usado para escolher uma categoria entre os valores permitidos. Sua API retorna decisões estruturadas, probabilidades e confiança, sem geração de texto. [Documentação da TypeSafe](https://docs.typesafe.ai/introduction).

A geração do resumo ficará a cargo de um segundo provedor. Gemini e GroqCloud são candidatos com faixa gratuita; a escolha do provedor e do modelo permanece em aberto. As condições de uso devem ser conferidas na [tabela de preços do Gemini](https://ai.google.dev/gemini-api/docs/pricing) e nos [limites gratuitos do GroqCloud](https://console.groq.com/docs/rate-limits).

## Modelo de dados planejado

| Modelo | Campos |
| --- | --- |
| Sugestão | `id`, `titulo`, `descricao`, `categoria`, `status`, `votos`, `criado_em`, `atualizado_em`; `resumo` será acrescentado na etapa 4 |
| Comentário | `id`, `sugestao_id`, `autor`, `texto`, `criado_em` |

- **Título:** texto obrigatório, até 200 caracteres.
- **Descrição:** texto obrigatório, até 4.000 caracteres, também aceito pelas rotas de IA.
- **Categoria:** obrigatória; valores `interface`, `funcionalidade`, `desempenho`, `integracao` e `outros`.
- **Status:** começa em `nova`; valores `nova`, `em analise`, `implementada` e `descartada`. A edição permite escolher qualquer um desses valores.
- **Votos:** inteiro não negativo, iniciado em zero e alterado somente pela rota de votação.
- **Resumo, a partir da etapa 4:** opcional; `null` ou texto não vazio de até 300 caracteres. Pode ser escrito manualmente ou adotado após revisão da IA.
- **Comentário:** `autor` obrigatório, até 100 caracteres; `texto` obrigatório, até 2.000 caracteres; `sugestao_id` aponta para uma sugestão existente.

Textos obrigatórios compostos apenas por espaços são inválidos. IDs, datas e votos são definidos pelo servidor. Ao excluir uma sugestão, seus comentários também são excluídos.

## Contrato planejado da API

As operações recebem e devolvem JSON. As datas serão representadas no formato ISO 8601. As listas serão arrays, inclusive quando vazias.

| Método | Rota | Comportamento e resposta de sucesso |
| --- | --- | --- |
| GET | `/health` | Verifica a conexão com o banco; 200 |
| GET | `/api/sugestoes` | Lista sugestões, da mais recente para a mais antiga; aceita filtros combináveis `status` e `categoria`; 200 |
| GET | `/api/sugestoes/{id}` | Consulta uma sugestão; 200 |
| POST | `/api/sugestoes` | Cria com `titulo`, `descricao` e `categoria`; `status` opcional; 201, registro criado e cabeçalho `Location` |
| PUT | `/api/sugestoes/{id}` | Edita um ou mais campos entre `titulo`, `descricao`, `categoria` e `status`; 200, registro atualizado |
| DELETE | `/api/sugestoes/{id}` | Exclui a sugestão e seus comentários; 204, sem corpo |
| GET | `/api/sugestoes/{id}/comentarios` | Lista comentários, do mais antigo para o mais recente; 200 |
| POST | `/api/sugestoes/{id}/comentarios` | Adiciona comentário com `autor` e `texto`; 201, comentário criado |
| POST | `/api/sugestoes/{id}/votos` | Sem corpo; acrescenta um voto e devolve `{"id":1,"votos":1}` como exemplo; 200 |
| POST | `/api/sugestoes/sugerir-categoria` | Etapa 4: recebe apenas `titulo` e `descricao`, consulta o Jev e devolve a categoria sugerida sem gravar dados; 200 |
| POST | `/api/sugestoes/sugerir-resumo` | Etapa 4: recebe apenas `titulo` e `descricao`, consulta o provedor de geração de texto e devolve o resumo sugerido sem gravar dados; 200 |

Na etapa 4, `POST /api/sugestoes` e `PUT /api/sugestoes/{id}` também aceitarão `resumo`. No cadastro, sua ausência resulta em `null`; na edição, omitir o campo preserva o valor e enviar `null` remove o resumo. O `PUT` aceitará apenas os campos a alterar e exigirá pelo menos um campo.

Erros de entrada, como campos desconhecidos, filtros inválidos, JSON malformado ou textos vazios, terão HTTP 400 com `{"erro":"mensagem"}`. Registros e rotas inexistentes sob `/api/` terão HTTP 404 no mesmo formato. As operações com corpo exigirão um objeto JSON e `Content-Type: application/json`.

Quando o banco não responder, `/health` terá HTTP 503. Cada rota de IA terá 503 para chave ausente/acesso recusado, indisponibilidade ou limite de uso do provedor, 504 para tempo limite e 502 para resposta inválida, sempre com a chave `erro`. A falha de uma integração não impedirá o uso da outra nem o cadastro manual.

Exemplo de resposta planejada de `/api/sugestoes/sugerir-categoria`:

```json
{
  "categoria_sugerida": "interface"
}
```

Exemplo de resposta planejada de `/api/sugestoes/sugerir-resumo`:

```json
{
  "resumo_sugerido": "Adicionar uma opção de tema escuro para melhorar o uso em ambientes com pouca luz."
}
```

Cada resultado será exibido para confirmação. As chamadas de IA não criarão nem atualizarão uma sugestão automaticamente.

## Estrutura planejada

Os arquivos serão criados gradualmente, na etapa correspondente:

```text
sugestoes-produto/
├── backend/
│   ├── __init__.py
│   ├── app/
│   │   ├── __init__.py             # cria a aplicação
│   │   ├── config.py               # configuração por ambiente
│   │   ├── extensions.py           # banco e migrações
│   │   ├── models.py               # sugestão e comentário
│   │   ├── validation.py           # campos e filtros
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   └── sugestoes.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── sugestoes.py        # regras, consultas e votos
│   │       ├── sugestao_categoria.py # classificação com Jev, na etapa 4
│   │       └── sugestao_resumo.py    # geração de texto, na etapa 4
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_sugestoes.py
│   │   ├── test_regras.py
│   │   ├── test_sugestao_categoria.py
│   │   └── test_sugestao_resumo.py
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/                       # etapa 5
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── migrations/                     # primeira versão na etapa 2
├── .env.example
├── .gitignore
├── PLANO.md
└── README.md
```

## Roteiro de implementação

1. Definir o contrato e preparar Flask, PostgreSQL e `/health`.
2. Criar modelos, migrações e rotas de sugestões, comentários e votos.
3. Testar, investigar uma falha pelos logs e corrigi-la com teste de regressão.
4. Integrar a classificação pelo Jev e o resumo por uma API de geração de texto; migrar o campo opcional de resumo.
5. Criar a interface, completar a documentação e revisar a entrega.

Os entregáveis e critérios de conclusão de cada etapa estão no [PLANO.md](PLANO.md).
