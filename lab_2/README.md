# Лабораторна робота 2: stateless request flow

## Аудит стану

| Категорія | Знайдений стан | Рішення |
|---|---|---|
| Ephemeral / Local Safe | Локальні змінні обробника та ORM-об'єкти | Тимчасовий контекст одного запиту; не кешується між запитами |
| Ephemeral / Local Safe | SQLAlchemy connection pool, S3 SDK session | Технічні ресурси процесу, не зберігають бізнес-дані |
| Ephemeral / Local Safe | Логи та буфер байтів при upload фото | Діагностика й короткоживучий payload; файли зберігаються в S3 |
| Shared / Externalized | Бізнес-сутності, зокрема користувачі, замовлення, рахунки, маршрути | PostgreSQL — shared primary storage |
| Shared / Externalized | Фото доставки | SeaweedFS через S3 API |
| Shared / Externalized | Авторизаційний контекст | Підписані JWT у клієнтських cookies; однаковий секрет конфігурації для всіх реплік |
| Critical Stateful Dependencies | Глобальні mutable business collections/cache, локальні блокування/лічильники, файлові сесії | Не виявлені в `backend/app`; стан не прив'язаний до пам'яті репліки |

Глобальні `order_service`/`user_service`/`s3_client` — stateless фасади або
технічні клієнти, не сховища бізнес-стану. Таблиці з переходами та наборами
дозволених типів файлів є незмінною конфігурацією. Пул з'єднань локальний для
процесу, але не є кешем даних; читання та зміни бізнес-даних виконуються через
спільне сховище.

Схема з двома backend-репліками, gateway та shared storage наведена в
кореневому [`README.md`](../README.md).

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
пам'яті конкретного процесу. Для сценарію оновлення одного замовлення зміна
рядка фіксується транзакцією PostgreSQL до відправлення відповіді.

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

Запуск у PowerShell:

```powershell
Set-Location .\infrastructure
docker compose up --build --scale backend=2 -d
docker compose exec backend alembic upgrade head
```

For local testing over `http://localhost`, set `COOKIE_SECURE=False` in
`infrastructure/.env.backend` before starting the backend. Secure cookies are
not sent over plain HTTP. Keep `COOKIE_SECURE=True` when serving the app over
HTTPS.

If Alembic reports `Can't locate revision`, the database points to a migration
that is not present in the current checkout. Restore that migration or recreate
the database only if its contents can be discarded; do not use `stamp head` to
hide a schema mismatch.

## Cross-instance consistency

Перед запуском переконайтеся, що зареєстрований тестовий користувач не потрібен:
скрипт створює одноразовий email. Потрібні Python 3.13 та `httpx` із dev-залежностей
backend. From the repository root, run:

```powershell
uv run --project .\backend --group dev python .\lab_2\resilience_test.py --base-url http://localhost
```

Скрипт перевіряє, що `POST` і наступний `GET` виконали різні instances, так само
як `PATCH` і фінальний `GET`. Він завершується помилкою, якщо не може довести
cross-instance читання або якщо фінальний title не відповідає оновленню.

Ручний cURL-приклад (Bash; потрібен `jq`) використовує один cookie jar для JWT.
`-i` показує `X-Instance-ID` у кожній відповіді:

```bash
API=http://localhost/api/v1
EMAIL="lab2-$(date +%s)@example.com"
PHONE="+38099$(printf '%06d' "$(( (RANDOM * 32768 + RANDOM) % 1000000 ))")"

curl -i -c cookies.txt -b cookies.txt "$API/auth/register" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"password123\",\"full_name\":\"Lab 2 Client\",\"role\":\"client\",\"phone_number\":\"$PHONE\"}"

curl -i -c cookies.txt -b cookies.txt "$API/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"password123\"}"

created=$(curl -sS -D /dev/stderr -c cookies.txt -b cookies.txt "$API/orders/" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Stateless flow","weight":10,"distance":50}')
ORDER_ID=$(printf '%s' "$created" | jq -r .id)

curl -i -b cookies.txt "$API/orders/$ORDER_ID"
curl -i -b cookies.txt -X PATCH "$API/orders/$ORDER_ID" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Updated on shared storage"}'
curl -i -b cookies.txt "$API/orders/$ORDER_ID"
```

Порівняйте `X-Instance-ID` у послідовних відповідях і перевірте фінальне тіло
відповіді на оновлений `title`. Для автоматичної перевірки різних instance ID
використовуйте скрипт вище: він завершується помилкою, якщо create/read або
update/read не пройшли через різні репліки.

## Restart / instance loss

Сценарій можна виконати автоматично:

```powershell
$instance = docker compose -f .\infrastructure\docker-compose.yml ps -q backend | Select-Object -First 1
uv run --project .\backend --group dev python .\lab_2\resilience_test.py --base-url http://localhost --stop-instance $instance
```

Скрипт визначає hostname контейнера, виконує `docker stop`, після чого
повторює `GET` через той самий gateway. Інша replica має повернути оновлений
title з PostgreSQL. Після перевірки скрипт запускає зупинений контейнер знову,
навіть якщо перевірка failover завершилася помилкою. Для ручного відновлення:

```powershell
docker compose -f .\infrastructure\docker-compose.yml up -d --scale backend=2 backend
```

Критерії успіху:

1. `X-Instance-ID` є у кожній API-відповіді.
2. Після `POST → GET → PATCH → GET` дані однакові незалежно від instance.
3. Після зупинки одного instance другий обробляє `GET`.
4. У PostgreSQL зберігається один актуальний бізнес-стан без локального кешу.
