# Plano de implementação — Sugestões de Produto

Este plano organiza a implementação de Sugestões de Produto em **cinco etapas**: base executável, dados e API, testes e manutenção, integração de IA e interface com revisão final. O objetivo é entregar uma aplicação para registrar propostas, acompanhar seu andamento e reunir comentários e votos.

**Organização das entregas:** cada etapa reúne atividades, critérios de conclusão e referências técnicas. As alterações devem ser registradas em commits pequenos e submetidas à revisão, com as verificações necessárias para demonstrar o comportamento entregue.

**Tecnologias:** Python, Flask, Flask-SQLAlchemy/SQLAlchemy, PostgreSQL local, psycopg, Flask-Migrate/Alembic, python-dotenv, pytest, React, TypeScript e Vite. A classificação de categorias utilizará TypeSafe AI, com System One/Jev. A geração de resumos utilizará uma API de geração de texto, com provedor a definir. Os testes automatizados usarão SQLite temporário e respostas simuladas das duas integrações.

## Escopo e decisões iniciais

- Cadastrar, listar, consultar, editar e excluir sugestões; filtrar por status e categoria.
- Adicionar e consultar comentários, mantendo duas tabelas relacionadas: `sugestoes` e `comentarios`.
- Registrar votos com um contador inteiro na sugestão, iniciado em zero. Cada chamada à rota de votação acrescenta um voto; não haverá identificação de votantes nem limite por pessoa nesta versão.
- Sugerir categoria pelo Jev e resumo curto por uma API de geração de texto, em operações independentes e com confirmação antes de salvar. O cadastro manual funciona sem as integrações de IA.
- Criar uma interface web para os fluxos de cadastro e acompanhamento. Autenticação, perfis, notificações, anexos e uma tabela própria de votos ficam fora deste escopo.

O contrato planejado da API, os campos e os valores permitidos estão no [README.md](README.md). As referências abaixo são caminhos relativos à raiz do repositório `chamados-suporte`.

## 1. Definição e base executável

**Objetivo:** transformar o contrato planejado em uma base Flask que inicia e se conecta a um banco próprio.

**Atividades**

- Conferir os campos, as rotas e as regras do README antes de escrever os modelos.
- Criar a estrutura inicial `backend/app`, a função `create_app`, a configuração por ambiente e as extensões de banco e migrações.
- Preparar `.venv`, dependências da aplicação e de desenvolvimento, `.gitignore` e `.env.example`, utilizando as tecnologias definidas neste plano.
- Criar o usuário PostgreSQL `sugestoes_app` e o banco `sugestoes_produto` no servidor local já instalado. Usar variáveis `SUGESTOES_DB_USER`, `SUGESTOES_DB_PASSWORD`, `SUGESTOES_DB_NAME`, `SUGESTOES_DB_HOST` e `SUGESTOES_DB_PORT`.
- Implementar `GET /health`, verificando também a conexão com o banco: HTTP 200 quando acessível e 503 quando indisponível.
- Registrar no README os comandos validados para instalar, configurar e iniciar a aplicação.

**Critério de conclusão:** seguindo o README em um ambiente novo, a API inicia e `/health` devolve `{"status":"ok","database":"ok"}` com HTTP 200 usando o PostgreSQL deste projeto. A falha de conexão também tem resposta previsível.

**Aspectos técnicos:** pacotes Python, ambiente virtual, variáveis de ambiente, função de criação da aplicação e o caminho de uma requisição até o banco.

**Referências:** `backend/app/__init__.py`, `backend/app/config.py`, `backend/app/extensions.py`, `backend/app/routes/health.py`, `backend/requirements*.txt` e `.env.example`.

## 2. Modelos relacionais, API REST e votos

**Objetivo:** entregar o fluxo principal de sugestões e comentários, acrescentando a regra de votação.

**Atividades**

- Criar os modelos `Sugestao` e `Comentario`, com chave estrangeira, campos obrigatórios, datas, status e categorias permitidos.
- Criar a primeira migração e aplicá-la em um PostgreSQL vazio. Incluir restrições de status, categoria e votos não negativos no banco.
- Implementar criação, listagem, consulta, atualização e exclusão de sugestões, além dos filtros combináveis por status e categoria.
- Implementar adição e consulta de comentários. Ao excluir uma sugestão, remover seus comentários em cascata; não permitir comentário para uma sugestão inexistente.
- Implementar `POST /api/sugestoes/{id}/votos`. Incrementar o contador diretamente no banco, numa operação atômica: duas requisições não devem sobrescrever o incremento uma da outra. O cliente não escolhe o valor de `votos` no cadastro ou na edição.
- Validar JSON, campos obrigatórios, limites de texto, valores vazios e campos desconhecidos. Devolver erros 400/404 no formato `{"erro":"mensagem"}`.
- Organizar as rotas, a validação e o serviço de sugestões em módulos com responsabilidades definidas.

