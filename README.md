![Banner](./docs/logo/logo.svg)

# Python.FastAPI.V1

Template project for FastAPI.

## Pipeline

CI/CD pipeline is implemented using Dagger.

### Tests

```powershell
dagger call test
```

### Publish

```powershell
dagger call publish --token cmd://"op read op://employee/github/dagger/password"
```