"""
Knowledge Base Seeder Script
Run this to populate your RAG system with initial content
"""

import asyncio
import httpx
import os

# Update this to your deployed backend URL
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

# Sample knowledge base content - customize for your business
KNOWLEDGE_BASE = [
    {
        "title": "Welcome to TechCorp",
        "content": """
        TechCorp is a leading provider of cloud-based software solutions. 
        We help businesses streamline their operations with cutting-edge technology.
        Our mission is to make powerful tools accessible to everyone.
        Founded in 2020, we now serve over 10,000 customers worldwide.
        """,
        "category": "about"
    },
    {
        "title": "Pricing Plans Overview",
        "content": """
        We offer three pricing tiers to fit your needs:
        
        STARTER PLAN - $9/month
        - Up to 5 users
        - 10GB storage
        - Email support
        - Basic analytics
        
        PROFESSIONAL PLAN - $29/month
        - Up to 25 users
        - 100GB storage
        - Priority support
        - Advanced analytics
        - API access
        
        ENTERPRISE PLAN - Custom pricing
        - Unlimited users
        - Unlimited storage
        - Dedicated support
        - Custom integrations
        - SLA guarantee
        
        All plans include a 14-day free trial. No credit card required.
        """,
        "category": "pricing"
    },
    {
        "title": "Getting Started Guide",
        "content": """
        Welcome! Here's how to get started with TechCorp:
        
        Step 1: Create your account at app.techcorp.com
        Step 2: Verify your email address
        Step 3: Complete the onboarding wizard
        Step 4: Invite your team members
        Step 5: Connect your first integration
        
        Our setup wizard guides you through each step. Most users are up and running in under 10 minutes.
        
        Need help? Chat with our AI assistant or contact support@techcorp.com
        """,
        "category": "guides"
    },
    {
        "title": "Password Reset FAQ",
        "content": """
        HOW TO RESET YOUR PASSWORD:
        
        1. Go to app.techcorp.com/login
        2. Click "Forgot Password"
        3. Enter your email address
        4. Check your inbox for the reset link
        5. Click the link and create a new password
        
        The reset link expires after 24 hours.
        
        PASSWORD REQUIREMENTS:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one number
        - At least one special character
        
        If you don't receive the email, check your spam folder or contact support.
        """,
        "category": "faq"
    },
    {
        "title": "Billing and Invoices",
        "content": """
        BILLING FAQ:
        
        When am I charged?
        - Monthly plans: Charged on the same date each month
        - Annual plans: Charged once per year (with 20% discount)
        
        How do I update my payment method?
        - Go to Settings > Billing > Payment Methods
        - Add a new card or update existing
        
        How do I download invoices?
        - Go to Settings > Billing > Invoice History
        - Click download on any invoice
        
        How do I cancel my subscription?
        - Go to Settings > Billing > Plan
        - Click "Cancel Subscription"
        - You'll retain access until the end of your billing period
        
        We accept Visa, Mastercard, American Express, and PayPal.
        """,
        "category": "billing"
    },
    {
        "title": "API Documentation Overview",
        "content": """
        Our REST API allows you to integrate TechCorp with your existing tools.
        
        BASE URL: https://api.techcorp.com/v1
        
        AUTHENTICATION:
        All requests require an API key in the header:
        Authorization: Bearer YOUR_API_KEY
        
        RATE LIMITS:
        - Starter: 100 requests/minute
        - Professional: 500 requests/minute
        - Enterprise: Custom limits
        
        COMMON ENDPOINTS:
        GET /users - List all users
        POST /users - Create new user
        GET /projects - List all projects
        POST /projects - Create new project
        
        Full documentation: docs.techcorp.com/api
        """,
        "category": "api"
    },
    {
        "title": "Contact and Support Hours",
        "content": """
        SUPPORT CHANNELS:
        
        AI Chat Assistant: Available 24/7
        Email: support@techcorp.com
        Phone: +1 (555) 123-4567
        
        SUPPORT HOURS (Human Agents):
        Monday - Friday: 9 AM - 6 PM EST
        Saturday: 10 AM - 4 PM EST
        Sunday: Closed
        
        Enterprise customers have access to 24/7 priority support.
        
        RESPONSE TIMES:
        - AI Chat: Instant
        - Email: Within 24 hours
        - Phone: Average wait 5 minutes
        - Enterprise: Within 1 hour
        
        OFFICE ADDRESS:
        TechCorp Inc.
        123 Innovation Drive
        San Francisco, CA 94105
        """,
        "category": "contact"
    },
    {
        "title": "Integrations",
        "content": """
        TechCorp integrates with 100+ popular tools:
        
        PRODUCTIVITY:
        - Slack
        - Microsoft Teams
        - Google Workspace
        - Notion
        
        CRM:
        - Salesforce
        - HubSpot
        - Pipedrive
        
        DEVELOPMENT:
        - GitHub
        - GitLab
        - Jira
        - Linear
        
        MARKETING:
        - Mailchimp
        - Sendgrid
        - Google Analytics
        
        PAYMENTS:
        - Stripe
        - PayPal
        - Square
        
        Setting up integrations:
        1. Go to Settings > Integrations
        2. Find your app
        3. Click "Connect"
        4. Authorize access
        
        Need a custom integration? Contact our enterprise team.
        """,
        "category": "integrations"
    },
    {
        "title": "Data Security and Privacy",
        "content": """
        Your data security is our top priority.
        
        SECURITY MEASURES:
        - AES-256 encryption at rest
        - TLS 1.3 encryption in transit
        - SOC 2 Type II certified
        - GDPR compliant
        - Regular third-party audits
        
        DATA CENTERS:
        - Primary: AWS US-East (Virginia)
        - Backup: AWS EU-West (Ireland)
        - 99.9% uptime SLA
        
        YOUR RIGHTS:
        - Export your data anytime
        - Delete your account and all data
        - Access audit logs (Professional+)
        
        We never sell your data to third parties.
        
        Full privacy policy: techcorp.com/privacy
        Security whitepaper: techcorp.com/security
        """,
        "category": "security"
    },
    {
        "title": "Troubleshooting - Common Issues",
        "content": """
        COMMON ISSUES AND SOLUTIONS:
        
        Issue: Can't log in
        Solution: Clear browser cache, try incognito mode, or reset password
        
        Issue: Slow performance
        Solution: Check your internet connection, try a different browser, disable extensions
        
        Issue: Missing data
        Solution: Check filters, refresh the page, check the trash folder
        
        Issue: Integration not syncing
        Solution: Disconnect and reconnect the integration, check permissions
        
        Issue: Email notifications not working
        Solution: Check spam folder, verify email in settings, check notification preferences
        
        Issue: File upload failing
        Solution: Check file size (max 100MB), supported formats, try different browser
        
        Still having issues? Our AI assistant can help, or contact support@techcorp.com
        """,
        "category": "troubleshooting"
    }
]


async def seed_knowledge_base():
    """Seed the knowledge base with initial content"""
    print(f"🚀 Seeding knowledge base at {API_BASE_URL}")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        for item in KNOWLEDGE_BASE:
            try:
                response = await client.post(
                    f"{API_BASE_URL}/api/knowledge/add",
                    json=item,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    print(f"✅ Added: {item['title']}")
                else:
                    print(f"❌ Failed: {item['title']} - {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {item['title']} - {e}")
    
    print("=" * 50)
    print("✨ Knowledge base seeding complete!")
    
    # Get stats
    try:
        async with httpx.AsyncClient() as client:
            stats = await client.get(f"{API_BASE_URL}/api/stats")
            if stats.status_code == 200:
                data = stats.json()
                print(f"📊 Total documents: {data.get('knowledge_items', 'N/A')}")
    except:
        pass


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
