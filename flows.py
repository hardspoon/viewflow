from viewflow import flow
from viewflow.flow.views import CreateProcessView, UpdateProcessView
from .models import OnboardingProcess
from .services import ExternalServices

services = ExternalServices()

class OnboardingFlow(flow.Flow):
    """Onboarding workflow definition using Viewflow"""
    
    process_class = OnboardingProcess
    
    start = (
        flow.Start(CreateProcessView, fields=[
            'first_name',
            'last_name',
            'email',
            'phone',
            'position_title',
            'department',
            'start_date'
        ])
        .Permission('can_start_onboarding')
        .Next('verify_information')
    )
    
    verify_information = (
        flow.View(UpdateProcessView, fields=[
            'first_name',
            'last_name',
            'email',
            'phone',
            'position_title',
            'department',
            'start_date'
        ])
        .Permission('can_approve_onboarding')
        .Next('generate_offer_letter')
    )
    
    generate_offer_letter = (
        flow.Handler(this.generate_offer_letter)
        .Next('sign_contract')
    )
    
    sign_contract = (
        flow.Handler(this.sign_contract)
        .Next('provision_account')
    )
    
    provision_account = (
        flow.Handler(this.provision_account)
        .Next('schedule_training')
    )
    
    schedule_training = (
        flow.Handler(this.schedule_training)
        .Next('complete_onboarding')
    )
    
    complete_onboarding = (
        flow.Handler(this.complete_onboarding)
        .Permission('can_complete_onboarding')
        .Next(this.end)
    )
    
    def generate_offer_letter(self, activation):
        """Generate offer letter using DocuSeal"""
        try:
            download_url = services.generate_offer_letter(activation.process)
            activation.process.offer_letter = download_url
            activation.process.status = 'in_progress'
            activation.process.save()
        except Exception as e:
            activation.process.status = 'error'
            activation.process.save()
            raise
    
    def sign_contract(self, activation):
        """Handle contract signing process"""
        # Wait for DocuSeal webhook callback
        if activation.process.docuseal_submission_id and not activation.process.signed_contract:
            activation.process.status = 'waiting_for_signature'
            activation.process.save()
    
    def provision_account(self, activation):
        """Provision Microsoft 365 account"""
        try:
            services.provision_user_account(activation.process)
            activation.process.status = 'account_provisioned'
            activation.process.save()
        except Exception as e:
            activation.process.status = 'error'
            activation.process.save()
            raise
    
    def schedule_training(self, activation):
        """Schedule training in TalentLMS"""
        try:
            services.schedule_training(activation.process)
            activation.process.status = 'training_scheduled'
            activation.process.save()
        except Exception as e:
            activation.process.status = 'error'
            activation.process.save()
            raise
    
    def complete_onboarding(self, activation):
        """Finalize onboarding process"""
        activation.process.status = 'completed'
        activation.process.save()
