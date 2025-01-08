import os
import requests
from O365 import Account
from python_docuseal import DocuSealClient
from talentlms import TalentLMS
from django.conf import settings

class ExternalServices:
    """Service layer for external service integrations"""
    
    def __init__(self):
        # Initialize DocuSeal client
        self.docuseal = DocuSealClient(
            api_key=os.getenv('DOCUSEAL_API_KEY'),
            base_url=os.getenv('DOCUSEAL_BASE_URL')
        )
        
        # Initialize Microsoft 365 client
        credentials = (
            os.getenv('M365_CLIENT_ID'),
            os.getenv('M365_CLIENT_SECRET')
        )
        self.m365 = Account(credentials)
        
        # Initialize TalentLMS client
        self.talentlms = TalentLMS(
            os.getenv('TALENTLMS_API_KEY'),
            os.getenv('TALENTLMS_DOMAIN')
        )
    
    def generate_offer_letter(self, process):
        """Generate offer letter using DocuSeal"""
        template_id = settings.DOCUSEAL_OFFER_LETTER_TEMPLATE
        response = self.docuseal.create_submission(
            template_id=template_id,
            data={
                'first_name': process.first_name,
                'last_name': process.last_name,
                'position_title': process.position_title,
                'start_date': process.start_date.strftime('%Y-%m-%d')
            }
        )
        process.docuseal_submission_id = response['id']
        process.save()
        return response['download_url']
    
    def provision_user_account(self, process):
        """Provision Microsoft 365 account"""
        user = self.m365.new_user(
            user_principal_name=process.email,
            display_name=f"{process.first_name} {process.last_name}",
            mail_nickname=f"{process.first_name}.{process.last_name}",
            account_enabled=True
        )
        process.m365_user_id = user.id
        process.save()
        return user
    
    def schedule_training(self, process):
        """Schedule training in TalentLMS"""
        course_id = settings.TALENTLMS_ONBOARDING_COURSE
        user = self.talentlms.users.create(
            first_name=process.first_name,
            last_name=process.last_name,
            email=process.email,
            login=process.email
        )
        enrollment = self.talentlms.enrollments.create(
            user_id=user.id,
            course_id=course_id
        )
        process.training_course_id = enrollment.id
        process.save()
        return enrollment
