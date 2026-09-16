FROM python:3.14 AS requirements-stage
WORKDIR /tmp

RUN pip install poetry poetry-plugin-export
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.14
EXPOSE 8080

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
# COPY --chmod=755 ./healthcheck.sh /code/healthcheck.sh

# HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 \
    # CMD ./healthcheck.sh
# CMD uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 1
CMD fastapi run app/main.py --port 8080