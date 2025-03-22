This package aims at allowing using RL to solve various power grid related problems.


## 1) Structure
```
.
├── configs/
├── src/
│   ├── core/
|   |   ├── application/
│   │   │   ├── api/
│   │   │   └── cli/
│   │   ├── domain/
|   |   |   ├── mappers/
│   │   │   ├── models/
│   │   │   ├── ports/
|   |   |   └── use_cases/
│   │   ├── infrastructure/
│   │   │   ├── adapters/
│   │   │   ├── services/
│   │   │       └── converters/
|   |   |   ├── settings.py
|   |   |   ├── schemas.py
|   |   |   └── sqlite_client.py
│   ├── rl/
|   |   ├── action/
|   |   ├── agent/
│   │   ├── artifacts/
|   |   ├── config_loaders/
|   |   ├── configs/
|   |   ├── logger/
│   │   ├── observation/
│   │   ├── outage/
│   │   ├── repositories/
|   |   ├── reward/
├── tests/
├── pyproject.toml
├── README.md
└── uv.lock
```
