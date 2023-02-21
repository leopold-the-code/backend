## Spinning up database

### With docker (for local development)

0. Run database container:

```bash
docker run --name localdb -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres
```

1. Configure app settings - Copy file `example.env` and save it as `.env`
2. Run migrations `aerich upgrade`

## App Installation

0. Clone and cd to repo

```bash
git clone https://github.com/leopold-the-code/backend.git
cd backend
```

Then you can do local or docker installation

### Local installation

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

### Docker installation

1. Build image

```bash
docker build -t backend .
```

2. Run container

```bash
docker run --rm -it -p 80:80 backend
```

Now server is running on http://127.0.0.1:8080/
With swagger on http://127.0.0.1:8080/docs
