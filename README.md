# hirehub

## Running Tests

To run the tests for the Applicant Tracking System (ATS) application, navigate to the root directory of the project (where the `manage.py` file for the `hirehub` Django project is located) and use the following command:

```bash
python hirehub/manage.py test ats
```

This command will discover and run all tests within the `ats` application.

Alternatively, to run all tests in the entire Django project (if there were other apps), you can use:

```bash
python hirehub/manage.py test
```

## CI with GitHub Actions

This project includes a Continuous Integration (CI) workflow using GitHub Actions, located in the file `.github/workflows/django-ci.yml`.

This workflow automatically triggers on every `push` to the `main` branch and on any `pull_request` targeting the `main` branch.

The CI pipeline performs the following steps:
1.  Checks out the repository code.
2.  Sets up a specified Python environment (e.g., Python 3.10).
3.  Installs project dependencies from `requirements.txt`.
4.  Runs the Django test suite for the `ats` application using the command `python hirehub/manage.py test ats`. The tests are configured to use SQLite in the CI environment.

This ensures that code merged into the main branch or proposed via pull requests is automatically tested, helping to maintain code quality and stability.
</tbody>
