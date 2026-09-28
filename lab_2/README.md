# Лабораторна робота 2: stateless request flow

## Реалізований сценарій

Ключовим бізнес-сценарієм обрано життєвий цикл замовлення:

```text
POST /api/v1/orders/ -> GET /api/v1/orders/{id}
-> PATCH /api/v1/orders/{id} -> GET /api/v1/orders/{id}
```

Кожна відповідь містить заголовок `X-Instance-ID`. Він показує, який
екземпляр backend обробив запит.

### Вхідний контекст

- cookie `access_token` містить JWT з `sub` (email користувача) і `type=access`;
- тіло `POST` містить дані замовлення;
- `PATCH` містить `order_id` у URL та змінені поля замовлення;
- gateway не додає sticky session або instance-specific cookie.

### Читання shared context

`get_current_user` декодує JWT, після чого читає користувача з PostgreSQL.
Операції замовлення щоразу читають актуальний рядок `orders` через SQLAlchemy.
JWT не містить копії бізнес-стану замовлення.

### Атомарні зміни

`create_order`, `update_order` і `delete_order` виконують зміну та `commit` в
одній SQLAlchemy-сесії. Наступний запит читає результат із PostgreSQL, а не з
пам'яті конкретного процесу.

### Відсутність залишкової пам'яті

Backend не має глобального кешу замовлень або mutable singleton для request
context. Змінні `order`, `current_user` і `order_in` живуть лише в межах
обробника запиту; після завершення запиту стан знаходиться у PostgreSQL.

## Multi-instance розгортання

`infrastructure/docker-compose.yml` містить один сервіс `backend`. Дві replicas
цього сервісу запускаються параметром Compose `--scale`, тому обидва контейнери
використовують єдину збірку та спільну мережеву адресу `backend`. Nginx
направляє запити до `backend_pool` без sticky sessions.

`INSTANCE_ID` не задається вручну: backend використовує hostname контейнера.
Compose генерує різний hostname для кожної replica, а middleware повертає його
як `X-Instance-ID`.

Запуск:

```bash
cd infrastructure
docker compose up --build --scale backend=2 -d
docker compose exec backend alembic upgrade head
```

## Cross-instance consistency

Перед запуском переконайтеся, що зареєстрований тестовий користувач не потрібен:
скрипт створює одноразовий email. Потрібні Python 3.13 та `httpx` із dev-залежностей
backend.

```bash
cd ..
uv run python lab_2/resilience_test.py --base-url http://localhost
```

У виводі мають бути різні значення `X-Instance-ID` хоча б для частини запитів,
а фінальний `GET` має повернути title `Updated on shared storage`. Це доводить,
що `POST` і `PATCH` не залишили стан тільки в одному процесі.

## Restart / instance loss

Сценарій можна виконати автоматично:

```bash
uv run python lab_2/resilience_test.py \
  --base-url http://localhost \
  --stop-instance "$(docker compose -f infrastructure/docker-compose.yml ps -q backend | head -n 1)"
```

Скрипт виконує `docker stop` для однієї replica, після чого повторює `GET`
через той самий gateway. Інша replica читає той самий рядок PostgreSQL і
повертає оновлений title. Для відновлення зупиненого сервісу:

```bash
docker compose -f infrastructure/docker-compose.yml up --scale backend=2 -d
```

Критерії успіху:

1. `X-Instance-ID` є у кожній API-відповіді.
2. Після `POST → GET → PATCH → GET` дані однакові незалежно від instance.
3. Після зупинки одного instance другий обробляє `GET`.
4. У PostgreSQL зберігається один актуальний бізнес-стан без локального кешу.
