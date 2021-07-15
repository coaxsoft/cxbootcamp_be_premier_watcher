FROM python-3.8-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
		build-essential \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        python3-cffi \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        shared-mime-info \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN cd /app
RUN mkdir /static
RUN export PIPENV_DONT_USE_PYENV=1

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

ENTRYPOINT ["./entrypoint.sh"]
