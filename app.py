#git
from flask import Flask, render_template,request,session,redirect,flash,url_for,flash, jsonify

from config import Database
import os

app = Flask(__name__)

app.secret_key = 'your_secret_key'
# Initialize Database
db = Database()


import re

# List of common stop words to exclude from hashtags
stop_words = {'and', 'the', 'in', 'on', 'with', 'without', 'for', 'is', 'to', 'a', 'of', 'by', 'this', 'that'}

import re

# List of common stop words to exclude from hashtags
stop_words = {'and', 'the', 'in', 'on', 'with', 'without', 'for', 'is', 'to', 'a', 'of', 'by', 'this', 'that'}

def create_hashtags(text_list):
    # Initialize an empty list to store all hashtags
    all_hashtags = []

    for text in text_list:
        # Initialize an empty list to store hashtags for the current text
        hashtag_list = []

        # Split the text into words
        words = text.split()

        for word in words:
            # Clean the word by removing non-alphanumeric characters
            cleaned_word = re.sub(r'\W+', '', word)

            # Convert to lowercase and ensure the word isn't in the stop_words list
            if cleaned_word.lower() not in stop_words and cleaned_word:
                # Create a hashtag and add it to the list
                hashtag_list.append(f"#{cleaned_word.capitalize()}")

        # If any hashtags were created, add them to the main list
        if hashtag_list:
            all_hashtags.extend(hashtag_list)

    # Return the final list of all hashtags
    print(f"this is all hash tags:{all_hashtags}")
    return all_hashtags




#Guest Block

@app.route("/")
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    categories=db.fetchall(f"""select * from tbl_category""")
    try:
        
        login_id = session.get('user_id')
        if login_id:
            try:
                query = f"""
                SELECT r.*, c.*, l.*,
                CASE WHEN f.favourite_recipe_id IS NOT NULL THEN 'true' ELSE 'false' END AS status,
                COALESCE(AVG(rw.rating), 0) AS average_rating
                FROM tbl_recipe r
                INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
                INNER JOIN tbl_login l ON r.recipe_login_id = l.login_id
                LEFT JOIN tbl_favourite f ON r.recipe_id = f.favourite_recipe_id 
                                AND f.favourite_login_id = {login_id}
                                AND f.status = 'true'
                LEFT JOIN tbl_review rw ON rw.review_recipe_id = r.recipe_id
                WHERE r.status= 1
                GROUP BY r.recipe_id, c.category_id, l.login_id
                ORDER BY r.recipe_id DESC
                """
                recipes = db.fetchall(query)
            except Exception as e:   
                flash(f"Failed: {str(e)}", "danger")
                print(f"exeption 123:{e}")
                print(f"this is recipes:{recipes}")
    
        else:
            query = f"""
                SELECT r.*, c.*, l.*, 
                    COALESCE(AVG(rw.rating), 0) AS average_rating
                FROM tbl_recipe r
                INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
                INNER JOIN tbl_login l ON r.recipe_login_id = l.login_id
                LEFT JOIN tbl_review rw ON r.recipe_id = rw.review_recipe_id
                WHERE r.status = 1
                GROUP BY r.recipe_id, c.category_id, l.login_id
                ORDER BY r.recipe_id DESC
            """
            recipes = db.fetchall(query)
    except Exception as e:   
                flash(f"Failed: {str(e)}", "danger")
                print(f"exeption 123:{e}")
                print(f"this is recipes:{recipes}")

    return render_template('guest/index.html',categories=categories, recipes= recipes)

@app.route('/about')
def about():
    return render_template('guest/about.html')

@app.route('/menu')
def menu():
    return render_template('guest/menu.html')

@app.route('/feedback', methods= ["GET","POST"])
def feedback():
    if request.method == "POST":
        login_id = request.form['user_id']
        name= request.form['name']
        feedback = request.form['feedback']
        email = request.form['email']
        try:
            query = f"""
                        INSERT INTO feedback (login_id, name, email, feedback, created_on)
                        VALUES ({login_id}, '{name}', '{email}', '{feedback}', NOW())
                        """
            db.execute(query)
        except Exception as e:   
            flash(f"Failed: {str(e)}", "danger")
            print(f"exeption :{e}")

    return redirect(url_for('home'))

    

