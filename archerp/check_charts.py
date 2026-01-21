
import frappe
import json

def execute():
    try:
        charts = frappe.get_all("Dashboard Chart", 
                               filters={"chart_name": ["like", "Sat%Trend%"]}, 
                               fields=["name", "chart_name", "chart_type", "type", "source", "value_based_on"])
        print(json.dumps(charts, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    execute()
