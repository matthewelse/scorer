# scorer

A (reasonably flexible) scoring system for quiz nights, written in Django. Includes a big screen mode for showing on a projector etc.

Tested with Django 1.7

## Setup

```bash
$ git clone https://github.com/matthewelse/scorer
$ cd scorer
$ ./manage.py syncdb
$ ./manage.py runserver
```

* Use http://localhost:8000/scoring/bigscreen for a projector.
* Use http://localhost:8000/scoring/controls for controlling the big screen
* Use the normal Django Admin for configuring things and setting scores.
