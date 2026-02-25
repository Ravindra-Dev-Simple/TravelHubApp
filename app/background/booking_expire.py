from sqlalchemy import text
from datetime import datetime
from app.db.session import SessionLocal

def expire_bookings():
    db = SessionLocal()

    try:
        expired_bookings = db.execute(
            text("""
                SELECT * FROM tbl_bookings
                WHERE status = 'RESERVED'
                AND expires_at <= :now
                FOR UPDATE
            """),
            {"now": datetime.utcnow()}
        ).fetchall()

        for booking in expired_bookings:

            # Restore inventory
            db.execute(
                text("""
                    UPDATE tbl_inventory
                    SET available_count = available_count + 1
                    WHERE room_id = :room_id
                    AND date >= :check_in
                    AND date < :check_out
                """),
                {
                    "room_id": booking.room_id,
                    "check_in": booking.check_in,
                    "check_out": booking.check_out
                }
            )

            # Update booking status
            db.execute(
                text("""
                    UPDATE tbl_bookings
                    SET status = 'EXPIRED'
                    WHERE id = :id
                """),
                {"id": booking.id}
            )

        db.commit()

    except:
        db.rollback()
    finally:
        db.close()
