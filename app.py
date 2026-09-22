from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "skillswap-hackathon-secret"

DATABASE = "database.db"


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS gigs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            rate REAL NOT NULL,
            description TEXT NOT NULL,
            creator_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            available INTEGER DEFAULT 1
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gig_id INTEGER NOT NULL,
            client_name TEXT NOT NULL,
            client_contact TEXT NOT NULL,
            requirements TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            FOREIGN KEY (gig_id) REFERENCES gigs(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# MARKETPLACE
# =========================================================

@app.route("/")
def home():

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    conn = get_db()

    query = """
        SELECT *
        FROM gigs
        WHERE available = 1
    """

    params = []

    if search:
        query += """
            AND (
                title LIKE ?
                OR description LIKE ?
                OR creator_name LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value
        ])

    if category:
        query += " AND category = ?"
        params.append(category)

    # DP3: newest available gigs first
    query += " ORDER BY datetime(created_at) DESC"

    gigs = conn.execute(query, params).fetchall()

    categories = conn.execute("""
        SELECT DISTINCT category
        FROM gigs
        ORDER BY category
    """).fetchall()

    # Marketplace statistics
    total_gigs = conn.execute("""
        SELECT COUNT(*)
        FROM gigs
        WHERE available = 1
    """).fetchone()[0]

    total_bookings = conn.execute("""
        SELECT COUNT(*)
        FROM bookings
    """).fetchone()[0]

    total_creators = conn.execute("""
        SELECT COUNT(DISTINCT creator_name)
        FROM gigs
    """).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        gigs=gigs,
        categories=categories,
        search=search,
        selected_category=category,
        total_gigs=total_gigs,
        total_bookings=total_bookings,
        total_creators=total_creators
    )


# =========================================================
# CREATE GIG
# =========================================================

@app.route("/create-gig", methods=["GET", "POST"])
def create_gig():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        rate = request.form.get("rate", "").strip()
        description = request.form.get("description", "").strip()
        creator_name = request.form.get("creator_name", "").strip()

        if not all([
            title,
            category,
            rate,
            description,
            creator_name
        ]):
            flash(
                "Please complete all service details.",
                "error"
            )

            return redirect(url_for("create_gig"))

        try:
            rate_value = float(rate)

            if rate_value <= 0:
                raise ValueError

        except ValueError:

            flash(
                "Please enter a valid positive price.",
                "error"
            )

            return redirect(url_for("create_gig"))

        conn = get_db()

        conn.execute("""
            INSERT INTO gigs
            (
                title,
                category,
                rate,
                description,
                creator_name,
                created_at,
                available
            )
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            title,
            category,
            rate_value,
            description,
            creator_name,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        flash(
            "Your service is now live on SkillSwap.",
            "success"
        )

        return redirect(url_for("home"))

    return render_template("create_gig.html")


# =========================================================
# GIG DETAILS
# =========================================================

@app.route("/gig/<int:gig_id>")
def gig_details(gig_id):

    conn = get_db()

    gig = conn.execute("""
        SELECT *
        FROM gigs
        WHERE id = ?
    """, (gig_id,)).fetchone()

    conn.close()

    if gig is None:
        return "Gig not found", 404

    return render_template(
        "gig.html",
        gig=gig
    )


# =========================================================
# BOOK GIG
# =========================================================

@app.route("/book/<int:gig_id>", methods=["POST"])
def book_gig(gig_id):

    client_name = request.form.get(
        "client_name",
        ""
    ).strip()

    client_contact = request.form.get(
        "client_contact",
        ""
    ).strip()

    requirements = request.form.get(
        "requirements",
        ""
    ).strip()

    if not all([
        client_name,
        client_contact,
        requirements
    ]):

        flash(
            "Please complete all booking details.",
            "error"
        )

        return redirect(
            url_for(
                "gig_details",
                gig_id=gig_id
            )
        )

    conn = get_db()

    gig = conn.execute("""
        SELECT *
        FROM gigs
        WHERE id = ?
    """, (gig_id,)).fetchone()

    if gig is None:

        conn.close()

        return "Gig not found", 404

    # DP2:
    # Pending requests are allowed.
    # Accepted gigs cannot receive new bookings.

    if not gig["available"]:

        conn.close()

        flash(
            "This service is no longer available.",
            "error"
        )

        return redirect(
            url_for(
                "gig_details",
                gig_id=gig_id
            )
        )

    conn.execute("""
        INSERT INTO bookings
        (
            gig_id,
            client_name,
            client_contact,
            requirements,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, 'PENDING', ?)
    """, (
        gig_id,
        client_name,
        client_contact,
        requirements,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    flash(
        "Booking request sent successfully!",
        "success"
    )

    return redirect(
        url_for(
            "my_bookings",
            client_name=client_name
        )
    )


# =========================================================
# MY BOOKINGS
# =========================================================

@app.route("/bookings")
def my_bookings():

    client_name = request.args.get(
        "client_name",
        "Avni"
    ).strip()

    conn = get_db()

    bookings = conn.execute("""
        SELECT
            bookings.*,
            gigs.title,
            gigs.category,
            gigs.rate,
            gigs.creator_name,
            gigs.available
        FROM bookings
        JOIN gigs
            ON bookings.gig_id = gigs.id
        WHERE bookings.client_name = ?
        ORDER BY datetime(bookings.created_at) DESC
    """, (client_name,)).fetchall()

    conn.close()

    return render_template(
        "bookings.html",
        bookings=bookings,
        client_name=client_name
    )


# =========================================================
# CREATOR DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    creator_name = request.args.get(
        "creator_name",
        "Avantika"
    ).strip()

    conn = get_db()

    bookings = conn.execute("""
        SELECT
            bookings.*,
            gigs.title,
            gigs.category,
            gigs.rate,
            gigs.creator_name
        FROM bookings
        JOIN gigs
            ON bookings.gig_id = gigs.id
        WHERE gigs.creator_name = ?
        ORDER BY
            CASE bookings.status
                WHEN 'PENDING' THEN 1
                WHEN 'ACCEPTED' THEN 2
                ELSE 3
            END,
            datetime(bookings.created_at) DESC
    """, (creator_name,)).fetchall()

    total_bookings = conn.execute("""
        SELECT COUNT(*)
        FROM bookings
        JOIN gigs
            ON bookings.gig_id = gigs.id
        WHERE gigs.creator_name = ?
    """, (creator_name,)).fetchone()[0]

    pending_count = conn.execute("""
        SELECT COUNT(*)
        FROM bookings
        JOIN gigs
            ON bookings.gig_id = gigs.id
        WHERE gigs.creator_name = ?
        AND bookings.status = 'PENDING'
    """, (creator_name,)).fetchone()[0]

    accepted_count = conn.execute("""
        SELECT COUNT(*)
        FROM bookings
        JOIN gigs
            ON bookings.gig_id = gigs.id
        WHERE gigs.creator_name = ?
        AND bookings.status = 'ACCEPTED'
    """, (creator_name,)).fetchone()[0]

    active_gigs = conn.execute("""
        SELECT COUNT(*)
        FROM gigs
        WHERE creator_name = ?
        AND available = 1
    """, (creator_name,)).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        bookings=bookings,
        creator_name=creator_name,
        total_bookings=total_bookings,
        pending_count=pending_count,
        accepted_count=accepted_count,
        active_gigs=active_gigs
    )


# =========================================================
# ACCEPT BOOKING
# =========================================================

@app.route(
    "/booking/<int:booking_id>/accept",
    methods=["POST"]
)
def accept_booking(booking_id):

    conn = get_db()

    booking = conn.execute("""
        SELECT *
        FROM bookings
        WHERE id = ?
    """, (booking_id,)).fetchone()

    if booking is None:

        conn.close()

        return "Booking not found", 404

    if booking["status"] != "PENDING":

        conn.close()

        flash(
            "This booking is no longer pending.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # Check whether another request
    # has already been accepted.
    existing = conn.execute("""
        SELECT id
        FROM bookings
        WHERE gig_id = ?
        AND status = 'ACCEPTED'
        AND id != ?
    """, (
        booking["gig_id"],
        booking_id
    )).fetchone()

    if existing:

        conn.close()

        flash(
            "This service already has an accepted booking.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # Accept selected booking
    conn.execute("""
        UPDATE bookings
        SET status = 'ACCEPTED'
        WHERE id = ?
    """, (booking_id,))

    # Make service unavailable
    conn.execute("""
        UPDATE gigs
        SET available = 0
        WHERE id = ?
    """, (booking["gig_id"],))

    # DP2:
    # Automatically decline all other pending
    # requests for the same service.
    conn.execute("""
        UPDATE bookings
        SET status = 'DECLINED'
        WHERE gig_id = ?
        AND id != ?
        AND status = 'PENDING'
    """, (
        booking["gig_id"],
        booking_id
    ))

    conn.commit()
    conn.close()

    flash(
        "Booking accepted. Other pending requests were updated.",
        "success"
    )

    return redirect(
        request.referrer or url_for("dashboard")
    )


# =========================================================
# DECLINE BOOKING
# =========================================================

@app.route(
    "/booking/<int:booking_id>/decline",
    methods=["POST"]
)
def decline_booking(booking_id):

    conn = get_db()

    booking = conn.execute("""
        SELECT *
        FROM bookings
        WHERE id = ?
    """, (booking_id,)).fetchone()

    if booking is None:

        conn.close()

        return "Booking not found", 404

    if booking["status"] != "PENDING":

        conn.close()

        flash(
            "This booking is already processed.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    conn.execute("""
        UPDATE bookings
        SET status = 'DECLINED'
        WHERE id = ?
    """, (booking_id,))

    conn.commit()
    conn.close()

    flash(
        "Booking declined.",
        "success"
    )

    return redirect(
        request.referrer or url_for("dashboard")
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    init_db()

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        debug=True,
        host="0.0.0.0",
        port=port
    )