@app.route('/view-recipe', methods=["GET"])
def viewrecipe():
   
    try:
        # Fetching recipe descriptions, ingredients, and titles
        description_text = db.fetchall(f"""
            SELECT recipe_description, ingredients, recipe_title 
            FROM tbl_recipe
        """)

        # Combine description, ingredients, and title into a single list
        combined_content_list = [
            f"{item['recipe_title']} {item['ingredients']} {item['recipe_description']}" 
            for item in description_text
        ]

        # Generate hashtags from the combined content
        hash_tags = create_hashtags(combined_content_list)

        # Debug print for combined content and hashtags
        print(f"Combined Content List: {combined_content_list}")
        print(f"Generated Hashtags: {hash_tags}")

    except Exception as e:
        flash(f"Failed: {str(e)}", "danger")
        print(f"Exception: {e}")
    
    try:
        
        login_id = session.get('user_id')
        if login_id:
            try:
                query = f"""
                SELECT r.*, c.*, l.*,
                CASE WHEN f.favourite_recipe_id IS NOT NULL THEN 'true' ELSE 'false' END AS status,
                COALESCE(AVG(rw.rating), 0) AS average_rating
                FROM tbl_recipe r
                INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
                INNER JOIN tbl_login l ON r.recipe_login_id = l.login_id
                LEFT JOIN tbl_favourite f ON r.recipe_id = f.favourite_recipe_id 
                                AND f.favourite_login_id = {login_id}
                                AND f.status = 'true'
                LEFT JOIN tbl_review rw On rw.review_recipe_id = r.recipe_id
                WHERE r.status= 1
                GROUP BY r.recipe_id, c.category_id, l.login_id
                ORDER BY r.recipe_id DESC
                """
                recipes = db.fetchall(query)
            except Exception as e:   
                flash(f"Failed: {str(e)}", "danger")
                print(f"exeption 123:{e}")
                print(f"this is recipes:{recipes}")
    
        else:
            query = f"""
                SELECT r.*, c.*, l.*, 
                    COALESCE(AVG(rw.rating), 0) AS average_rating
                FROM tbl_recipe r
                INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
                INNER JOIN tbl_login l ON r.recipe_login_id = l.login_id
                LEFT JOIN tbl_review rw ON r.recipe_id = rw.review_recipe_id
                WHERE r.status = 1
                GROUP BY r.recipe_id, c.category_id, l.login_id
                ORDER BY r.recipe_id DESC
            """
            
           
            recipes = db.fetchall(query)
    except Exception as e:   
                flash(f"Failed: {str(e)}", "danger")
                print(f"exeption 123:{e}")
                print(f"this is recipes:{recipes}")
    print(f"this is recipes last: {recipes}")
    print(f"this is hash tags: {hash_tags}")
    return render_template('guest/view-recipe.html',recipes=recipes, hash_tags=hash_tags)

