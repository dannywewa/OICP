python run.py typecheck
python run.py lint
python run.py test -v --suite all
coverage run --source=webthing --branch .\run.py test
coverage report
set cov_file="htmlcov\index.html"
if exist %cov_file% del %cov_file%
coverage html
start htmlcov\index.html