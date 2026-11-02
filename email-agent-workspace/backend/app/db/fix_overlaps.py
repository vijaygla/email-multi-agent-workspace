"""
Migration and cleanup script to resolve existing calendar proposal overlaps in MSSQL.
Assigns distinct, non-overlapping time slots to all confirmed (Stage 2) proposals
and refreshes open (Stage 1) proposals with truly available slots.
"""
import json
import logging
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.db.models import MeetingProposalModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_all_overlaps():
    db = SessionLocal()
    try:
        proposals = db.query(MeetingProposalModel).order_by(MeetingProposalModel.created_at.asc()).all()
        logger.info(f"Loaded {len(proposals)} total proposals from MSSQL.")

        # Pool of standard afternoon/business hours candidate slot times (hour, minute)
        CANDIDATES = [
            (14, 0),   # 02:00 PM
            (14, 30),  # 02:30 PM
            (15, 0),   # 03:00 PM
            (15, 30),  # 03:30 PM
            (16, 0),   # 04:00 PM
            (16, 30),  # 04:30 PM
            (17, 0),   # 05:00 PM
            (17, 30),  # 05:30 PM
            (10, 0),   # 10:00 AM
            (10, 30),  # 10:30 AM
            (11, 0),   # 11:00 AM
            (11, 30),  # 11:30 AM
        ]

        # Group proposals by target date
        # Target date is calculated from created_at + 1 day
        confirmed_by_date = {}
        for p in proposals:
            if p.stage == 2 or p.status == "confirmed":
                target_date = (p.created_at + timedelta(days=1)).date()
                confirmed_by_date.setdefault(target_date, []).append(p)

        booked_slots_by_date = {}

        # 1. Fix confirmed proposals: give each unique slot on its target date
        for target_date, conf_list in confirmed_by_date.items():
            booked_slots_by_date[target_date] = set()
            date_dt = datetime.combine(target_date, datetime.min.time())
            day_str = date_dt.strftime("%A, %b %d")

            for idx, p in enumerate(conf_list):
                cand_idx = idx % len(CANDIDATES)
                h, m = CANDIDATES[cand_idx]
                start_dt = date_dt.replace(hour=h, minute=m)
                end_dt = start_dt + timedelta(minutes=30)

                start_time_str = start_dt.strftime("%Y-%m-%d %I:%M %p")
                end_time_str = end_dt.strftime("%I:%M %p")
                display_str = f"{day_str} from {start_dt.strftime('%I:%M %p')} - {end_time_str}"

                booked_slot = {
                    "start_time": start_time_str,
                    "end_time": end_time_str,
                    "display": display_str,
                    "confirmed": True
                }

                p.proposed_slots_json = json.dumps([booked_slot])
                p.requested_dates = display_str
                booked_slots_by_date[target_date].add(start_time_str)
                logger.info(f"Fixed Confirmed Proposal #{p.id} on {target_date}: {display_str}")

        # 2. Fix staged (Stage 1) proposals: offer only slots NOT booked by Stage 2 proposals
        for p in proposals:
            if p.stage == 1 and p.status != "confirmed":
                target_date = (p.created_at + timedelta(days=1)).date()
                booked_for_date = booked_slots_by_date.get(target_date, set())
                date_dt = datetime.combine(target_date, datetime.min.time())
                day_str = date_dt.strftime("%A, %b %d")

                free_slots = []
                for h, m in CANDIDATES:
                    cand_start = date_dt.replace(hour=h, minute=m)
                    cand_start_str = cand_start.strftime("%Y-%m-%d %I:%M %p")
                    if cand_start_str in booked_for_date:
                        continue
                    cand_end = cand_start + timedelta(minutes=30)
                    free_slots.append({
                        "start_time": cand_start_str,
                        "end_time": cand_end.strftime("%I:%M %p"),
                        "display": f"{day_str} from {cand_start.strftime('%I:%M %p')} - {cand_end.strftime('%I:%M %p')}"
                    })
                    if len(free_slots) == 3:
                        break

                if free_slots:
                    p.proposed_slots_json = json.dumps(free_slots)
                    logger.info(f"Updated Staged Proposal #{p.id} on {target_date} with {len(free_slots)} non-overlapping slots.")

        db.commit()
        logger.info("Successfully committed all non-overlapping slot fixes to MSSQL database.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error fixing proposal overlaps: {e}", exc_info=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_overlaps()
