### Углублённые примеры векторных операций в Unity с подробными комментариями

```csharp
using UnityEngine;

public class AdvancedVectorOperations : MonoBehaviour
{
    public Transform target;
    public Transform player;
    public Transform obstacle;
    public float speed = 8f;
    public float forceMultiplier = 10f;
    
    void Update()
    {
        // 1. Сложение и вычитание векторов (комбинирование перемещений)
        Vector3 keyboardInput = new Vector3(Input.GetAxis("Horizontal"), 0, Input.GetAxis("Vertical"));
        Vector3 gravity = new Vector3(0, Physics.gravity.y * Time.deltaTime, 0);
        Vector3 combinedMovement = keyboardInput * speed + gravity;
        player.position += combinedMovement * Time.deltaTime;

        /*
        Принцип: 
        - keyboardInput: направление от пользовательского ввода
        - gravity: постоянная сила тяжести
        - combinedMovement: суммарное воздействие на объект
        Важно: физические силы обычно умножаются на Time.deltaTime для frame-rate независимости
        */

        // 2. Умножение на скаляр (контроль интенсивности)
        Vector3 baseDirection = new Vector3(1, 0, 1).normalized;
        Vector3 dashVector = baseDirection * 15f; // Рывок вперед
        if (Input.GetKeyDown(KeyCode.Space))
        {
            player.position += dashVector;
        }

        /*
        Принцип:
        - Базовое направление нормализуется для сохранения направления
        - Умножение на 15 увеличивает магнитуду вектора
        - Результат: мгновенное смещение на 15 юнитов по диагонали
        */

        // 3. Нормализация (работа с направлениями)
        Vector3 toEnemy = target.position - player.position;
        Vector3 fireDirection = toEnemy.normalized;
        Debug.DrawRay(player.position, fireDirection * 10, Color.red);

        /*
        Принцип:
        - toEnemy: разница позиций (вектор от игрока к врагу)
        - normalised: преобразует вектор в единичную длину (magnitude=1)
        - Использование: направление выстрела/атаки не зависит от расстояния
        */

        // 4. Магнитуд и sqrMagnitude (оптимизированные расстояния)
        float distanceToTarget = toEnemy.magnitude;
        float sqrDistance = toEnemy.sqrMagnitude; // Квадрат расстояния
        
        // Оптимизация: сравнение квадратов расстояний быстрее
        if (sqrDistance < 100f) // Эквивалентно distance < 10
        {
            Debug.Log($"Враг в радиусе! Точное расстояние: {distanceToTarget:F2}");
        }

        /*
        Принцип:
        - magnitude: точное расстояние (дорогой расчет с квадратным корнем)
        - sqrMagnitude: квадрат расстояния (оптимизация для сравнений)
        - Предпочтительно использовать sqrMagnitude в Update()
        */

        // 5. Скалярное произведение (углы и проекции)
        Vector3 playerForward = player.forward;
        float aimPrecision = Vector3.Dot(playerForward, fireDirection);
        
        // Определение относительного положения
        float relativePosition = Vector3.Dot(playerForward, toEnemy.normalized);
        string positionStatus = relativePosition > 0 ? "ВПЕРЕДИ" : "ПОЗАДИ";

        /*
        Принцип:
        - Возвращает косинус угла между векторами (1=0°, 0=90°, -1=180°)
        - Использование: 
          * Определение фронтальной зоны (прицеливание)
          * Проверка видимости объектов
          * Расчет проекции вектора (например, силы на поверхность)
        */

        // 6. Векторное произведение (перпендикуляры и вращения)
        Vector3 surfaceNormal = obstacle.up;
        Vector3 tangentDirection = Vector3.Cross(surfaceNormal, playerForward).normalized;
        
        // Создание локальной системы координат
        Vector3 binormal = Vector3.Cross(surfaceNormal, tangentDirection);
        Debug.DrawRay(obstacle.position, tangentDirection * 3, Color.blue);
        Debug.DrawRay(obstacle.position, binormal * 3, Color.green);

        /*
        Принцип:
        - Результат перпендикулярен обоим исходным векторам
        - Длина = произведение длин векторов на синус угла между ними
        - Применение:
          * Расчет касательных к поверхностям
          * Определение оси вращения
          * Построение ортогональных базисов
        */

        // 7. Отражение (физика столкновений)
        Vector3 incomingVelocity = player.forward * speed;
        Vector3 bounceVelocity = Vector3.Reflect(incomingVelocity, surfaceNormal);
        
        // Реалистичное отражение с сохранением энергии
        Vector3 energyConservingBounce = bounceVelocity.normalized * incomingVelocity.magnitude;
        Debug.DrawRay(obstacle.position, energyConservingBounce, Color.yellow);

        /*
        Принцип:
        - Формула: R = V - 2*(V·N)*N, где V - входящий вектор, N - нормаль
        - Вариант с сохранением энергии: нормализация + умножение на исходную длину
        - Использование: 
          * Отскок шаров
          * Рикошет снарядов
          * Траектории после столкновений
        */

        // 8. Интерполяции (плавные переходы)
        // Линейная интерполяция (Lerp)
        Vector3 lerpedPosition = Vector3.Lerp(
            player.position, 
            target.position, 
            0.5f * Time.deltaTime
        );
        
        // Сферическая интерполяция (Slerp) - сохранение скорости на кривых
        Vector3 slerpedPosition = Vector3.Slerp(
            player.position,
            target.position,
            0.3f * Time.deltaTime
        );
        
        // Интерполяция с замедлением (SmoothDamp)
        Vector3 currentVelocity = Vector3.zero;
        Vector3 smoothPosition = Vector3.SmoothDamp(
            player.position,
            target.position,
            ref currentVelocity,
            0.5f
        );

        /*
        Принцип:
        - Lerp: линейное перемещение (постоянная скорость)
        - Slerp: движение по дуге (постоянная угловая скорость)
        - SmoothDamp: физически корректное движение с плавным ускорением/торможением
        - Параметры:
          * currentVelocity: ссылка на переменную состояния
          * smoothTime: приблизительное время достижения цели
          * maxSpeed (необязательный): ограничение скорости
        */
    }
    
    // Дополнительные практические примеры
    void FixedUpdate()
    {
        // Расчет силы для толкания объекта
        Vector3 pushDirection = (target.position - player.position).normalized;
        float distanceFactor = Mathf.Clamp01(1 - (pushDirection.magnitude / 10f));
        Vector3 appliedForce = pushDirection * forceMultiplier * distanceFactor;
        
        Rigidbody targetRb = target.GetComponent<Rigidbody>();
        if(targetRb) targetRb.AddForce(appliedForce, ForceMode.Impulse);

        /*
        Комплексный пример:
        1. Определение направления к цели
        2. Нормализация для получения чистого направления
        3. Расчет коэффициента расстояния (сила уменьшается при отдалении)
        4. Применение импульса к физическому телу
        */
    }
}
```

