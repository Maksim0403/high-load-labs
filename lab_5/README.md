# Лабораторна робота № 5

## Performance baseline та saturation testing LogiFlow

## 1. Мета роботи

Мета лабораторної роботи — дослідити продуктивність LogiFlow під ступеневим
навантаженням, порівняти read-intensive, write-intensive та complex workflow
сценарії, оцінити вплив Redis-кешу та визначити точку насичення системи.

Навантаження генерувалося декларативним скриптом k6
[`logiflow.js`](logiflow.js). Ручні запити через Postman або Swagger не
використовувалися.

## 2. Тестовий контур

Використано ізольований стек Lab 4:

| Компонент | Конфігурація |
| --- | --- |
| Load generator | k6 v2.3.0, `/home/nda/Desktop/k6` |
| Gateway | Nginx, `http://localhost:8084` |
| Backend | FastAPI, 1 instance |
| Database | PostgreSQL 17 Alpine |
| Cache | Redis 7 Alpine, 128 MB, `allkeys-lru` |
| Cache object | `GET /api/v1/orders/{id}` |
| Cache TTL | 60 секунд |
| Database pool | стандартні налаштування SQLAlchemy, `pool_size` і `max_overflow` явно не задані |
| CPU/RAM limits | не задані в Compose |

Після тестів зафіксовано snapshot контейнерів: backend — 145.5 MiB, DB —
105.1 MiB, Redis — 12.42 MiB. Це не є піковими значеннями, а лише моментним
post-run спостереженням.

## 3. Сценарії

| Сценарій | Послідовність | Ресурсний профіль |
| --- | --- | --- |
| Scenario A: Read-Intensive | login -> create seed order -> повторні detail GET | DB/Redis reads, connection pool, memory |
| Scenario B: Write-Intensive | login -> повторні POST order | PostgreSQL WAL/I/O, транзакції, locks |
| Scenario C: Complex Workflow | POST -> GET -> PATCH -> GET | змішане читання, запис, commit та cache invalidation |

Для кожного fixed-VU тесту використовувалася тривалість 15 секунд. Виміряні
рівні: 10, 50, 100 та 200 VUs. Повна таблиця результатів знаходиться у
[`results/measurements.csv`](results/measurements.csv), сирі k6 summaries — у
`results/*-*.json`.

## 4. Результати вимірювань

### 4.1. Scenario A: Read-Intensive

| Cache | VUs | RPS | Avg, ms | p50, ms | p95, ms | p99, ms | Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Disabled | 10 | 83.32 | 20.37 | 11.87 | 40.54 | 183.04 | 0.00% |
| Disabled | 50 | 174.73 | 186.84 | 132.93 | 389.08 | 1680.84 | 0.00% |
| Disabled | 100 | 163.78 | 489.02 | 215.70 | 2629.34 | 3002.66 | 3.62% |
| Disabled | 200 | 60.64 | 2316.79 | 3000.71 | 3009.77 | 3011.37 | 61.06% |
| Warm | 10 | 85.15 | 17.84 | 11.58 | 21.36 | 248.58 | 0.00% |
| Warm | 50 | 195.26 | 156.27 | 96.65 | 315.70 | 1704.90 | 0.00% |
| Warm | 100 | 201.36 | 380.98 | 184.63 | 1838.61 | 3009.25 | 2.63% |
| Warm | 200 | 59.88 | 2528.05 | 3000.93 | 3006.85 | 3009.86 | 66.52% |

Warm cache покращує throughput на 50 VUs приблизно на 11.7% та знижує p95
з 389.08 до 315.70 ms. На 100 VUs p95 зменшується з 2629.34 до 1838.61 ms,
а error rate — з 3.62% до 2.63%. На 200 VUs система вже saturated: throughput
падає приблизно до 60 RPS, а error rate перевищує 61% в обох режимах.

### 4.2. Scenario B: Write-Intensive

| VUs | RPS | Avg, ms | p50, ms | p95, ms | p99, ms | Errors |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 44.31 | 27.26 | 15.19 | 49.02 | 372.55 | 0.00% |
| 50 | 99.66 | 298.72 | 268.15 | 548.08 | 2113.55 | 0.00% |
| 100 | 106.13 | 708.49 | 353.57 | 3001.08 | 3010.81 | 7.04% |
| 200 | 66.55 | 2295.96 | 3000.81 | 3008.93 | 3014.47 | 61.07% |

Між 50 і 100 VUs throughput майже перестає зростати: 99.66 -> 106.13 RPS.
Водночас p99 збільшується до 3010.81 ms, а error rate — до 7.04%. Це
характерна ознака чергування транзакцій, lock contention або вичерпання
доступних DB connections. При 200 VUs throughput падає до 66.55 RPS.

### 4.3. Scenario C: Complex Workflow

| VUs | RPS | Avg, ms | p50, ms | p95, ms | p99, ms | Errors |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 115.95 | 32.68 | 9.65 | 29.66 | 513.81 | 0.17% |
| 50 | 191.98 | 207.38 | 137.71 | 493.03 | 1662.23 | 0.00% |
| 100 | 152.79 | 566.66 | 262.57 | 2671.43 | 3004.13 | 4.16% |
| 200 | 70.16 | 2148.85 | 3000.36 | 3005.53 | 3008.39 | 53.95% |

Workflow має найкращий throughput на 50 VUs — 191.98 RPS. На 100 VUs він
падає до 152.79 RPS, а p95 зростає більш ніж у п'ять разів: 493.03 ->
2671.43 ms. Це означає, що послідовність POST/GET/PATCH/GET накопичує черги
та помилки кожного окремого етапу.

## 5. Аналіз latency distribution

