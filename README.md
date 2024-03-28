### start backend
```bash
docker-compose up --build
docker-compose -f docker-compose.yaml exec backend alembic --config app/alembic.ini upgrade head
```

### start frontend
```bash
cd frontend/
npm i
npm run dev
```

### build frontend
```bash
npm run build
```
