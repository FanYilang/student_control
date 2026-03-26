from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import close_db, get_db, init_db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev-secret-key-change-me",
        DATABASE=app.instance_path + "/student_control.db",
    )

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    @app.route("/")
    def index():
        if session.get("admin_id"):
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if session.get("admin_id"):
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                flash("请输入用户名和密码。", "error")
                return render_template("login.html")

            db = get_db()
            admin = db.execute(
                "SELECT id, username, password_hash FROM admins WHERE username = ?",
                (username,),
            ).fetchone()

            if admin is None or not check_password_hash(admin["password_hash"], password):
                flash("用户名或密码错误。", "error")
                return render_template("login.html")

            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            flash("登录成功。", "success")
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        if not session.get("admin_id"):
            flash("请先登录。", "error")
            return redirect(url_for("login"))
        return render_template("dashboard.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("已退出登录。", "success")
        return redirect(url_for("login"))

    return app
