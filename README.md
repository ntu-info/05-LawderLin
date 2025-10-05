[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/SO1PVZ3b)
# Neurosynth Backend

A lightweight Flask backend that exposes **functional dissociation** endpoints on top of a Neurosynth-backed PostgreSQL database.

The service provides two APIs that return studies mentioning one concept/coordinate **but not** the other (A \ B). You can also query the opposite direction (B \ A).

---

## Table of Contents

- [Endpoints](#endpoints)
  - [Dissociate by terms](#dissociate-by-terms)
  - [Dissociate by MNI coordinates](#dissociate-by-mni-coordinates)
- [Example Requests](#example-requests)
- [Requirements](#requirements)
- [Files](#files)
- [Notes](#notes)
- [License](#license)

---

## Endpoints

### Dissociate by terms

```
GET /dissociate/terms/<term_a>/<term_b>
```

Returns studies that mention **`term_a`** but **not** `term_b`.

**Examples**

```
/dissociate/terms/posterior_cingulate/ventromedial_prefrontal
/dissociate/terms/ventromedial_prefrontal/posterior_cingulate
```

---

### Dissociate by MNI coordinates

Coordinates are passed as `x_y_z` (underscores, not commas).  
Returns studies that mention **`[x1, y1, z1]`** but **not** `[x2, y2, z2]`.

**Default Mode Network test case**

```
/dissociate/locations/0_-52_26/-2_50_-6
/dissociate/locations/-2_50_-6/0_-52_26
```

---

## Example Requests

**By terms**
```bash
curl https://ns-nano-ih4e.onrender.com/dissociate/terms/posterior_cingulate
```

You can also add in another term as the exclusion condition.

```bash
curl https://ns-nano-ih4e.onrender.comdissociate/terms/posterior_cingulate/ventromedial_prefrontal
curl https://ns-nano-ih4e.onrender.comdissociate/terms/ventromedial_prefrontal/posterior_cingulate
```

**By coordinates**

```bash
curl https://ns-nano-ih4e.onrender.com/dissociate/locations/0_-52_26/
```

You can also add in another coordinate as exclusion condition.

```bash
curl https://ns-nano-ih4e.onrender.comdissociate/locations/0_-52_26/-2_50_-6
curl https://ns-nano-ih4e.onrender.comdissociate/locations/-2_50_-6/0_-52_26
```

---

## Requirements

- Python 3.10+
- PostgreSQL 12+
- Python dependencies (typical):
  - `Flask`
  - `SQLAlchemy`
  - PostgreSQL driver (e.g., `psycopg2-binary`)
  - Production WSGI server (e.g., `gunicorn`)

---

## Files
```txt
.
├── amygdala.gif            # gif file for smoke test
├── annotation_columns.txt  # all the annotation terms
├── annotations.parquet     # .parquet file for PostgreSQL database
├── app.py                  # Main backend app
├── chat.json               # LLM interaction history (backend)
├── chat_shell.json         # LLM interaction history (shell script)
├── check_annotation.py     # python script for checking annotation format
├── check_db.py             # python script for checking database status
├── coordinates.parquet     # .parquet file for PostgreSQL database
├── create_db.py            # python script for building database
├── LICENSE                 # MIT license for this project
├── metadata.parquet        # .parquet file for PostgreSQL database
├── README.md               # This
├── requirements.txt        # 安裝需求
├── test_command.sh         # 查詢指令，加快測試過程
└── test_response           # 測試查詢結果
    ├── coords.json         # 座標查詢測試結果
    ├── home.html           # home route 測試結果
    ├── terms.json          # 詞彙查詢測試結果
    └── test_db.json        # 範例測試
```

---

## Notes

- Path parameters use underscores (`_`) between coordinates: `x_y_z`.
- Term strings should be URL-safe (e.g., `posterior_cingulate`, `ventromedial_prefrontal`). Replace spaces with underscores on the client if needed.
- The term/coordinate pairs above illustrate a **Default Mode Network** dissociation example. Adjust for your analysis.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
