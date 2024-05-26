# Реалізація інформаційного та програмного забезпечення

В рамках проєкту розробляється:
## SQL-скрипт для створення на початкового наповнення бази даних

```sql
-- CreateEnum
CREATE TYPE "task_status" AS ENUM ('completed', 'in_progress');

CREATE TYPE "project_status" AS ENUM ('completed', 'in_progress');

CREATE TYPE "developer_status" AS ENUM ('online', 'offline');

-- CreateTable
CREATE TABLE "users" (
    "id" SERIAL NOT NULL,
    "username" VARCHAR(30) NOT NULL,
    "email" VARCHAR(40) NOT NULL,
    "password" VARCHAR(50),
    "fullname" VARCHAR(40),

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "task" (
    "id" SERIAL NOT NULL,
    "project_id" INTEGER NOT NULL,
    "description" VARCHAR(200) NOT NULL,
    "status" "task_status" NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "price" VARCHAR(50) NOT NULL,

    CONSTRAINT "tasks_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "project"(
    "id" SERIAL NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "developers" VARCHAR(250) NOT NULL,
    "status" "project_status" NOT NULL,

    CONSTRAINT "project_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "developers" (
    "user_id" INTEGER NOT NULL,
    "task_id" INTEGER NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "status" "developer_status" NOT NULL
);

-- CreateTable
CREATE TABLE "role" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(50) NOT NULL,

    CONSTRAINT "roles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "members" (
    "id" SERIAL NOT NULL,
    "roles_id" INTEGER NOT NULL,
    "users_id" INTEGER NOT NULL,
    "project_id" INTEGER NOT NULL,

    CONSTRAINT "members_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_login_key" ON "users"("username");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "project_name_key" ON "project"("name");

-- CreateIndex
CREATE UNIQUE INDEX "developers_name_key" ON "developers"("name");

-- CreateIndex
CREATE UNIQUE INDEX "developers_user_id_task_id_key" ON "developers"("user_id", "task_id");

-- CreateIndex
CREATE UNIQUE INDEX "members_roles_id_users_id_project_id_key" ON "members"("roles_id", "users_id", "project_id");


-- AddForeignKey
ALTER TABLE "developers" ADD CONSTRAINT "developers_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "developers" ADD CONSTRAINT "developers_task_id_fkey" FOREIGN KEY ("task_id") REFERENCES "task"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "task" ADD CONSTRAINT "task_task_id_fkey" FOREIGN KEY ("project_id") REFERENCES "project"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "members" ADD CONSTRAINT "members_roles_id_fkey" FOREIGN KEY ("roles_id") REFERENCES "role"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "members" ADD CONSTRAINT "members_users_id_fkey" FOREIGN KEY ("users_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "members" ADD CONSTRAINT "members_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "project"("id") ON DELETE CASCADE ON UPDATE CASCADE;
```

## RESTfull система управління проектами
``` python
from flask import Flask
from flask import request, jsonify
from module import Project

app = Flask(__name__)
project = Project()

@app.route("/project/all", methods=["GET"])
def get_all_projects():
    result =project.get_all_projects()
    return jsonify(result), 200

@app.route("/project/<id>", methods=["GET"])
def get_project(id):
    result =project.get_project(id)
    return jsonify(result), 200

@app.route("/project/add", methods=["POST"])
def add_project():
    data = request.get_json()
    result =project.add_project(data)
    return jsonify(result), 200

@app.route("/project/update", methods=["PATCH"])
def update_project():
    data = request.get_json()
    result =project.update_project(data)
    return jsonify(result), 200

@app.route("/project/delete/<id>", methods=["DELETE"])
def delete_project(id):
    result =project.delete_project(id)
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)
```
``` python
import psycopg


class Project:
    def __init__(self):
        try:
            self.connection = psycopg.connect(
                dbname="DB_Lesia",
                user="postgres",
                password="22032005",
                host="localhost",
                port="5432"
            )
            print("Connection to database established successfully!")
            self.cursor = self.connection.cursor()
        except psycopg.Error as error:
            print("Failed to connect to the database:", str(error))

    def get_all_projects(self):
        try:
            self.cursor.execute("SELECT * FROM project")
            result = self.cursor.fetchall()
            if not result:
                return {"message": "There are no projects", "error": "Not Found", "status_code": 404}
            return {"data": result, "status_code": 200}
        except psycopg.Error as error:
            return {"message": str(error), "error": "Database Error", "status_code": 500}

    def get_project(self, id):
        if not str(id).isdigit():
            return {"message": "Invalid project id", "error": "Bad Request", "status_code": 400}
        try:
            self.cursor.execute("SELECT * FROM project WHERE id = %s", (id,))
            result = self.cursor.fetchone()
            if not result:
                return {"message": f"There is no project with id {id}", "error": "Not Found", "status_code": 404}
            return {"data": result, "status_code": 200}
        except psycopg.Error as error:
            return {"message": str(error), "error": "Database Error", "status_code": 500}

    def add_project(self, data):
        required_keys = {'id', 'name', 'developers', 'status'}
        if not required_keys.issubset(data):
            return {"message": "Invalid or missing keys", "error": "Bad Request", "status_code": 400}
        try:
            query = "INSERT INTO project (id, name, developers, status) VALUES (%s, %s, %s, %s)"
            values = (data['id'], data['name'], data['developers'], data['status'])
            self.cursor.execute(query, values)
            self.connection.commit()
            if self.cursor.rowcount > 0:
                return {"message": "Project added successfully", "status_code": 200}
            else:
                return {"message": "Project wasn't added to database", "error": "Not Acceptable", "status_code": 406}
        except psycopg.Error as error:
            self.connection.rollback()
            return {"message": "Add project failed: " + str(error), "error": "Database Error", "status_code": 500}

    def update_project(self, data):
        if 'id' not in data:
            return {"message": "No project id provided", "error": "Bad Request", "status_code": 400}
        project_id = data.pop('id')
        if not data:
            return {"message": "No data provided", "error": "Bad Request", "status_code": 400}
        set_clause = ', '.join([f"{key} = %s" for key in data])
        values = list(data.values())
        values.append(project_id)
        try:
            query = f"UPDATE project SET {set_clause} WHERE id = %s"
            self.cursor.execute(query, values)
            self.connection.commit()
            if self.cursor.rowcount > 0:
                return {"message": "Project updated successfully", "status_code": 200}
            else:
                return {"message": "Project wasn't updated", "error": "Not Found", "status_code": 404}
        except psycopg.Error as error:
            self.connection.rollback()
            return {"message": "Project update failed: " + str(error), "error": "Database Error", "status_code": 500}

    def delete_project(self, id):
        if not str(id).isdigit():
            return {"message": "Invalid project id", "error": "Bad Request", "status_code": 400}
        try:
            self.cursor.execute("DELETE FROM project WHERE id = %s", (id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                return {"message": "Project deleted successfully", "status_code": 200}
            else:
                return {"message": "Nothing to delete", "error": "Not Found", "status_code": 404}
        except Exception as error:
            self.connection.rollback()
            return {"message": "Delete project failed", "error": str(error), "status_code": 500}

```

