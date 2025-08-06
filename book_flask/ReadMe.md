
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
# flask-book-app
