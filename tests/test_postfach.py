import unittest

from agent.postfach import jobs_aus_mail

PORTAL = {"name": "Stepstone", "link": "stepstone\\."}

MAIL = """
<html><body>
<a href="https://www.stepstone.de/stellenangebote--Social-Media-Videograf-Bremen--123.html">Social Media Videograf (m/w/d)</a>
<p>Muster GmbH</p><p>Bremen</p>
<a href="https://www.stepstone.de/stellenangebote--Content-Creator--456.html">Content Creator Freelance</a>
<p>Agentur X, Oldenburg</p>
<a href="https://www.stepstone.de/settings">Einstellungen ändern</a>
<a href="https://www.stepstone.de/unsubscribe">Abmelden</a>
</body></html>
"""

UMLEITUNG = """
<a href="https://u123.ct.sendgrid.net/ls/click?upn=abc">Videoproduktion für Social Media Kampagne</a>
<a href="https://u123.ct.sendgrid.net/ls/click?upn=xyz">Abmelden</a>
"""


class Postfach(unittest.TestCase):
    def test_jobs_mit_kontext(self):
        jobs = jobs_aus_mail(MAIL, PORTAL)
        self.assertEqual([j.titel for j in jobs], ["Social Media Videograf (m/w/d)", "Content Creator Freelance"])
        self.assertIn("Bremen", jobs[0].text)
        self.assertIn("Oldenburg", jobs[1].text)

    def test_klickzaehler_links(self):
        jobs = jobs_aus_mail(UMLEITUNG, {"name": "Malt", "link": "malt\\."})
        self.assertEqual([j.titel for j in jobs], ["Videoproduktion für Social Media Kampagne"])


if __name__ == "__main__":
    unittest.main()


BEBEE = """
<a href="https://bebee.com/api/t/c/x0">beBee</a>
<p>13 neue Stellen</p><p>Hallo Tim,</p>
<p>Social Influencer gesucht! Promoter (m/w/d)</p><p>Apollon GmbH · Bremen</p><p>3.000 €/Monat</p>
<a href="https://bebee.com/api/t/c/x1">Stelle ansehen</a>
<p>Content Creator &amp; Social Media (m/f/d)</p><p>UJAM Music Technology · Bremen</p>
<a href="https://bebee.com/api/t/c/x2">Stelle ansehen</a>
<a href="https://bebee.com/api/t/c/x3">Alle Stellen ansehen</a>
<a href="https://bebee.com/api/t/u/y?action=manage">Benachrichtigungen verwalten</a>
"""


class BeBee(unittest.TestCase):
    def test_titel_vor_button(self):
        jobs = jobs_aus_mail(BEBEE, {"name": "BeBee", "link": "bebee"})
        self.assertEqual([(j.titel, j.firma, j.ort) for j in jobs], [
            ("Social Influencer gesucht! Promoter (m/w/d)", "Apollon GmbH", "Bremen"),
            ("Content Creator & Social Media (m/f/d)", "UJAM Music Technology", "Bremen"),
        ])
        self.assertEqual(jobs[1].url, "https://bebee.com/api/t/c/x2")
