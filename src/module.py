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


