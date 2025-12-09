
```bash 
flask app --debug  
```
```bash
pyinstaller --onefile \
  --add-data "templates:templates" \
  --add-data "static:static" \
  app.py

cp dist/app ../flask_server/
```

# book_flask


```bash
rmdir ./out/

cd book_flask/src

pip install pyinstaller

pyinstaller --onefile \
  --add-data "templates:templates" \
  --add-data "static:static" \
  app.py

cp dist/app ../../flask_server/
cd ../..
npm run make

```

```bash
docker-compose down && docker-compose up --build -d

docker commit book_flask taylormyers01/book_flask

docker buildx build -t taylormyers01/book_flask --platform linux/amd64,linux/arm64 .

docker push taylormyers01/book_flask
```

** Linux-server **
```bash
docker pull taylormyers01/book_falsk

docker run -d --restart unless-stopped -p 5000:5000 taylormyers01/book_flask
```

