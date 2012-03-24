# Google App Engine SDK 

## [master branch](https://github.com/lukmdo/googleappengine-python/tree/master) is a git mirror ([with tags](https://github.com/lukmdo/googleappengine-python/tags)) of [the official repo](http://code.google.com/p/googleappengine/source/browse/#svn%2Ftrunk%2Fpython)

```bash
$ git diff 1.6.2 1.6.3 # simple as it should
```

## [pip branch](https://github.com/lukmdo/googleappengine-python/tree/pip) makes it pip installable

**Zero modifications/patching only by adding ```setup.py``` + ```MANIFEST.in```**

```bash
$ mkvirtualenv --no-site-packages -p `which python2.5`
$ cat requirements.txt
pep8
-e git://github.com/lukmdo/googleappengine-python.git@pip#egg=googleappengine-python
$ pip install --install-option="install" -r ./requirements.txt
$ pip freeze
googleappengine-python==1.6.3
pep8==0.6.1
wsgiref==0.1.2
```

It provides two scripts:

- appcfg.py
- dev_appserver_main.py (yeap _main) [...more info](https://github.com/lukmdo/googleappengine-python/commit/2077eeeb3455a849cfa7f9171194c5ed2f6f579b)

## Alternatives
- SDK ≥ 1.6.1 + gae.pth with list of libs in virtualenvs *site-packages* like [found on stackoverflow](http://stackoverflow.com/questions/3858772/how-to-use-virtualenv-with-google-app-engine-sdk-on-mac-os-x-10-6)
- [mkappenginevenv.sh](https://gist.github.com/1012769)
- ... or a bit more manual way by [schettino72 blog](http://schettino72.wordpress.com/2010/11/21/appengine-virtualenv/)

## Found issues or got ideas ?
Please [contact me](mailto:me@lukmdo.com) or use [github issues system](https://github.com/lukmdo/googleappengine-python/issues)