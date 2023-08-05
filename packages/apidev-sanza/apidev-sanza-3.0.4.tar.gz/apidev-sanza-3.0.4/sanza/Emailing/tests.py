# -*- coding: utf-8 -*-

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()
    
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from datetime import datetime
from model_mommy import mommy
from sanza.Crm import models
from sanza.Emailing.models import Emailing, MagicLink
from coop_cms.models import Newsletter
from django.core import management
from django.core import mail
from django.conf import settings
from coop_cms import tests as coop_cms_tests
from captcha.models import CaptchaStore
from django.utils import timezone
from django.contrib.sites.models import Site
from bs4 import BeautifulSoup as BS4
from sanza.Users.models import UserPreferences
from django.utils.translation import ugettext

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.is_staff = True
        self.user.save()
        self._login()

    def _login(self):
        return self.client.login(username="toto", password="abc")


class EmailingManagementTestCase(BaseTestCase):
    
    def now(self):
        if settings.USE_TZ:
            return datetime.now().replace(tzinfo=timezone.utc)
        else:
            return datetime.now()
    
    
    def test_view_newsletters_list(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        newsletter1 = mommy.make(Newsletter, subject='newsletter1')
        newsletter2 = mommy.make(Newsletter, subject='newsletter2')
        
        emailing1 = mommy.make(Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = self.now(), sending_dt = None)
        for c in contacts:
            emailing1.send_to.add(c)
        emailing1.save()
        
        emailing2 = mommy.make(Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SENDING,
            scheduling_dt = self.now(), sending_dt = None)
        emailing2.send_to.add(contacts[0])
        emailing2.save()
        
        emailing3 = mommy.make(Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SENT,
            scheduling_dt = self.now(), sending_dt = self.now())
        emailing3.send_to.add(contacts[-1])
        emailing3.save()
        
        response = self.client.get(reverse('emailing_newsletter_list'))
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'newsletter1')
        self.assertContains(response, 'newsletter2')
        
        self.assertContains(response, emailing1.get_info())
        self.assertContains(response, emailing2.get_info())
        self.assertContains(response, emailing3.get_info())

    def test_emailing_next_action(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        emailing = mommy.make(Emailing,
            status=Emailing.STATUS_EDITING,
            scheduling_dt = self.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        next_url = reverse('emailing_confirm_send_mail', args=[emailing.id])
        self.assertTrue(emailing.next_action().find(next_url))
        
        emailing.status = Emailing.STATUS_SCHEDULED
        emailing.save()
        next_url = reverse('emailing_cancel_send_mail', args=[emailing.id])
        self.assertTrue(emailing.next_action().find(next_url))
        
        emailing.status = Emailing.STATUS_SENDING
        emailing.save()
        self.assertEqual(emailing.next_action(), "")
        
        emailing.status = Emailing.STATUS_SENT
        emailing.save()
        self.assertEqual(emailing.next_action(), "")
        
    def test_view_magic_link(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        emailing = mommy.make(Emailing,
            status=Emailing.STATUS_SENT,
            scheduling_dt = self.now(), sending_dt = self.now())
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        emailing2 = mommy.make(Emailing)
        
        google = "http://www.google.fr"
        google_link = MagicLink.objects.create(emailing=emailing, url=google)
        for c in contacts:
            google_link.visitors.add(c)
        google_link.save()
        
        toto = "http://www.toto.fr"
        toto_link = MagicLink.objects.create(emailing=emailing, url=toto)
        toto_link.visitors.add(contacts[0])
        toto_link.save()
        
        titi = "http://www.titi.fr"
        titi_link = MagicLink.objects.create(emailing=emailing2, url=titi)
        titi_link.visitors.add(contacts[0])
        titi_link.save()
        
        url = reverse('emailing_view', args=[emailing.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, toto)
        self.assertContains(response, google)
        self.assertNotContains(response, titi)
        
    def test_confirm_sending(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        emailing = mommy.make(Emailing, status=Emailing.STATUS_EDITING)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        next_url = reverse('emailing_confirm_send_mail', args=[emailing.id])
        response = self.client.get(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)
        
        response = self.client.post(next_url, data={"scheduling_dt": "01/01/2120 00:00"})
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)
        
        response = self.client.post(next_url, data={"confirm": "1", "scheduling_dt": "01/01/2120 00:00"})
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SCHEDULED)
        self.assertNotEqual(emailing.scheduling_dt, None)
        if settings.USE_TZ:
            self.assertTrue(emailing.scheduling_dt > datetime.now().replace(tzinfo=timezone.get_current_timezone()))
        else:
            self.assertTrue(emailing.scheduling_dt > datetime.now())
            
        
        
    def test_cancel_sending(self):
        entity = mommy.make(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        emailing = mommy.make(Emailing, status=Emailing.STATUS_SCHEDULED, scheduling_dt=self.now())
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        next_url = reverse('emailing_cancel_send_mail', args=[emailing.id])
        response = self.client.get(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SCHEDULED)
        self.assertNotEqual(emailing.scheduling_dt, None)
        
        response = self.client.post(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SCHEDULED)
        self.assertNotEqual(emailing.scheduling_dt, None)
        
        response = self.client.post(next_url, data={"confirm": "1"})
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)
        
    

class SendEmailingTest(BaseTestCase):
    
    def setUp(self):
        super(SendEmailingTest, self).setUp()
        settings.COOP_CMS_FROM_EMAIL = 'toto@toto.fr'
        settings.COOP_CMS_REPLY_TO = 'titi@toto.fr'
        
        site = Site.objects.get_current()
        site.domain = settings.COOP_CMS_SITE_PREFIX
        site.save()
        
        
    def test_send_newsletter(self):
            
        entity = mommy.make(models.Entity, name="my corp")
        
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a><a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        
        emailing = mommy.make(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        management.call_command('emailing_scheduler', verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        
        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))
        
        self.assertEqual(len(mail.outbox), len(contacts))
        
        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)
        
        for email, contact in zip(outbox, contacts):
            self.assertEqual(email.to, [contact.get_email_address()])
            self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
            self.assertEqual(email.subject, newsletter_data['subject'])
            self.assertTrue(email.body.find(entity.name)>=0)
            #print email.body
            self.assertEqual(email.extra_headers['Reply-To'], settings.COOP_CMS_REPLY_TO)
            self.assertTrue(email.body.find(contact.fullname)>=0)
            self.assertTrue(email.alternatives[0][1], "text/html")
            self.assertTrue(email.alternatives[0][0].find(contact.fullname)>=0)
            self.assertTrue(email.alternatives[0][0].find(entity.name)>=0)
            viewonline_url = settings.COOP_CMS_SITE_PREFIX + reverse('emailing_view_online', args=[emailing.id, contact.uuid])
            self.assertTrue(email.alternatives[0][0].find(viewonline_url)>=0)
            unsubscribe_url = settings.COOP_CMS_SITE_PREFIX + reverse('emailing_unregister', args=[emailing.id, contact.uuid])
            self.assertTrue(email.alternatives[0][0].find(unsubscribe_url)>=0)
            
            #Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("mailto:me@me.fr")>0)
            
            #Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("#art1")>0)
            
            #check magic links
            self.assertTrue(MagicLink.objects.count()>0)
            
            #check an action has been created
            c = models.Contact.objects.get(id=contact.id)
            self.assertEqual(c.action_set.count(), 1)
            self.assertEqual(c.action_set.all()[0].subject, email.subject)
                
    def test_view_magic_link(self):
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Toto')
        emailing = mommy.make(Emailing)
        emailing.sent_to.add(contact)
        emailing.save()
        
        link = "http://www.google.fr"
        magic_link = MagicLink.objects.create(emailing=emailing, url=link)
        
        response = self.client.get(reverse('emailing_view_link', args=[magic_link.uuid, contact.uuid]))
        self.assertEqual(302, response.status_code)
        self.assertEqual(response['Location'], link)
        
        
    def test_unregister_mailinglist(self):
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Toto', accept_newsletter=True)
        emailing = mommy.make(Emailing)
        emailing.sent_to.add(contact)
        emailing.save()
        
        url = reverse('emailing_unregister', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        response = self.client.post(url, data={'unregister': True})
        self.assertEqual(200, response.status_code)
        
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.accept_newsletter, False)
    
    def test_view_online(self):
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Azerty', firstname='Albert')
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        emailing = mommy.make(Emailing, newsletter=newsletter)
        emailing.sent_to.add(contact)
        emailing.save()
        
        url = reverse('emailing_view_online', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, contact.fullname)
        self.assertEqual(MagicLink.objects.count(), 1)
        ml = MagicLink.objects.all()[0]
        self.assertContains(response, reverse('emailing_view_link', args=[ml.uuid, contact.uuid]))
        

class NewsletterTest(coop_cms_tests.NewsletterTest):
    def test_send_newsletter_template(self):
        def extra_checker(e):
            site = Site.objects.get(id=settings.SITE_ID)
            url = "http://"+site.domain+"/this-link-without-prefix-in-template"
            self.assertTrue(e.alternatives[0][0].find(url)>=0)
        super(NewsletterTest, self).test_send_test_newsletter('test/newsletter_contact.html')
        
class SubscribeTest(TestCase):
    
    def setUp(self):
        
        if not getattr(settings, 'SANZA_ALLOW_SINGLE_CONTACT', True):
            settings.SANZA_INDIVIDUAL_ENTITY_ID = models.EntityType.objects.create(name="particulier").id
        
        default_country = mommy.make(models.Zone, name=settings.SANZA_DEFAULT_COUNTRY, parent=None)
    
    def test_view_subscribe_newsletter(self):
        url = reverse("emailing_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    def test_view_email_subscribe_newsletter(self):
        url = reverse("emailing_email_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    def test_email_subscribe_newsletter(self):
        url = reverse("emailing_email_subscribe_newsletter")
        
        data = {
            'email': 'pdupond@apidev.fr',
        }
        
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)
        
        contact = models.Contact.objects.all()[0]
        
        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_email_done'))>=0)
        
        self.assertEqual(contact.email, data['email'])
        
        self.assertEqual(len(mail.outbox), 2) #email verification
        
        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification
        
        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        
    def test_email_subscribe_newsletter_no_email(self):
        url = reverse("emailing_email_subscribe_newsletter")
        
        data = {
            'email': '',
        }
        
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(200, response.status_code)
        soup = BS4(response.content)
        self.assertEqual(len(soup.select("ul.errorlist")), 1)
        self.assertEqual(models.Contact.objects.count(), 0)
        
        self.assertEqual(len(mail.outbox), 0) #email verification
        
    def test_email_subscribe_newsletter_invalid_email(self):
        url = reverse("emailing_email_subscribe_newsletter")
        
        data = {
            'email': 'coucou',
        }
        
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(200, response.status_code)
        soup = BS4(response.content)
        self.assertEqual(len(soup.select("ul.errorlist")), 1)
        self.assertEqual(models.Contact.objects.count(), 0)
        
        self.assertEqual(len(mail.outbox), 0) #email verification
        
        
    def test_subscribe_newsletter_no_email(self):
        group1 = mommy.make(models.Group, name="ABC", subscribe_form=True)
        
        url = reverse("emailing_subscribe_newsletter")
        
        data = {
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': str(group1.id),
        }
        self._patch_with_captcha(url, data)
        
        self.assertEqual(models.Contact.objects.count(), 0)
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 0)
        
        self.assertEqual(len(mail.outbox), 0)
        
    def test_subscribe_newsletter_message(self):
        url = reverse("emailing_subscribe_newsletter")
        
        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': "pierre.dupond@mon-mail.fr",
            'message': "Hello",
        }
        self._patch_with_captcha(url, data)
        
        self.assertEqual(models.Contact.objects.count(), 0)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)
        contact = models.Contact.objects.all()[0]
        
        self.assertEqual(contact.email, data["email"])
        self.assertEqual(contact.lastname, data["lastname"])
        self.assertEqual(contact.firstname, data["firstname"])
        
        self.assertEqual(1, contact.action_set.count())
        action = contact.action_set.all()[0]
        self.assertEqual(data["message"], action.detail)
        
        self.assertEqual(len(mail.outbox), 2) #email verification
        
        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification
        
        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
    
    def test_subscribe_newsletter_empty_message(self):
        url = reverse("emailing_subscribe_newsletter")
        
        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': "pierre.dupond@mon-mail.fr",
            'message': "",
        }
        self._patch_with_captcha(url, data)
        
        self.assertEqual(models.Contact.objects.count(), 0)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        
        self.assertEqual(models.Contact.objects.count(), 1)
        contact = models.Contact.objects.all()[0]
        
        self.assertEqual(contact.email, data["email"])
        self.assertEqual(contact.lastname, data["lastname"])
        self.assertEqual(contact.firstname, data["firstname"])
        
        self.assertEqual(0, contact.action_set.count())
        
        self.assertEqual(len(mail.outbox), 2) #email verification
        
        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification
        
        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        
        
    def test_subscribe_newsletter_no_entity(self):
        group1 = mommy.make(models.Group, name="ABC", subscribe_form=True)
        
        url = reverse("emailing_subscribe_newsletter")
        
        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': str(group1.id),
            'email': 'pdupond@apidev.fr',
        }
        self._patch_with_captcha(url, data)
        
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)
        
        contact = models.Contact.objects.all()[0]
        
        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid]))>=0)
        
        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])
        self.assertEqual(list(contact.entity.group_set.all()), [group1])
        
        self.assertEqual(len(mail.outbox), 2) #email verification
        
        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification
        
        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        
        
    def test_subscribe_newsletter_entity(self):
        group1 = mommy.make(models.Group, name="ABC", subscribe_form=True)
        group2 = mommy.make(models.Group, name="DEF", subscribe_form=True)
        
        url = reverse("emailing_subscribe_newsletter")
        
        entity_type = mommy.make(models.EntityType, name='Pro', subscribe_form=True)
        
        data = {
            'entity_type': entity_type.id,
            'entity': 'Toto',
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': 'pdupond@apidev.fr',
            'groups': [group1.id, group2.id],
        }
        self._patch_with_captcha(url, data)
        
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        
        self.assertEqual(models.Contact.objects.count(), 1)
        
        contact = models.Contact.objects.all()[0]
        
        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid]))>=0)
        
        self.assertEqual(contact.entity.name, data['entity'])
        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])
        self.assertEqual(list(contact.entity.group_set.all()), [group1, group2])
        
        self.assertEqual(len(mail.outbox), 2) #email verification
        
        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification
        
        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        
    def test_subscribe_newsletter_private_group(self):
        group1 = mommy.make(models.Group, name="ABC", subscribe_form=True)
        group2 = mommy.make(models.Group, name="DEF", subscribe_form=False)
        
        url = reverse("emailing_subscribe_newsletter")
        
        entity_type = mommy.make(models.EntityType, name='Pro', subscribe_form=True)
        data = {
            'entity_type': entity_type.id,
            'entity': 'Toto',
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': 'pdupond@apidev.fr',
            'groups': [group1.id, group2.id],
        }
        self._patch_with_captcha(url, data)
        
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
        self.assertEqual(models.Contact.objects.count(), 0)
        
        self.assertEqual(len(mail.outbox), 0) #email verification
        
    
    def test_view_subscribe_done(self):
        contact = mommy.make(models.Contact)
        url = reverse('emailing_subscribe_done', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        #unregister_url = reverse('emailing_unregister', args=[0, contact.uuid])
        #self.assertContains(response, unregister_url)
        
    def _patch_with_captcha(self, url, data):
        self.failUnlessEqual(CaptchaStore.objects.count(), 0)
        self.client.get(url)
        self.failUnlessEqual(CaptchaStore.objects.count(), 1)
        captcha = CaptchaStore.objects.all()[0]
        data.update({
            'captcha_0': captcha.hashkey,
            'captcha_1': captcha.response
        })
    
    def test_accept_newsletter(self, accept_newsletter=True, accept_3rdparty=True):
        url = reverse("emailing_subscribe_newsletter")
        
        data = {
            'entity_type': 0,
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'email': 'pdupond@apidev.fr',
            'accept_newsletter': accept_newsletter,
            'accept_3rdparty': accept_3rdparty,
        }
        
        self._patch_with_captcha(url, data)
        
        response = self.client.post(url, data=data, follow=False)
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)
        
        contact = models.Contact.objects.all()[0]
        
        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid]))>=0)
        
        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])
        self.assertEqual(contact.accept_newsletter, data['accept_newsletter'])
        self.assertEqual(contact.accept_3rdparty, data['accept_3rdparty'])
        self.assertEqual(contact.email_verified, False)
        
        self.assertEqual(len(mail.outbox), 2) #email verification
        
        verification_email = mail.outbox[1]
        self.assertEqual(verification_email.to, [contact.email]) #email verification
        url = reverse('emailing_email_verification', args=[contact.uuid])
        email_content = verification_email.message().as_string().decode('utf-8')
        self.assertTrue(email_content.find(url)>0) #email verification
        
        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        
    def test_refuse_newsletter(self):
        self.test_accept_newsletter(accept_newsletter=False, accept_3rdparty=False)
            
    def test_refuse_newsletter_accept_3rdparty(self):
        self.test_accept_newsletter(accept_newsletter=False, accept_3rdparty=True)
            
    def test_accept_newsletter_refuse_3rdparty(self):
        self.test_accept_newsletter(accept_newsletter=True, accept_3rdparty=False)
        
    def test_verify_email(self):
        self.client.logout()
        contact = mommy.make(models.Contact, email='toto@apidev.fr',
            accept_newsletter=True, accept_3rdparty=True, email_verified=False)
        
        url = reverse('emailing_email_verification', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email_verified, True)
        self.assertEqual(contact.accept_newsletter, True)
        self.assertEqual(contact.accept_3rdparty, True)
        
    def test_verify_email_no_newsletter(self):
        self.client.logout()
        contact = mommy.make(models.Contact, email='toto@apidev.fr',
            accept_newsletter=False, accept_3rdparty=False, email_verified=False)
        
        url = reverse('emailing_email_verification', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email_verified, True)
        self.assertEqual(contact.accept_newsletter, False)
        self.assertEqual(contact.accept_3rdparty, False)
        
    def test_verify_email_strange_uuid(self):
        self.client.logout()
        contact = mommy.make(models.Contact, email='toto@apidev.fr',
            accept_newsletter=False, accept_3rdparty=False, email_verified=False)
        
        url = reverse('emailing_email_verification', args=['abcd'])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.email_verified, False)
        
        
        