@app.route('/search-recipe', methods=["GET"])
def searchrecipe():
    try:
        search_value = request.args.get('search')
        login_id = session.get('user_id')
        recipes = []  # Initialize recipes list

        if search_value:
            # Split the search value into words and create a pattern for each word
            search_words = search_value.strip().split()
            # Create conditions where each word must match in any of the fields
            search_conditions = " AND ".join(
                [f"(LOWER(r.recipe_title) LIKE LOWER('%{word}%') OR LOWER(r.recipe_description) LIKE LOWER('%{word}%') OR LOWER(r.ingredients) LIKE LOWER('%{word}%'))" for word in search_words]
            )

            if login_id:
                query = f"""
                    SELECT r.*, c.*, l.*,
                    CASE WHEN f.favourite_recipe_id IS NOT NULL THEN 'true' ELSE 'false' END AS status
                    FROM tbl_recipe r
                    INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
                    INNER JOIN tbl_login l ON r.recipe_login_id = l.login_id
                    LEFT JOIN tbl_favourite f ON r.recipe_id = f.favourite_recipe_id 
                                AND f.favourite_login_id = {login_id}
                                AND f.status = 'true'
                    WHERE r.status = 1 AND ({search_conditions})
                """
                recipes = db.fetchall(query)
            else:
                query = f"""
                    SELECT r.*, c.*, l.* 
                    FROM tbl_recipe r
                    INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
                    INNER JOIN tbl_login l ON r.recipe_login_id = l.login_id
                    WHERE r.status = 1 AND ({search_conditions})
                """
                recipes = db.fetchall(query)

        # Return the recipes as JSON
        print(f"This is the searched recipe: {recipes}")
        return jsonify({'recipes': recipes})

    except Exception as e:   
        flash(f"Failed: {str(e)}", "danger")
        print(f"Exception occurred: {e}")
        return jsonify({'recipes': []}) 
    
    


@app.route('/add-fav', methods=["GET","POST"])
def addfav():
    try:
        check_status = None
        login_id = session.get('user_id')
        recipe_id = request.args.get('recipe_id')
        check_status =db.fetchone(f"""select status from tbl_favourite where favourite_recipe_id={recipe_id} and  favourite_login_id ={login_id}""")
        print(f"this is status {check_status}")
        if not check_status:
            print(f"this is the user ID:{login_id} ")
            print(f"this is the reipe ID:{recipe_id}")
            query = f"""
                    INSERT INTO tbl_favourite(favourite_recipe_id, favourite_login_id,status)
                    VALUES ({recipe_id}, {login_id},'true')
                    """
            db.execute(query)
          
        elif check_status['status'] == 'true':
            db.execute(f"""UPDATE tbl_favourite set status='false' where favourite_recipe_id={recipe_id} and  favourite_login_id ={login_id}""")
        elif check_status['status'] == 'false':
            print(f"this is status false")
            db.execute(f"""update tbl_favourite set status='true' where favourite_recipe_id={recipe_id} and  favourite_login_id ={login_id}""")
        
        
    except Exception as e:   
                flash(f"Failed: {str(e)}", "danger")
                print(f"exeption 123:{e}")
    return redirect(url_for('viewrecipe'))

@app.route('/user-recipes', methods=["GET"])
def userrecipes():
    try:

        login_id = session.get('user_id')
        recipes = None
        query = f"""
        SELECT * FROM tbl_recipe r
        INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
        INNER JOIN tbl_login l on r.recipe_login_id=l.login_id
        WHERE r.recipe_login_id = {login_id} 
        """
        recipes = db.fetchall(query)
    except Exception as e:   
                flash(f"Failed: {str(e)}", "danger")
                print(f"exeption 123:{e}")

    return render_template('guest/view-recipe.html',recipes=recipes, hash_tags=None)

@app.route('/fav-list', methods=["GET"])
def favlist():
    try:
        login_id = session.get('user_id')
        recipes = None
        fav_list =db.fetchall(f"""SELECT favourite_recipe_id FROM tbl_favourite WHERE favourite_login_id={login_id} AND status='true'""")
        print(f"this is fav ids: {fav_list}")
        fav_ids = ', '.join([str(fav['favourite_recipe_id']) for fav in fav_list])
        query = f"""
            SELECT r.*, c.*, l.*,
            CASE WHEN f.favourite_recipe_id IS NOT NULL THEN 'true' ELSE 'false' END AS status
            FROM tbl_recipe r
            INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
            INNER JOIN tbl_login l ON r.recipe_login_id = l.login_id
             LEFT JOIN tbl_favourite f ON r.recipe_id = f.favourite_recipe_id 
                               AND f.favourite_login_id = {login_id}
            WHERE r.recipe_id IN ({fav_ids})
        """
        recipes = db.fetchall(query)
        print(f"thsis is recipes:{recipes}")
    except Exception as e:   
        flash(f"Failed: {str(e)}", "danger")
        print(f"exeption 123:{e}")

    return render_template('guest/fav_list.html',recipes=recipes)