**Critério de conclusão:** a API permite cadastrar, filtrar, consultar, editar, comentar, votar e excluir sugestões. Duas chamadas de votação aumentam o contador em dois. A exclusão remove os comentários, os erros seguem o contrato e as migrações recriam o esquema em um banco vazio.

**Aspectos técnicos:** classes e relacionamentos no SQLAlchemy, consultas, integridade referencial, restrições do banco, métodos HTTP e atualização de um contador.

**Referências:** `backend/app/models.py`, `backend/app/validation.py`, `backend/app/services/chamados.py`, `backend/app/routes/chamados.py` e `migrations/versions/`.

## 3. Testes, logs e investigação de uma falha

**Objetivo:** validar as regras da API e estabelecer procedimentos de diagnóstico e correção de falhas.

**Atividades**

- Criar testes com pytest e o cliente de testes do Flask, usando um SQLite temporário diferente por teste e habilitando as chaves estrangeiras.
- Cobrir o fluxo de sugestões, filtros combinados, edição, comentários, votos e exclusão. Verificar lista vazia, dados inválidos, registros inexistentes e tentativas de escrever campos controlados pelo servidor.
- Testar as restrições relacionais e a cascata, além das validações da API. Confirmar o isolamento do banco de testes.
- Investigar uma falha reproduzível: registrar a requisição, observar a resposta e os logs, escrever um teste que falha antes da correção e corrigir a causa. Um cenário a verificar é a resposta de `/api/sugestoes/invalido`: o retorno de HTML viola o contrato que exige JSON. Esse cenário deverá ser verificado durante a implementação.
- Registrar método e caminho nos logs úteis ao diagnóstico, sem incluir credenciais ou parâmetros de consulta. Refatorar o trecho envolvido e revisar o diff.
- Conferir manualmente as migrações e o fluxo principal no PostgreSQL; a suíte SQLite não comprova o comportamento específico desse banco nem a concorrência da votação.

**Critério de conclusão:** a suíte passa; uma falha documentada possui teste de regressão, que evita seu retorno; as restrições estão cobertas e os logs ajudam a explicar a correção. A migração foi conferida no PostgreSQL.

**Aspectos técnicos:** fixtures, testes de rotas e regras, leitura de erros, logs, refatoração e revisão de código.

**Referências:** `backend/tests/conftest.py`, `backend/tests/test_chamados.py`, `backend/tests/test_regras.py` e o tratamento de 404 em `backend/app/__init__.py`.

## 4. Categoria e resumo por IA

**Objetivo:** integrar a classificação de categorias pelo Jev e a geração de resumos por um segundo provedor, com validação no backend e revisão antes de salvar.

**Atividades**

