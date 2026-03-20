# Working on issues

When you are working on an issue, you should:

1. Create specs files with openspec.
2. Write tests first, based on the specs.
3. Implement the feature to make the tests pass.
4. Make small commits as you work.
5. Run all tests to ensure nothing is broken.
6. Run code formatting and linting checks.
7. Update OpenAPI specs by running `dagger call -q export-openapi-schema -o .` if the API has changed
8. Commit the changes and push the current branch.
9. Open a pull request with
   `gh pr create -t "<issue_number> - <short_description>" -B main -F <path_to_spec_file_for_this_change>`.