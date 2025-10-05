# app.py
from flask import Flask, jsonify, abort, send_file
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError

_engine = None

def get_engine():
    """
    Get a SQLAlchemy engine instance. The database URL is taken from the DB_URL environment variable.
    If the variable is not set, an error is raised.
    """

    global _engine
    if _engine is not None:
        return _engine
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise RuntimeError("Missing DB_URL (or DATABASE_URL) environment variable.")
    # Normalize old 'postgres://' scheme to 'postgresql://'
    if db_url.startswith("postgres://"):
        db_url = "postgresql://" + db_url[len("postgres://"):]
    _engine = create_engine(
        db_url,
        pool_pre_ping=True,
    )
    return _engine

def validate_coords(coords):
    """
    Validate and parse coordinates in the format "x_y_z". Used in the get_studies_by_coordinates() function.
    """
    parts = coords.split("_")
    if len(parts) != 3 or not all(part.lstrip('-').isdigit() for part in parts):
        raise ValueError("Invalid coordinate format. Expected format: x_y_z")
    return map(int, parts)


def create_app():
    app = Flask(__name__)

    @app.get("/", endpoint="health")
    def health():
        return "<p>Server working!</p>"

    @app.get("/img", endpoint="show_img")
    def show_img():
        """ Smoke test to show an image """
        return send_file("amygdala.gif", mimetype="image/gif")

    @app.get("/dissociate/terms/<term1>/", endpoint="terms_studies")
    @app.get("/dissociate/terms/<term1>/<term2>", endpoint="terms_studies")
    def get_studies_by_term(term1, term2 = None):
        """
        Get studies associated with term1 but not with term2.

        Term2 can be optional. If term2 not provided, just return studies associated with term1.

        Term format in parquet: "terms_abstract_tfidf__<term>"
        <term> is separated by whitespaces, e.g. "anterior cingulate", "ventromedial prefrontal"
        """

        term1 = "terms_abstract_tfidf__" + term1.replace("_", " ")
        term2 = "terms_abstract_tfidf__" + term2.replace("_", " ") if term2 else None

        eng = get_engine()
        payload = {"ok": False, "dialect": eng.dialect.name}

        if term2:

            query = text(
                "WITH excluded_studies AS ("
                "    SELECT study_id "
                "    FROM ns.annotations_terms "
                "    WHERE term = :term2"
                ") "
                "SELECT study_id, contrast_id, term, weight "
                "FROM ns.annotations_terms "
                "WHERE term = :term1 "
                "AND study_id NOT IN (SELECT study_id FROM excluded_studies) "
                "ORDER BY weight DESC "
                "LIMIT 10"
            ).bindparams(term1=term1, term2=term2)
        else:
            # When term2 is not provided
            query = text(
                "SELECT study_id, contrast_id, term, weight "
                "FROM ns.annotations_terms "
                "WHERE term = :term1 "
                "ORDER BY weight DESC "
                "LIMIT 10"
            ).bindparams(term1=term1)

        try:
            with eng.begin() as conn:
                # Ensure we are in the correct schema
                conn.execute(text("SET search_path TO ns, public;"))
                payload["version"] = conn.exec_driver_sql("SELECT version()").scalar()

                # Counts
                payload["annotations_terms_count"] = conn.execute(text("SELECT COUNT(*) FROM ns.annotations_terms")).scalar()

                try:
                    # Term1 is the term that we want to keep, term2 is the term that we want to filter out
                    rows = conn.execute(query).mappings().all()
                    payload["annotations_terms_studies"] = [dict(r) for r in rows]
                except Exception as e:
                    payload["error"] = str(e)
                    payload["annotations_terms_studies"] = []

            payload["ok"] = True
            return jsonify(payload), 200

        except Exception as e:
            payload["error"] = str(e)
            return jsonify(payload), 500

    @app.get("/dissociate/locations/<coords1>/", endpoint="locations_studies")
    @app.get("/dissociate/locations/<coords1>/<coords2>", endpoint="locations_studies")
    def get_studies_by_coordinates(coords1, coords2 = None):

        """
        Get studies associated with coordinates1 but not with coordinates2.

        Coordinates2 can be optional. If coord2 not provided, just return studies associated with coordinates1.

        coordinates format: "x_y_z", e.g. "36_-58_52"
        """

        try:
            x1, y1, z1 = validate_coords(coords1)
            # coords2 can be optional
            x2, y2, z2 = validate_coords(coords2) if coords2 else (None, None, None)
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400

        eng = get_engine()
        payload = {"ok": False, "dialect": eng.dialect.name}

        # Making the query conditional on whether coords2 is provided
        if coords2:
            query = text(
                "WITH excluded_studies AS ("
                "    SELECT study_id "
                "    FROM ns.coordinates "
                "    WHERE ST_X(geom) = :x2 AND ST_Y(geom) = :y2 AND ST_Z(geom) = :z2"
                ") "
                "SELECT study_id, ST_X(geom) AS x, ST_Y(geom) AS y, ST_Z(geom) AS z "
                "FROM ns.coordinates "
                "WHERE ST_X(geom) = :x1 AND ST_Y(geom) = :y1 AND ST_Z(geom) = :z1 "
                "AND study_id NOT IN (SELECT study_id FROM excluded_studies) "
                "LIMIT 10"
            ).bindparams(x1=x1, y1=y1, z1=z1, x2=x2, y2=y2, z2=z2)
        else:
            query = text(
                "SELECT study_id, ST_X(geom) AS x, ST_Y(geom) AS y, ST_Z(geom) AS z "
                "FROM ns.coordinates "
                "WHERE ST_X(geom) = :x1 AND ST_Y(geom) = :y1 AND ST_Z(geom) = :z1 "
                "LIMIT 10"
            ).bindparams(x1=x1, y1=y1, z1=z1)

        try:
            with eng.begin() as conn:
                # Ensure we are in the correct schema
                conn.execute(text("SET search_path TO ns, public;"))
                payload["version"] = conn.exec_driver_sql("SELECT version()").scalar()

                # Counts
                payload["coordinates_count"] = conn.execute(text("SELECT COUNT(*) FROM ns.coordinates")).scalar()

                try:
                    # Coords1 is the coord that we want to keep
                    # Coords2 is the coord that we want to filter out
                    rows = conn.execute(query).mappings().all()
                    payload["coordinates_studies"] = [dict(r) for r in rows]
                except Exception as e:
                    payload["error"] = str(e)
                    payload["coordinates_studies"] = []

            payload["ok"] = True
            return jsonify(payload), 200

        except Exception as e:
            payload["error"] = str(e)
            return jsonify(payload), 500

    @app.get("/test_db", endpoint="test_db")
    def test_db():
        eng = get_engine()
        payload = {"ok": False, "dialect": eng.dialect.name}

        try:
            with eng.begin() as conn:
                # Ensure we are in the correct schema
                conn.execute(text("SET search_path TO ns, public;"))
                payload["version"] = conn.exec_driver_sql("SELECT version()").scalar()

                # Counts
                payload["coordinates_count"] = conn.execute(text("SELECT COUNT(*) FROM ns.coordinates")).scalar()
                payload["metadata_count"] = conn.execute(text("SELECT COUNT(*) FROM ns.metadata")).scalar()
                payload["annotations_terms_count"] = conn.execute(text("SELECT COUNT(*) FROM ns.annotations_terms")).scalar()

                # Samples
                try:
                    rows = conn.execute(text(
                        "SELECT study_id, ST_X(geom) AS x, ST_Y(geom) AS y, ST_Z(geom) AS z FROM ns.coordinates LIMIT 3"
                    )).mappings().all()
                    payload["coordinates_sample"] = [dict(r) for r in rows]
                except Exception:
                    payload["coordinates_sample"] = []

                try:
                    # Select a few columns if they exist; otherwise select a generic subset
                    rows = conn.execute(text("SELECT * FROM ns.metadata LIMIT 3")).mappings().all()
                    payload["metadata_sample"] = [dict(r) for r in rows]
                except Exception:
                    payload["metadata_sample"] = []

                try:

                    rows = conn.execute(text(
                        "SELECT study_id, contrast_id, term, weight FROM ns.annotations_terms LIMIT 3"
                    )).mappings().all()
                    payload["annotations_terms_sample"] = [dict(r) for r in rows]
                except Exception:
                    payload["annotations_terms_sample"] = []

            payload["ok"] = True
            return jsonify(payload), 200

        except Exception as e:
            payload["error"] = str(e)
            return jsonify(payload), 500

    return app

# WSGI entry point (no __main__)
app = create_app()
