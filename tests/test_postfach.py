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
