# OpenAPI

### Устанавка необходимых компонентов

```commandline
sudo apt install python3.9
sudo apt install python3-pip
sudo pip3 install flask
sudo pip3 install sqlalchemy
```

### Запуск
Вводим в терминале `python3 app.py`

### Тесты
Запускаем программу (если она была не запущена)
Вводим в терминале `python3 tests.py`

### Зависимости
- `Flask` - фреймворк для создания WEB приложений. На основе его был создан этот REST сервис
- `SqlAlchemy` - библиотека для описания реляционных бд.
  В ней я использую модели для удобства взаимодействия 
  с таблицами sqlite
  