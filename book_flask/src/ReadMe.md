
``` 
flask app --debug  
```
```
pyinstaller --onefile \
  --add-data "templates:templates" \
  --add-data "static:static" \
  app.py

cp dist/app ../flask_server/

```
# book_flask


```bash
````
```bash
cd book_flask/src

pip install pyinstaller

pyinstaller --onefile \
  --add-data "templates:templates" \
  --add-data "static:static" \
  app.py
  
  cp dist/app ../../flask_server/
  cd ../../flask-book-app/
  npm run make

```

