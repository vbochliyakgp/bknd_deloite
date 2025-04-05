# app/services/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from app.config import settings
from app.models.employee import Employee
import logging

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    async def send_email(
        to_email: str, subject: str, text_content: str, html_content: str = None
    ) -> bool:
        """
        Send an email using SMTP
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = settings.EMAILS_FROM_EMAIL
            message["To"] = to_email

            # Add text content
            message.attach(MIMEText(text_content, "plain"))

            # Add HTML content if provided
            if html_content:
                message.attach(MIMEText(html_content, "html"))

            # Connect to SMTP server
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    async def send_employee_alert(
        db: Session, employee_id: int, subject: str, message: str
    ) -> bool:
        """
        Send an alert to an employee
        """
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            logger.error(f"Employee with ID {employee_id} not found")
            return False

        html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #86BC25; color: white; padding: 10px 20px; }}
                        .content {{ padding: 20px; border: 1px solid #ddd; }}
                        .footer {{ font-size: 12px; color: #999; margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Deloitte Employee Alert</h2>
                        </div>
                        <div class="content">
                            <p>Hello {employee.name},</p>
                            <p>{message}</p>
                            <p>This is an automated message from the Vibemeter system. If you have any questions, please reply to this email or contact HR.</p>
                            <p>Best regards,<br>Deloitte People Experience Team</p>
                        </div>
                        <div class="footer">
                            <p>This email is confidential and intended solely for the person or entity to whom it is addressed.</p>
                        </div>
                    </div>
                </body>
                </html>
                """

                text_content = f"""
        Hello {employee.name},

        {message}

        This is an automated message from the Vibemeter system. If you have any questions, please reply to this email or contact HR.

        Best regards,
        Deloitte People Experience Team

        This email is confidential and intended solely for the person or entity to whom it is addressed.
                """

        return await EmailService.send_email(
            to_email=employee.email,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
        )

    @staticmethod
    async def send_hr_notification(
        employee_name: str, session_id: int, reason: str
    ) -> bool:
        """
        Send notification to HR about an escalated chat
        """
        subject = f"Chat Escalation: {employee_name}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #86BC25; color: white; padding: 10px 20px; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .alert {{ color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 5px; }}
                .footer {{ font-size: 12px; color: #999; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>HR Alert: Chat Escalation</h2>
                </div>
                <div class="content">
                    <p>A chat session with <strong>{employee_name}</strong> has been escalated to HR.</p>
                    <div class="alert">
                        <p><strong>Reason for Escalation:</strong> {reason}</p>
                    </div>
                    <p><strong>Session ID:</strong> {session_id}</p>
                    <p>Please review this conversation as soon as possible and follow up with the employee.</p>
                    <p>You can access the full conversation details in the HR Dashboard.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the Vibemeter system.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
            HR Alert: Chat Escalation

            A chat session with {employee_name} has been escalated to HR.

            Reason for Escalation: {reason}

            Session ID: {session_id}

            Please review this conversation as soon as possible and follow up with the employee.
            You can access the full conversation details in the HR Dashboard.

            This is an automated message from the Vibemeter system.
        """

        # Send to HR email (could be a distribution list or specific HR users)
        return await EmailService.send_email(
            to_email=settings.EMAILS_FROM_EMAIL,  # Replace with actual HR email
            subject=subject,
            text_content=text_content,
            html_content=html_content,
        )

    @staticmethod
    async def send_daily_report_notification(report_date: str) -> bool:
        """
        Send notification about daily report availability
        """
        subject = f"Daily Vibemeter Report - {report_date}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #86BC25; color: white; padding: 10px 20px; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .button {{ display: inline-block; background-color: #86BC25; color: white; 
                           padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .footer {{ font-size: 12px; color: #999; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Vibemeter Daily Report</h2>
                </div>
                <div class="content">
                    <p>Hello HR Team,</p>
                    <p>The daily Vibemeter report for <strong>{report_date}</strong> is now available.</p>
                    <p>Please check the HR Dashboard to view the full report with analytics on employee well-being, 
                    at-risk employees, and recommended actions.</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="#" class="button">View Report</a>
                    </p>
                    <p>Best regards,<br>Vibemeter System</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the Vibemeter system.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
            Vibemeter Daily Report

            Hello HR Team,

            The daily Vibemeter report for {report_date} is now available.

            Please check the HR Dashboard to view the full report with analytics on employee well-being, at-risk employees, and recommended actions.

            Best regards,
            Vibemeter System

            This is an automated message from the Vibemeter system.
        """

        # Send to HR team
        return await EmailService.send_email(
            to_email=settings.EMAILS_FROM_EMAIL,  # Replace with actual HR email
            subject=subject,
            text_content=text_content,
            html_content=html_content,
        )