Середнє значення не описує поведінку системи під saturation. Наприклад, для
write на 100 VUs середня latency дорівнює 708.49 ms, але p99 — 3010.81 ms.
Отже, більшість запитів ще завершується швидше, але приблизно крайній 1%
потрапляє у timeout/чергу.

Найбільш показові розриви між p50 та p99:

- read disabled, 100 VUs: 215.70 -> 3002.66 ms;
- write, 100 VUs: 353.57 -> 3010.81 ms;
- workflow, 100 VUs: 262.57 -> 3004.13 ms.

Це нелінійне зростання tail latency пояснюється очікуванням DB connection,
транзакційними блокуваннями, повільним WAL/I/O та накопиченням запитів у
gateway/backend. Значення близько 3000 ms вказують на timeout або граничний
час очікування запиту.

## 6. Saturation Point

Практична точка насичення для всіх трьох профілів починається на **100 VUs**:

- throughput перестає зростати лінійно або починає падати;
- p95/p99 переходять у діапазон 1.8-3.0 секунд;
- з'являються помилки від 2.63% до 7.04%.

На **200 VUs** система перебуває у важкому saturation: throughput становить
лише 59.88-70.16 RPS, а error rate — 53.95-66.52%.

Для production-like SLO з p95 < 1000 ms та error rate < 2% максимальним
стабільним рівнем у цих тестах є приблизно **50 VUs**. Для warm read p99 уже
перевищує 1.7 секунди на 50 VUs, тому p99-SLO є суворішим за p95-SLO.

## 7. Первинний bottleneck

Найімовірніший первинний bottleneck — спільний PostgreSQL path: транзакційний
I/O, lock contention та/або очікування SQLAlchemy connection pool. Підстави:

1. Write-intensive має найгірший tail latency серед стабільних write-профілів.
2. Workflow деградує сильніше за read через послідовні записи та invalidation.
3. На 100 VUs throughput write майже не збільшується, хоча VUs подвоюються
     від 50 до 100.
4. На 200 VUs у всіх сценаріях з'являється timeout-подібна latency близько
     3 секунд.

Redis зменшує DB-read навантаження, але не усуває auth lookup, записи та
транзакційні блокування. Тому cache покращує read-профіль до saturation, але
не змінює критичну поведінку на 200 VUs.

## 8. Scaling та caching analysis

### Caching Impact Analysis

Порівняння read-сценарію:

| Рівень | p95 disabled | p95 warm | Зміна p95 | Error disabled | Error warm |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 VUs | 40.54 ms | 21.36 ms | -47.3% | 0% | 0% |
| 50 VUs | 389.08 ms | 315.70 ms | -18.9% | 0% | 0% |
| 100 VUs | 2629.34 ms | 1838.61 ms | -30.1% | 3.62% | 2.63% |
| 200 VUs | 3009.77 ms | 3006.85 ms | -0.1% | 61.06% | 66.52% |

Кеш ефективний у stable та early-saturation режимах, але після вичерпання
спільного bottleneck його вплив практично зникає. Warm-cache режим на 200 VUs
навіть має трохи вищий error rate, тому кеш не можна розглядати як заміну
масштабуванню DB/backend.

### Scaling Impact Analysis

Експеримент з 2+ backend instances не проводився: у наявній таблиці немає
окремих рядків для кількості реплік, а зміна instances зробила б результати
непорівнюваними з поточним baseline. Тому scalability efficiency factor
чесно не обчислюється. Для повного захисту потрібно повторити ті самі fixed-VU
тести з `--scale backend=2` та зафіксувати окремий набір результатів.

## 9. System Performance Baseline

```text
=== SYSTEM PERFORMANCE BASELINE ===
Environment Config: Lab 4 Compose; 1 FastAPI backend; PostgreSQL 17;
                            Redis 7, 128 MB, allkeys-lru; k6 v2.3.0;
                            CPU/RAM limits не задані
Stable Throughput:  до 195.26 RPS на warm read і 191.98 RPS на workflow при 50 VUs;
                            write — 99.66 RPS при 50 VUs
Saturation Point:   100 VUs, повна деградація на 200 VUs
p95 / p99 Latency:  stable 50 VUs: read warm 315.70 / 1704.90 ms;
                            write 548.08 / 2113.55 ms; workflow 493.03 / 1662.23 ms
Error Rate:         0% на 50 VUs для всіх трьох сценаріїв
Critical Scenario:  Scenario B, Write-Intensive, за tail latency
Primary Bottleneck: PostgreSQL transaction/I/O, lock contention або DB pool wait
=== END BASELINE ===
```

## 10. Теоретичний захист

**Coordinated Omission.** Якщо генератор чекає завершення попереднього запиту,
він може не створити запити, які мали б надійти під час затримки. У цьому
тесті незалежні VUs продовжують працювати, а помилки та timeouts не відкидаються
з результатів.

**GC/JIT та warm-up.** Перші запити можуть містити вартість ініціалізації
connection pools, DNS, runtime та Redis connections. Тому 10 VUs слугують
warm-up/control stage, а висновки про saturation робляться за поведінкою всіх
рівнів.

**Tail latency.** p50 показує типову відповідь, p95 — межу повільніших 5%, а
p99 — поведінку крайнього 1%. Саме p99 першим показує черги, блокування та
timeouts, навіть коли середня latency ще виглядає прийнятною.

## 11. Висновок

Система стабільно працює до 50 VUs, але на 100 VUs переходить у saturation.
Найбільш ресурсомістким є write-intensive сценарій, а найнебезпечніша
деградація проявляється в p95/p99 і error rate, а не лише в average latency.
Redis дає помітне покращення read-профілю до saturation, проте не усуває
спільне обмеження PostgreSQL і не забезпечує масштабування на 200 VUs.
