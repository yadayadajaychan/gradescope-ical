import json
import os
from datetime import datetime, timedelta

import dateparser

DATA_DIR = 'data'


def get_assignment_dict(title, course, due_date, link, submitted, late_due_date=None):
    return {
        'title': title,
        'course': course,
        'dueDate': dateparser.parse(due_date).strftime('%Y%m%dT%H%M%SZ'),  # sets to pseudo utc time
        'lateDueDate': dateparser.parse(late_due_date[14:]).strftime('%Y%m%dT%H%M%SZ') if late_due_date else None,
        'link': link,
        'submitted': submitted
    }


def save_data(var_name, obj):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    target = os.path.join(DATA_DIR, var_name + '.json')
    with open(target, 'w') as file:
        file.write(f'{json.dumps(obj, indent=2)}')


def fold_line(line, limit=75):
    # Split the line into parts based on the limit
    parts = [line[i:i + limit] for i in range(0, len(line), limit)]
    # Rejoin parts with CRLF followed by a whitespace to fold
    return "\r\n ".join(parts)


def json_to_ics(time_offset, json_path=os.path.join(DATA_DIR, 'assignments.json')):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    ics_str = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//github.com/jakobz5404/Gradescope-iCal-Integration//EN\r" \
              "\nCALSCALE:GREGORIAN\r\n "
    ics_str += "X-WR-CALNAME:Gradescope Assignments\r\n"
    uid = 1
    for course, course_assignments in data.items():
        for assignment in course_assignments:
            if not assignment['submitted']:
                uid = uid + 1
                if time_offset == 0:
                    time = assignment['dueDate']
                else:
                    time = datetime.strftime(datetime.strptime(assignment['dueDate'], '%Y%m%dT%H%M%SZ') - time_offset,
                                             '%Y%m%dT%H%M%SZ')
                event_details = (f"BEGIN:VEVENT\r\n"
                                 f"SUMMARY:{fold_line(assignment['title'])}\r\n"
                                 f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}\r\n"
                                 f"DTSTART:{time}\r\n"
                                 f"DTEND:{time}\r\n"
                                 f"LOCATION:{fold_line(assignment['course'])}\r\n"
                                 f"DESCRIPTION:{fold_line(assignment['link'])}\r\n"
                                 f"UID:{uid}\r\n"
                                 f"END:VEVENT\r\n")
                ics_str += event_details
                if assignment['lateDueDate']:
                    uid = uid + 1
                    if time_offset == 0:
                        time = assignment['lateDueDate']
                    else:
                        time = datetime.strftime(
                            datetime.strptime(assignment['lateDueDate'], '%Y%m%dT%H%M%SZ') - time_offset,
                            '%Y%m%dT%H%M%SZ')
                    event_details = (f"BEGIN:VEVENT\r\n"
                                     f"SUMMARY:{fold_line('Late Due Date: ' + assignment['title'])}\r\n"
                                     f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}\r\n"
                                     f"DTSTART:{time}\r\n"
                                     f"DTEND:{time}\r\n"
                                     f"LOCATION:{fold_line(assignment['course'])}\r\n"
                                     f"DESCRIPTION:{fold_line(assignment['link'])}\r\n"
                                     f"UID:{uid}\r\n"
                                     f"END:VEVENT\r\n")
                    ics_str += event_details
    ics_str += "END:VCALENDAR\r\n"
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    target = os.path.join(DATA_DIR, 'assignments.ics')
    with open(target, 'w') as file:
        file.write(ics_str)


def old_cleaner(json_path=os.path.join(DATA_DIR, 'assignments.json'), cutoff=180):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    cutoff_date = datetime.now() - timedelta(days=cutoff)
    data.items()
    for course, course_assignments in data.items():
        # Filter assignments that are newer than cutoff_date
        data[course] = [
            assignment for assignment in course_assignments
            if datetime.strptime(assignment['lateDueDate'] if assignment['lateDueDate'] else assignment['dueDate'],
                                 "%Y%m%dT%H%M%SZ") >= cutoff_date
        ]
    save_data("assignments", data)
