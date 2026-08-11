from datetime import datetime

def generate_receipt():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"FCS-{timestamp}"
