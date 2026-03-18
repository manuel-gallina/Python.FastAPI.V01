# Git workflow

1. Production code is maintained in the `main` branch.
2. All changes must be made on feature branches created from `main`.
3. Feature branches must be named `issues/<issue-number>-<issue-title-kebab-case>`, e.g.
   `issues/123-add-user-authentication`.
4. Merge to `main` is only allowed via pull request after passing CI checks.