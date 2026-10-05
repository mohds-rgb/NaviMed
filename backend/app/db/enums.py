from enum import StrEnum


class Role(StrEnum):
    OWNER = "owner"
    PLATFORM_ADMIN = "platformAdmin"
    SUPPORT_ADMIN = "supportAdmin"
    PROVIDER_ADMIN = "providerAdmin"
    CLINIC_MANAGER = "clinicManager"
    RECEPTIONIST = "receptionist"
    PROVIDER = "provider"
    PHARMACY_MANAGER = "pharmacyManager"
    PHARMACY_STAFF = "pharmacyStaff"
    CITY_DUTY_COORDINATOR = "cityDutyCoordinator"
    PATIENT = "patient"


class Capability(StrEnum):
    PROFILE_READ = "profile.read"
    PROFILE_MANAGE = "profile.manage"
    CLINIC_READ = "clinic.read"
    CLINIC_MANAGE = "clinic.manage"
    SCHEDULE_READ = "schedule.read"
    SCHEDULE_MANAGE = "schedule.manage"
    APPOINTMENT_READ = "appointment.read"
    APPOINTMENT_MANAGE = "appointment.manage"
    APPOINTMENT_CONFIRM = "appointment.confirm"
    APPOINTMENT_RESCHEDULE = "appointment.reschedule"
    APPOINTMENT_CANCEL = "appointment.cancel"
    APPOINTMENT_CHECKIN = "appointment.checkin"
    APPOINTMENT_COMPLETE = "appointment.complete"
    PATIENT_READ = "patient.read"
    PATIENT_MANAGE = "patient.manage"
    MESSAGE_READ = "message.read"
    MESSAGE_SEND = "message.send"
    MESSAGE_TEMPLATE_MANAGE = "message.template.manage"
    PHARMACY_READ = "pharmacy.read"
    PHARMACY_MANAGE = "pharmacy.manage"
    DUTY_READ = "dutySchedule.read"
    DUTY_MANAGE = "dutySchedule.manage"
    DUTY_PUBLISH = "dutySchedule.publish"
    EMERGENCY_READ = "emergencyContact.read"
    EMERGENCY_MANAGE = "emergencyContact.manage"
    REPORTS_READ = "reports.read"
    ADMIN_MANAGE = "admin.manage"
    AUDIT_READ = "audit.read"


class AppointmentStatus(StrEnum):
    REQUESTED = "requested"
    PENDING_CONFIRMATION = "pendingConfirmation"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checkedIn"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    CANCELLED_BY_PATIENT = "cancelledByPatient"
    CANCELLED_BY_PROVIDER = "cancelledByProvider"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "noShow"
    EXPIRED = "expired"


ACTIVE_APPOINTMENT_STATUSES = tuple(s.value for s in AppointmentStatus if s not in {AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CANCELLED_BY_PROVIDER, AppointmentStatus.RESCHEDULED, AppointmentStatus.NO_SHOW, AppointmentStatus.EXPIRED})


class BookingPolicy(StrEnum):
    INSTANT = "instant"
    PROVIDER_CONFIRMATION = "provider_confirmation"
