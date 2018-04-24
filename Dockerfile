FROM python:3.6-slim

RUN pip install --upgrade pip \
    && pip install pipenv \
    && find / | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf \
    && rm -rf /root/.cache/pip

WORKDIR /opt

COPY . .

CMD ["bash", "run-test.sh"]