@app.route('/add-review', methods=["GET","POST"])
def addreview():
     reviews =None
     if request.method == "POST":
        try: 
            login_id = session.get('user_id')
            recipe_id = request.args.get('recipe_id')
            review = request.form['review']
            rating = request.form['rating']
               
            print(f"this is the user ID:{login_id} ")
            print(f"this is the reipe ID:{recipe_id}")
            query = f"""
                            INSERT INTO tbl_review(review_recipe_id, review_login_id, review, rating)
                            VALUES ({recipe_id}, {login_id},'{review}',{rating})
                            """
            db.execute(query)
            return redirect(url_for('addreview',recipe_id=recipe_id))
        except Exception as e:   
            flash(f"Failed: {str(e)}", "danger")
            print(f"exeption 123:{e}")
            
     else:
        try:
            recipe_id = request.args.get('recipe_id')
            reviews = db.fetchall(f"""SELECT r.*, u.user_name AS user_name
                            FROM tbl_review r
                            INNER JOIN tbl_user u ON u.user_login_id = r.review_login_id
                            WHERE r.review_recipe_id= {recipe_id} """)
        except Exception as e:   
            flash(f"Failed: {str(e)}", "danger")
            print(f"exeption reviews:{e}")

        return render_template('guest/review.html',reviews= reviews)

@app.route('/view-single-recipe/<id>', methods=["GET"])
def viewsinglerecipe(id):
    # Use a parameterized query to avoid SQL injection
    query = f"""
    SELECT * FROM tbl_recipe r
    INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
    INNER JOIN tbl_login l ON r.recipe_login_id = l.login_id
    WHERE r.recipe_id = '{id}'
    """
    recipes = db.fetchone(query)  

    if recipes:
        return render_template('guest/view-single-recipe.html',recipes=recipes)
    else:
        return "Recipe not found", 404

STATIC_FOLDER = 'static'
@app.route('/recipe', methods=["GET", "POST"])
def recipe():
    user_id=session['user_id']
    if request.method == "POST":
        try:
            category_id = request.form['category']
            title = request.form['title']
            details = request.form['details']
            image = request.files['image']
            link = request.form['link']
            ingredients = request.form['ingredients']
            filename = image.filename
            
            insert_recipe=f"""insert into tbl_recipe(recipe_category_id,recipe_login_id,recipe_video,recipe_title,recipe_description,recipe_image,ingredients)
            values('{category_id}','{user_id}','{link}','{title}','{details}','{filename}','{ingredients}')"""
            print(insert_recipe)
            db.execute(insert_recipe)
            # Save the image in the 'static/guest' folder instead of 'static/recipe'
            upload_folder = os.path.join(STATIC_FOLDER, 'recipe')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            full_image_path = os.path.join(upload_folder, filename)
            image.save(full_image_path)
            
        except Exception as e:
                flash(f"Failed: {str(e)}", "danger")
    
    categories=db.fetchall("select * from tbl_category")
    query = f"""
    SELECT * FROM tbl_recipe r
    INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id
    INNER JOIN tbl_login l ON l.login_id = {user_id}
    WHERE recipe_login_id ='{user_id}' ORDER BY r.recipe_id DESC
     """
    recipes = db.fetchall(query)

    return render_template('guest/recipe.html', categories=categories,recipes=recipes)

@app.route("/logout")
def logout():
    # Clear the session data
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))



