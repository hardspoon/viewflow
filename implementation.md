



Workflow Implementation
Define the Process Model Create a process model to manage workflow states and store necessary data.

python
Copy code
from django.db import models
from viewflow import jsonstore
from viewflow.workflow.models import Process

class OnboardingProcess(Process):
    personal_details = jsonstore.JSONField()
    position_info = jsonstore.JSONField()
    start_date = jsonstore.DateField()
    location = jsonstore.CharField(max_length=100)
    consent_signed = jsonstore.BooleanField(default=False)
    hr_approved = jsonstore.BooleanField(default=False)
    offer_signed = jsonstore.BooleanField(default=False)
    provisioning_done = jsonstore.BooleanField(default=False)

    class Meta:
        proxy = True
Define Workflow Stages Use Viewflow's flow.Flow to define the onboarding process stages.

python
Copy code
from viewflow import this
from viewflow.workflow import flow, act
from viewflow.workflow.flow import views

class OnboardingFlow(flow.Flow):
    process_class = OnboardingProcess

    start = (
        flow.Start(views.CreateProcessView.as_view(fields=['personal_details', 'position_info', 'start_date', 'location']))
        .Permission(auto_create=True)
        .Next(this.validate_submission)
    )

    validate_submission = (
        flow.Function(this.validate_request)
        .Next(this.consent_documents)
    )

    consent_documents = (
        flow.View(views.UpdateProcessView.as_view(fields=['consent_signed']))
        .Permission(auto_create=True)
        .Next(this.check_consent)
    )

    check_consent = (
        flow.If(act.process.consent_signed)
        .Then(this.hr_review)
        .Else(this.end)
    )

    hr_review = (
        flow.View(views.UpdateProcessView.as_view(fields=['hr_approved']))
        .Permission(auto_create=True)
        .Next(this.generate_offer if act.process.hr_approved else this.end)
    )

    generate_offer = (
        flow.Function(this.send_offer_letter)
        .Next(this.wait_for_offer_acceptance)
    )

    wait_for_offer_acceptance = (
        flow.View(views.UpdateProcessView.as_view(fields=['offer_signed']))
        .Permission(auto_create=True)
        .Next(this.check_offer)
    )

    check_offer = (
        flow.If(act.process.offer_signed)
        .Then(this.system_provisioning)
        .Else(this.end)
    )

    system_provisioning = (
        flow.Function(this.create_system_accounts)
        .Next(this.schedule_orientation)
    )

    schedule_orientation = (
        flow.Function(this.plan_orientation)
        .Next(this.final_provisioning)
    )

    final_provisioning = (
        flow.Function(this.complete_provisioning)
        .Next(this.end)
    )

    end = flow.End()

    def validate_request(self, activation):
        # Validation logic: fields, start date, location
        pass

    def send_offer_letter(self, activation):
        # Generate and send offer letter using DocuSeal
        pass

    def create_system_accounts(self, activation):
        # Provision accounts (Microsoft 365, HRIS, etc.)
        pass

    def plan_orientation(self, activation):
        # Notify trainer to schedule orientation
        pass

    def complete_provisioning(self, activation):
        # Ensure all access and requirements are met
        pass
Role-Based Access Use Django permissions and Viewflow's .Permission() to enforce role-specific access to tasks. Define these roles in your Django settings or middleware.

Integrations

DocuSeal: Manage document generation and tracking in the send_offer_letter method.
Microsoft 365: Use APIs to set up accounts in create_system_accounts.
TalentLMS: Schedule training and track progress in plan_orientation.
Notification System Integrate email, Microsoft Teams, and system notifications in methods like send_offer_letter and plan_orientation using third-party Django packages or APIs.

Track Status Extend the process model with additional status fields, and use these to track progress through the workflow stages.