- Criar um serviço de classificação que recebe título e descrição e consulta o Jev, usando a integração existente como referência. Usar uma pergunta do tipo `Choice` com as categorias permitidas e validar a opção retornada. O Jev retorna decisões, probabilidades e confiança; não gera o texto do resumo. [Documentação da TypeSafe](https://docs.typesafe.ai/introduction).
- Selecionar uma API de geração de texto com faixa gratuita para o resumo e criar um serviço separado. Gemini e GroqCloud são candidatos; o provedor e o modelo serão definidos antes da integração. Conferir os limites vigentes da conta e o contrato da API escolhida.
- Expor `POST /api/sugestoes/sugerir-categoria`, devolvendo `categoria_sugerida`, e `POST /api/sugestoes/sugerir-resumo`, devolvendo `resumo_sugerido`. As duas rotas recebem apenas título e descrição, sem consultar ou alterar sugestões no banco.
- Restringir a categoria à lista do README e o resumo a um texto não vazio de até 300 caracteres. Orientar o modelo de geração de texto a resumir a entrada sem acrescentar informações; validar a resposta no backend e deixá-la para revisão da pessoa.
- Adicionar `resumo` opcional à sugestão por uma nova migração. Aceitar seu envio no cadastro e na edição; `null` permite deixá-lo ausente ou removê-lo. Preservar as sugestões já cadastradas.
- Configurar `TYPESAFE_API_KEY` e a credencial do provedor de resumos apenas no backend, de forma independente. Tratar chave ausente/acesso recusado, indisponibilidade e limite de uso do provedor com 503, tempo limite com 504 e resposta inválida com 502, sempre no formato de erro da API.
- Testar cada integração com respostas simuladas: categoria fora da lista, resumo inválido, falhas e ausência de cada chave. Verificar que as rotas de IA não gravam dados, que a falha de um provedor não bloqueia a outra operação e que o cadastro manual continua disponível.

**Critério de conclusão:** cada rota devolve um resultado válido quando seu provedor está disponível, os erros são previsíveis e nenhuma sugestão é salva automaticamente. Classificação, resumo e cadastro manual funcionam de forma independente. Os testes não fazem chamadas externas. A nova migração funciona tanto num banco novo quanto num banco com sugestões existentes; a verificação de chamadas reais requer as respectivas chaves configuradas no ambiente.

**Aspectos técnicos:** classificação probabilística, geração de texto, serviços externos independentes, configuração, validação de respostas, testes com mocks e evolução do banco por migração.

**Referências:** `backend/app/services/sugestao_categoria.py`, `backend/tests/test_sugestao_categoria.py` e `backend/app/config.py`, para a classificação com Jev; [geração de texto com Gemini](https://ai.google.dev/gemini-api/docs/text-generation) e [geração de texto com GroqCloud](https://console.groq.com/docs/text-chat), para avaliação do provedor de resumos.

## 5. Interface, documentação e revisão final

**Objetivo:** disponibilizar os fluxos pela interface e preparar uma entrega reproduzível e documentada.

**Atividades**

- Criar uma tela em React com TypeScript e Vite para cadastrar, listar, filtrar, consultar, editar e excluir sugestões, além de comentar e votar.
- Oferecer ações independentes para sugerir categoria e gerar resumo, permitindo adotar ou editar cada resultado antes de salvar. Mostrar mensagens de carregamento, lista vazia, sucesso e erro.
- Usar o proxy local do Vite para encaminhar `/api` e `/health` ao Flask, como em Chamados de Suporte.
- Atualizar o README com a árvore real, comandos de instalação e execução, configuração do banco, migrações, testes, compilação da interface e exemplos de requisição.
- Conferir o fluxo completo pela interface, com cada provedor de IA disponível e indisponível, e executar a suíte do backend e `npm run build`.
- Revisar commits e abrir um pull request com problema, comportamento entregue e validações. Reproduzir a execução a partir de um clone limpo.
- Documentar a preparação para deploy: variáveis no servidor, migrações, logs, arquivos estáticos e encaminhamento das rotas para a API. Escolher hospedagem e publicar poderá ser uma atividade posterior.

**Critério de conclusão:** os fluxos principais funcionam pela interface, os testes e a compilação passam, o README permite reproduzir a execução e o pull request está pronto para revisão. A documentação descreve o fluxo React → Flask → SQLAlchemy → PostgreSQL e a integração de IA.

**Aspectos técnicos:** consumo de API, tipos TypeScript, estados da interface, Git/GitHub e documentação.

**Referências:** `frontend/src/App.tsx`, `frontend/src/api.ts`, `frontend/vite.config.ts`, `frontend/package.json` e a documentação de execução e deploy no `README.md` de Chamados de Suporte.

## Acompanhamento das entregas

Cada etapa deve ser desenvolvida em uma branch, com commits pequenos e instruções de verificação registradas no README. A revisão deve incluir o diff ou pull request, os resultados das verificações e eventuais questões técnicas pendentes. A etapa seguinte começa após o atendimento dos critérios de conclusão.

- [ ] Etapa 1 — Base Flask e PostgreSQL verificada.
- [ ] Etapa 2 — Sugestões, comentários e votos pela API.
- [ ] Etapa 3 — Testes, diagnóstico e correção documentados.
- [ ] Etapa 4 — IA revisável e migração do resumo.
- [ ] Etapa 5 — Interface, documentação e revisão final.

**Resultado esperado:** aplicação com API, banco relacional, interface web, testes automatizados e documentação de execução. O contador de votos deve preservar os incrementos, e a geração de categoria e resumo por IA deve funcionar como um recurso opcional, sujeito à confirmação antes da gravação.