@app.route("/login", methods=["GET", "POST"])
def login():
    not_fount=None
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Fetch user from the database
        query = f"SELECT * FROM tbl_login WHERE login_username = '{username}' and login_password='{password}'"
        user = db.fetchone(query)

        if user:
            session['user_id'] = user['login_id']
            session['user_name'] = user['login_username']
            # Verify the password
            if user['login_usertype']=='admin':
                session['admin'] = 'admin'
                flash("Login successful!", "success")
                return redirect(url_for('adminhome'))  
            elif user['login_usertype']=='user':
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid username or password.", "danger")
            
        else:
            flash("User not found.", "danger")
            not_fount= "true"

    return render_template("guest/login.html" ,not_found=not_fount)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            name = request.form.get('name')
            details = request.form.get('details')
            username = request.form.get('username')
            password = request.form.get('password')
            insert_login=f"""insert into tbl_login(login_username,login_password,login_usertype) values('{username}','{password}','user')"""
            insert_id=db.executeAndReturnId(insert_login)
            if insert_id:
                insert_user=f"""insert into tbl_user(user_name,user_details,user_login_id) values('{name}','{details}','{insert_id}')"""
                db.execute(insert_user)
                return redirect(url_for('login'))
        except Exception as e:
                flash(f"Failed to register: {str(e)}", "danger")
            
    return render_template("guest/register.html")


#admin Block

def checkAdmin():
    admin = session.get('admin')
    if not admin:
        return redirect(url_for('login'))

@app.route("/admin-home")
def adminhome():
    admin = checkAdmin()
    if admin:
        return admin
    try:
        query = f"""
            SELECT
                (SELECT COUNT(*) FROM tbl_recipe) AS total_recipes,
                (SELECT COUNT(*) FROM tbl_favourite) AS total_favourites,
                (SELECT COUNT(*) FROM tbl_user) AS total_users
        """
        counts = db.fetchone(query)
        print(f"this is counts:{counts}")
        query = f"""
                SELECT 
                    f.favourite_recipe_id, 
                    r.recipe_title, 
                    COUNT(f.favourite_recipe_id) AS favourite_count
                FROM tbl_favourite f
                INNER JOIN tbl_recipe r ON f.favourite_recipe_id = r.recipe_id
                WHERE f.status = 'true'
                GROUP BY f.favourite_recipe_id, r.recipe_title
            """
        favourite_counts = db.fetchall(query)
        print(f"this is favourites:{favourite_counts}")
        query = f"""
            SELECT 
                l.login_id, 
                l.login_username, 
                COUNT(r.recipe_id) AS recipe_count
            FROM tbl_recipe r
            INNER JOIN tbl_login l ON r.recipe_login_id = l.login_id
            WHERE r.status = 1 
            GROUP BY l.login_id, l.login_username
            ORDER BY recipe_count DESC
        """
        user_interactions = db.fetchall(query)
        print(f"this is user interactions:{user_interactions}")

    except Exception as e:
        print(f"exeption:{e}")
        flash(f"Failed to update category: {str(e)}", "danger") 
    
    return render_template("admin/index.html", counts = counts, favourite_counts= favourite_counts,user_interactions=user_interactions)

@app.route("/admin-category", methods=["GET", "POST"])
def admincategory():
    admin = checkAdmin()
    if admin:
        return admin
    if request.method == "POST":
        category_id = request.form.get('category_id')
        category_name = request.form['category']
        details = request.form['details']

        if category_id:  # Update operation
            try:
                update_category_query = f"""
                UPDATE tbl_category 
                SET category_name = '{category_name}', category_details = '{details}'
                WHERE category_id = {category_id}
                """
                db.execute(update_category_query)
                flash("Category updated successfully!", "success")
            except Exception as e:
                flash(f"Failed to update category: {str(e)}", "danger")
        else:  # Create operation
            try:
                insert_category_query = f"""
                INSERT INTO tbl_category (category_name, category_details) 
                VALUES ('{category_name}', '{details}')
                """
                db.single_insert(insert_category_query)
                flash("Category added successfully!", "success")
            except Exception as e:
                flash(f"Failed to add category: {str(e)}", "danger")
        
        return redirect(url_for('admincategory'))

    # Fetch all categories and the category to edit (if any)
    categories = db.fetchall("SELECT * FROM tbl_category")
    category_to_edit = None
    if 'edit' in request.args:
        category_id = request.args.get('edit')
        category_to_edit = db.fetchone(f"SELECT * FROM tbl_category WHERE category_id = {category_id}")
    
    return render_template("admin/category.html", categories=categories, category_to_edit=category_to_edit)

