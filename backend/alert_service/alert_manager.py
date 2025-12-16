"""Alert Manager for DAO Proposal Monitoring"""
import os
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertManager:
    """Manages alerts for investment funds monitoring DAO proposals"""
    
    def __init__(self, db_url: Optional[str] = None, smtp_config: Optional[Dict] = None):
        self.db_url = db_url or os.getenv('DATABASE_URL', 'sqlite:///dao_analytics.db')
        try:
            self.engine = create_engine(self.db_url)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            print(f"Warning: Database initialization failed: {e}")
            self.engine = None
            self.Session = None        
        # SMTP configuration for email alerts
        self.smtp_config = smtp_config or {
            'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            'port': int(os.getenv('SMTP_PORT', 587)),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD'),
            'from_email': os.getenv('ALERT_FROM_EMAIL', 'alerts@dao-data-ai.com')
        }
        
        # Alert thresholds
        self.thresholds = {
            'high_impact_voting_power': 0.1,  # 10% of total voting power
            'large_treasury_request': 100000,  # $100k USD
            'negative_sentiment_threshold': -0.3,
            'high_risk_score': 0.7,
            'voting_deadline_hours': 24  # Alert 24h before deadline
        }
    
    def check_high_impact_proposal(self, proposal: Dict) -> Optional[Dict]:
        """Check if proposal has high impact criteria"""
        alerts = []
        
        # Check voting power concentration
        if proposal.get('top_voter_power', 0) > self.thresholds['high_impact_voting_power']:
            alerts.append({
                'type': 'HIGH_VOTING_CONCENTRATION',
                'severity': 'HIGH',
                'message': f"Proposal {proposal['id']}: Top voter holds {proposal['top_voter_power']:.1%} of voting power"
            })
        
        # Check treasury request size
        if proposal.get('requested_amount', 0) > self.thresholds['large_treasury_request']:
            alerts.append({
                'type': 'LARGE_TREASURY_REQUEST',
                'severity': 'CRITICAL',
                'message': f"Proposal {proposal['id']}: Requesting ${proposal['requested_amount']:,.0f} from treasury"
            })
        
        # Check negative sentiment
        if proposal.get('sentiment_score', 0) < self.thresholds['negative_sentiment_threshold']:
            alerts.append({
                'type': 'NEGATIVE_SENTIMENT',
                'severity': 'MEDIUM',
                'message': f"Proposal {proposal['id']}: Negative community sentiment detected ({proposal['sentiment_score']:.2f})"
            })
        
        # Check high risk score
        if proposal.get('risk_score', 0) > self.thresholds['high_risk_score']:
            alerts.append({
                'type': 'HIGH_RISK',
                'severity': 'HIGH',
                'message': f"Proposal {proposal['id']}: High risk score ({proposal['risk_score']:.2f})"
            })
        
        return alerts if alerts else None
    
    def check_deadline_approaching(self, proposal: Dict) -> Optional[Dict]:
        """Check if proposal voting deadline is approaching"""
        if 'end_date' not in proposal:
            return None
        
        end_date = datetime.fromisoformat(proposal['end_date'])
        hours_remaining = (end_date - datetime.now()).total_seconds() / 3600
        
        if 0 < hours_remaining <= self.thresholds['voting_deadline_hours']:
            return {
                'type': 'DEADLINE_APPROACHING',
                'severity': 'MEDIUM',
                'message': f"Proposal {proposal['id']}: Voting ends in {hours_remaining:.1f} hours"
            }
        
        return None
    
    def check_prediction_confidence(self, proposal: Dict) -> Optional[Dict]:
        """Alert on predictions with high confidence"""
        if 'prediction' not in proposal or 'confidence' not in proposal:
            return None
        
        if proposal['confidence'] > 0.8:
            outcome = 'PASS' if proposal['prediction'] > 0.5 else 'FAIL'
            return {
                'type': 'HIGH_CONFIDENCE_PREDICTION',
                'severity': 'INFO',
                'message': f"Proposal {proposal['id']}: Predicted to {outcome} with {proposal['confidence']:.1%} confidence"
            }
        
        return None
    
    def generate_alerts(self, proposal: Dict) -> List[Dict]:
        """Generate all applicable alerts for a proposal"""
        all_alerts = []
        
        # Check various alert conditions
        high_impact_alerts = self.check_high_impact_proposal(proposal)
        if high_impact_alerts:
            all_alerts.extend(high_impact_alerts)
        
        deadline_alert = self.check_deadline_approaching(proposal)
        if deadline_alert:
            all_alerts.append(deadline_alert)
        
        prediction_alert = self.check_prediction_confidence(proposal)
        if prediction_alert:
            all_alerts.append(prediction_alert)
        
        return all_alerts
    
    def format_alert_email(self, alerts: List[Dict], proposal: Dict) -> str:
        """Format alerts into HTML email"""
        severity_colors = {
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107',
            'INFO': '#17a2b8'
        }
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert {{ padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .proposal-info {{ background: #f8f9fa; padding: 15px; margin: 20px 0; }}
                h2 {{ color: #333; }}
            </style>
        </head>
        <body>
            <h2>DAO Proposal Alert: {proposal.get('title', proposal['id'])}</h2>
            
            <div class="proposal-info">
                <strong>Proposal ID:</strong> {proposal['id']}<br>
                <strong>DAO:</strong> {proposal.get('dao', 'Unknown')}<br>
                <strong>Status:</strong> {proposal.get('status', 'Active')}<br>
            </div>
            
            <h3>Alerts:</h3>
        """
        
        for alert in alerts:
            color = severity_colors.get(alert['severity'], '#6c757d')
            html += f"""
            <div class="alert" style="border-left: 4px solid {color};">
                <strong style="color: {color};">[{alert['severity']}] {alert['type']}</strong><br>
                {alert['message']}
            </div>
            """
        
        html += """
            <p style="margin-top: 30px;">
                <a href="https://www.sky-mind.com" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Full Analysis
                </a>
            </p>
        </body>
        </html>
        """
        
        return html
    
    def send_email_alert(self, recipients: List[str], subject: str, html_content: str) -> bool:
        """Send email alert to recipients"""
        if not self.smtp_config.get('username') or not self.smtp_config.get('password'):
            print("SMTP not configured, skipping email send")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            print(f"Alert email sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False
    
    def process_proposal_alerts(self, proposal: Dict, recipients: List[str]) -> Dict:
        """Process alerts for a proposal and send notifications"""
        alerts = self.generate_alerts(proposal)
        
        if not alerts:
            return {'status': 'no_alerts', 'proposal_id': proposal['id']}
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'INFO': 3}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 999))
        
        # Format email
        html_content = self.format_alert_email(alerts, proposal)
        subject = f"[DAO Alert] {alerts[0]['severity']}: {proposal.get('title', proposal['id'])}"
        
        # Send email
        email_sent = self.send_email_alert(recipients, subject, html_content)
        
        return {
            'status': 'alerts_generated',
            'proposal_id': proposal['id'],
            'alert_count': len(alerts),
            'alerts': alerts,
            'email_sent': email_sent
        }
    
    def monitor_proposals(self, proposals: List[Dict], recipients: List[str]) -> List[Dict]:
        """Monitor multiple proposals and generate alerts"""
        results = []
        
        for proposal in proposals:
            result = self.process_proposal_alerts(proposal, recipients)
            if result['status'] == 'alerts_generated':
                results.append(result)
        
        return results


if __name__ == "__main__":
    # Test with mock data
    manager = AlertManager()
    
    mock_proposal = {
        'id': 'ARB-001',
        'title': 'Treasury Allocation for Marketing Campaign',
        'dao': 'Arbitrum DAO',
        'status': 'Active',
        'requested_amount': 150000,
        'sentiment_score': -0.35,
        'risk_score': 0.75,
        'top_voter_power': 0.15,
        'prediction': 0.65,
        'confidence': 0.82,
        'end_date': '2025-01-20T23:59:59'
    }
    
    alerts = manager.generate_alerts(mock_proposal)
    print(f"Generated {len(alerts)} alerts:")
    for alert in alerts:
        print(f"  [{alert['severity']}] {alert['type']}: {alert['message']}")
    
    # Test email formatting (won't send without SMTP config)
    html = manager.format_alert_email(alerts, mock_proposal)
    print("\nEmail HTML generated successfully")
