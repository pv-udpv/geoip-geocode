# 🚀 Быстрый старт geoip-geocode

Это краткое руководство поможет вам быстро начать работу с пакетом geoip-geocode.

## 📋 Требования

- Python 3.8+
- База данных GeoIP (GeoLite2-City.mmdb или IP2Location BIN)

## 🔧 Установка

### Вариант 1: Установка с pip
```bash
pip install geoip-geocode
```

### Вариант 2: Установка для разработки
```bash
# Клонируйте репозиторий
git clone https://github.com/your-repo/geoip-geocode.git
cd geoip-geocode

# Установите с помощью uv (рекомендуется)
uv sync --all-extras

# Или с pip в виртуальном окружении
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
pip install -e ".[dev]"
```

## 📦 Получение базы данных GeoIP

### Вариант 1: GeoLite2 (бесплатно)

1. Зарегистрируйтесь на [MaxMind](https://www.maxmind.com/en/geolite2/signup)
2. Получите лицензионный ключ
3. Скачайте GeoLite2-City.mmdb

```bash
# Используйте CLI для автоматической загрузки
geoip-geocode update-db --license-key YOUR_LICENSE_KEY
```

### Вариант 2: IP2Location (альтернатива)

Скачайте бесплатную базу данных с [IP2Location](https://www.ip2location.com/database/ip2location)

```bash
# Пример использования с IP2Location
geoip-geocode lookup 8.8.8.8 --provider ip2location --database ./IP2LOCATION-LITE-DB11.BIN
```

## 🎯 Базовое использование

### 1. Через командную строку (CLI)

```bash
# Простой поиск IP
geoip-geocode lookup 8.8.8.8

# С указанием пути к базе данных
geoip-geocode lookup 8.8.8.8 --database ./GeoLite2-City.mmdb

# Список доступных провайдеров
geoip-geocode list-providers

# Создание конфигурационного файла
geoip-geocode config-init --database ./GeoLite2-City.mmdb

# Показать версию
geoip-geocode version
```

### 2. Через Python API

#### Простой пример

```python
from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers import GeoIP2Provider

# Настройка провайдера
config = ProviderConfig(
    name="geoip2",
    enabled=True,
    database_path="./GeoLite2-City.mmdb"
)

# Создание провайдера
provider = GeoIP2Provider(config)

# Поиск IP адреса
result = provider.lookup("8.8.8.8")

if result:
    print(f"Город: {result.city}")
    print(f"Страна: {result.country_name}")
    print(f"Координаты: {result.latitude}, {result.longitude}")
    print(f"GeoName ID: {result.geoname_id}")
```

#### Использование IP2Location провайдера

```python
from geoip_geocode.models import ProviderConfig
from geoip_geocode.providers import IP2LocationProvider

# Настройка IP2Location провайдера
config = ProviderConfig(
    name="ip2location",
    enabled=True,
    database_path="./IP2LOCATION-LITE-DB11.BIN"
)

# Создание провайдера
provider = IP2LocationProvider(config)

# Поиск IP адреса
result = provider.lookup("8.8.8.8")

if result:
    print(f"Город: {result.city}")
    print(f"Страна: {result.country_name}")
    print(f"Координаты: {result.latitude}, {result.longitude}")
```

#### Использование реестра провайдеров

```python
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import GeoIP2Provider
from geoip_geocode.models import ProviderConfig

# Получаем глобальный реестр
registry = get_registry()

# Регистрируем провайдер
registry.register("geoip2", GeoIP2Provider)

# Создаем конфигурацию
config = ProviderConfig(
    name="geoip2",
    database_path="./GeoLite2-City.mmdb",
    priority=100
)

# Получаем провайдер
provider = registry.get_provider("geoip2", config)

# Выполняем поиск
result = provider.lookup("8.8.8.8")
```

#### Использование конфигурационного файла

```python
from geoip_geocode.config import load_config
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import GeoIP2Provider

# Загружаем конфигурацию
config = load_config(yaml_path="config.yaml")

# Настраиваем реестр
registry = get_registry()
registry.register("geoip2", GeoIP2Provider)

# Получаем конфигурацию провайдера
provider_config = config.get_provider_config("geoip2")
provider = registry.get_provider("geoip2", provider_config)

# Выполняем поиск
result = provider.lookup("8.8.8.8")
```

## ⚙️ Конфигурация

### Создание config.yaml

```yaml
default_provider: geoip2
cache_enabled: false
cache_ttl: 3600

providers:
  - name: geoip2
    enabled: true
    priority: 100
    database_path: ./GeoLite2-City.mmdb
    timeout: 30
    max_retries: 3
```

### Использование переменных окружения

Создайте файл `.env`:

```env
GEOIP_DEFAULT_PROVIDER=geoip2
GEOIP_CACHE_ENABLED=false
GEOIP_CACHE_TTL=3600
MAXMIND_LICENSE_KEY=your_license_key_here
```

## 📊 Модель данных GeoData

Все географические данные возвращаются в виде объектов `GeoData`:

```python
from geoip_geocode.models import GeoData

geo_data = GeoData(
    geoname_id=5375480,          # Первичный ключ из GeoNames
    ip_address="8.8.8.8",
    country_code="US",
    country_name="United States",
    city="Mountain View",
    postal_code="94035",
    latitude=37.386,
    longitude=-122.0838,
    time_zone="America/Los_Angeles",
    continent_code="NA",
    continent_name="North America",
    subdivision="California",
    subdivision_code="CA",
    accuracy_radius=100,
    provider="geoip2"
)

# Преобразование в словарь
data_dict = geo_data.model_dump()

# Преобразование в JSON
data_json = geo_data.model_dump_json(indent=2)
```

## 🔍 Примеры использования

### Поиск нескольких IP адресов

```python
from geoip_geocode.providers import GeoIP2Provider
from geoip_geocode.models import ProviderConfig

config = ProviderConfig(
    name="geoip2",
    database_path="./GeoLite2-City.mmdb"
)

provider = GeoIP2Provider(config)

ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]

for ip in ips:
    result = provider.lookup(ip)
    if result:
        print(f"{ip}: {result.city}, {result.country_name}")
```

### Обработка ошибок

```python
from geoip_geocode.providers import GeoIP2Provider
from geoip_geocode.models import ProviderConfig

config = ProviderConfig(
    name="geoip2",
    database_path="./GeoLite2-City.mmdb"
)

try:
    provider = GeoIP2Provider(config)
    result = provider.lookup("8.8.8.8")
    
    if result:
        print(f"Найдено: {result.city}")
    else:
        print("IP не найден в базе данных")
        
except FileNotFoundError:
    print("База данных не найдена!")
except Exception as e:
    print(f"Ошибка: {e}")
```

### Использование нескольких провайдеров (Fallback)

```python
from geoip_geocode.registry import get_registry
from geoip_geocode.providers import GeoIP2Provider, IP2LocationProvider
from geoip_geocode.models import ProviderConfig

# Настройка реестра
registry = get_registry()
registry.register("geoip2", GeoIP2Provider)
registry.register("ip2location", IP2LocationProvider)

# Провайдер с высоким приоритетом (основной)
config1 = ProviderConfig(
    name="geoip2",
    database_path="./GeoLite2-City.mmdb",
    priority=100,
    enabled=True
)

# Провайдер с низким приоритетом (резервный)
config2 = ProviderConfig(
    name="ip2location",
    database_path="./IP2LOCATION-LITE-DB11.BIN",
    priority=50,
    enabled=True
)

# Создаем провайдеры
provider1 = registry.get_provider("geoip2", config1)
provider2 = registry.get_provider("ip2location", config2)

# Пробуем провайдеры по порядку приоритета
ip = "8.8.8.8"
for provider in [provider1, provider2]:
    if provider and provider.is_available():
        result = provider.lookup(ip)
        if result:
            print(f"✓ Найдено через {provider.config.name}")
            print(f"  Город: {result.city}, {result.country_name}")
            break
    else:
        print(f"✗ Провайдер {provider.config.name} недоступен")
```

## ✅ Проверка установки

Запустите тесты чтобы убедиться, что все работает:

```bash
# С использованием uv
uv run pytest

# С использованием pytest напрямую
pytest

# С покрытием кода
pytest --cov=geoip_geocode --cov-report=html
```

Все 92 теста должны пройти успешно! ✨

## 📚 Дополнительные ресурсы

- [README.md](README.md) - полная документация
- [examples/](examples/) - больше примеров использования
- [docs/](docs/) - расширенная документация
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
- [IP2Location](https://www.ip2location.com/)

## 🆘 Помощь

Если у вас возникли проблемы:

1. Проверьте, что база данных существует по указанному пути
2. Убедитесь, что все зависимости установлены: `uv sync --all-extras`
3. Запустите тесты: `uv run pytest`
4. Проверьте версию: `geoip-geocode version`
5. Создайте issue на GitHub

## 🎉 Готово!

Теперь вы готовы использовать geoip-geocode для определения геолокации по IP адресам!

Попробуйте:
```bash
uv run geoip-geocode lookup 8.8.8.8 --database ./GeoLite2-City.mmdb
