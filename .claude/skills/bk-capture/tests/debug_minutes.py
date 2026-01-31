"""Debug minutes parser."""
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from minutes_parser import MinutesParser

transcript = """
Sprint Planning Meeting
Date: 2026/01/30
Attendees: @taro, @hanako, @john

Agenda:
1. Review last sprint
2. Plan next sprint
3. Discuss blockers

Discussion:
Taro: We completed 80% of planned tasks
Hanako: Database migration is ready

Action Items:
- Deploy to staging 明日 @taro
- Review PR this week @hanako
- Fix bugs 至急 @john

Next Meeting: 2026/02/06
"""

parser = MinutesParser()
minutes = parser.parse(transcript)

print("Title:", minutes["title"])
print("Date:", minutes["date"])
print("Attendees:", minutes["attendees"])
print("Attendees count:", len(minutes["attendees"]))
print("Agenda:", minutes["agenda"])
print("Agenda count:", len(minutes["agenda"]))
print("Action items count:", len(minutes["action_items"]))
for item in minutes["action_items"]:
    print(f"  - {item}")
print("Next meeting:", minutes["next_meeting"])
