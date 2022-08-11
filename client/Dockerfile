FROM python:3.10

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m pip install requests numpy

ADD . /usr/app

WORKDIR /usr/app/

CMD ["python", "main.py"]
