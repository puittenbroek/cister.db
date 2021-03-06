from datetime import datetime
from datetime import timedelta
import hashlib
import logging
from cister.db.models.cister import DBSession
from cister.db.models.cister import User
from cister.db.views.viewbase import BaseCisterView
from cister.db.views.index import UnauthroziedView
from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.renderers import get_renderer
from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import remember
from pyramid.url import route_url
from pyramid.security import has_permission
from pyramid.security import view_execution_permitted

logger = logging.getLogger(__name__)

class LoginView(BaseCisterView):

    def __init__(self, request):

        self.request = request
        self._coupon = ''

    def __call__(self):

        """ login view callable """

        # convenient method to set Cache-Control and Expires headers
        self.request.response.cache_expires = 0

        dbsession = DBSession()

        params = self.request.params
        login_url = route_url('login', self.request)
        message = ''

        # playerid, password from cookie
        playerid = ''
        password = ''
        passwordFromCookie = False
        lc = self.request.cookies.get('cis_login_credentials', '')
        if lc:
            lc = lc.split('|')
            if len(lc) == 3:
                passwordFromCookie = True
                playerid = lc[0]
                password = lc[1]

        activeUser = User()
        activeUser.playerid = playerid
        activeUser.password = password

        user = None
        errors = {}
        passwordOk = False
        referrer = self.request.url

        if referrer == login_url:
            referrer = '/'

        came_from = self.request.params.get('came_from', referrer)
        url = came_from
        logged_in = authenticated_userid(self.request)
        headers = ''

        initial_login = not logged_in

        storeplayeridPwd = params.get('remember', '')

        # if already logged in and requesting this page, redirect to forbidden

        if logged_in:
            message = 'You do not have the required permissions to see this page.'
            return dict(
                    message=message,
                    url=url,
                    came_from=came_from,
                    password=password,
                    user=activeUser,
                    headers=headers,
                    errors=errors,
                    logged_in=logged_in,
                    remember=storeplayeridPwd
                    )
        # check whether we are asked to do an autologin (from pwdreset.py)
        autologin = 0 #self.request.session.pop_flash(queue='autologin')

        # 'SECURITY RISK'
        forcelogin = lc and self.request.params.get('forcelogin', '')
        if forcelogin or autologin or 'form.submitted' in params:

            if autologin:
                autologin = autologin[0].split('|')
                playerid = autologin[0]
                password = autologin[1] #encrypted
            elif forcelogin:
                pass
            else:
                playerid = params['playerid']
                # when we get a password from a cookie, we already receive it encrypted. If not, encrypt it here
                password = (passwordFromCookie and password) or params['password']

            if not password:
                errors['password'] = "Enter your password"
            else:
                # if autologin, we already receive it encrypted. If not, encrypt it here
                password = ((forcelogin or autologin) and password) or hashlib.md5(params['password']).hexdigest()

            if not playerid:
                errors['playerid'] = "Enter your player id"

            if playerid and password:
                user = dbsession.query(User).filter_by(playerid=playerid).first()

                if user:
                    passwordOk = (user.password == password)
                if not user:
                    message = 'You do not have a CIS account'
                elif user.banned:
                    message = 'Your account has been banned.'
                elif not user.activated:
                    message = 'Your account has not yet been activated'
                elif not passwordOk:
                    message = 'Your account/password do not match' 
                else:
                    
                    # READY TO LOGIN, SOME FINAL CHECKS
                    now = datetime.now()

                    headers = remember(self.request, user.playerid)
                    last_login = now.strftime('%Y-%m-%d %H:%M:%S')
                    user.last_web = last_login

                    response = HTTPFound()
                    user.last_login = last_login
                    response.headers = headers

                    response.content_type = 'text/html'
                    response.charset = 'UTF-8' 
                    if storeplayeridPwd:
                        cookie_val = '%s|%s' % (playerid, password)
                        response.set_cookie('cis_login_credentials', cookie_val, max_age=timedelta(days=365), path='/')

                    response.location = came_from
                    if (not forcelogin) and (not storeplayeridPwd):
                        response.delete_cookie('cis_login_credentials')

                    response.cache_control = 'no-cache'
                    return response

            activeUser.playerid = playerid

        storeplayeridPwd = self.request.cookies.get('cis_login_credentials') and '1' or ''
        return dict(
                    message=message,
                    url=url,
                    came_from=came_from,
                    password=password,
                    user=activeUser,
                    headers=headers,
                    errors=errors,
                    logged_in=logged_in,
                    remember=storeplayeridPwd
                    )

class LogoutView(object):

    def __init__(self, request):

        self.request = request

    @classmethod
    def do_logout(self, request, location):
        """ do the logout """
        # convenient method to set Cache-Control and Expires headers
        request.response.cache_expires = 0

        headers = forget(request)
        response = HTTPFound(location=location, headers=headers)
        response.delete_cookie('cis_account', path="/")
        response.cache_control = 'no-cache'

        request.session.pop_flash('token')
        return response


    def __call__(self):
        """ logout view callable; deactivate cookie """

        return LogoutView.do_logout(self.request, route_url('index', self.request))
