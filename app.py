from flask import Flask,render_template, url_for, flash, redirect, request
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

db = pymysql.connect("localhost","root","","project_db_2")

print("Connected to database !")

def records_needed_in_layout():
	posts = []
	data = sql_show_bookmark()
	for item in data:
		temp_object = {'bookmark_id':item[0],'post_title':item[1],'user_id':item[2], 'category':item[4], 'post_id':item[5],'category_id':item[6]}
		posts.append(temp_object)

	recent_posts = []
	data_recent = sql_show_recent_post();
	for item in data_recent:
		temp_recent = {'post_id':item[0],'post_title':item[1],'username':item[2], 'date':item[3], 'category':item[4],'category_id':item[5] }
		recent_posts.append(temp_recent)

	trending_post = []
	data_trends = sql_show_trending_post()
	for item in data_trends:
		temp_recent = {'post_title':item[0],'share_amount':item[1],'username':item[2], 'date':item[3], 'category':item[4], 'post_id':item[5], 'category_id':item[6]}
		trending_post.append(temp_recent)

	list=[posts,recent_posts,trending_post]

	return list

def sql_show_bookmark():
	cursor = db.cursor()
	sql= """ 
	SELECT bookmark_id,post_title , bookmark.user_id reader_id, post.author_id author_id,category.category_name, post.post_id, post.category_id
	FROM bookmark JOIN post JOIN user JOIN category
	ON bookmark.post_id=post.post_id AND bookmark.user_id=user.user_id AND category.category_id=post.category_id
	WHERE bookmark.user_id=2;
																	"""
	cursor.execute(sql)
	data = cursor.fetchall()
	return data	


def sql_filter_by_category(param): 
	cursor = db.cursor()
	sql= """ 
	SELECT post_id,user.user_username, post.post_title,post_date , category.category_name , post.post_content as content
	FROM user JOIN post JOIN category 
	ON user.user_id=post.author_id AND category.category_id=post.category_id
	WHERE post.category_id=%s ORDER BY post_date desc;
																	"""
	args = (param,)
	cursor.execute(sql,args)
	data = cursor.fetchall()

	return data


def sql_show_recent_post():
	cursor = db.cursor()
	sql= """ 
	SELECT post.post_id, post.post_title, user.user_username, post_date, category.category_name, post.category_id
	FROM post JOIN user JOIN category
	ON user.user_id=post.author_id AND category.category_id=post.category_id
	ORDER BY post_date DESC LIMIT 3;
																	"""
	cursor.execute(sql)
	data = cursor.fetchall()
	return data	

def sql_show_trending_post():
	cursor = db.cursor()
	sql= """ 
	SELECT post.post_title, post.total_share, user.user_username, post_date, category.category_name, post.post_id, post.category_id
	FROM post JOIN user JOIN category
	ON user.user_id=post.author_id AND category.category_id=post.category_id
	ORDER BY total_share DESC LIMIT 3;
																	"""
	cursor.execute(sql)
	data = cursor.fetchall()
	return data

def sql_insert_bookmark(post_id,user_id):
	cursor = db.cursor()
	sql= """insert into bookmark(post_id,user_id) values(%s,%s);"""
	args = (post_id,user_id)
	cursor.execute(sql,args)
	db.commit()
	
def sql_delete_bookmark(post_id,user_id):
	cursor = db.cursor()
	sql = """delete from bookmark where post_id=%s and user_id=%s;"""
	args = (post_id,user_id)
	cursor.execute(sql,args)
	db.commit()


@app.route("/")
@app.route("/home/")
def home():
	cursor = db.cursor()
	list = records_needed_in_layout()
   	author_post=[]
	bookmark_posts = list[0]
	recent_posts = list[1]
	data_trends = list[2]
	sql=""" 
		SELECT post.post_id,author_id,user.user_username,post_title,post_date,category_name,post.post_content
		FROM user JOIN post JOIN category 
		ON user.user_id=post.author_id AND post.category_id=category.category_id 
		WHERE author_id=2 ORDER BY post_date DESC;
													"""

	cursor.execute(sql)
	data = cursor.fetchall()

	for item in data:
		temp_object = {'post_id':item[0],'author_id':item[1],'username':item[2],'title':item[3], 'date':item[4],'category':item[5],'content':item[6]}
		author_post.append(temp_object)

	return render_template('home.html',bookmark_posts=bookmark_posts ,
							recent_posts=recent_posts, data_trends=data_trends,
							bookmark_status = True, author_post=author_post , username=item[2]
							)

@app.route("/search_res")
def search_res():
	return("404 not found")


@app.route("/insert_bookmark/<int:post_id>",methods=['GET', 'POST'])
def insert_bookmark(post_id):
	cursor = db.cursor()
	sql_insert_bookmark(post_id,2)
	flash('Post Bookmarked !', 'success')
	return redirect(url_for('home'))


@app.route("/delete_bookmark/<int:post_id>/<int:user_id>",methods=['GET', 'POST'])
def delete_bookmark(post_id,user_id):
	cursor = db.cursor()
	sql_delete_bookmark(post_id,user_id)
	flash('Bookmark deleted !', 'success')
	return redirect(url_for('home'))


@app.route("/category=<string:c_name>=<int:c_id>")
def category_list(c_name,c_id):
	
	cursor = db.cursor()
	posts = []

	list = records_needed_in_layout()
	bookmark_posts = list[0]
	recent_posts = list[1]
	data_trends = list[2]

	try:
   # Execute the SQL commands
		data = sql_filter_by_category(c_id)
		for item in data:
			temp_object = {'post_id':item[0],'username':item[1],'post_title':item[2],'date_posted':item[3],'category':item[4],'content':item[5]}			
			posts.append(temp_object)		   	
	except:
   # Rollback in case there is any error
   		db.rollback()
	return render_template('each_category.html',title=c_name , posts=posts,
							bookmark_posts=bookmark_posts,recent_posts=recent_posts,
							data_trends=data_trends)

@app.route("/category=<string:c_name>=<int:c_id>/post=<int:p_id>")
def each_post(c_name,c_id,p_id):
	cursor = db.cursor()
	list = records_needed_in_layout()
	bookmark_posts = list[0]
	recent_posts = list[1]
	data_trends = list[2]
	sql = """  
		SELECT user_username, post_title, post_date , category.category_name, post_content,post.post_id
		FROM user JOIN post JOIN category 
		ON user.user_id=post.author_id AND category.category_id=post.category_id
		WHERE post.post_id=%s;
								"""
	args = (p_id,)
	try:
   # Execute the SQL commands
		cursor.execute(sql,args)
		data = cursor.fetchall()
		for item in data:
			temp_object = {'username':item[0],'post_title':item[1],'date_posted':item[2],'category':item[3],'content':item[4],'post_id':item[5]}
	except:
   # Rollback in case there is any error
   		db.rollback()
	return render_template('each_post.html',data_post=temp_object,bookmark_posts=bookmark_posts,
							recent_posts=recent_posts, data_trends=data_trends)

if __name__ == '__main__':
	app.run(debug=True)