# -*- coding: utf-8 -*-
"""
admin_panel.py — Flask Blueprint serving the /admin web panel.

Pages: login, dashboard (stats + config + API key), corrections (table + add +
moderate + search), usage (log + daily totals), plus export/import of
corrections.json. State is read from current_app.config['STATE'].
"""

import io
import json
from functools import wraps

from flask import (
    Blueprint, request, render_template, redirect, url_for,
    session, flash, current_app, jsonify, Response,
)

admin_bp = Blueprint("admin", __name__)


def _state():
    return current_app.config["STATE"]


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("admin"):
            return redirect(url_for("admin.login"))
        return view(*a, **kw)
    return wrapped


# ----- auth --------------------------------------------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pw = request.form.get("password", "")
        if pw == _state().cfg.get("admin_password", "admin123"):
            session["admin"] = True
            return redirect(url_for("admin.dashboard"))
        flash("Wrong password / වැරදි මුරපදය", "error")
    return render_template("base.html", login_page=True)


@admin_bp.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin.login"))


# ----- dashboard + config ------------------------------------------------
@admin_bp.route("/")
@login_required
def dashboard():
    st = _state()
    return render_template(
        "dashboard.html",
        stats=st.db.get_stats(),
        cfg=st.cfg.data,
        usage=st.logger.summary(),
        model_ready=st.model is not None,
        model_error=st.model_error,
        has_key=bool(st.cfg.get_api_key()),
    )


@admin_bp.route("/save_config", methods=["POST"])
@login_required
def save_config():
    st = _state()
    f = request.form
    st.cfg.set("model", f.get("model", st.cfg.get("model")).strip())
    st.cfg.set("precheck_threshold", int(f.get("precheck_threshold") or 5))
    st.cfg.set("inject_top_n", int(f.get("inject_top_n") or 40))
    st.cfg.set("max_concurrent", int(f.get("max_concurrent") or 4))
    new_pw = f.get("admin_password", "").strip()
    if new_pw:
        st.cfg.set("admin_password", new_pw)
    st.cfg.save()
    st.reload_model()
    flash("Settings saved / සැකසීම් සුරැකිණි", "ok")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/save_api_key", methods=["POST"])
@login_required
def save_api_key():
    st = _state()
    key = request.form.get("api_key", "").strip()
    if key:
        st.cfg.set_api_key(key)
        st.reload_model()
        flash("API key saved", "ok")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/test_api_key")
@login_required
def test_api_key():
    st = _state()
    st.reload_model()
    if st.model is None:
        flash("API key NOT working: %s" % (st.model_error or "no key"), "error")
    else:
        try:
            st.proofread("ලංකාවේ අද්‍යාපන ප්‍රශ්ණ ගොඩක් තිබේ.")
            flash("API key works ✓ (test proofread succeeded)", "ok")
        except Exception as e:
            flash("API key test failed: %s" % str(e)[:120], "error")
    return redirect(url_for("admin.dashboard"))


# ----- corrections -------------------------------------------------------
@admin_bp.route("/corrections")
@login_required
def corrections():
    st = _state()
    q = request.args.get("q", "").strip()
    items = st.db.search(q) if q else list(st.db.data["corrections"])
    items.sort(key=lambda c: c.get("count", 0), reverse=True)
    return render_template("corrections.html", items=items, q=q,
                           stats=st.db.get_stats())


@admin_bp.route("/corrections/add", methods=["POST"])
@login_required
def corrections_add():
    st = _state()
    wrong = request.form.get("wrong", "").strip()
    correct = request.form.get("correct", "").strip()
    etype = request.form.get("type", "spelling").strip() or "spelling"
    res = st.db.record_correction(wrong, correct, etype, added_by="admin", source="admin")
    flash("Added: %s → %s (%s)" % (wrong, correct, res.get("status")), "ok")
    return redirect(url_for("admin.corrections"))


@admin_bp.route("/corrections/action", methods=["POST"])
@login_required
def corrections_action():
    st = _state()
    cid = request.form.get("id", "")
    action = request.form.get("action", "")
    if action == "delete":
        st.db.delete(cid)
    elif action == "confirm":
        st.db.confirm(cid)
    elif action in ("precheck", "inject_only", "disabled"):
        st.db.set_mode(cid, action, confirm=(action == "precheck"))
    return redirect(url_for("admin.corrections", q=request.form.get("q", "")))


# ----- usage -------------------------------------------------------------
@admin_bp.route("/usage")
@login_required
def usage():
    st = _state()
    return render_template("usage.html", rows=st.logger.read_rows(500),
                           daily=st.logger.daily_totals(), summary=st.logger.summary())


# ----- export / import ---------------------------------------------------
@admin_bp.route("/export")
@login_required
def export():
    st = _state()
    payload = json.dumps(st.db.data, ensure_ascii=False, indent=2)
    return Response(
        payload, mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=corrections.json"},
    )


@admin_bp.route("/import", methods=["POST"])
@login_required
def import_corrections():
    st = _state()
    f = request.files.get("file")
    if not f:
        flash("No file selected", "error")
        return redirect(url_for("admin.corrections"))
    try:
        data = json.load(io.TextIOWrapper(f.stream, encoding="utf-8"))
        incoming = data.get("corrections", []) if isinstance(data, dict) else []
        added = 0
        for c in incoming:
            st.db.record_correction(
                c.get("wrong", ""), c.get("correct", ""),
                c.get("type", "spelling"), added_by="import", source="import")
            added += 1
        flash("Imported %d corrections" % added, "ok")
    except Exception as e:
        flash("Import failed: %s" % str(e)[:120], "error")
    return redirect(url_for("admin.corrections"))
