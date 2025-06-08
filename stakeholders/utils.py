# stakeholders/utils.py

import google.generativeai as genai
from django.conf import settings
from .models import StakeholderInsight, Activity

def initialize_gemini():
    """Initialize the Gemini API with the API key from settings"""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_stakeholder_insights(stakeholder, user):
    """Generate insights for a stakeholder using Gemini AI"""
    model = initialize_gemini()
    if not model:
        return "Gemini API key not configured. Please add your API key to .env file."
    
    # Create the prompt
    prompt = f"""
    Analyze this stakeholder profile and provide 3-5 actionable engagement recommendations:
    
    Name: {stakeholder.name}
    Role: {stakeholder.role}
    Organization: {stakeholder.organization}
    Influence Level: {stakeholder.influence_level}
    Interest Level: {stakeholder.interest_level}
    Current Engagement: {stakeholder.engagement_strategy}
    Desired Engagement: {stakeholder.desired_engagement}
    Quadrant: {stakeholder.get_quadrant()}
    Notes: {stakeholder.notes}
    
    Provide specific, actionable recommendations for improving engagement with this stakeholder.
    Format as a numbered list with brief explanations for each recommendation.
    """
    
    try:
        # Call Gemini API
        response = model.generate_content(prompt)
        insight_text = response.text
        
        # Create insight record
        insight = StakeholderInsight.objects.create(
            stakeholder=stakeholder,
            insight_text=insight_text,
            confidence_score=0.85,  # Default confidence score
            generated_by=user
        )
        
        # Log activity
        Activity.objects.create(
            user=user,
            activity_type='ai_insight',
            stakeholder_name=stakeholder.name,
            stakeholder_id=stakeholder.id,
            description=f"Generated AI insights for {stakeholder.name}"
        )
        
        return insight
    
    except Exception as e:
        return f"Error generating insights: {str(e)}"

def generate_stakeholder_report(user):
    """Generate a summary report of all stakeholders for a user using Gemini AI"""
    model = initialize_gemini()
    if not model:
        return "Gemini API key not configured. Please add your API key to .env file."
    
    from .models import Stakeholder
    
    stakeholders = Stakeholder.objects.filter(created_by=user)
    
    # Generate summary statistics
    stats = {
        'total': stakeholders.count(),
        'high_influence': stakeholders.filter(influence_level='High').count(),
        'high_interest': stakeholders.filter(interest_level='High').count(),
        'manage_closely': sum(1 for s in stakeholders if s.get_quadrant() == "Manage Closely"),
        'keep_satisfied': sum(1 for s in stakeholders if s.get_quadrant() == "Keep Satisfied"),
        'keep_informed': sum(1 for s in stakeholders if s.get_quadrant() == "Keep Informed"),
        'monitor': sum(1 for s in stakeholders if s.get_quadrant() == "Monitor"),
    }
    
    # Calculate engagement gaps
    engagement_gaps = sum(1 for s in stakeholders if s.get_desired_engagement_level_value() > s.get_engagement_level_value())
    stats['engagement_gaps'] = engagement_gaps
    
    # Generate the prompt for Gemini
    prompt = f"""
    Generate a stakeholder management report summary based on the following data:
    
    Total Stakeholders: {stats['total']}
    High Influence Stakeholders: {stats['high_influence']}
    High Interest Stakeholders: {stats['high_interest']}
    Stakeholders by Quadrant:
      - Manage Closely: {stats['manage_closely']}
      - Keep Satisfied: {stats['keep_satisfied']}
      - Keep Informed: {stats['keep_informed']}
      - Monitor: {stats['monitor']}
    Engagement Gaps (stakeholders whose current engagement is below desired level): {stats['engagement_gaps']}
    
    Format the report as:
    1. Executive Summary (brief overview)
    2. Stakeholder Distribution Analysis (analyze the quadrant distribution)
    3. Engagement Gap Analysis (discuss the engagement gaps)
    4. Recommendations (3-4 strategic recommendations)
    
    Make it professional, concise, and actionable.
    """
    
    try:
        # Call Gemini API
        response = model.generate_content(prompt)
        report_text = response.text
        
        return report_text
    
    except Exception as e:
        return f"Error generating report: {str(e)}"
