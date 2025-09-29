from flask import Flask, request, render_template, redirect
import mysql.connector
import redis
import json
import os

app = Flask(__name__)

# Lấy config từ ENV
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DB = os.getenv("MYSQL_DB", "todo_db")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# MySQL connection
db = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = db.cursor(dictionary=True)

# Redis connection
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        task = request.form["task"]
        cursor.execute("INSERT INTO tasks (name) VALUES (%s)", (task,))
        db.commit()
        cache.delete("tasks") 
        return redirect("/")

    # Check cache
    tasks_cache = cache.get("tasks")
    if tasks_cache:
        tasks = json.loads(tasks_cache)
    else:
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        cache.set("tasks", json.dumps(tasks))

    return render_template("index.html", tasks=tasks)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
