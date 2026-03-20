from django.utils.timezone import now

def get_sla_status(complaint):
    if complaint.status == 'resolved':
        return "completed"

    elapsed = (now() - complaint.created_at).total_seconds() / 3600

    if elapsed > complaint.sla_hours:
        return "breached"

    return "within_sla"