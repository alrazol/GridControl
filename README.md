```
.
├── .venv
│   ├── bin
│   ├── lib
│   └── pyvenv.cfg
├── etls
    ├── pipeline.py
├── models
    ├── line.py

├── README.md
├── pyproject.toml
└── uv.lock

```

```

src/
    core/                   # Core package
        domain/             # Domain logic and models
            models/
                network.py
                network_element.py
            enums.py
            services/
                network_solver.py
                network_metrics.py
        infra/              # Infrastructure layer for core
            database/
                models.py
                session.py
            api/
                routers/
                    networks.py
                dependencies.py
        __init__.py

    rl/                     # RL package
        environment/
            network_env.py  # RL environment for interacting with networks
        agents/
            dqn_agent.py
            ppo_agent.py
        trainers/
            trainer.py      # Handles training of agents
        services/
            rl_service.py   # Coordinates RL-specific operations
        api/
            routers/
                rl.py       # RL-specific API endpoints
        __init__.py

```
