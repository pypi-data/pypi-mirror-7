'use strict';

define(['js/postRequest', 'strings'], function(bashFn, strings) {
  i18n.init({
    resStore: strings,
    lng: 'ru',
    fallbackLng: 'en'
  });
  _.mixin(_.string.exports());
  
  describe('Post request', function() {
    var t;

    beforeEach(function() {
      var bash = bashFn(
        jasmine.createSpy(),
        jasmine.createSpy()
      );
      t = $('<div></div>').terminal(bash.handler, bash.object);
      t.exec('telnet coursify.ru 80');
    })

    it('success', function() {
      t.exec('POST /login HTTP/1.1');
      t.exec('HOST: coursify.ru');
      t.exec('Content-Type: application/x-www-form-urlencoded');
      t.exec('Content-Length: 28');
      t.exec('');
      t.exec(_('login=user&password=12345678').escapeHTML());
      t.exec('');
      
      expect(t.get_output().indexOf($.t('postResponse'))).not.toEqual(-1);
    });

    it('reaction to wrong first header', function() {
      t.exec('gsafdghasfdghasfdgh');

      expect(t.get_output().indexOf($.t('fail'))).not.toEqual(-1);
    });

    it('reaction to wrong method', function() {
      t.exec('GET /login HTTP/1.1');

      expect(t.get_output().indexOf($.t('postRequestMsgs.wrongMethod'))).not.toEqual(-1);
    });

    it('reaction to wrong URI', function() {
      t.exec('POST /login123 HTTP/1.1');
      
      expect(t.get_output().indexOf($.t('response404'))).not.toEqual(-1);
    });

    it('reaction to wrong header', function() {
      t.exec('POST /login HTTP/1.1');
      t.exec('hdsjfsfgsjgfjk');
      
      expect(t.get_output().indexOf($.t('fail'))).not.toEqual(-1);
    });

    it('reaction to absent host header', function() {
      t.exec('POST /login HTTP/1.1');
      t.exec('Content-Type: application/x-www-form-urlencoded');
      t.exec('Content-Length: 28');
      t.exec('');
      t.exec(_('login=user&password=12345678').escapeHTML());
      t.exec('');
      
      expect(t.get_output().indexOf($.t('postRequestMsgs.noHostName'))).not.toEqual(-1);
    });

    it('reaction to wrong host name', function() {
      t.exec('POST /login HTTP/1.1');
      t.exec('HOST: coursify123.ru');
      t.exec('Content-Type: application/x-www-form-urlencoded');
      t.exec('Content-Length: 28');
      t.exec('');
      t.exec(_('login=user&password=12345678').escapeHTML());
      t.exec('');
      
      expect(t.get_output().indexOf($.t('postRequestMsgs.wrongHostName'))).not.toEqual(-1);
    });

    it('reaction to absent content type header', function() {
      t.exec('POST /login HTTP/1.1');
      t.exec('HOST: coursify.ru');
      t.exec('Content-Length: 28');
      t.exec('');
      t.exec(_('login=user&password=12345678').escapeHTML());
      t.exec('');

      expect(t.get_output().indexOf($.t('postRequestMsgs.noContentType'))).not.toEqual(-1);
    });

    it('reaction to wrong content type', function() {
      t.exec('POST /login HTTP/1.1');
      t.exec('HOST: coursify.ru');
      t.exec('Content-Type: text/plain');
      t.exec('Content-Length: 28');
      t.exec('');
      t.exec(_('login=user&password=12345678').escapeHTML());
      t.exec('');

      expect(t.get_output().indexOf($.t('postRequestMsgs.wrongContentType'))).not.toEqual(-1);
    });

    it('reaction to absent content length field', function() {
      t.exec('POST /login HTTP/1.1');
      t.exec('HOST: coursify.ru');
      t.exec('Content-Type: application/x-www-form-urlencoded');
      t.exec('');
      t.exec(_('login=user&password=12345678').escapeHTML());
      t.exec('');

      expect(t.get_output().indexOf($.t('postRequestMsgs.noContentLength'))).not.toEqual(-1);
    });

    it('reaction to wrong content length', function() {
      t.exec('POST /login HTTP/1.1');
      t.exec('HOST: coursify.ru');
      t.exec('Content-Type: application/x-www-form-urlencoded');
      t.exec('Content-Length: 123');
      t.exec('');
      t.exec(_('login=user&password=12345678').escapeHTML());
      t.exec('');

      expect(t.get_output().indexOf($.t('postRequestMsgs.wrongContentLength'))).not.toEqual(-1);
    });

    it('reaction to wrong content', function() {
      t.exec('POST /login HTTP/1.1');
      t.exec('HOST: coursify.ru');
      t.exec('Content-Type: application/x-www-form-urlencoded');
      t.exec('Content-Length: 5');
      t.exec('');
      t.exec('aaaaa');
      t.exec('');

      expect(t.get_output().indexOf($.t('postRequestMsgs.wrongContent'))).not.toEqual(-1);
    });
  });
});
