# Working on issues

When you are working on an issue, you should:

1. Write tests first, based on the specs.
2. Implement the feature to make the tests pass.
3. Run all tests to ensure nothing is broken.
4. Run code formatting and linting checks.
5. Update OpenAPI specs by running `dagger call -q export-openapi-schema -o .` if the API has changed
6. Commit the changes and push the current branch.
7. Open a pull request to `main` with a clear description of the changes.