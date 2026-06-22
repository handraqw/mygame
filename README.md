Survivor Arena

Запуск:

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Запустить игру:

```bash
python main.py
```


| Алгоритм | Где находится | Сложность реализации из теории | Разобран в «АЛГОСЫ» |
|---|---|---:|:---:|
| ***Lightmap + multiply blending*** | `systems/light_system.py` | Сложно | ✅ |
| ***Particle System*** | `systems/particle_system.py` | Легко/Средне | ✅ |
| ***Boids Separation*** | `entities/enemy.py` | Средне | ✅ |
| ***Uniform Grid (с динамическим радиусом запроса)*** | `core/spatial_grid.py`, `core/game.py` | Средне | ✅ |
| ***Fixed Timestep Accumulator*** | `core/game.py`, `Game.run` | Легко | ✅ |
| ***FSM, конечный автомат*** | `core/fsm.py`, `core/states.py` | Ультра-легко | ✅ |
| ***Camera offset + clamp*** | `core/camera.py` | Ультра-легко | ✅ |
| ***Circle overlap*** | `core/utils.py`, `core/game.py` | Ультра-легко | ✅ |
| Игровой цикл + deltaTime | `core/game.py`, `Game.run` | Легко | |
| Observer / EventBus | `core/eventbus.py` | Ультра-легко | |
| Object Pool | `utils/object_pool.py` | Легко | |
| Weighted random + binary search | `systems/wave_manager.py` | Легко | |
| Arrive steering | `entities/enemy.py` | Легко | |