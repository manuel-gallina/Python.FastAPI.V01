![Banner](./docs/logo/logo.svg)

# FastAPI Template V1

Template project for FastAPI applications.

## Tests

Automated tests are implemented with pytest, and are organized in three levels:

- Unit tests: single functions; every external dependency is mocked;
- Integration tests: single endpoints; databases and external services are mocked;
- Acceptance tests: single or multiple endpoints; databases and external services are not mocked.

## Pipeline

CI/CD pipeline is implemented using Dagger.

### Examples of Dagger calls

- Run tests<br>`dagger call test`
- Publish Docker image<br>
  `dagger call publish-docker-image --token cmd://"op read op://employee/github/dagger/password"`
- Export OpenAPI schema<br>`dagger call export-openapi-schema -o .`

## Databases

Because databases are usually managed externally, all the schema definitions and migrations that
are implemented in this project are meant to be used for autocompletion during development
and to set up testing databases.

For production, the database schema should be managed with dedicated tools.

## Docs

### Diagrams

Diagrams are implemented with PlantUML, and are located under the `docs/diagrams` folder.
To edit and generate diagrams, you should use the PlantUML extension for
VSCode (see the [marketplace page](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml)),
which allows you to edit and generate diagrams directly from the editor.

# More

For further details, see the [docs page](./docs/index.md).
