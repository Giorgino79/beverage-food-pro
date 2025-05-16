from django import template
from datetime import datetime
import locale

register = template.Library()

@register.inclusion_tag('current_datetime.html')
def show_current_datetime():
    try:
        locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'it_IT')
        except:
            pass
    
    now = datetime.now()
    
    return {
        'today_day': now.strftime('%A'),
        'today_date': now.strftime('%d %B %Y'),
        'current_time': now.strftime('%H:%M:%S'),
    }