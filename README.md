# Actual proyect structure

✅ Monolitic reuse

```bash
dj_users/
├── dj_users/                    ← App as package
│   ├── __init__.py
│   ├── apps.py                  ← AppConfig
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── serializers.py          ← DRF
│   ├── permissions.py          ← Auth logic
│   ├── signals.py              ← Logic associated with models
│   ├── services/               ← (opcional) Isolated business logic
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_users.py
│   └── migrations/
│       └── __init__.py
├── pyproject.toml              ← install package
├── MANIFEST.in
├── README.md<
└── LICENSE
```

🧱 In the future migrate to microservice:

```bash
dj_users/
├── dj_users/                    ← still being DjangoApp
│   └── ...
├── manage.py                    ← now has a new entrypoint
├── config/                      ← new djangoProject
│   ├── __init__.py
│   ├── settings.py              ← own settings, urls, wsgi
│   └── urls.py
├── Dockerfile
├── pyproject.toml              ← You can keep it
└── requirements.txt
```

And you can have this microservice expose:

- Authentication
- User registration
- Password recovery
- Profile management 
  Via API (via DRF, JWT, OAuth, etc.), communicating with your orchestrator or frontend.