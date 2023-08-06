Python client for the [billomat.com](http://www.billomat.com) [API](http://www.billomat.com/en/api/)
=====================================================================================================

The syntax of the client is inspired by the great [Django ORM](https://docs.djangoproject.com/en/dev/topics/db/queries/).

Example usage
--------------
```python
from billomat import models
from billomat.base import Client

Client.api_name = 'apiname'
Client.api_key = 'apikey'

# set optional app-id and -secret
Client.app_id = 'app_id'
Client.app_secret = 'app_secret'

articles = models.Article.objects.all()
for article in articles:
    print unicode(article.title)
articles = articles.filter(title='Awesome')
for article in articles:
    print unicode(article.title)

article = models.Article.objects.get(article_number=2)
article.title = u'This is an awesome article'
article.save()

article = models.Article.objects.create(
    title=u'This is an awesome article',
)
article.delete()
```

License
--------
[MIT](https://github.com/lociii/billomat/blob/master/LICENSE.md)
