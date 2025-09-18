#!/usr/bin/env python3
"""
Test script to verify SendGrid email functionality
This script tests the actual email sending capability
"""

import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def test_email_sending():
    """Test if SendGrid can send emails with the configured API key"""
    
    # Check if API key exists
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        print("❌ SendGrid API key not found in environment variables")
        print("To enable real email sending, please set SENDGRID_API_KEY")
        return False
    
    print(f"✅ SendGrid API key found (first 8 chars: {api_key[:8]}...)")
    
    # Test email configuration
    test_email = "test@flowmarket.com"  # Replace with actual test email
    
    message = Mail(
        from_email='noreply@flowmarket.com',
        to_emails=test_email,
        subject='اختبار إرسال الرسائل - فلوماركت',
        html_content="""
        <div style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
            <h2 style="color: #2c5aa0;">اختبار نظام الرسائل</h2>
            <p>هذه رسالة اختبار للتأكد من عمل نظام إرسال الرسائل في فلوماركت.</p>
            <p>إذا وصلتك هذه الرسالة، فهذا يعني أن النظام يعمل بشكل صحيح.</p>
            <hr style="margin: 20px 0;">
            <p style="color: #666; font-size: 14px;">
                هذه رسالة اختبار تلقائية من موقع فلوماركت.
            </p>
        </div>
        """
    )
    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        if response.status_code == 202:
            print(f"✅ Test email sent successfully to {test_email}")
            print(f"Response status: {response.status_code}")
            return True
        else:
            print(f"❌ SendGrid error: {response.status_code}")
            print(f"Response body: {response.body}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing SendGrid email functionality...")
    success = test_email_sending()
    sys.exit(0 if success else 1)