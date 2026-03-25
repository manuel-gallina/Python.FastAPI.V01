# Working on issues

When you are working on an issue, you should (in order):

1. Create specs files with openspec (if not present yet).
2. Write tests first, based on the specs.
3. Implement the feature to make the tests pass; make small commits as you work.
4. Run all tests to ensure no regression was introduced.
5. Run code formatting and linting checks.
6. Update OpenAPI specs by running `dagger call -q export-openapi-schema -o .` if the API has changed.
7. Push the current branch.
8. Open a pull request with
   `gh pr create -t "<current_issue_branch_name>" -B main -F <path_to_spec_file_for_this_change>`.
9. You will be told via prompt, if the PR checks have passed or not; if not, fix the issues and push again until all
   checks pass.
10. After everything is done, review and update the `.claude/CLAUDE.md` file with new findings and insights from the
    issue you just worked on, so that it can be helpful for future reference.