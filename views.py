from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import OnboardingProcess
from .flows import OnboardingFlow

class OnboardingViewSet(viewsets.ViewSet):
    """
    ViewSet for handling onboarding process operations
    """
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """Start a new onboarding process"""
        try:
            # Create and start the onboarding process
            process = OnboardingProcess.objects.create(
                first_name=request.data.get('first_name'),
                last_name=request.data.get('last_name'),
                email=request.data.get('email'),
                phone=request.data.get('phone'),
                position_title=request.data.get('position_title'),
                department=request.data.get('department'),
                start_date=request.data.get('start_date'),
                status='pending'
            )
            
            # Start the workflow
            OnboardingFlow.start.run(process=process)
            
            return Response({
                'id': process.id,
                'status': process.status,
                'message': 'Onboarding process started successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """Get onboarding process status"""
        process = get_object_or_404(OnboardingProcess, pk=pk)
        
        return Response({
            'id': process.id,
            'status': process.status,
            'first_name': process.first_name,
            'last_name': process.last_name,
            'email': process.email,
            'position_title': process.position_title,
            'department': process.department,
            'start_date': process.start_date,
            'offer_letter': process.offer_letter.url if process.offer_letter else None,
            'signed_contract': process.signed_contract.url if process.signed_contract else None,
            'docuseal_submission_id': process.docuseal_submission_id,
            'm365_user_id': process.m365_user_id,
            'training_course_id': process.training_course_id
        })
    
    @action(detail=True, methods=['post'])
    def document_callback(self, request, pk=None):
        """Handle document signing callbacks from DocuSeal"""
        process = get_object_or_404(OnboardingProcess, pk=pk)
        
        try:
            submission_id = request.data.get('submission_id')
            if submission_id == process.docuseal_submission_id:
                process.signed_contract = request.data.get('signed_document_url')
                process.save()
                
                # Continue the workflow
                activation = OnboardingFlow.sign_contract.activate(process=process)
                activation.done()
                
                return Response({
                    'message': 'Document signing processed successfully'
                })
            else:
                return Response({
                    'error': 'Invalid submission ID'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def training_callback(self, request, pk=None):
        """Handle training completion callbacks from TalentLMS"""
        process = get_object_or_404(OnboardingProcess, pk=pk)
        
        try:
            if request.data.get('course_id') == process.training_course_id:
                # Continue the workflow
                activation = OnboardingFlow.schedule_training.activate(process=process)
                activation.done()
                
                return Response({
                    'message': 'Training completion processed successfully'
                })
            else:
                return Response({
                    'error': 'Invalid course ID'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