### Ключевые принципы работы с векторами в играх:

1. **Фреймрейт-независимость**
   - Все перемещения умножаются на `Time.deltaTime`
   - Физические расчеты выполняются в `FixedUpdate()`

2. **Оптимизация вычислений**
   - Использование `sqrMagnitude` вместо `magnitude`
   - Кэширование повторяющихся вычислений
   - Минимизация операций в цикле обновления

3. **Комбинирование операций**
```csharp
// Пример: расчет отражения с учетом трения
Vector3 CalculateBounceWithFriction(Vector3 velocity, Vector3 normal, float friction)
{
    Vector3 perfectBounce = Vector3.Reflect(velocity, normal);
    Vector3 tangent = Vector3.Cross(normal, Vector3.Cross(perfectBounce, normal)).normalized;
    return perfectBounce - tangent * friction * perfectBounce.magnitude;
}
```

4. **Взаимодействие с физикой**
   - Использование `Rigidbody.AddForce()` с различными ForceMode
   - Корректировка векторов для `ForceMode.Impulse` и `ForceMode.VelocityChange`

5. **Пространственные преобразования**
   - Локальные/глобальные координаты: `Transform.TransformDirection()`
   - Учет вращения объектов: `Quaternion * Vector3`

6. **Геометрические применения**
```csharp
// Проверка нахождения точки в поле зрения
bool IsInFieldOfView(Vector3 point, Vector3 viewOrigin, Vector3 viewDirection, float maxAngle)
{
    Vector3 directionToPoint = (point - viewOrigin).normalized;
    float angle = Vector3.Angle(viewDirection, directionToPoint);
    return angle <= maxAngle;
}
```

### Основные типы векторных операций:

1. **Базовые операции (12 основных)**
   - Сложение/вычитание (2)
   - Умножение/деление на скаляр (2)
   - Нормализация (1)
   - Магнитуд/sqrMagnitude (2)
   - Скалярное произведение (1)
   - Векторное произведение (1)
   - Проекции (2)
   - Отражаение (1)

2. **Специализированные операции (8+)**
   - Интерполяции (Lerp/Slerp/SmoothDamp)
   - Ограничение (ClampMagnitude)
   - Вращение (RotateTowards)
   - Дельта-вычисления (MoveTowards)
   - Угловые расчеты (Angle, SignedAngle)
   - Координатные преобразования

3. **Комбинированные операции (бесконечное множество)**
   - Физические симуляции
   - Коллизионные расчеты
   - Траекторный анализ
   - Процедурная анимация

Каждая операция служит строительным блоком для игровых механик. Например:
- **ИИ врагов**: нормализация + магнитуд для преследования
- **Платформер**: векторное произведение для определения поверхности
- **Стратегии**: скалярное произведение для проверки видимости
- **Гонки**: интерполяции для плавного управления
