# Миграции базы данных

## add_terms_accepted_at

Добавляет поле `terms_accepted_at` в таблицу `users` для хранения времени принятия условий пользования.

### Запуск миграции

```bash
# Из корневой директории backend
python -m migrations.add_terms_accepted_at
```

Или из директории проекта:

```bash
cd backend
python -m migrations.add_terms_accepted_at
```

Миграция идемпотентна - её можно запускать несколько раз, она проверит существование колонки перед добавлением.

