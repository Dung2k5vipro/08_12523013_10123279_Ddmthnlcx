# Cấu trúc dự án

```
fuel-consumption-prediction/
├── app/
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   ├── types/
│   │   │   └── utils/
│   │   ├── public/
│   │   ├── Dockerfile
│   │   ├── .dockerignore
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── next.config.js
│   │   └── .gitkeep
│   └── backend/
│       ├── src/
│       │   ├── config/
│       │   ├── controllers/
│       │   ├── routes/
│       │   ├── services/
│       │   ├── models/
│       │   ├── middlewares/
│       │   ├── validators/
│       │   ├── utils/
│       │   └── app.js
│       ├── tests/
│       │   └── .gitkeep
│       ├── Dockerfile
│       ├── .dockerignore
│       ├── package.json
│       └── .gitkeep
├── ai-models/
│   ├── colab/
│   │   ├── 01_eda.ipynb
│   │   ├── 02_preprocess.ipynb
│   │   ├── 03_train.ipynb
│   │   └── 04_evaluate.ipynb
│   ├── src/
│   │   ├── preprocess.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── utils.py
│   ├── data/
│   │   ├── raw/
│   │   │   └── .gitkeep
│   │   ├── processed/
│   │   │   └── .gitkeep
│   │   └── DATA.md
│   ├── models/
│   │   ├── schema.json
│   │   ├── metadata.json
│   │   └── versions/
│   │       └── .gitkeep
│   ├── service/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── model_loader.py
│   │   ├── config.py
│   │   ├── tests/
│   │   │   └── .gitkeep
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   └── requirements.txt
├── docs/
│   ├── figures/
│   │   ├── eda/
│   │   │   └── .gitkeep
│   │   ├── evaluation/
│   │   │   └── .gitkeep
│   │   └── .gitkeep
│   ├── test-results/
│   │   └── .gitkeep
│   ├── logs/
│   │   └── .gitkeep
│   └── (baocao.docx và slide.pptx sẽ thêm sau)
├── scripts/
│   ├── train.bat
│   ├── run-local.bat
│   ├── test.bat
│   └── .gitkeep
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── PROJECT_STRUCTURE.md
```
