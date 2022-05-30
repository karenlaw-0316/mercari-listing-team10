import os
import logging
import pathlib
import json
import sqlite3
import hashlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile, Body
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Union, List
from imgProcess import removeBackground, addBackground
from addSampleData import add_sample_data

DATABASE_PATH = "./db/mercari.sqlite3"
SCHEMA_PATH = "./db/schema.db"
ERR_MSG = "ERROR"
image_dir = pathlib.Path(__file__).parent.resolve() / "db" / "image"
mask_dir = pathlib.Path(__file__).parent.resolve() / "db" / "mask"

logger = logging.getLogger("uvicorn")
logger.setLevel(os.environ.get('LOGLEVEL', 'DEBUG').upper())

try:
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    logger.info("Connected to database.")
except Exception as e:
    logger.error(f"Failed to connect to database. Error message: {e}")

app = FastAPI()

origins = [os.environ.get('FRONT_URL', 'http://localhost:3000')]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


@app.on_event("startup")
def init_database():
    try:
        cur = conn.cursor()
        with open(SCHEMA_PATH) as schema_file:
            schema = schema_file.read()
            logger.debug("Read schema file.")
        cur.executescript(f'''{schema}''')
        add_sample_data(conn)
        conn.commit()
        logger.info("Completed database initialization.")
    except Exception as e:
        logger.warn(f"Failed to initialize database. Error message: {e}")

@app.get("/")
def root():
    return {"message": "Hello, world!"}


@app.get("/items")
def get_items():
    logger.info("Received get_items request.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT items.id, items.name, category.name as category, items.image_filename, items.user_id
            FROM items INNER JOIN category
            ON category.id = items.category_id
        ''')
        items = cur.fetchall()
        item_list = [dict(item) for item in items]
        items_json = {"items": item_list}
        logger.info("Returning all items.")
        return items_json
    except Exception as e:
        logger.warn(f"Failed to get items. Error message: {e}")
        return ERR_MSG


@app.get("/items/{item_id}")
def get_item(item_id: int):
    logger.info(f"Received get_item request of item id: {item_id}.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT items.id, items.name, category.name as category, items.image_filename, items.user_id
            FROM items INNER JOIN category
            ON category.id = items.category_id
            WHERE items.id = (?)
        ''', (item_id, ))
        item_result = cur.fetchone()
        if (item_result is None):
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(f"Returning the item of id: {item_id}.")
        return item_result
    except HTTPException:
        logger.info("Failed to get item: Item not found")
        return "Item not found"
    except Exception as e:
        logger.warn(f"Failed to get item. Error message: {e}")
        return ERR_MSG