class EmailTrackingTest(BaseTestCase):
    
    def setUp(self):
        super(EmailTrackingTest, self).setUp()
        settings.COOP_CMS_FROM_EMAIL = 'toto@toto.fr'
        settings.COOP_CMS_REPLY_TO = 'titi@toto.fr'
        
        settings.COOP_CMS_SITE_PREFIX = "toto.fr"
        site = Site.objects.get_current()
        site.domain = "toto.fr"
        site.save()
        
    def test_track_image(self):
            
        entity = mommy.make(models.Entity, name="my corp")
        
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a><a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        
        emailing = mommy.make(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SENT,
            scheduling_dt = datetime.now(), sending_dt = datetime.now())
        for c in contacts:
            emailing.sent_to.add(c)
        emailing.save()
        
        self.assertEqual(emailing.opened_emails.count(), 0)
        
        for c in contacts[:-1]:
            tracking_url = reverse("emailing_email_tracking", args=[emailing.id, c.uuid])
            response = self.client.get(tracking_url)
            self.assertEqual(response.status_code, 200)
        
        self.assertEqual(emailing.opened_emails.count(), len(contacts)-1)
        for c in contacts[:-1]:
            self.assertTrue(c in list(emailing.opened_emails.all()))
        
        for c in contacts[-1:]:
            self.assertFalse(c in list(emailing.opened_emails.all()))
            
    def test_track_image_twice(self):
            
        entity = mommy.make(models.Entity, name="my corp")
        
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a><a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        
        emailing = mommy.make(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SENT,
            scheduling_dt = datetime.now(), sending_dt = datetime.now())
        for c in contacts:
            emailing.sent_to.add(c)
        emailing.save()
        
        self.assertEqual(emailing.opened_emails.count(), 0)
        
        for c in contacts[:-1]:
            tracking_url = reverse("emailing_email_tracking", args=[emailing.id, c.uuid])
            response = self.client.get(tracking_url)
            self.assertEqual(response.status_code, 200)
            
            response = self.client.get(tracking_url)
            self.assertEqual(response.status_code, 200)
        
        self.assertEqual(emailing.opened_emails.count(), len(contacts)-1)
        for c in contacts[:-1]:
            self.assertTrue(c in list(emailing.opened_emails.all()))
        
        for c in contacts[-1:]:
            self.assertFalse(c in list(emailing.opened_emails.all()))
            
    def test_send_newsletter_check_tracking(self):
            
        entity = mommy.make(models.Entity, name="my corp")
        
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a><a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        
        emailing = mommy.make(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        management.call_command('emailing_scheduler', verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        
        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))
        
        self.assertEqual(len(mail.outbox), len(contacts))
        
        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)
        
        for email, contact in zip(outbox, contacts):
            self.assertNotEqual(newsletter.get_site_prefix(), "")
            tracking_url = newsletter.get_site_prefix() + reverse("emailing_email_tracking",
                args=[emailing.id, contact.uuid])
            self.assertTrue(email.alternatives[0][1], "text/html")
            self.assertTrue(email.alternatives[0][0].find(tracking_url)>=0)

class ActionInFavoriteTestCase(BaseTestCase):

    def test_create_action_in_favorite(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, message_in_favorites=True)
        
        at = mommy.make(models.ActionType, name=ugettext(u"Message"))
        a = mommy.make(models.Action, type=at)
        
        self.assertEqual(1, u.user_favorite_set.count())
        fav = u.user_favorite_set.all()[0]
        self.assertEqual(a, fav.content_object)
        
    def test_create_action_not_in_favorite(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, message_in_favorites=False)
        
        at = mommy.make(models.ActionType, name=ugettext(u"Message"))
        a = mommy.make(models.Action, type=at)
        
        self.assertEqual(0, u.user_favorite_set.count())