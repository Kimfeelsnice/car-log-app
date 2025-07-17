from flask import render_template
from collections import defaultdict, Counter
from your_app import app
from your_app.models import FuelLog, TripLog, MaintenanceLog  # Adjust if needed
from your_app import db

@app.route('/report_log')
def report_log():
    # ----------- Fuel Report -----------
    fuel_data = db.session.query(FuelLog).all()
    fuel_summary = defaultdict(lambda: {'total_liters': 0, 'total_cost': 0, 'count': 0})
    for entry in fuel_data:
        summary = fuel_summary[entry.vehicle]
        summary['total_liters'] += entry.litres
        summary['total_cost'] += entry.cost
        summary['count'] += 1

    fuel_report = [
        {
            'vehicle': vehicle,
            'total_liters': data['total_liters'],
            'total_cost': data['total_cost'],
            'count': data['count']
        }
        for vehicle, data in fuel_summary.items()
    ]

    # ----------- Trip Report -----------
    trip_data = db.session.query(TripLog).all()
    trip_summary = defaultdict(lambda: {'total_distance': 0, 'count': 0, 'drivers': []})
    for entry in trip_data:
        summary = trip_summary[entry.vehicle]
        summary['total_distance'] += entry.distance
        summary['count'] += 1
        summary['drivers'].append(entry.driver)

    trip_report = [
        {
            'vehicle': vehicle,
            'total_distance': data['total_distance'],
            'count': data['count'],
            'driver': Counter(data['drivers']).most_common(1)[0][0] if data['drivers'] else 'N/A'
        }
        for vehicle, data in trip_summary.items()
    ]

    # ----------- Maintenance Report -----------
    maint_data = db.session.query(MaintenanceLog).all()
    maint_summary = defaultdict(lambda: {'total_cost': 0, 'count': 0, 'services': []})
    for entry in maint_data:
        summary = maint_summary[entry.vehicle]
        summary['total_cost'] += entry.cost
        summary['count'] += 1
        summary['services'].append(entry.service_type)

    maintenance_report = [
        {
            'vehicle': vehicle,
            'total_cost': data['total_cost'],
            'count': data['count'],
            'common_service': Counter(data['services']).most_common(1)[0][0] if data['services'] else 'N/A'
        }
        for vehicle, data in maint_summary.items()
    ]

    return render_template('report_log.html',
                           fuel_report=fuel_report,
                           trip_report=trip_report,
                           maintenance_report=maintenance_report)