@app.route("/delete-category/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    admin = checkAdmin()
    if admin:
        return admin
    try:
        delete_query = f"DELETE FROM tbl_category WHERE category_id = {category_id}"
        db.execute(delete_query)
        flash("Category deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete category: {str(e)}", "danger")
    
    return redirect(url_for('admincategory'))


@app.route('/admin-recipe', methods=["GET","POST"])
def adminrecipe():
    admin = checkAdmin()
    if admin:
        return admin
    rejected=request.args.get('rejected')
    if rejected:
        query = f"""
        SELECT * FROM tbl_recipe r
        INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id inner join tbl_login l on r.recipe_login_id=l.login_id
        WHERE r.status=2"""
        recipes = db.fetchall(query)
    else:
        query = f"""
            SELECT * FROM tbl_recipe r
            INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id inner join tbl_login l on r.recipe_login_id=l.login_id
            WHERE r.status=1"""
        recipes = db.fetchall(query)

    return render_template('admin/recipe.html',recipes=recipes)

# @app.route('/admin-recipe-review', methods=["GET","POST"])
# def adminrecipereview():
    
#         query = f"""
#             SELECT * FROM tbl_recipe r
#             INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id inner join tbl_login l on r.recipe_login_id=l.login_id
#             WHERE r.status=1"""
#         recipes = db.fetchall(query)
#         return render_template('admin/show_reviews.html',recipes=recipes)

@app.route('/admin-new-recipe', methods=["GET","POST"])
def adminnewrecipe():
    admin = checkAdmin()
    if admin:
        return admin
    query = f"""
    SELECT * FROM tbl_recipe r
    INNER JOIN tbl_category c ON r.recipe_category_id = c.category_id inner join tbl_login l on r.recipe_login_id=l.login_id
    WHERE r.status=0"""
    recipes = db.fetchall(query)

    return render_template('admin/new_recipe.html',recipes=recipes)

@app.route('/approve-recipe', methods=["GET","POST"])
def approverecipe():
    admin = checkAdmin()
    if admin:
        return admin
    recipe_id = request.args.get('recipe_id')
    query = f"""UPDATE  tbl_recipe SET status=1
                 WHERE recipe_id ={recipe_id}
                      """
    db.execute(query)
    return redirect(url_for('adminnewrecipe'))

@app.route('/admin-feedback', methods=["GET","POST"])
def adminfeedback():
    admin = checkAdmin()
    if admin:
        return admin
    user=request.args.get('user')
    if user:
        query = f"""
            SELECT feedback.*, tbl_login.login_username AS name FROM feedback
            LEFT JOIN tbl_login ON tbl_login.login_id = feedback.login_id
            WHERE feedback.name ='user'
            """
        feedback = db.fetchall(query)
    else:
        query = f"""
        SELECT * FROM feedback
        WHERE login_id =0
        """
        feedback = db.fetchall(query)

    return render_template('admin/feedback.html',feedback=feedback)

@app.route('/reject-recipe', methods=["GET","POST"])
def rejectrecipe():
    admin = checkAdmin()
    if admin:
        return admin
    recipe_id = request.args.get('recipe_id')
    query = f"""UPDATE  tbl_recipe SET status=2
                 WHERE recipe_id ={recipe_id}
                      """
    db.execute(query)
    return redirect(url_for('adminnewrecipe'))

@app.route('/admin-users', methods=["GET","POST"])
def adminusers():
    admin = checkAdmin()
    if admin:
        return admin
    query = f"""
    SELECT * FROM tbl_login l
    INNER JOIN tbl_user u ON l.login_id = u.user_login_id"""
    users = db.fetchall(query)

    return render_template('admin/user.html',users=users)

STATIC_FOLDER = 'static'
@app.route('/adminaddrecipe', methods=["GET", "POST"])
def adminaddrecipe():
    admin = checkAdmin()
    if admin:
        return admin
    user_id = session['user_id']

    if request.method == "POST":

        recipe_id = request.form.get('recipe_id')
        category_id = request.form['category']
        title = request.form['title']
        details = request.form['details']
        ingredients = request.form['ingredients']
        image = request.files['image']
        link = request.form['link']
        filename = image.filename if image else ''

        # Save the image in the 'static/guest' folder instead of 'static/recipe'
        upload_folder = os.path.join(STATIC_FOLDER, 'recipe')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # if filename:
        #     print(f"Filename: {filename}")
        #     filename = os.path.join(upload_folder, filename)
        #     print(f"Filename: {filename}")
        
        full_image_path = os.path.join(upload_folder, filename)

        # Convert backslashes to forward slashes for the filename
        filename = filename.replace('\\', '/')
            
        
        # Update operation
        if recipe_id:
            try:
                if filename:
                   
                    
                    update_recipe_query = f"""
                    UPDATE tbl_recipe 
                    SET recipe_category_id = '{category_id}', recipe_login_id = '{user_id}', recipe_video = '{link}', 
                    recipe_title = '{title}', recipe_description = '{details}', recipe_image = '{filename}' , ingredients='{ingredients}'
                    WHERE recipe_id = {recipe_id}
                    """
                    image.save(full_image_path)
                else:
                    update_recipe_query = f"""
                    UPDATE tbl_recipe 
                    SET recipe_category_id = '{category_id}', recipe_login_id = '{user_id}', recipe_video = '{link}', 
                    recipe_title = '{title}', recipe_description = '{details}' , ingredients='{ingredients}'
                    WHERE recipe_id = {recipe_id}
                    """
                db.execute(update_recipe_query)
                flash("Recipe updated successfully!", "success")
            except Exception as e:
                flash(f"Failed to update recipe: {str(e)}", "danger")
        else:
            # Insert operation
            try:
                status = 1
                print(f"Filename1: {filename}")
                insert_recipe_query = f"""
                INSERT INTO tbl_recipe (recipe_category_id, recipe_login_id, recipe_video, recipe_title, recipe_description, recipe_image, ingredients, status)
                VALUES ('{category_id}', '{user_id}', '{link}', '{title}', '{details}', '{filename}', '{ingredients}', {status})
                """
                db.execute(insert_recipe_query)
                if filename:  # Save the image to the file system only if there's a filename
                    image.save(full_image_path)
                flash("Recipe added successfully!", "success")
            except Exception as e:
                flash(f"Failed to add recipe: {str(e)}", "danger")

        return redirect(url_for('adminaddrecipe'))

    # Fetch categories and recipes
    categories = db.fetchall("SELECT * FROM tbl_category")
    category_to_edit = None

    if 'edit' in request.args:
        recipe_id = request.args.get('edit')
        category_to_edit = db.fetchone(f"SELECT * FROM tbl_recipe WHERE recipe_id = {recipe_id}")

    recipes = db.fetchall("SELECT r.recipe_id, r.recipe_title, r.recipe_description, r.recipe_image, r.ingredients, r.recipe_video, c.category_name "
                          "FROM tbl_recipe r "
                          "JOIN tbl_category c ON r.recipe_category_id = c.category_id")

    return render_template("admin/addrecipe.html", categories=categories, category_to_edit=category_to_edit, recipes=recipes)

@app.route("/delete_recipe/<int:recipe_id>", methods=["POST"])
def delete_recipe(recipe_id):
    admin = checkAdmin()
    if admin:
        return admin
    try:
        delete_query = f"DELETE FROM tbl_recipe WHERE recipe_id = {recipe_id}"
        db.execute(delete_query)
        flash("Category deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete category: {str(e)}", "danger")
    
    return redirect(url_for('adminaddrecipe'))
# running application 
if __name__ == '__main__': 
    app.run(debug=True) 