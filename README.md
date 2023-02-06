## Local installation

1. Install `poetry` for python dependencies management

```bash
pip install poetry
```

2. Activate virtual env and install dependencies

```bash
poetry shell
poetry install
```

3. Run the server

```bash
python -m backend
```

Now server is running on http://127.0.0.1:8000/
With swagger on http://127.0.0.1:8000/docs

## Docker installation

1. Build image

```bash
docker build -t backend .
```

2. Run container

```bash
docker run --rm -it -p 80:80 backend
```

Now server is running on http://127.0.0.1:8000/
With swagger on http://127.0.0.1:8000/docs
