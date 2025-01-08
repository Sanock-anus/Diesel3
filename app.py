from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import get_db, close_db
from models import User, Game, Purchase

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'zip', 'rar', '7z'}  # Допустимые расширения для игр
ALLOWED_IMG_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key'  # Заменить на реальный ключ
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename, allowed_extensions):
    """Проверяет, является ли расширение файла допустимым."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/')
def index():
  """Главная страница, отображает список игр."""
  with get_db() as db:
    games = db.execute('SELECT * FROM games').fetchall()
    close_db(db)
    return render_template('index.html', games = games)


@app.route('/game/<int:game_id>')
def game_details(game_id):
  """Страница с деталями игры."""
  with get_db() as db:
      game = db.execute('SELECT games.*, users.username FROM games INNER JOIN users ON games.publisher_id = users.id WHERE games.id = ?', (game_id,)).fetchone()
      close_db(db)
      return render_template('game.html', game=game)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации пользователя."""
    if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']
      if not username or not password:
         flash('Пожалуйста, заполните все поля', 'error')
         return render_template('register.html')

      hashed_password = generate_password_hash(password)
      try:
        with get_db() as db:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            db.commit()
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('login'))
      except Exception as e:
         flash('Произошла ошибка при регистрации', 'error')
         return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа пользователя."""
    if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']
      if not username or not password:
         flash('Пожалуйста, заполните все поля', 'error')
         return render_template('login.html')
      with get_db() as db:
        user_data = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        close_db(db)
      if user_data and check_password_hash(user_data['password'], password):
         session['user_id'] = user_data['id']
         session['username'] = user_data['username']
         flash('Вы успешно вошли!', 'success')
         return redirect(url_for('index'))
      else:
        flash('Неверное имя пользователя или пароль', 'error')
        return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Выход пользователя из системы."""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('index'))

def is_logged_in():
    """Проверяет, вошел ли пользователь в систему."""
    return 'user_id' in session

def get_current_user():
    """Возвращает текущего пользователя, если он вошел в систему."""
    if is_logged_in():
      with get_db() as db:
        user_data = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        close_db(db)
      return User(user_data['id'], user_data['username'], user_data['password'])
    return None

@app.route('/upload_game', methods=['GET','POST'])
def upload_game():
  """Страница загрузки игр, доступна только авторизованным пользователям."""
  if not is_logged_in():
    flash('Требуется авторизация!', 'error')
    return redirect(url_for('login'))

  if request.method == 'POST':
    if 'file' not in request.files:
      flash('Не выбран файл!', 'error')
      return render_template('upload_game.html')
    if 'image' not in request.files:
      flash('Не выбрано изображение!', 'error')
      return render_template('upload_game.html')
    file = request.files['file']
    image = request.files['image']
    title = request.form['title']
    description = request.form['description']
    genre = request.form['genre']
    price = request.form['price']
    if not file or not title or not description or not genre or not price or not image:
      flash('Заполните все поля', 'error')
      return render_template('upload_game.html')

    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
       filename = secure_filename(file.filename)
       file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
       file.save(file_path)
    else:
        flash('Неверный формат файла!', 'error')
        return render_template('upload_game.html')
    if image and allowed_file(image.filename, ALLOWED_IMG_EXTENSIONS):
       image_name = secure_filename(image.filename)
       image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
       image.save(image_path)
    else:
        flash('Неверный формат изображения', 'error')
        return render_template('upload_game.html')

    with get_db() as db:
      publisher_id = get_current_user().id
      db.execute('INSERT INTO games (title, description, genre, publisher_id, file_path, image_path, price) VALUES (?, ?, ?, ?, ?, ?, ?)', (title, description, genre, publisher_id, file_path, image_path, price))
      db.commit()
    flash('Игра успешно загружена', 'success')
    return redirect(url_for('index'))
  return render_template('upload_game.html')


@app.route('/buy_game/<int:game_id>', methods = ['POST'])
def buy_game(game_id):
  """Обрабатывает покупку игры."""
  if not is_logged_in():
    flash('Требуется авторизация!', 'error')
    return redirect(url_for('login'))
  user_id = get_current_user().id
  with get_db() as db:
    db.execute('INSERT INTO purchases (user_id, game_id) VALUES (?, ?)', (user_id, game_id))
    db.commit()
  flash('Вы успешно приобрели игру', 'success')
  return redirect(url_for('index'))

@app.route('/download_game/<int:game_id>')
def download_game(game_id):
    """Обрабатывает скачивание игры, доступно только после покупки."""
    if not is_logged_in():
        flash('Требуется авторизация!', 'error')
        return redirect(url_for('login'))
    user_id = get_current_user().id
    with get_db() as db:
       purchase = db.execute('SELECT * FROM purchases WHERE user_id = ? AND game_id = ?', (user_id, game_id)).fetchone()
       game = db.execute('SELECT * FROM games WHERE id = ?', (game_id,)).fetchone()
       close_db(db)
       if purchase and game:
         file_path = game['file_path']
         return send_file(file_path, as_attachment=True)
       else:
        flash('Вы не приобретали игру', 'error')
        return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)