@app.delete("/items/{item_id}")
def get_item(item_id: int):
    logger.info(f"Received delete_item request of item id: {item_id}.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''SELECT name FROM items WHERE id = (?)''', (item_id, ))
        item_result = cur.fetchone()
        if (item_result is None):
            raise HTTPException(status_code=404, detail="Item not found")
        cur.execute('''DELETE FROM items WHERE id = (?)''', (item_id, ))
        conn.commit()
        logger.info(f"Deleted item {item_result[0]} of id: {item_id}.")
        return {"message": f"Deleted item {item_result[0]} of id: {item_id}."}
    except HTTPException:
        logger.info("Failed to delete item: Item not found")
        return "Item not found"
    except Exception as e:
        logger.warn(f"Failed to get item. Error message: {e}")
        return ERR_MSG


@app.post("/items")
async def add_item(name: str = Form(..., max_length=32),
                   category: str = Form(..., max_length=12),
                   image: list[UploadFile] = File(...),
                   user_id: int = 1,
                   oneliner_description: str = Form(..., max_length=100),
                   detailed_description: str = Form(..., max_length=200),
                   price: int = Form(...)):
    logger.info(f"Received add_item request.")
    logger.info(image[0].content_type)

    for file in image:
        if file.content_type == "image/jpeg":
            file_extension = ".jpg"
        elif file.content_type == "video/mp4":
            file_extension = ".mp4"
        elif file.content_type == "video/quicktime":
            file_extension = ".mp4"
        else:
            raise HTTPException(
                400, detail="Image not in jpg format or video not in mp4 format.")

    try:
        cur = conn.cursor()
        new_image_names = []
        for file in image:
            image_binary = await file.read()
            new_image_name = hashlib.sha256(
                image_binary).hexdigest() + file_extension
            new_image_names.append(new_image_name)
            image_path = image_dir / new_image_name
            with open(image_path, 'wb') as image_file:
                image_file.write(image_binary)

        cur.execute(
            '''SELECT id FROM category WHERE name = (?)''', (category, ))
        category_result = cur.fetchone()
        if (category_result is None):
            cur.execute(
                '''INSERT INTO category(name) VALUES (?)''', (category, ))
            cur.execute(
                '''SELECT id FROM category WHERE name = (?)''', (category, ))
            category_result = cur.fetchone()

        cur.execute('''INSERT INTO items(name, category_id, image_filename, user_id, oneliner_description, detailed_description, price) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (name, category_result[0], new_image_names[0], user_id, oneliner_description, detailed_description, price))

        # cur.execute(f'''INSERT INTO files(file1) VALUES(?)''',
        #             (new_image_names[0]))
        # for i in range(2, len(new_image_names)+1):
        #     cur.execute(
        #         f'''UPDATE files SET file{i}={new_image_name[i-1]} WHERE file1={new_image_names[0]}''')
        if (len(new_image_names) == 1):
            cur.execute(f'''INSERT INTO files(file1) VALUES(?)''',
                        (new_image_names[0], ))
        if (len(new_image_names) == 2):
            cur.execute(f'''INSERT INTO files(file1, file2) VALUES(?, ?)''',
                        (new_image_names[0], new_image_names[1]))
        if (len(new_image_names) == 3):
            cur.execute(f'''INSERT INTO files(file1, file2, file3) VALUES(?, ?, ?)''',
                        (new_image_names[0], new_image_names[1], new_image_names[2]))
        if (len(new_image_names) == 4):
            cur.execute(f'''INSERT INTO files(file1, file2, file3, file4) VALUES(?, ?, ?, ?)''',
                        (new_image_names[0], new_image_names[1], new_image_names[2], new_image_names[3]))
        if (len(new_image_names) == 5):
            cur.execute(f'''INSERT INTO files(file1, file2, file3, file4, file5) VALUES(?, ?, ?, ?, ?)''',
                        (new_image_names[0], new_image_names[1], new_image_names[2], new_image_names[3], new_image_names[4]))
        conn.commit()

        logger.info(
            f"Item {name} of {category} category is added into database.")
        return {"message": f"Item {name} of {category} category is received."}
    except Exception as e:
        logger.warn(f"Failed to add item. Error message: {e}")
        return ERR_MSG


@ app.get("/search")
def search_item(keyword: str):
    logger.info(f"Received search_item request of search keyword: {keyword}.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT items.id, items.name, category.name as category, items.image_filename, items.user_id
            FROM items INNER JOIN category
            ON category.id=items.category_id
            WHERE items.name LIKE(?)
        ''', (f"%{keyword}%", ))
        items = cur.fetchall()
        item_list = [dict(item) for item in items]
        items_json = {"items": item_list}
        logger.info(f"Returning items with name containing {keyword}.")
        return items_json
    except Exception as e:
        logger.warn(f"Failed to search items. Error message: {e}")
        return ERR_MSG


@ app.get("/image/{image_filename}")
async def get_image(image_filename: str):
    logger.debug(f"API endpoint get_image is called.")
    # Create image path
    image = image_dir / image_filename

    # if not image_filename.endswith(".jpg"):
    #     raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.info(f"Image not found: {image}")
        image = image_dir / "default.jpg"

    return FileResponse(image)


@ app.post("/login")
def user_login(username: str = Form(...), password: str = Form(...)):
    logger.info(f"Received user_login request.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''SELECT id FROM user WHERE username=(?) AND hashed_password=(?)''',
                    (username, hashlib.sha256(password.encode()).hexdigest()))
        login_result = cur.fetchone()
        if (login_result is None):
            raise HTTPException(detail="Username or password not correct.")
        logger.info(f"Returning the user id: {login_result[0]}.")
        return login_result
    except Exception as e:
        logger.warn(f"Failed to login user. Error message: {e}")
        return ERR_MSG


@ app.get("/user-external-history/{user_id}")
def get_user_external_history(user_id: int):
    logger.info("Received get_user_external_history request.")
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''SELECT * FROM user WHERE id=(?)''', (user_id, ))
        user_result = cur.fetchone()
        if (user_result is None):
            raise HTTPException(status_code=404, detail="User not found")
        cur.execute('''
            SELECT
            external_purchase_history.id as historyId,
            external_purchase_history.name as itemName,
            external_purchase_history.image_filename as imageFilename,
            source.name as sourceName,
            external_purchase_history.price
            FROM
            external_purchase_history INNER JOIN source
            ON
            external_purchase_history.source_id=source.id
            WHERE
            external_purchase_history.user_id=(?)
            LIMIT 5
        ''', (user_id, ))
        items = cur.fetchall()
        item_list = [dict(item) for item in items]
        items_json = {"purchased items": item_list}
        logger.info("Returning up to 5 external purchased items.")
        return items_json
    except HTTPException:
        logger.info(
            "Failed to get user external purchase history: User not found")
        return "User not found"
    except Exception as e:
        logger.warn(
            f"Failed to get user external purchase history. Error message: {e}")
        return ERR_MSG


@ app.get("/external-history/{history_id}")
def get_external_history(history_id: int):
   logger.info("Received get_external_history request.")
   try:
       conn.row_factory = sqlite3.Row
       cur = conn.cursor()
       cur.execute('''
           SELECT
           external_purchase_history.name as itemName,
           external_purchase_history.image_filename as imageFilename,
           source.name as sourceName,
           external_purchase_history.oneliner_description,
           external_purchase_history.detailed_description,
           external_purchase_history.price
           FROM
           external_purchase_history INNER JOIN source
           ON
           external_purchase_history.source_id=source.id
           WHERE
           external_purchase_history.id=(?)
       ''', (history_id, ))
       item_result = cur.fetchone()
       if (item_result is None):
           raise HTTPException(status_code=404, detail="Item not found")
       logger.info(
           f"Returning the external purchased item of id: {history_id}")
       return item_result
   except HTTPException:
       logger.info("Failed to get external purchased item: Item not found")
       return "Item not found"
   except Exception as e:
       logger.warn(
           f"Failed to get external purchase history. Error message: {e}")
       return ERR_MSG


@app.get("/categories")
def get_categories():
   logger.info("Received get_categories request.")
   try:
       conn.row_factory = sqlite3.Row
       cur = conn.cursor()
       cur.execute('''
           SELECT id, name FROM category
       ''')
       categories = cur.fetchall()
       category_list = [dict(category) for category in categories]
       categories_json = {"categories": category_list}
       logger.info("Returning all categories.")
       return categories_json
   except Exception as e:
       logger.warn(f"Failed to get categories. Error message: {e}")
       return ERR_MSG


@ app.on_event("shutdown")
def disconnect_database():
    try:
        conn.close()
        logger.info("Disconnected database.")
    except Exception as e:
        logger.error(f"Failed to disconnect database. Error message: {e}")


@ app.post("/edit")
def edit_image(
        R: int,
        G: int,
        B: int,
        image: str = Body(...),
        background_id: int = 0,
        x: int = 0,
        y: int = 0,
        w: int = 0,
        l: int = 0
):

    image_filename = hashlib.sha256(image.encode("utf-8")).hexdigest() + '.jpg'

    logger.info(f"Processing {image_filename}")
    logger.info(f"w:{w}, l:{l}")

    if w != 0 and l != 0:
        removeBackground(image, image_filename, x, y, w, l)

    color = [R,G,B]
    res = addBackground(image, image_filename, color, background_id)
    return res

@app.delete("/edit")
def delete_edited_image(image_filename: str):

    mask_img = "./db/mask/mask_" + image_filename
    if os.path.exists(mask_img):
        os.remove(mask_img)
        return {f"Remove {mask_img}"}

    return {f"{mask_img} does not exist"}
