
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

