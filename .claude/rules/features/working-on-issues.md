# Working on issues

When you are working on an issue, you should:

1. Create specs files with openspec.
2. Write tests first, based on the specs.
3. Implement the feature to make the tests pass.
4. Run all tests to ensure nothing is broken.
5. Run code formatting and linting checks.
6. Update OpenAPI specs by running `dagger call -q export-openapi-schema -o .` if the API has changed
7. Commit the changes and push the current branch.
8. Open a pull request with
   `gh pr create -t "<issue_number> - <short_description>" -B main -F <path_to_spec_file_for_this_change>`.