from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random

def get_chatbot_response(message):
    """Intelligent chatbot responses for BOCRA"""
    message = message.lower().strip()
    
    # 1. CONTACT INFORMATION
    if any(word in message for word in ['contact', 'phone', 'call', 'email', 'address', 'location', 'office', 'reach']):
        return """📞 BOCRA Contact Information:
        
📍 Physical Address: Plot 50671, Prime Plaza, Gaborone, Botswana

📞 Phone: +267 123 4567
📠 Fax: +267 123 4568

📧 Emails:
• General: info@bocra.org.bw
• Complaints: complaints@bocra.org.bw
• Licensing: licensing@bocra.org.bw

🕒 Working Hours: Monday - Friday, 8:00 AM - 5:00 PM

Is there anything specific you'd like to know about our offices?"""
    
    # 2. COMPLAINTS
    elif any(word in message for word in ['complaint', 'complain', 'issue', 'problem', 'report']):
        return """📝 How to File a Complaint with BOCRA:

1️⃣ Online: Click 'Submit Complaint' in the Services menu or from your dashboard
2️⃣ Email: Send details to complaints@bocra.org.bw
3️⃣ Phone: Call +267 123 4567
4️⃣ In-person: Visit our Gaborone office

📋 What to include:
• Your name and contact details
• Company/service provider name
• Description of the issue
• Dates and times
• Any supporting documents

✅ You can track your complaint status from your dashboard.

Would you like to submit a complaint now?"""
    
    # 3. LICENSING
    elif any(word in message for word in ['license', 'licence', 'apply', 'application', 'approval']):
        return """📜 License Information:

We offer the following licenses:
• ✈️ Aircraft Radio License
• 📡 Cellular Network License
• 📺 Broadcasting License
• 📮 Postal Services License

📝 Application Process:
1. Click 'Apply for License' in the Services menu
2. Fill in your business details
3. Complete the specific license form
4. Submit for review

⏱️ Processing time: 5-10 business days
💰 Fees: Vary by license type

Would you like to know more about a specific license type?"""
    
    # 4. TYPE APPROVAL
    elif any(word in message for word in ['type approval', 'approval', 'equipment', 'device', 'certification']):
        return """🔧 Type Approval Information:

What is Type Approval?
Equipment certification to ensure compliance with BOCRA technical standards.

📱 Equipment that needs approval:
• Mobile phones and devices
• Radio equipment
• Network infrastructure
• Broadcasting equipment

📋 Process:
1. Submit application with equipment specs
2. Technical review and testing
3. Approval or rejection notification

⏱️ Processing time: 10-15 business days

Need help with a specific device?"""
    
    # 5. TELECOMMUNICATIONS
    elif any(word in message for word in ['telecom', 'telecommunications', 'network', 'signal', 'coverage', 'quality']):
        return """📡 Telecommunications Services:

BOCRA regulates:
• Mobile network operators
• Fixed line services
• Internet service providers

📊 Quality of Service (QoS):
We monitor:
• Call completion rates
• Network availability
• Data speeds
• Service reliability

🔍 Consumer Rights:
• Right to quality service
• Right to file complaints
• Right to information

Experiencing network issues? We can help you file a complaint."""

    # 6. BROADCASTING
    elif any(word in message for word in ['broadcast', 'tv', 'television', 'radio', 'channel', 'content']):
        return """📺 Broadcasting Services:

BOCRA regulates:
• Television broadcasters
• Radio stations
• Digital platforms

📜 Types of Licenses:
• Commercial broadcasting
• Community broadcasting
• Subscription broadcasting

⚖️ Content Guidelines:
• Fair and balanced reporting
• Protection of minors
• Local content requirements

🎯 Digital Migration:
Botswana is transitioning to digital broadcasting. Need information about this?"""
    
    # 7. POSTAL SERVICES
    elif any(word in message for word in ['post', 'postal', 'mail', 'courier', 'package']):
        return """✉️ Postal Services Regulation:

BOCRA oversees:
• BotswanaPost
• Private courier services
• International mail services

📋 Key Responsibilities:
• Licensing postal operators
• Monitoring service quality
• Consumer protection
• Universal service obligation

📮 Issues we handle:
• Delayed mail delivery
• Lost packages
• Service quality complaints

Need to file a postal service complaint?"""
    
    # 8. INTERNET & ICT
    elif any(word in message for word in ['internet', 'ict', 'cyber', 'security', 'data', 'digital']):
        return """💻 Internet & ICT Services:

BOCRA promotes:
• Internet connectivity
• Digital transformation
• Cybersecurity awareness

🔐 Internet Governance:
• Domain name management
• IP address allocation
• Internet exchange points

🛡️ Cybersecurity Tips:
• Use strong passwords
• Enable two-factor authentication
• Keep software updated
• Report suspicious activities

🚀 Digital Botswana:
We're working towards a digitally connected society. How can we help?"""
    
    # 9. ACCOUNT & DASHBOARD
    elif any(word in message for word in ['account', 'dashboard', 'profile', 'password', 'login', 'register']):
        return """👤 Account & Dashboard Help:

📝 Create Account:
Click 'Register' in the top menu

🔐 Login:
Use your username and password

🎛️ Dashboard Features:
• Track complaints
• View license applications
• Update profile
• Receive notifications

🔑 Forgot Password?
Click 'Forgot Password?' on the login page

Need help accessing your account?"""
    
    # 10. GENERAL INFORMATION
    elif any(word in message for word in ['about', 'mission', 'vision', 'history', 'who is', 'what is bocra', 'bocra']):
        return """🏛️ About BOCRA:

Botswana Communications Regulatory Authority was established in 2013 to regulate the communications sector in Botswana.

🎯 Our Mission:
To regulate the Communications sector for the promotion of competition, innovation, consumer protection and universal access.

👁️ Our Vision:
A connected and Digitally Driven Society.

📜 Our Mandate:
• Telecommunications regulation
• Broadcasting oversight
• Postal services supervision
• Internet governance
• Spectrum management
• Consumer protection

We're committed to serving Botswana's communications needs!"""
    
    # 11. FEES & PAYMENTS
    elif any(word in message for word in ['fee', 'cost', 'price', 'payment', 'pay', 'money']):
        return """💰 Fees & Payments:

📄 Application Fees:
• License application: P500 - P5,000 (varies by type)
• Type approval: P1,000 - P3,000
• Renewal fees: 50% of application fee

💳 Payment Methods:
• Online banking
• Bank deposit
• In-person at our office

📋 Bank Details:
Bank: Bank of Botswana
Account: BOCRA Licensing Account

For exact fees for specific licenses, please contact our licensing department at licensing@bocra.org.bw"""
    
    # 12. FAQ FALLBACK
    elif any(word in message for word in ['help', 'faq', 'what can you do', 'how can you help']):
        return """🤖 I can help you with:

📞 Contact information
📝 Filing complaints
📜 License applications
🔧 Type approval
📡 Telecommunications issues
📺 Broadcasting
✉️ Postal services
💻 Internet & ICT
👤 Account management
🏛️ About BOCRA
💰 Fees and payments

Just ask me anything about these topics!"""
    
    # GREETINGS
    elif any(word in message for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        greetings = [
            "Hello! 👋 How can I assist you with BOCRA services today?",
            "Hi there! Welcome to BOCRA Digital Platform. What can I help you with?",
            "Greetings! I'm your BOCRA Assistant. Need help with licenses, complaints, or information?",
            "Hello! How may I assist you today? Ask me about BOCRA services, contact info, or file a complaint!"
        ]
        return random.choice(greetings)
    
    # DEFAULT RESPONSE
    else:
        responses = [
            "I'm here to help! You can ask me about:\n• Contact information 📞\n• Filing complaints 📝\n• License applications 📜\n• Type approval 🔧\n• Telecommunications 📡\n• Account help 👤\n\nWhat would you like to know?",
            "I'm not sure I understand. Try asking about:\n- 'How to file a complaint'\n- 'Contact BOCRA'\n- 'Apply for a license'\n- 'About BOCRA'\n\nHow can I help you today?",
            "Let me help! Would you like information about complaints, licenses, contact details, or something else? Just let me know!",
            "I can assist with many things! Try: 'contact', 'complaint', 'license', 'type approval', 'about', or 'account'."
        ]
        return random.choice(responses)

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            if message:
                response = get_chatbot_response(message)
                return JsonResponse({'response': response})
            else:
                return JsonResponse({'response': "Please type a message."})
        except:
            return JsonResponse({'response': "Sorry, something went wrong. Please try again."})
    
    return JsonResponse({'response': "Send a POST request with a message."})