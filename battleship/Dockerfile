FROM python:3.10

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV SECRET_KEY="django-insecure-$^2go^q94%m^oqqao74dus&k(h*hx6$!7e7uvjnqro!kn1+d4z"
ENV DEBUG=1

RUN python -m pip install django django-rest-framework numpy

ADD . /usr/app

WORKDIR /usr/app/

RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "./manage.py", "runserver", "0.0.0.0:8000", "--settings=battleship.settings"]
