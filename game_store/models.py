class User:
    """Модель пользователя."""
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class Game:
    """Модель игры."""
    def __init__(self, id, title, description, genre, publisher_id, file_path, image_path, price):
        self.id = id
        self.title = title
        self.description = description
        self.genre = genre
        self.publisher_id = publisher_id
        self.file_path = file_path
        self.image_path = image_path
        self.price = price

class Purchase:
    """Модель покупки."""
    def __init__(self, id, user_id, game_id, purchase_date):
        self.id = id
        self.user_id = user_id
        self.game_id = game_id
        self.purchase_date = purchase_date