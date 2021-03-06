from cister.db.models import DBSession
from cister.db.models import News
from cister.db.views import BaseCisterView
from pyramid.httpexceptions import HTTPFound
import webhelpers.paginate as paginate
from webhelpers.util import update_params


class NewsView(BaseCisterView):

    def list(self):
        def url_generator( ** kw):
            new_url = update_params(self.request.url, page=kw['page'])
            return new_url
        dbsession = DBSession()
        returnvalue = {}

        news = dbsession.query(News).order_by("created DESC")
        per_page = 10
        news = paginate.Page(news, page=int(self.request.params.get('page', 1)), items_per_page=per_page, url=url_generator, item_count=news.count())
        returnvalue['news'] = news

        return returnvalue


    def delete(self):
        session = DBSession()
        newsid = self.request.matchdict.get('newsid')
        newsitem = session.query(News).filter_by(news_id=newsid).one()
        if 'form.submitted' in self.request.params:
            session = DBSession()
            newsitem = session.query(News).filter_by(news_id=newsid)
            newsitem.delete()
            session.flush()
            return HTTPFound(location=self.request.route_url('newslist', message="Newsitem %s has been deleted" % newsid))
        delete_url = self.request.route_url('news_delete', newsid=newsid)
        return dict(news=newsitem, delete_url=delete_url)

    def add(self):
        if 'form.submitted' in self.request.params:
            session = DBSession()
            title = self.request.params['title']
            body = self.request.params['body']
            news = News(title, body)
            session.add(news)
            session.flush()
            return HTTPFound(location=self.request.route_url('newsdetail', newsid=news.news_id))
            
        save_url = self.request.route_url('news_add')
        news = News('', '')
        return dict(news=news, save_url=save_url)
    
    def detail(self):
        session = DBSession()
        newsid = self.request.matchdict.get('newsid')
        news = session.query(News).filter_by(news_id=newsid).one()
        return dict(news=news)
    
    def edit(self):
        session = DBSession()
        newsid = self.request.matchdict.get('newsid')
        news = session.query(News).filter_by(news_id=newsid).one()
        if 'form.submitted' in self.request.params:
            title = self.request.params['title']
            body = self.request.params['body']
            news.title = title
            news.body = body
            session.add(news)
            session.flush()
            return HTTPFound(location=self.request.route_url('newsdetail', newsid=news.news_id))

        save_url = self.request.route_url('newsedit', newsid=news.news_id)
        return dict(news=news, save_url=save_url)
