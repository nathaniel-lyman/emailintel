"""
Email delivery module for Retail Price Cut Summary App.
Handles daily digest generation and delivery via SMTP or SendGrid.
"""

import sqlite3
import smtplib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict

from config import Config

# Configure logging
logger = logging.getLogger(__name__)


class EmailSender:
    """Handle email delivery via SMTP or SendGrid."""
    
    def __init__(self):
        # Determine which email service to use
        self.use_sendgrid = bool(Config.SENDGRID_API_KEY)
        
        if self.use_sendgrid:
            try:
                import sendgrid
                from sendgrid.helpers.mail import Mail
                self.sg = sendgrid.SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
                logger.info("Using SendGrid for email delivery")
            except ImportError:
                logger.error("SendGrid package not installed but API key provided")
                self.use_sendgrid = False
    
    def send_email(self, subject: str, body_text: str, body_html: Optional[str] = None) -> bool:
        """Send email using configured service."""
        try:
            if self.use_sendgrid:
                return self._send_via_sendgrid(subject, body_text, body_html)
            else:
                return self._send_via_smtp(subject, body_text, body_html)
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _send_via_smtp(self, subject: str, body_text: str, body_html: Optional[str] = None) -> bool:
        """Send email via SMTP."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = Config.SMTP_FROM_EMAIL
            msg['To'] = Config.SMTP_TO_EMAIL
            
            # Add text part
            text_part = MIMEText(body_text, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if body_html:
                html_part = MIMEText(body_html, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully via SMTP: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False
    
    def _send_via_sendgrid(self, subject: str, body_text: str, body_html: Optional[str] = None) -> bool:
        """Send email via SendGrid."""
        try:
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=Config.SENDGRID_FROM_EMAIL,
                to_emails=Config.SENDGRID_TO_EMAIL,
                subject=subject,
                plain_text_content=body_text,
                html_content=body_html or body_text
            )
            
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully via SendGrid: {subject}")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return False


class DailyDigest:
    """Generate and send daily email digests."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.email_sender = EmailSender()
    
    def send_daily_digest(self) -> bool:
        """Generate and send the daily digest email."""
        # Get summaries from past 24 hours
        summaries = self._get_recent_summaries(hours=24)
        
        if not summaries:
            logger.info("No new summaries for daily digest - skipping email")
            self._log_operation('email', 'skipped', 'No new summaries', 0)
            return True  # Not an error, just nothing to send
        
        # Group summaries by topic
        grouped_summaries = self._group_by_topic(summaries)
        
        # Generate email content
        subject = f"Retail Price Cuts Digest - {datetime.now().strftime('%B %d, %Y')}"
        body_text = self._generate_text_email(grouped_summaries)
        body_html = self._generate_html_email(grouped_summaries)
        
        # Send email
        success = self.email_sender.send_email(subject, body_text, body_html)
        
        # Log the operation
        status = 'success' if success else 'failure'
        message = f"Sent digest with {len(summaries)} summaries" if success else "Failed to send digest"
        self._log_operation('email', status, message, len(summaries))
        
        return success
    
    def _get_recent_summaries(self, hours: int) -> List[Dict]:
        """Get summaries from the past N hours."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT s.summary_text, s.topic, h.title, h.link, h.source, h.published_date
            FROM summaries s
            JOIN headlines h ON s.headline_id = h.id
            WHERE s.created_at >= ?
            ORDER BY s.topic, h.published_date DESC
        """, (cutoff.isoformat(),))
        
        summaries = []
        for row in cursor.fetchall():
            summaries.append({
                'summary': row['summary_text'],
                'topic': row['topic'] or 'General Retail',
                'title': row['title'],
                'link': row['link'],
                'source': row['source'],
                'published_date': row['published_date']
            })
        
        conn.close()
        return summaries
    
    def _group_by_topic(self, summaries: List[Dict]) -> Dict[str, List[Dict]]:
        """Group summaries by topic category."""
        grouped = defaultdict(list)
        
        for summary in summaries:
            # Use the topic from the summary, default to 'General Retail' if missing
            topic = summary.get('topic', 'General Retail')
            grouped[topic].append(summary)
        
        # Sort topics with 'General Retail' last
        sorted_topics = sorted(grouped.items(), key=lambda x: (x[0] == 'General Retail', x[0]))
        return dict(sorted_topics)
    
    def _extract_retailer(self, summary: Dict) -> str:
        """Extract retailer name from summary or source."""
        # Common retailer names to look for
        retailers = [
            'Walmart', 'Target', 'Amazon', 'Costco', 'Kroger',
            'Home Depot', 'Lowe\'s', 'Best Buy', 'CVS', 'Walgreens',
            'Macy\'s', 'Nordstrom', 'Kohl\'s', 'JCPenney', 'TJ Maxx'
        ]
        
        # Check summary text
        summary_lower = summary['summary'].lower()
        for retailer in retailers:
            if retailer.lower() in summary_lower:
                return retailer
        
        # Check source
        source_lower = summary['source'].lower()
        for retailer in retailers:
            if retailer.lower() in source_lower:
                return retailer
        
        # Default to source if no retailer found
        return summary['source']
    
    def _generate_text_email(self, grouped_summaries: Dict[str, List[Dict]]) -> str:
        """Generate plain text email content."""
        lines = []
        lines.append("RETAIL PRICE CUTS DAILY DIGEST")
        lines.append(f"{datetime.now().strftime('%B %d, %Y')}")
        lines.append("=" * 50)
        lines.append("")
        
        total_count = sum(len(summaries) for summaries in grouped_summaries.values())
        lines.append(f"Today's digest includes {total_count} price cuts across {len(grouped_summaries)} categories:")
        lines.append("")
        
        for topic, summaries in grouped_summaries.items():
            lines.append(f"\n📦 {topic.upper()} ({len(summaries)} items)")
            lines.append("-" * 50)
            
            for summary in summaries:
                lines.append(f"\n• {summary['summary']}")
                lines.append(f"  Published: {self._format_date(summary['published_date'])}")
                lines.append(f"  Read more: {summary['link']}")
            
            lines.append("")
        
        lines.append("\n" + "=" * 50)
        lines.append("This digest was automatically generated.")
        lines.append("To update your search preferences, visit the settings page.")
        
        return "\n".join(lines)
    
    def _generate_html_email(self, grouped_summaries: Dict[str, List[Dict]]) -> str:
        """Generate HTML email content."""
        html_parts = []
        
        html_parts.append("""
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; margin-top: 30px; }
                .summary { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }
                .meta { color: #7f8c8d; font-size: 0.9em; margin-top: 5px; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 0.9em; }
            </style>
        </head>
        <body>
        """)
        
        html_parts.append(f"<h1>Retail Price Cuts Daily Digest - {datetime.now().strftime('%B %d, %Y')}</h1>")
        
        total_count = sum(len(summaries) for summaries in grouped_summaries.values())
        html_parts.append(f"<p>Today's digest includes <strong>{total_count}</strong> price cuts across <strong>{len(grouped_summaries)}</strong> categories:</p>")
        
        for topic, summaries in grouped_summaries.items():
            html_parts.append(f"<h2>📦 {topic} ({len(summaries)} items)</h2>")
            
            for summary in summaries:
                html_parts.append('<div class="summary">')
                html_parts.append(f'<p>{summary["summary"]}</p>')
                html_parts.append('<div class="meta">')
                html_parts.append(f'Published: {self._format_date(summary["published_date"])} | ')
                html_parts.append(f'<a href="{summary["link"]}">Read full article</a>')
                html_parts.append('</div>')
                html_parts.append('</div>')
        
        html_parts.append("""
        <div class="footer">
            <p>This digest was automatically generated.</p>
            <p>To update your search preferences, visit the settings page.</p>
        </div>
        </body>
        </html>
        """)
        
        return "".join(html_parts)
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display."""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return date_str
    
    def _log_operation(self, operation_type: str, status: str, message: str, items_processed: int) -> None:
        """Log operation to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO processing_log (operation_type, status, message, items_processed)
                VALUES (?, ?, ?, ?)
            """, (operation_type, status, message, items_processed))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error logging operation: {e}")
        finally:
            conn.close()


def send_test_email():
    """Send a test email to verify configuration."""
    sender = EmailSender()
    
    subject = "Test Email - Retail Price Cut Summary App"
    body_text = """
This is a test email from the Retail Price Cut Summary App.

If you received this email, your email configuration is working correctly!

Configuration details:
- Email service: {}
- From: {}
- To: {}

Best regards,
Retail Price Cut Summary App
""".format(
        "SendGrid" if sender.use_sendgrid else "SMTP",
        Config.SENDGRID_FROM_EMAIL if sender.use_sendgrid else Config.SMTP_FROM_EMAIL,
        Config.SENDGRID_TO_EMAIL if sender.use_sendgrid else Config.SMTP_TO_EMAIL
    )
    
    success = sender.send_email(subject, body_text)
    
    if success:
        print("Test email sent successfully!")
    else:
        print("Failed to send test email. Check your configuration and logs.")
    
    return success


if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Send test email
        send_test_email()
    else:
        # Send daily digest
        digest = DailyDigest()
        success = digest.send_daily_digest()
        
        if success:
            print("Daily digest sent successfully!")
        else:
            print("Failed to send daily digest.")