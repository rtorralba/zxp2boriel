@echo off
echo Running tests before push...
python -m pytest -q
if %ERRORLEVEL% neq 0 (
  echo Tests failed. Push aborted.
  exit /b %ERRORLEVEL%
)
echo Tests passed. Proceeding with push.
exit /b 0
